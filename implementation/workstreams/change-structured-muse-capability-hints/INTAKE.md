# Intake — Structured Muse capability hints

- Workstream ID: `change-structured-muse-capability-hints`
- Kind: `change`
- Status: `complete`
- Branch: `work/structured-muse-capability-hints`
- Integration target: `main`

## Authorized subject

Implement the accepted cross-repository milestone `MCA-P1 M02 — Structured Muse capability hints in codex_workflow`.

The durable source of product/system and plan authority is the immutable `elmakus/muse-capability-admin@8aecaa42d0ffd40efa2342b5bbace85fcc976d7e` package, not the initiating chat.

## Accepted authority

- Requirements: `requirements/MUSE_CAPABILITY_ADMIN.md`, especially MCA-REQ-004, 005, 006, 007, 008, 009 and 017.
- Decision: `MCA-DEC-001-STRUCTURED_CAPABILITY_HINTS.md`.
- Boundary decision: `MCA-DEC-002-ADMIN_AUTH_AND_SECRET_REUSE.md`.
- Approved milestone: `planning/MASTER_PLAN.md#M02`.

All refs above are at `elmakus/muse-capability-admin@8aecaa42d0ffd40efa2342b5bbace85fcc976d7e`.

## Pre-creation discovery and dependency classification

- Current `elmakus/codex_workflow/main` baseline at intake creation: `738ac89eeaa0522348f175eb5e936bda02a3de8c`.
- No existing branch or code/workstream locator matching this M02 subject was found.
- The accepted M02 plan explicitly depends only on Definition authority; it does not depend on M01 or on any unmerged codex_workflow branch.
- Existing historical implementation branches are therefore not valid parent-only dependencies.

Classification: **independent**.

Selected base: `main@738ac89eeaa0522348f175eb5e936bda02a3de8c`.

## Scope boundaries

Included:
- immutable structured Muse capability-hint value attached to `MuseWorkerInvocation`;
- four v1 categories: required skills, relevant skills, required capabilities, suggested capabilities;
- equivalent normal CLI inputs and centralized normalization;
- bounded opaque-ID validation, stable de-duplication and required-over-advisory precedence within skill/capability namespaces;
- deterministic prompt rendering for every invocation, including an explicit empty current set and explicit supersession of prior-turn hints;
- Main-side Muse delegation guidance;
- tests covering direct/concurrent/initial/resume/empty/conflict/required-vs-advisory/regression semantics.

Excluded:
- capability installation/configuration/removal;
- capability discovery/global registry;
- secret access/storage;
- changes to workstation-owned Muse installation/home/auth substrate;
- implicit mutation triggered by a missing required capability.

## Downstream classification

The strategic Definition and milestone plan are already accepted and immutable for this work package. No new product/architecture decision is required and no Research dependency blocks the generic hint transport.

Path: `execution_prep:MCA-P1-M02`.

Execution Prep materialized:
- Task Board: `implementation/workstreams/change-structured-muse-capability-hints/TASK_BOARD.yaml`
- Card: `implementation/workstreams/change-structured-muse-capability-hints/cards/M02-T01.md`
- OpenSpec: required JIT at `openspec/changes/m02-muse-capability-hints/`

The workstream is now recoverable without chat history. Router continuation: execute the READY Card.
