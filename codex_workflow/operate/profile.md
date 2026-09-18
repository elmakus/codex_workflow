# Compute Profile

Use this procedure only when the user's trimmed message is exactly one of:

    codex_workflow --profile
    codex_workflow --profile plus
    codex_workflow --profile luna-xhigh
    codex_workflow --profile pro-x5
    codex_workflow --profile muse-max

Compute profile is user-runtime state, not project personalization. It applies to
workflow-owned worker routing under `~/.codex/` and does not change the Main
agent selected by the user or Codex runtime.

Do not infer the user's ChatGPT/Codex subscription and do not switch profiles
automatically. The user explicitly chooses the profile.

## Show the current profile

For:

```text
codex_workflow --profile
```

run:

```text
python3 ~/.codex/codex_workflow/runtime/workflow.py profile --json
```

Report the active profile and its worker model/reasoning/harness mapping. Do not
mutate anything.

## Switch profile

For `plus`, `luna-xhigh`, `pro-x5`, or `muse-max`, run exactly one complete
profile transaction:

```text
python3 ~/.codex/codex_workflow/runtime/workflow.py profile <profile> --json
```

The CLI validates the installed workflow, all managed worker templates, the
Heavy communication section, and the requested profile before applying changes.
The worker files, rendered Heavy communication policy, and persistent
`~/.codex/codex_workflow/settings.toml` selection are changed in one compensating
transaction, so a failure must not leave a partial profile switch.

The profiles are:

- `plus`: preserves the historical worker allocation. Micro fallback is GPT-5.6
  Luna / high; Default, Tester, Companion, Investigator and Archivist use GPT-5.6
  Luna / max; Senior uses GPT-5.6 Sol / medium. User-visible communication is
  restrained to meaningful milestones and avoids routine orchestration chatter.
- `luna-xhigh`: Micro, Default, Tester, Companion, Investigator and Archivist use
  GPT-5.6 Luna / xhigh; Senior stays GPT-5.6 Sol / medium. Orchestration remains
  strictly silent except for blockers, required approvals, or requested updates.
- `pro-x5`: Micro fallback, Default, Tester, Companion, Investigator and Archivist
  use GPT-5.6 Sol / low; Senior stays GPT-5.6 Sol / medium. Main may use normal
  concise progress and skill announcements without internal meta-reasoning.
- `muse-max`: mixed-harness profile. Main remains the user-selected Codex
  model. Companion remains one persistent internal Codex worker on GPT-5.6 Luna
  XHigh. Micro, Default, Senior, Tester, Investigator and Archivist are routed
  through the native Muse Code harness using `muse-spark-1.3-contributor` with
  `max` reasoning. User-visible orchestration uses normal concise milestone
  updates rather than silent orchestration. Muse-backed roles are bounded
  one-shot invocations; later milestones own managed lane concurrency.

`muse-max` requires the `muse` CLI on `PATH`, a completed `muse login`, and access
to Muse Spark 1.3 Contributor Max. The profile switch itself does not install or
authenticate Muse. Before the first production worker, a smoke test may invoke:

```text
python3 ~/.codex/codex_workflow/runtime/muse_worker.py \
  --role investigator \
  --workspace <project-root> \
  --task-file <capsule-file> \
  --dry-run
```

Micro's optional GPT-5.3-Codex-Spark / high override remains an acceleration path
for `plus` and `pro-x5` when the current runtime exposes and accepts model
overrides. In `luna-xhigh`, do not use the Spark override: Micro follows the
installed Luna XHigh worker. In `muse-max`, do not use the Codex Spark override:
Micro is one of the six roles using Muse Spark 1.3 Contributor Max through Muse Code.

Profile state is global to this Codex home and is preserved by workflow updates.
A pre-profile installation with no settings file is interpreted as `plus`, and
the next bootstrap/update/profile operation materializes that default explicitly.
