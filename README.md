# elmakus codex_workflow fork

Version **1.1.17-private.10**, based directly on upstream prerelease `v1.1.17`
commit `414a5d301ff17ca6e655330474c8346863d0d5d0`.

This public fork keeps upstream's lifecycle/runtime foundation while applying
owner-specific orchestration, model, update-channel, and safety choices.

## Private behavior

- **Heavy is the only workflow route.** Leaf-state questions and genuinely
  trivial bounded actions work directly without subagents and without reading
  `heavy_route.md`; bounded but nontrivial work still enters Heavy.
- Deployment communication follows the active profile. `plus` allows restrained,
  outcome-oriented milestone updates, `luna-xhigh` keeps strict silent
  orchestration, and `pro-x5` and experimental `muse-max` allow normal concise
  progress. No profile permits hidden reasoning or narration of internal
  instruction-conflict resolution.
- Heavy uses progressive disclosure: standing orchestration stays in
  `heavy_route.md`; detailed work-package, Micro Execution, follow-up, and
  recovery guidance lives in `delegation.md` and is loaded only when needed.
- Fresh/independent execution boundaries use isolated worker contexts. Internal
  Codex roles use new workers with `fork_turns="none"` by default; the six
  Muse-backed `muse-max` roles use fresh one-shot Muse Code invocations.
  App-level `create_thread` is not used merely to obtain review independence,
  milestone isolation, or a context reset.
- Worker compute is selected by one global runtime profile. `plus` preserves the
  historical Luna-heavy allocation. `luna-xhigh` puts every non-Senior workflow
  worker on GPT-5.6 Luna XHigh. `pro-x5` moves ordinary worker roles to GPT-5.6
  Sol Low. `muse-max` is mixed-harness: Companion stays internal Codex on
  GPT-5.6 Luna XHigh, while the six remaining roles use native Muse Code on Muse
  Spark 1.3 Contributor with `max` reasoning. Main is never changed by the profile.
- In `plus`, `luna-xhigh`, and `pro-x5`, Senior Executor stays Sol Medium.
  In `muse-max`, Senior is one of the six Muse Spark 1.3 Contributor Max roles;
  Companion remains the persistent internal Luna XHigh role.
- Micro Executor is a distinct seventh worker below Default Executor. Its
  installed internal model follows the active Codex-backed profile: Luna High in
  `plus`, Luna XHigh in `luna-xhigh`, and Sol Low in `pro-x5`. Spark High remains
  an optional acceleration route for `plus` and `pro-x5`; `luna-xhigh`
  intentionally keeps Micro on Luna XHigh. `muse-max` routes Micro through Muse
  Code as one of its six Muse-backed roles.
- Investigator may inspect one bounded project evidence gap, Internet sources,
  or both, while remaining read-only. Main retains causal, architecture,
  solution, integration, and acceptance decisions.
- Companion is bootstrapped at the first deployment-state entry while Main's
  context is still small and remains one persistent internal Codex worker in every
  profile. Under `muse-max` it is GPT-5.6 Luna XHigh. Bootstrap remains scoped to
  the current goal and does not trigger a full `agent_docs/` or unrelated-module
  intake.
- Main owns deployment updates to `project_progress.md`, `project_diary.md`, and
  `latest_session_work.md`. Archivist handles other assigned documentation and
  the read-only closing handoff.
- Heavy has no workflow-imposed aggregate worker limit for internal Codex roles.
  The workflow does not write a fixed `max_concurrent_threads_per_session`;
  available concurrency is left to the Codex platform/account. Muse-backed
  `muse-max` calls use the bounded single-invocation adapter; lane-level Muse
  concurrency remains deferred to the managed concurrency milestone rather than
  being emulated with unmanaged background processes.
- Heavy is orchestration-only for Main. Internal Codex roles retain long
  event-driven waits; each Muse-backed role treats its bounded `muse exec` process
  as the worker boundary. User-visible update cadence follows the active profile.
- Running internal Codex workers, including the `muse-max` Companion, may use
  `send_message` to `/root` only for rare material mid-task `BLOCKER`,
  `COURSE_CHANGE`, or `CRITICAL_PARTIAL` events. Routine progress and normal
  completion never use that channel. One-shot Muse workers do not emulate
  `send_message` or polling.
- No token-accounting skill, deployment counting marker, usage-report table, or
  reporting obligation is included.
- Release discovery and downloads are restricted to GitHub Releases published
  from `elmakus/codex_workflow`. There is no background/startup auto-update and
  no release channel from upstream.
- Installation, updates, and compute-profile changes happen only when the owner
  asks. Subscription type is never detected or inferred automatically.

## Workflow and roles

For substantive work Main enters deployment state, bootstraps the session
Companion using the active worker runtime, and loads `codex_workflow/heavy_route.md`.
Main chooses only useful worker capabilities and owns scope, architecture,
scheduling, integration, acceptance, and final claims. Before preparing or
following up a worker package, using Micro Execution, or recovering a worker,
Main loads `~/.codex/codex_workflow/delegation.md`.

