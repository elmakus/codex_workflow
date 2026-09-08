"""Current regression entry point for the private Heavy-only workflow.

The full lifecycle regression suite remains in ``workflow_runtime_regression``.
This entry point replaces only policy assertions that intentionally changed in
1.1.14-private.2 development: Heavy-only routing and Astra Senior Executor.
"""

from __future__ import annotations

import json
import tomllib
import unittest
from pathlib import Path

import workflow_runtime_regression as base


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "codex_workflow"


def _test_worker_models_and_reasoning(self: unittest.TestCase) -> None:
    worker_paths = sorted((PACKAGE / "agents").glob("*.toml"))
    self.assertEqual(
        {path.stem for path in worker_paths},
        {
            "default_executor",
            "senior_executor",
            "tester",
            "archivist",
            "companion",
            "investigator",
        },
    )
    for path in worker_paths:
        with self.subTest(worker=path.stem):
            config = tomllib.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(config["name"], path.stem)
            if path.stem == "senior_executor":
                self.assertEqual(config["model"], "gpt-6-astra")
                self.assertEqual(config["model_reasoning_effort"], "low")
            else:
                self.assertEqual(config["model"], "gpt-5.6-luna")
                self.assertEqual(config["model_reasoning_effort"], "max")


def _test_heavy_only_workflow_keeps_leaf_direct_path(
    self: unittest.TestCase,
) -> None:
    agents = (PACKAGE / "AGENTS.md").read_text(encoding="utf-8")
    self.assertIn("## Workflow", agents)
    self.assertIn("codex_workflow/heavy_route.md", agents)
    self.assertIn("In leaf state, work directly without reading", agents)
    self.assertIn("enter `deployment state`, read that Heavy contract", agents)
    self.assertNotIn("## Route Selection", agents)
    self.assertNotIn("**Light**", agents)
    self.assertNotIn("**Medium**", agents)
    self.assertFalse((PACKAGE / "medium_route.md").exists())

    heavy = (PACKAGE / "heavy_route.md").read_text(encoding="utf-8")
    self.assertIn("Use as the substantive-work contract under `AGENTS.md`.", heavy)
    self.assertNotIn("## Fast Path", heavy)
    self.assertIn("## Closure", heavy)


