# Section acceptance checklist

## Version-2 state

- [ ] `session.md` records `harness_version: 2`, routing, constraints, and next action.
- [ ] The active round has a unique `round_id`, explicit `language_coverage`,
      immutable original source and boundaries, current candidate, identifiers,
      and is selected by `CURRENT`.
- [ ] `section-brief.md` contains the global physics spine.
- [ ] `object-ledger.md` covers every new or changed story-bearing object.
- [ ] Chunks are argument-sized, normally at most 12 sentences, and source-
      format-safe. Any indivisible oversized unit is section-owned and reviewed.
- [ ] Every chunk inherited the current spine and ledger.
- [ ] Every chunk result belongs to the current round and matches the live
      chunk snapshot plus its reviewed context and object-ledger revisions.
- [ ] Selective coverage identifies which sentences were checked; exhaustive
      coverage records a current verdict for every sentence in every chunk.
- [ ] No ordinary synchronous direct chunk manufactured a reviewer or legacy
      `OVERALL` state. Direct work still persisted state when lifecycle or
      evidence requirements demanded it.
- [ ] No version-2 path launched one reviewer per sentence; reviewed work used one
      whole-unit sentence reviewer and one terminology-and-notation reviewer per chunk.
- [ ] Any factor or normalization change passed factor round-trip, inline-substitution, and payoff tests.
- [ ] Every in-scope sentence was checked against all 15 sentence principles;
      coverage selected sentences, not principles.
- [ ] Stage E reviewed global physics story, object consistency, and the
      assembled terminology-and-notation delta once.
- [ ] All applicable required quality axes pass; any `N/A` has no object to
      inspect, and no unresolved `FIX` or `USER_DECISION` remains.
- [ ] Verification independence is stated accurately.
- [ ] Each persisted review records the role and actual model metadata available
      from the runtime.
- [ ] No legacy or superseded result contributes to current completion.
- [ ] The first reply announced and used any standing role-to-model policy without
      asking for confirmation. If no standing policy existed, it asked and
      waited. Resumed work re-read current standing instructions; chunks did
      not ask again.
- [ ] Every user-facing message follows the shared communication policy: it
      uses ordinary language and exposes no unexplained internal workflow or
      schema label. If the user requested an audit, each necessary internal
      term is explained in plain language on first use.

## Regression scenarios

- [ ] A one-use reduced weight is absorbed into the physically relevant total.
- [ ] A genuinely reused normalized function is retained.
- [ ] A valid construction definition is not forced into an invented operational form.
- [ ] A user prohibition on subagents is honored.
- [ ] An unknown model takes economy routing without an invented identifier.
- [ ] A version-1 session is treated as closed history and a new version-2
      round starts with all checks pending.
- [ ] A source edit after PASS makes the affected snapshot result stale.
- [ ] An exhaustive round cannot complete with a skipped or missing sentence
      verdict.
- [ ] Starting a new internal version-2 round is described to the user, when it
      matters at all, as a fresh editing pass based on the current text.
- [ ] A likely direct edit announces an existing standing role-to-model policy or asks
      for a mapping when none exists.
- [ ] An ordinary synchronous short direct edit checks the full applicable
      canon without manufacturing reviewer or persistence artifacts; a
      resumable or concurrent direct edit persists the required state.
- [ ] A newly drafted passage treats every sentence as changed.
- [ ] A one-off coined technical label or mathematical alias is replaced,
      defined and justified, or removed before completion.
- [ ] Reviewed work ran independent whole-unit sentence and terminology checks;
      every principle hit triggered its whole-unit specialist.
- [ ] A newly discovered source-level scientific defect paused the entire round
      instead of becoming a limitation or allowing other chunks to continue.
- [ ] Selective chunk results record checked sentence IDs; exhaustive results
      contain every sentence.
- [ ] A context or ledger revision invalidates dependent reviews even when the
      chunk text hash is unchanged.
- [ ] Formal PASS records whether it covers changed statements, their dependency
      closure, or all in-scope formal content.
- [ ] A whole section of at most 12 sentences still routes to this skill.

The detailed micro semantic fixtures live in
[semantic-fixtures.md](../physics-paper-editing/semantic-fixtures.md).