| Role | `plus` | `luna-xhigh` | `pro-x5` | `muse-max` | Responsibility |
| --- | --- | --- | --- | --- | --- |
| Micro Executor | Spark/high when available; fallback Luna/high | Luna/xhigh | Spark/high when available; fallback Sol/low | Muse Contributor/max | Tiny deterministic implementation subtasks inside Heavy. |
| Default Executor | Luna/max | Luna/xhigh | Sol/low | Muse Contributor/max | Normal bounded implementation and repair. |
| Senior Executor | Sol/medium | Sol/medium | Sol/medium | Muse Contributor/max | Exceptionally difficult bounded production or solution work. |
| Tester | Luna/max | Luna/xhigh | Sol/low | Muse Contributor/max | Independent verification. |
| Companion | Luna/max | Luna/xhigh | Sol/low | Luna/xhigh | Bounded read-only project context. Persistent internal Codex worker in every profile. |
| Investigator | Luna/max | Luna/xhigh | Sol/low | Muse Contributor/max | Disposable read-only project/Internet evidence investigation. |
| Archivist | Luna/max | Luna/xhigh | Sol/low | Muse Contributor/max | Verified documentation outside Main-owned deployment-state docs and closing handoff. |

If a micro task ceases to be tiny and deterministic, Main reclassifies it
directly to Default Executor or Senior Executor; there is no Micro reasoning
escalation ladder.

The active selection is stored in
`~/.codex/codex_workflow/settings.toml`. Missing settings on a pre-profile
installation mean `plus`. Profile switches rewrite the rendered Heavy
communication policy and settings in one compensating transaction. Every role
assigned to the internal Codex harness is rendered from the profile allocation;
under `muse-max`, that means Companion is rendered to Luna XHigh while the six
Muse-assigned role TOMLs remain valid but dormant and are routed through
`runtime/muse_worker.py`. Updates preserve the selected profile.

### Muse Max mixed-harness profile

`muse-max` requires the official Muse Code CLI on `PATH`, an existing `muse login`,
and account access to `muse-spark-1.3-contributor` at `max` reasoning. The runner
uses the native harness directly; there is no OpenRouter or provider proxy in
this path. It launches the equivalent of:

```text
muse exec --disable-approval --trust-workspace \
  --model muse-spark-1.3-contributor \
  --reasoning-effort max \
  --prompt-file <private-generated-role-capsule> \
  --workspace <assigned-workspace> \
  --json \
  --output-schema <private-generated-result-schema> \
  --session-id <run-uuid> \
  --user-input-auto-resolve \
  --disable-sandbox
```

The adapter continuously drains JSONL stdout and diagnostic stderr into private
per-run artifacts under `~/.codex/codex_workflow/muse_runs/`, validates exactly
one terminal lifecycle record plus the versioned final worker report, and prints
only one bounded normalized result on the normal path. Raw streams have per-run
size limits and retained runs are bounded by age, count, and aggregate size.

Timeout or cancellation sends graceful termination to the Muse process and the
captured descendant tree, including children that moved into a separate process
group/session, then escalates to hard termination after a bounded grace period.
Live workstation evidence for Muse Code 1.3.0 established that nested bubblewrap
cannot run in the current unprivileged Docker boundary, so this workstation path
uses `--disable-sandbox`; Docker remains the outer isolation boundary.
Temporary prompt/schema files and run artifacts are private, workers are not
granted `.git` mutation authority, and Muse authentication/subscription state
remains owned by the official CLI.

## Documentation locations

Project documents stay in `<project>/agent_docs/`: `project_overview.md`,
`project_core_tech.md`, `project_structure.md`, `project_progress.md`,
`project_diary.md`, `latest_session_work.md`, and assigned module documents.
Existing documents and protected project instructions are preserved during
migration. The progress and latest-session templates contain project state only,
not embedded maintenance instructions.

`~/.codex/codex_workflow/operate/` holds workflow command guides and version
metadata. The lifecycle launcher is
`~/.codex/codex_workflow/runtime/workflow.py`.

## Updates

The normal update channel is the owner's GitHub Releases in
`elmakus/codex_workflow`.

`codex_workflow --check-update` performs a read-only check. It accepts only
non-draft SemVer releases containing both the expected versioned ZIP and
`SHA256SUMS`.

`codex_workflow --update` downloads those assets, verifies SHA-256, applies
strict URL/path/size checks, safely extracts and validates the package, and
delegates migration to the incoming runtime. A verified local `--source` path
remains available internally for recovery and explicit/manual migrations.

The incoming package is the desired state of workflow-owned files. Unrelated
Codex settings/workers/skills, user content outside managed regions,
project-local instructions, personalization, `agent_docs/`, and the selected
compute profile are preserved. Updates create a timestamped backup and apply
through a compensating transaction.

## Commands

| Prompt | Purpose |
| --- | --- |
| `codex_workflow --install` | Install into the explicitly selected project. |
| `codex_workflow --check-update` | Read-only check of owner releases. |
| `codex_workflow --update` | Install the latest verified owner release into the selected project/runtime. |
| `codex_workflow --profile` | Show the active global compute profile and worker model/reasoning/harness mapping. |
| `codex_workflow --profile plus` | Use the historical Luna-heavy worker allocation. |
| `codex_workflow --profile luna-xhigh` | Use Luna XHigh for every non-Senior workflow worker; keep Senior on Sol Medium. |
| `codex_workflow --profile pro-x5` | Use Sol Low for ordinary workers and Sol Medium for Senior. |
| `codex_workflow --profile muse-max` | Keep Main unchanged; use one persistent internal GPT-5.6 Luna XHigh Companion and route the six remaining roles through Muse Spark 1.3 Contributor Max; normal concise orchestration. |
| `codex_workflow --personal` | Change project workflow preferences. |
| `codex_workflow --disable` / `--enable` | Disable or enable the selected project. |
| `codex_workflow --remove` | Preview removal, then remove owned files after explicit confirmation; preserve project documents. |

For release preparation and provenance see [RELEASING.md](RELEASING.md).
For the ownership map see [workflow_break_down.md](workflow_break_down.md).
