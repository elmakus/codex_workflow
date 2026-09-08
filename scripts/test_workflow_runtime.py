"""Current regression entry point for the owner-customized Heavy-only workflow.

The full lifecycle regression suite remains in ``workflow_runtime_regression``.
This entry point replaces only assertions whose private contract intentionally
changed, while retaining the base lifecycle, migration, safety, packaging, and
platform-setting regression coverage.
"""

from __future__ import annotations

import contextlib
import hashlib
import io
import json
import sys
import tempfile
import tomllib
import unittest
import warnings
import zipfile
from pathlib import Path
from unittest import mock

import workflow_runtime_regression as base
from runtime.errors import ValidationError


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "codex_workflow"


def _asset_url(version: str, name: str) -> str:
    return (
        "https://github.com/elmakus/codex_workflow/releases/download/"
        f"v{version}/{name}"
    )


def _selection(version: str = "1.1.14-private.3"):
    import runtime.release as release

    name = f"codex_workflow-{version}.zip"
    return release.ReleaseSelection(
        version,
        release.parse_semver(version),
        name,
        _asset_url(version, name),
        _asset_url(version, "SHA256SUMS"),
    )


def _archive_bytes(entries: list[tuple[str | zipfile.ZipInfo, bytes]]) -> bytes:
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
        for member, content in entries:
            bundle.writestr(member, content)
    return output.getvalue()


def _assert_acquire_rejects(
    self: unittest.TestCase,
    archive: bytes,
    pattern: str,
    *,
    uncompressed_limit: int | None = None,
) -> None:
    import runtime.release as release

    selection = _selection()
    digest = hashlib.sha256(archive).hexdigest()
    checksums = f"{digest}  {selection.zip_name}\n".encode("ascii")
    limit = (
        mock.patch.object(release, "MAX_UNCOMPRESSED_BYTES", uncompressed_limit)
        if uncompressed_limit is not None
        else contextlib.nullcontext()
    )
    with (
        limit,
        mock.patch.object(release, "_read_url", side_effect=[archive, checksums]),
        self.assertRaisesRegex(ValidationError, pattern),
    ):
        release.acquire(selection)


def _test_private_version_and_user_marker_are_synchronized(
    self: unittest.TestCase,
) -> None:
    version = (PACKAGE / "operate" / "VERSION").read_text(encoding="utf-8").strip()
    self.assertEqual(version, "1.1.14-private.3")
    user_agents = (PACKAGE / "operate" / "user_AGENTS.md").read_text(
        encoding="utf-8"
    )
    marker = f"<!-- codex-workflow-version: {version} -->"
    self.assertEqual(user_agents.count(marker), 1)
    self.assertGreater(
        base.parse_semver("1.1.14-private.3"),
        base.parse_semver("1.1.14-private.2"),
    )
    self.assertEqual(base.NEXT_PACKAGE_VERSION, "1.1.14-private.4")


def _test_worker_models_and_reasoning(self: unittest.TestCase) -> None:
    worker_paths = sorted((PACKAGE / "agents").glob("*.toml"))
    self.assertEqual(
        {path.stem for path in worker_paths},
        {
            "default_executor",
            "senior_executor",
            "tester",
            "archivist",
            "companion",
            "investigator",
        },
    )
    for path in worker_paths:
        with self.subTest(worker=path.stem):
            config = tomllib.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(config["name"], path.stem)
            if path.stem == "senior_executor":
                self.assertEqual(config["model"], "gpt-6-astra")
                self.assertEqual(config["model_reasoning_effort"], "low")
            else:
                self.assertEqual(config["model"], "gpt-5.6-luna")
                self.assertEqual(config["model_reasoning_effort"], "max")


def _test_heavy_only_workflow_keeps_leaf_direct_path(
    self: unittest.TestCase,
) -> None:
    agents = (PACKAGE / "AGENTS.md").read_text(encoding="utf-8")
    self.assertIn("## Workflow", agents)
    self.assertIn("codex_workflow/heavy_route.md", agents)
    self.assertIn("In leaf state, work directly without reading", agents)
    self.assertIn("enter `deployment state`, read that Heavy contract", agents)
    self.assertNotIn("## Route Selection", agents)
    self.assertNotIn("**Light**", agents)
    self.assertNotIn("**Medium**", agents)
    self.assertFalse((PACKAGE / "medium_route.md").exists())

    heavy = (PACKAGE / "heavy_route.md").read_text(encoding="utf-8")
    self.assertIn("Use as the substantive-work contract under `AGENTS.md`.", heavy)
    self.assertNotIn("## Fast Path", heavy)
    self.assertIn("## Closure", heavy)


