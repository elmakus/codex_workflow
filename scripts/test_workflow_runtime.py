"""Current-contract regression overrides for the owner-customized workflow."""

from __future__ import annotations

import tomllib
import unittest

import workflow_owner_regression as owner
from runtime.platform_settings import patch_codex_settings


base = owner.base
PACKAGE = owner.PACKAGE


def _test_private_version_and_user_marker_are_synchronized(self: unittest.TestCase) -> None:
    version = (PACKAGE / "operate" / "VERSION").read_text(encoding="utf-8").strip()
    self.assertEqual(version, "1.1.17-private.1")
    user_agents = (PACKAGE / "operate" / "user_AGENTS.md").read_text(encoding="utf-8")
    self.assertEqual(user_agents.count(f"<!-- codex-workflow-version: {version} -->"), 1)
    self.assertGreater(base.parse_semver("1.1.17-private.1"), base.parse_semver("1.1.17-private.0"))
    self.assertEqual(base.NEXT_PACKAGE_VERSION, "1.1.17-private.2")


def _test_worker_models_and_reasoning(self: unittest.TestCase) -> None:
    expected = {
        "micro_executor": ("gpt-5.6-luna", "high"),
        "default_executor": ("gpt-5.6-luna", "max"),
        "senior_executor": ("gpt-6-astra", "low"),
        "tester": ("gpt-5.6-luna", "max"),
        "archivist": ("gpt-5.6-luna", "max"),
        "companion": ("gpt-5.6-luna", "max"),
        "investigator": ("gpt-5.6-luna", "max"),
    }
    paths = sorted((PACKAGE / "agents").glob("*.toml"))
    self.assertEqual({path.stem for path in paths}, set(expected))
    for path in paths:
        config = tomllib.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(config["name"], path.stem)
        self.assertEqual((config["model"], config["model_reasoning_effort"]), expected[path.stem])


def _test_current_private_contract(self: unittest.TestCase) -> None:
    agents = (PACKAGE / "AGENTS.md").read_text(encoding="utf-8")
    heavy = (PACKAGE / "heavy_route.md").read_text(encoding="utf-8")
    delegation = (PACKAGE / "delegation.md").read_text(encoding="utf-8")
    investigator = (PACKAGE / "agents" / "investigator.toml").read_text(encoding="utf-8")
    archivist = (PACKAGE / "agents" / "archivist.toml").read_text(encoding="utf-8")
    heavy_flat = " ".join(heavy.split())
    delegation_flat = " ".join(delegation.split())

    self.assertFalse((PACKAGE / "medium_route.md").exists())
    self.assertFalse((PACKAGE / "skills").exists())
    self.assertIn("In leaf state, work directly without reading", agents)
    self.assertIn("enter `deployment state`, read that Heavy contract", agents)
    for doc in ("project_progress.md", "project_diary.md", "latest_session_work.md"):
        self.assertIn(doc, agents)
    self.assertIn("Main is an orchestrator, not an executor", heavy)
    self.assertIn("do not send user-visible progress", heavy)
    self.assertIn("intermediate findings", heavy)
    self.assertIn('Do not narrate an "important discovery"', heavy)
    self.assertIn("changed hypothesis", heavy)
    self.assertIn("changed plan", heavy)
    self.assertIn("If work can continue safely without user input, remain silent", heavy)
    self.assertNotIn("scope or plan changes materially", heavy)
    self.assertIn("one event-driven `wait_agent` call", heavy_flat)
    self.assertIn("`1500000` ms (25 minutes)", heavy)
    self.assertIn("wait again rather than polling", heavy_flat)
    self.assertIn("Do not load it merely to enter Heavy", heavy_flat)
    self.assertIn("project or Internet context gap", heavy)
    self.assertIn("Micro Executor", heavy)
    self.assertIn("Spark High", heavy)
    self.assertIn("Luna High", heavy)
    self.assertIn("## Work Packages", delegation)
    self.assertIn("## Micro Execution", delegation)
    self.assertIn("## Recovery", delegation)
    self.assertIn("**Investigation Context**", delegation)
    self.assertIn("**Evidence Question + Goal**", delegation)
    self.assertIn("project evidence, Internet sources, or both", delegation_flat)
    self.assertIn('agent_type="micro_executor"', delegation)
    self.assertIn('model="gpt-5.3-codex-spark"', delegation)
    self.assertIn("Default Executor (Luna Max)", delegation)
    self.assertIn("Senior Executor (Astra Low)", delegation)
    self.assertIn("project evidence, Internet sources, or both", investigator)
    self.assertIn("Do not\nedit those files during a deployment", archivist)
    for template in ("project_progress.md", "latest_session_work.md"):
        text = (PACKAGE / "project_docs" / template).read_text(encoding="utf-8")
        self.assertNotIn("updates this document", text)
        self.assertNotIn("Keep only", text)
        self.assertNotIn("Keep one concise", text)


def _test_platform_configuration_has_no_fixed_concurrency(self: unittest.TestCase) -> None:
    rendered = patch_codex_settings("")
    config = tomllib.loads(rendered)
    self.assertTrue(config["agents"]["enabled"])
    self.assertTrue(config["features"]["multi_agent"])
    self.assertNotIn("max_concurrent_threads_per_session", rendered)


base.PrivateCustomizationTests.test_private_version_and_user_marker_are_synchronized = _test_private_version_and_user_marker_are_synchronized
base.PrivateCustomizationTests.test_worker_models_and_reasoning = _test_worker_models_and_reasoning
base.MarkerTests.test_operational_policies_are_compact_and_knowledge_aware = _test_current_private_contract
if hasattr(base.PrivateCustomizationTests, "test_platform_configuration_keeps_multi_agent_and_ceiling_twenty"):
    delattr(base.PrivateCustomizationTests, "test_platform_configuration_keeps_multi_agent_and_ceiling_twenty")
base.PrivateCustomizationTests.test_platform_configuration_has_no_fixed_concurrency = _test_platform_configuration_has_no_fixed_concurrency


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
