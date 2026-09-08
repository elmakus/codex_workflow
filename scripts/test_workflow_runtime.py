"""Current-contract regression overrides for the owner-customized workflow."""

from __future__ import annotations

import tomllib
import unittest

import workflow_owner_regression as owner


base = owner.base
PACKAGE = owner.PACKAGE


def _test_worker_models_and_reasoning(self: unittest.TestCase) -> None:
    worker_paths = sorted((PACKAGE / "agents").glob("*.toml"))
    self.assertEqual(
        {path.stem for path in worker_paths},
        {
            "micro_executor",
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
            elif path.stem == "micro_executor":
                self.assertEqual(config["model"], "gpt-5.6-luna")
                self.assertEqual(config["model_reasoning_effort"], "high")
            else:
                self.assertEqual(config["model"], "gpt-5.6-luna")
                self.assertEqual(config["model_reasoning_effort"], "max")


def _test_progressive_disclosure_and_micro_executor_contract(
    self: unittest.TestCase,
) -> None:
    agents = (PACKAGE / "AGENTS.md").read_text(encoding="utf-8")
    heavy = (PACKAGE / "heavy_route.md").read_text(encoding="utf-8")
    delegation = (PACKAGE / "delegation.md").read_text(encoding="utf-8")
    micro = (PACKAGE / "agents" / "micro_executor.toml").read_text(encoding="utf-8")
    heavy_flat = " ".join(heavy.split())
    delegation_flat = " ".join(delegation.split())

    self.assertLess(len(agents.splitlines()), 90)
    self.assertLess(len(heavy.splitlines()), 200)
    self.assertFalse((PACKAGE / "medium_route.md").exists())

    self.assertIn("Main is an orchestrator, not an executor", heavy)
    self.assertIn("prefer `delegate -> resume -> wait -> integrate`", heavy_flat)
    self.assertIn("Default to silent orchestration", heavy)
    self.assertIn("one event-driven `wait_agent` call", heavy_flat)
    self.assertIn("`1500000` ms (25 minutes)", heavy)
    self.assertIn("wait again rather than polling", heavy_flat)
    self.assertIn("## Closure", heavy)

    for role in (
        "Companion",
        "Investigator",
        "Micro Executor",
        "Default Executor",
        "Senior Executor",
        "Tester",
        "Archivist",
    ):
        self.assertIn(role, heavy)

    self.assertIn("~/.codex/codex_workflow/delegation.md", heavy)
    self.assertIn("Do not load it merely to enter Heavy", heavy_flat)
    self.assertIn("use `micro_executor`", heavy)
    self.assertIn("Spark High", heavy)
    self.assertIn("Luna High", heavy)
    self.assertIn("Default Executor or Senior Executor", heavy_flat)

    self.assertIn("## Work Packages", delegation)
    self.assertIn("## Micro Execution", delegation)
    self.assertIn("## Worker Follow-up and Repair", delegation)
    self.assertIn("## Recovery", delegation)
    self.assertIn("Micro Executor is a distinct worker below Default Executor", delegation_flat)
    self.assertIn('agent_type="micro_executor"', delegation)
    self.assertIn('model="gpt-5.3-codex-spark"', delegation)
    self.assertIn('reasoning_effort="high"', delegation)
    self.assertIn("installed Micro Executor profile is", delegation_flat)
    self.assertIn("Luna High", delegation)
    self.assertIn("Default Executor (Luna Max)", delegation)
    self.assertIn("Senior Executor (Astra Low)", delegation)
    self.assertNotIn(
        'agent_type="default_executor"',
        delegation.split("## Micro Execution", 1)[1].split("## Worker Follow-up", 1)[0],
    )

    micro_config = tomllib.loads(micro)
    self.assertEqual(micro_config["name"], "micro_executor")
    self.assertEqual(micro_config["model"], "gpt-5.6-luna")
    self.assertEqual(micro_config["model_reasoning_effort"], "high")
    self.assertIn("tiny deterministic", micro)
    self.assertIn("reclassify it to Default Executor or Senior", micro)


base.PrivateCustomizationTests.test_worker_models_and_reasoning = (
    _test_worker_models_and_reasoning
)
base.MarkerTests.test_operational_policies_are_compact_and_knowledge_aware = (
    _test_progressive_disclosure_and_micro_executor_contract
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
