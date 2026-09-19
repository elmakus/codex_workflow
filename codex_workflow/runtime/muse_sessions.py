"""Private durable Muse logical-worker session registry and leases."""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
import fcntl
import hashlib
import json
import os
import re
import tempfile
import time
import uuid
from pathlib import Path
from typing import Any, Iterator

from runtime.layout import RuntimePaths


SESSION_REGISTRY_VERSION = "1"
MAX_SESSION_RECORDS = 256
LOGICAL_WORKER_ID_RE = re.compile(r"^[A-Za-z0-9_.:-]{1,128}$")
_SESSION_STATES = {"reserved", "active", "ready", "needs_probe", "cleanup_unconfirmed"}


class SessionStateError(RuntimeError):
    """A fail-closed logical-session lifecycle error."""

    def __init__(
        self,
        kind: str,
        message: str,
        *,
        logical_worker_id: str | None = None,
        session_id: str | None = None,
        resumed: bool = False,
    ) -> None:
        super().__init__(message)
        self.kind = kind
        self.logical_worker_id = logical_worker_id
        self.session_id = session_id
        self.resumed = resumed


@dataclass(slots=True)
class SessionLease:
    logical_worker_id: str
    session_id: str
    resumed: bool
    lock_fd: int
    _closed: bool = False

    def release(self) -> None:
        if self._closed:
            return
        try:
            fcntl.flock(self.lock_fd, fcntl.LOCK_UN)
        finally:
            os.close(self.lock_fd)
            self._closed = True
def _sessions_root(runtime: RuntimePaths) -> Path:
    return runtime.runtime / "muse_sessions"


def _registry_path(runtime: RuntimePaths) -> Path:
    return _sessions_root(runtime) / "registry.json"


def _registry_lock_path(runtime: RuntimePaths) -> Path:
    return _sessions_root(runtime) / "registry.lock"


def _session_locks_root(runtime: RuntimePaths) -> Path:
    return _sessions_root(runtime) / "locks"


def _ensure_private_dir(path: Path) -> None:
    if path.is_symlink():
        raise SessionStateError("adapter_internal", f"session path is a symlink: {path}")
    path.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(path, 0o700)


def _open_private_lock(path: Path, *, nonblocking: bool) -> int:
    if path.is_symlink():
        raise SessionStateError("adapter_internal", f"lock path is a symlink: {path}")
    flags = os.O_CREAT | os.O_RDWR
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    fd = os.open(path, flags, 0o600)
    os.fchmod(fd, 0o600)
    operation = fcntl.LOCK_EX | (fcntl.LOCK_NB if nonblocking else 0)
    try:
        fcntl.flock(fd, operation)
    except BlockingIOError:
        os.close(fd)
        raise
    return fd


@contextmanager
def _registry_guard(runtime: RuntimePaths) -> Iterator[None]:
    root = _sessions_root(runtime)
    _ensure_private_dir(root)
    fd = _open_private_lock(_registry_lock_path(runtime), nonblocking=False)
    try:
        yield
    finally:
        fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)


def _default_registry() -> dict[str, Any]:
    return {"schema_version": SESSION_REGISTRY_VERSION, "workers": {}}
def _load_registry(runtime: RuntimePaths) -> dict[str, Any]:
    path = _registry_path(runtime)
    if not path.exists():
        return _default_registry()
    if path.is_symlink() or not path.is_file():
        raise SessionStateError("adapter_internal", "Muse session registry is not a regular file")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise SessionStateError("adapter_internal", "Muse session registry is unreadable") from error
    if (
        not isinstance(value, dict)
        or set(value) != {"schema_version", "workers"}
        or value.get("schema_version") != SESSION_REGISTRY_VERSION
        or not isinstance(value.get("workers"), dict)
    ):
        raise SessionStateError("adapter_internal", "Muse session registry schema is invalid")
    if len(value["workers"]) > MAX_SESSION_RECORDS:
        raise SessionStateError("adapter_internal", "Muse session registry exceeds its bounded capacity")
    return value


def _save_registry(runtime: RuntimePaths, registry: dict[str, Any]) -> None:
    root = _sessions_root(runtime)
    _ensure_private_dir(root)
    path = _registry_path(runtime)
    fd, temporary = tempfile.mkstemp(prefix=".registry.", dir=root)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(registry, handle, sort_keys=True, separators=(",", ":"))
            handle.write("\n")
        os.replace(temporary, path)
        os.chmod(path, 0o600)
    finally:
        try:
            Path(temporary).unlink()
        except FileNotFoundError:
            pass


def _safe_worker_id(value: str | None, *, resume: bool) -> str:
    if value is None:
        if resume:
            raise SessionStateError(
                "resume_rejected",
                "resuming a Muse worker requires its logical_worker_id",
                resumed=True,
            )
        return f"worker-{uuid.uuid4()}"
    if not LOGICAL_WORKER_ID_RE.fullmatch(value):
        raise SessionStateError(
            "adapter_internal",
            "logical_worker_id must be 1-128 safe identifier characters",
            logical_worker_id=value,
            resumed=resume,
        )
    return value
