"""Global compute-profile selection and workflow-owned worker rendering."""

from __future__ import annotations

import re
from dataclasses import dataclass

from ._toml import tomllib
from .errors import ValidationError
from .layout import BUILTIN_WORKERS, WORKER_MARKER, PackageLayout, RuntimePaths
from .plan import OperationPlan, deduplicate, text_mutation
from .platform_settings import patch_codex_settings


DEFAULT_COMPUTE_PROFILE = "plus"
COMPUTE_SETTINGS = "settings.toml"


@dataclass(frozen=True)
class WorkerModel:
    model: str
    reasoning_effort: str
    harness: str = "codex"
    model_provider: str | None = None


PROFILE_COMMUNICATION_POLICIES: dict[str, str] = {
    "plus": """## Orchestration Communication

During substantive work, keep user-visible updates restrained and outcome-oriented. Send a brief update only at a meaningful user-relevant milestone, or when work has lasted long enough that continued silence would be awkward.

Do not narrate hidden or internal reasoning, instruction-conflict resolution, routine routing or worker state, trivial discoveries, changed hypotheses, repository bookkeeping, or a running play-by-play. Skill announcements should be brief and say only why the skill is useful to the user's task. Do not announce that you are resolving a skill-announcement or instruction conflict.

A mid-task question or risk notice is appropriate when execution cannot continue without user input, or when an immediate security, publication, destructive-action, or authorization risk requires explicit approval. At completion, send one normal final response containing the result, material findings, verification, and residual risk.
""",
    "muse-max": """## Orchestration Communication

Use quiet milestone orchestration during substantive work. Keep routine worker starts, healthy waiting, liveness/status updates, session or recovery bookkeeping, Git/repository bookkeeping, and other operational narration silent when they do not materially change user understanding or require action.

A concise update is allowed when a user-meaningful phase changes, such as implementation completing and independent review beginning, or a RED review moving into repair. Always surface a blocker that requires user input, an immediate security/publication/destructive-action/authorization risk, or a material scope/architecture change. Healthy-running state, timers, heartbeats, and liveness-only progress are not user milestones and must not by themselves wake Main or create commentary.

This is quiet milestone communication, not hard silence. Do not expose hidden or internal reasoning or narrate instruction-conflict resolution. At completion, send one normal final response containing the result, material findings, verification, and residual risk.
""",
}

# muse-native shares the accepted quiet user-visible communication policy with
# muse-max while using a different worker transport.
PROFILE_COMMUNICATION_POLICIES["muse-native"] = PROFILE_COMMUNICATION_POLICIES["muse-max"]

_COMMUNICATION_SECTION = re.compile(
    r"^## (?:Silent Orchestration|Orchestration Communication)\n.*?(?=^## Agents You Can Use\n)",
    re.MULTILINE | re.DOTALL,
)


COMPUTE_PROFILES: dict[str, dict[str, WorkerModel]] = {
    "plus": {
        "explorer": WorkerModel("gpt-5.6-luna", "max"),
        "investigator": WorkerModel("gpt-5.6-luna", "max"),
        "default_executor": WorkerModel("gpt-5.6-luna", "max"),
        "senior_executor": WorkerModel("gpt-5.6-sol", "medium"),
        "tester": WorkerModel("gpt-5.6-luna", "max"),
        "archivist": WorkerModel("gpt-5.6-luna", "max"),
    },
    "muse-max": {
        "explorer": WorkerModel("muse-spark-1.3-contributor", "max", "muse-code"),
        "investigator": WorkerModel("muse-spark-1.3-contributor", "max", "muse-code"),
        "default_executor": WorkerModel("muse-spark-1.3-contributor", "max", "muse-code"),
        "senior_executor": WorkerModel("muse-spark-1.3-contributor", "max", "muse-code"),
        "tester": WorkerModel("muse-spark-1.3-contributor", "max", "muse-code"),
        "archivist": WorkerModel("muse-spark-1.3-contributor", "max", "muse-code"),
    },
    "muse-native": {
        "explorer": WorkerModel("muse-spark-1.3-contributor", "max", "codex", "cliproxyapi"),
        "investigator": WorkerModel("muse-spark-1.3-contributor", "max", "codex", "cliproxyapi"),
        "default_executor": WorkerModel("muse-spark-1.3-contributor", "max", "codex", "cliproxyapi"),
        "senior_executor": WorkerModel("muse-spark-1.3-contributor", "max", "codex", "cliproxyapi"),
        "tester": WorkerModel("muse-spark-1.3-contributor", "max", "codex", "cliproxyapi"),
        "archivist": WorkerModel("muse-spark-1.3-contributor", "max", "codex", "cliproxyapi"),
    },
}

