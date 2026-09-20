# M04 acceptance — release 1.1.18-private.2

Status: GREEN for release readiness, final integration, publication and post-merge readback.

## Accepted subject and integration result

- Reviewed implementation/content subject: `8336e6efe68dd12de8836e5e36ef667594d48754`.
- Final source package head merged by PR #11: `67e82a4d26258dfd779f61a209344268143ef0d8`.
- Integration target: `main`.
- Target baseline used by implementation/review refresh: `760a595125335411288cf3a673356ccdd8ea47af`.
- Final integration result: `72f821dbc3afb7a6d580bf3fe6661bc88985149c`.

## Acceptance

The release-preparation outcome satisfies the M04 release-readiness contract and the M04-T01 Card authority.

- User release-publication authorization is durably satisfied by this workstream Intake.
- The private release is exactly `1.1.18-private.2` under DEC-005.
- VERSION, user_AGENTS version marker, README current version, and RELEASING current version are synchronized.
- Historical selective-alignment/source provenance remains truthful.
- No runtime implementation behavior changed in the reviewed release subject.
- M04-T01 is terminal with independent GREEN review on `8336e6efe68dd12de8836e5e36ef667594d48754`.
- Final-integration review is GREEN by exact coverage reuse from that independent Card review; all commits after the reviewed subject and before merge are namespaced workflow state/evidence only.
- Closure-ready head CI Tests run #253 / `35514700936` is GREEN.

## Merge, publication and readback

PR #11 merged into `main` as `72f821dbc3afb7a6d580bf3fe6661bc88985149c`. Immutable merge evidence confirms the merge commit has parents `main@760a595125335411288cf3a673356ccdd8ea47af` and source head `67e82a4d26258dfd779f61a209344268143ef0d8`.

Post-merge GitHub Actions on that exact result are GREEN:
- Release run #12 / `35514755577`: completed success.
- Tests run #254 / `35514755611`: completed success.

Published release readback is GREEN:
- tag `v1.1.18-private.2` points exactly to `72f821dbc3afb7a6d580bf3fe6661bc88985149c`;
- GitHub Release id `392448028` is non-draft and prerelease;
- release target is exactly `72f821dbc3afb7a6d580bf3fe6661bc88985149c`;
- assets are exactly `codex_workflow-1.1.18-private.2.zip` and `SHA256SUMS`;
- ZIP digest reported by GitHub and the successful release verification is `sha256:e5b4d108d83ce00a85e224bfa3269bc57a1a7045afd2ecb3e76661cd51b27486`;
- Release workflow verification includes package validation, archive verification and `sha256sum -c SHA256SUMS`.

Target-side readback confirms the namespaced workstream package survived the merge. GitHub removed the source branch automatically; the fallback `branch_cleanup` lifecycle remains inactive and the original branch identity stays as provenance.

Production Workstation deployment was not performed and remains a separate live-write authorization gate.

## Result

M04 final integration/publication/readback: GREEN.

The workstream is eligible for terminal target-side Task Board and manifest reconciliation with result `72f821dbc3afb7a6d580bf3fe6661bc88985149c`.
