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
    harness: str = "codex"


PROFILE_COMMUNICATION_POLICIES: dict[str, str] = {
    "plus": """## Orchestration Communication

During substantive work, keep user-visible updates restrained and outcome-oriented. Send a brief update only at a meaningful user-relevant milestone, or when work has lasted long enough that continued silence would be awkward.

Do not narrate hidden or internal reasoning, instruction-conflict resolution, routine routing or worker state, trivial discoveries, changed hypotheses, repository bookkeeping, or a running play-by-play. Skill announcements should be brief and say only why the skill is useful to the user's task. Do not announce that you are resolving a skill-announcement or instruction conflict.

A mid-task question or risk notice is appropriate when execution cannot continue without user input, or when an immediate security, publication, destructive-action, or authorization risk requires explicit approval. At completion, send one normal final response containing the result, material findings, verification, and residual risk.
""",
    "luna-xhigh": """## Silent Orchestration

During execution, do not send user-visible progress, status narration, intermediate findings, hypotheses, evidence summaries, routing decisions, worker-state updates, Git or branch-state updates, checkpoints, or next-step descriptions. Perform orchestration through tool calls only.

Do not narrate an \"important discovery\", changed hypothesis, changed plan, successful intermediate result, newly discovered evidence, repository state, skill selection, or instruction-conflict resolution. Incorporate those internally and continue working.

A mid-task user-visible message is permitted only when execution cannot continue without a user decision or missing information, an immediate security/publication/destructive-action/authorization risk requires explicit approval, or the user explicitly requested progress updates for this task. If work can continue safely without user input, remain silent.

When the task completes, send one normal final response containing the result, material findings, verification, and residual risk. Silence limits narration only; correctness work continues.
""",
    "pro-x5": """## Orchestration Communication

Use normal concise commentary during substantive work. Give relevant progress updates, including a brief announcement when a skill is used and why it helps, often enough that the user can follow meaningful progress without a routine play-by-play.

Keep updates focused on user-relevant outcomes, assumptions, blockers, and material milestones. Do not expose hidden or internal reasoning, narrate instruction-conflict resolution, or report routine routing, worker state, trivial discoveries, and repository bookkeeping.

Ask promptly when execution cannot continue without user input, or when an immediate security, publication, destructive-action, or authorization risk requires explicit approval. At completion, send one normal final response containing the result, material findings, verification, and residual risk.
""",
    "muse-max": """## Orchestration Communication

Use normal concise commentary during substantive work. Give relevant progress updates at meaningful milestones so the user can follow the live Muse-worker experiment without a routine play-by-play.

Keep updates focused on user-relevant outcomes, assumptions, blockers, worker results, and material milestones. Do not expose hidden or internal reasoning, narrate instruction-conflict resolution, or report low-value process bookkeeping.

Ask promptly when execution cannot continue without user input, or when an immediate security, publication, destructive-action, or authorization risk requires explicit approval. At completion, send one normal final response containing the result, material findings, verification, and residual risk.
""",
}

_COMMUNICATION_SECTION = re.compile(
    r"^## (?:Silent Orchestration|Orchestration Communication)\n.*?(?=^## Agents You Can Use\n)",
    re.MULTILINE | re.DOTALL,
)


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
    "luna-xhigh": {
        "micro_executor": WorkerModel("gpt-5.6-luna", "xhigh"),
        "default_executor": WorkerModel("gpt-5.6-luna", "xhigh"),
        "senior_executor": WorkerModel("gpt-5.6-sol", "medium"),
        "tester": WorkerModel("gpt-5.6-luna", "xhigh"),
        "archivist": WorkerModel("gpt-5.6-luna", "xhigh"),
        "companion": WorkerModel("gpt-5.6-luna", "xhigh"),
        "investigator": WorkerModel("gpt-5.6-luna", "xhigh"),
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
    "muse-max": {
        "micro_executor": WorkerModel("muse-spark-1.3-contributor", "max", "muse-code"),
        "default_executor": WorkerModel("muse-spark-1.3-contributor", "max", "muse-code"),
        "senior_executor": WorkerModel("muse-spark-1.3-contributor", "max", "muse-code"),
        "tester": WorkerModel("muse-spark-1.3-contributor", "max", "muse-code"),
        "archivist": WorkerModel("muse-spark-1.3-contributor", "max", "muse-code"),
        "companion": WorkerModel("muse-spark-1.3-contributor", "max", "muse-code"),
        "investigator": WorkerModel("muse-spark-1.3-contributor", "max", "muse-code"),
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

    # External harness profiles deliberately keep the installed Codex worker
    # TOMLs valid but dormant. The active Heavy contract routes these roles to
    # the external harness instead of asking Codex to resolve an unsupported
    # model identifier as an internal subagent.
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
        # but patch the installed worker in place so a Codex-backed profile switch
        # changes only the model and reasoning fields. External-harness profiles
        # leave the internal TOMLs dormant and unchanged.
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
            "main_agent": "unchanged",
        },
    )
