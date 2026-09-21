# M06 release acceptance — 1.1.18-private.4

Status: GREEN through the pre-publication boundary; terminal publication readback pending.

## Accepted release subject

- Reviewed implementation subject: `232072b87524b2d1398af5b12b70c6a96e8a5ded`
- Integration target: `main`
- Target/base at final refresh: `016a42ba0cf0d274bf12d718db6d7580abe54658`
- PR: #19

## Pre-publication acceptance

GREEN:
- synchronized current version is `1.1.18-private.4`;
- next private-version regression expectation is `1.1.18-private.5`;
- selective-upstream provenance remains truthful;
- base-to-reviewed-subject scope contains no runtime/profile/Muse behavior implementation change;
- required runtime/Muse/package/diff/readback verification is GREEN;
- independent M06-R01 review is GREEN;
- final-target refresh is GREEN with no target drift;
- manifest final-integration review coverage is satisfied by the exact independent Card review;
- tag and GitHub Release `v1.1.18-private.4` were absent before publication;
- explicit release publication authorization is durable in this workstream Intake.

## Publication gate

Merge of PR #19 to `main` is the authorized write that triggers the normal Release workflow. Terminal acceptance requires post-write readback proving:
- the final merge result is the release target;
- Release and affected push Tests are GREEN;
- tag/release `v1.1.18-private.4` exists as a non-draft prerelease;
- assets are exactly `codex_workflow-1.1.18-private.4.zip` and `SHA256SUMS`.

Production Workstation installation/update is outside this workstream.
