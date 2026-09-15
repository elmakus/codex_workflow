"""Current-contract regression overrides for the owner-customized workflow."""

from __future__ import annotations

import shutil
import tempfile
import tomllib
import unittest
from pathlib import Path

import workflow_owner_regression as owner
from runtime.compute_profiles import (
    COMPUTE_PROFILES,
    DEFAULT_COMPUTE_PROFILE,
    plan_compute_profile,
    read_compute_profile,
)
from runtime.errors import TransactionError, ValidationError
from runtime.layout import PackageLayout, ProjectPaths, RuntimePaths
from runtime.lifecycle import plan_bootstrap, plan_update
from runtime.platform_settings import patch_codex_settings


base = owner.base
PACKAGE = owner.PACKAGE


def _test_private_version_and_user_marker_are_synchronized(self: unittest.TestCase) -> None:
    version = (PACKAGE / "operate" / "VERSION").read_text(encoding="utf-8").strip()
    self.assertEqual(version, "1.1.17-private.7")
    user_agents = (PACKAGE / "operate" / "user_AGENTS.md").read_text(encoding="utf-8")
    self.assertEqual(user_agents.count(f"<!-- codex-workflow-version: {version} -->"), 1)
    self.assertGreater(base.parse_semver("1.1.17-private.7"), base.parse_semver("1.1.17-private.6"))
    self.assertEqual(base.NEXT_PACKAGE_VERSION, "1.1.17-private.8")


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
    self.assertIn("Luna XHigh", heavy)
    self.assertIn("Sol Low", heavy)
    self.assertIn("luna-xhigh", heavy)
    self.assertIn("active compute profile", heavy)
    self.assertIn("## Companion Lifecycle", heavy)
    self.assertIn("bootstrapped on first `deployment state` entry", heavy)
    self.assertIn("do not create a second one", heavy)
    self.assertIn("bootstrap does not authorize a full-project intake", heavy)
    self.assertIn("Wait for its result only when the result gates a decision", heavy)
    self.assertIn("Use one persistent Companion per workflow session", heavy)
    self.assertIn("## Fresh and Independent Context Routing", heavy)
    self.assertIn('`fork_turns="none"`', heavy)
    self.assertIn("Do not call app-level `create_thread` solely", heavy)
    self.assertIn("Use a new Tester for independent review", heavy)
    self.assertIn("effective child permissions must be treated as separate runtime state", heavy)
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
        self.assertIn("pro-x5", public_doc)
        self.assertIn("luna-xhigh", public_doc)
        self.assertIn("settings.toml", public_doc)

    self.assertIn("## Work Packages", delegation)
    self.assertIn("## Fresh and Independent Contexts", delegation)
    self.assertIn("new internal worker/subagent by default", delegation)
    self.assertIn("Do not use app-level `create_thread` solely", delegation)
    self.assertIn("implementing worker must not substitute for the independent reviewer", delegation)
    self.assertIn("effective child permissions as an independent runtime fact", delegation)
    self.assertIn("## Micro Execution", delegation)
    self.assertIn("## Recovery", delegation)
    self.assertIn("**Investigation Context**", delegation)
    self.assertIn("**Evidence Question + Goal**", delegation)
    self.assertIn("project evidence, Internet sources, or both", delegation_flat)
    self.assertIn('agent_type="micro_executor"', delegation)
    self.assertIn('model="gpt-5.3-codex-spark"', delegation)
    self.assertIn("Default Executor using the active compute profile", delegation)
    self.assertIn("Senior Executor (Sol Medium in every current profile)", delegation)
    self.assertIn("luna-xhigh", delegation)
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


def _installed_worker_models(runtime: RuntimePaths) -> dict[str, tuple[str, str]]:
    result: dict[str, tuple[str, str]] = {}
    for path in sorted(runtime.agents.glob("*.toml")):
        config = tomllib.loads(path.read_text(encoding="utf-8"))
        result[path.stem] = (config["model"], config["model_reasoning_effort"])
    return result


def _expected_profile_models(profile: str) -> dict[str, tuple[str, str]]:
    return {
        worker: (spec.model, spec.reasoning_effort)
        for worker, spec in COMPUTE_PROFILES[profile].items()
    }


class ComputeProfileTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        root = Path(self.temporary.name)
        self.runtime = RuntimePaths(root / "codex-home")
        self.project = ProjectPaths(root / "project")
        self.package = PackageLayout.resolve(PACKAGE)
        plan_bootstrap(self.package, self.runtime, self.project).apply()

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_bootstrap_defaults_to_plus_and_materializes_settings(self) -> None:
        self.assertEqual(read_compute_profile(self.runtime), DEFAULT_COMPUTE_PROFILE)
        self.assertEqual(DEFAULT_COMPUTE_PROFILE, "plus")
        self.assertTrue(self.runtime.compute_settings.is_file())
        self.assertEqual(
            _installed_worker_models(self.runtime),
            _expected_profile_models("plus"),
        )

    def test_missing_pre_profile_settings_are_backward_compatible_plus(self) -> None:
        self.runtime.compute_settings.unlink()
        self.assertEqual(read_compute_profile(self.runtime), "plus")
        plan_compute_profile(self.runtime, "plus").apply()
        self.assertTrue(self.runtime.compute_settings.is_file())
        self.assertEqual(read_compute_profile(self.runtime), "plus")

    def test_luna_xhigh_uses_luna_xhigh_except_senior(self) -> None:
        expected = {
            worker: (
                ("gpt-5.6-sol", "medium")
                if worker == "senior_executor"
                else ("gpt-5.6-luna", "xhigh")
            )
            for worker in COMPUTE_PROFILES["luna-xhigh"]
        }
        self.assertEqual(_expected_profile_models("luna-xhigh"), expected)

    def test_switches_between_all_profiles(self) -> None:
        for profile in ("luna-xhigh", "pro-x5", "plus"):
            plan_compute_profile(self.runtime, profile).apply()
            self.assertEqual(read_compute_profile(self.runtime), profile)
            self.assertEqual(
                _installed_worker_models(self.runtime),
                _expected_profile_models(profile),
            )

    def test_invalid_profile_changes_nothing(self) -> None:
        before_settings = self.runtime.compute_settings.read_bytes()
        before_workers = {
            path.name: path.read_bytes() for path in self.runtime.agents.glob("*.toml")
        }
        with self.assertRaisesRegex(ValidationError, "unsupported compute profile"):
            plan_compute_profile(self.runtime, "unlimited")
        self.assertEqual(self.runtime.compute_settings.read_bytes(), before_settings)
        self.assertEqual(
            {path.name: path.read_bytes() for path in self.runtime.agents.glob("*.toml")},
            before_workers,
        )

    def test_profile_apply_rolls_back_earlier_worker_writes_on_failure(self) -> None:
        plan = plan_compute_profile(self.runtime, "luna-xhigh")
        before_settings = self.runtime.compute_settings.read_bytes()
        before_workers = {
            path.name: path.read_bytes() for path in self.runtime.agents.glob("*.toml")
        }
        blocker = self.runtime.agents / "investigator.toml"
        blocker.unlink()
        blocker.mkdir()
        with self.assertRaises(TransactionError):
            plan.apply()
        self.assertEqual(self.runtime.compute_settings.read_bytes(), before_settings)
        for name, content in before_workers.items():
            if name == "investigator.toml":
                continue
            self.assertEqual((self.runtime.agents / name).read_bytes(), content)

    def test_update_preserves_selected_luna_xhigh_profile(self) -> None:
        plan_compute_profile(self.runtime, "luna-xhigh").apply()
        root = Path(self.temporary.name)
        incoming_root = root / "incoming"
        shutil.copytree(PACKAGE, incoming_root)
        next_version = base.NEXT_PACKAGE_VERSION
        (incoming_root / "operate" / "VERSION").write_text(
            next_version + "\n", encoding="utf-8"
        )
        user_agents = incoming_root / "operate" / "user_AGENTS.md"
        user_agents.write_text(
            user_agents.read_text(encoding="utf-8").replace(
                "1.1.17-private.7", next_version
            ),
            encoding="utf-8",
        )
        incoming = PackageLayout.resolve(incoming_root)
        plan_update(incoming, self.runtime, self.project).apply()
        self.assertEqual(read_compute_profile(self.runtime), "luna-xhigh")
        self.assertEqual(
            _installed_worker_models(self.runtime),
            _expected_profile_models("luna-xhigh"),
        )


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