def _test_heavy_uses_instruction_only_long_wait_policy(
    self: unittest.TestCase,
) -> None:
    heavy = (PACKAGE / "heavy_route.md").read_text(encoding="utf-8")
    flat = " ".join(heavy.split())
    self.assertIn("one event-driven `wait_agent` call", flat)
    self.assertIn("short repeated polling", flat)
    self.assertIn("`1500000` ms (25 minutes)", heavy)
    self.assertNotIn("`1200000` ms", heavy)
    self.assertIn("`300000`-`3600000` ms", heavy)
    self.assertIn("continue immediately when a child finishes early", flat)
    self.assertIn("not by itself a reason to poll status", flat)
    self.assertIn("issue another appropriately long `wait_agent`", flat)


def _test_user_command_contract_exposes_owner_update_channel(
    self: unittest.TestCase,
) -> None:
    instructions = (PACKAGE / "operate" / "user_AGENTS.md").read_text(
        encoding="utf-8"
    )
    self.assertIn("codex_workflow --update", instructions)
    self.assertIn("codex_workflow --check-update", instructions)
    self.assertIn("operate/check_update.md", instructions)
    self.assertTrue((PACKAGE / "operate" / "check_update.md").is_file())
    self.assertIn("codex_workflow --remove", instructions)

    personalization = (PACKAGE / "operate" / "personalization_guide.md").read_text(
        encoding="utf-8"
    )
    self.assertIn("resources/personalization.md", personalization)
    self.assertIn("missing or invalid", personalization)
    self.assertIn("copy that section's complete", personalization)


