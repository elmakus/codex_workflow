# Medium Route

Use after Medium is selected under `AGENTS.md`.

## Your Ownership

You are the main agent. Own planning, diagnosis, implementation, verification,
integration, and user communication. Keep production repair and root-cause
decisions in your role.

Use only these support roles:

| Role | Ownership |
| --- | --- |
| Companion | Create at most one persistent read-only worker for bounded context work in the project ecosystem and retained operational context. |
| Investigator | Create a disposable read-only worker for bounded external-information research on the Internet. Use its synthesis as evidence; retain project discovery and decisions yourself. |
| Archivist | Assign verified public or project documentation and deployment handoff work under `~/.codex/codex_workflow/archivist.md`; it owns documentation, the read-only Git handoff, and closure evidence. |

## Proportionate Documentation Read

Read documentation in proportion to the task. When continuing, start from the
specified checkpoint. Search `agent_docs/` and read the documents or sections
needed to understand the task, its constraints, and dependencies. Expand the
read when context is missing. Read the complete set only when the scope of
work requires it. A missing unrelated document does not block the task.

## Assign Support Work

Decide whether Investigator is useful, what Companion should handle, and how
support work relates to your implementation. Assign a support capability only
when it fits the task. Create Companion with `agent_type="companion"`,
`task_name="companion"`, and `fork_turns="none"` when one bounded assignment can
replace multiple reads or tool turns, suppress bulky evidence, or reuse retained
context later. Reuse the same Companion after a route change.

Start each initial package for a role in this table with **Task ID**, a logical
identifier unique within the deployment. Then use its capsule:

| Role | Capsule parts |
| --- | --- |
| Companion | **Project Context Scope**; **Context Task + Goal**; **Main-Agent Context Guidance** |
| Investigator | **Research Context**; **Research Question + Goal**; **Main-Agent Research Guidance** |
| Archivist | **Documentation Context + Audience**; **Documentation Task + Goal**; **Main-Agent Documentation Guidance** |

Treat these named parts as the complete structure. Use Task ID to correlate
dispatch, reports, follow-ups, and artifacts. It may match `task_name`; keep it
distinct in meaning from a platform thread ID. Require each worker to echo Task
ID in every report. Repeat it in follow-ups and send only the delta. Use the
package format to standardize communication while retaining the ownership
defined above.

## Orchestration Guidance

Reduce main-agent rollouts while retaining implementation and verification
ownership. Batch independent reads, searches, metadata checks, and tool
operations into bounded calls. When several support workers inform the same
decision, dispatch them together, wait for the relevant set to finish, and
synthesize once. Combine related Companion questions into one assignment. Use
appropriately long lifecycle waits for the expected worker set. Start another
batch only when existing evidence materially changes the questions.

Use each batch as a temporary scheduling choice. Preserve sequential ordering
for dependent work and choose the topology that fits the task.

## Fixed Boundaries

- Limit Medium subagents to Companion, Investigator, and Archivist.
  Archivist owns documentation only; keep production implementation
  and verification with the main agent.
- Keep at most 20 active subagents in the session, including Companion,
  Investigators and Archivists. Use at most one persistent Companion and one
  Archivist closure owner per deployment.
- Give support workers bounded questions and sufficient context. Own all
  material interpretations and final claims.
- Preserve unrelated work, verify in proportion to risk, and base every passing
  claim on completed validation evidence.

Within those boundaries, choose the task-specific topology, order, concurrency,
tools, checkpoints, and response to failures. Work directly when a support role
adds no value.

## Fast Path and Closure

Use the direct fast path for questions and small or odd bounded tasks. This path
uses no workers or closure handoff.

Before the final response that completes, pauses, or blocks a substantive
deployment, follow `~/.codex/codex_workflow/archivist.md` exactly once.
Update `agent_docs/project_diary.md` yourself when lasting decisions or lessons
change. Combine remaining documentation and handoff work in one Archivist
assignment when practical. Relay its evidence-backed handoff. Use a new
deployment ID for each later deployment.
