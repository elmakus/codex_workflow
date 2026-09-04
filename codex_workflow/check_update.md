# Check for Updates

Run the installed lifecycle CLI:

```text
python3 ~/.codex/codex_workflow/workflow.py check-update --json
```

Treat this as an explicit, read-only check regardless of the automatic
update-check setting. Expect it to report the installed private version and that
public release comparison is disabled. It must not query, recommend, download,
or install a public release. Keep workflow files unchanged.

To update, obtain an approved, reviewed private package and matching checksum,
then follow `update.md` with an explicit verified private/local `--source`.