def _test_operational_policies_are_compact_and_knowledge_aware(
    self: unittest.TestCase,
) -> None:
    policies = {
        "AGENTS.md": (PACKAGE / "AGENTS.md").read_text(encoding="utf-8"),
        "heavy_route.md": (PACKAGE / "heavy_route.md").read_text(encoding="utf-8"),
    }
    self.assertLess(len(policies["AGENTS.md"].splitlines()), 90)
    self.assertLess(len(policies["heavy_route.md"].splitlines()), 240)
    self.assertFalse((PACKAGE / "medium_route.md").exists())

    required_documentation_policy = (
        "Read documentation in proportion to the task.",
        "When continuing, start from the specified checkpoint.",
        "Search `agent_docs/` and read the documents or sections",
        "needed to understand the task, its constraints, and dependencies.",
        "Expand the read when context is missing.",
        "Read the complete set only when the scope of work requires it.",
        "A missing unrelated document does not block the task.",
    )
    for name, text in policies.items():
        with self.subTest(documentation_policy=name):
            section = text.split("## Proportionate Documentation Read\n", 1)[1]
            section = section.split("\n## ", 1)[0].strip()
            flat = " ".join(section.split())
            for requirement in required_documentation_policy:
                self.assertIn(requirement, flat)
            for retired_requirement in (
                "Required Documentation Read",
                "framework exactly once",
                "one shared session-level read",
                "leave deployment entry incomplete",
                "intake blocker",
            ):
                self.assertNotIn(retired_requirement, " ".join(text.split()))

    heavy = policies["heavy_route.md"]
    heavy_flat = " ".join(heavy.split())
    self.assertIn("## Your Role and Authority", heavy)
    self.assertIn("You are the main agent and central knowledge director", heavy)
    self.assertIn("For each task, decide which roles are useful", heavy_flat)
    self.assertIn("## Orchestrator-First Execution", heavy)
    self.assertIn("Main is an orchestrator, not an executor", heavy)
    self.assertIn("prefer `delegate -> resume -> wait -> integrate`", heavy_flat)
    self.assertIn("If assigned work needs intervention", heavy)
    self.assertIn("Resume it when possible", heavy)
    self.assertIn("irrecoverably unavailable", heavy)
    self.assertIn("not a reason for Main to take over", heavy_flat)
    self.assertIn("prefer resuming the same worker or thread", heavy_flat)
    self.assertIn("`wait_agent` timeout that returns no new worker state", heavy_flat)
    self.assertIn("not by itself a reason to poll status", heavy_flat)
    for timeout_action in (
        "list threads",
        "message",
        "interrupt",
        "replace",
        "inspect worker progress",
    ):
        self.assertIn(timeout_action, heavy)
    self.assertIn("issue another appropriately long `wait_agent`", heavy_flat)
    self.assertIn("identify only the available recovery sources", heavy_flat)
    for recovery_source in (
        "predecessor thread",
        "worktree",
        "branch",
        "handoff path",
        "existing commits",
    ):
        self.assertIn(recovery_source, heavy)
    self.assertIn("replacement worker owns detailed state recovery", heavy_flat)
    self.assertIn("determine completed versus remaining work", heavy_flat)
    self.assertIn("delegate recovery + continuation", heavy_flat)
    self.assertIn("Main should not reconstruct the predecessor's detailed work", heavy_flat)
    self.assertIn("genuinely trivial and shorter than delegation overhead", heavy_flat)
    self.assertIn("required solely for orchestration", heavy_flat)
    for non_takeover_task in (
        "implementation",
        "security review",
        "repository migration",
        "material Git/GitHub operations",
        "testing",
        "delegable research",
    ):
        self.assertIn(non_takeover_task, heavy)
    self.assertIn('"Take over to make progress"', heavy_flat)
    self.assertIn('"take over to go faster"', heavy_flat)
    self.assertIn("## Silent Orchestration", heavy)
    self.assertIn("Default to silent orchestration", heavy)
    self.assertIn("Perform routine coordination through tool calls", heavy_flat)
    for routine_event in (
        "waited",
        "resumed",
        "messaged a worker",
        "listed threads",
        "routine status check",
        "chose not to take over assigned work",
        "left other work queued",
        "reused an existing result",
        "next routine orchestration step",
    ):
        self.assertIn(routine_event, heavy)
    self.assertIn(
        "Do not report a successful intermediate stage or repository", heavy_flat
    )
    self.assertIn("everything is proceeding as expected, stay silent", heavy_flat)
    self.assertIn("defer successful progress to the final response", heavy_flat)
    for meaningful_update in (
        "blocker requires the user's decision",
        "security or publication risk",
        "scope or plan changes materially",
        "user explicitly requested progress updates",
        "whole task completes",
    ):
        self.assertIn(meaningful_update, heavy_flat)
    self.assertIn("Always send the normal final response", heavy_flat)
    self.assertNotIn("at most one brief line", heavy_flat)
    self.assertIn("Silence limits narration only", heavy)
    self.assertIn("## Agents You Can Use", heavy)
    for role in (
        "Companion",
        "Investigator",
        "Default Executor",
        "Senior Executor",
        "Tester",
        "Archivist",
    ):
        self.assertIn(role, heavy)
    self.assertIn("Reserve the Astra production worker", heavy)
    self.assertIn("## Assign Companion", heavy)
    self.assertIn('agent_type="companion"', heavy)
    self.assertIn('task_name="companion"', heavy)
    self.assertIn('fork_turns="none"', heavy)
    self.assertIn("Reuse the same Companion across later assignments", heavy_flat)
    self.assertIn("## Role-Specific Work Packages", heavy)
    for capsule in (
        "**Task ID**",
        "**Project Context Scope**",
        "**Research Question + Goal**",
        "**Implementation Context + Ownership**",
        "**Verification Context**",
        "**Documentation Context + Audience**",
    ):
        self.assertIn(capsule, heavy)
    self.assertIn("Require workers to echo Task ID in every report", heavy)
    self.assertIn("Do not repeat the worker's substantive task", heavy)
    self.assertNotIn("intervene directly", heavy)
    self.assertIn("## Orchestration Guidance", heavy)
    self.assertIn("synthesize their results\n  once", heavy)
    self.assertIn("bounded batches or sequential", heavy_flat)
    self.assertIn("main-agent tracking cost", heavy_flat)
    self.assertIn("orchestration-only tool operations", heavy_flat)
    self.assertIn("rather than taking over its task", heavy_flat)
    self.assertIn("Preserve sequential ordering", heavy)
    self.assertIn("Do not\nmaximize concurrency without a concrete benefit", heavy)
    self.assertIn("Use\n  appropriately long lifecycle waits", heavy)
    self.assertIn("Heavy does not impose an aggregate active-subagent limit", heavy_flat)
    self.assertNotIn("at most 20 active subagents", heavy)
    self.assertIn("at most one Senior Executor", heavy)
    self.assertIn("Create and coordinate every worker directly", heavy)
    self.assertNotIn("## Fast Path", heavy)
    self.assertIn("## Closure", heavy)
    self.assertNotIn("deployment-token-report", heavy)
    self.assertIn("one\n  event-driven `wait_agent` call", heavy)
    self.assertIn("`1500000` ms (25 minutes)", heavy)
    self.assertNotIn("`1800000` ms", heavy)
    self.assertIn("wait again rather\n  than polling", heavy)

    agents_policy = policies["AGENTS.md"]
    self.assertIn("## Design Principles", agents_policy)
    self.assertIn("## Rollout Efficiency", agents_policy)
    self.assertIn("## Working State", agents_policy)
    self.assertIn("## Project Documentation", agents_policy)
    self.assertIn("## Workflow", agents_policy)
    self.assertIn("## Platform Paths", agents_policy)
    self.assertIn("In leaf state, work directly without reading", agents_policy)
    self.assertIn("codex_workflow/heavy_route.md", agents_policy)
    self.assertNotIn("codex_workflow/medium_route.md", agents_policy)
    self.assertNotIn("Select one of these routes", agents_policy)
    self.assertNotIn("Follow the user's route selection", agents_policy)

    handoff_contract = (PACKAGE / "archivist.md").read_text(encoding="utf-8")
    archivist = (PACKAGE / "agents" / "archivist.toml").read_text(encoding="utf-8")
    self.assertIn('agent_type="archivist"', handoff_contract)
    self.assertIn("one closure owner for each deployment", handoff_contract)
    self.assertNotIn("Medium or Heavy", handoff_contract)
    self.assertIn("in leaf state", handoff_contract)
    self.assertIn("durable, cross-session documentation framework", archivist)
    self.assertIn("canonical home", archivist)
    self.assertIn("cross-reference rather than duplicate", archivist)
    self.assertNotIn("deployment-token-report", archivist)

    executor = (PACKAGE / "agents" / "default_executor.toml").read_text(
        encoding="utf-8"
    )
    senior = (PACKAGE / "agents" / "senior_executor.toml").read_text(
        encoding="utf-8"
    )
    tester = (PACKAGE / "agents" / "tester.toml").read_text(encoding="utf-8")
    companion = (PACKAGE / "agents" / "companion.toml").read_text(encoding="utf-8")
    investigator = (PACKAGE / "agents" / "investigator.toml").read_text(
        encoding="utf-8"
    )
    self.assertIn('model = "gpt-5.6-luna"', executor)
    self.assertIn('model = "gpt-6-astra"', senior)
    self.assertIn('model_reasoning_effort = "low"', senior)
    for worker in (executor, tester, companion, investigator, archivist):
        self.assertIn('model_reasoning_effort = "max"', worker)

    retired_architecture_phrases = (
        "wave barrier",
        "evidence manifest",
        "verification_ledger",
        "repair packet",
        "root-cause gate",
        "fixed execution pipeline",
        "predefined pipeline",
    )
    instruction_surfaces = {
        **policies,
        "archivist.md": handoff_contract,
        "archivist.toml": archivist,
        "default_executor.toml": executor,
        "senior_executor.toml": senior,
        "tester.toml": tester,
        "companion.toml": companion,
        "investigator.toml": investigator,
        "README.md": (ROOT / "README.md").read_text(encoding="utf-8"),
        "workflow_break_down.md": (ROOT / "workflow_break_down.md").read_text(
            encoding="utf-8"
        ),
    }
    for name, text in instruction_surfaces.items():
        lowered = text.lower()
        for phrase in retired_architecture_phrases:
            self.assertNotIn(phrase, lowered, name)


