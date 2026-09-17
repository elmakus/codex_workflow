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


MODEL = "muse-spark-1.3-contributor"
REASONING_EFFORT = "max"
ROLE_RE = re.compile(r"^[A-Za-z0-9_-]+$")
WORKER_MARKER = re.compile(r"^# codex-workflow-worker: ([A-Za-z0-9_-]+)$", re.MULTILINE)


class MuseWorkerError(RuntimeError):
    pass


def _worker_contract(role: str) -> str:
    if not ROLE_RE.fullmatch(role):
        raise MuseWorkerError(f"unsafe worker role: {role!r}")
    path = Path.home() / ".codex" / "agents" / f"{role}.toml"
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


def build_prompt(role: str, task: str) -> str:
    contract = _worker_contract(role)
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


def build_command(muse: str, prompt_file: str) -> list[str]:
    # Approval/trust are Muse Code global flags. Keep the managed sandbox on;
    # neither --yolo nor --disable-sandbox is permitted by this runner.
    return [
        muse,
        "--disable-approval",
        "--trust-workspace",
        "exec",
        "--model",
        MODEL,
        "--reasoning-effort",
        REASONING_EFFORT,
        "--prompt-file",
        prompt_file,
    ]


def run(role: str, workspace_arg: str, task_file: str, *, dry_run: bool = False) -> int:
    workspace = _workspace(workspace_arg)
    task = _task(task_file)
    prompt = build_prompt(role, task)
    muse = shutil.which("muse")
    if muse is None:
        raise MuseWorkerError(
            "Muse Code CLI is not installed or is not on PATH; install it and run `muse login` first"
        )

    if dry_run:
        command = build_command(muse, "<temporary-prompt>")
        print(
            json.dumps(
                {
                    "harness": "muse-code",
                    "model": MODEL,
                    "reasoning_effort": REASONING_EFFORT,
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
            build_command(muse, prompt_path),
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
        description="Run one codex_workflow role via Muse Spark 1.3 Contributor Max."
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
