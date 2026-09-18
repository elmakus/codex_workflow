"""Run one codex_workflow role through the native Muse Code harness."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time
import uuid
from pathlib import Path
from typing import Any

import tomllib

PACKAGE_ROOT = Path(__file__).resolve().parent.parent
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from runtime.compute_profiles import read_compute_profile, worker_model
from runtime.errors import WorkflowError
from runtime.layout import WORKER_MARKER, RuntimePaths, default_codex_home


ROLE_RE = re.compile(r"^[A-Za-z0-9_-]+$")
TASK_ID_RE = re.compile(r"^[A-Za-z0-9_.:-]{1,128}$")
RESULT_SCHEMA_VERSION = "1"
TERMINAL_TYPES = {"run.terminal.completed", "run.terminal.failed"}
VERDICTS = {"GREEN", "RED", "INCONCLUSIVE"}
CHECK_STATUSES = {"pass", "fail", "not_run", "unknown"}

DEFAULT_TIMEOUT_SECONDS = 30 * 60
TERMINATE_GRACE_SECONDS = 3.0
RETENTION_MAX_RUNS = 50
RETENTION_MAX_AGE_SECONDS = 14 * 24 * 60 * 60
RETENTION_MAX_BYTES = 100 * 1024 * 1024

MAX_SUMMARY_CHARS = 2000
MAX_ITEM_CHARS = 800
MAX_ITEMS = 20
MAX_CHANGED_PATHS = 100
MAX_PATH_CHARS = 400
MAX_DIFF_STAT_CHARS = 4000
MAX_JSONL_LINE_BYTES = 2 * 1024 * 1024
MAX_RAW_STREAM_BYTES = 25 * 1024 * 1024

_SECRET_PATTERNS = (
    re.compile(r"(?i)(authorization\s*:\s*bearer\s+)[^\s]+"),
    re.compile(r"(?i)\b(api[_-]?key|token|secret|password)\s*[:=]\s*[^\s]+"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{16,}\b"),
)


class MuseWorkerError(RuntimeError):
    pass


def _runtime_paths() -> RuntimePaths:
    return RuntimePaths(default_codex_home())


def _muse_allocation(role: str, runtime: RuntimePaths):
    if not ROLE_RE.fullmatch(role):
        raise MuseWorkerError(f"unsafe worker role: {role!r}")
    try:
        profile = read_compute_profile(runtime)
        allocation = worker_model(profile, role)
    except WorkflowError as error:
        raise MuseWorkerError(str(error)) from error
    if allocation.harness != "muse-code":
        raise MuseWorkerError(
            f"worker role {role!r} is not assigned to muse-code in active profile {profile!r}"
        )
    return profile, allocation


def _worker_contract(role: str, runtime: RuntimePaths) -> str:
    if not ROLE_RE.fullmatch(role):
        raise MuseWorkerError(f"unsafe worker role: {role!r}")
    path = runtime.agents / f"{role}.toml"
    if path.is_symlink() or not path.is_file():
        raise MuseWorkerError(f"workflow worker contract is missing: {path}")
    text = path.read_text(encoding="utf-8")
    marker = WORKER_MARKER.search(text)
    if marker is None or marker.group(1) != role:
        raise MuseWorkerError(f"worker ownership marker missing or wrong: {path}")
    try:
        config = tomllib.loads(text)
    except tomllib.TOMLDecodeError as error:
        raise MuseWorkerError(f"invalid worker TOML {path}: {error}") from error
    if config.get("name") != role:
        raise MuseWorkerError(f"worker name does not match requested role: {role}")
    instructions = config.get("developer_instructions")
    if not isinstance(instructions, str) or not instructions.strip():
        raise MuseWorkerError(f"worker has no developer_instructions: {role}")
    return instructions.strip()


def _workspace(path: str) -> Path:
    workspace = Path(path).expanduser().resolve()
    if workspace.is_symlink() or not workspace.is_dir():
        raise MuseWorkerError(f"workspace is not a directory: {workspace}")
    return workspace


def _task(path: str) -> tuple[Path, str]:
    task_path = Path(path).expanduser().resolve()
    if task_path.is_symlink() or not task_path.is_file():
        raise MuseWorkerError(f"task file is not a regular file: {task_path}")
    text = task_path.read_text(encoding="utf-8")
    if not text.strip():
        raise MuseWorkerError("task file is empty")
    return task_path, text.strip()


def _logical_task_id(task_id: str | None, task_path: Path) -> str:
    value = task_id or task_path.stem
    if not TASK_ID_RE.fullmatch(value):
        raise MuseWorkerError(
            "task id must be 1-128 characters using letters, digits, '.', '_', ':', or '-'"
        )
    return value


def worker_report_schema(role: str, task_id: str) -> dict[str, Any]:
    verdict_schema: dict[str, Any]
    if role == "tester":
        verdict_schema = {"type": "string", "enum": sorted(VERDICTS)}
    else:
        verdict_schema = {"type": "null"}
    return {
        "type": "object",
        "additionalProperties": False,
        "required": [
            "schema_version",
            "task_id",
            "role",
            "summary",
            "blocking_findings",
            "decision_requirement",
            "verification",
            "limitations",
            "verdict",
        ],
        "properties": {
            "schema_version": {"type": "string", "enum": [RESULT_SCHEMA_VERSION]},
            "task_id": {"type": "string", "enum": [task_id]},
            "role": {"type": "string", "enum": [role]},
            "summary": {"type": "string", "minLength": 1, "maxLength": MAX_SUMMARY_CHARS},
            "blocking_findings": {
                "type": "array",
                "maxItems": MAX_ITEMS,
                "items": {"type": "string", "maxLength": MAX_ITEM_CHARS},
            },
            "decision_requirement": {
                "type": ["string", "null"],
                "maxLength": MAX_ITEM_CHARS,
            },
            "verification": {
                "type": "array",
                "maxItems": MAX_ITEMS,
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["check", "status", "evidence"],
                    "properties": {
                        "check": {"type": "string", "maxLength": MAX_ITEM_CHARS},
                        "status": {"type": "string", "enum": sorted(CHECK_STATUSES)},
                        "evidence": {"type": "string", "maxLength": MAX_ITEM_CHARS},
                    },
                },
            },
            "limitations": {
                "type": "array",
                "maxItems": MAX_ITEMS,
                "items": {"type": "string", "maxLength": MAX_ITEM_CHARS},
            },
            "verdict": verdict_schema,
        },
    }


def build_prompt(role: str, task_id: str, task: str, runtime: RuntimePaths) -> str:
    contract = _worker_contract(role, runtime)
    verdict_rule = (
        "Set verdict to exactly GREEN, RED, or INCONCLUSIVE."
        if role == "tester"
        else "Set verdict to null."
    )
    return f"""You are a codex_workflow worker running through Muse Code.