def _test_release_module_targets_owner_fork_and_requires_assets(
    self: unittest.TestCase,
) -> None:
    import runtime.release as release

    self.assertEqual(release.RELEASES_REPOSITORY, "elmakus/codex_workflow")
    self.assertEqual(
        release.RELEASES_URL,
        "https://api.github.com/repos/elmakus/codex_workflow/releases?per_page=100",
    )
    for name in (
        "ReleaseSelection",
        "select_releases",
        "select_latest",
        "summarize_release_notes",
        "acquire",
    ):
        self.assertTrue(hasattr(release, name), name)

    version = "1.1.14-private.3"
    zip_name = f"codex_workflow-{version}.zip"
    records = [
        {
            "draft": True,
            "tag_name": "v9.9.9",
            "assets": [],
        },
        {
            "draft": False,
            "tag_name": "v1.1.14-private.4",
            "assets": [
                {
                    "name": "codex_workflow-1.1.14-private.4.zip",
                    "browser_download_url": _asset_url(
                        "1.1.14-private.4",
                        "codex_workflow-1.1.14-private.4.zip",
                    ),
                }
            ],
        },
        {
            "draft": False,
            "tag_name": f"v{version}",
            "assets": [
                {
                    "name": zip_name,
                    "browser_download_url": _asset_url(version, zip_name),
                },
                {
                    "name": "SHA256SUMS",
                    "browser_download_url": _asset_url(version, "SHA256SUMS"),
                },
            ],
            "body": "# Owner release\n- Verified update",
            "html_url": (
                "https://github.com/elmakus/codex_workflow/releases/tag/"
                f"v{version}"
            ),
        },
    ]
    with mock.patch.object(release, "_read_json_url", return_value=records):
        selected = release.select_releases()
    self.assertEqual(len(selected), 1)
    self.assertEqual(selected[0].version_text, version)
    self.assertEqual(selected[0].zip_name, zip_name)
    self.assertIn(
        "Owner release",
        release.summarize_release_notes(selected[0].release_notes),
    )