def _test_operational_policies_are_compact_and_knowledge_aware(
    self: unittest.TestCase,
) -> None:
    policies = {
        "AGENTS.md": (PACKAGE / "AGENTS.md").read_text(encoding="utf-8"),
        "heavy_route.md": (PACKAGE / "heavy_route.md").read_text(encoding="utf-8"),
    }
    self.assertLess(len(policies["AGENTS.md"].splitlines()), 90)
    self.assertLess(len(policies["heavy_route.md"].splitlines()), 240)
    self.assertFalse((PACKAGE / "medium_route.md").exists())

    required_documentation_policy = (
        "Read documentation in proportion to the task.",
        "When continuing, start from the specified checkpoint.",
        "Search `agent_docs/` and read the documents or sections",
        "needed to understand the task, its constraints, and dependencies.",
        "Expand the read when context is missing.",
        "Read the complete set only when the scope of work requires it.",
        "A missing unrelated document does not block the task.",
    )
    for name, text in policies.items():
        with self.subTest(documentation_policy=name):
            section = text.split("## Proportionate Documentation Read\n", 1)[1]
            section = section.split("\n## ", 1)[0].strip()
            flat = " ".join(section.split())
            for requirement in required_documentation_policy:
                self.assertIn(requirement, flat)
            for retired_requirement in (
                "Required Documentation Read",
                "framework exactly once",
                "one shared session-level read",
                "leave deployment entry incomplete",
                "intake blocker",
            ):
                self.assertNotIn(retired_requirement, " ".join(text.split()))

    heavy = policies["heavy_route.md"]
    heavy_flat = " ".join(heavy.split())
    self.assertIn("## Your Role and Authority", heavy)
    self.assertIn("You are the main agent and central knowledge director", heavy)
    self.assertIn("For each task, decide which roles are useful", heavy_flat)
    self.assertIn("## Orchestrator-First Execution", heavy)
    self.assertIn("Main is an orchestrator, not an executor", heavy)
    self.assertIn("prefer `delegate -> resume -> wait -> integrate`", heavy_flat)
    self.assertIn("If assigned work needs intervention", heavy)
    self.assertIn("Resume it when possible", heavy)
    self.assertIn("irrecoverably unavailable", heavy)
    self.assertIn("not a reason for Main to take over", heavy_flat)
    self.assertIn("prefer resuming the same worker or thread", heavy_flat)
    self.assertIn("`wait_agent` timeout that returns no new worker state", heavy_flat)
    self.assertIn("not by itself a reason to poll status", heavy_flat)
    for timeout_action in (
        "list threads",
        "message",
        "interrupt",
        "replace",
        "inspect worker progress",
    ):
        self.assertIn(timeout_action, heavy)
    self.assertIn("issue another appropriately long `wait_agent`", heavy_flat)
    self.assertIn("identify only the available recovery sources", heavy_flat)
    for recovery_source in (
        "predecessor thread",
        "worktree",
        "branch",
        "handoff path",
        "existing commits",
    ):
        self.assertIn(recovery_source, heavy)
    self.assertIn("replacement worker owns detailed state recovery", heavy_flat)
    self.assertIn("determine completed versus remaining work", heavy_flat)
    self.assertIn("delegate recovery + continuation", heavy_flat)
    self.assertIn("Main should not reconstruct the predecessor's detailed work", heavy_flat)
    self.assertIn("genuinely trivial and shorter than delegation overhead", heavy_flat)
    self.assertIn("required solely for orchestration", heavy_flat)
    for non_takeover_task in (
        "implementation",
        "security review",
        "repository migration",
        "material Git/GitHub operations",
        "testing",
        "delegable research",
    ):
        self.assertIn(non_takeover_task, heavy)
    self.assertIn('"Take over to make progress"', heavy)
    self.assertIn('"take over to go faster"', heavy)
    self.assertIn("## Silent Orchestration", heavy)
    self.assertIn("Default to silent orchestration", heavy)
    self.assertIn("Perform routine coordination through tool calls", heavy_flat)
    for routine_event in (
        "waited",
        "resumed",
        "messaged a worker",
        "listed threads",
        "routine status check",
        "chose not to take over assigned work",
        "left other work queued",
        "reused an existing result",
        "next routine orchestration step",
    ):
        self.assertIn(routine_event, heavy)
    self.assertIn(
        "Do not report a successful intermediate stage or repository", heavy_flat
    )
    self.assertIn("everything is proceeding as expected, stay silent", heavy_flat)
    self.assertIn("defer successful progress to the final response", heavy_flat)
    for meaningful_update in (
        "blocker requires the user's decision",
        "security or publication risk",
        "scope or plan changes materially",
        "user explicitly requested progress updates",
        "whole task completes",
    ):
        self.assertIn(meaningful_update, heavy_flat)
    self.assertIn("Always send the normal final response", heavy_flat)
    self.assertNotIn("at most one brief line", heavy_flat)
    self.assertIn("Silence limits narration only", heavy)
    self.assertIn("## Agents You Can Use", heavy)
    for role in (
        "Companion",
        "Investigator",
        "Default Executor",
        "Senior Executor",
        "Tester",
        "Archivist",
    ):
        self.assertIn(role, heavy)
    self.assertIn("Reserve the Astra production worker", heavy)
    self.assertIn("## Assign Companion", heavy)
    self.assertIn('agent_type="companion"', heavy)
    self.assertIn('task_name="companion"', heavy)
    self.assertIn('fork_turns="none"', heavy)
    self.assertIn("Reuse the same Companion across later assignments", heavy_flat)
    self.assertIn("## Role-Specific Work Packages", heavy)
    for capsule in (
        "**Task ID**",
        "**Project Context Scope**",
        "**Research Question + Goal**",
        "**Implementation Context + Ownership**",
        "**Verification Context**",
        "**Documentation Context + Audience**",
    ):
        self.assertIn(capsule, heavy)
    self.assertIn("Require workers to echo Task ID in every report", heavy)
    self.assertIn("Do not repeat the worker's substantive task", heavy)
    self.assertNotIn("intervene directly", heavy)
    self.assertIn("## Orchestration Guidance", heavy)
    self.assertIn("synthesize their results\n  once", heavy)
    self.assertIn("bounded batches or sequential", heavy_flat)
    self.assertIn("main-agent tracking cost", heavy_flat)
    self.assertIn("orchestration-only tool operations", heavy_flat)
    self.assertIn("rather than taking over its task", heavy_flat)
    self.assertIn("Preserve sequential ordering", heavy)
    self.assertIn("Do not\nmaximize concurrency without a concrete benefit", heavy)
    self.assertIn("Use\n  appropriately long lifecycle waits", heavy)
    self.assertIn("Heavy does not impose an aggregate active-subagent limit", heavy_flat)
    self.assertNotIn("at most 20 active subagents", heavy)
    self.assertIn("at most one Senior Executor", heavy)
    self.assertIn("Create and coordinate every worker directly", heavy)
    self.assertNotIn("## Fast Path", heavy)
    self.assertIn("## Closure", heavy)
    self.assertNotIn("deployment-token-report", heavy)
    self.assertIn("one\n  event-driven `wait_agent` call", heavy)
    self.assertIn("`1500000` ms (25 minutes)", heavy)
    self.assertNotIn("`1800000` ms", heavy)
    self.assertIn("wait again rather\n  than polling", heavy)

    agents_policy = policies["AGENTS.md"]
    self.assertIn("## Design Principles", agents_policy)
    self.assertIn("## Rollout Efficiency", agents_policy)
    self.assertIn("## Working State", agents_policy)
    self.assertIn("## Project Documentation", agents_policy)
    self.assertIn("## Workflow", agents_policy)
    self.assertIn("## Platform Paths", agents_policy)
    self.assertIn("In leaf state, work directly without reading", agents_policy)
    self.assertIn("codex_workflow/heavy_route.md", agents_policy)
    self.assertNotIn("codex_workflow/medium_route.md", agents_policy)
    self.assertNotIn("Select one of these routes", agents_policy)
    self.assertNotIn("Follow the user's route selection", agents_policy)

    handoff_contract = (PACKAGE / "archivist.md").read_text(encoding="utf-8")
    archivist = (PACKAGE / "agents" / "archivist.toml").read_text(encoding="utf-8")
    self.assertIn('agent_type="archivist"', handoff_contract)
    self.assertIn("one closure owner for each deployment", handoff_contract)
    self.assertIn("durable, cross-session documentation framework", archivist)
    self.assertIn("canonical home", archivist)
    self.assertIn("cross-reference rather than duplicate", archivist)
    self.assertNotIn("deployment-token-report", archivist)

    executor = (PACKAGE / "agents" / "default_executor.toml").read_text(
        encoding="utf-8"
    )
    senior = (PACKAGE / "agents" / "senior_executor.toml").read_text(
        encoding="utf-8"
    )
    tester = (PACKAGE / "agents" / "tester.toml").read_text(encoding="utf-8")
    companion = (PACKAGE / "agents" / "companion.toml").read_text(encoding="utf-8")
    investigator = (PACKAGE / "agents" / "investigator.toml").read_text(
        encoding="utf-8"
    )
    self.assertIn('model = "gpt-5.6-luna"', executor)
    self.assertIn('model = "gpt-6-astra"', senior)
    self.assertIn('model_reasoning_effort = "low"', senior)
    for worker in (executor, tester, companion, investigator, archivist):
        self.assertIn('model_reasoning_effort = "max"', worker)

    retired_architecture_phrases = (
        "wave barrier",
        "evidence manifest",
        "verification_ledger",
        "repair packet",
        "root-cause gate",
        "fixed execution pipeline",
        "predefined pipeline",
    )
    instruction_surfaces = {
        **policies,
        "archivist.md": handoff_contract,
        "archivist.toml": archivist,
        "default_executor.toml": executor,
        "senior_executor.toml": senior,
        "tester.toml": tester,
        "companion.toml": companion,
        "investigator.toml": investigator,
        "README.md": (ROOT / "README.md").read_text(encoding="utf-8"),
        "workflow_break_down.md": (ROOT / "workflow_break_down.md").read_text(
            encoding="utf-8"
        ),
    }
    for name, text in instruction_surfaces.items():
        lowered = text.lower()
        for phrase in retired_architecture_phrases:
            self.assertNotIn(phrase, lowered, name)


