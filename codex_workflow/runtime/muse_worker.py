"""Run one codex_workflow role through the native Muse Code harness."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
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
from runtime.muse_sessions import (
    SessionStateError,
    acquire_worker_session,
    finish_worker_session,
)


ROLE_RE = re.compile(r"^[A-Za-z0-9_-]+$")
TASK_ID_RE = re.compile(r"^[A-Za-z0-9_.:-]{1,128}$")
CAPABILITY_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/@+-]{0,127}$")
RESULT_SCHEMA_VERSION = "1"
TERMINAL_TYPES = {"run.terminal.completed", "run.terminal.failed"}
VERDICTS = {"GREEN", "RED", "INCONCLUSIVE"}
CHECK_STATUSES = {"pass", "fail", "not_run", "unknown"}

DEFAULT_TIMEOUT_SECONDS = 30 * 60
TERMINATE_GRACE_SECONDS = 3.0
RETENTION_MAX_RUNS = 50
RETENTION_MAX_AGE_SECONDS = 14 * 24 * 60 * 60
RETENTION_MAX_BYTES = 100 * 1024 * 1024
MAX_CONCURRENT_INVOCATIONS = 8

_RETENTION_LOCK = threading.Lock()

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



def _normalize_hint_values(values: Any, *, category: str) -> tuple[str, ...]:
    if values is None:
        return ()
    if isinstance(values, str):
        values = (values,)
    try:
        items = tuple(values)
    except TypeError as error:
        raise MuseWorkerError(f"{category} must be an iterable of capability identifiers") from error

    normalized: list[str] = []
    seen: set[str] = set()
    for value in items:
        if not isinstance(value, str) or not CAPABILITY_ID_RE.fullmatch(value):
            raise MuseWorkerError(
                f"{category} entries must be 1-128 character opaque identifiers using "
                "letters, digits, '.', '_', ':', '/', '@', '+', or '-', starting "
                f"with a letter or digit: {value!r}"
            )
        if value in seen:
            continue
        seen.add(value)
        normalized.append(value)
    return tuple(normalized)


@dataclass(frozen=True, slots=True)
class MuseCapabilityHints:
    """Complete capability guidance for one Muse invocation."""

    required_skills: tuple[str, ...] = ()
    relevant_skills: tuple[str, ...] = ()
    required_capabilities: tuple[str, ...] = ()
    suggested_capabilities: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        required_skills = _normalize_hint_values(
            self.required_skills,
            category="required_skills",
        )
        relevant_skills = _normalize_hint_values(
            self.relevant_skills,
            category="relevant_skills",
        )
        required_capabilities = _normalize_hint_values(
            self.required_capabilities,
            category="required_capabilities",
        )
        suggested_capabilities = _normalize_hint_values(
            self.suggested_capabilities,
            category="suggested_capabilities",
        )

        required_skill_set = set(required_skills)
        required_capability_set = set(required_capabilities)
        relevant_skills = tuple(
            value for value in relevant_skills if value not in required_skill_set
        )
        suggested_capabilities = tuple(
            value
            for value in suggested_capabilities
            if value not in required_capability_set
        )

        object.__setattr__(self, "required_skills", required_skills)
        object.__setattr__(self, "relevant_skills", relevant_skills)
        object.__setattr__(self, "required_capabilities", required_capabilities)
        object.__setattr__(self, "suggested_capabilities", suggested_capabilities)

    def as_dict(self) -> dict[str, list[str]]:
        return {
            "required_skills": list(self.required_skills),
            "relevant_skills": list(self.relevant_skills),
            "required_capabilities": list(self.required_capabilities),
            "suggested_capabilities": list(self.suggested_capabilities),
        }


def _capability_hints(value: MuseCapabilityHints | None) -> MuseCapabilityHints:
    if value is None:
        return MuseCapabilityHints()
    if not isinstance(value, MuseCapabilityHints):
        raise MuseWorkerError("capability_hints must be a MuseCapabilityHints value")
    return value


def _format_hint_values(values: tuple[str, ...]) -> str:
    return ", ".join(values) if values else "(none)"


def _render_capability_hints(hints: MuseCapabilityHints) -> str:
    return "\n".join(
        [
            "CURRENT MUSE CAPABILITY HINTS",
            "This is the complete authoritative capability-hint set for this invocation.",
            "It supersedes all capability hints from prior turns, including resumed logical "
            "sessions; hints not repeated here are no longer authoritative.",
            f"Required skills: {_format_hint_values(hints.required_skills)}",
            f"Relevant skills: {_format_hint_values(hints.relevant_skills)}",
            f"Required capabilities: {_format_hint_values(hints.required_capabilities)}",
            f"Suggested capabilities: {_format_hint_values(hints.suggested_capabilities)}",
            "Capability semantics:",
            "- If a required skill or capability is unavailable, report that fact fail-visibly "
            "to Main.",
            "- Relevant skills and suggested capabilities are advisory; their absence is "
            "non-blocking.",
            "- Do not install, configure, authenticate, update, or remove any capability merely "
            "because it appears in these hints.",
            "- Muse remains responsible for native skill loading and MCP/tool execution.",
        ]
    )


@dataclass(frozen=True, slots=True)
class MuseWorkerInvocation:
    """One already-authorized Muse invocation against an assigned workspace.

    The caller owns dependency, parallel-safety, branch/worktree and write-scope
    decisions. codex_workflow owns only the bounded worker/session runtime.
    """

    role: str
    workspace: str
    task_file: str
    task_id: str | None = None
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS
    cancel_event: threading.Event | None = None
    terminate_grace_seconds: float = TERMINATE_GRACE_SECONDS
    runtime: RuntimePaths | None = None
    muse_path: str | None = None
    logical_worker_id: str | None = None
    caller_scope: str | None = None
    resume: bool = False
    capability_hints: MuseCapabilityHints = MuseCapabilityHints()
    invocation_id: str | None = None
    run_id: str | None = None


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


def build_prompt(
    role: str,
    task_id: str,
    task: str,
    runtime: RuntimePaths,
    capability_hints: MuseCapabilityHints | None = None,
) -> str:
    contract = _worker_contract(role, runtime)
    hints = _capability_hints(capability_hints)
    capability_block = _render_capability_hints(hints)
    verdict_rule = (
        "Set verdict to exactly GREEN, RED, or INCONCLUSIVE."
        if role == "tester"
        else "Set verdict to null."
    )
    return f"""You are a codex_workflow worker running through Muse Code.