def _test_release_discovery_paginates(self: unittest.TestCase) -> None:
    import runtime.release as release

    first_page = [
        {"draft": True, "tag_name": f"v0.0.{index}", "assets": []}
        for index in range(release.RELEASE_PAGE_SIZE)
    ]
    version = "1.1.14-private.4"
    name = f"codex_workflow-{version}.zip"
    second_page = [
        {
            "draft": False,
            "tag_name": f"v{version}",
            "assets": [
                {"name": name, "browser_download_url": _asset_url(version, name)},
                {
                    "name": "SHA256SUMS",
                    "browser_download_url": _asset_url(version, "SHA256SUMS"),
                },
            ],
        }
    ]
    with mock.patch.object(
        release,
        "_read_json_url",
        side_effect=[first_page, second_page],
    ) as read:
        selected = release.select_releases()
    self.assertEqual([item.version_text for item in selected], [version])
    self.assertEqual(
        [call.args[0] for call in read.call_args_list],
        [release.RELEASES_URL, f"{release.RELEASES_URL}&page=2"],
    )


def _test_release_rejects_untrusted_asset_urls(self: unittest.TestCase) -> None:
    import runtime.release as release

    version = "1.1.14-private.4"
    name = f"codex_workflow-{version}.zip"
    records = [
        {
            "draft": False,
            "tag_name": f"v{version}",
            "assets": [
                {"name": name, "browser_download_url": "file:///tmp/workflow.zip"},
                {
                    "name": "SHA256SUMS",
                    "browser_download_url": _asset_url(version, "SHA256SUMS"),
                },
            ],
        }
    ]
    with (
        mock.patch.object(release, "_read_json_url", return_value=records),
        self.assertRaisesRegex(ValidationError, "release asset URL"),
    ):
        release.select_releases()
    with self.assertRaisesRegex(ValidationError, "untrusted"):
        release._read_url("file:///tmp/workflow.zip", 1)


def _test_release_download_enforces_size_limit(self: unittest.TestCase) -> None:
    import runtime.release as release

    url = _asset_url("1.1.14-private.3", "SHA256SUMS")

    class FakeResponse:
        headers = {}

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def geturl(self):
            return url

        def read(self, size: int):
            return b"12345"

    opener = mock.Mock()
    opener.open.return_value = FakeResponse()
    with (
        mock.patch.object(release.urllib.request, "build_opener", return_value=opener),
        self.assertRaisesRegex(ValidationError, "exceeds 4 byte limit"),
    ):
        release._read_url(url, 1, max_bytes=4)


def _test_release_acquire_verifies_checksum_and_extracts_asset(
    self: unittest.TestCase,
) -> None:
    import runtime.release as release

    archive = _archive_bytes(
        [("codex_workflow/operate/VERSION", b"1.1.14-private.3\n")]
    )
    digest = hashlib.sha256(archive).hexdigest()
    selection = _selection()
    checksums = f"{digest}  {selection.zip_name}\n".encode("ascii")
    with mock.patch.object(release, "_read_url", side_effect=[archive, checksums]):
        temporary, package = release.acquire(selection)
    self.addCleanup(temporary.cleanup)
    self.assertEqual(
        (package / "operate" / "VERSION").read_text(encoding="utf-8"),
        "1.1.14-private.3\n",
    )


