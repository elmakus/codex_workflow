# codex_workflow 1.1.17-private.3

Source basis: upstream `v1.1.17` commit `414a5d301ff17ca6e655330474c8346863d0d5d0` plus owner-specific changes through this release.

## Changes

- Keep the existing long event-driven `wait_agent` lifecycle unchanged.
- Add rare worker-to-Main material-event push through runtime `send_message` for only:
  - `BLOCKER`
  - `COURSE_CHANGE`
  - `CRITICAL_PARTIAL`
- Forbid routine progress, heartbeat, ETA, status chatter, ordinary partial findings, duplicate unchanged events, and manual normal-completion notifications on that channel.
- Require Main to process only the affected orchestration consequence when a material message is received, including when it wakes Main from `wait_agent`, without falling back to worker polling.
- Preserve worker-to-`/root` as the default routing topology; sibling messaging remains exceptional.
- Fold the material-event regression contract into the canonical `scripts/test_workflow_runtime.py` suite.
- Keep early bounded Companion bootstrap, Heavy-only execution, silent deployment output gating, and private release/update ownership unchanged.

## Verification

Release verification must pass:

- `python3 -B scripts/test_workflow_runtime.py -v`
- package validation
- package build
- independent archive verification

The exact release commit, test count, ZIP SHA-256, and final asset verification are recorded in the GitHub Release when published.
