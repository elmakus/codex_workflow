# Brainstorm — upstream 1.1.18 alignment

Date: `2026-09-20`
Scope ID: `upstream-1.1.18-alignment`
Revision: `R1`
Status: `ready_for_definition`

## Problem / goal

Review changes made in upstream `viettran-edgeAI/codex_workflow` since this fork diverged, then deliberately select which changes should shape the next architecture of `elmakus/codex_workflow`.

## Current understanding

### Verified facts

- The meaningful common baseline is upstream commit `414a5d301ff17ca6e655330474c8346863d0d5d0` from 2026-09-08.
- Fork `main` is `1.1.17-private.12`; upstream `main` is `1.1.18`.
- Upstream 1.1.18 introduces Explorer, three independent Investigator lanes per bounded investigation problem, direct parent-child worker reporting, project-only same-version update handling, stale legacy route-reference rejection, and removal of Companion.
- The fork already has historical per-project workflow source resolution and multi-project catch-up behavior.
- The fork currently has compute profiles `plus`, `luna-xhigh`, `pro-x5`, and `muse-max`; Companion and Micro Executor are fork-specific active roles.
- The fork intentionally enables `[features] multi_agent = true` while removing workflow-owned `[features.multi_agent_v2]` settings.

See `research/upstream-1.1.18-audit.md` for source-grounded details.

### Existing accepted decisions

None before this scope. The choices below were explicitly accepted by the user during this brainstorming session and are to be promoted through Project Definition.

## Ideas / alternatives considered

The session compared whole-upstream synchronization against selective semantic adoption. Whole-branch merge/cherry-pick was rejected because the fork has materially diverged in Muse runtime, compute profiles, worker topology, and lifecycle semantics.

## Explicit user/product choices to promote

- Preserve existing historical source-backup and multi-project update safeguards.
- Adopt upstream-style project-only same-version updates, avoiding redundant release downloads, limiting backup/mutations to the target project, and producing a true no-op when current.
- Preserve the fork's explicit downgrade protection when adapting project-only update behavior.
- Adopt stale legacy route-reference hardening and extend reviewed `--legacy-local-instructions` support to bootstrap/install/update.
- Do not adopt upstream's `multi_agent_v2` timeout values or change multi-agent versioning as part of this scope.
- Remove Companion and all Companion-specific lifecycle/bootstrap/profile exceptions.
- Add Explorer and split responsibilities: Explorer maps existing project context; Investigator researches fault hypotheses, solution alternatives, feasibility and prior art.
- For every bounded problem that requires Investigator, use exactly three independent Investigator lanes with one shared Problem ID, distinct Task IDs and complementary search angles; Main compares evidence/disagreement rather than voting.
- Remove hard report word caps and require the smallest complete, evidence-linked, decision-ready report.
- Remove Micro Executor.
- Keep Senior Executor, Tester and Archivist.
- Keep only compute profiles `plus` and `muse-max`; remove `luna-xhigh`, `pro-x5` and their code/tests/docs.
- Retain the Muse runtime/session lifecycle. Under `muse-max`, all remaining worker roles are Muse-backed; there is no internal Companion exception.
- Keep Material Event Push only for internal Codex workers in `plus`; remove Muse-specific Material Event Push policy.
- Use direct worker-to-Main reporting only; remove sibling worker messaging.
- Preserve the fork's proportionate documentation read. Do not adopt upstream's mandatory complete `agent_docs/` session intake.
- Keep Medium route and Deployment Token Report absent.
- Rename `workflow_break_down.md` to `workflow_breakdown.md`.
- Bring in/adapt the upstream benchmark/deep-dive documentation so it describes the resulting fork accurately.
- Do not wholesale merge upstream 1.1.18; adopt selected behavior semantically.

## Research needed

Completed for this scope. The upstream/fork comparison is recorded in `research/upstream-1.1.18-audit.md`.

## Open questions

None that materially block Project Definition.

## Outcome of this session

- Tentative conclusions: selective upstream adoption with a simplified worker/profile architecture.
- Explicit user/product choices to promote through Project Definition: all choices listed above.
- Research still needed: none before Definition.
- Open questions: none.
- Next phase/action: `ready for definition`
- Definition promotion authorization: `user_authorized`
- Definition promotion subject: `upstream-1.1.18-alignment@R1`

> Nothing in this file becomes accepted requirement/decision authority by itself. Project Definition owns promotion into canonical `requirements/` and `decisions/`.