def _test_release_acquire_rejects_wrong_checksum(self: unittest.TestCase) -> None:
    import runtime.release as release

    archive = _archive_bytes(
        [("codex_workflow/operate/VERSION", b"1.1.14-private.3\n")]
    )
    selection = _selection()
    checksums = f"{'0' * 64}  {selection.zip_name}\n".encode("ascii")
    with (
        mock.patch.object(release, "_read_url", side_effect=[archive, checksums]),
        self.assertRaisesRegex(ValidationError, "checksum mismatch"),
    ):
        release.acquire(selection)


def _test_checksum_parser_rejects_malformed_and_duplicate_entries(
    self: unittest.TestCase,
) -> None:
    import runtime.release as release

    filename = "codex_workflow-1.1.14-private.3.zip"
    digest = "a" * 64
    with self.assertRaisesRegex(ValidationError, "malformed"):
        release._checksum_for(
            f"{digest}  {filename}\n{digest} extra {filename}\n",
            filename,
        )
    with self.assertRaisesRegex(ValidationError, "unique"):
        release._checksum_for(
            f"{digest}  {filename}\n{digest} *{filename}\n",
            filename,
        )
    self.assertEqual(
        release._checksum_for(f"{digest} *{filename}\n", filename),
        digest,
    )


def _test_release_acquire_rejects_unsafe_zip_members(
    self: unittest.TestCase,
) -> None:
    traversal = _archive_bytes(
        [("codex_workflow/../escape", b"x")]
    )
    _assert_acquire_rejects(self, traversal, "unsafe ZIP member")

    normalized_collision = _archive_bytes(
        [
            ("codex_workflow/data.txt", b"first"),
            ("codex_workflow/./data.txt", b"second"),
        ]
    )
    _assert_acquire_rejects(
        self,
        normalized_collision,
        "non-canonical ZIP member|colliding members",
    )

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        exact_duplicate = _archive_bytes(
            [
                ("codex_workflow/data.txt", b"first"),
                ("codex_workflow/data.txt", b"second"),
            ]
        )
    _assert_acquire_rejects(self, exact_duplicate, "colliding members")

    symlink = zipfile.ZipInfo("codex_workflow/link")
    symlink.create_system = 3
    symlink.external_attr = 0o120777 << 16
    _assert_acquire_rejects(
        self,
        _archive_bytes([(symlink, b"target")]),
        "symlink",
    )

    special = zipfile.ZipInfo("codex_workflow/device")
    special.create_system = 3
    special.external_attr = 0o020666 << 16
    _assert_acquire_rejects(
        self,
        _archive_bytes([(special, b"x")]),
        "special filesystem entry",
    )

    oversized = _archive_bytes([("codex_workflow/data", b"xx")])
    _assert_acquire_rejects(
        self,
        oversized,
        "uncompressed size limit",
        uncompressed_limit=1,
    )


def _test_check_update_command_uses_owner_release(self: unittest.TestCase) -> None:
    import runtime.release as release

    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        codex_home = root / "codex-home"
        version_path = codex_home / "codex_workflow" / "operate" / "VERSION"
        version_path.parent.mkdir(parents=True)
        version_path.write_text("1.1.14-private.3\n", encoding="utf-8")
        candidate = _selection("1.1.14-private.4")
        candidate = release.ReleaseSelection(
            candidate.version_text,
            candidate.version,
            candidate.zip_name,
            candidate.zip_url,
            candidate.checksums_url,
            "# Changes\n- Safe owner update",
            (
                "https://github.com/elmakus/codex_workflow/releases/tag/"
                "v1.1.14-private.4"
            ),
        )
        output = io.StringIO()
        argv = [
            "workflow.py",
            "check-update",
            "--codex-home",
            str(codex_home),
            "--json",
        ]
        with (
            mock.patch.object(
                base.workflow_cli,
                "select_releases",
                return_value=[candidate],
            ),
            mock.patch.object(sys, "argv", argv),
            contextlib.redirect_stdout(output),
        ):
            self.assertEqual(base.workflow_cli.main(), 0)
        payload = json.loads(output.getvalue())
        self.assertEqual(payload["status"], "update available")
        self.assertEqual(payload["installed"], "1.1.14-private.3")
        self.assertEqual(payload["available"], "1.1.14-private.4")
        self.assertEqual(
            payload["asset"],
            "codex_workflow-1.1.14-private.4.zip",
        )
        self.assertEqual(
            [item["version"] for item in payload["updates"]],
            ["1.1.14-private.4"],
        )


