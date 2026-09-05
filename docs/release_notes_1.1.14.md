# Private 1.1.14-private.1 preparation notes

Upstream base: experimental 1.1.14 commit
`a224f32c423ef56be322de160d5440bba0a786b2` (2026-09-05).
Previous private base: `898ee86a4b8fb80f4dbfe8780d2ea017db202d37`
(1.1.13-private.2).

## Retained upstream changes

- Batched independent work and on-demand Companion.
- Role-specific concise reports and main-owned acceptance decisions.
- Archivist replaces Doc-writer and Closure Steward, including in Medium.
- Main owns the project diary; Archivist owns assigned documentation and handoff.
- Lifecycle guides and version metadata move to `operate/` and the launcher to
  `runtime/workflow.py`. Project documents remain under `agent_docs/`.

## Private requirements

- Heavy is default; the direct path for questions and small tasks is retained.
- All five Luna roles use max; Senior Executor remains Sol medium.
- Token accounting, its skill and script, markers, and report tables are removed.
- No release checks, downloads, automatic updates or automatic publication.
  Manual migration uses an explicit verified local package.
- Installation is only on request. The previous private startup auto-install
  instruction is removed.
- Migration preserves unrelated content and supports bringing an older project
  wrapper up to the already-installed shared runtime version.

## Installation status

This change prepares source and an artifact. It does not install into projects
or replace the shared user runtime. Future owner-requested migrations use the
incoming launcher. One coordinated rollout will replace the shared user
runtime and migrate all existing project wrappers, calling the explicit
project target sequentially as needed. No partial adoption is planned.

## Verification evidence

Use the private artifact's accompanying provenance record for the exact source
commit, completed tests, archive checks, and checksum. Upstream's original
package-validation statements are not evidence for this modified package.
