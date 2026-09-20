# M01-T01 independent review evidence

Status: GREEN
Review subject: commit `a3f848ede935a8dc39e22eecbd8255dfee262c05`
Reviewed tree: `f06e75e4a6caedd536bdd61b415010dcd6efcea3`

## Authority reviewed

- `implementation/workstreams/upstream-1-1-18-alignment/cards/M01-T01.md`
- `planning/MASTER_PLAN.md` R2 / M01
- `requirements/REQUIREMENTS.md`: REQ-001, REQ-002, REQ-003, REQ-004, REQ-021
- `decisions/DEC-004-selective-upstream-adoption.md`
- `research/upstream-1.1.18-audit.md`
- `openspec/changes/m01-project-only-update/`

## Subject inspection

The exact parent-to-subject change is one commit and is bounded to:
- `codex_workflow/runtime/backup.py`
- `codex_workflow/runtime/lifecycle.py`
- `codex_workflow/runtime/workflow.py`
- the M01 project-only OpenSpec task state
- focused runtime/owner regression tests.

The review subject leaves `codex_workflow/operate/VERSION` unchanged at `1.1.17-private.12`.

The implementation satisfies the required boundaries:
- release-selected equal-version update reuses installed verified source and does not acquire/download the same release;
- equal-version execution uses `plan_project_only_update`, not full shared-runtime update planning;
- project-only mutations are produced from the recorded historical project source versus the installed target source;
- unchanged mutations are removed before apply;
- backup mutations are limited to existing target-project files that will actually change/delete;
- an already-current project has no mutations and no backup;
- a project with no workflow entry point performs no mutation;
- a project newer than the target remains blocked unless explicit downgrade approval is present;
- missing/mismatched historical source continues to fail closed;
- the project-only plan does not mutate shared runtime/workers/config/install state;
- the existing transaction layer still provides duplicate-target checks, symlink/non-regular-target rejection, atomic writes, post-write verification, and rollback on failure.

No wholesale upstream merge/cherry-pick, legacy-route hardening, worker/profile change, VERSION bump, or publication change is present in the subject.

## Verification evidence

Implementation evidence at `implementation/workstreams/upstream-1-1-18-alignment/evidence/M01-T01.md` records:
- focused project-only/historical-source/downgrade regressions: 6/6 GREEN;
- fork runtime suite: 94/94 GREEN;
- `git show --check`: clean;
- VERSION unchanged;
- tested tree `f06e75e4a6caedd536bdd61b415010dcd6efcea3` exactly equals the immutable review-subject tree.

GitHub has no CI/status run attached to this exact commit, so this independent review does not claim a second CI execution. The verdict is based on independent inspection of the exact immutable subject and its governing source/transaction paths, with the existing test evidence accepted only because it is pinned to the identical reviewed tree.

## Verdict

GREEN — no material correctness, data-integrity, scope, authority, or acceptance defect found in M01-T01.
