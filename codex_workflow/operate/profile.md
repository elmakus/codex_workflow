# Compute Profile

Use this procedure only when the user's trimmed message is exactly one of:

    codex_workflow --profile
    codex_workflow --profile plus
    codex_workflow --profile luna-xhigh
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

For `plus`, `luna-xhigh`, or `pro-x5`, run exactly one complete profile
transaction:

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

Micro's optional GPT-5.3-Codex-Spark / high override remains an acceleration path
for `plus` and `pro-x5` when the current runtime exposes and accepts model
overrides. In `luna-xhigh`, do not use the Spark override: Micro follows the
installed GPT-5.6 Luna / xhigh profile so every non-Senior workflow worker uses
Luna / xhigh.

Profile state is global to this Codex home and is preserved by workflow updates.
A pre-profile installation with no settings file is interpreted as `plus`, and
the next bootstrap/update/profile operation materializes that default explicitly.
