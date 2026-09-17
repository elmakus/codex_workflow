"""Focused regression coverage for the experimental Muse Max worker profile."""

from __future__ import annotations

import sys
import tempfile
import tomllib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "codex_workflow"
sys.path.insert(0, str(PACKAGE))

from runtime.compute_profiles import (  # noqa: E402
    COMPUTE_PROFILES,
    plan_compute_profile,
    profile_summary,
    read_compute_profile,
    render_worker_for_profile,
)
from runtime.layout import BUILTIN_WORKERS, PackageLayout, ProjectPaths, RuntimePaths  # noqa: E402
from runtime.lifecycle import plan_bootstrap  # noqa: E402
from runtime.muse_worker import MODEL, REASONING_EFFORT, build_command  # noqa: E402


class MuseMaxProfileTests(unittest.TestCase):
    def test_every_worker_role_uses_muse_contributor_max(self) -> None:
        profile = COMPUTE_PROFILES["muse-max"]
        self.assertEqual(set(profile), set(BUILTIN_WORKERS))
        for worker, spec in profile.items():
            with self.subTest(worker=worker):
                self.assertEqual(spec.model, "muse-spark-1.3-contributor")
                self.assertEqual(spec.reasoning_effort, "max")
                self.assertEqual(spec.harness, "muse-code")

        summary = profile_summary("muse-max")
        for worker in BUILTIN_WORKERS:
            self.assertEqual(summary[worker]["harness"], "muse-code")

    def test_external_profile_leaves_internal_codex_worker_dormant(self) -> None:
        source = (PACKAGE / "agents" / "default_executor.toml").read_text(
            encoding="utf-8"
        )
        rendered = render_worker_for_profile(source, "default_executor", "muse-max")
        self.assertEqual(rendered, source)
        parsed = tomllib.loads(rendered)
        self.assertEqual(parsed["model"], "gpt-5.6-luna")

    def test_profile_switch_sets_muse_runtime_and_non_silent_policy(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            runtime = RuntimePaths(root / "codex-home")
            project = ProjectPaths(root / "project")
            package = PackageLayout.resolve(PACKAGE)
            plan_bootstrap(package, runtime, project).apply()

            plan = plan_compute_profile(runtime, "muse-max")
            self.assertEqual(plan.details["main_agent"], "unchanged")
            self.assertEqual(plan.details["worker_harnesses"], ["muse-code"])
            plan.apply()

            self.assertEqual(read_compute_profile(runtime), "muse-max")
            heavy = (runtime.runtime / "heavy_route.md").read_text(encoding="utf-8")
            self.assertIn("normal concise commentary", heavy)
            self.assertIn("live Muse-worker experiment", heavy)
            self.assertNotIn("## Silent Orchestration", heavy)

    def test_runner_pins_native_muse_contributor_max_and_keeps_sandbox(self) -> None:
        self.assertEqual(MODEL, "muse-spark-1.3-contributor")
        self.assertEqual(REASONING_EFFORT, "max")
        command = build_command("/usr/local/bin/muse", "/tmp/prompt.md")
        self.assertEqual(
            command,
            [
                "/usr/local/bin/muse",
                "--disable-approval",
                "--trust-workspace",
                "exec",
                "--model",
                "muse-spark-1.3-contributor",
                "--reasoning-effort",
                "max",
                "--prompt-file",
                "/tmp/prompt.md",
            ],
        )
        self.assertNotIn("--yolo", command)
        self.assertNotIn("--disable-sandbox", command)

    def test_user_command_and_profile_guide_expose_muse_max(self) -> None:
        user_agents = (PACKAGE / "operate" / "user_AGENTS.md").read_text(
            encoding="utf-8"
        )
        profile_guide = (PACKAGE / "operate" / "profile.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("codex_workflow --profile muse-max", user_agents)
        self.assertIn("muse-spark-1.3-contributor", profile_guide)
        self.assertIn("`max` reasoning", profile_guide)
        self.assertIn("native Muse Code harness", profile_guide)


if __name__ == "__main__":
    unittest.main()
