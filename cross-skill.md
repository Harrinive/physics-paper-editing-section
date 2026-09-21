# Micro and section integration

## Routing

| Target | Skill |
|---|---|
| At most 12 sentences | `physics-paper-editing` |
| Over 12 sentences or whole section | `physics-paper-editing-section` |

Both skills use the same version-2 routing state, runtime roles, quality axes,
and physics-paper-principles canon.

## Inherited context

Every chunk receives:

- `harness_version: 2`;
- edit intent, model tier, tier source, and user constraints;
- section physics spine;
- global object ledger;
- adjacent context and manuscript conventions;
- its initial risk and any formal-review trigger.

The chunk may raise its risk but must not silently lower a section-declared
risk. It may propose a ledger change, but the section editor must reconcile that
change globally before later chunks inherit it.

## Roles

The section editor owns global physics architecture and may author body prose.
Independent reviewers do not write source files. Economy models may prepare
worksheets or apply bounded local repairs. There is no absolute
orchestrator-versus-author split in version 2.

## Resume

1. Read `session.md`, `section-brief.md`, `object-ledger.md`, and `manifest.json`.
2. If `harness_version` is absent or not `2`, use
   [legacy-v1/LEGACY.md](legacy-v1/LEGACY.md).
3. For version 2, reject stale reviews whose snapshot does not match the live
   chunk or section. Detail: [automation.md](automation.md).
4. Honor the recorded edit intent, tier, user constraints, and next action.
5. Do not repeat model-profile questions already resolved by the adapter or user.

## Completion mapping

Chunk `completion: ready` maps to manifest status `ready`. `needs_fix` maps to
`editing`; `needs_user` maps to `needs_user`. The section is ready only after
Stage E passes its required axes.
