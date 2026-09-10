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
    self.assertEqual(version, "1.1.17-private.4")
    user_agents = (PACKAGE / "operate" / "user_AGENTS.md").read_text(encoding="utf-8")
    self.assertEqual(user_agents.count(f"<!-- codex-workflow-version: {version} -->"), 1)
    self.assertGreater(base.parse_semver("1.1.17-private.4"), base.parse_semver("1.1.17-private.3"))
    self.assertEqual(base.NEXT_PACKAGE_VERSION, "1.1.17-private.5")


def _test_worker_models_and_reasoning(self: unittest.TestCase) -> None:
    expected = {
        "micro_executor": ("gpt-5.6-luna", "high"),
        "default_executor": ("gpt-5.6-luna", "max"),
        "senior_executor": ("gpt-5.6-sol", "medium"),
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


def _test_heavy_only_workflow_keeps_leaf_direct_path(self: unittest.TestCase) -> None:
    agents = (PACKAGE / "AGENTS.md").read_text(encoding="utf-8")
    self.assertIn("## Workflow", agents)
    self.assertIn("codex_workflow/heavy_route.md", agents)
    self.assertIn("In leaf state, work directly without reading", agents)
    self.assertIn("enter `deployment state`, bootstrap the session Companion below", agents)
    self.assertIn("read that Heavy contract", agents)
    self.assertIn("## Early Companion", agents)
    self.assertNotIn("## Route Selection", agents)
    self.assertNotIn("**Light**", agents)
    self.assertNotIn("**Medium**", agents)
    self.assertFalse((PACKAGE / "medium_route.md").exists())

    heavy = (PACKAGE / "heavy_route.md").read_text(encoding="utf-8")
    self.assertIn("Use as the substantive-work contract under `AGENTS.md`.", heavy)
    self.assertIn("## Companion Lifecycle", heavy)
    self.assertNotIn("## Fast Path", heavy)
    self.assertIn("## Closure", heavy)


def _test_current_private_contract(self: unittest.TestCase) -> None:
    agents = (PACKAGE / "AGENTS.md").read_text(encoding="utf-8")
    heavy = (PACKAGE / "heavy_route.md").read_text(encoding="utf-8")
    delegation = (PACKAGE / "delegation.md").read_text(encoding="utf-8")
    companion = (PACKAGE / "agents" / "companion.toml").read_text(encoding="utf-8")
    investigator = (PACKAGE / "agents" / "investigator.toml").read_text(encoding="utf-8")
    archivist = (PACKAGE / "agents" / "archivist.toml").read_text(encoding="utf-8")
    repo_root = PACKAGE.parent
    readme = (repo_root / "README.md").read_text(encoding="utf-8")
    workflow_map = (repo_root / "workflow_break_down.md").read_text(encoding="utf-8")
    heavy_flat = " ".join(heavy.split())
    delegation_flat = " ".join(delegation.split())

    self.assertFalse((PACKAGE / "medium_route.md").exists())
    self.assertFalse((PACKAGE / "skills").exists())
    self.assertIn("In leaf state, work directly without reading", agents)
    self.assertIn("enter `deployment state`, bootstrap the session Companion", agents)
    self.assertIn("## Deployment Output Gate", agents)
    self.assertIn("before task completion, emit no user-visible prose", agents)
    self.assertIn("Can execution safely continue without user input?", agents)
    self.assertIn("Intermediate findings, discoveries, changed hypotheses, changed plans", agents)
    self.assertIn("At completion, send one normal final response", agents)
    for doc in ("project_progress.md", "project_diary.md", "latest_session_work.md"):
        self.assertIn(doc, agents)

    self.assertIn("## Early Companion", agents)
    self.assertIn('agent_type="companion"', agents)
    self.assertIn('task_name="companion"', agents)
    self.assertIn('fork_turns="none"', agents)
    self.assertIn("before broad project discovery, planning", agents)
    self.assertIn("while Main's context is still small", agents)
    self.assertIn("Do not ask it to read the complete `agent_docs/` framework", agents)
    self.assertIn("unrelated module documents", agents)
    self.assertIn("Do not wait solely for Companion", agents)
    self.assertIn("later deployments in the same workflow session", agents)
    self.assertIn("continue with proportionate Main reads", agents)

    self.assertIn("## Worker Material Event Push", agents)
    self.assertIn("`send_message`", agents)
    self.assertIn("`BLOCKER`", agents)
    self.assertIn("`COURSE_CHANGE`", agents)
    self.assertIn("`CRITICAL_PARTIAL`", agents)
    self.assertIn("routine progress", agents)
    self.assertIn("normal completion", agents)
    self.assertIn("Do not resend an unchanged event", agents)
    self.assertIn("worker-to-`/root`", agents)

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
    self.assertIn("## Companion Lifecycle", heavy)
    self.assertIn("bootstrapped on first `deployment state` entry", heavy)
    self.assertIn("do not create a second one", heavy)
    self.assertIn("bootstrap does not authorize a full-project intake", heavy)
    self.assertIn("Wait for its result only when the result gates a decision", heavy)
    self.assertIn("Use one persistent Companion per workflow session", heavy)
    self.assertIn("## Material Event Handling", heavy)
    self.assertIn("long event-driven `wait_agent` lifecycle unchanged", heavy)
    self.assertIn("When Main receives a material worker message", heavy)
    self.assertIn("must not cause status polling", heavy)
    self.assertIn("Do not ask workers to send routine progress", heavy)

    self.assertIn("Do not turn the bootstrap into a full-project intake", companion)
    self.assertIn("do not read the complete `agent_docs/` framework", companion)
    self.assertIn("unrelated module documents", companion)
    self.assertIn("If no useful bounded context is", companion)

    for public_doc in (readme, workflow_map):
        self.assertNotIn("created on demand", public_doc)
        self.assertIn("first deployment", public_doc)
        self.assertIn("full `agent_docs/`", public_doc)
        self.assertIn("send_message", public_doc)
        self.assertIn("BLOCKER", public_doc)
        self.assertIn("COURSE_CHANGE", public_doc)
        self.assertIn("CRITICAL_PARTIAL", public_doc)

    self.assertIn("## Work Packages", delegation)
    self.assertIn("## Micro Execution", delegation)
    self.assertIn("## Recovery", delegation)
    self.assertIn("**Investigation Context**", delegation)
    self.assertIn("**Evidence Question + Goal**", delegation)
    self.assertIn("project evidence, Internet sources, or both", delegation_flat)
    self.assertIn('agent_type="micro_executor"', delegation)
    self.assertIn('model="gpt-5.3-codex-spark"', delegation)
    self.assertIn("Default Executor (Luna Max)", delegation)
    self.assertIn("Senior Executor (Sol Medium)", delegation)
    self.assertIn("## Material Event Push", delegation)
    self.assertIn("do not repeat it in every task capsule", delegation)
    self.assertIn("Do not use Main follow-ups to poll worker status", delegation)
    self.assertIn("A `wait_agent` timeout without new evidence is not a reason to request an update", delegation)
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
base.PrivateCustomizationTests.test_heavy_only_workflow_keeps_leaf_direct_path = _test_heavy_only_workflow_keeps_leaf_direct_path
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
