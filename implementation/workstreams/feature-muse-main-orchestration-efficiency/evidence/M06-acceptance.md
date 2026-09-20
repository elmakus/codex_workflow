# M06 Integrated Acceptance — quiet milestone communication and final Muse acceptance

Date: 2026-09-20
Milestone: `M06`
Plan: `planning/MASTER_PLAN.md` R3
Result: `GREEN`

## Accepted implementation subject

The final M06 behavior is implemented by exact subject `commit:3114bcc1c732adebf16efc9876301f98cae77d85`. Later branch commits through milestone close are Project Workflow state/evidence only and do not change the reviewed behavior.

## Authority and evidence

- Master Plan R3 / M06 and its verification strategy.
- Requirements REQ-025, REQ-026, REQ-027 and REQ-029, with final integrated preservation/acceptance for REQ-022 through REQ-028.
- Accepted decision `decisions/DEC-006-muse-event-driven-waiting.md`.
- Accepted M05 checkpoint: `implementation/workstreams/feature-muse-main-orchestration-efficiency/evidence/M05-acceptance.md`.
- M06-T01 execution evidence: `implementation/workstreams/feature-muse-main-orchestration-efficiency/evidence/M06-T01.md`.
- M06-T01 independent GREEN review: `implementation/workstreams/feature-muse-main-orchestration-efficiency/evidence/M06-T01-review.md`.

## Milestone acceptance

- `muse-max` rendered communication uses quiet milestone orchestration and suppresses routine worker-start/wait/status/session/recovery/Git/liveness narration: GREEN.
- User-meaningful phase transitions remain allowed; blockers requiring user input, immediate risk/authorization needs, material scope/architecture changes and the normal final result remain visible: GREEN.
- Historical hard silence is not restored: GREEN.
- `plus` communication/runtime semantics remain unchanged: GREEN by bounded diff and rendering regression.
- No timer, heartbeat or liveness-only update is introduced as a reason to wake Main: GREEN.
- M05 one-cell event-driven wait contract remains active and regression-visible: GREEN.
- Exact-subject regressions independently reran `scripts/test_muse_profile.py` 9/9 GREEN and `scripts/test_muse_adapter.py` 39/39 GREEN.
- Final live Muse acceptance remains healthy for several minutes and completes normally: GREEN; the controlled foreground `sleep 190` run completed with `M06_REAL_MUSE_WAIT_OK`.
- Independent Codex-LB readback confirms zero periodic Main/model requests for the accepted conversation between `2026-09-20 19:19:27.239352 UTC` and `2026-09-20 19:23:12.294952 UTC`, approximately 225.06 seconds.
- Independent rollout readback confirms one accepted outer Code Mode `exec` interval containing the initial `tools.exec_command` and same-cell `tools.write_stdin` waits, with no competing top-level custom-tool call during the healthy wait.
- Post-run readback shows no surviving controlled M06 worker process and no repository change from the live worker.
- No release/version/tag/GitHub Release or external deployment boundary was crossed.

## Close result

M06 satisfies its approved milestone outcome and stable acceptance. The complete DEC-006 event-driven wait plus quiet-milestone communication feature is GREEN on the workstream branch. No M06 corrective work or unresolved product decision remains; workstream final-integration refresh/review remains the next lifecycle gate before integration to `main`.
