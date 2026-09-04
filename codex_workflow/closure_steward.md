# Closure Steward

Run this automatic closure once after every substantive Medium or Heavy
deployment and before your final response, including when the deployment pauses
or blocks. Skip this handoff and its token report for questions and small or odd
bounded tasks on the direct fast path.

Spawn one fresh worker with:

- `agent_type="closure_steward"`
- `task_name="closure_steward_<deployment_id>"`, where the suffix is a unique,
  lowercase, underscore-safe deployment identifier
- `fork_turns="200"`

Pass only the active route, deployment ID, and closure state (`complete`,
`paused`, or `blocked`). Do not summarize the session, build a task capsule, or
maintain a separate usage summary. Rely on the automatic finite fork to pass
recent main-agent turns while retaining the worker's Luna max model. Use that
inherited deployment context and the full procedure in its TOML.

Give that worker sole ownership of reconciling the complete `agent_docs/`
framework, performing compact closing checks, inspecting and reporting relevant
Git status, and returning the final handoff report. Allow it to inspect other
documents for conflicts, but require all edits to stay within `agent_docs/`.
Keep every commit as a separate, explicitly authorized user action.
Do not call a second documentation worker or duplicate these steps. Wait while
Closure Steward seals its closure work, invokes `$deployment-token-report`, and
returns the exact six-column table with its final handoff. Relay both results
without a Companion dispatch. Create a fresh uniquely named Closure Steward for
every later substantive deployment in the same session.

If the worker cannot be created or is blocked, report that limitation. Do not
silently transfer the handoff or token report to Companion or another role.
