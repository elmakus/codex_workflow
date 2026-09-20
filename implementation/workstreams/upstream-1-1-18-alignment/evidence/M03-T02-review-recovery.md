# M03-T02 independent review recovery

Verdict: RED
Reviewed subject: `b07e93a29aa70f97e585bbdaf5b41e8a44d1ea5e`
Card: `M03-T02 — Plus-only Material Event Push and two-profile communication contract`
Recovery reason: durable post-review scan found an acceptance-surface omission in the prior GREEN review.

## Blocking finding

`codex_workflow/operate/user_AGENTS.md` is an active installed operator command surface, but the reviewed subject still advertises both retired commands:

- `codex_workflow --profile luna-xhigh`
- `codex_workflow --profile pro-x5`

This contradicts the Card acceptance that active orchestration/profile surfaces name only `plus` and `muse-max`, and contradicts REQ-011 / DEC-002. The earlier GREEN evidence sampled `operate/profile.md` but omitted the command-dispatch surface in `operate/user_AGENTS.md`.

## Classification

The defect is a bounded L1/L2 implementation correction inside already accepted M03 authority. No requirement, decision, plan, research, release authorization, or external write is needed.

Required correction:
- remove the two retired profile command forms from `codex_workflow/operate/user_AGENTS.md`;
- add focused regression coverage that the installed command dispatch surface exposes only supported profile forms;
- rerun the M03 affected/full repository verification required by the Card;
- freeze the corrected exact subject for a new REQUIRED independent review.

The prior file `M03-T02-review.md` is preserved as superseded review history; this record is the recovered verdict for the same immutable failing subject.
