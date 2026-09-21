# M07 Integrated Acceptance — native profile and provider foundation

Date: 2026-09-21
Milestone: `M07`
Plan: `planning/MASTER_PLAN.md` R4
Result: `GREEN`

## Accepted implementation subject

The final functional implementation for M07 is present by `commit:b2291cc64210a15fb63cc1f05fccf08395e3193d`. M07-T02 was independently reviewed against frozen subject `2e3090795f965c1beafff56b4ca71056851c4c49`, which adds only implementation evidence/OpenSpec reconciliation after the functional result. Later review/close commits do not change M07 behavior.

## Authority and evidence

- Master Plan R4 / M07.
- Requirements REQ-030, REQ-031, REQ-040, REQ-042 and REQ-044.
- Accepted decision `decisions/DEC-007-muse-native-profile.md` with inherited DEC-001/002/003/006 constraints.
- OpenSpec `openspec/changes/muse-native-profile/specs/muse-native-profile/spec.md`.
- `M07-T01`: terminal, independent review GREEN.
- `M07-T02`: terminal, independent review GREEN.

## Milestone acceptance

- Exactly three supported profiles are established: `plus`, external `muse-max`, and native `muse-native`.
- All six `muse-native` workers resolve through the native Codex lifecycle to `muse-spark-1.3-contributor`, reasoning `max`, and provider selector `cliproxyapi`; Main remains user-selected.
- Provider ownership is fail-closed and non-secret: `muse-native` requires the configured user-owned CLIProxyAPI route with a non-empty endpoint and Responses wire API before profile/update mutation. No provider/model/effort fallback is introduced.
- Internal Codex agents remain enabled for `plus` and `muse-native`; external `muse-max` retains its disabled-native-worker path and external Muse transport.
- Selected `muse-native` survives the update path with exact worker/provider state. Missing/incompatible provider configuration fails during planning before update application; unrelated provider/config data remains preserved.
- Repository verification is GREEN on the accepted implementation: runtime 101/101, Muse adapter 39/39, focused profile 14/14, compile, package validate/build and archive verification.
- The installed-environment provider probe correctly returns a precise external configuration/auth blocker: the workstation has no configured `[model_providers.cliproxyapi]` route and the unauthenticated provider endpoint responds 401. This is the explicit M07 permitted outcome; no fallback or credential mutation occurred.
- No Muse/Meta OAuth token, CLIProxyAPI client credential or other secret is copied into repository state/evidence.
- No external-Muse session/JSONL/wait/raw-run/`--disable-sandbox` machinery was made a requirement of the native path merely for parity.
- Existing `plus` and external `muse-max` regression boundaries remain GREEN.

## Close result

M07 satisfies its approved outcome and stable acceptance. The repository foundation is GREEN and can feed M08 JIT execution preparation. The existing installed environment still lacks the user-owned CLIProxyAPI credential/provider configuration required for OAuth-backed M08 live runtime acceptance; that prerequisite does not invalidate M07 and must not be repaired by repository code.
