# MF-T01 independent review evidence — corrected subject

Status: GREEN
Card: `MF-T01`
Exact reviewed subject: `e8b553403fc4af36c9fc9da9fbca00d31ea7868c`
Review requirement: RECOMMENDED

## Authority checked

- `implementation/workstreams/issue-compaction-runtime-routing/cards/MF-T01.md`
- `requirements/REQUIREMENTS.md` REQ-011..REQ-014
- `decisions/DEC-002-compute-profiles.md`
- `decisions/DEC-003-communication-context.md`
- `implementation/workstreams/issue-compaction-runtime-routing/INTAKE.md`
- `implementation/workstreams/issue-compaction-runtime-routing/evidence/MF-T01-implementation.md`
- Prior RED evidence for subject `408dec625109d923938dc3e77ee22ac251a65ad0`

## Independent inspection

The cumulative implementation range `f9d3dd0867ef9ea8b59583663a68faba876ebe93..e8b553403fc4af36c9fc9da9fbca00d31ea7868c` was inspected against the Card acceptance surface.

The corrected implementation:
- keeps `[features].multi_agent = true` while rendering `[agents].enabled = true` for `plus` and `false` for `muse-max`;
- applies that guard both during explicit profile switching and bootstrap/update materialization from the active profile;
- preserves unrelated TOML content through the existing targeted patching path;
- rejects effective MultiAgentV2 enablement before legacy cleanup for both the flat boolean form and the documented `[features.multi_agent_v2] enabled = true` table form;
- retains all six `muse-max` role allocations on `muse-code` and leaves Muse process/session semantics unchanged;
- adds a compact always-injected dispatch invariant that rereads only `~/.codex/codex_workflow/settings.toml` before each deployment worker dispatch, rejects remembered pre-compaction routing as authority, and forbids internal Codex multi-agent APIs under `muse-max`;
- introduces no full post-compaction Heavy/delegation/document reload.

The previous RED condition is resolved: the table-shaped MultiAgentV2 override is now detected as enabled before any mutation/cleanup and causes `ValidationError`.

## Independent verification

An isolated checkout of exact subject `e8b553403fc4af36c9fc9da9fbca00d31ea7868c` passed:

- `PYTHONDONTWRITEBYTECODE=1 python3 scripts/test_workflow_runtime.py` — 99/99 GREEN
- `PYTHONDONTWRITEBYTECODE=1 python3 scripts/test_muse_profile.py` — 7/7 GREEN
- `PYTHONDONTWRITEBYTECODE=1 python3 scripts/test_muse_adapter.py` — 39/39 GREEN
- package validation — `valid=true`, exactly six expected workers
- compile probe for changed runtime Python files — GREEN
- `git diff --check f9d3dd0867ef9ea8b59583663a68faba876ebe93..HEAD` — GREEN

Focused regressions independently confirm profile switching, unrelated-config preservation, both MultiAgentV2 conflict forms failing before mutation, selected `muse-max` surviving update with internal agents disabled, and the compact compaction/stale-tool dispatch invariant.

## Verdict

GREEN. All eight Card acceptance points are satisfied on the exact reviewed subject. No blocking or authority-expanding finding remains.
