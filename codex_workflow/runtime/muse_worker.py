"""Run one codex_workflow role through the native Muse Code harness."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import tomllib

PACKAGE_ROOT = Path(__file__).resolve().parent.parent
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from runtime.compute_profiles import read_compute_profile, worker_model
from runtime.errors import WorkflowError
from runtime.layout import WORKER_MARKER, RuntimePaths, default_codex_home


ROLE_RE = re.compile(r"^[A-Za-z0-9_-]+$")


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


def _task(path: str) -> str:
    task_path = Path(path).expanduser().resolve()
    if task_path.is_symlink() or not task_path.is_file():
        raise MuseWorkerError(f"task file is not a regular file: {task_path}")
    text = task_path.read_text(encoding="utf-8")
    if not text.strip():
        raise MuseWorkerError("task file is empty")
    return text.strip()


def build_prompt(role: str, task: str, runtime: RuntimePaths) -> str:
    contract = _worker_contract(role, runtime)
    return f"""You are a codex_workflow worker running through Muse Code.

ROLE CONTRACT
{contract}

TASK CAPSULE
{task}

EXTERNAL-HARNESS EXECUTION RULES
- The Codex Main agent remains the orchestrator. Do not create or coordinate other workers.
- Work only on the assigned role and task capsule.
- Do not modify .git internals or perform commits, pushes, merges, rebases, or branch changes.
- Preserve unrelated user work.
- Use the available repository tools and tests proportionately.
- Return the compact role report requested by the role contract when finished.
"""


def build_command(
    muse: str,
    prompt_file: str,
    *,
    model: str,
    reasoning_effort: str,
) -> list[str]:
    # M06 keeps the existing process-policy seam. Production sandbox/protocol
    # behavior is bound by the later adapter milestone from live M05 evidence.
    return [
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


def run(role: str, workspace_arg: str, task_file: str, *, dry_run: bool = False) -> int:
    runtime = _runtime_paths()
    profile, allocation = _muse_allocation(role, runtime)
    workspace = _workspace(workspace_arg)
    task = _task(task_file)
    prompt = build_prompt(role, task, runtime)
    muse = shutil.which("muse")
    if muse is None:
        raise MuseWorkerError(
            "Muse Code CLI is not installed or is not on PATH; install it and run `muse login` first"
        )

    if dry_run:
        command = build_command(
            muse,
            "<temporary-prompt>",
            model=allocation.model,
            reasoning_effort=allocation.reasoning_effort,
        )
        print(
            json.dumps(
                {
                    "profile": profile,
                    "harness": allocation.harness,
                    "model": allocation.model,
                    "reasoning_effort": allocation.reasoning_effort,
                    "role": role,
                    "workspace": str(workspace),
                    "command": command,
                },
                sort_keys=True,
            )
        )
        return 0

    prompt_path: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            prefix=f"codex-workflow-{role}-",
            suffix=".md",
            delete=False,
        ) as handle:
            handle.write(prompt)
            prompt_path = handle.name
        os.chmod(prompt_path, 0o600)
        completed = subprocess.run(
            build_command(
                muse,
                prompt_path,
                model=allocation.model,
                reasoning_effort=allocation.reasoning_effort,
            ),
            cwd=workspace,
            stdin=subprocess.DEVNULL,
            check=False,
        )
        return completed.returncode
    finally:
        if prompt_path is not None:
            try:
                Path(prompt_path).unlink()
            except FileNotFoundError:
                pass


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run one codex_workflow role through its active Muse Code allocation."
    )
    parser.add_argument("--role", required=True)
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--task-file", required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    try:
        return run(
            args.role,
            args.workspace,
            args.task_file,
            dry_run=args.dry_run,
        )
    except MuseWorkerError as error:
        print(f"muse worker error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
