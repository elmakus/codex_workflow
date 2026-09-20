# M05 Integrated Acceptance — event-driven Muse wait boundary

Date: 2026-09-20
Milestone: `M05`
Plan: `planning/MASTER_PLAN.md` R3
Result: `GREEN`

## Accepted implementation subject

The milestone behavior is implemented by exact subject `commit:1c0c0bf073308b8e87c009652e1192422445862c`. Later branch commits through this close are Project Workflow state/evidence only and do not change the reviewed behavior.

## Authority and evidence

- Master Plan R3 / M05.
- Requirements REQ-022, REQ-023, REQ-024, REQ-027, REQ-028 and unchanged-`plus` constraint REQ-029.
- Accepted decision `decisions/DEC-006-muse-event-driven-waiting.md`.
- `M05-T01`: terminal GREEN native-host feasibility with independent GREEN review.
- `M05-T02`: terminal GREEN native-path implementation/live acceptance with independent GREEN review.

## Milestone acceptance

- Isolated healthy wait exceeds two minutes with zero intervening Main requests: GREEN from M05-T01.
- Native Code Mode one-cell ownership across repeated internal terminal waits: GREEN from M05-T01 and activated in the M05-T02 Heavy/Delegation contract.
- Real Muse worker remains healthy for several minutes and completes normally: GREEN from M05-T02; foreground `sleep 190` completes with terminal marker `M05_REAL_MUSE_WAIT_OK`.
- Exact live conversation has no periodic Main/model sampling during the healthy wait: GREEN. Independent review re-read Codex-LB and confirmed request 129354 at 18:34:29.660004 UTC followed by request 129355 at 18:38:26.010823 UTC with no intervening request for that conversation.
- Matching rollout topology has no recurring top-level Main-driven liveness loop: GREEN from sanitized M05-T02 live evidence; one outer Code Mode `exec` owns the adapter launch and internal terminal waits.
- Timeout/cancellation/session-busy/fail-closed recovery and logical-session/artifact invariants remain GREEN: exact-subject `scripts/test_muse_adapter.py` independently reran 39/39 GREEN; M05-T01 separately exercised interruption/process-tree cleanup.
- Active profile/documentation contract regression: exact-subject `scripts/test_muse_profile.py` independently reran 8/8 GREEN.
- No unrelated `plus` implementation change: GREEN by exact diff and profile regressions.
- No fallback broker/wait surface was activated; no release/version/deployment boundary was crossed.

## Close result

M05 satisfies its approved milestone outcome and stable acceptance. The native DEC-006 one-cell wait path is the accepted predecessor for M06. No M05 corrective work or additional user/product decision is outstanding.
