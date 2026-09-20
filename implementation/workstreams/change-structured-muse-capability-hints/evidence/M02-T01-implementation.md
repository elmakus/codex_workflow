# M02-T01 implementation evidence — structured Muse capability hints

Status: implementation complete; pending independent review.

## Exact implementation subject

- Review subject: `c8fc2d2c60a395bc20562d3f81efc844ee9a7405`
- Pull request: #10
- Base at implementation intake: `main@738ac89eeaa0522348f175eb5e936bda02a3de8c`
- OpenSpec: `openspec/changes/m02-muse-capability-hints/` with all implementation tasks checked on the review subject.

The later workflow-state commit that records this evidence and `review_state: pending` is not part of the reviewed implementation subject.

## Implemented behavior

- Added frozen `MuseCapabilityHints` with required/relevant skills and required/suggested capabilities.
- Added one normalization boundary with bounded opaque-ID validation, stable de-duplication, and required-over-advisory precedence within each namespace.
- Added structured hints to `MuseWorkerInvocation`, direct execution, concurrent forwarding and dry-run output.
- Added repeatable CLI flags `--required-skill`, `--relevant-skill`, `--required-capability`, and `--suggested-capability`.
- Every Muse prompt now renders one deterministic current-invocation hint block, including explicit empty categories, and states that current hints supersede prior-turn hints on resume.
- Required unavailability is fail-visible; relevant/suggested unavailability is advisory and non-blocking.
- The prompt and delegation contract explicitly deny install/configure/authenticate/update/remove authority from hints.
- Main-side delegation guidance documents the separate Muse capability plane.
- Executor/Tester logical-session isolation is preserved while allowing the same domain hint to be supplied to both.

## Verification

Exact-subject GitHub Actions `Tests` run #222 / run id `35511607347` on `c8fc2d2c60a395bc20562d3f81efc844ee9a7405`: **GREEN**.

- Runtime regression tests: **97/97 GREEN**.
- Muse adapter tests: **39/39 GREEN**, including new normalization, invalid-ID, CLI parity, prompt, concurrent-forwarding and resume-empty replacement coverage.
- Python compile check: **GREEN**.
- Muse Max profile regressions: **7/7 GREEN**.
- Package validation: **GREEN**.
- Package build: **GREEN**.
- Package archive verification: **GREEN**.
- Pull-request diff scan: 690 added lines inspected, **0 trailing-whitespace findings**, **0 conflict markers**.
- Target comparison at verification: branch ahead of `main` by 6 commits, behind by 0.
- `codex_workflow/operate/VERSION`: **unchanged**.

An earlier PR run #220 failed before adapter execution because two pre-existing source lines were accidentally concatenated while composing a large remote edit from line chunks. Commit `e20ff2429a2791c7756ccae588b293cda1edf1e0` repaired only those transport-induced line-boundary defects. Subsequent full runs #221 and exact-subject #222 are GREEN.

## Boundary verification

No capability installation/configuration/authentication/update/removal path was added. No secret storage/read path, capability registry/catalog, alias resolver, workstation Muse substrate change, VERSION bump, release/tag or deployment was introduced.

## Review boundary

Card review requirement is `RECOMMENDED`. The implementing chat did not issue a verdict. Review must inspect the exact immutable subject above using this evidence plus the Card authority slice.