ROLE CONTRACT
{contract}

{capability_block}

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
        "exec",
        "--disable-approval",
        "--trust-workspace",
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


def _safe_invocation_id(value: str | None = None) -> str:
    if value is None:
        return str(uuid.uuid4())
    try:
        parsed = uuid.UUID(value)
    except ValueError as error:
        raise MuseWorkerError(f"invalid invocation id: {value!r}") from error
    if str(parsed) != value.lower():
        raise MuseWorkerError(f"invocation id is not canonical UUID text: {value!r}")
    return str(parsed)


def _resolve_invocation_id(
    invocation_id: str | None,
    run_id: str | None,
) -> str:
    if invocation_id is not None and run_id is not None and invocation_id != run_id:
        raise MuseWorkerError("invocation_id and legacy run_id disagree")
    return _safe_invocation_id(invocation_id or run_id)


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
    """Apply bounded retention without racing another in-process Muse lane."""

    preserve = {path.resolve() for path in (preserve or set())}
    with _RETENTION_LOCK:
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

        existing: list[Path] = []
        for run_dir in runs:
            try:
                run_dir.stat()
            except FileNotFoundError:
                continue
            existing.append(run_dir)
        existing.sort(key=lambda path: path.stat().st_mtime, reverse=True)

        kept: list[Path] = []
        for index, run_dir in enumerate(existing):
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


