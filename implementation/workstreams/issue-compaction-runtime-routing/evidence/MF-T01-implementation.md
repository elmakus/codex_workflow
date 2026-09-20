# MF-T01 implementation evidence

Status: implementation complete; independent review pending
Card: `MF-T01`
Exact implementation subject: `e8b553403fc4af36c9fc9da9fbca00d31ea7868c`
Implementation baseline after accepted micro-fix contract: `f9d3dd0867ef9ea8b59583663a68faba876ebe93`

## Result

The compaction-routing failure now has two deliberately small defenses.

1. **Fail-closed Codex worker surface under `muse-max`.** Profile/bootstrap/update rendering sets workflow-owned `[agents].enabled = false` for `muse-max` and `true` for `plus`. DEC-002's existing `[features].multi_agent = true` ownership is preserved. Profile switches update the guard transactionally with the profile state.
2. **Token-light post-compaction routing invariant.** The globally managed `operate/user_AGENTS.md` adds one compact rule: immediately before each deployment worker dispatch, reread only `~/.codex/codex_workflow/settings.toml`; do not trust a profile/harness remembered across turns or compaction. Under `muse-max`, all six workflow roles must use `runtime/muse_worker.py`, even if a stale long-lived session still exposes internal Codex agent tools.

An effective external MultiAgentV2 enable causes `muse-max` profile materialization to fail closed, including both the defensive flat `[features] multi_agent_v2 = true` form and the documented upstream `[features.multi_agent_v2] enabled = true` table form. This is checked before legacy-key cleanup because enabled MultiAgentV2 takes precedence over `agents.enabled`.

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

All checks were rerun from exact corrected HEAD `e8b553403fc4af36c9fc9da9fbca00d31ea7868c`.

- `PYTHONDONTWRITEBYTECODE=1 python3 scripts/test_workflow_runtime.py` → **98/98 GREEN**
- `PYTHONDONTWRITEBYTECODE=1 python3 scripts/test_muse_profile.py` → **7/7 GREEN**
- `PYTHONDONTWRITEBYTECODE=1 python3 scripts/test_muse_adapter.py` → **39/39 GREEN**
- `python3 -B codex_workflow/runtime/workflow.py validate --package-root codex_workflow --json` → **valid=true**, six expected workers
- Python source compile probe for changed Python files → **GREEN**
- `git diff --check f9d3dd0867ef9ea8b59583663a68faba876ebe93..HEAD` → **GREEN**

Focused regression coverage proves:
- bootstrap/default `plus` keeps `agents.enabled=true`;
- `plus -> muse-max -> plus` changes only the profile-aware agent guard while preserving unrelated config and `features.multi_agent=true`;
- `muse-max` retains all six Muse-backed allocations;
- selected `muse-max` survives update with the internal-agent guard still disabled;
- both flat `features.multi_agent_v2=true` and documented table `[features.multi_agent_v2] enabled=true` are rejected before profile mutation;
- the globally managed dispatch invariant is present and explicitly covers context compaction and stale exposed tools.

## Corrective review history

The first independent review of subject `408dec625109d923938dc3e77ee22ac251a65ad0` was RED because the guard recognized only a flat `[features] multi_agent_v2 = true` value while repository authority documents upstream's effective table form as `[features.multi_agent_v2] enabled = true`. That table form passed through without `ValidationError` and was then removed by legacy cleanup.

The bounded correction now recognizes the table/dict form before cleanup while retaining the flat-form defensive check. A dedicated regression proves the documented table override is rejected without mutating the active profile or config bytes.

## External state

No production Workstation deployment, profile change, release, merge, or other live runtime mutation was performed by this Card.
