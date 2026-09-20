# Research — upstream 1.1.18 audit

Date: `2026-09-20`
Status: `complete`
Subject: `upstream-1.1.18-alignment@R1`

## Baseline

- Fork: `elmakus/codex_workflow`
- Fork main at audit: `d285aa1a271258052d23e3a2d3b585117fc1e862`
- Fork version: `1.1.17-private.12`
- Upstream: `viettran-edgeAI/codex_workflow`
- Upstream version: `1.1.18`
- Meaningful common baseline: `414a5d301ff17ca6e655330474c8346863d0d5d0`

At audit time upstream was 15 commits ahead of the common baseline while this fork had independently diverged substantially.

## Relevant upstream changes

### Runtime/update hardening

Upstream commit `a6ceeab735` added a dedicated project-only update path. When the installed user-level version already matches the selected release, the installed verified source can update an older target project without re-downloading/replacing shared runtime files. Only changed project files are backed up and a current project can return a no-op without a new backup.

The fork already resolves a project's recorded historical workflow version from `.source_backup/<version>` and already tests multi-project catch-up. The useful upstream delta is therefore the narrower project-only path, not historical-source support itself.

Upstream commit `dd65c21503` added explicit rejection of stale protected/local instructions that still reference removed legacy route paths and broadened reviewed `--legacy-local-instructions` handling to bootstrap/install/update.

### Worker topology

Upstream 1.1.18 separates:
- Explorer: bounded read-only project-context discovery/mapping/evidence retrieval.
- Investigator: bounded read-only fault hypotheses, solution alternatives, feasibility and prior-art research.

For one bounded problem that requires Investigator, upstream now starts exactly three independent lanes with a shared Problem ID and distinct Task IDs/search angles.

Upstream removed Companion after an intermediate design used it as a sibling-worker report collector. The final upstream topology sends reports directly through the parent-child channel to Main.

### Reporting

Upstream worker prompts moved away from hard 120/180/200-word limits toward the smallest complete evidence-linked/decision-ready report, with bulky logs and diffs referenced rather than copied.

### Platform settings

Upstream 1.1.18 writes:
- `[features] multi_agent = true`
- `[features.multi_agent_v2] enabled = true`
- wait timeout ownership of 120000 / 300000 / 1800000 ms.

The fork currently intentionally retains `multi_agent = true` while removing workflow-owned `multi_agent_v2` keys, with regression coverage for that behavior. No migration to upstream's timeout ownership is part of this scope.

### Documentation intake

Upstream requires one complete direct `agent_docs/` framework intake per substantive Medium/Heavy session, then uses Explorer for bounded deltas. The fork instead reads documentation proportionately to the current task and expands only when context is missing.

### Fork-specific baseline

The fork has:
- compute profiles `plus`, `luna-xhigh`, `pro-x5`, `muse-max`;
- Companion as a persistent internal project-context worker;
- Micro Executor;
- a dedicated Muse process/session lifecycle;
- Material Event Push for internal Codex workers, with Muse workers lacking the same `send_message` channel;
- Medium route and Deployment Token Report already removed.

## Research conclusion

The source evidence supports selective semantic adoption rather than merging upstream 1.1.18 wholesale. Runtime project-only update/stale-route hardening and several worker-contract simplifications are independently portable. Upstream's topology, timeout ownership and complete-doc-intake policy conflict with fork-specific architecture unless explicitly chosen as product/system changes.