_MODEL_LINE = re.compile(r'^model\\s*=\\s*"[^"]+"\\s*$', re.MULTILINE)
_REASONING_LINE = re.compile(
    r'^model_reasoning_effort\\s*=\\s*"[^"]+"\\s*$', re.MULTILINE
)
_MODEL_PROVIDER_LINE = re.compile(
    r'^model_provider\\s*=\\s*"[^"]+"\\s*$', re.MULTILINE
)
_WORKFLOW_PROVIDER_BLOCK = re.compile(
    r'^# codex-workflow-model-provider\\nmodel_provider\\s*=\\s*"[^"]+"\\s*\\n?',
    re.MULTILINE,
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
    result: dict[str, dict[str, str]] = {}
    for worker, spec in sorted(COMPUTE_PROFILES[profile].items()):
        summary = {
            "model": spec.model,
            "reasoning_effort": spec.reasoning_effort,
            "harness": spec.harness,
        }
        if spec.model_provider is not None:
            summary["model_provider"] = spec.model_provider
        result[worker] = summary
    return result


def validate_model_provider_config(text: str, provider: str) -> dict[str, str]:
    """Validate a user-owned provider route without reading or emitting secrets."""

    try:
        config = tomllib.loads(text) if text.strip() else {}
    except tomllib.TOMLDecodeError as error:
        raise ValidationError(f"existing Codex config is invalid TOML: {error}") from error
    providers = config.get("model_providers")
    provider_config = providers.get(provider) if isinstance(providers, dict) else None
    if not isinstance(provider_config, dict):
        raise ValidationError(
            f"muse-native requires configured [model_providers.{provider}] in user Codex config"
        )
    base_url = provider_config.get("base_url")
    if not isinstance(base_url, str) or not base_url.strip():
        raise ValidationError(
            f"muse-native provider {provider!r} must define a non-empty base_url"
        )
    wire_api = provider_config.get("wire_api", "responses")
    if wire_api != "responses":
        raise ValidationError(
            f"muse-native provider {provider!r} must use wire_api = \"responses\""
        )
    return {
        "model_provider": provider,
        "configured": "yes",
        "wire_api": "responses",
        "credential_owner": "external",
    }


def render_heavy_route_for_profile(text: str, profile: str) -> str:
    validate_compute_profile(profile)
    if len(_COMMUNICATION_SECTION.findall(text)) != 1:
        raise ValidationError(
            "heavy route must contain exactly one profile communication section"
        )
    rendered = _COMMUNICATION_SECTION.sub(
        PROFILE_COMMUNICATION_POLICIES[profile] + "\n", text, count=1
    )
    if PROFILE_COMMUNICATION_POLICIES[profile] not in rendered:
        raise ValidationError("rendered heavy-route communication policy verification failed")
    return rendered


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

    # Roles assigned to an external harness deliberately keep their installed
    # Codex worker TOMLs valid but dormant. Internal Codex roles are rendered
    # normally from this same profile authority.
    if spec.harness != "codex":
        return text

    rendered = _WORKFLOW_PROVIDER_BLOCK.sub("", text, count=1)
    rendered = _MODEL_LINE.sub(f'model = "{spec.model}"', rendered, count=1)
    rendered = _REASONING_LINE.sub(
        f'model_reasoning_effort = "{spec.reasoning_effort}"', rendered, count=1
    )
    if spec.model_provider is not None:
        if _MODEL_PROVIDER_LINE.search(rendered):
            raise ValidationError(
                f"refusing to replace unowned model_provider in workflow worker: {worker}"
            )
        rendered = _REASONING_LINE.sub(
            lambda match: (
                match.group(0)
                + "\n# codex-workflow-model-provider"
                + f'\nmodel_provider = "{spec.model_provider}"'
            ),
            rendered,
            count=1,
        )
    try:
        parsed = tomllib.loads(rendered)
    except tomllib.TOMLDecodeError as error:
        raise ValidationError(
            f"rendered worker TOML is invalid for {worker}: {error}"
        ) from error
    if parsed.get("model") != spec.model or parsed.get("model_reasoning_effort") != spec.reasoning_effort:
        raise ValidationError(f"rendered worker profile verification failed: {worker}")
    if spec.model_provider is not None and parsed.get("model_provider") != spec.model_provider:
        raise ValidationError(f"rendered worker provider verification failed: {worker}")
    return rendered


def plan_compute_profile(runtime: RuntimePaths, profile: str) -> OperationPlan:
    profile = validate_compute_profile(profile)
    if runtime.config_toml.is_symlink() or (
        runtime.config_toml.exists() and not runtime.config_toml.is_file()
    ):
        raise ValidationError(f"Codex config path is not a regular file: {runtime.config_toml}")
    config_text = (
        runtime.config_toml.read_text(encoding="utf-8")
        if runtime.config_toml.is_file()
        else ""
    )
    providers = sorted(
        {
            spec.model_provider
            for spec in COMPUTE_PROFILES[profile].values()
            if spec.model_provider is not None
        }
    )
    provider_routes = [
        validate_model_provider_config(config_text, provider)
        for provider in providers
    ]

    package = PackageLayout.resolve(runtime.runtime)
    templates = package.agent_templates
    mutations = []
    for worker in sorted(BUILTIN_WORKERS):
        source = templates / f"{worker}.toml"
        if not source.is_file():
            raise ValidationError(f"installed worker template is missing: {source}")
        # Validate the package template as part of the installed workflow contract,
        # but patch the installed worker in place so an internal-Codex allocation
        # changes only the model and reasoning fields. External-harness roles leave
        # their installed Codex TOMLs dormant and unchanged.
        render_worker_for_profile(source.read_text(encoding="utf-8"), worker, profile)
        target = runtime.agents / f"{worker}.toml"
        if target.is_symlink() or not target.is_file():
            raise ValidationError(f"installed workflow worker is missing or invalid: {target}")
        target_text = target.read_text(encoding="utf-8")
        target_match = WORKER_MARKER.search(target_text)
        if target_match is None or target_match.group(1) != worker:
            raise ValidationError(f"refusing to replace non-owned worker file: {target}")
        rendered = render_worker_for_profile(target_text, worker, profile)
        mutations.append(text_mutation(target, rendered))
    mutations.append(text_mutation(runtime.compute_settings, render_compute_settings(profile)))
    mutations.append(
        text_mutation(
            runtime.config_toml,
            patch_codex_settings(
                config_text,
                internal_agents_enabled=profile in {"plus", "muse-native"},
            ),
        )
    )
    heavy_route = runtime.runtime / "heavy_route.md"
    if heavy_route.is_symlink() or not heavy_route.is_file():
        raise ValidationError(f"installed heavy route is missing or invalid: {heavy_route}")
    mutations.append(
        text_mutation(
            heavy_route,
            render_heavy_route_for_profile(
                heavy_route.read_text(encoding="utf-8"), profile
            ),
        )
    )
    harnesses = sorted({spec.harness for spec in COMPUTE_PROFILES[profile].values()})
    details: dict[str, object] = {
        "profile": profile,
        "workers": profile_summary(profile),
        "worker_harnesses": harnesses,
        "communication_policy": profile,
        "internal_codex_agents": (
            "enabled" if profile in {"plus", "muse-native"} else "disabled"
        ),
        "main_agent": "unchanged",
    }
    if provider_routes:
        details["provider_routes"] = provider_routes
    return OperationPlan(
        "profile",
        deduplicate(mutations),
        [],
        [],
        details,
    )
, re.MULTILINE
)
_MODEL_PROVIDER_LINE = re.compile(
    r'^model_provider\s*=\s*"[^"]+"\s*

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
            "harness": spec.harness,
        }
        for worker, spec in sorted(COMPUTE_PROFILES[profile].items())
    }


