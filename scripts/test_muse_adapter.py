#!/usr/bin/env python3
"""Deterministic tests for the Muse process/result adapter."""

from __future__ import annotations

import json
import os
import stat
import sys
import tempfile
import threading
import time
import unittest
import uuid
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "codex_workflow"
if str(PACKAGE) not in sys.path:
    sys.path.insert(0, str(PACKAGE))

from runtime.compute_profiles import plan_compute_profile  # noqa: E402
from runtime.layout import PackageLayout, ProjectPaths, RuntimePaths  # noqa: E402
from runtime.lifecycle import plan_bootstrap  # noqa: E402
from runtime.muse_worker import (  # noqa: E402
    MuseWorkerError,
    MuseWorkerInvocation,
    _failure_kind,
    build_command,
    enforce_retention,
    execute_worker,
    execute_workers_concurrently,
)


FAKE_MUSE = r'''#!/usr/bin/env python3
import json
import os
import subprocess
import sys
import time
from pathlib import Path


def value(flag):
    index = sys.argv.index(flag)
    return sys.argv[index + 1]


if len(sys.argv) > 1 and sys.argv[1] == "export":
    if os.environ.get("FAKE_MUSE_EXPORT_MODE", "success") == "missing":
        print("no retained session log found", file=sys.stderr, flush=True)
        raise SystemExit(1)
    print("{}", flush=True)
    raise SystemExit(0)

schema = json.loads(Path(value("--output-schema")).read_text(encoding="utf-8"))
role = schema["properties"]["role"]["enum"][0]
task_id = schema["properties"]["task_id"]["enum"][0]
workspace = Path(value("--workspace"))
mode = os.environ.get("FAKE_MUSE_MODE", "success")
mode_file = workspace / ".fake-muse-mode"
if mode_file.is_file():
    mode = mode_file.read_text(encoding="utf-8").strip()

report = {
    "schema_version": "1",
    "task_id": task_id,
    "role": role,
    "summary": "bounded fake worker summary",
    "blocking_findings": [],
    "decision_requirement": None,
    "verification": [
        {"check": "fixture", "status": "pass", "evidence": "fake process"}
    ],
    "limitations": [],
    "verdict": "GREEN" if role == "tester" else None,
}

configured = {
    "payload_type": "run.model.configured",
    "payload": {"model_id": "muse-spark-1.3-contributor", "provider": "meta"},
}
print(json.dumps(configured), flush=True)

if mode in {"success", "barrier", "hold"}:
    if mode == "barrier":
        barrier = Path(os.environ["FAKE_MUSE_BARRIER_DIR"])
        barrier.mkdir(parents=True, exist_ok=True)
        (barrier / ("ready-" + workspace.name)).write_text("ready", encoding="utf-8")
        deadline = time.monotonic() + 3.0
        while len(list(barrier.glob("ready-*"))) < 2:
            if time.monotonic() >= deadline:
                print("barrier peer did not start", file=sys.stderr, flush=True)
                raise SystemExit(4)
            time.sleep(0.02)
    if mode == "hold":
        (workspace / "hold.started").write_text("started", encoding="utf-8")
        time.sleep(0.75)
    terminal = {
        "payload_type": "run.terminal.completed",
        "payload": {
            "kind": "run_terminal",
            "terminal": "completed",
            "reason": None,
            "text": json.dumps(report, separators=(",", ":")),
        },
    }
    print(json.dumps(terminal), flush=True)
    print("fake diagnostic", file=sys.stderr, flush=True)
    raise SystemExit(0)

if mode == "secret":
    report["summary"] = "api_key=SUPERSECRET123456789"
    terminal = {
        "payload_type": "run.terminal.completed",
        "payload": {
            "kind": "run_terminal",
            "terminal": "completed",
            "reason": None,
            "text": json.dumps(report, separators=(",", ":")),
        },
    }
    print(json.dumps(terminal), flush=True)
    raise SystemExit(0)

if mode == "bad_report":
    terminal = {
        "payload_type": "run.terminal.completed",
        "payload": {
            "kind": "run_terminal",
            "terminal": "completed",
            "reason": None,
            "text": "{}",
        },
    }
    print(json.dumps(terminal), flush=True)
    raise SystemExit(0)

if mode == "missing_terminal":
    print(
        json.dumps(
            {
                "payload_type": "task.lifecycle.completed",
                "payload": {"kind": "task_lifecycle"},
            }
        ),
        flush=True,
    )
    raise SystemExit(0)

if mode == "malformed_json":
    print("{not-json", flush=True)
    raise SystemExit(0)

if mode == "model_failure":
    terminal = {
        "payload_type": "run.terminal.failed",
        "payload": {
            "kind": "run_terminal",
            "terminal": "failed",
            "reason": "model provider rejected requested model",
            "text": "",
        },
    }
    print(json.dumps(terminal), flush=True)
    print("provider model failure", file=sys.stderr, flush=True)
    raise SystemExit(1)

if mode == "auth_failure":
    print("login credential missing", file=sys.stderr, flush=True)
    raise SystemExit(1)

if mode == "child":
    child = subprocess.Popen(
        [sys.executable, "-c", "import time; time.sleep(60)"],
        start_new_session=True,
    )
    (workspace / "child.pid").write_text(str(child.pid), encoding="utf-8")
    print(
        json.dumps(
            {
                "payload_type": "task.lifecycle.started",
                "payload": {"kind": "task_lifecycle"},
            }
        ),
        flush=True,
    )
    time.sleep(60)
    raise SystemExit(0)

raise SystemExit(3)
'''


