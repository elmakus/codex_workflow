"""Focused regression coverage for the mixed-harness Muse Max profile."""

from __future__ import annotations

import io
import json
import os
import sys
import tempfile
import tomllib
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch


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
from runtime.layout import (  # noqa: E402
    BUILTIN_WORKERS,
    PackageLayout,
    ProjectPaths,
    RuntimePaths,
)
from runtime.lifecycle import plan_bootstrap  # noqa: E402
from runtime.muse_worker import (  # noqa: E402
    MuseWorkerError,
    build_command,
    run,
)


MUSE_ROLES = {
    "micro_executor",
    "default_executor",
    "senior_executor",
    "tester",
    "archivist",
    "investigator",
}


class MuseMaxProfileTests(unittest.TestCase):
    def test_muse_max_is_one_internal_companion_plus_six_muse_roles(self) -> None:
        profile = COMPUTE_PROFILES["muse-max"]
        self.assertEqual(set(profile), set(BUILTIN_WORKERS))
        companion = profile["companion"]
        self.assertEqual(companion.model, "gpt-5.6-luna")
        self.assertEqual(companion.reasoning_effort, "xhigh")
        self.assertEqual(companion.harness, "codex")

        self.assertEqual(set(profile) - {"companion"}, MUSE_ROLES)
        for worker in MUSE_ROLES:
            with self.subTest(worker=worker):
                spec = profile[worker]
                self.assertEqual(spec.model, "muse-spark-1.3-contributor")
                self.assertEqual(spec.reasoning_effort, "max")
                self.assertEqual(spec.harness, "muse-code")

        summary = profile_summary("muse-max")
        self.assertEqual(summary["companion"]["harness"], "codex")
        for worker in MUSE_ROLES:
            self.assertEqual(summary[worker]["harness"], "muse-code")

    def test_mixed_profile_renders_only_internal_companion(self) -> None:
        executor_source = (PACKAGE / "agents" / "default_executor.toml").read_text(
            encoding="utf-8"
        )
        executor_rendered = render_worker_for_profile(
            executor_source, "default_executor", "muse-max"
        )
        self.assertEqual(executor_rendered, executor_source)

        companion_source = (PACKAGE / "agents" / "companion.toml").read_text(
            encoding="utf-8"
        )
        companion_rendered = render_worker_for_profile(
            companion_source, "companion", "muse-max"
        )
        parsed = tomllib.loads(companion_rendered)
        self.assertEqual(parsed["model"], "gpt-5.6-luna")
        self.assertEqual(parsed["model_reasoning_effort"], "xhigh")

    def test_profile_switch_materializes_mixed_runtime(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            runtime = RuntimePaths(root / "codex-home")
            project = ProjectPaths(root / "project")
            package = PackageLayout.resolve(PACKAGE)
            plan_bootstrap(package, runtime, project).apply()

            plan = plan_compute_profile(runtime, "muse-max")
            self.assertEqual(plan.details["main_agent"], "unchanged")
            self.assertEqual(
                plan.details["worker_harnesses"], ["codex", "muse-code"]
            )
            plan.apply()
            self.assertEqual(read_compute_profile(runtime), "muse-max")
            companion = tomllib.loads(
                (runtime.agents / "companion.toml").read_text(encoding="utf-8")
            )
            self.assertEqual(companion["model"], "gpt-5.6-luna")
            self.assertEqual(companion["model_reasoning_effort"], "xhigh")
            heavy = (runtime.runtime / "heavy_route.md").read_text(encoding="utf-8")
            self.assertIn("normal concise commentary", heavy)
            self.assertNotIn("## Silent Orchestration", heavy)

    def test_other_profile_allocations_are_unchanged_and_codex_backed(self) -> None:
        expected = {
            "plus": {
                "micro_executor": ("gpt-5.6-luna", "high"),
                "default_executor": ("gpt-5.6-luna", "max"),
                "senior_executor": ("gpt-5.6-sol", "medium"),
                "tester": ("gpt-5.6-luna", "max"),
                "archivist": ("gpt-5.6-luna", "max"),
                "companion": ("gpt-5.6-luna", "max"),
                "investigator": ("gpt-5.6-luna", "max"),
            },
            "luna-xhigh": {
                "micro_executor": ("gpt-5.6-luna", "xhigh"),
                "default_executor": ("gpt-5.6-luna", "xhigh"),
                "senior_executor": ("gpt-5.6-sol", "medium"),
                "tester": ("gpt-5.6-luna", "xhigh"),
                "archivist": ("gpt-5.6-luna", "xhigh"),
                "companion": ("gpt-5.6-luna", "xhigh"),
                "investigator": ("gpt-5.6-luna", "xhigh"),
            },
            "pro-x5": {
                "micro_executor": ("gpt-5.6-sol", "low"),
                "default_executor": ("gpt-5.6-sol", "low"),
                "senior_executor": ("gpt-5.6-sol", "medium"),
                "tester": ("gpt-5.6-sol", "low"),
                "archivist": ("gpt-5.6-sol", "low"),
                "companion": ("gpt-5.6-sol", "low"),
                "investigator": ("gpt-5.6-sol", "low"),
            },
        }
        for profile_name, workers in expected.items():
            with self.subTest(profile=profile_name):
                actual = COMPUTE_PROFILES[profile_name]
                self.assertEqual(set(actual), set(workers))
                for worker, pair in workers.items():
                    spec = actual[worker]
                    self.assertEqual((spec.model, spec.reasoning_effort), pair)
                    self.assertEqual(spec.harness, "codex")

    def test_build_command_uses_profile_supplied_model_and_effort(self) -> None:
        command = build_command(
            "/usr/local/bin/muse",
            "/tmp/prompt.md",
            model="profile-model",
            reasoning_effort="profile-effort",
        )
        self.assertEqual(
            command,
            [
                "/usr/local/bin/muse",
                "exec",
                "--disable-approval",
                "--trust-workspace",
                "--model",
                "profile-model",
                "--reasoning-effort",
                "profile-effort",
                "--prompt-file",
                "/tmp/prompt.md",
            ],
        )

    def test_runner_honors_codex_home_and_rejects_non_muse_allocations(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            runtime = RuntimePaths(root / "custom-codex-home")
            project = ProjectPaths(root / "project")
            package = PackageLayout.resolve(PACKAGE)
            plan_bootstrap(package, runtime, project).apply()
            plan_compute_profile(runtime, "muse-max").apply()

            workspace = root / "workspace"
            workspace.mkdir()
            task = root / "task.md"
            task.write_text(
                "Task ID: M06-T01\nDo the bounded test.",
                encoding="utf-8",
            )

            with patch.dict(
                os.environ,
                {"CODEX_HOME": str(runtime.codex_home)},
                clear=False,
            ):
                with patch(
                    "runtime.muse_worker.shutil.which",
                    return_value="/usr/local/bin/muse",
                ):
                    output = io.StringIO()
                    with redirect_stdout(output):
                        result = run(
                            "default_executor",
                            str(workspace),
                            str(task),
                            dry_run=True,
                        )
                    self.assertEqual(result, 0)
                    payload = json.loads(output.getvalue())
                    self.assertEqual(payload["profile"], "muse-max")
                    self.assertEqual(payload["harness"], "muse-code")
                    self.assertEqual(
                        payload["model"],
                        "muse-spark-1.3-contributor",
                    )
                    self.assertEqual(payload["reasoning_effort"], "max")

                    with self.assertRaisesRegex(
                        MuseWorkerError,
                        "not assigned to muse-code",
                    ):
                        run(
                            "companion",
                            str(workspace),
                            str(task),
                            dry_run=True,
                        )

                plan_compute_profile(runtime, "plus").apply()
                with self.assertRaisesRegex(
                    MuseWorkerError,
                    "not assigned to muse-code",
                ):
                    run(
                        "default_executor",
                        str(workspace),
                        str(task),
                        dry_run=True,
                    )

    def test_active_docs_describe_mixed_harness_semantics(self) -> None:
        docs = [
            ROOT / "README.md",
            PACKAGE / "AGENTS.md",
            PACKAGE / "heavy_route.md",
            PACKAGE / "delegation.md",
            PACKAGE / "operate" / "profile.md",
        ]
        combined = "\n".join(
            path.read_text(encoding="utf-8")
            for path in docs
        )
        self.assertNotIn("all seven", combined)
        self.assertNotIn("one-shot Muse Companion", combined)
        self.assertNotIn(
            "every workflow worker role is an external",
            combined,
        )
        self.assertIn("GPT-5.6 Luna XHigh", combined)
        self.assertIn("six", combined.lower())
        self.assertIn("logical worker/session", combined)
        self.assertIn("--logical-worker-id", combined)
        self.assertIn("--resume", combined)
        self.assertNotIn("one-shot", combined)
        self.assertNotIn("Project Workflow/Main", combined)


if __name__ == "__main__":
    unittest.main()