def _terminate_process_tree(process: subprocess.Popen[bytes], grace_seconds: float) -> bool:
    """Terminate the captured process tree and positively confirm its absence."""

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
            return True
        time.sleep(0.05)

    # Capture descendants that appeared during graceful shutdown before escalation.
    snapshot.update(_snapshot_process_tree(process.pid))
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

    confirm_deadline = time.monotonic() + 1.0
    while time.monotonic() < confirm_deadline:
        if process.poll() is not None and _tree_is_gone(snapshot):
            return True
        time.sleep(0.05)
    return process.poll() is not None and _tree_is_gone(snapshot)


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
) -> tuple[int | None, str | None, list[str], bool]:
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
        return None, f"spawn:{type(error).__name__}", [str(error)], True

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

    cleanup_confirmed = True
    if stop_reason is not None:
        cleanup_confirmed = _terminate_process_tree(process, terminate_grace_seconds)

    return_code = process.poll()
    if return_code is None:
        try:
            return_code = process.wait(timeout=1.0)
        except subprocess.TimeoutExpired:
            cleanup_confirmed = _terminate_process_tree(process, 0.0)
            return_code = process.poll()

    for thread in threads:
        thread.join(timeout=2.0)
    if any(thread.is_alive() for thread in threads):
        drain_errors.append("stream drain thread did not terminate")
    return return_code, stop_reason, drain_errors, cleanup_confirmed


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
    if (
        "invalid tui options" in lowered
        or "unexpected argument" in lowered
        or ("usage: muse" in lowered and "error:" in lowered)
    ):
        return "adapter_internal"
    if any(word in lowered for word in ("auth", "login", "credential", "unauthorized", "forbidden")):
        return "auth_runtime"
    if (
        "no retained session log found" in lowered
        or "session not found" in lowered
        or "unknown session" in lowered
        or "session does not exist" in lowered
    ):
        return "session_unavailable"
    if "session" in lowered and any(word in lowered for word in ("busy", "locked", "in use")):
        return "session_busy"
    if "session" in lowered and any(word in lowered for word in ("resume", "rejected", "invalid")):
        return "resume_rejected"
    if any(word in lowered for word in ("model", "provider", "rate limit", "quota")):
        return "muse_model"
    return default


def _probe_retained_session(
    muse: str,
    session_id: str,
    *,
    timeout_seconds: float = 15.0,
) -> tuple[bool, str | None]:
    """Check exact retained-session existence without exposing exported trajectory."""

    try:
        completed = subprocess.run(
            [muse, "export", "--session", session_id, "--redacted"],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            check=False,
            timeout=timeout_seconds,
        )
    except FileNotFoundError:
        return False, "auth_runtime"
    except subprocess.TimeoutExpired:
        return False, "session_unavailable"
    except OSError:
        return False, "adapter_internal"

    if completed.returncode == 0:
        return True, None
    diagnostic = completed.stderr[-32768:].decode("utf-8", errors="replace")
    kind = _failure_kind(diagnostic, default="session_unavailable")
    return False, kind


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


def _artifact_refs(runtime: RuntimePaths, invocation_id: str) -> dict[str, str]:
    base = Path("codex_workflow") / "muse_runs" / invocation_id
    return {
        "invocation_id": invocation_id,
        "run_id": invocation_id,
        "events": str(base / "events.jsonl"),
        "stderr": str(base / "stderr.log"),
        "result": str(base / "result.json"),
    }


