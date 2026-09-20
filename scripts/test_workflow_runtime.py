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
    render_heavy_route_for_profile,
)
from runtime.errors import TransactionError, ValidationError
from runtime.layout import PackageLayout, ProjectPaths, RuntimePaths
from runtime.lifecycle import plan_bootstrap, plan_update
from runtime.platform_settings import patch_codex_settings


base = owner.base
PACKAGE = owner.PACKAGE


def _test_private_version_and_user_marker_are_synchronized(self: unittest.TestCase) -> None:
    version = (PACKAGE / "operate" / "VERSION").read_text(encoding="utf-8").strip()
    self.assertEqual(version, "1.1.17-private.12")
    user_agents = (PACKAGE / "operate" / "user_AGENTS.md").read_text(encoding="utf-8")
    self.assertEqual(user_agents.count(f"<!-- codex-workflow-version: {version} -->"), 1)
    self.assertIn("codex_workflow --profile plus", user_agents)
    self.assertIn("codex_workflow --profile muse-max", user_agents)
    self.assertNotIn("codex_workflow --profile luna-xhigh", user_agents)
    self.assertNotIn("codex_workflow --profile pro-x5", user_agents)
    self.assertGreater(base.parse_semver("1.1.17-private.12"), base.parse_semver("1.1.17-private.11"))
    self.assertEqual(base.NEXT_PACKAGE_VERSION, "1.1.17-private.13")