def _test_update_removes_retired_medium_route(self: unittest.TestCase) -> None:
    self.bootstrap()
    retired = self.runtime.runtime / "medium_route.md"
    retired.write_text("# Retired Medium Route\n", encoding="utf-8")
    state_path = self.runtime.runtime / "install_state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    state["owned_runtime_files"].append("medium_route.md")
    state_path.write_text(json.dumps(state) + "\n", encoding="utf-8")

    incoming = self.incoming_package("heavy-only-incoming", base.NEXT_PACKAGE_VERSION)
    base.plan_update(incoming, self.runtime, self.project).apply()

    self.assertFalse(retired.exists())


# Replace only assertions whose contract intentionally changed. Keep every other
# lifecycle, migration, safety, packaging, and platform-setting regression test.
delattr(
    base.PrivateCustomizationTests,
    "test_worker_customization_changes_only_luna_reasoning",
)
base.PrivateCustomizationTests.test_worker_models_and_reasoning = (
    _test_worker_models_and_reasoning
)

delattr(
    base.PrivateCustomizationTests,
    "test_heavy_is_default_and_keeps_explicit_routes_and_fast_path",
)
base.PrivateCustomizationTests.test_heavy_only_workflow_keeps_leaf_direct_path = (
    _test_heavy_only_workflow_keeps_leaf_direct_path
)

base.MarkerTests.test_operational_policies_are_compact_and_knowledge_aware = (
    _test_operational_policies_are_compact_and_knowledge_aware
)
base.LifecycleIntegrationTests.test_update_removes_retired_medium_route = (
    _test_update_removes_retired_medium_route
)


PrivateCustomizationTests = base.PrivateCustomizationTests
MarkerTests = base.MarkerTests
SafetyTests = base.SafetyTests
PlatformSettingsTests = base.PlatformSettingsTests
ReleaseTests = base.ReleaseTests
TransactionTests = base.TransactionTests
LifecycleIntegrationTests = base.LifecycleIntegrationTests
PersonalizationTests = base.PersonalizationTests


if __name__ == "__main__":
    unittest.main()