def _test_check_update_handles_empty_release_channel(
    self: unittest.TestCase,
) -> None:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        codex_home = root / "codex-home"
        version_path = codex_home / "codex_workflow" / "operate" / "VERSION"
        version_path.parent.mkdir(parents=True)
        version_path.write_text("1.1.14-private.3\n", encoding="utf-8")
        output = io.StringIO()
        argv = [
            "workflow.py",
            "check-update",
            "--codex-home",
            str(codex_home),
            "--json",
        ]
        with (
            mock.patch.object(base.workflow_cli, "select_releases", return_value=[]),
            mock.patch.object(sys, "argv", argv),
            contextlib.redirect_stdout(output),
        ):
            self.assertEqual(base.workflow_cli.main(), 0)
        payload = json.loads(output.getvalue())
        self.assertEqual(payload["status"], "no releases")
        self.assertEqual(payload["installed"], "1.1.14-private.3")
        self.assertIsNone(payload["available"])
        self.assertEqual(payload["updates"], [])


def _test_source_less_update_uses_verified_owner_release(
    self: unittest.TestCase,
) -> None:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        project = root / "project"
        project.mkdir()
        codex_home = root / "codex-home"
        installed_version = codex_home / "codex_workflow" / "operate" / "VERSION"
        installed_version.parent.mkdir(parents=True)
        installed_version.write_text("1.1.14-private.3\n", encoding="utf-8")
        incoming = root / "incoming"
        incoming_version = incoming / "operate" / "VERSION"
        incoming_version.parent.mkdir(parents=True)
        incoming_version.write_text("1.1.14-private.3\n", encoding="utf-8")
        release_temporary = mock.Mock()
        selection = mock.sentinel.selection
        argv = [
            "workflow.py",
            "update",
            "--codex-home",
            str(codex_home),
            "--project",
            str(project),
            "--json",
        ]
        with (
            mock.patch.object(
                base.workflow_cli,
                "select_latest",
                return_value=selection,
            ) as select,
            mock.patch.object(
                base.workflow_cli,
                "acquire",
                return_value=(release_temporary, incoming),
            ) as acquire,
            mock.patch.object(
                base.workflow_cli,
                "_delegate_update",
                return_value=0,
            ) as delegate,
            mock.patch.object(sys, "argv", argv),
        ):
            self.assertEqual(base.workflow_cli.main(), 0)
        select.assert_called_once_with()
        acquire.assert_called_once_with(selection)
        delegate.assert_called_once()
        release_temporary.cleanup.assert_called_once_with()


def _test_explicit_source_update_skips_release_discovery(
    self: unittest.TestCase,
) -> None:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        project = root / "project"
        project.mkdir()
        codex_home = root / "codex-home"
        installed_version = codex_home / "codex_workflow" / "operate" / "VERSION"
        installed_version.parent.mkdir(parents=True)
        installed_version.write_text("1.1.14-private.3\n", encoding="utf-8")
        incoming = root / "incoming"
        incoming_version = incoming / "operate" / "VERSION"
        incoming_version.parent.mkdir(parents=True)
        incoming_version.write_text("1.1.14-private.3\n", encoding="utf-8")
        argv = [
            "workflow.py",
            "update",
            "--source",
            str(incoming),
            "--codex-home",
            str(codex_home),
            "--project",
            str(project),
            "--json",
        ]
        with (
            mock.patch.object(
                base.workflow_cli,
                "select_latest",
                side_effect=AssertionError("release discovery must not run"),
            ),
            mock.patch.object(
                base.workflow_cli,
                "_delegate_update",
                return_value=0,
            ) as delegate,
            mock.patch.object(sys, "argv", argv),
        ):
            self.assertEqual(base.workflow_cli.main(), 0)
        delegate.assert_called_once()


def _test_update_removes_retired_medium_route(self: unittest.TestCase) -> None:
    self.bootstrap()
    retired = self.runtime.runtime / "medium_route.md"
    retired.write_text("# Retired Medium Route\n", encoding="utf-8")
    state_path = self.runtime.runtime / "install_state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    state["owned_runtime_files"].append("medium_route.md")
    state_path.write_text(json.dumps(state) + "\n", encoding="utf-8")

    incoming = self.incoming_package(
        "heavy-only-incoming",
        base.NEXT_PACKAGE_VERSION,
    )
    base.plan_update(incoming, self.runtime, self.project).apply()

    self.assertFalse(retired.exists())