def _wait_dead(pid: int, timeout: float = 2.0) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if not Path(f"/proc/{pid}").exists():
            return True
        time.sleep(0.05)
    return not Path(f"/proc/{pid}").exists()


class AdapterFixture:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.runtime = RuntimePaths(root / "codex-home")
        self.project = ProjectPaths(root / "project")
        package = PackageLayout.resolve(PACKAGE)
        plan_bootstrap(package, self.runtime, self.project).apply()
        plan_compute_profile(self.runtime, "muse-max").apply()

        self.workspace = root / "workspace"
        self.workspace.mkdir()
        self.task = self.workspace / "M07-T01.md"
        self.task.write_text("Perform the bounded fixture task.\n", encoding="utf-8")
        self.fake_muse = root / "fake-muse"
        self.fake_muse.write_text(FAKE_MUSE, encoding="utf-8")
        self.fake_muse.chmod(0o755)

    def execute(
        self,
        role: str = "default_executor",
        *,
        mode: str = "success",
        timeout: float = 3.0,
        cancel_event: threading.Event | None = None,
        grace: float = 0.15,
        logical_worker_id: str | None = None,
        caller_scope: str | None = None,
        resume: bool = False,
        invocation_id: str | None = None,
    ):
        with patch.dict(os.environ, {"FAKE_MUSE_MODE": mode}, clear=False):
            return execute_worker(
                role,
                str(self.workspace),
                str(self.task),
                task_id="M07-T01",
                timeout_seconds=timeout,
                cancel_event=cancel_event,
                terminate_grace_seconds=grace,
                runtime=self.runtime,
                muse_path=str(self.fake_muse),
                logical_worker_id=logical_worker_id,
                caller_scope=caller_scope,
                resume=resume,
                invocation_id=invocation_id,
            )

    def artifact(self, result, key: str) -> Path:
        return self.runtime.codex_home / result["artifacts"][key]


