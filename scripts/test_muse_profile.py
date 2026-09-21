"""Focused regression coverage for the Muse Max worker profile."""

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
    render_heavy_route_for_profile,
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
    "explorer",
    "investigator",
    "default_executor",
    "senior_executor",
    "tester",
    "archivist",
}


def _configure_cliproxyapi(runtime: RuntimePaths) -> None:
    with runtime.config_toml.open("a", encoding="utf-8") as handle:
        handle.write(
            '\n[model_providers.cliproxyapi]\n'
            'name = "CLIProxyAPI"\n'
            'base_url = "http://127.0.0.1:8317/v1"\n'
            'wire_api = "responses"\n'
        )


class MuseMaxProfileTests(unittest.TestCase):
    def test_muse_max_routes_all_six_workers_through_muse(self) -> None:
        profile = COMPUTE_PROFILES["muse-max"]
        self.assertEqual(set(profile), set(BUILTIN_WORKERS))
        self.assertEqual(set(profile), MUSE_ROLES)
        for worker in MUSE_ROLES:
            with self.subTest(worker=worker):
                spec = profile[worker]
                self.assertEqual(spec.model, "muse-spark-1.3-contributor")
                self.assertEqual(spec.reasoning_effort, "max")
                self.assertEqual(spec.harness, "muse-code")

        summary = profile_summary("muse-max")
        for worker in MUSE_ROLES:
            self.assertEqual(summary[worker]["harness"], "muse-code")

    def test_muse_profile_keeps_external_worker_templates_dormant(self) -> None:
        for worker in ("explorer", "default_executor"):
            with self.subTest(worker=worker):
                source = (PACKAGE / "agents" / f"{worker}.toml").read_text(
                    encoding="utf-8"
                )
                rendered = render_worker_for_profile(source, worker, "muse-max")
                self.assertEqual(rendered, source)

    def test_profile_switch_materializes_muse_runtime(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            runtime = RuntimePaths(root / "codex-home")
            project = ProjectPaths(root / "project")
            package = PackageLayout.resolve(PACKAGE)
            plan_bootstrap(package, runtime, project).apply()
            plus_config = tomllib.loads(runtime.config_toml.read_text(encoding="utf-8"))
            self.assertTrue(plus_config["agents"]["enabled"])
            self.assertTrue(plus_config["features"]["multi_agent"])

            plan = plan_compute_profile(runtime, "muse-max")
            self.assertEqual(plan.details["main_agent"], "unchanged")
            self.assertEqual(plan.details["worker_harnesses"], ["muse-code"])
            self.assertEqual(plan.details["internal_codex_agents"], "disabled")
            plan.apply()
            self.assertEqual(read_compute_profile(runtime), "muse-max")
            self.assertEqual(
                {path.stem for path in runtime.agents.glob("*.toml")},
                MUSE_ROLES,
            )
            muse_config = tomllib.loads(runtime.config_toml.read_text(encoding="utf-8"))
            self.assertFalse(muse_config["agents"]["enabled"])
            self.assertTrue(muse_config["features"]["multi_agent"])
            heavy = (runtime.runtime / "heavy_route.md").read_text(encoding="utf-8")
            self.assertIn("quiet milestone orchestration", heavy)
            self.assertIn("routine worker starts", heavy)
            self.assertIn("must not by themselves wake Main", heavy)
            self.assertNotIn("normal concise commentary", heavy)
            self.assertNotIn("## Silent Orchestration", heavy)

            plan_compute_profile(runtime, "plus").apply()
            restored = tomllib.loads(runtime.config_toml.read_text(encoding="utf-8"))
            self.assertTrue(restored["agents"]["enabled"])
            self.assertTrue(restored["features"]["multi_agent"])

    def test_profile_communication_policies_are_distinct(self) -> None:
        source = (PACKAGE / "heavy_route.md").read_text(encoding="utf-8")
        plus = render_heavy_route_for_profile(source, "plus")
        muse = render_heavy_route_for_profile(source, "muse-max")

        self.assertIn("keep user-visible updates restrained", plus)
        self.assertNotIn("quiet milestone orchestration", plus)
        self.assertIn("quiet milestone orchestration", muse)
        self.assertIn("routine worker starts", muse)
        self.assertIn("session or recovery bookkeeping", muse)
        self.assertIn("Git/repository bookkeeping", muse)
        self.assertIn("user-meaningful phase changes", muse)
        self.assertIn("blocker that requires user input", muse)
        self.assertIn("material scope/architecture change", muse)
        self.assertIn("not hard silence", muse)
        self.assertIn("must not by themselves wake Main", muse)
        self.assertNotIn("normal concise commentary", muse)
        self.assertNotIn("## Silent Orchestration", muse)

    def test_muse_docs_require_one_cell_event_driven_wait(self) -> None:
        heavy = (PACKAGE / "heavy_route.md").read_text(encoding="utf-8")
        delegation = (PACKAGE / "delegation.md").read_text(encoding="utf-8")

        for source in (heavy, delegation):
            self.assertIn("one outer Code Mode `exec` cell", source)
            self.assertIn("unmanaged background", source)

        self.assertIn("tools.exec_command", heavy)
        self.assertIn("tools.write_stdin", heavy)
        self.assertIn("Do not return to Main solely because", heavy)
        self.assertIn("## Muse event-driven await", delegation)
        self.assertIn("tools.exec_command", delegation)
        self.assertIn("tools.write_stdin", delegation)
        self.assertIn("inside the cell", delegation)
        self.assertIn("Mere healthy-running state may not", delegation)

    def test_plus_routes_all_six_workers_through_codex(self) -> None:
        expected = {
            "explorer": ("gpt-5.6-luna", "max"),
            "investigator": ("gpt-5.6-luna", "max"),
            "default_executor": ("gpt-5.6-luna", "max"),
            "senior_executor": ("gpt-5.6-sol", "medium"),
            "tester": ("gpt-5.6-luna", "max"),
            "archivist": ("gpt-5.6-luna", "max"),
        }
        self.assertEqual(set(COMPUTE_PROFILES), {"plus", "muse-max", "muse-native"})
        actual = COMPUTE_PROFILES["plus"]
        self.assertEqual(set(actual), set(expected))
        for worker, pair in expected.items():
            spec = actual[worker]
            self.assertEqual((spec.model, spec.reasoning_effort), pair)
            self.assertEqual(spec.harness, "codex")

    def test_muse_native_routes_all_six_workers_through_codex_provider(self) -> None:
        profile = COMPUTE_PROFILES["muse-native"]
        self.assertEqual(set(profile), MUSE_ROLES)
        for worker in MUSE_ROLES:
            with self.subTest(worker=worker):
                spec = profile[worker]
                self.assertEqual(spec.model, "muse-spark-1.3-contributor")
                self.assertEqual(spec.reasoning_effort, "max")
                self.assertEqual(spec.harness, "codex")
                self.assertEqual(spec.model_provider, "cliproxyapi")

        summary = profile_summary("muse-native")
        for worker in MUSE_ROLES:
            self.assertEqual(summary[worker]["harness"], "codex")
            self.assertEqual(summary[worker]["model_provider"], "cliproxyapi")

    def test_muse_native_worker_rendering_owns_only_marked_provider(self) -> None:
        source = (PACKAGE / "agents" / "default_executor.toml").read_text(
            encoding="utf-8"
        )
        rendered = render_worker_for_profile(source, "default_executor", "muse-native")
        config = tomllib.loads(rendered)
        self.assertEqual(config["model"], "muse-spark-1.3-contributor")
        self.assertEqual(config["model_reasoning_effort"], "max")
        self.assertEqual(config["model_provider"], "cliproxyapi")
        self.assertEqual(rendered.count("# codex-workflow-model-provider"), 1)

        restored = render_worker_for_profile(rendered, "default_executor", "plus")
        restored_config = tomllib.loads(restored)
        self.assertNotIn("model_provider", restored_config)
        self.assertNotIn("# codex-workflow-model-provider", restored)

        unowned = source.replace(
            'model_reasoning_effort = "max"\n',
            'model_reasoning_effort = "max"\nmodel_provider = "user-owned"\n',
            1,
        )
        with self.assertRaisesRegex(ValidationError, "unowned model_provider"):
            render_worker_for_profile(unowned, "default_executor", "muse-native")

    def test_muse_native_requires_configured_responses_provider_before_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            runtime = RuntimePaths(root / "codex-home")
            project = ProjectPaths(root / "project")
            package = PackageLayout.resolve(PACKAGE)
            plan_bootstrap(package, runtime, project).apply()
            before_config = runtime.config_toml.read_bytes()
            before_settings = runtime.compute_settings.read_bytes()
            before_workers = {
                path.name: path.read_bytes() for path in runtime.agents.glob("*.toml")
            }

            with self.assertRaisesRegex(
                ValidationError,
                r"requires configured \[model_providers\.cliproxyapi\]",
            ):
                plan_compute_profile(runtime, "muse-native")

            self.assertEqual(runtime.config_toml.read_bytes(), before_config)
            self.assertEqual(runtime.compute_settings.read_bytes(), before_settings)
            self.assertEqual(
                {path.name: path.read_bytes() for path in runtime.agents.glob("*.toml")},
                before_workers,
            )

            _configure_cliproxyapi(runtime)
            config_text = runtime.config_toml.read_text(encoding="utf-8")
            runtime.config_toml.write_text(
                config_text.replace('wire_api = "responses"', 'wire_api = "chat"'),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValidationError, 'wire_api = "responses"'):
                plan_compute_profile(runtime, "muse-native")

    def test_switches_muse_native_with_provider_and_restores_plus(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            runtime = RuntimePaths(root / "codex-home")
            project = ProjectPaths(root / "project")
            package = PackageLayout.resolve(PACKAGE)
            plan_bootstrap(package, runtime, project).apply()
            with runtime.config_toml.open("a", encoding="utf-8") as handle:
                handle.write('\n[unrelated]\nkeep = "yes"\n')
            _configure_cliproxyapi(runtime)

            native_plan = plan_compute_profile(runtime, "muse-native")
            self.assertEqual(native_plan.details["worker_harnesses"], ["codex"])
            self.assertEqual(native_plan.details["internal_codex_agents"], "enabled")
            self.assertEqual(
                native_plan.details["provider_routes"],
                [
                    {
                        "model_provider": "cliproxyapi",
                        "configured": "yes",
                        "wire_api": "responses",
                        "credential_owner": "external",
                    }
                ],
            )
            native_plan.apply()
            self.assertEqual(read_compute_profile(runtime), "muse-native")
            config = tomllib.loads(runtime.config_toml.read_text(encoding="utf-8"))
            self.assertTrue(config["agents"]["enabled"])
            self.assertEqual(config["unrelated"]["keep"], "yes")
            self.assertEqual(
                config["model_providers"]["cliproxyapi"]["base_url"],
                "http://127.0.0.1:8317/v1",
            )
            for path in runtime.agents.glob("*.toml"):
                worker_config = tomllib.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(
                    worker_config["model"], "muse-spark-1.3-contributor"
                )
                self.assertEqual(worker_config["model_reasoning_effort"], "max")
                self.assertEqual(worker_config["model_provider"], "cliproxyapi")

            plan_compute_profile(runtime, "muse-max").apply()
            config = tomllib.loads(runtime.config_toml.read_text(encoding="utf-8"))
            self.assertFalse(config["agents"]["enabled"])
            # External muse-max deliberately leaves the installed native worker
            # TOMLs dormant and unchanged.
            self.assertTrue(
                all(
                    tomllib.loads(path.read_text(encoding="utf-8")).get(
                        "model_provider"
                    )
                    == "cliproxyapi"
                    for path in runtime.agents.glob("*.toml")
                )
            )

            plan_compute_profile(runtime, "plus").apply()
            config = tomllib.loads(runtime.config_toml.read_text(encoding="utf-8"))
            self.assertTrue(config["agents"]["enabled"])
            self.assertEqual(config["unrelated"]["keep"], "yes")
            self.assertIn("cliproxyapi", config["model_providers"])
            for path in runtime.agents.glob("*.toml"):
                worker_config = tomllib.loads(path.read_text(encoding="utf-8"))
                self.assertNotIn("model_provider", worker_config)

    def test_muse_native_uses_quiet_profile_communication_policy(self) -> None:
        source = (PACKAGE / "heavy_route.md").read_text(encoding="utf-8")
        rendered = render_heavy_route_for_profile(source, "muse-native")
        self.assertIn("quiet milestone orchestration", rendered)
        self.assertIn("must not by themselves wake Main", rendered)
        self.assertNotIn("restrained and outcome-oriented", rendered)

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

    def test_active_docs_describe_two_profile_harness_semantics(self) -> None:
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
        self.assertNotIn("luna-xhigh", combined)
        self.assertNotIn("pro-x5", combined)
        self.assertNotIn("Companion", combined)
        self.assertNotIn("Micro Executor", combined)
        self.assertIn("six", combined.lower())
        self.assertIn("logical worker/session", combined)
        self.assertIn("--logical-worker-id", combined)
        self.assertIn("--resume", combined)
        self.assertNotIn("one-shot", combined)
        self.assertNotIn("Project Workflow/Main", combined)


if __name__ == "__main__":
    unittest.main()
