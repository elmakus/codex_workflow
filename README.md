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
- Fresh/independent execution boundaries use isolated worker contexts. Codex-backed
  profiles use new internal workers with `fork_turns="none"` by default;
  `muse-max` uses fresh one-shot Muse Code invocations. App-level `create_thread`
  is not used merely to obtain review independence, milestone isolation, or a
  context reset.
- Worker compute is selected by one global runtime profile. `plus` preserves the
  historical Luna-heavy allocation. `luna-xhigh` puts every non-Senior workflow
  worker on GPT-5.6 Luna XHigh. `pro-x5` moves ordinary worker roles to GPT-5.6
  Sol Low. Experimental `muse-max` changes the worker harness itself: all seven
  workflow roles run through native Muse Code on Muse Spark 1.3 Contributor with
  `max` reasoning. Main is never changed by the profile.
- In the three Codex-backed profiles, Senior Executor stays Sol Medium. In
  `muse-max`, Senior is also Muse Spark 1.3 Contributor Max so the live test has
  no non-Muse worker role.
- Micro Executor is a distinct seventh worker below Default Executor. Its
  installed internal model follows the active Codex-backed profile: Luna High in
  `plus`, Luna XHigh in `luna-xhigh`, and Sol Low in `pro-x5`. Spark High remains
  an optional acceleration route for `plus` and `pro-x5`; `luna-xhigh`
  intentionally keeps Micro on Luna XHigh. `muse-max` routes Micro through Muse
  Code like every other worker.
- Investigator may inspect one bounded project evidence gap, Internet sources,
  or both, while remaining read-only. Main retains causal, architecture,
  solution, integration, and acceptance decisions.
- Companion is bootstrapped at the first deployment-state entry while Main's
  context is still small. Codex-backed profiles keep one persistent Companion;
  `muse-max` uses a bounded one-shot Muse Companion and fresh later invocations.
  Bootstrap remains scoped to the current goal and does not trigger a full `agent_docs/`
  or unrelated-module intake.
- Main owns deployment updates to `project_progress.md`, `project_diary.md`, and
  `latest_session_work.md`. Archivist handles other assigned documentation and
  the read-only closing handoff.
- Heavy has no workflow-imposed aggregate worker limit for Codex-backed profiles.
  The workflow does not write a fixed `max_concurrent_threads_per_session`;
  available concurrency is left to the Codex platform/account. The initial
  `muse-max` live-test runtime is deliberately sequential rather than emulating
  subagent concurrency with unmanaged background processes.
- Heavy is orchestration-only for Main. Codex-backed profiles retain long
  event-driven waits; `muse-max` treats each bounded `muse exec` process as the
  worker boundary. User-visible update cadence follows the active profile.
- Running internal Codex workers may use `send_message` to `/root` only for rare
  material mid-task `BLOCKER`, `COURSE_CHANGE`, or `CRITICAL_PARTIAL` events.
  Routine progress and normal completion never use that channel. One-shot Muse
  workers do not emulate `send_message` or polling.
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
| Companion | Luna/max | Luna/xhigh | Sol/low | Muse Contributor/max | Bounded read-only project context. Persistent for Codex-backed profiles; one-shot for the Muse live test. |
| Investigator | Luna/max | Luna/xhigh | Sol/low | Muse Contributor/max | Disposable read-only project/Internet evidence investigation. |
| Archivist | Luna/max | Luna/xhigh | Sol/low | Muse Contributor/max | Verified documentation outside Main-owned deployment-state docs and closing handoff. |

If a micro task ceases to be tiny and deterministic, Main reclassifies it
directly to Default Executor or Senior Executor; there is no Micro reasoning
escalation ladder.

The active selection is stored in
`~/.codex/codex_workflow/settings.toml`. Missing settings on a pre-profile
installation mean `plus`. Profile switches rewrite the rendered Heavy
communication policy and settings in one compensating transaction; Codex-backed
profiles also render internal worker model/reasoning fields. `muse-max` leaves
those internal TOMLs valid but dormant and routes role execution through
`runtime/muse_worker.py`. Updates preserve the selected profile.

### Muse Max live-test profile

`muse-max` requires the official Muse Code CLI on `PATH`, an existing `muse login`,
and account access to `muse-spark-1.3-contributor` at `max` reasoning. The runner
uses the native harness directly; there is no OpenRouter or provider proxy in
this path. It launches the equivalent of:

```text
muse --disable-approval --trust-workspace exec \
  --model muse-spark-1.3-contributor \
  --reasoning-effort max \
  --prompt-file <generated-role-capsule>
```

The managed Muse sandbox stays enabled. The runner does not use `--yolo` or
`--disable-sandbox`, protects temporary prompt files with mode `0600`, and does
not grant `.git` mutation authority to workers. Authentication and subscription
usage remain owned by Muse Code.

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
| `codex_workflow --profile muse-max` | Keep Main unchanged and run every workflow worker through Muse Code with Muse Spark 1.3 Contributor Max; normal concise orchestration, sequential live-test runtime. |
| `codex_workflow --personal` | Change project workflow preferences. |
| `codex_workflow --disable` / `--enable` | Disable or enable the selected project. |
| `codex_workflow --remove` | Preview removal, then remove owned files after explicit confirmation; preserve project documents. |

For release preparation and provenance see [RELEASING.md](RELEASING.md).
For the ownership map see [workflow_break_down.md](workflow_break_down.md).
