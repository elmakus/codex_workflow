# Compute Profile

Use this procedure only when the user's trimmed message is exactly one of:

    codex_workflow --profile
    codex_workflow --profile plus
    codex_workflow --profile pro-x5

Compute profile is user-runtime state, not project personalization. It applies to
workflow-owned worker TOMLs under `~/.codex/agents/` and does not change the Main
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

Report the active profile and its worker model/reasoning mapping. Do not mutate
anything.

## Switch profile

For `plus` or `pro-x5`, run exactly one complete profile transaction:

```text
python3 ~/.codex/codex_workflow/runtime/workflow.py profile <profile> --json
```

The CLI validates the installed workflow, all managed worker templates and the
requested profile before applying changes. The worker files and persistent
`~/.codex/codex_workflow/settings.toml` selection are changed in one compensating
transaction, so a failure must not leave a partial profile switch.

The profiles are:

- `plus`: preserves the historical worker allocation. Micro fallback is GPT-5.6
  Luna / high; Default, Tester, Companion, Investigator and Archivist use GPT-5.6
  Luna / max; Senior uses GPT-5.6 Sol / medium.
- `pro-x5`: Micro fallback, Default, Tester, Companion, Investigator and Archivist
  use GPT-5.6 Sol / low; Senior stays GPT-5.6 Sol / medium.

Micro's optional GPT-5.3-Codex-Spark / high override remains an acceleration path
when the current runtime exposes and accepts model overrides. The selected
compute profile controls the installed stable fallback.

Profile state is global to this Codex home and is preserved by workflow updates.
A pre-profile installation with no settings file is interpreted as `plus`, and
the next bootstrap/update/profile operation materializes that default explicitly.
