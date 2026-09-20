# Compute Profile

Use this procedure only when the user's trimmed message is exactly one of:

    codex_workflow --profile
    codex_workflow --profile plus
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

For `plus` or `muse-max`, run exactly one complete profile transaction:

```text
python3 ~/.codex/codex_workflow/runtime/workflow.py profile <profile> --json
```

The CLI validates the installed workflow, all managed worker templates, the
Heavy communication section, and the requested profile before applying changes.
The worker files, rendered Heavy communication policy, and persistent
`~/.codex/codex_workflow/settings.toml` selection are changed in one compensating
transaction, so a failure must not leave a partial profile switch.

The profiles are:

- `plus`: all six supported roles — Explorer, Investigator, Default Executor,
  Senior Executor, Tester and Archivist — use the internal Codex worker
  lifecycle. Explorer, Investigator, Default Executor, Tester and Archivist use
  GPT-5.6 Luna / max; Senior uses GPT-5.6 Sol / medium. User-visible
  orchestration is restrained to meaningful milestones and avoids routine
  orchestration chatter.
- `muse-max`: all six supported roles run through the native Muse Code harness
  using `muse-spark-1.3-contributor` with `max` reasoning. Main remains the
  user-selected Codex model. Muse-backed roles use stable bound logical
  sessions with bounded per-turn invocations; the caller owns lane and
  higher-level workflow policy.

`muse-max` also disables the workflow-owned internal Codex multi-agent
surface as a fail-closed routing guard; `plus` enables it. A long-lived session
may still display a stale internal-agent surface after a profile/workflow change,
but the always-injected dispatch invariant forbids using that stale surface under
`muse-max`.

`muse-max` requires the `muse` CLI on `PATH`, a completed `muse login`, and
access to Muse Spark 1.3 Contributor Max. The profile switch itself does not
install or authenticate Muse. Before the first production worker, a smoke test
may invoke:

```text
python3 ~/.codex/codex_workflow/runtime/muse_worker.py \
  --role investigator \
  --workspace <project-root> \
  --task-file <capsule-file> \
  --dry-run
```

Profile state is global to this Codex home and is preserved by workflow updates.
A pre-profile installation with no settings file is interpreted as `plus`, and
the next bootstrap/update/profile operation materializes that default explicitly.