def _test_update_adds_new_workflow_owned_runtime_file(
    self: unittest.TestCase,
) -> None:
    self.bootstrap()
    incoming = self.incoming_package(
        "new-owned-runtime-file",
        base.NEXT_PACKAGE_VERSION,
    )
    relative = Path("operate") / "new_owned_guide.md"
    (incoming.root / relative).write_text("new managed file\n", encoding="utf-8")

    base.plan_update(incoming, self.runtime, self.project).apply()

    installed = self.runtime.runtime / relative
    self.assertEqual(installed.read_text(encoding="utf-8"), "new managed file\n")
    state = json.loads(
        (self.runtime.runtime / "install_state.json").read_text(encoding="utf-8")
    )
    self.assertIn(relative.as_posix(), state["owned_runtime_files"])


# Replace only assertions whose contract intentionally changed. Keep every other
# lifecycle, migration, safety, packaging, and platform-setting regression test.
delattr(
    base.PrivateCustomizationTests,
    "test_private_version_and_user_marker_are_synchronized",
)
base.PrivateCustomizationTests.test_private_version_and_user_marker_are_synchronized = (
    _test_private_version_and_user_marker_are_synchronized
)

delattr(
    base.PrivateCustomizationTests,
    "test_worker_customization_changes_only_luna_reasoning",
)
base.PrivateCustomizationTests.test_worker_models_and_reasoning = (
    _test_worker_models_and_reasoning
)

delattr(
    base.PrivateCustomizationTests,
    "test_heavy_is_default_and_keeps_explicit_routes_and_fast_path",
)
base.PrivateCustomizationTests.test_heavy_only_workflow_keeps_leaf_direct_path = (
    _test_heavy_only_workflow_keeps_leaf_direct_path
)
base.PrivateCustomizationTests.test_heavy_uses_instruction_only_long_wait_policy = (
    _test_heavy_uses_instruction_only_long_wait_policy
)

base.MarkerTests.test_user_command_contract_exposes_only_supported_lifecycle_prompts = (
    _test_user_command_contract_exposes_owner_update_channel
)
base.MarkerTests.test_operational_policies_are_compact_and_knowledge_aware = (
    _test_operational_policies_are_compact_and_knowledge_aware
)
if hasattr(base.MarkerTests, "test_check_update_command_is_removed"):
    delattr(base.MarkerTests, "test_check_update_command_is_removed")

for retired_test in (
    "test_release_module_has_no_public_discovery_or_download_api",
    "test_source_less_update_fails_closed_without_network",
):
    delattr(base.ReleaseTests, retired_test)

base.ReleaseTests.test_release_module_targets_owner_fork_and_requires_assets = (
    _test_release_module_targets_owner_fork_and_requires_assets
)
base.ReleaseTests.test_release_discovery_paginates = _test_release_discovery_paginates
base.ReleaseTests.test_release_rejects_untrusted_asset_urls = (
    _test_release_rejects_untrusted_asset_urls
)
base.ReleaseTests.test_release_download_enforces_size_limit = (
    _test_release_download_enforces_size_limit
)
base.ReleaseTests.test_release_acquire_verifies_checksum_and_extracts_asset = (
    _test_release_acquire_verifies_checksum_and_extracts_asset
)
base.ReleaseTests.test_release_acquire_rejects_wrong_checksum = (
    _test_release_acquire_rejects_wrong_checksum
)
base.ReleaseTests.test_checksum_parser_rejects_malformed_and_duplicate_entries = (
    _test_checksum_parser_rejects_malformed_and_duplicate_entries
)
base.ReleaseTests.test_release_acquire_rejects_unsafe_zip_members = (
    _test_release_acquire_rejects_unsafe_zip_members
)
base.ReleaseTests.test_check_update_command_uses_owner_release = (
    _test_check_update_command_uses_owner_release
)
base.ReleaseTests.test_check_update_handles_empty_release_channel = (
    _test_check_update_handles_empty_release_channel
)
base.ReleaseTests.test_source_less_update_uses_verified_owner_release = (
    _test_source_less_update_uses_verified_owner_release
)
base.ReleaseTests.test_explicit_source_update_skips_release_discovery = (
    _test_explicit_source_update_skips_release_discovery
)

base.LifecycleIntegrationTests.test_update_removes_retired_medium_route = (
    _test_update_removes_retired_medium_route
)
base.LifecycleIntegrationTests.test_update_adds_new_workflow_owned_runtime_file = (
    _test_update_adds_new_workflow_owned_runtime_file
)


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