def _runtime_metadata(
    *,
    logical_worker_id: str | None,
    session_id: str | None,
    invocation_id: str,
    resumed: bool,
    session_state: str,
) -> dict[str, Any]:
    return {
        "logical_worker_id": logical_worker_id,
        "session_id": session_id,
        "invocation_id": invocation_id,
        "resumed": resumed,
        "session_state": session_state,
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
    runtime_metadata: dict[str, Any],
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
        "runtime": runtime_metadata,
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
    runtime_metadata: dict[str, Any],
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
        "runtime": runtime_metadata,
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
    logical_worker_id: str | None = None,
    caller_scope: str | None = None,
    resume: bool = False,
    capability_hints: MuseCapabilityHints | None = None,
    invocation_id: str | None = None,
    run_id: str | None = None,
    retention_preserve: set[Path] | None = None,
) -> dict[str, Any]:
    if timeout_seconds <= 0:
        raise MuseWorkerError("timeout_seconds must be positive")
    runtime = runtime or _runtime_paths()
    profile, allocation = _muse_allocation(role, runtime)
    workspace = _workspace(workspace_arg)
    task_path, task = _task(task_file)
    logical_task_id = _logical_task_id(task_id, task_path)
    hints = _capability_hints(capability_hints)
    prompt = build_prompt(
        role,
        logical_task_id,
        task,
        runtime,
        capability_hints=hints,
    )

    runs_root = _runs_root(runtime)
    _ensure_private_dir(runs_root)
    enforce_retention(runs_root, preserve=retention_preserve)
    resolved_invocation_id = _resolve_invocation_id(invocation_id, run_id)
    run_dir = runs_root / resolved_invocation_id
    if run_dir.exists():
        raise MuseWorkerError(f"run artifact directory already exists: {run_dir}")
    run_dir.mkdir(mode=0o700)
    os.chmod(run_dir, 0o700)

    events_path = run_dir / "events.jsonl"
    stderr_path = run_dir / "stderr.log"
    _touch_private(events_path)
    _touch_private(stderr_path)
    artifacts = _artifact_refs(runtime, resolved_invocation_id)
    runtime_metadata = _runtime_metadata(
        logical_worker_id=logical_worker_id,
        session_id=None,
        invocation_id=resolved_invocation_id,
        resumed=resume,
        session_state="unassigned",
    )

    def failure(kind: str, summary: str, process_exit_code: int | None = None) -> dict[str, Any]:
        return _failure_result(
            task_id=logical_task_id,
            role=role,
            failure_kind=kind,
            summary=summary,
            artifacts=artifacts,
            process_exit_code=process_exit_code,
            workspace=workspace,
            runtime_metadata=runtime_metadata,
        )

    muse = muse_path or shutil.which("muse")
    if muse is None:
        result = failure("auth_runtime", "Muse runtime is unavailable on PATH.")
        _persist_result(run_dir, result)
        enforce_retention(runs_root, preserve={run_dir, *(retention_preserve or set())})
        return result

    try:
        lease = acquire_worker_session(
            runtime,
            logical_worker_id=logical_worker_id,
            role=role,
            profile=profile,
            model=allocation.model,
            reasoning_effort=allocation.reasoning_effort,
            harness=allocation.harness,
            workspace=str(workspace),
            task_id=logical_task_id,
            caller_scope=caller_scope,
            resume=resume,
        )
    except SessionStateError as error:
        runtime_metadata.update(
            {
                "logical_worker_id": error.logical_worker_id or logical_worker_id,
                "session_id": error.session_id,
                "resumed": error.resumed or resume,
                "session_state": error.kind,
            }
        )
        result = failure(error.kind, str(error))
        _persist_result(run_dir, result)
        enforce_retention(runs_root, preserve={run_dir, *(retention_preserve or set())})
        return result

    runtime_metadata.update(
        {
            "logical_worker_id": lease.logical_worker_id,
            "session_id": lease.session_id,
            "resumed": lease.resumed,
            "session_state": "active",
        }
    )

    if lease.resumed:
        retained, probe_kind = _probe_retained_session(muse, lease.session_id)
        if not retained:
            result = failure(
                probe_kind or "session_unavailable",
                "Retained Muse session failed the fail-closed resume precondition.",
            )
            try:
                finish_worker_session(runtime, lease, state="needs_probe")
                runtime_metadata["session_state"] = "needs_probe"
            except SessionStateError:
                runtime_metadata["session_state"] = "unknown"
                result = failure(
                    "adapter_internal",
                    "Muse resume probe failed and durable session state could not be reconciled.",
                )
            _persist_result(run_dir, result)
            enforce_retention(runs_root, preserve={run_dir, *(retention_preserve or set())})
            return result
    prompt_path: Path | None = None
    schema_path: Path | None = None
    return_code: int | None = None
    cleanup_confirmed = True
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
            session_id=lease.session_id,
        )
        return_code, stop_reason, drain_errors, cleanup_confirmed = _run_process(
            command,
            workspace=workspace,
            events_path=events_path,
            stderr_path=stderr_path,
            timeout_seconds=timeout_seconds,
            cancel_event=cancel_event,
            terminate_grace_seconds=terminate_grace_seconds,
        )

        if stop_reason in {"timeout", "cancelled"} and not cleanup_confirmed:
            result = failure(
                "adapter_internal",
                "Muse process-tree cleanup could not be confirmed; the affected workspace is quarantined.",
                return_code,
            )
        elif stop_reason == "timeout":
            result = failure(
                "timeout",
                "Muse worker exceeded the adapter timeout and its process tree was terminated.",
                return_code,
            )
        elif stop_reason == "cancelled":
            result = failure(
                "cancelled",
                "Muse worker was cancelled and its process tree was terminated.",
                return_code,
            )
        elif stop_reason is not None and stop_reason.startswith("spawn:"):
            result = failure(
                "auth_runtime",
                "Muse runtime could not be started by the adapter.",
                return_code,
            )
        elif drain_errors:
            result = failure(
                "adapter_internal",
                "Muse output draining failed; raw artifacts may be incomplete.",
                return_code,
            )
        else:
            terminal, protocol_error = _parse_terminal(events_path)
            diagnostic = _read_diagnostic(stderr_path)
            if protocol_error is not None:
                kind = _failure_kind(diagnostic, default="protocol")
                result = failure(
                    kind,
                    f"Muse terminal protocol failed validation: {protocol_error}.",
                    return_code,
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
                    result = failure(
                        kind,
                        "Muse reported a structured terminal failure.",
                        return_code,
                    )
                elif return_code != 0:
                    result = failure(
                        "protocol",
                        "Muse reported terminal completion with a non-zero process exit.",
                        return_code,
                    )
                else:
                    try:
                        report = _validate_report(
                            payload.get("text"),
                            role=role,
                            task_id=logical_task_id,
                        )
                    except MuseWorkerError:
                        result = failure(
                            "normalized_report",
                            "Muse completed but its final worker report failed validation.",
                            return_code,
                        )
                    else:
                        result = _success_result(
                            task_id=logical_task_id,
                            role=role,
                            report=report,
                            artifacts=artifacts,
                            process_exit_code=return_code,
                            workspace=workspace,
                            runtime_metadata=runtime_metadata,
                        )
    except OSError as error:
        kind = "auth_runtime" if isinstance(error, FileNotFoundError) else "adapter_internal"
        result = failure(
            kind,
            "Muse process could not be started by the adapter.",
            return_code,
        )
    except Exception:
        result = failure(
            "adapter_internal",
            "Muse adapter failed unexpectedly while owning the logical-session lease.",
            return_code,
        )
    finally:
        for temporary_path in (prompt_path, schema_path):
            if temporary_path is None:
                continue
            try:
                temporary_path.unlink()
            except FileNotFoundError:
                pass

    next_state = (
        "cleanup_unconfirmed"
        if not cleanup_confirmed
        else ("ready" if result["terminal_status"] == "completed" else "needs_probe")
    )
    try:
        # Persist the durable quarantine before releasing the process-local flock.
        finish_worker_session(runtime, lease, state=next_state)
        runtime_metadata["session_state"] = next_state
    except SessionStateError:
        runtime_metadata["session_state"] = "unknown"
        result = failure(
            "adapter_internal",
            "Muse invocation finished but durable logical-session state could not be reconciled.",
            return_code,
        )

    _persist_result(run_dir, result)
    enforce_retention(runs_root, preserve={run_dir, *(retention_preserve or set())})
    return result


def _validate_concurrent_workspaces(
    invocations: tuple[MuseWorkerInvocation, ...],
) -> tuple[Path, ...]:
    workspaces = tuple(_workspace(invocation.workspace) for invocation in invocations)
    for index, left in enumerate(workspaces):
        for right in workspaces[index + 1 :]:
            if left == right or left in right.parents or right in left.parents:
                raise MuseWorkerError(
                    "concurrent Muse invocations require distinct non-overlapping workspaces: "
                    f"{left} <-> {right}"
                )
    return workspaces


def execute_workers_concurrently(
    invocations: list[MuseWorkerInvocation] | tuple[MuseWorkerInvocation, ...],
    *,
    max_workers: int = 2,
) -> list[dict[str, Any]]:
    """Await already-authorized independent Muse invocations concurrently.

    This helper is intentionally not a scheduler: callers supply the complete
    lane set and isolated workspaces after establishing dependency and
    parallel-safety authority. Results retain input order.
    """

    items = tuple(invocations)
    if not items:
        return []
    if len(items) > MAX_CONCURRENT_INVOCATIONS:
        raise MuseWorkerError(
            f"at most {MAX_CONCURRENT_INVOCATIONS} Muse invocations may be awaited together"
        )
    if max_workers <= 0 or max_workers > MAX_CONCURRENT_INVOCATIONS:
        raise MuseWorkerError(
            f"max_workers must be between 1 and {MAX_CONCURRENT_INVOCATIONS}"
        )

    _validate_concurrent_workspaces(items)

    prepared: list[tuple[MuseWorkerInvocation, RuntimePaths, str]] = []
    preserve_by_root: dict[Path, set[Path]] = {}
    seen_run_dirs: set[Path] = set()
    for invocation in items:
        runtime = invocation.runtime or _runtime_paths()
        resolved_invocation_id = _resolve_invocation_id(
            invocation.invocation_id,
            invocation.run_id,
        )
        runs_root = _runs_root(runtime).resolve()
        run_dir = (runs_root / resolved_invocation_id).resolve()
        if run_dir in seen_run_dirs or run_dir.exists():
            raise MuseWorkerError(f"duplicate or existing concurrent run directory: {run_dir}")
        seen_run_dirs.add(run_dir)
        preserve_by_root.setdefault(runs_root, set()).add(run_dir)
        prepared.append((invocation, runtime, resolved_invocation_id))

    results: list[dict[str, Any] | None] = [None] * len(prepared)
    failures: list[tuple[int, BaseException]] = []
    worker_count = min(max_workers, len(prepared))
    with ThreadPoolExecutor(
        max_workers=worker_count,
        thread_name_prefix="muse-worker",
    ) as pool:
        futures = []
        for invocation, runtime, resolved_invocation_id in prepared:
            preserve = preserve_by_root[_runs_root(runtime).resolve()]
            futures.append(
                pool.submit(
                    execute_worker,
                    invocation.role,
                    invocation.workspace,
                    invocation.task_file,
                    task_id=invocation.task_id,
                    timeout_seconds=invocation.timeout_seconds,
                    cancel_event=invocation.cancel_event,
                    terminate_grace_seconds=invocation.terminate_grace_seconds,
                    runtime=runtime,
                    muse_path=invocation.muse_path,
                    logical_worker_id=invocation.logical_worker_id,
                    caller_scope=invocation.caller_scope,
                    resume=invocation.resume,
                    capability_hints=invocation.capability_hints,
                    invocation_id=resolved_invocation_id,
                    retention_preserve=preserve,
                )
            )

        for index, future in enumerate(futures):
            try:
                results[index] = future.result()
            except BaseException as error:
                failures.append((index, error))

    if failures:
        indexes = ", ".join(str(index) for index, _ in failures)
        raise MuseWorkerError(
            f"concurrent Muse adapter invocation failed before normalized result for lane(s): {indexes}"
        ) from failures[0][1]

    return [result for result in results if result is not None]


def run(
    role: str,
    workspace_arg: str,
    task_file: str,
    *,
    task_id: str | None = None,
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
    dry_run: bool = False,
    logical_worker_id: str | None = None,
    caller_scope: str | None = None,
    resume: bool = False,
    capability_hints: MuseCapabilityHints | None = None,
    invocation_id: str | None = None,
) -> int:
    runtime = _runtime_paths()
    profile, allocation = _muse_allocation(role, runtime)
    workspace = _workspace(workspace_arg)
    task_path, _ = _task(task_file)
    logical_task_id = _logical_task_id(task_id, task_path)
    hints = _capability_hints(capability_hints)
    muse = shutil.which("muse")

    if dry_run:
        if muse is None:
            raise MuseWorkerError(
                "Muse Code CLI is not installed or is not on PATH; install it and run muse login first"
            )
        if resume and logical_worker_id is None:
            raise MuseWorkerError("--resume requires --logical-worker-id")
        command = build_command(
            muse,
            "<temporary-prompt>",
            model=allocation.model,
            reasoning_effort=allocation.reasoning_effort,
            workspace=str(workspace),
            schema_file="<temporary-schema>",
            session_id="<retained-session-id>" if resume else "<new-session-id>",
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
                    "logical_worker_id": logical_worker_id,
                    "caller_scope": caller_scope,
                    "session_mode": "resume" if resume else "create",
                    "capability_hints": hints.as_dict(),
                    "invocation_id": invocation_id,
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
        logical_worker_id=logical_worker_id,
        caller_scope=caller_scope,
        resume=resume,
        capability_hints=hints,
        invocation_id=invocation_id,
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
    parser.add_argument("--logical-worker-id")
    parser.add_argument("--caller-scope")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--required-skill", action="append", default=[])
    parser.add_argument("--relevant-skill", action="append", default=[])
    parser.add_argument("--required-capability", action="append", default=[])
    parser.add_argument("--suggested-capability", action="append", default=[])
    parser.add_argument("--invocation-id")
    parser.add_argument(
        "--timeout-seconds",
        type=float,
        default=DEFAULT_TIMEOUT_SECONDS,
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    try:
        capability_hints = MuseCapabilityHints(
            required_skills=tuple(args.required_skill),
            relevant_skills=tuple(args.relevant_skill),
            required_capabilities=tuple(args.required_capability),
            suggested_capabilities=tuple(args.suggested_capability),
        )
        return run(
            args.role,
            args.workspace,
            args.task_file,
            task_id=args.task_id,
            timeout_seconds=args.timeout_seconds,
            dry_run=args.dry_run,
            logical_worker_id=args.logical_worker_id,
            caller_scope=args.caller_scope,
            resume=args.resume,
            capability_hints=capability_hints,
            invocation_id=args.invocation_id,
        )
    except MuseWorkerError as error:
        print(f"muse worker error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())