def render_heavy_route_for_profile(text: str, profile: str) -> str:
    validate_compute_profile(profile)
    if len(_COMMUNICATION_SECTION.findall(text)) != 1:
        raise ValidationError(
            "heavy route must contain exactly one profile communication section"
        )
    rendered = _COMMUNICATION_SECTION.sub(
        PROFILE_COMMUNICATION_POLICIES[profile] + "\n", text, count=1
    )
    if PROFILE_COMMUNICATION_POLICIES[profile] not in rendered:
        raise ValidationError("rendered heavy-route communication policy verification failed")
    return rendered


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

    # Roles assigned to an external harness deliberately keep their installed
    # Codex worker TOMLs valid but dormant. Internal Codex roles are rendered
    # normally from this same profile authority.
    if spec.harness != "codex":
        return text

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
        # Validate the package template as part of the installed workflow contract,
        # but patch the installed worker in place so an internal-Codex allocation
        # changes only the model and reasoning fields. External-harness roles leave
        # their installed Codex TOMLs dormant and unchanged.
        render_worker_for_profile(source.read_text(encoding="utf-8"), worker, profile)
        target = runtime.agents / f"{worker}.toml"
        if target.is_symlink() or not target.is_file():
            raise ValidationError(f"installed workflow worker is missing or invalid: {target}")
        target_text = target.read_text(encoding="utf-8")
        target_match = WORKER_MARKER.search(target_text)
        if target_match is None or target_match.group(1) != worker:
            raise ValidationError(f"refusing to replace non-owned worker file: {target}")
        rendered = render_worker_for_profile(target_text, worker, profile)
        mutations.append(text_mutation(target, rendered))
    mutations.append(text_mutation(runtime.compute_settings, render_compute_settings(profile)))
    if runtime.config_toml.is_symlink() or (
        runtime.config_toml.exists() and not runtime.config_toml.is_file()
    ):
        raise ValidationError(f"Codex config path is not a regular file: {runtime.config_toml}")
    config_text = (
        runtime.config_toml.read_text(encoding="utf-8")
        if runtime.config_toml.is_file()
        else ""
    )
    mutations.append(
        text_mutation(
            runtime.config_toml,
            patch_codex_settings(
                config_text,
                internal_agents_enabled=profile == "plus",
            ),
        )
    )
    heavy_route = runtime.runtime / "heavy_route.md"
    if heavy_route.is_symlink() or not heavy_route.is_file():
        raise ValidationError(f"installed heavy route is missing or invalid: {heavy_route}")
    mutations.append(
        text_mutation(
            heavy_route,
            render_heavy_route_for_profile(
                heavy_route.read_text(encoding="utf-8"), profile
            ),
        )
    )
    harnesses = sorted({spec.harness for spec in COMPUTE_PROFILES[profile].values()})
    return OperationPlan(
        "profile",
        deduplicate(mutations),
        [],
        [],
        {
            "profile": profile,
            "workers": profile_summary(profile),
            "worker_harnesses": harnesses,
            "communication_policy": profile,
            "internal_codex_agents": "enabled" if profile == "plus" else "disabled",
            "main_agent": "unchanged",
        },
    )
