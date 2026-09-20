# Decision — Muse event-driven waiting and quiet milestone orchestration

- Decision ID: `DEC-006`
- Date: `2026-09-20`
- Status: `accepted`
- Authority: `user`
- Supersedes: `none`
- Related requirements: `REQ-022, REQ-023, REQ-024, REQ-025, REQ-026, REQ-027, REQ-028, REQ-029`
- Related milestone/card: `none`

## Context

Live Codex-LB and rollout evidence from a healthy roughly fourteen-minute Muse Executor run showed that Main was repeatedly re-entered while the same worker remained healthy. The observed interval contained 24 extra GPT-5.6 Sol Medium requests, mostly near-zero-reasoning large-cache turns, caused by the current Code Mode command/session wait topology rather than by `muse_worker.py` itself.

Upstream Codex source confirms that ordinary unified `exec_command` yield is capped around 30 seconds, while Code Mode has its own long-lived cell/wait semantics. Public Codex and Claude Code reports describe the same long-running-tool polling cost pattern, and MCP Tasks provides analogous task/notification semantics.

The user also chose to make `muse-max` quieter, but explicitly not to restore the former hard-silent `luna-xhigh` behavior.

## Decision

`muse-max` will use **event-driven Main waiting**: healthy Muse execution is runtime-owned and Main is re-entered only for a terminal result, terminal failure/cancellation/timeout, explicit user interaction, or another genuinely material event that requires Main.

Routine worker liveness MUST NOT be observed by repeated Main-driven terminal/session polling.

The implementation strategy is conditional and evidence-driven:

1. first prove the smallest native Codex path: one long-lived Code Mode `exec` cell owns the whole Muse launch-and-await sequence, including internal terminal-session waits, so those waits do not escape to repeated Main samples;
2. if that live feasibility gate fails, use the smallest dedicated managed wait/tool/broker surface that provides the same terminal/material-event semantics;
3. do not replace this with an unmanaged background process plus model polling.

`muse-max` communication will use **quiet milestone orchestration**. Routine operational narration is suppressed. Concise user-meaningful phase transitions remain allowed, and blockers, risks/authorization needs, material scope/architecture changes and final results remain visible.

The `plus` profile is not changed by this decision.

## Rationale

The dominant measured cost is repeated model re-entry with a very large cached context, not Muse reasoning or adapter polling. Moving liveness waiting below the model boundary directly addresses that cost.

Keeping a moderated milestone communication mode preserves useful visibility during long work without recreating the former hard-silent experience.

Trying the native Code Mode cell first minimizes new infrastructure. The fallback remains bounded because the accepted behavior is terminal/material-event waiting, not any specific transport.

## Alternatives considered

- Communication-only quieting: rejected as incomplete because hidden Main samples would remain.
- Larger `exec_command`/terminal yields plus prompting: rejected as sufficient architecture because the live path already crosses a roughly 30-second command boundary.
- Restore historical strict silent orchestration unchanged: rejected by explicit user preference.
- Immediately add a new MCP/broker service: deferred unless the native one-cell feasibility gate fails.
- Continue periodic Main polling: rejected.

## Consequences

- Planning must include a live feasibility gate for one-cell Code Mode waiting before freezing a heavier runtime surface.
- Acceptance must use both Codex-LB request evidence and Codex rollout/tool evidence, not only user-visible output.
- Existing Muse cancellation/session/recovery correctness remains a hard regression boundary.
- Profile rendering/docs/tests must distinguish quiet milestone communication from hard silence.
- A timer-based progress update is never sufficient reason to wake Main.

## Required authoritative updates

- Requirements / Project Definition: captured in `requirements/REQUIREMENTS.md` Revision R2.
- Planning: add a current-scope milestone sequence for wait-path feasibility/implementation and quiet communication, with live evidence gates.
- Task Card/OpenSpec: Execution Prep decides exact Card split and whether a dedicated behavior contract is warranted.
- PROJECT.md: add DEC-006 and current Definition provenance.

## Provenance

- Source discussion/request: `brainstorming/muse-main-orchestration-efficiency.md` — `muse-main-orchestration-efficiency@R1`
- Evidence/research: `research/muse-main-orchestration-efficiency.md` / `R-MUSE-MAIN-ORCH-01`
- Definition promotion authority: explicit user authorization on 2026-09-20