def _safe_scope(value: str | None) -> str | None:
    if value is None:
        return None
    if (
        not isinstance(value, str)
        or not value
        or len(value) > 512
        or "\x00" in value
        or "\n" in value
        or "\r" in value
    ):
        raise SessionStateError("adapter_internal", "caller_scope is invalid")
    return value




def _registry_key(logical_worker_id: str, caller_scope: str | None) -> str:
    payload = json.dumps(
        [caller_scope, logical_worker_id],
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _binding_record(
    *,
    logical_worker_id: str,
    session_id: str,
    role: str,
    profile: str,
    model: str,
    reasoning_effort: str,
    harness: str,
    workspace: str,
    task_id: str,
    caller_scope: str | None,
    state: str,
) -> dict[str, Any]:
    return {
        "logical_worker_id": logical_worker_id,
        "session_id": session_id,
        "role": role,
        "profile": profile,
        "model": model,
        "reasoning_effort": reasoning_effort,
        "harness": harness,
        "workspace": workspace,
        "task_id": task_id,
        "caller_scope": caller_scope,
        "state": state,
        "updated_at": time.time(),
    }


def _binding_mismatches(record: dict[str, Any], expected: dict[str, Any]) -> list[str]:
    fields = (
        "logical_worker_id",
        "role",
        "profile",
        "model",
        "reasoning_effort",
        "harness",
        "workspace",
        "task_id",
        "caller_scope",
    )
    return [field for field in fields if record.get(field) != expected.get(field)]


def _update_state(
    runtime: RuntimePaths,
    logical_worker_id: str,
    session_id: str,
    state: str,
) -> None:
    if state not in _SESSION_STATES:
        raise SessionStateError("adapter_internal", f"invalid Muse session state: {state}")
    with _registry_guard(runtime):
        registry = _load_registry(runtime)
        matches = [
            record
            for record in registry["workers"].values()
            if isinstance(record, dict)
            and record.get("logical_worker_id") == logical_worker_id
            and record.get("session_id") == session_id
        ]
        if len(matches) != 1:
            raise SessionStateError(
                "session_unavailable",
                "logical Muse session record disappeared or changed",
                logical_worker_id=logical_worker_id,
                session_id=session_id,
            )
        record = matches[0]
        record["state"] = state
        record["updated_at"] = time.time()
        _save_registry(runtime, registry)
def acquire_worker_session(
    runtime: RuntimePaths,
    *,
    logical_worker_id: str | None,
    role: str,
    profile: str,
    model: str,
    reasoning_effort: str,
    harness: str,
    workspace: str,
    task_id: str,
    caller_scope: str | None,
    resume: bool,
) -> SessionLease:
    """Create or acquire one bound logical Muse session with a process-safe lease."""

    worker_id = _safe_worker_id(logical_worker_id, resume=resume)
    scope = _safe_scope(caller_scope)
    registry_key = _registry_key(worker_id, scope)
    created = False
    session_id: str

    with _registry_guard(runtime):
        registry = _load_registry(runtime)
        workers = registry["workers"]
        unreconciled = next(
            (
                candidate
                for candidate in workers.values()
                if isinstance(candidate, dict)
                and candidate.get("state") in {"active", "cleanup_unconfirmed"}
                and candidate.get("workspace") == workspace
            ),
            None,
        )
        if unreconciled is not None:
            state = unreconciled.get("state")
            summary = (
                "Muse workspace is quarantined because prior process-tree cleanup was not confirmed"
                if state == "cleanup_unconfirmed"
                else "Muse workspace has an unreconciled active session; explicit reconciliation is required"
            )
            raise SessionStateError(
                "session_busy",
                summary,
                logical_worker_id=worker_id,
                session_id=unreconciled.get("session_id"),
                resumed=resume,
            )
        record = workers.get(registry_key)
        expected = _binding_record(
            logical_worker_id=worker_id,
            session_id="",
            role=role,
            profile=profile,
            model=model,
            reasoning_effort=reasoning_effort,
            harness=harness,
            workspace=workspace,
            task_id=task_id,
            caller_scope=scope,
            state="reserved",
        )

        if resume:
            if not isinstance(record, dict):
                other_scope = any(
                    isinstance(candidate, dict)
                    and candidate.get("logical_worker_id") == worker_id
                    for candidate in workers.values()
                )
                raise SessionStateError(
                    "session_binding_mismatch" if other_scope else "session_unavailable",
                    (
                        "logical Muse worker exists only under a different caller scope"
                        if other_scope
                        else "logical Muse worker has no retained session mapping"
                    ),
                    logical_worker_id=worker_id,
                    resumed=True,
                )
            mismatches = _binding_mismatches(record, expected)
            if mismatches:
                raise SessionStateError(
                    "session_binding_mismatch",
                    "logical Muse session binding mismatch: " + ", ".join(mismatches),
                    logical_worker_id=worker_id,
                    session_id=record.get("session_id"),
                    resumed=True,
                )
            session_id = record.get("session_id")
            try:
                if str(uuid.UUID(session_id)) != str(session_id).lower():
                    raise ValueError
            except (ValueError, TypeError, AttributeError) as error:
                raise SessionStateError(
                    "adapter_internal",
                    "retained Muse session_id is invalid",
                    logical_worker_id=worker_id,
                    resumed=True,
                ) from error
        else:
            if record is not None:
                raise SessionStateError(
                    "resume_rejected",
                    "logical Muse worker already exists; resume it or use a new logical identity",
                    logical_worker_id=worker_id,
                    session_id=record.get("session_id") if isinstance(record, dict) else None,
                )
            if len(workers) >= MAX_SESSION_RECORDS:
                raise SessionStateError(
                    "adapter_internal",
                    "Muse session registry reached its bounded capacity",
                    logical_worker_id=worker_id,
                )
            session_id = str(uuid.uuid4())
            record = _binding_record(
                logical_worker_id=worker_id,
                session_id=session_id,
                role=role,
                profile=profile,
                model=model,
                reasoning_effort=reasoning_effort,
                harness=harness,
                workspace=workspace,
                task_id=task_id,
                caller_scope=scope,
                state="reserved",
            )
            workers[registry_key] = record
            _save_registry(runtime, registry)
            created = True
    locks_root = _session_locks_root(runtime)
    _ensure_private_dir(locks_root)
    lock_path = locks_root / f"{session_id}.lock"
    try:
        lock_fd = _open_private_lock(lock_path, nonblocking=True)
    except BlockingIOError as error:
        if created:
            with _registry_guard(runtime):
                registry = _load_registry(runtime)
                current = registry["workers"].get(registry_key)
                if isinstance(current, dict) and current.get("session_id") == session_id:
                    del registry["workers"][registry_key]
                    _save_registry(runtime, registry)
        raise SessionStateError(
            "session_busy",
            "logical Muse session already has an active invocation",
            logical_worker_id=worker_id,
            session_id=session_id,
            resumed=resume,
        ) from error

    lease = SessionLease(worker_id, session_id, resume, lock_fd)
    try:
        _update_state(runtime, worker_id, session_id, "active")
    except Exception:
        lease.release()
        raise
    return lease


def finish_worker_session(
    runtime: RuntimePaths,
    lease: SessionLease,
    *,
    state: str,
) -> None:
    """Persist terminal resumability state, then release the per-session lease."""

    # Persist terminal/quarantine state before releasing the process-local
    # flock. If persistence fails, keep the flock held fail-closed for the
    # lifetime of this adapter process rather than exposing an unknown session.
    _update_state(runtime, lease.logical_worker_id, lease.session_id, state)
    lease.release()


def read_worker_session(
    runtime: RuntimePaths,
    logical_worker_id: str,
    caller_scope: str | None = None,
) -> dict[str, Any] | None:
    """Return a private registry record copy for diagnostics/tests."""

    worker_id = _safe_worker_id(logical_worker_id, resume=True)
    scope = _safe_scope(caller_scope)
    key = _registry_key(worker_id, scope)
    with _registry_guard(runtime):
        registry = _load_registry(runtime)
        record = registry["workers"].get(key)
        return None if record is None else dict(record)


def retire_worker_session(
    runtime: RuntimePaths,
    logical_worker_id: str,
    caller_scope: str | None = None,
) -> None:
    """Explicitly retire one logical mapping when its caller lifecycle closes."""

    worker_id = _safe_worker_id(logical_worker_id, resume=True)
    scope = _safe_scope(caller_scope)
    key = _registry_key(worker_id, scope)
    with _registry_guard(runtime):
        registry = _load_registry(runtime)
        record = registry["workers"].get(key)
        if not isinstance(record, dict):
            return
        session_id = record.get("session_id")
        locks_root = _session_locks_root(runtime)
        _ensure_private_dir(locks_root)
        lock_path = locks_root / f"{session_id}.lock"
        try:
            lock_fd = _open_private_lock(lock_path, nonblocking=True)
        except BlockingIOError as error:
            raise SessionStateError(
                "session_busy",
                "cannot retire an active logical Muse session",
                logical_worker_id=worker_id,
                session_id=session_id,
            ) from error
        try:
            del registry["workers"][key]
            _save_registry(runtime, registry)
        finally:
            fcntl.flock(lock_fd, fcntl.LOCK_UN)
            os.close(lock_fd)
        try:
            lock_path.unlink()
        except FileNotFoundError:
            pass
