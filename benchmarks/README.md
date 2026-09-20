# Benchmark coverage

The existing [light benchmark](../light_benchmark/README.md) is an initial case
study, not a general performance claim. Broader benchmarks should test whether
the workflow remains useful across different task shapes, repository sizes, and
execution profiles.

Useful coverage includes:

- bug fixes, feature work, refactors, repository research, and mixed
  implementation/verification tasks;
- small repositories and larger codebases with meaningful cross-file context;
- short bounded work and longer tasks that exercise durable context and
  handoffs;
- the supported `plus` and `muse-max` profiles, with a no-workflow baseline
  when that comparison is meaningful;
- normal success paths plus repair, blocked-worker, long-running-worker, and
  recovery cases.

## Comparison method

For a controlled comparison, keep the starting repository state, task prompt,
tool permissions, acceptance checks, and relevant external inputs equivalent.
Record enough provenance to reproduce the run:

- exact repository commit and workflow version/commit;
- active compute profile and actual Main/worker allocations;
- completion status and acceptance/test result;
- elapsed time when it is measured consistently;
- token or cost data only when the runtime exposes comparable measurements;
- material retries, repairs, recoveries, or human interventions.

Do not compare different providers or model families as if one number were
portable across different prompts, tools, repositories, or acceptance criteria.
When those variables differ, treat the result as a separate case rather than a
ranking.

## Interpretation

A benchmark should help find regressions, context bottlenecks, coordination
overhead, and tasks where a different orchestration choice deserves further
study. A single successful case does not establish that one profile or workflow
shape is universally better. Prefer repeated, reproducible cases and keep raw
evidence available for later analysis.