ROLE CONTRACT
{contract}

TASK CAPSULE
Logical Task ID: {task_id}

{task}

EXTERNAL-HARNESS EXECUTION RULES
- The Codex Main agent remains the orchestrator. Do not create or coordinate other workers.
- Work only on the assigned role and task capsule.
- Do not modify .git internals or perform commits, pushes, merges, rebases, or branch changes.
- Preserve unrelated user work.
- Use the available repository tools and tests proportionately.
- Do not include chain-of-thought, raw tool streams, large diffs, credentials, or session material in the final report.
- Your final answer must be exactly one JSON object matching the supplied output schema, with no markdown fence or prose around it.
- Use schema_version {RESULT_SCHEMA_VERSION!r}, task_id {task_id!r}, and role {role!r} exactly.
- Keep summary/findings/decision_requirement/checks/limitations concise and evidence-grounded.
- Set decision_requirement to null unless Main/user authority is actually required.
- {verdict_rule}
"""


def build_command(
    muse: str,
    prompt_file: str,
    *,
    model: str,
    reasoning_effort: str,
    workspace: str | None = None,
    schema_file: str | None = None,
    session_id: str | None = None,
) -> list[str]:
    command = [
        muse,
        "--disable-approval",
        "--trust-workspace",
        "exec",
        "--model",
        model,
        "--reasoning-effort",
        reasoning_effort,
        "--prompt-file",
        prompt_file,
    ]
    advanced = (workspace, schema_file, session_id)
    if any(value is not None for value in advanced):
        if not all(value is not None for value in advanced):
            raise MuseWorkerError(
                "workspace, schema_file, and session_id must be supplied together"
            )
        command.extend(
            [
                "--workspace",
                str(workspace),
                "--json",
                "--output-schema",
                str(schema_file),
                "--session-id",
                str(session_id),
                "--user-input-auto-resolve",
                "--disable-sandbox",
            ]
        )
    return command


def _runs_root(runtime: RuntimePaths) -> Path:
    return runtime.runtime / "muse_runs"


def _safe_run_id(value: str | None = None) -> str:
    if value is None:
        return str(uuid.uuid4())
    try:
        parsed = uuid.UUID(value)
    except ValueError as error:
        raise MuseWorkerError(f"invalid run id: {value!r}") from error
    if str(parsed) != value.lower():
        raise MuseWorkerError(f"run id is not canonical UUID text: {value!r}")
    return str(parsed)


def _ensure_private_dir(path: Path) -> None:
    if path.is_symlink():
        raise MuseWorkerError(f"runtime artifact path must not be a symlink: {path}")
    path.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(path, 0o700)


def _touch_private(path: Path) -> None:
    fd = os.open(path, os.O_CREAT | os.O_WRONLY | os.O_TRUNC, 0o600)
    os.close(fd)


def _write_private_text(path: Path, text: str) -> None:
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
        os.replace(temporary, path)
        os.chmod(path, 0o600)
    finally:
        try:
            Path(temporary).unlink()
        except FileNotFoundError:
            pass


def _directory_size(path: Path) -> int:
    total = 0
    for entry in path.rglob("*"):
        try:
            if entry.is_symlink() or not entry.is_file():
                continue
            total += entry.stat().st_size
        except FileNotFoundError:
            continue
    return total


def _eligible_run_dirs(root: Path) -> list[Path]:
    result: list[Path] = []
    if not root.is_dir():
        return result
    for entry in root.iterdir():
        if entry.is_symlink() or not entry.is_dir():
            continue
        try:
            if str(uuid.UUID(entry.name)) != entry.name.lower():
                continue
        except ValueError:
            continue
        result.append(entry)
    return result


def enforce_retention(
    root: Path,
    *,
    preserve: set[Path] | None = None,
    now: float | None = None,
    max_runs: int = RETENTION_MAX_RUNS,
    max_age_seconds: int = RETENTION_MAX_AGE_SECONDS,
    max_bytes: int = RETENTION_MAX_BYTES,
) -> None:
    preserve = {path.resolve() for path in (preserve or set())}
    now = time.time() if now is None else now
    runs = _eligible_run_dirs(root)

    for run_dir in list(runs):
        try:
            too_old = now - run_dir.stat().st_mtime > max_age_seconds
        except FileNotFoundError:
            runs.remove(run_dir)
            continue
        if too_old and run_dir.resolve() not in preserve:
            shutil.rmtree(run_dir, ignore_errors=True)
            runs.remove(run_dir)

    runs.sort(key=lambda path: path.stat().st_mtime, reverse=True)
    kept: list[Path] = []
    for index, run_dir in enumerate(runs):
        if index < max_runs or run_dir.resolve() in preserve:
            kept.append(run_dir)
        else:
            shutil.rmtree(run_dir, ignore_errors=True)

    total = sum(_directory_size(path) for path in kept if path.exists())
    for run_dir in reversed(kept):
        if total <= max_bytes:
            break
        if run_dir.resolve() in preserve:
            continue
        size = _directory_size(run_dir)
        shutil.rmtree(run_dir, ignore_errors=True)
        total -= size


def _proc_parent_and_start(pid: int) -> tuple[int, str] | None:
    try:
        text = Path(f"/proc/{pid}/stat").read_text(encoding="utf-8")
    except (FileNotFoundError, PermissionError, ProcessLookupError):
        return None
    close = text.rfind(")")
    if close < 0:
        return None
    fields = text[close + 2 :].split()
    if len(fields) <= 19:
        return None
    try:
        parent = int(fields[1])
    except ValueError:
        return None
    return parent, fields[19]


def _proc_start_time(pid: int) -> str | None:
    identity = _proc_parent_and_start(pid)
    return None if identity is None else identity[1]


def _direct_children(pid: int) -> list[int]:
    result: list[int] = []
    proc = Path("/proc")
    try:
        entries = list(proc.iterdir())
    except OSError:
        return result
    for entry in entries:
        if not entry.name.isdigit():
            continue
        child_pid = int(entry.name)
        identity = _proc_parent_and_start(child_pid)
        if identity is not None and identity[0] == pid:
            result.append(child_pid)
    return result


def _snapshot_process_tree(root_pid: int) -> dict[int, str]:
    snapshot: dict[int, str] = {}
    pending = [root_pid]
    seen: set[int] = set()
    while pending:
        pid = pending.pop()
        if pid in seen:
            continue
        seen.add(pid)
        start_time = _proc_start_time(pid)
        if start_time is None:
            continue
        snapshot[pid] = start_time
        pending.extend(_direct_children(pid))
    return snapshot


def _same_process(pid: int, start_time: str) -> bool:
    return _proc_start_time(pid) == start_time


def _signal_snapshot(snapshot: dict[int, str], sig: int, *, skip: int | None = None) -> None:
    for pid, start_time in sorted(snapshot.items(), reverse=True):
        if pid == skip or not _same_process(pid, start_time):
            continue
        try:
            os.kill(pid, sig)
        except (ProcessLookupError, PermissionError):
            continue


def _tree_is_gone(snapshot: dict[int, str]) -> bool:
    return not any(_same_process(pid, start) for pid, start in snapshot.items())


def _terminate_process_tree(process: subprocess.Popen[bytes], grace_seconds: float) -> None:
    snapshot = _snapshot_process_tree(process.pid)
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except (ProcessLookupError, PermissionError):
        try:
            process.terminate()
        except ProcessLookupError:
            pass
    _signal_snapshot(snapshot, signal.SIGTERM, skip=process.pid)

    deadline = time.monotonic() + max(0.0, grace_seconds)
    while time.monotonic() < deadline:
        if process.poll() is not None and _tree_is_gone(snapshot):
            return
        time.sleep(0.05)

    try:
        os.killpg(process.pid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError):
        try:
            process.kill()
        except ProcessLookupError:
            pass
    _signal_snapshot(snapshot, signal.SIGKILL, skip=process.pid)
    try:
        process.wait(timeout=1.0)
    except subprocess.TimeoutExpired:
        pass


def _copy_stream(stream, destination: Path, errors: list[str]) -> None:
    written = 0
    overflow_reported = False
    try:
        with destination.open("ab", buffering=0) as handle:
            while True:
                chunk = stream.read(65536)
                if not chunk:
                    break
                remaining = MAX_RAW_STREAM_BYTES - written
                if remaining > 0:
                    payload = chunk[:remaining]
                    handle.write(payload)
                    written += len(payload)
                if len(chunk) > max(remaining, 0) and not overflow_reported:
                    errors.append("raw stream exceeded artifact size limit")
                    overflow_reported = True
    except Exception as error:  # pragma: no cover - defensive drain guard
        errors.append(f"{type(error).__name__}: {error}")
    finally:
        try:
            stream.close()
        except Exception:
            pass


def _run_process(
    command: list[str],
    *,
    workspace: Path,
    events_path: Path,
    stderr_path: Path,
    timeout_seconds: float,
    cancel_event: threading.Event | None,
    terminate_grace_seconds: float,
) -> tuple[int | None, str | None, list[str]]:
    drain_errors: list[str] = []
    try:
        process = subprocess.Popen(
            command,
            cwd=workspace,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True,
        )
    except OSError as error:
        return None, f"spawn:{type(error).__name__}", [str(error)]

    assert process.stdout is not None
    assert process.stderr is not None
    threads = [
        threading.Thread(
            target=_copy_stream,
            args=(process.stdout, events_path, drain_errors),
            daemon=True,
        ),
        threading.Thread(
            target=_copy_stream,
            args=(process.stderr, stderr_path, drain_errors),
            daemon=True,
        ),
    ]
    for thread in threads:
        thread.start()

    started = time.monotonic()
    stop_reason: str | None = None
    while process.poll() is None:
        if cancel_event is not None and cancel_event.is_set():
            stop_reason = "cancelled"
            break
        if time.monotonic() - started >= timeout_seconds:
            stop_reason = "timeout"
            break
        time.sleep(0.05)

    if stop_reason is not None:
        _terminate_process_tree(process, terminate_grace_seconds)

    return_code = process.poll()
    if return_code is None:
        try:
            return_code = process.wait(timeout=1.0)
        except subprocess.TimeoutExpired:
            _terminate_process_tree(process, 0.0)
            return_code = process.poll()

    for thread in threads:
        thread.join(timeout=2.0)
    if any(thread.is_alive() for thread in threads):
        drain_errors.append("stream drain thread did not terminate")
    return return_code, stop_reason, drain_errors


def _parse_terminal(events_path: Path) -> tuple[dict[str, Any] | None, str | None]:
    terminals: list[dict[str, Any]] = []
    try:
        with events_path.open("rb") as handle:
            for raw_line in handle:
                line = raw_line.strip()
                if not line:
                    continue
                if len(line) > MAX_JSONL_LINE_BYTES:
                    return None, "JSONL record exceeds adapter limit"
                try:
                    decoded = line.decode("utf-8")
                    record = json.loads(decoded)
                except (UnicodeDecodeError, json.JSONDecodeError):
                    return None, "stdout contains malformed JSONL"
                if not isinstance(record, dict):
                    return None, "stdout JSONL record is not an object"
                if record.get("payload_type") in TERMINAL_TYPES:
                    terminals.append(record)
                    if len(terminals) > 1:
                        return None, "multiple terminal records observed"
    except OSError as error:
        return None, f"cannot read raw event artifact: {error}"

    if not terminals:
        return None, "terminal record is missing"
    terminal = terminals[0]
    payload = terminal.get("payload")
    if not isinstance(payload, dict):
        return None, "terminal payload is missing or invalid"
    expected = (
        "completed"
        if terminal.get("payload_type") == "run.terminal.completed"
        else "failed"
    )
    if payload.get("kind") != "run_terminal" or payload.get("terminal") != expected:
        return None, "terminal record fields are inconsistent"
    return terminal, None


def _bounded_string(value: Any, *, name: str, limit: int, allow_empty: bool = True) -> str:
    if not isinstance(value, str):
        raise MuseWorkerError(f"worker report field {name!r} must be a string")
    if not allow_empty and not value:
        raise MuseWorkerError(f"worker report field {name!r} must not be empty")
    if len(value) > limit:
        raise MuseWorkerError(f"worker report field {name!r} exceeds {limit} characters")
    return value


def _bounded_string_list(value: Any, *, name: str) -> list[str]:
    if not isinstance(value, list) or len(value) > MAX_ITEMS:
        raise MuseWorkerError(f"worker report field {name!r} must be a bounded list")
    return [
        _bounded_string(item, name=f"{name}[{index}]", limit=MAX_ITEM_CHARS)
        for index, item in enumerate(value)
    ]


def _validate_report(
    text: Any,
    *,
    role: str,
    task_id: str,
) -> dict[str, Any]:
    if not isinstance(text, str) or not text.strip():
        raise MuseWorkerError("completed terminal record has no final worker report")
    if len(text) > 64 * 1024:
        raise MuseWorkerError("final worker report exceeds adapter size limit")
    try:
        report = json.loads(text)
    except json.JSONDecodeError as error:
        raise MuseWorkerError("final worker report is not valid JSON") from error
    if not isinstance(report, dict):
        raise MuseWorkerError("final worker report must be a JSON object")

    expected_keys = {
        "schema_version",
        "task_id",
        "role",
        "summary",
        "blocking_findings",
        "decision_requirement",
        "verification",
        "limitations",
        "verdict",
    }
    if set(report) != expected_keys:
        raise MuseWorkerError("final worker report fields do not match schema")
    if report["schema_version"] != RESULT_SCHEMA_VERSION:
        raise MuseWorkerError("final worker report schema_version is unsupported")
    if report["task_id"] != task_id or report["role"] != role:
        raise MuseWorkerError("final worker report identity does not match invocation")

    summary = _bounded_string(
        report["summary"],
        name="summary",
        limit=MAX_SUMMARY_CHARS,
        allow_empty=False,
    )
    findings = _bounded_string_list(report["blocking_findings"], name="blocking_findings")
    decision_requirement = report["decision_requirement"]
    if decision_requirement is not None:
        decision_requirement = _bounded_string(
            decision_requirement,
            name="decision_requirement",
            limit=MAX_ITEM_CHARS,
            allow_empty=False,
        )
    limitations = _bounded_string_list(report["limitations"], name="limitations")

    verification_value = report["verification"]
    if not isinstance(verification_value, list) or len(verification_value) > MAX_ITEMS:
        raise MuseWorkerError("worker report field 'verification' must be a bounded list")
    verification: list[dict[str, str]] = []
    for index, item in enumerate(verification_value):
        if not isinstance(item, dict) or set(item) != {"check", "status", "evidence"}:
            raise MuseWorkerError(f"verification[{index}] fields do not match schema")
        status = item["status"]
        if status not in CHECK_STATUSES:
            raise MuseWorkerError(f"verification[{index}] has unsupported status")
        verification.append(
            {
                "check": _bounded_string(
                    item["check"], name=f"verification[{index}].check", limit=MAX_ITEM_CHARS
                ),
                "status": status,
                "evidence": _bounded_string(
                    item["evidence"],
                    name=f"verification[{index}].evidence",
                    limit=MAX_ITEM_CHARS,
                ),
            }
        )

    verdict = report["verdict"]
    if role == "tester":
        if verdict not in VERDICTS:
            raise MuseWorkerError("tester report verdict must be GREEN, RED, or INCONCLUSIVE")
    elif verdict is not None:
        raise MuseWorkerError("non-tester report verdict must be null")

    return {
        "summary": summary,
        "blocking_findings": findings,
        "decision_requirement": decision_requirement,
        "verification": verification,
        "limitations": limitations,
        "verdict": verdict,
    }


def _redact_text(text: str) -> str:
    value = text
    for pattern in _SECRET_PATTERNS:
        if pattern.pattern.startswith("(?i)(authorization"):
            value = pattern.sub(r"\1[REDACTED]", value)
        elif pattern.pattern.startswith("(?i)\b(api"):
            value = pattern.sub(r"\1=[REDACTED]", value)
        else:
            value = pattern.sub("[REDACTED]", value)
    return value


def _sanitize_report(report: dict[str, Any]) -> dict[str, Any]:
    return {
        "summary": _redact_text(report["summary"]),
        "blocking_findings": [_redact_text(item) for item in report["blocking_findings"]],
        "decision_requirement": (
            None
            if report["decision_requirement"] is None
            else _redact_text(report["decision_requirement"])
        ),
        "verification": [
            {
                "check": _redact_text(item["check"]),
                "status": item["status"],
                "evidence": _redact_text(item["evidence"]),
            }
            for item in report["verification"]
        ],
        "limitations": [_redact_text(item) for item in report["limitations"]],
        "verdict": report["verdict"],
    }


def _read_diagnostic(path: Path, limit: int = 32768) -> str:
    try:
        data = path.read_bytes()[:limit]
    except OSError:
        return ""
    return data.decode("utf-8", errors="replace")


def _failure_kind(text: str, *, default: str) -> str:
    lowered = text.lower()
    if any(word in lowered for word in ("auth", "login", "credential", "unauthorized", "forbidden")):
        return "auth_runtime"
    if any(word in lowered for word in ("model", "provider", "rate limit", "quota")):
        return "muse_model"
    return default



def _git_repository_evidence(workspace: Path) -> dict[str, Any]:
    try:
        probe = subprocess.run(
            ["git", "-C", str(workspace), "rev-parse", "--is-inside-work-tree"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            check=False,
            timeout=5,
            text=True,
        )
    except (OSError, subprocess.TimeoutExpired):
        return {"changed_paths": [], "diff_stat": None, "truncated": False}
    if probe.returncode != 0 or probe.stdout.strip() != "true":
        return {"changed_paths": [], "diff_stat": None, "truncated": False}

    changed_paths: list[str] = []
    truncated = False
    try:
        status = subprocess.run(
            [
                "git",
                "-C",
                str(workspace),
                "status",
                "--porcelain=v1",
                "-z",
                "--untracked-files=all",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            check=False,
            timeout=5,
        )
        records = status.stdout.split(b"\0") if status.returncode == 0 else []
        index = 0
        while index < len(records):
            raw = records[index]
            index += 1
            if not raw:
                continue
            text = raw.decode("utf-8", errors="replace")
            if len(text) < 4:
                continue
            code = text[:2]
            path = text[3:]
            if "R" in code or "C" in code:
                if index < len(records) and records[index]:
                    index += 1
            if len(changed_paths) >= MAX_CHANGED_PATHS:
                truncated = True
                break
            changed_paths.append(_redact_text(path[:MAX_PATH_CHARS]))
    except (OSError, subprocess.TimeoutExpired):
        pass

    stat_parts: list[str] = []
    for cached in (False, True):
        args = ["git", "-C", str(workspace), "diff"]
        if cached:
            args.append("--cached")
        args.extend(["--stat", "--no-ext-diff", "--", "."])
        try:
            completed = subprocess.run(
                args,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                check=False,
                timeout=5,
                text=True,
            )
        except (OSError, subprocess.TimeoutExpired):
            continue
        text = completed.stdout.strip()
        if completed.returncode == 0 and text:
            stat_parts.append(("staged:\n" if cached else "unstaged:\n") + text)
    diff_stat = "\n".join(stat_parts) or None
    if diff_stat is not None and len(diff_stat) > MAX_DIFF_STAT_CHARS:
        diff_stat = diff_stat[: MAX_DIFF_STAT_CHARS - 20] + "\n...[truncated]"
        truncated = True
    if diff_stat is not None:
        diff_stat = _redact_text(diff_stat)

    return {
        "changed_paths": changed_paths,
        "diff_stat": diff_stat,
        "truncated": truncated,
    }


def _artifact_refs(runtime: RuntimePaths, run_id: str) -> dict[str, str]:
    base = Path("codex_workflow") / "muse_runs" / run_id
    return {
        "run_id": run_id,
        "events": str(base / "events.jsonl"),
        "stderr": str(base / "stderr.log"),
        "result": str(base / "result.json"),
    }


def _failure_result(
    *,
    task_id: str,
    role: str,
    failure_kind: str,
    summary: str,
    artifacts: dict[str, str],
    process_exit_code: int | None,
    workspace: Path,
) -> dict[str, Any]:
    return {
        "schema_version": RESULT_SCHEMA_VERSION,
        "task_id": task_id,
        "role": role,
        "terminal_status": "failed",
        "failure_kind": failure_kind,
        "summary": _redact_text(summary)[:MAX_SUMMARY_CHARS],
        "blocking_findings": [],
        "decision_requirement": None,
        "verification": [],
        "limitations": [],
        "verdict": "INCONCLUSIVE" if role == "tester" else None,
        "repository": _git_repository_evidence(workspace),
        "artifacts": artifacts,
        "process_exit_code": process_exit_code,
    }


def _success_result(
    *,
    task_id: str,
    role: str,
    report: dict[str, Any],
    artifacts: dict[str, str],
    process_exit_code: int,
    workspace: Path,
) -> dict[str, Any]:
    safe = _sanitize_report(report)
    return {
        "schema_version": RESULT_SCHEMA_VERSION,
        "task_id": task_id,
        "role": role,
        "terminal_status": "completed",
        "failure_kind": None,
        **safe,
        "repository": _git_repository_evidence(workspace),
        "artifacts": artifacts,
        "process_exit_code": process_exit_code,
    }


def _persist_result(run_dir: Path, result: dict[str, Any]) -> None:
    _write_private_text(
        run_dir / "result.json",
        json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n",
    )


def execute_worker(
    role: str,
    workspace_arg: str,
    task_file: str,
    *,
    task_id: str | None = None,
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
    cancel_event: threading.Event | None = None,
    terminate_grace_seconds: float = TERMINATE_GRACE_SECONDS,
    runtime: RuntimePaths | None = None,
    muse_path: str | None = None,
    run_id: str | None = None,
) -> dict[str, Any]:
    if timeout_seconds <= 0:
        raise MuseWorkerError("timeout_seconds must be positive")
    runtime = runtime or _runtime_paths()
    _, allocation = _muse_allocation(role, runtime)
    workspace = _workspace(workspace_arg)
    task_path, task = _task(task_file)
    logical_task_id = _logical_task_id(task_id, task_path)
    prompt = build_prompt(role, logical_task_id, task, runtime)

    runs_root = _runs_root(runtime)
    _ensure_private_dir(runs_root)
    enforce_retention(runs_root)
    resolved_run_id = _safe_run_id(run_id)
    run_dir = runs_root / resolved_run_id
    if run_dir.exists():
        raise MuseWorkerError(f"run artifact directory already exists: {run_dir}")
    run_dir.mkdir(mode=0o700)
    os.chmod(run_dir, 0o700)

    events_path = run_dir / "events.jsonl"
    stderr_path = run_dir / "stderr.log"
    _touch_private(events_path)
    _touch_private(stderr_path)
    artifacts = _artifact_refs(runtime, resolved_run_id)

    muse = muse_path or shutil.which("muse")
    if muse is None:
        result = _failure_result(
            task_id=logical_task_id,
            role=role,
            failure_kind="auth_runtime",
            summary="Muse runtime is unavailable on PATH.",
            artifacts=artifacts,
            process_exit_code=None,
            workspace=workspace,
        )
        _persist_result(run_dir, result)
        enforce_retention(runs_root, preserve={run_dir})
        return result

    prompt_path: Path | None = None
    schema_path: Path | None = None
    try:
        prompt_fd, prompt_name = tempfile.mkstemp(
            prefix="prompt-", suffix=".md", dir=run_dir
        )
        os.fchmod(prompt_fd, 0o600)
        with os.fdopen(prompt_fd, "w", encoding="utf-8") as handle:
            handle.write(prompt)
        prompt_path = Path(prompt_name)

        schema_fd, schema_name = tempfile.mkstemp(
            prefix="schema-", suffix=".json", dir=run_dir
        )
        os.fchmod(schema_fd, 0o600)
        with os.fdopen(schema_fd, "w", encoding="utf-8") as handle:
            json.dump(
                worker_report_schema(role, logical_task_id),
                handle,
                sort_keys=True,
                separators=(",", ":"),
            )
            handle.write("\n")
        schema_path = Path(schema_name)

        command = build_command(
            muse,
            str(prompt_path),
            model=allocation.model,
            reasoning_effort=allocation.reasoning_effort,
            workspace=str(workspace),
            schema_file=str(schema_path),
            session_id=resolved_run_id,
        )
        return_code, stop_reason, drain_errors = _run_process(
            command,
            workspace=workspace,
            events_path=events_path,
            stderr_path=stderr_path,
            timeout_seconds=timeout_seconds,
            cancel_event=cancel_event,
            terminate_grace_seconds=terminate_grace_seconds,
        )

        if stop_reason == "timeout":
            result = _failure_result(
                task_id=logical_task_id,
                role=role,
                failure_kind="timeout",
                summary="Muse worker exceeded the adapter timeout and was terminated.",
                artifacts=artifacts,
                process_exit_code=return_code,
                workspace=workspace,
            )
        elif stop_reason == "cancelled":
            result = _failure_result(
                task_id=logical_task_id,
                role=role,
                failure_kind="cancelled",
                summary="Muse worker was cancelled and its process tree was terminated.",
                artifacts=artifacts,
                process_exit_code=return_code,
                workspace=workspace,
            )
        elif stop_reason is not None and stop_reason.startswith("spawn:"):
            result = _failure_result(
                task_id=logical_task_id,
                role=role,
                failure_kind="auth_runtime",
                summary="Muse runtime could not be started by the adapter.",
                artifacts=artifacts,
                process_exit_code=return_code,
                workspace=workspace,
            )
        elif drain_errors:
            result = _failure_result(
                task_id=logical_task_id,
                role=role,
                failure_kind="adapter_internal",
                summary="Muse output draining failed; raw artifacts may be incomplete.",
                artifacts=artifacts,
                process_exit_code=return_code,
                workspace=workspace,
            )
        else:
            terminal, protocol_error = _parse_terminal(events_path)
            diagnostic = _read_diagnostic(stderr_path)
            if protocol_error is not None:
                kind = _failure_kind(diagnostic, default="protocol")
                result = _failure_result(
                    task_id=logical_task_id,
                    role=role,
                    failure_kind=kind,
                    summary=f"Muse terminal protocol failed validation: {protocol_error}.",
                    artifacts=artifacts,
                    process_exit_code=return_code,
                    workspace=workspace,
                )
            else:
                assert terminal is not None
                payload = terminal["payload"]
                terminal_state = payload["terminal"]
                if terminal_state == "failed":
                    reason = payload.get("reason")
                    reason_text = reason if isinstance(reason, str) else ""
                    kind = _failure_kind(
                        reason_text + "\n" + diagnostic,
                        default="muse_model",
                    )
                    result = _failure_result(
                        task_id=logical_task_id,
                        role=role,
                        failure_kind=kind,
                        summary="Muse reported a structured terminal failure.",
                        artifacts=artifacts,
                        process_exit_code=return_code,
                        workspace=workspace,
                    )
                elif return_code != 0:
                    result = _failure_result(
                        task_id=logical_task_id,
                        role=role,
                        failure_kind="protocol",
                        summary="Muse reported terminal completion with a non-zero process exit.",
                        artifacts=artifacts,
                        process_exit_code=return_code,
                        workspace=workspace,
                    )
                else:
                    try:
                        report = _validate_report(
                            payload.get("text"),
                            role=role,
                            task_id=logical_task_id,
                        )
                    except MuseWorkerError:
                        result = _failure_result(
                            task_id=logical_task_id,
                            role=role,
                            failure_kind="normalized_report",
                            summary="Muse completed but its final worker report failed validation.",
                            artifacts=artifacts,
                            process_exit_code=return_code,
                            workspace=workspace,
                        )
                    else:
                        result = _success_result(
                            task_id=logical_task_id,
                            role=role,
                            report=report,
                            artifacts=artifacts,
                            process_exit_code=return_code,
                            workspace=workspace,
                        )
    except OSError as error:
        kind = (
            "auth_runtime"
            if isinstance(error, FileNotFoundError)
            else "adapter_internal"
        )
        result = _failure_result(
            task_id=logical_task_id,
            role=role,
            failure_kind=kind,
            summary="Muse process could not be started by the adapter.",
            artifacts=artifacts,
            process_exit_code=None,
            workspace=workspace,
        )
    finally:
        for path in (prompt_path, schema_path):
            if path is None:
                continue
            try:
                path.unlink()
            except FileNotFoundError:
                pass

    _persist_result(run_dir, result)
    enforce_retention(runs_root, preserve={run_dir})
    return result



def run(
    role: str,
    workspace_arg: str,
    task_file: str,
    *,
    task_id: str | None = None,
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
    dry_run: bool = False,
) -> int:
    runtime = _runtime_paths()
    profile, allocation = _muse_allocation(role, runtime)
    workspace = _workspace(workspace_arg)
    task_path, _ = _task(task_file)
    logical_task_id = _logical_task_id(task_id, task_path)
    muse = shutil.which("muse")

    if dry_run:
        if muse is None:
            raise MuseWorkerError(
                "Muse Code CLI is not installed or is not on PATH; install it and run `muse login` first"
            )
        command = build_command(
            muse,
            "<temporary-prompt>",
            model=allocation.model,
            reasoning_effort=allocation.reasoning_effort,
            workspace=str(workspace),
            schema_file="<temporary-schema>",
            session_id="<run-id>",
        )
        print(
            json.dumps(
                {
                    "profile": profile,
                    "harness": allocation.harness,
                    "model": allocation.model,
                    "reasoning_effort": allocation.reasoning_effort,
                    "role": role,
                    "task_id": logical_task_id,
                    "workspace": str(workspace),
                    "command": command,
                },
                sort_keys=True,
            )
        )
        return 0

    result = execute_worker(
        role,
        workspace_arg,
        task_file,
        task_id=logical_task_id,
        timeout_seconds=timeout_seconds,
        runtime=runtime,
        muse_path=muse,
    )
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0 if result["terminal_status"] == "completed" else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run one codex_workflow role through its active Muse Code allocation."
    )
    parser.add_argument("--role", required=True)
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--task-file", required=True)
    parser.add_argument("--task-id")
    parser.add_argument(
        "--timeout-seconds",
        type=float,
        default=DEFAULT_TIMEOUT_SECONDS,
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    try:
        return run(
            args.role,
            args.workspace,
            args.task_file,
            task_id=args.task_id,
            timeout_seconds=args.timeout_seconds,
            dry_run=args.dry_run,
        )
    except MuseWorkerError as error:
        print(f"muse worker error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
