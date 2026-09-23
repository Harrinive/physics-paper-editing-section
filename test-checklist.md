# Section acceptance checklist

## Version-2 state

- [ ] `session.md` records `harness_version: 2`, routing, constraints, and next action.
- [ ] The active round has a unique `round_id`, explicit `language_coverage`,
      source hashes, and is selected by `CURRENT`.
- [ ] `section-brief.md` contains the global physics spine.
- [ ] `object-ledger.md` covers every new or changed story-bearing object.
- [ ] Chunks are argument-sized, at most 12 sentences, and source-format-safe.
- [ ] Every chunk inherited the current spine and ledger.
- [ ] Every chunk result belongs to the current round and matches the live
      chunk snapshot.
- [ ] Selective coverage identifies which sentences were checked; exhaustive
      coverage records a current verdict for every sentence in every chunk.
- [ ] No direct chunk manufactured a worker, job directory, or legacy `OVERALL`
      state. Section-owned snapshot and sentence evidence is present when the
      coverage contract requires it.
- [ ] No version-2 path launched one worker per sentence; exhaustive coverage
      used at most one language reviewer per chunk.
- [ ] Any factor or normalization change passed factor round-trip, inline-substitution, and payoff tests.
- [ ] Every in-scope sentence was checked against all 15 sentence principles;
      coverage selected sentences, not principles.
- [ ] Stage E reviewed global physics story, object consistency, and the
      assembled terminology-and-notation delta once.
- [ ] Required quality axes pass; no unresolved `FIX` or `USER_DECISION` remains.
- [ ] Verification independence is stated accurately.
- [ ] Each persisted review records the role and actual model metadata available
      from the runtime.
- [ ] No legacy or superseded result contributes to current completion.
- [ ] The first reply in the editing conversation asked which models to use if
      subagents are needed, and substantive editing waited for the user's
      explicit answer. A resumed conversation asked again; inherited chunks
      did not.
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
- [ ] A likely direct edit still asks the model-choice question at conversation
      intake; later choosing the direct path does not retroactively skip it.
- [ ] A direct edit checks the full applicable canon without manufacturing
      worker or persistence artifacts.
- [ ] A newly drafted passage treats every sentence as changed.
- [ ] A one-off coined technical label or mathematical alias is replaced,
      defined and justified, or removed before completion.

The detailed micro semantic fixtures live in
[semantic-fixtures.md](../physics-paper-editing/semantic-fixtures.md).