, re.MULTILINE
)
_WORKFLOW_PROVIDER_BLOCK = re.compile(
    r'^# codex-workflow-model-provider\nmodel_provider\s*=\s*"[^"]+"\s*\n?',
    re.MULTILINE,
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
            "harness": spec.harness,
        }
        for worker, spec in sorted(COMPUTE_PROFILES[profile].items())
    }


def render_heavy_route_for_profile(text: str, profile: str) -> str:
    validate_compute_profile(profile)
    if len(_COMMUNICATION_SECTION.findall(text)) != 1:
        raise ValidationError(
            "heavy route must contain exactly one profile communication section"
        )
    rendered = _COMMUNICATION_SECTION.sub(
        PROFILE_COMMUNICATION_POLICIES[profile] + "\n", text, count=1
    )
    if PROFILE_COMMUNICATION_POLICIES[profile] not in rendered:
        raise ValidationError("rendered heavy-route communication policy verification failed")
    return rendered


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

    # Roles assigned to an external harness deliberately keep their installed
    # Codex worker TOMLs valid but dormant. Internal Codex roles are rendered
    # normally from this same profile authority.
    if spec.harness != "codex":
        return text

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
        # Validate the package template as part of the installed workflow contract,
        # but patch the installed worker in place so an internal-Codex allocation
        # changes only the model and reasoning fields. External-harness roles leave
        # their installed Codex TOMLs dormant and unchanged.
        render_worker_for_profile(source.read_text(encoding="utf-8"), worker, profile)
        target = runtime.agents / f"{worker}.toml"
        if target.is_symlink() or not target.is_file():
            raise ValidationError(f"installed workflow worker is missing or invalid: {target}")
        target_text = target.read_text(encoding="utf-8")
        target_match = WORKER_MARKER.search(target_text)
        if target_match is None or target_match.group(1) != worker:
            raise ValidationError(f"refusing to replace non-owned worker file: {target}")
        rendered = render_worker_for_profile(target_text, worker, profile)
        mutations.append(text_mutation(target, rendered))
    mutations.append(text_mutation(runtime.compute_settings, render_compute_settings(profile)))
    if runtime.config_toml.is_symlink() or (
        runtime.config_toml.exists() and not runtime.config_toml.is_file()
    ):
        raise ValidationError(f"Codex config path is not a regular file: {runtime.config_toml}")
    config_text = (
        runtime.config_toml.read_text(encoding="utf-8")
        if runtime.config_toml.is_file()
        else ""
    )
    mutations.append(
        text_mutation(
            runtime.config_toml,
            patch_codex_settings(
                config_text,
                internal_agents_enabled=profile == "plus",
            ),
        )
    )
    heavy_route = runtime.runtime / "heavy_route.md"
    if heavy_route.is_symlink() or not heavy_route.is_file():
        raise ValidationError(f"installed heavy route is missing or invalid: {heavy_route}")
    mutations.append(
        text_mutation(
            heavy_route,
            render_heavy_route_for_profile(
                heavy_route.read_text(encoding="utf-8"), profile
            ),
        )
    )
    harnesses = sorted({spec.harness for spec in COMPUTE_PROFILES[profile].values()})
    return OperationPlan(
        "profile",
        deduplicate(mutations),
        [],
        [],
        {
            "profile": profile,
            "workers": profile_summary(profile),
            "worker_harnesses": harnesses,
            "communication_policy": profile,
            "internal_codex_agents": "enabled" if profile == "plus" else "disabled",
            "main_agent": "unchanged",
        },
    )
