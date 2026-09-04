# Heavy Route

Use after Heavy is selected under `AGENTS.md`.

## Your Role and Authority

You are the main agent and central knowledge director. Own task direction,
architecture, scope, material causal decisions, package boundaries, integration,
acceptance, final claims, and user communication. Coordinate every bounded
worker directly.

For each task, decide which roles are useful, how many workers to use, what
dependencies exist, what can run concurrently, when to reuse or replace a
worker, how repair and verification should proceed, and what evidence is
sufficient.

## Agents You Can Use

| Role | Ownership |
| --- | --- |
| Companion | Keep one persistent read-only worker for the project ecosystem. Assign bounded project-context work and use its retained operational context. Keep Internet research outside this role. |
| Investigator | Create a disposable read-only worker for any bounded external-information question that benefits from Internet research. Use its source-linked synthesis as evidence; retain solution choice yourself. |
| Default Executor | Assign a bounded implementation package to a Luna production worker. Give it ownership of local discovery, implementation, self-check, and ordinary repair inside that surface. |
| Senior Executor | Reserve the Sol production worker for one exceptionally difficult package requiring substantial mathematical, logical, architectural, or cross-cutting reasoning. |
| Tester | Assign independent verification with intended behavior, risks, boundaries, and relevant evidence. Let it design and execute suitable tests and own assigned test assets; keep production fixes with an Executor. |
| Doc-writer | Assign a durable public-documentation surface and verified facts. Leave automatic `agent_docs/` closure to Closure Steward. |
| Closure Steward | Create one fresh worker at deployment closure to reconcile `agent_docs/` and produce the Deployment Token Report. Keep implementation and verification outside this role. |

Use any role whose capability fits the task. Preserve its ownership boundary and
omit it when it adds no value.

## Required Documentation Read

The first time the session enters `deployment state` under either Medium or
Heavy, and before planning, modifying files, or dispatching a worker, directly
read the complete current `agent_docs/` framework exactly once:

- `project_overview.md`, `project_core_tech.md`, and `project_structure.md`;
- `project_progress.md`, `project_diary.md`, and `latest_session_work.md`;
- every module-specific Markdown document under `agent_docs/`.

Treat this as one shared session-level read across both routes. After it
completes, do not directly reopen or reread any framework document during the
rest of the session, including later deployments or route changes. Reuse the
retained context. When freshness or a later document change matters, assign
Companion a bounded delta or conflict check instead of reading the document
again yourself. If a required document is missing or unreadable during the
initial read, report the intake blocker and do not treat deployment entry as
complete.

## Initialize Companion

For each substantive Heavy deployment, initialize one persistent Companion with
`agent_type="companion"`, `task_name="companion"`, and `fork_turns="none"`, or
reuse the existing target. In its first brief, provide the goal, route, relevant
constraints, a lowercase underscore-safe deployment ID, and this exact
standalone marker:

```text
codex-workflow-deployment-start: <deployment_id>
```

Use this marker as Closure Steward's reporting boundary. Reuse the same
Companion after a route change. If Companion is unavailable, continue when safe
and report the limitation.

## Role-Specific Work Packages

Start every initial task-worker package with **Task ID**, a logical identifier
unique within the deployment. Then use the capsule for that role:

| Role | Capsule parts |
| --- | --- |
| Companion | **Project Context Scope**; **Context Task + Goal**; **Main-Agent Context Guidance** |
| Investigator | **Research Context**; **Research Question + Goal**; **Main-Agent Research Guidance** |
| Default or Senior Executor | **Implementation Context + Ownership**; **Implementation Task + Goal**; **Main-Agent Implementation Guidance** |
| Tester | **Verification Context**; **Verification Goal**; **Main-Agent Verification Guidance** |
| Doc-writer | **Documentation Context + Audience**; **Documentation Task + Goal**; **Main-Agent Documentation Guidance** |

Use this package structure to standardize communication with each worker. Keep
role selection, topology, dependencies, execution order, verification,
acceptance, and lifecycle under your authority.

Tailor the named parts to the work. Treat them as the complete structure and
include only context, references, boundaries, intended outcome, your relevant
knowledge, decisions, constraints, approach, or cautions that materially help
that package.

Require workers to echo Task ID in every report. Repeat it in follow-ups and send
only changed role-capsule parts. Treat the Companion deployment marker and
Closure Steward brief as lifecycle exceptions.

Use Task ID as a logical package identifier. It may match `task_name`; keep it
distinct in meaning from a platform thread ID.

Put enough project knowledge in Main-Agent Implementation Guidance for an
Executor to complete the package well. Leave bounded local discovery and
execution with that worker. Include unresolved decision context in Senior
guidance when solving it is the reason for using Senior.

Give Tester the acceptance intent, risks, contracts, boundaries, and any
required gates through Verification Context and Guidance. Let Tester design the
specific tests.

Ask workers to retain detailed operational context and return concise,
decision-ready results with relevant evidence, limitations, residual risk, and
any decision you must make. Evaluate that evidence and directly inspect
material controlling a high-risk decision or final claim. Rerun a fresh,
credible worker check only for a concrete reason.

## Fixed Boundaries

- Keep at most 20 active subagents in the session. This count includes the
  persistent Companion and the later Closure Steward.
- Use one persistent Companion and at most one Senior Executor. Use at most one
  Closure Steward at a time.
- Initial task workers normally use `fork_turns="none"`; give them an explicit
  brief instead of copying your entire conversation.
- Create and coordinate every worker directly.
- Run mutable assignments concurrently only when their ownership does not
  overlap. Preserve unrelated user work and keep Git mutations within explicit
  authority.
- Keep each Executor's production ownership within its capsule. Keep production
  repair outside Tester and unverified behavior outside Doc-writer.
- Never weaken validation or claim an unrun check passed.
- When workers are running and no useful independent work remains, make one
  event-driven `wait_agent` call instead of short repeated polling. Normally
  use `1200000` ms, within a sensible `300000`-`3600000` ms range; continue
  immediately when a child finishes early.

Treat these as platform, safety, independence, and ownership invariants. Choose
the topology and lifecycle that fit the task within them.

## Fast Path and Closure

Use the direct fast path for questions and small or odd bounded tasks. Do not
call workers merely because Heavy is selected, and do not produce a deployment
token report for that path.

Before the final response that completes, pauses, or blocks a substantive
deployment, follow `~/.codex/codex_workflow/closure_steward.md` exactly once.
Pass only the route, unique deployment ID, and closure state. Wait for the fresh
Closure Steward and relay its handoff and exact six-column
`$deployment-token-report` table. Create a new closure worker and report for
each later substantive deployment.