class MuseAdapterTests(unittest.TestCase):
    def test_build_command_binds_m05_machine_surface(self) -> None:
        command = build_command(
            "/usr/local/bin/muse",
            "/tmp/prompt.md",
            model="profile-model",
            reasoning_effort="profile-effort",
            workspace="/repo",
            schema_file="/tmp/schema.json",
            session_id="00000000-0000-0000-0000-000000000001",
        )
        self.assertEqual(command[:2], ["/usr/local/bin/muse", "exec"])
        self.assertIn("--json", command)
        self.assertIn("--output-schema", command)
        self.assertIn("--session-id", command)
        self.assertIn("--user-input-auto-resolve", command)
        self.assertIn("--disable-sandbox", command)
        self.assertEqual(command[command.index("--model") + 1], "profile-model")
        self.assertEqual(
            command[command.index("--reasoning-effort") + 1],
            "profile-effort",
        )
        self.assertEqual(command[command.index("--workspace") + 1], "/repo")

    def test_cli_usage_failure_is_adapter_internal_even_if_help_mentions_login(self) -> None:
        diagnostic = (
            "invalid TUI options: error: unexpected argument '--prompt-file' found\n"
            "Usage: muse [OPTIONS] <COMMAND>\n"
            "Commands: login logout auth"
        )
        self.assertEqual(
            _failure_kind(diagnostic, default="protocol"),
            "adapter_internal",
        )

    def test_success_returns_one_bounded_result_and_private_raw_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture = AdapterFixture(Path(temporary))
            result = fixture.execute()

            self.assertEqual(result["terminal_status"], "completed")
            self.assertIsNone(result["failure_kind"])
            self.assertEqual(result["task_id"], "M07-T01")
            self.assertEqual(result["role"], "default_executor")
            self.assertEqual(result["summary"], "bounded fake worker summary")
            serialized = json.dumps(result)
            self.assertNotIn("run.terminal.completed", serialized)
            self.assertNotIn("fake diagnostic", serialized)

            events = fixture.artifact(result, "events")
            stderr = fixture.artifact(result, "stderr")
            stored = fixture.artifact(result, "result")
            self.assertIn("run.terminal.completed", events.read_text(encoding="utf-8"))
            self.assertIn("fake diagnostic", stderr.read_text(encoding="utf-8"))
            self.assertEqual(json.loads(stored.read_text(encoding="utf-8")), result)
            for path in (events, stderr, stored):
                self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)

            run_dir = events.parent
            self.assertEqual(
                sorted(path.name for path in run_dir.iterdir()),
                ["events.jsonl", "result.json", "stderr.log"],
            )

    def test_tester_requires_and_returns_bounded_verdict(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture = AdapterFixture(Path(temporary))
            result = fixture.execute("tester")
            self.assertEqual(result["terminal_status"], "completed")
            self.assertEqual(result["verdict"], "GREEN")

    def test_completed_run_with_invalid_report_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture = AdapterFixture(Path(temporary))
            result = fixture.execute(mode="bad_report")
            self.assertEqual(result["terminal_status"], "failed")
            self.assertEqual(result["failure_kind"], "normalized_report")

    def test_missing_or_malformed_terminal_protocol_fails_closed(self) -> None:
        for mode in ("missing_terminal", "malformed_json"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as temporary:
                fixture = AdapterFixture(Path(temporary))
                result = fixture.execute(mode=mode)
                self.assertEqual(result["terminal_status"], "failed")
                self.assertEqual(result["failure_kind"], "protocol")

    def test_model_and_auth_failures_are_distinct(self) -> None:
        cases = {
            "model_failure": "muse_model",
            "auth_failure": "auth_runtime",
        }
        for mode, expected in cases.items():
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as temporary:
                fixture = AdapterFixture(Path(temporary))
                result = fixture.execute(mode=mode)
                self.assertEqual(result["terminal_status"], "failed")
                self.assertEqual(result["failure_kind"], expected)

    def test_profile_rejection_prevents_companion_muse_launch(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture = AdapterFixture(Path(temporary))
            with self.assertRaisesRegex(MuseWorkerError, "not assigned to muse-code"):
                fixture.execute("companion")

    def test_normalized_result_redacts_obvious_secret_material(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture = AdapterFixture(Path(temporary))
            result = fixture.execute(mode="secret")
            self.assertEqual(result["terminal_status"], "completed")
            self.assertIn("[REDACTED]", result["summary"])
            self.assertNotIn("SUPERSECRET", json.dumps(result))

    def test_timeout_kills_child_in_separate_session(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture = AdapterFixture(Path(temporary))
            result = fixture.execute(mode="child", timeout=0.35, grace=0.1)
            self.assertEqual(result["failure_kind"], "timeout")
            child_pid = int((fixture.workspace / "child.pid").read_text())
            self.assertTrue(_wait_dead(child_pid), f"child {child_pid} survived timeout")

    def test_cancellation_kills_child_in_separate_session(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture = AdapterFixture(Path(temporary))
            cancel = threading.Event()
            timer = threading.Timer(0.25, cancel.set)
            timer.start()
            try:
                result = fixture.execute(
                    mode="child",
                    timeout=5.0,
                    cancel_event=cancel,
                    grace=0.1,
                )
            finally:
                timer.cancel()
            self.assertEqual(result["failure_kind"], "cancelled")
            child_pid = int((fixture.workspace / "child.pid").read_text())
            self.assertTrue(_wait_dead(child_pid), f"child {child_pid} survived cancellation")

    def _batch_invocation(
        self,
        fixture: AdapterFixture,
        workspace: Path,
        task_id: str,
        *,
        cancel_event: threading.Event | None = None,
        run_id: str | None = None,
    ) -> MuseWorkerInvocation:
        workspace.mkdir(exist_ok=True)
        task = workspace / f"{task_id}.md"
        task.write_text("Perform the bounded concurrent fixture task.\n", encoding="utf-8")
        return MuseWorkerInvocation(
            role="default_executor",
            workspace=str(workspace),
            task_file=str(task),
            task_id=task_id,
            timeout_seconds=5.0,
            cancel_event=cancel_event,
            terminate_grace_seconds=0.1,
            runtime=fixture.runtime,
            muse_path=str(fixture.fake_muse),
            run_id=run_id,
        )

    def test_managed_concurrency_starts_two_isolated_lanes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            fixture = AdapterFixture(root)
            barrier = root / "barrier"
            invocations = [
                self._batch_invocation(fixture, root / "lane-a", "M09-A"),
                self._batch_invocation(fixture, root / "lane-b", "M09-B"),
            ]
            with patch.dict(
                os.environ,
                {"FAKE_MUSE_MODE": "barrier", "FAKE_MUSE_BARRIER_DIR": str(barrier)},
                clear=False,
            ):
                results = execute_workers_concurrently(invocations, max_workers=2)

            self.assertEqual(
                [result["terminal_status"] for result in results],
                ["completed", "completed"],
            )
            self.assertEqual([result["task_id"] for result in results], ["M09-A", "M09-B"])
            event_refs = [result["artifacts"]["events"] for result in results]
            self.assertEqual(len(set(event_refs)), 2)

    def test_managed_concurrency_rejects_overlapping_workspaces_before_launch(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            fixture = AdapterFixture(root)
            parent = root / "lane-parent"
            child = parent / "nested"
            parent.mkdir()
            child.mkdir()
            parent_task = parent / "parent.md"
            child_task = child / "child.md"
            parent_task.write_text("parent\n", encoding="utf-8")
            child_task.write_text("child\n", encoding="utf-8")
            invocations = [
                MuseWorkerInvocation(
                    role="default_executor",
                    workspace=str(parent),
                    task_file=str(parent_task),
                    task_id="M09-parent",
                    runtime=fixture.runtime,
                    muse_path=str(fixture.fake_muse),
                ),
                MuseWorkerInvocation(
                    role="default_executor",
                    workspace=str(child),
                    task_file=str(child_task),
                    task_id="M09-child",
                    runtime=fixture.runtime,
                    muse_path=str(fixture.fake_muse),
                ),
            ]
            with self.assertRaisesRegex(MuseWorkerError, "non-overlapping workspaces"):
                execute_workers_concurrently(invocations, max_workers=2)

    def test_concurrent_lane_failure_does_not_cancel_healthy_lane(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            fixture = AdapterFixture(root)
            failing = root / "lane-fail"
            healthy = root / "lane-healthy"
            invocations = [
                self._batch_invocation(fixture, failing, "M09-fail"),
                self._batch_invocation(fixture, healthy, "M09-healthy"),
            ]
            (failing / ".fake-muse-mode").write_text("model_failure", encoding="utf-8")
            results = execute_workers_concurrently(invocations, max_workers=2)
            self.assertEqual(results[0]["terminal_status"], "failed")
            self.assertEqual(results[0]["failure_kind"], "muse_model")
            self.assertEqual(results[1]["terminal_status"], "completed")
            self.assertTrue(fixture.artifact(results[1], "result").is_file())

    def test_concurrent_lane_cancel_does_not_cancel_healthy_lane(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            fixture = AdapterFixture(root)
            cancelled = root / "lane-cancel"
            healthy = root / "lane-healthy"
            cancel_event = threading.Event()
            invocations = [
                self._batch_invocation(
                    fixture,
                    cancelled,
                    "M09-cancel",
                    cancel_event=cancel_event,
                ),
                self._batch_invocation(fixture, healthy, "M09-healthy"),
            ]
            (cancelled / ".fake-muse-mode").write_text("child", encoding="utf-8")
            timer = threading.Timer(0.25, cancel_event.set)
            timer.start()
            try:
                results = execute_workers_concurrently(invocations, max_workers=2)
            finally:
                timer.cancel()
            self.assertEqual(results[0]["failure_kind"], "cancelled")
            self.assertEqual(results[1]["terminal_status"], "completed")
            child_pid = int((cancelled / "child.pid").read_text())
            self.assertTrue(_wait_dead(child_pid), f"child {child_pid} survived cancellation")

    def test_concurrent_active_runs_are_retention_protected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            fixture = AdapterFixture(root)
            runs_root = fixture.runtime.runtime / "muse_runs"
            runs_root.mkdir(parents=True, exist_ok=True)
            for index in range(50):
                run_dir = runs_root / str(uuid.UUID(int=index + 1))
                run_dir.mkdir()
                (run_dir / "events.jsonl").write_text("old", encoding="utf-8")

            run_ids = [str(uuid.uuid4()), str(uuid.uuid4())]
            invocations = [
                self._batch_invocation(
                    fixture,
                    root / "lane-a",
                    "M09-A",
                    run_id=run_ids[0],
                ),
                self._batch_invocation(
                    fixture,
                    root / "lane-b",
                    "M09-B",
                    run_id=run_ids[1],
                ),
            ]
            barrier = root / "barrier"
            with patch.dict(
                os.environ,
                {"FAKE_MUSE_MODE": "barrier", "FAKE_MUSE_BARRIER_DIR": str(barrier)},
                clear=False,
            ):
                results = execute_workers_concurrently(invocations, max_workers=2)

            self.assertEqual(
                [result["terminal_status"] for result in results],
                ["completed", "completed"],
            )
            self.assertTrue(all((runs_root / run_id).is_dir() for run_id in run_ids))
            self.assertLessEqual(len(list(runs_root.iterdir())), 50)

    def test_retention_is_bounded_by_age_count_and_size(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            now = time.time()
            runs: list[Path] = []
            for index in range(4):
                run_dir = root / str(uuid.UUID(int=index + 1))
                run_dir.mkdir()
                (run_dir / "events.jsonl").write_bytes(b"x" * 20)
                timestamp = now - index
                os.utime(run_dir, (timestamp, timestamp))
                runs.append(run_dir)

            enforce_retention(
                root,
                now=now,
                max_runs=3,
                max_age_seconds=1000,
                max_bytes=45,
            )
            remaining = [path for path in runs if path.exists()]
            self.assertLessEqual(len(remaining), 2)
            self.assertLessEqual(
                sum((path / "events.jsonl").stat().st_size for path in remaining),
                45,
            )

            old = root / str(uuid.uuid4())
            old.mkdir()
            (old / "events.jsonl").write_text("old", encoding="utf-8")
            os.utime(old, (now - 100, now - 100))
            enforce_retention(
                root,
                now=now,
                max_runs=50,
                max_age_seconds=10,
                max_bytes=10_000,
            )
            self.assertFalse(old.exists())


    def test_stateful_resume_reuses_session_with_unique_invocations(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture = AdapterFixture(Path(temporary))
            first = fixture.execute(
                logical_worker_id="A1",
                caller_scope="M10:lane-a",
            )
            second = fixture.execute(
                logical_worker_id="A1",
                caller_scope="M10:lane-a",
                resume=True,
            )

            self.assertEqual(first["terminal_status"], "completed")
            self.assertEqual(second["terminal_status"], "completed")
            self.assertFalse(first["runtime"]["resumed"])
            self.assertTrue(second["runtime"]["resumed"])
            self.assertEqual(
                first["runtime"]["session_id"],
                second["runtime"]["session_id"],
            )
            self.assertNotEqual(
                first["runtime"]["invocation_id"],
                second["runtime"]["invocation_id"],
            )
            self.assertEqual(first["runtime"]["session_state"], "ready")
            self.assertEqual(second["runtime"]["session_state"], "ready")
            self.assertNotEqual(
                first["runtime"]["session_id"],
                first["runtime"]["invocation_id"],
            )

    def test_executor_and_tester_logical_sessions_are_distinct(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture = AdapterFixture(Path(temporary))
            executor = fixture.execute(
                logical_worker_id="A1",
                caller_scope="M10:lane-a",
            )
            tester = fixture.execute(
                "tester",
                logical_worker_id="B1",
                caller_scope="M10:lane-a",
            )

            self.assertEqual(executor["terminal_status"], "completed")
            self.assertEqual(tester["terminal_status"], "completed")
            self.assertNotEqual(
                executor["runtime"]["logical_worker_id"],
                tester["runtime"]["logical_worker_id"],
            )
            self.assertNotEqual(
                executor["runtime"]["session_id"],
                tester["runtime"]["session_id"],
            )

    def test_resume_binding_rejects_scope_role_and_workspace_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            fixture = AdapterFixture(root)
            first = fixture.execute(
                logical_worker_id="A1",
                caller_scope="M10:lane-a",
            )
            session_id = first["runtime"]["session_id"]

            scope_mismatch = fixture.execute(
                logical_worker_id="A1",
                caller_scope="M10:lane-b",
                resume=True,
            )
            self.assertEqual(
                scope_mismatch["failure_kind"],
                "session_binding_mismatch",
            )
            self.assertIsNone(scope_mismatch["runtime"]["session_id"])

            other_lane = fixture.execute(
                logical_worker_id="A1",
                caller_scope="M10:lane-b",
            )
            self.assertEqual(other_lane["terminal_status"], "completed")
            self.assertNotEqual(other_lane["runtime"]["session_id"], session_id)

            role_mismatch = fixture.execute(
                "tester",
                logical_worker_id="A1",
                caller_scope="M10:lane-a",
                resume=True,
            )
            self.assertEqual(
                role_mismatch["failure_kind"],
                "session_binding_mismatch",
            )

            other_workspace = root / "other-workspace"
            other_workspace.mkdir()
            other_task = other_workspace / "M07-T01.md"
            other_task.write_text("Perform the bounded fixture task.\n", encoding="utf-8")
            workspace_mismatch = execute_worker(
                "default_executor",
                str(other_workspace),
                str(other_task),
                task_id="M07-T01",
                runtime=fixture.runtime,
                muse_path=str(fixture.fake_muse),
                logical_worker_id="A1",
                caller_scope="M10:lane-a",
                resume=True,
            )
            self.assertEqual(
                workspace_mismatch["failure_kind"],
                "session_binding_mismatch",
            )

    def test_unavailable_resume_fails_closed_and_replacement_is_explicit(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture = AdapterFixture(Path(temporary))
            first = fixture.execute(
                logical_worker_id="A1",
                caller_scope="M10:lane-a",
            )
            with patch.dict(
                os.environ,
                {"FAKE_MUSE_EXPORT_MODE": "missing"},
                clear=False,
            ):
                failed_resume = fixture.execute(
                    logical_worker_id="A1",
                    caller_scope="M10:lane-a",
                    resume=True,
                )

            self.assertEqual(failed_resume["terminal_status"], "failed")
            self.assertEqual(failed_resume["failure_kind"], "session_unavailable")
            self.assertEqual(
                failed_resume["runtime"]["session_id"],
                first["runtime"]["session_id"],
            )

            replacement = fixture.execute(
                logical_worker_id="A2",
                caller_scope="M10:lane-a",
            )
            self.assertEqual(replacement["terminal_status"], "completed")
            self.assertNotEqual(
                replacement["runtime"]["session_id"],
                first["runtime"]["session_id"],
            )
            self.assertEqual(replacement["runtime"]["logical_worker_id"], "A2")

    def test_session_lease_rejects_overlapping_turn_for_same_worker(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture = AdapterFixture(Path(temporary))
            first_result: list[dict] = []

            def run_first() -> None:
                first_result.append(
                    fixture.execute(
                        mode="hold",
                        logical_worker_id="A1",
                        caller_scope="M10:lane-a",
                    )
                )

            thread = threading.Thread(target=run_first)
            thread.start()
            marker = fixture.workspace / "hold.started"
            deadline = time.monotonic() + 2.0
            while not marker.exists() and time.monotonic() < deadline:
                time.sleep(0.02)
            self.assertTrue(marker.exists(), "first Muse turn never acquired the session")

            overlapping = fixture.execute(
                logical_worker_id="A1",
                caller_scope="M10:lane-a",
                resume=True,
            )
            thread.join(timeout=3.0)
            self.assertFalse(thread.is_alive())
            self.assertEqual(first_result[0]["terminal_status"], "completed")
            self.assertEqual(overlapping["terminal_status"], "failed")
            self.assertEqual(overlapping["failure_kind"], "session_busy")

    def test_interrupted_turn_can_resume_same_session_after_probe(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture = AdapterFixture(Path(temporary))
            interrupted = fixture.execute(
                mode="child",
                timeout=0.35,
                grace=0.1,
                logical_worker_id="A1",
                caller_scope="M10:lane-a",
            )
            self.assertEqual(interrupted["failure_kind"], "timeout")
            self.assertEqual(
                interrupted["runtime"]["session_state"],
                "needs_probe",
            )
            child_pid = int((fixture.workspace / "child.pid").read_text())
            self.assertTrue(_wait_dead(child_pid), f"child {child_pid} survived timeout")

            resumed = fixture.execute(
                logical_worker_id="A1",
                caller_scope="M10:lane-a",
                resume=True,
            )
            self.assertEqual(resumed["terminal_status"], "completed")
            self.assertTrue(resumed["runtime"]["resumed"])
            self.assertEqual(
                resumed["runtime"]["session_id"],
                interrupted["runtime"]["session_id"],
            )
            self.assertEqual(resumed["runtime"]["session_state"], "ready")

    def test_unconfirmed_cleanup_quarantines_workspace_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture = AdapterFixture(Path(temporary))
            with patch(
                "runtime.muse_worker._run_process",
                return_value=(None, "timeout", [], False),
            ):
                interrupted = fixture.execute(
                    logical_worker_id="A1",
                    caller_scope="M10:lane-a",
                )

            self.assertEqual(interrupted["terminal_status"], "failed")
            self.assertEqual(interrupted["failure_kind"], "adapter_internal")
            self.assertEqual(
                interrupted["runtime"]["session_state"],
                "cleanup_unconfirmed",
            )

            resumed = fixture.execute(
                logical_worker_id="A1",
                caller_scope="M10:lane-a",
                resume=True,
            )
            self.assertEqual(resumed["terminal_status"], "failed")
            self.assertEqual(resumed["failure_kind"], "session_busy")

            replacement = fixture.execute(
                logical_worker_id="A2",
                caller_scope="M10:lane-a",
            )
            self.assertEqual(replacement["terminal_status"], "failed")
            self.assertEqual(replacement["failure_kind"], "session_busy")
            self.assertIn("quarantined", replacement["summary"])

    def test_persistence_failure_stale_active_blocks_later_process_reuse(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            env = os.environ.copy()
            pythonpath = [str(PACKAGE), str(ROOT / "scripts")]
            if env.get("PYTHONPATH"):
                pythonpath.append(env["PYTHONPATH"])
            env["PYTHONPATH"] = os.pathsep.join(pythonpath)
            child = r"""
import sys
from pathlib import Path
from unittest.mock import patch

import test_muse_adapter as fixture_module
import runtime.muse_sessions as muse_sessions

root = Path(sys.argv[1])
fixture = fixture_module.AdapterFixture(root)
real_save = muse_sessions._save_registry

def fail_quarantine(runtime, registry):
    if any(
        isinstance(record, dict)
        and record.get("state") == "cleanup_unconfirmed"
        for record in registry["workers"].values()
    ):
        raise OSError("simulated registry persistence failure")
    return real_save(runtime, registry)

try:
    with patch(
        "runtime.muse_worker._run_process",
        return_value=(None, "timeout", [], False),
    ), patch(
        "runtime.muse_sessions._save_registry",
        side_effect=fail_quarantine,
    ):
        fixture.execute(logical_worker_id="A1", caller_scope="M10:lane-a")
except OSError:
    pass
else:
    raise SystemExit("expected quarantine persistence failure")
"""
            completed = subprocess.run(
                [sys.executable, "-c", child, str(root)],
                cwd=ROOT,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(
                completed.returncode,
                0,
                completed.stdout + completed.stderr,
            )

            runtime = RuntimePaths(root / "codex-home")
            registry = json.loads(
                (runtime.runtime / "muse_sessions" / "registry.json").read_text(
                    encoding="utf-8"
                )
            )
            record = next(iter(registry["workers"].values()))
            self.assertEqual(record["state"], "active")

            resumed = execute_worker(
                "default_executor",
                str(root / "workspace"),
                str(root / "workspace" / "M07-T01.md"),
                task_id="M07-T01",
                runtime=runtime,
                muse_path=str(root / "fake-muse"),
                logical_worker_id="A1",
                caller_scope="M10:lane-a",
                resume=True,
            )
            self.assertEqual(resumed["terminal_status"], "failed")
            self.assertEqual(resumed["failure_kind"], "session_busy")
            self.assertIn("unreconciled active", resumed["summary"])

            replacement = execute_worker(
                "default_executor",
                str(root / "workspace"),
                str(root / "workspace" / "M07-T01.md"),
                task_id="M07-T01",
                runtime=runtime,
                muse_path=str(root / "fake-muse"),
                logical_worker_id="A2",
                caller_scope="M10:lane-a",
            )
            self.assertEqual(replacement["terminal_status"], "failed")
            self.assertEqual(replacement["failure_kind"], "session_busy")
            self.assertIn("unreconciled active", replacement["summary"])

    def test_session_registry_and_leases_are_private(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture = AdapterFixture(Path(temporary))
            result = fixture.execute(
                logical_worker_id="A1",
                caller_scope="M10:lane-a",
            )
            self.assertEqual(result["terminal_status"], "completed")
            root = fixture.runtime.runtime / "muse_sessions"
            registry = root / "registry.json"
            lock = root / "locks" / f"{result['runtime']['session_id']}.lock"
            self.assertEqual(stat.S_IMODE(root.stat().st_mode), 0o700)
            self.assertEqual(stat.S_IMODE(registry.stat().st_mode), 0o600)
            self.assertEqual(stat.S_IMODE(lock.stat().st_mode), 0o600)
            stored = json.loads(registry.read_text(encoding="utf-8"))
            self.assertEqual(stored["schema_version"], "1")
            self.assertLessEqual(len(stored["workers"]), 256)


if __name__ == "__main__":
    unittest.main()
