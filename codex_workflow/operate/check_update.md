# Check for Updates

Run the installed lifecycle CLI:

```text
python3 ~/.codex/codex_workflow/runtime/workflow.py check-update --json
```

This is an explicit, read-only network check. It queries GitHub Releases only
for `elmakus/codex_workflow`, considers non-draft SemVer releases that contain
both the versioned `codex_workflow-<version>.zip` asset and `SHA256SUMS`, and
reports every version newer than the installed runtime. Prereleases are valid
because the private version line uses SemVer prerelease identifiers.

The check does not modify workflow files, projects, or Git state. No background
or startup update check is implied.

If an update is available, review the reported summaries and then send
`codex_workflow --update` when you are ready to install the latest owner release.
