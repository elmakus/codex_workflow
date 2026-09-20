# elmakus codex_workflow fork

Version **1.1.18-private.1**, selectively aligned to upstream `v1.1.18` while
preserving intentional fork-specific divergence. The meaningful common source
baseline remains upstream `v1.1.17` commit
`414a5d301ff17ca6e655330474c8346863d0d5d0`.

This public fork keeps upstream's lifecycle/runtime foundation while applying
owner-specific orchestration, model, update-channel, and safety choices.

## Private behavior

- **Heavy is the only workflow route.** Leaf-state questions and genuinely
  trivial bounded actions work directly without subagents and without reading
  `heavy_route.md`; bounded but nontrivial work still enters Heavy.
- Deployment communication follows one of exactly two supported profiles:
  `plus` uses restrained, outcome-oriented milestone updates and `muse-max`
  uses normal concise milestone updates. Neither profile permits hidden reasoning
  or narration of internal instruction-conflict resolution.
- Heavy uses progressive disclosure: standing orchestration stays in
  `heavy_route.md`; detailed worker-package, follow-up, and recovery guidance
  lives in `delegation.md` and is loaded only when needed.
- Fresh/independent execution boundaries use isolated worker contexts. Internal
  Codex roles under `plus` use new workers with `fork_turns="none"` by default;
  Muse-backed `muse-max` roles use new logical Muse worker/session identities
  when freshness is required. Ordinary follow-up and repair may resume the same
  bound Muse session through a new bounded invocation when that session is safe.
- The supported worker set is Explorer, Investigator, Default Executor, Senior
  Executor, Tester, and Archivist. `plus` maps all six to the internal Codex
  lifecycle; `muse-max` maps all six to native Muse Code using Muse Spark 1.3
  Contributor with `max` reasoning. Main remains the user-selected Codex model.
- Explorer owns bounded read-only project-context discovery and mapping.
  Investigator owns bounded fault hypotheses, alternatives, feasibility, and
  prior-art research; qualifying Investigator problems use exactly three
  independent lanes and report directly to Main.
- Documentation intake is proportionate to the current task. Main expands reads
  only when needed and uses Explorer for bounded broader-context discovery; the
  workflow does not require a complete session-level `agent_docs/` intake.
- Main owns deployment updates to `project_progress.md`, `project_diary.md`,
  and `latest_session_work.md`. Archivist handles other assigned documentation
  and the read-only closing handoff.
- Heavy has no workflow-imposed aggregate worker limit for internal Codex roles.
  The workflow does not write a fixed `max_concurrent_threads_per_session`;
  available concurrency is left to the Codex platform/account. Muse-backed calls
  keep bounded per-turn adapter invocations and may use the managed batch helper
  only for already-authorized independent lanes with isolated workspaces.
- Under `plus`, running internal Codex workers may use `send_message` to
  `/root` only for rare material mid-task `BLOCKER`, `COURSE_CHANGE`, or
  `CRITICAL_PARTIAL` events. Routine progress and normal completion stay on the
  standard worker result path, and all material events route worker -> Main.
- No token-accounting skill, deployment counting marker, usage-report table, or
  reporting obligation is included.
- Release discovery and downloads are restricted to GitHub Releases published
  from `elmakus/codex_workflow`. There is no background/startup auto-update and
  no release channel from upstream.
- Installation, updates, and compute-profile changes happen only when the owner
  asks. Subscription type is never detected or inferred automatically.

## Workflow and roles

For substantive work Main enters deployment state and loads
`codex_workflow/heavy_route.md`. Main chooses only useful worker capabilities
and owns scope, architecture, scheduling, integration, acceptance, and final
claims. Use Explorer for bounded broader-context discovery, and load
`~/.codex/codex_workflow/delegation.md` when preparing or following up a worker
package or recovering a worker.

| Role | `plus` | `muse-max` | Responsibility |
| --- | --- | --- | --- |
| Explorer | Luna/max | Muse Contributor/max | Bounded read-only project-context discovery, mapping, and evidence retrieval. |
| Investigator | Luna/max | Muse Contributor/max | Bounded fault/solution/feasibility/prior-art research using the exact-three-lane contract when qualifying. |
| Default Executor | Luna/max | Muse Contributor/max | Normal bounded implementation and repair. |
| Senior Executor | Sol/medium | Muse Contributor/max | Exceptionally difficult bounded production or solution work. |
| Tester | Luna/max | Muse Contributor/max | Independent verification. |
| Archivist | Luna/max | Muse Contributor/max | Verified documentation outside Main-owned deployment-state docs and closing handoff. |

The active selection is stored in
`~/.codex/codex_workflow/settings.toml`. Missing settings on a pre-profile
installation mean `plus`. Profile switches rewrite the rendered Heavy
communication policy and settings in one compensating transaction. Under
`plus`, all six managed worker TOMLs are rendered for the internal Codex
allocation. Under `muse-max`, those TOMLs remain valid but dormant while all six
roles route through `runtime/muse_worker.py`. Updates preserve the selected
profile.

### Muse Max profile

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
  --session-id <logical-session-uuid> \
  --user-input-auto-resolve \
  --disable-sandbox
```

The adapter separates a stable logical Muse `session_id` from a unique
per-turn `invocation_id`. Session bindings are kept in a private bounded
`~/.codex/codex_workflow/muse_sessions/` registry and bind logical worker,
role, active allocation, canonical workspace, Task ID, and any opaque caller
scope. A process-safe per-session lease allows at most one active turn and
fail-closed resume first probes the exact retained Muse session. JSONL stdout
and diagnostic stderr are drained into private per-invocation artifacts under
`~/.codex/codex_workflow/muse_runs/`; exactly one terminal lifecycle record
plus the versioned final worker report is normalized for Main. Raw streams have
per-invocation size limits and retained artifacts are bounded by age, count, and
aggregate size.

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
| `codex_workflow --profile plus` | Route all six workflow workers through internal Codex; Luna Max except Senior on Sol Medium. |
| `codex_workflow --profile muse-max` | Keep Main unchanged and route all six workflow workers through Muse Spark 1.3 Contributor Max. |
| `codex_workflow --personal` | Change project workflow preferences. |
| `codex_workflow --disable` / `--enable` | Disable or enable the selected project. |
| `codex_workflow --remove` | Preview removal, then remove owned files after explicit confirmation; preserve project documents. |

For release preparation and provenance see [RELEASING.md](RELEASING.md).
For the ownership map and adapted orchestration analysis see [workflow_breakdown.md](workflow_breakdown.md).
The existing light benchmark is an initial case study; broader evaluation guidance lives in [benchmarks/README.md](benchmarks/README.md).
