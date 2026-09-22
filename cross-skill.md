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
- the current `round_id`, declared language coverage, and section/chunk snapshot
  identifiers;
- edit intent, model tier, tier source, user constraints, and the section's
  user-confirmed reviewer model profile;
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

1. Resolve `CURRENT` and read that version-2 round's `session.md`,
   `section-brief.md`, `object-ledger.md`, and `manifest.json`.
2. If the only state is legacy or lacks `harness_version: 2`, treat it as
   closed history and create a fresh version-2 round. Do not copy its PASS or
   completion state into the new manifest.
3. Reject stale reviews whose snapshot does not match the live
   chunk or section. Detail: [automation.md](automation.md).
4. Honor the recorded edit intent, tier, user constraints, and next action.
5. At the first reply of a resumed conversation, ask for a fresh explicit model
   choice. The saved profile or a standing project instruction may be shown as
   the recommended option but does not replace the question. Reuse the answer
   within the current conversation. An adapter-resolved capability tier alone
   does not confirm a model choice.

## Completion mapping

Chunk `completion: ready` maps to manifest status `ready`. `needs_fix` maps to
`editing`; `needs_user` maps to `needs_user`. The section is ready only after
Stage E passes its required axes and the declared language coverage is complete
on current snapshots.
