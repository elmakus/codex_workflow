# Independent review — M07-T02

Card: `M07-T02 — Native update preservation and live provider route smoke`
Review subject: `2e3090795f965c1beafff56b4ca71056851c4c49`
Verdict: `GREEN`

## Reviewed authority

- `implementation/workstreams/feature-muse-native-profile/cards/M07-T02.md`
- `planning/MASTER_PLAN.md` R4 — M07
- `requirements/REQUIREMENTS.md` — REQ-030, REQ-031, REQ-040, REQ-042, REQ-044
- `decisions/DEC-007-muse-native-profile.md` with applicable inherited DEC-001/002/003/006 constraints
- `openspec/changes/muse-native-profile/specs/muse-native-profile/spec.md`
- accepted M07-T01 implementation/review evidence
- `implementation/workstreams/feature-muse-native-profile/evidence/M07-T02.md`
- exact functional commits contained by the frozen subject: `14e08d08e899a4de79f2e6dbfdaad07208332fbf`, `31a956969e0ee0c22968df6602a8116e3d82f7c8`, `b2291cc64210a15fb63cc1f05fccf08395e3193d`

## Verdict evidence

- The frozen subject contains the bounded M07-T02 functional change in `runtime/runtime_ops.py` plus focused update regressions. Commits after the functional result and before the frozen subject add only durable implementation evidence and OpenSpec task reconciliation; no later functional-source drift is present.
- Update materialization reads the persisted selected profile, validates every provider required by that profile from existing user-owned `config.toml`, and raises before returning the update `OperationPlan` when the required `cliproxyapi` route is absent or incompatible. No update mutation is applied during this validation path.
- `muse-native` update now keeps internal Codex agents enabled while retaining the selected profile. Incoming worker templates are rendered through the existing profile authority, preserving all six workers at `muse-spark-1.3-contributor`, reasoning `max`, and provider `cliproxyapi`.
- `plus` remains enabled and provider-free; external `muse-max` remains disabled and provider-free. The new provider validation therefore has no provider requirement for either existing profile. The added regular-file check is consistent with the existing transaction/profile safety contract, which already refuses replacing a symlinked config target.
- Focused regressions prove selected `muse-native` survives update, exact agent/provider/worker state is retained, missing provider and wrong wire API fail closed without changing config/settings/workers, unrelated provider/config state is preserved, and the existing `muse-max` update path stays GREEN.
- The exact implementation evidence records full branch verification GREEN: runtime 101/101, Muse adapter 39/39, profile 14/14, compile, validate, build and archive verification. GitHub Actions run `35569162187` on the preceding test commit failed only because the two new tests hard-coded the prior package marker; the log shows both errors as `package version and user marker disagree`. Commit `b2291cc64210a15fb63cc1f05fccf08395e3193d` makes that fixture derive the current marker dynamically; no production code changed in that repair.
- Installed-environment smoke evidence is contract-compliant: the existing workstation has no configured `[model_providers.cliproxyapi]` route and the unauthenticated provider probe returns 401, so the Card records the explicitly permitted external environment/config blocker. No fallback route was attempted and no credential/token material was read, copied, persisted, rotated or repaired.
- No secret material appears in the reviewed repository/evidence, and the live blocker does not weaken later M08/M09 live acceptance gates.

No review finding requires correction to the reviewed subject.

Verdict: `GREEN`.
