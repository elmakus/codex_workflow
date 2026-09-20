# MF-T01 implementation evidence

Status: implementation complete; independent review pending
Card: `MF-T01`
Exact implementation subject: `408dec625109d923938dc3e77ee22ac251a65ad0`
Implementation baseline after accepted micro-fix contract: `f9d3dd0867ef9ea8b59583663a68faba876ebe93`

## Result

The compaction-routing failure now has two deliberately small defenses.

1. **Fail-closed Codex worker surface under `muse-max`.** Profile/bootstrap/update rendering sets workflow-owned `[agents].enabled = false` for `muse-max` and `true` for `plus`. DEC-002's existing `[features].multi_agent = true` ownership is preserved. Profile switches update the guard transactionally with the profile state.
2. **Token-light post-compaction routing invariant.** The globally managed `operate/user_AGENTS.md` adds one compact rule: immediately before each deployment worker dispatch, reread only `~/.codex/codex_workflow/settings.toml`; do not trust a profile/harness remembered across turns or compaction. Under `muse-max`, all six workflow roles must use `runtime/muse_worker.py`, even if a stale long-lived session still exposes internal Codex agent tools.

A known external `[features].multi_agent_v2 = true` override causes `muse-max` profile materialization to fail closed, because upstream Codex documents that enabled MultiAgentV2 takes precedence over `agents.enabled`.

No full Heavy/delegation/document reload was added after compaction. Muse process/session semantics and all compute allocations are unchanged.

## Changed production surface

- `codex_workflow/runtime/platform_settings.py`
- `codex_workflow/runtime/runtime_ops.py`
- `codex_workflow/runtime/compute_profiles.py`
- `codex_workflow/operate/user_AGENTS.md`
- `codex_workflow/operate/profile.md`

Regression coverage:
- `scripts/test_workflow_runtime.py`
- `scripts/test_muse_profile.py`

## Verification on exact subject

All checks were run from exact HEAD `408dec625109d923938dc3e77ee22ac251a65ad0`.

- `PYTHONDONTWRITEBYTECODE=1 python3 scripts/test_workflow_runtime.py` → **98/98 GREEN**
- `PYTHONDONTWRITEBYTECODE=1 python3 scripts/test_muse_profile.py` → **7/7 GREEN**
- `PYTHONDONTWRITEBYTECODE=1 python3 scripts/test_muse_adapter.py` → **39/39 GREEN**
- `python3 -B codex_workflow/runtime/workflow.py validate --package-root codex_workflow --json` → **valid=true**, six expected workers
- Python source compile probe for changed Python files → **GREEN**
- `git diff --check 8130efb340ea2c6308e33c96dbff2a53bc98fc49..HEAD` → **GREEN**
- Release package build + archive verification → **GREEN**
- Package SHA-256: `4d405286a29677a9711b9645170a3a4ae6ea7b3e607c8046feb108f1c495e0e5`

Focused regression coverage proves:
- bootstrap/default `plus` keeps `agents.enabled=true`;
- `plus -> muse-max -> plus` changes only the profile-aware agent guard while preserving unrelated config and `features.multi_agent=true`;
- `muse-max` retains all six Muse-backed allocations;
- selected `muse-max` survives update with the internal-agent guard still disabled;
- external modern `features.multi_agent_v2=true` is rejected before profile mutation;
- the globally managed dispatch invariant is present and explicitly covers context compaction and stale exposed tools.

## External state

No production Workstation deployment, profile change, release, merge, or other live runtime mutation was performed by this Card.