def _test_worker_models_and_reasoning(self: unittest.TestCase) -> None:
    expected = {
        "explorer": ("gpt-5.6-luna", "max"),
        "investigator": ("gpt-5.6-luna", "max"),
        "default_executor": ("gpt-5.6-luna", "max"),
        "senior_executor": ("gpt-5.6-sol", "medium"),
        "tester": ("gpt-5.6-luna", "max"),
        "archivist": ("gpt-5.6-luna", "max"),
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
    self.assertIn("Use `leaf state` only for questions and genuinely trivial bounded actions", agents)
    self.assertIn("Do not classify nontrivial work as leaf merely because it is bounded or short", agents)
    self.assertNotIn("small bounded operations", agents)
    self.assertIn("enter `deployment state`, read that Heavy contract", agents)
    self.assertIn("Use Explorer for bounded project-context discovery", agents)
    self.assertIn("## Bounded Context Discovery", agents)
    self.assertNotIn("## Route Selection", agents)
    self.assertNotIn("**Light**", agents)
    self.assertNotIn("**Medium**", agents)
    self.assertFalse((PACKAGE / "medium_route.md").exists())

    heavy = (PACKAGE / "heavy_route.md").read_text(encoding="utf-8")
    self.assertIn("Use as the substantive-work contract under `AGENTS.md`.", heavy)
    self.assertIn("## Explorer Discovery", heavy)
    self.assertIn("## Investigator Lanes", heavy)
    self.assertNotIn("## Fast Path", heavy)
    self.assertIn("## Closure", heavy)


def _test_current_private_contract(self: unittest.TestCase) -> None:
    agents = (PACKAGE / "AGENTS.md").read_text(encoding="utf-8")
    heavy = (PACKAGE / "heavy_route.md").read_text(encoding="utf-8")
    delegation = (PACKAGE / "delegation.md").read_text(encoding="utf-8")
    explorer = (PACKAGE / "agents" / "explorer.toml").read_text(encoding="utf-8")
    investigator = (PACKAGE / "agents" / "investigator.toml").read_text(encoding="utf-8")
    archivist = (PACKAGE / "agents" / "archivist.toml").read_text(encoding="utf-8")
    archivist_contract = (PACKAGE / "archivist.md").read_text(encoding="utf-8")
    repo_root = PACKAGE.parent
    readme = (repo_root / "README.md").read_text(encoding="utf-8")
    workflow_map_path = repo_root / "workflow_breakdown.md"
    self.assertTrue(workflow_map_path.is_file())
    self.assertFalse((repo_root / "workflow_break_down.md").exists())
    workflow_map = workflow_map_path.read_text(encoding="utf-8")
    benchmark_guide = (repo_root / "benchmarks" / "README.md").read_text(encoding="utf-8")
    heavy_flat = " ".join(heavy.split())
    delegation_flat = " ".join(delegation.split())
    active_contracts = "\n".join((agents, heavy, delegation))

    self.assertFalse((PACKAGE / "medium_route.md").exists())
    self.assertFalse((PACKAGE / "skills").exists())
    self.assertIn("In leaf state, work directly without reading", agents)
    self.assertIn("Use `leaf state` only for questions and genuinely trivial bounded actions", agents)
    self.assertIn("Do not classify nontrivial work as leaf merely because it is bounded or short", agents)
    self.assertNotIn("small bounded operations", agents)
    self.assertIn("enter `deployment state`, read that Heavy contract", agents)
    self.assertIn("## Deployment Communication", agents)
    self.assertIn("profile-specific user-communication policy", agents)
    self.assertIn("never expose hidden reasoning", agents)
    self.assertIn("instruction-conflict resolution", agents)
    for doc in ("project_progress.md", "project_diary.md", "latest_session_work.md"):
        self.assertIn(doc, agents)

    self.assertIn("## Bounded Context Discovery", agents)
    self.assertIn("bounded disposable Explorer assignment", agents)
    self.assertIn("not a persistent session secretary", agents)
    self.assertIn("complete-`agent_docs/` intake", agents)
    self.assertIn("directly to Main", agents)

    self.assertIn("## Worker Material Event Push", agents)
    self.assertIn("Under `plus`, an internal Codex worker", agents)
    self.assertIn("`send_message`", agents)
    self.assertIn("`BLOCKER`", agents)
    self.assertIn("`COURSE_CHANGE`", agents)
    self.assertIn("`CRITICAL_PARTIAL`", agents)
    self.assertIn("routine progress", agents)
    self.assertIn("normal completion", agents)
    self.assertIn("Do not resend an unchanged event", agents)
    self.assertIn("material events to `/root`/Main", agents)
    self.assertIn("direct sibling messaging is not part of the workflow contract", agents)
    self.assertNotIn("do not have the Codex `send_message` channel", agents)
    self.assertNotIn("do not emulate material-event push", agents)

    archivist_contract_flat = " ".join(archivist_contract.split()).lower()
    self.assertIn("genuinely trivial bounded actions classified as leaf state before heavy entry", archivist_contract_flat)
    self.assertIn("bounded but nontrivial documentation work belongs to archivist", archivist_contract_flat)
    self.assertIn("do not transfer its work to main", archivist_contract_flat)
    self.assertNotIn("questions and small bounded tasks", archivist_contract_flat)

    self.assertIn("Main is an orchestrator, not an executor", heavy)
    self.assertIn("do not perform production execution directly", heavy)
    self.assertIn("Main may act directly only on orchestration-owned work", heavy)
    self.assertIn("Unavailable worker capacity does not transfer worker ownership to Main", heavy)
    self.assertIn("only for genuinely trivial tasks classified as leaf state", heavy)
    self.assertNotIn("genuinely trivial and shorter than delegation overhead", heavy)
    self.assertIn("## Orchestration Communication", heavy)
    self.assertIn("restrained and outcome-oriented", heavy)
    self.assertIn("meaningful user-relevant milestone", heavy)
    self.assertIn("instruction-conflict resolution", heavy)
    self.assertIn("Skill announcements should be brief", heavy)
    self.assertNotIn("scope or plan changes materially", heavy)
    self.assertIn("one event-driven `wait_agent` call", heavy_flat)
    self.assertIn("`1500000` ms (25 minutes)", heavy)
    self.assertIn("wait again rather than polling", heavy_flat)
    self.assertIn("Do not load it merely to enter Heavy", heavy_flat)
    self.assertIn("## Explorer Discovery", heavy)
    self.assertIn("## Investigator Lanes", heavy)
    self.assertIn("exactly three independent lanes", heavy)
    self.assertIn("shared **Problem ID**", heavy)
    self.assertIn("distinct **Task IDs**", heavy)
    self.assertIn("complementary evidence/search angles", heavy)
    self.assertIn("majority count is never a decision rule", heavy)
    self.assertIn("Every worker final result returns directly to Main", heavy)
    self.assertIn("Direct worker-to-worker messaging is not part of the workflow contract", heavy)
    for role in ("Explorer", "Investigator", "Default Executor", "Senior Executor", "Tester", "Archivist"):
        self.assertIn(f"| {role} |", heavy)
    self.assertNotIn("luna-xhigh", heavy)
    self.assertNotIn("pro-x5", heavy)
    self.assertIn("For `plus`, all six supported roles use the internal Codex worker lifecycle", heavy)
    self.assertIn("When the profile is `muse-max`, all six supported roles", heavy)
    self.assertIn("active compute profile", heavy)
    self.assertIn("## Fresh and Independent Context Routing", heavy)
    self.assertIn('`fork_turns="none"`', heavy)
    self.assertIn("Do not call app-level `create_thread` solely", heavy)
    self.assertIn("Use a new Tester for independent review", heavy)
    self.assertIn("effective child permissions must be treated as separate runtime state", heavy)
    self.assertIn("## Plus Material Event Handling", heavy)
    self.assertIn("When the active profile is `plus`", heavy)
    self.assertIn("long event-driven `wait_agent` lifecycle unchanged", heavy)
    self.assertIn("When Main receives a material worker message", heavy)
    self.assertIn("must not cause status polling", heavy)
    self.assertIn("Do not ask workers to send routine progress", heavy)

    self.assertIn("disposable read-only project-context worker", explorer)
    self.assertIn("bounded project evidence", explorer)
    self.assertIn("not fault", explorer)
    self.assertIn("Do not modify project, environment, or", explorer)
    self.assertIn("project evidence, Internet sources, or both", investigator)

    self.assertNotIn("Companion", active_contracts)
    self.assertNotIn("Micro Executor", active_contracts)
    self.assertNotIn("micro_executor", active_contracts)
    self.assertNotIn("Micro Execution", active_contracts)
    self.assertNotIn("luna-xhigh", active_contracts)
    self.assertNotIn("pro-x5", active_contracts)
    self.assertNotIn("do not have the Codex `send_message` channel", active_contracts)
    self.assertNotIn("Do not build a polling or background-message shim", active_contracts)
    self.assertEqual(heavy.count("## Role-Specific Work Packages"), 1)
    self.assertNotRegex(active_contracts, r"(?i)at most\s+\d+\s+words")
    self.assertNotIn("direct sibling messaging is exceptional", active_contracts)
    self.assertNotIn("sibling's active task", active_contracts)

    for public_doc in (readme, workflow_map):
        public_doc_flat = " ".join(public_doc.split()).lower()
        self.assertIn("genuinely trivial", public_doc_flat)
        self.assertIn("bounded but nontrivial", public_doc_flat)
        self.assertNotIn("small bounded tasks", public_doc_flat)
        self.assertNotIn("created on demand", public_doc)
        self.assertIn("proportionate", public_doc_flat)
        self.assertIn("send_message", public_doc)
        self.assertIn("BLOCKER", public_doc)
        self.assertIn("COURSE_CHANGE", public_doc)
        self.assertIn("CRITICAL_PARTIAL", public_doc)
        self.assertIn("plus", public_doc)
        self.assertIn("muse-max", public_doc)
        self.assertNotIn("pro-x5", public_doc)
        self.assertNotIn("luna-xhigh", public_doc)
        self.assertNotIn("Companion", public_doc)
        self.assertNotIn("Micro Executor", public_doc)
        self.assertIn("settings.toml", public_doc)

    self.assertIn("## Deep dive: orchestration design", workflow_map)
    self.assertIn("exactly three independent Investigator lanes", " ".join(workflow_map.split()))
    benchmark_guide_flat = " ".join(benchmark_guide.split())
    self.assertIn("initial case study", benchmark_guide_flat)
    self.assertIn("`plus`", benchmark_guide)
    self.assertIn("`muse-max`", benchmark_guide)
    self.assertNotIn("luna-xhigh", benchmark_guide)
    self.assertNotIn("pro-x5", benchmark_guide)
    self.assertNotIn("Companion", benchmark_guide)
    self.assertNotIn("Micro Executor", benchmark_guide)

    self.assertIn("## Work Packages", delegation)
    self.assertIn("## Fresh and Independent Contexts", delegation)
    self.assertIn("new internal worker/subagent by default", delegation)
    self.assertIn("Do not use app-level `create_thread` solely", delegation)
    self.assertIn("implementing worker must not substitute for the independent reviewer", delegation)
    self.assertIn("effective child permissions as an independent runtime fact", delegation)
    self.assertIn("## Recovery", delegation)
    self.assertIn("Explorer | **Project Context Scope**", delegation)
    self.assertIn("Investigator | **Problem ID**", delegation)
    self.assertIn("**Investigation Context**", delegation)
    self.assertIn("**Evidence Question + Goal**", delegation)
    self.assertIn("one shared **Problem ID**", delegation)
    self.assertIn("exactly three independent Investigator lanes", delegation)
    self.assertIn("distinct **Task ID**", delegation)
    self.assertIn("Lanes do not coordinate, message one another, or vote", delegation)
    self.assertIn("Main compares all three reports", delegation)
    self.assertIn("majority voting is not a decision rule", delegation)
    self.assertIn("project evidence, Internet sources, or both", delegation_flat)
    self.assertIn("For `plus`, all six supported roles use the normal internal Codex lifecycle", delegation)
    self.assertIn("Under `muse-max`, all six roles use Muse Spark 1.3 Contributor Max", delegation)
    self.assertNotIn("luna-xhigh", delegation)
    self.assertNotIn("pro-x5", delegation)
    self.assertIn("## Plus Material Event Push", delegation)
    self.assertIn("Under `plus`, the standing internal-Codex-worker material-event policy", delegation)
    self.assertIn("do not repeat it in every task capsule", delegation)
    self.assertNotIn("have no `send_message` path", delegation)
    self.assertNotIn("polling or background-message shim", delegation)
    self.assertEqual(delegation.count("## Worker Follow-up and Repair"), 1)
    self.assertIn("Do not use Main follow-ups to poll worker status", delegation)
    self.assertIn("a `wait_agent` timeout without new evidence is not a reason to request an update", delegation)
    self.assertIn("Do not instruct or permit direct sibling messaging", delegation)
    self.assertIn("smallest complete, evidence-linked, decision-ready return", delegation)
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

    def test_only_plus_and_muse_max_are_supported(self) -> None:
        self.assertEqual(set(COMPUTE_PROFILES), {"plus", "muse-max"})
        for removed in ("luna-xhigh", "pro-x5"):
            with self.subTest(profile=removed):
                with self.assertRaisesRegex(ValidationError, "unsupported compute profile"):
                    plan_compute_profile(self.runtime, removed)

    def test_switches_between_supported_profiles(self) -> None:
        plan_compute_profile(self.runtime, "muse-max").apply()
        self.assertEqual(read_compute_profile(self.runtime), "muse-max")
        heavy = (self.runtime.runtime / "heavy_route.md").read_text(encoding="utf-8")
        self.assertIn("live Muse-worker experiment", heavy)

        plan_compute_profile(self.runtime, "plus").apply()
        self.assertEqual(read_compute_profile(self.runtime), "plus")
        self.assertEqual(
            _installed_worker_models(self.runtime),
            _expected_profile_models("plus"),
        )

    def test_profile_switch_renders_distinct_communication_policies(self) -> None:
        heavy_path = self.runtime.runtime / "heavy_route.md"
        expected = {
            "plus": ("restrained and outcome-oriented", "live Muse-worker experiment"),
            "muse-max": ("live Muse-worker experiment", "restrained and outcome-oriented"),
        }
        for profile, (present, absent) in expected.items():
            plan_compute_profile(self.runtime, profile).apply()
            heavy = heavy_path.read_text(encoding="utf-8")
            self.assertIn(present, heavy)
            self.assertNotIn(absent, heavy)
            self.assertIn("instruction-conflict resolution", heavy)

    def test_heavy_route_renderer_rejects_missing_owned_section(self) -> None:
        with self.assertRaisesRegex(ValidationError, "exactly one"):
            render_heavy_route_for_profile("# Heavy Route\n", "plus")

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
        plan = plan_compute_profile(self.runtime, "plus")
        before_settings = self.runtime.compute_settings.read_bytes()
        heavy_path = self.runtime.runtime / "heavy_route.md"
        before_heavy = heavy_path.read_bytes()
        before_workers = {
            path.name: path.read_bytes() for path in self.runtime.agents.glob("*.toml")
        }
        blocker = self.runtime.agents / "investigator.toml"
        blocker.unlink()
        blocker.mkdir()
        with self.assertRaises(TransactionError):
            plan.apply()
        self.assertEqual(self.runtime.compute_settings.read_bytes(), before_settings)
        self.assertEqual(heavy_path.read_bytes(), before_heavy)
        for name, content in before_workers.items():
            if name == "investigator.toml":
                continue
            self.assertEqual((self.runtime.agents / name).read_bytes(), content)

    def test_update_preserves_selected_muse_max_profile(self) -> None:
        plan_compute_profile(self.runtime, "muse-max").apply()
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
                "1.1.17-private.12", next_version
            ),
            encoding="utf-8",
        )
        incoming = PackageLayout.resolve(incoming_root)
        plan_update(incoming, self.runtime, self.project).apply()
        self.assertEqual(read_compute_profile(self.runtime), "muse-max")
        heavy = (self.runtime.runtime / "heavy_route.md").read_text(encoding="utf-8")
        self.assertIn("live Muse-worker experiment", heavy)



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
