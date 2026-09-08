# Archivist Assignments

Use Archivist for verified documentation work in Heavy. Give each assignment a
Task ID and the Documentation Context + Audience, Documentation Task + Goal, and
Main-Agent Documentation Guidance capsule. Identify the write surface and provide
verified facts or exact evidence references.

Choose the number, timing, and reuse of Archivist workers according to the task.
Give concurrent workers non-overlapping document ownership. Ordinary assignments
normally use `agent_type="archivist"` and `fork_turns="none"`.

## Deployment Closure

Assign one Archivist to close each substantive deployment before the final
response, including paused or blocked work. Finish your own required update to
`agent_docs/project_diary.md` first. Combine remaining verified documentation
updates with this handoff when practical. Include `project_progress.md` and
`latest_session_work.md` in the assigned scope, plus the deployment ID, closure
state (`complete`, `paused`, or `blocked`), and read-only Git handoff.

Reuse an Archivist when its retained context plus a concise delta is sufficient.
Otherwise create one with `agent_type="archivist"`, a unique task name such as
`archivist_<deployment_id>`, and `fork_turns="200"`. For this inherited-context
assignment, reference the fork as documentation context instead of writing a
deployment summary. Supply only scope and guidance the fork does not establish.

Ensure other workers have finished changes relevant to the handoff before
Archivist seals it. Assign only one closure owner for each deployment. Relay its
documentation handoff without repeating its operational checks. A later
substantive deployment receives its own closure handoff.

For questions and small bounded tasks in leaf state, work directly without this
closure handoff. If Archivist is unavailable or blocked, report the limitation
and the remaining work accurately.
