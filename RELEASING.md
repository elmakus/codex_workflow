# Release Process

This private downstream builds a local workflow artifact and matching checksum
from a reviewed, pushed private commit. It does not publish GitHub Releases or
use a public release channel. The package payload remains independent of
repository presentation and development files.

## Repository and asset layout

The repository-only packaging machinery used by this downstream is:

```text
scripts/package_release.py
RELEASING.md
```

The inherited `.github/workflows/release.yml` remains untouched but is not used
for private delivery.

Every archive contains exactly this top-level directory and nothing beside it:

```text
codex_workflow/
├── VERSION
├── user_AGENTS.md
├── AGENTS.md
├── bootstrap.md
├── install.md
├── update.md
├── remove.md
├── workflow.py
├── runtime/
├── resources/                              # immutable package defaults
├── agents/
└── project_docs/
```

The package does not contain `README.md`, `illustration.png`,
`workflow_break_down.md`, `RELEASING.md`, `.github/`, `scripts/`, `.git/`, or any
other repository-only file. All files below `codex_workflow/` are included so
the installed workflow remains self-contained.

Each private build produces one universal asset for every supported operating
system:

- `codex_workflow-<version>.zip`;
- `SHA256SUMS` for the ZIP asset.

## Versioning

Use SemVer 2.0.0. Keep the plain version in `codex_workflow/VERSION` and the
`codex-workflow-version` marker in `codex_workflow/user_AGENTS.md` identical.
The current private version is `1.1.13-private.2`. A later private build may
increment the suffix to `1.1.13-private.3`, then `.4`, as needed. No release tag
or new versioning framework is required.

## Local build and validation

First commit and push the reviewed private changes. Create a clean checkout of
that pushed commit, confirm its commit ID, and run these commands there with a
fresh, empty output directory. The builder uses only Python's standard library,
requires Python 3.11 or newer, and works on Linux, macOS, and Windows.

Linux/macOS:

```sh
private_output_dir="/absolute/path/to/fresh-empty-output"
python3 -B scripts/test_workflow_runtime.py -v
python3 -B scripts/test_deployment_token_report.py -v
python3 scripts/package_release.py --output-dir "$private_output_dir"
python3 scripts/package_release.py --verify "$private_output_dir/codex_workflow-1.1.13-private.2.zip"
```

Windows PowerShell:

```powershell
$PrivateOutputDir = "C:\absolute\path\to\fresh-empty-output"
py -3.11 -B scripts\test_workflow_runtime.py -v
py -3.11 -B scripts\test_deployment_token_report.py -v
py -3.11 scripts\package_release.py --output-dir $PrivateOutputDir
py -3.11 scripts\package_release.py --verify "$PrivateOutputDir\codex_workflow-1.1.13-private.2.zip"
```

The build validates the version, marker, lifecycle runtime, and required
resources; rejects generated Python caches; creates a deterministic ZIP asset;
and writes `SHA256SUMS` beside the ZIP. Run the runtime tests before packaging,
inspect the archive listing when package contents change, and record the clean
commit ID and ZIP checksum. Never use the upstream-tracked
`dist/codex_workflow-1.1.11.zip` as the private installation artifact.

## Private artifact handoff

The tested clean private commit, its freshly built ZIP, and `SHA256SUMS` are
sufficient. Do not create or push a release tag or publish a GitHub Release for
this artifact.

Private installation and update use the local verified package root. They do
not require a downloader, GitHub authentication, keyring integration, or a
custom release service.

## Consumer commands

- Initial installation reads the extracted release package's
  `codex_workflow/bootstrap.md`; the bundled lifecycle CLI validates and
  applies the user-level bootstrap transaction directly.
- `codex_workflow --install` reads the installed `install.md` and creates only
  project-level workflow assets from the existing bootstrap.
- `codex_workflow --check-update` reports the installed private version and that
  public release comparison is disabled.
- `codex_workflow --update` requires an explicit verified private/local
  `--source`; without one it fails closed before any public release lookup.
- `codex_workflow --remove` first displays a destructive dry-run summary and
  requires one explicit second confirmation before deleting workflow-owned
  files.
