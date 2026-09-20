# M01 integrated acceptance

Verdict: GREEN
Milestone: `M01 — project-only update and legacy-migration hardening`
Integrated review subject: commit `3f7aa3c67a564216a6095b5ad92a3db2589ef8a1`
Reviewed tree: `84bb2d5d75c2672cda885805f4d5944928a5593f`

## Authority

- `planning/MASTER_PLAN.md#M01--project-only-update-and-legacy-migration-hardening`
- `requirements/REQUIREMENTS.md`: REQ-001, REQ-002, REQ-003, REQ-004, REQ-016, REQ-021
- `decisions/DEC-004-selective-upstream-adoption.md`
- `openspec/changes/m01-project-only-update/`
- `openspec/changes/m01-legacy-local-instructions/`
- Card contracts/evidence/reviews for `M01-T01` and `M01-T02`

## Integrated findings

No blocking findings.

The final M01 subject satisfies the approved milestone acceptance surface:
- equal-version release selection reuses installed verified source without reacquiring/replacing shared runtime state;
- older projects resolve through recorded historical source, while missing/mismatched history and unintended downgrade remain fail-closed;
- project-only mutation/backup scope is limited to changed target-project files and already-current/no-entry cases produce no project mutation or unnecessary backup;
- stale removed workflow-route references in selected project-local instructions fail closed;
- explicitly reviewed local instructions are supported consistently across bootstrap, install and update, including delegated and project-only update paths;
- user-owned local content, workflow-managed/personalization boundaries, transaction safety and reserved-marker protections remain enforced;
- the implementation is selective semantic adoption and does not wholesale merge/cherry-pick upstream;
- release-triggering VERSION metadata remains unchanged.

Both required Card reviews are GREEN on immutable subjects. The final integrated M01 subject contains the already-reviewed T01 behavior plus the reviewed T02 behavior.

## Verification

GitHub Actions PR #7 run #67 (`35484711064`) completed successfully on PR merge commit `bb3f20c0e60c37871af8694d5dbfdca134df0a7f`. Its tree `84bb2d5d75c2672cda885805f4d5944928a5593f` is identical to the integrated M01 review-subject tree.

Observed integrated verification:
- runtime regression suite: 97/97 GREEN, including equal-version project-only, historical-source, multi-project, downgrade and stale-route migration coverage;
- Muse adapter suite: 33/33 GREEN;
- Muse Max profile suite: 7/7 GREEN;
- Python compile, package validation, package build and archive verification: GREEN;
- `codex_workflow/operate/VERSION` remains `1.1.17-private.12`.

No deployment, release publication or VERSION-triggered publication action occurred.

## Result

GREEN — M01 meets its approved integrated milestone contract and is eligible for checkpoint closure on the workstream branch.
