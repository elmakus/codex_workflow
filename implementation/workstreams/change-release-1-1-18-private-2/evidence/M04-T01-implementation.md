# M04-T01 implementation evidence — 1.1.18-private.2

Status: implementation complete; independent review pending.

## Exact implementation subject

- Branch: `work/release-1-1-18-private-2`
- Subject: `8336e6efe68dd12de8836e5e36ef667594d48754`
- PR: #11
- Base: `760a595125335411288cf3a673356ccdd8ea47af`

## Scope implemented

Release metadata is synchronized to `1.1.18-private.2` in:
- `codex_workflow/operate/VERSION`
- managed version marker in `codex_workflow/operate/user_AGENTS.md`
- current-version text in `README.md`
- release procedure/examples/assets in `RELEASING.md`

The only additional source change is the version-specific regression expectation in
`scripts/test_workflow_runtime.py`, advanced from current `.1` / next `.2` to current
`.2` / next `.3`. No runtime behavior code changed.

## Verification

GitHub Actions PR Tests run #240 / `35514056242` is GREEN on the exact subject:
- runtime regression tests GREEN;
- Muse adapter regression tests GREEN;
- Python compile check GREEN;
- Muse Max profile regression tests GREEN;
- package validation GREEN;
- package build GREEN;
- release archive verify GREEN.

The first PR run #237 failed because two regression expectations still hard-coded
`1.1.18-private.1`; the test-only correction above resolved that stale release-version
expectation without changing runtime behavior.

Independent disposable exact-subject package verification:
- package validate GREEN;
- built `codex_workflow-1.1.18-private.2.zip` and `SHA256SUMS`;
- archive verify GREEN;
- `sha256sum -c SHA256SUMS` => `codex_workflow-1.1.18-private.2.zip: OK`;
- `git diff --check` GREEN;
- bounded readback confirms VERSION/user_AGENTS/README/RELEASING current-version metadata is synchronized.

## Boundary

No tag/release has been published yet. No production Workstation update or persistent Muse
state mutation occurred. Merge remains gated by independent review and final integration
handling.
