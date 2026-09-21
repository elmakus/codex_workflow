<!-- codex-workflow-user-id: viettran-edgeAI/codex_workflow -->
<!-- codex-workflow-version: 1.1.18-private.4 -->
<!-- codex-workflow-user-managed-start -->
# AGENTS.md

When the user's trimmed message matches one of the following command forms,
read and follow the corresponding guide. Forms without placeholders must match
exactly.

When an enabled project is in `deployment state`, reread only
`~/.codex/codex_workflow/settings.toml` immediately before every worker
dispatch; never reuse a profile or harness remembered across turns or context
compaction. If it says `muse-max`, all six workflow roles must use
`runtime/muse_worker.py`; never use internal Codex multi-agent APIs even if a
stale long-lived session still exposes them.

- codex_workflow --install
  Guide:  ~/.codex/codex_workflow/operate/install.md.

- codex_workflow --update
  Guide:  ~/.codex/codex_workflow/operate/update.md.

- codex_workflow --check-update
  Guide:  ~/.codex/codex_workflow/operate/check_update.md.

- codex_workflow --remove
  Guide: ~/.codex/codex_workflow/operate/remove.md.

- codex_workflow --profile
  Guide: ~/.codex/codex_workflow/operate/profile.md.

- codex_workflow --profile plus
  Guide: ~/.codex/codex_workflow/operate/profile.md.


- codex_workflow --profile muse-max
  Guide: ~/.codex/codex_workflow/operate/profile.md.

- codex_workflow --personal
  Guide: ~/.codex/codex_workflow/operate/personalization_guide.md.

- codex_workflow --disable
  Guide: ~/.codex/codex_workflow/operate/disable.md.

- codex_workflow --enable
  Guide: ~/.codex/codex_workflow/operate/enable.md.
<!-- codex-workflow-user-managed-end -->
