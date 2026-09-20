# MF-T01 independent review evidence

Status: RED
Card: `MF-T01`
Exact reviewed subject: `408dec625109d923938dc3e77ee22ac251a65ad0`
Review requirement: RECOMMENDED

## Authority checked

- `implementation/workstreams/issue-compaction-runtime-routing/cards/MF-T01.md`
- `requirements/REQUIREMENTS.md` REQ-011..REQ-014
- `decisions/DEC-002-compute-profiles.md`
- `decisions/DEC-003-communication-context.md`
- `implementation/workstreams/issue-compaction-runtime-routing/INTAKE.md`
- `research/upstream-1.1.18-audit.md`

## Independent verification

On the exact reviewed subject, an isolated detached worktree passed:

- `scripts/test_workflow_runtime.py` — 98/98 GREEN
- `scripts/test_muse_profile.py` — 7/7 GREEN
- `scripts/test_muse_adapter.py` — 39/39 GREEN
- package validation — `valid=true`, six expected workers
- changed Python compile probe — GREEN
- `git diff --check f9d3dd0867ef9ea8b59583663a68faba876ebe93..HEAD` — GREEN

## Blocking finding

Acceptance #4 is not met for the effective MultiAgentV2 form already documented by repository authority.

The accepted upstream audit records MultiAgentV2 as:

```toml
[features.multi_agent_v2]
enabled = true
```

But `patch_codex_settings(..., internal_agents_enabled=False)` only rejects the flat shape `[features] multi_agent_v2 = true`. For the documented nested-table form, `parsed["features"]["multi_agent_v2"]` is a table/dict, so the guard does not fire. The subsequent legacy-owned-key cleanup removes `enabled = true` and the table instead of failing closed.

Independent reproduction on the exact subject with `[features.multi_agent_v2] enabled = true` returned normally and rendered `[agents] enabled = false`; no `ValidationError` was raised.

This violates the Card requirement that `muse-max` fail closed when an effective externally-owned MultiAgentV2 enable would override the internal-agent guard, and it weakens the promised preservation of unrelated user-owned configuration.

## Corrective classification

Bounded L1/L2 implementation correction inside accepted authority:

- detect the documented nested-table effective enable before any legacy cleanup, while retaining the existing flat-form defensive check if desired;
- add focused regression coverage proving `muse-max` rejects `[features.multi_agent_v2] enabled = true` without mutating profile/config state;
- rerun the existing required regression suites and freeze a new exact review subject.

No requirements, decisions, plan, or user/product authority change is needed.
