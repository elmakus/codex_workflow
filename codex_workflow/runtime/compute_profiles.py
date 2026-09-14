"""Global compute-profile selection and workflow-owned worker rendering."""

from __future__ import annotations

import re
from dataclasses import dataclass

from ._toml import tomllib
from .errors import ValidationError
from .layout import BUILTIN_WORKERS, WORKER_MARKER, PackageLayout, RuntimePaths
from .plan import OperationPlan, deduplicate, text_mutation


DEFAULT_COMPUTE_PROFILE = "plus"
COMPUTE_SETTINGS = "settings.toml"


@dataclass(frozen=True)
class WorkerModel:
    model: str
    reasoning_effort: str


COMPUTE_PROFILES: dict[str, dict[str, WorkerModel]] = {
    "plus": {
        "micro_executor": WorkerModel("gpt-5.6-luna", "high"),
        "default_executor": WorkerModel("gpt-5.6-luna", "max"),
        "senior_executor": WorkerModel("gpt-5.6-sol", "medium"),
        "tester": WorkerModel("gpt-5.6-luna", "max"),
        "archivist": WorkerModel("gpt-5.6-luna", "max"),
        "companion": WorkerModel("gpt-5.6-luna", "max"),
        "investigator": WorkerModel("gpt-5.6-luna", "max"),
    },
    "pro-x5": {
        "micro_executor": WorkerModel("gpt-5.6-sol", "low"),
        "default_executor": WorkerModel("gpt-5.6-sol", "low"),
        "senior_executor": WorkerModel("gpt-5.6-sol", "medium"),
        "tester": WorkerModel("gpt-5.6-sol", "low"),
        "archivist": WorkerModel("gpt-5.6-sol", "low"),
        "companion": WorkerModel("gpt-5.6-sol", "low"),
        "investigator": WorkerModel("gpt-5.6-sol", "low"),
    },
}


_MODEL_LINE = re.compile(r'^model\s*=\s*"[^"]+"\s*$', re.MULTILINE)
_REASONING_LINE = re.compile(
    r'^model_reasoning_effort\s*=\s*"[^"]+"\s*$', re.MULTILINE
)


def validate_compute_profile(profile: str) -> str:
    if profile not in COMPUTE_PROFILES:
        supported = ", ".join(sorted(COMPUTE_PROFILES))
        raise ValidationError(
            f"unsupported compute profile {profile!r}; supported profiles: {supported}"
        )
    expected = set(BUILTIN_WORKERS)
    actual = set(COMPUTE_PROFILES[profile])
    if actual != expected:
        raise ValidationError(
            f"compute profile {profile!r} has an invalid worker set; "
            f"missing={sorted(expected - actual)}, unexpected={sorted(actual - expected)}"
        )
    return profile


def read_compute_profile(runtime: RuntimePaths) -> str:
    path = runtime.compute_settings
    if path.is_symlink() or (path.exists() and not path.is_file()):
        raise ValidationError(f"compute profile settings path is not a regular file: {path}")
    if not path.is_file():
        return DEFAULT_COMPUTE_PROFILE
    try:
        value = tomllib.loads(path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as error:
        raise ValidationError(f"invalid compute profile settings {path}: {error}") from error
    profile = value.get("compute_profile")
    if not isinstance(profile, str) or not profile:
        raise ValidationError("compute profile settings must define non-empty compute_profile")
    return validate_compute_profile(profile)


def render_compute_settings(profile: str) -> str:
    validate_compute_profile(profile)
    return f'compute_profile = "{profile}"\n'


def worker_model(profile: str, worker: str) -> WorkerModel:
    validate_compute_profile(profile)
    try:
        return COMPUTE_PROFILES[profile][worker]
    except KeyError as error:
        raise ValidationError(f"unknown workflow worker for compute profile: {worker}") from error


def profile_summary(profile: str) -> dict[str, dict[str, str]]:
    validate_compute_profile(profile)
    return {
        worker: {
            "model": spec.model,
            "reasoning_effort": spec.reasoning_effort,
        }
        for worker, spec in sorted(COMPUTE_PROFILES[profile].items())
    }


def render_worker_for_profile(text: str, worker: str, profile: str) -> str:
    spec = worker_model(profile, worker)
    match = WORKER_MARKER.search(text)
    if match is None or match.group(1) != worker:
        raise ValidationError(f"worker ownership marker missing or wrong: {worker}")
    try:
        config = tomllib.loads(text)
    except tomllib.TOMLDecodeError as error:
        raise ValidationError(f"invalid worker TOML {worker}: {error}") from error
    if config.get("name") != worker:
        raise ValidationError(f"worker name does not match file name: {worker}")
    if len(_MODEL_LINE.findall(text)) != 1:
        raise ValidationError(f"worker must contain exactly one top-level model line: {worker}")
    if len(_REASONING_LINE.findall(text)) != 1:
        raise ValidationError(
            f"worker must contain exactly one top-level model_reasoning_effort line: {worker}"
        )
    rendered = _MODEL_LINE.sub(f'model = "{spec.model}"', text, count=1)
    rendered = _REASONING_LINE.sub(
        f'model_reasoning_effort = "{spec.reasoning_effort}"', rendered, count=1
    )
    try:
        parsed = tomllib.loads(rendered)
    except tomllib.TOMLDecodeError as error:
        raise ValidationError(
            f"rendered worker TOML is invalid for {worker}: {error}"
        ) from error
    if parsed.get("model") != spec.model or parsed.get("model_reasoning_effort") != spec.reasoning_effort:
        raise ValidationError(f"rendered worker profile verification failed: {worker}")
    return rendered


def plan_compute_profile(runtime: RuntimePaths, profile: str) -> OperationPlan:
    profile = validate_compute_profile(profile)
    package = PackageLayout.resolve(runtime.runtime)
    templates = package.agent_templates
    mutations = []
    for worker in sorted(BUILTIN_WORKERS):
        source = templates / f"{worker}.toml"
        if not source.is_file():
            raise ValidationError(f"installed worker template is missing: {source}")
        target = runtime.agents / f"{worker}.toml"
        if target.is_symlink() or (target.exists() and not target.is_file()):
            raise ValidationError(f"worker path is not a regular file: {target}")
        if target.is_file():
            target_match = WORKER_MARKER.search(target.read_text(encoding="utf-8"))
            if target_match is None or target_match.group(1) != worker:
                raise ValidationError(f"refusing to replace non-owned worker file: {target}")
        rendered = render_worker_for_profile(
            source.read_text(encoding="utf-8"), worker, profile
        )
        mutations.append(text_mutation(target, rendered))
    mutations.append(text_mutation(runtime.compute_settings, render_compute_settings(profile)))
    return OperationPlan(
        "profile",
        deduplicate(mutations),
        [],
        [],
        {
            "profile": profile,
            "workers": profile_summary(profile),
            "main_agent": "unchanged",
        },
    )
