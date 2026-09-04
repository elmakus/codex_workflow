<!-- codex-workflow-user-id: viettran-edgeAI/codex_workflow -->
<!-- codex-workflow-version: 1.1.13-private.1 -->
<!-- codex-workflow-user-managed-start -->
# AGENTS.md

When the user's trimmed message matches one of the following command forms,
read and follow the corresponding guide. Forms without placeholders must match
exactly.

- codex_workflow --install
  Guide:  ~/.codex/codex_workflow/install.md.

- codex_workflow --update
  Guide:  ~/.codex/codex_workflow/update.md.

- codex_workflow --check-update
  Guide:  ~/.codex/codex_workflow/check_update.md.

- codex_workflow --remove
  Guide: ~/.codex/codex_workflow/remove.md.

- codex_workflow --personal
  Guide: ~/.codex/codex_workflow/personalization_guide.md.

- codex_workflow --disable
  Guide: ~/.codex/codex_workflow/disable.md.

- codex_workflow --enable
  Guide: ~/.codex/codex_workflow/enable.md.

At the start of the first substantive turn in a new session, resolve only the
Git root containing the opened working directory. If the directory is not in a
Git project, do nothing. If codex_workflow is absent from that root, follow
`~/.codex/codex_workflow/install.md` to install it there before substantive
work, preserve any existing project AGENTS instructions through the normal
importer, and complete the installer's required doc-writer action. Then stop
without continuing the original task and tell the user to open a fresh session.
Never scan or install into child repositories recursively.
<!-- codex-workflow-user-managed-end -->
