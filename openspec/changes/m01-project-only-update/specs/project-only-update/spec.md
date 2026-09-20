# Project-only update behavior

## Equal-version routing

When the selected release version equals the installed user-level runtime version, the CLI MUST reuse installed verified source and MUST NOT acquire the release archive. An explicit `--source` with equal version MAY be version-checked, but the project-only mutation plan MUST target the installed runtime version and MUST NOT replace shared runtime state.

## Project source resolution

The current project's recorded workflow version MUST resolve through existing historical `.source_backup/<version>` behavior. Missing or mismatched historical source MUST fail closed. A project newer than the incoming/installed target MUST still require explicit downgrade approval.

## Mutation boundary

The project-only plan MUST contain only mutations required for the selected project. It MUST NOT mutate user-level runtime files, workers, skills, user-level install state, or shared runtime configuration.

Before applying, unchanged project mutations MUST be removed from the plan. Only existing project files that are actually changed or deleted MAY be backed up.

## Backup / no-op

When changed existing project files exist, the plan MUST create one project-scoped backup preserving their paths under the normal backup root. It MUST NOT back up unrelated user/runtime/project files.

If the selected project is already current and produces no changed mutations, the command MUST return a no-op and MUST NOT create a backup. A project without a workflow entry point also MUST perform no mutation.

## Compatibility

Historical-source, multi-project catch-up, transactional write safety, and explicit downgrade protection remain authoritative.
