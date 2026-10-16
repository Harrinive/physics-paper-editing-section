# Version-2 stages

## Stage A — Intake and session

1. In the first reply, check for a standing project or conversation
   role-to-model policy. A project policy is the file `physics-edit-policy.json`
   at the repository root (`scripts/check_edit_round.py policy show`). If present,
   state its mapping and continue without asking for confirmation. If absent, the
   skill supplies no default: ask which model and effort each reviewer role uses,
   wait for the answer, and write it with `policy set`, once per project.
   `init` refuses to create a round without the file. On resume, current standing instructions override stale saved
   profiles; chunks inherit the active mapping and do not ask again.
2. Decide whether this is an explicit continuation of the active version-2
   round or a new round. A rerun, rewrite, fresh pass, or request to review the
   whole text anew creates a new round; legacy state is never resumable.
3. Read the section, immediate neighbors, and enough introduction/abstract
   context to identify the promised result.
4. Infer `edit_intent`; ask only if copyedit versus substantive work is genuinely
   ambiguous and changes scope.
5. Set `language_coverage: selective | exhaustive`. Infer exhaustive only from
   requests such as every sentence, line by line, full language audit, or an
   equivalent explicit requirement. If coverage materially affects the
   expected result and is ambiguous, ask before editing.
6. Resolve model tier through the runtime adapter and classify initial risk.
7. Record the active role-to-model policy following the micro
   [runtime contract](../physics-paper-editing/runtime-contract.md).
8. Create version-2 round state using [disk-layout.md](disk-layout.md), including
   a unique `round_id`, immutable copy of the round-start section, original
   chunk boundaries, starting source hash, and `round_status: active`.
9. Preserve user constraints and manuscript conventions. Historical findings
   may inform context but never count as current quality results.

## Stage B — Physics architecture

Before moving paragraphs or drafting prose:

1. Write the section physics spine: situation → mechanism → relevant quantities
   → principal result.
2. Build the global object ledger using
   [physical-lead.md](../physics-paper-principles/physical-lead.md).
3. Record every object's category, scope, units/scaling, included factors,
   normalization, first use, later payoff, and disposition.
4. Identify the section's terminology and notation sources, including any
   project vocabulary registry and established manuscript symbols.
5. Identify missing links, duplicate objects, conflicting normalizations,
   unnecessary synonyms or aliases, and unresolved scientific choices.
6. Run the convention-merge check
   ([physical-lead.md](../physics-paper-principles/physical-lead.md))
   section-wide, not per chunk — chunk-level review sees only a local slice
   of a symbol's usage count.
7. If the section contains parallel bullets, paragraphs, derivations, or
   subsections, pick one shared presentation template for them (parallel-unit
   alignment in [narrative.md](../physics-paper-principles/narrative.md))
   before chunking, so independently edited chunks don't drift apart for no
   physical reason.
8. Make structure-level moves only after the physics architecture is coherent.

An unresolved essential meaning becomes `needs_user`; do not ask a reviewer to
guess it.

Any newly discovered scientific defect in the author's source that is outside
the authorized objective also makes the whole round `needs_user`. Stop other
chunk work until the author decides whether to expand the scope or supplies the
intended science.

## Stage C — Argument-sized chunks

1. Split at physical subclaims, derivation steps, or paragraph boundaries.
2. Keep each chunk at most 12 typographic sentences when source-safe boundaries
   permit it.
3. Preserve the source format. Do not split inside equations, citations,
   references, definitions, or a definition's immediate interpretation.
4. Assign each chunk its edit intent, initial risk, object-ledger dependencies,
   adjacent context, current snapshot identifier, and stable sentence IDs.
5. If an indivisible definition, equation, citation, or immediate interpretation
   exceeds 12 sentences, keep it as one section-owned oversized chunk and use
   the reviewed contract directly; do not split the unit merely to satisfy the
   cap.
6. Set every chunk's current-round quality and language results to pending.

Prefer coherent argument units over uniform sentence counts.

## Stage D — Adaptive chunk editing

For each pending chunk:

1. Read the current section spine and global object ledger.
2. Route ordinary chunks through the micro skill's `direct | reviewed` path.
   Apply the same reviewed contract directly to a section-owned oversized
   chunk.
3. A strong section editor may draft the chunk directly. An economy or unknown
   editor uses [scaffolded-mode.md](../physics-paper-editing/scaffolded-mode.md).
4. Reconcile every new or changed object with the global ledger before writing.
5. Apply canon closure from the micro skill. Every changed or newly written
   sentence receives all 15 sentence checks; every other applicable canon
   principle is also mandatory.
6. Under `reviewed`, run one whole-unit sentence reviewer and one
   terminology-and-notation reviewer on the first draft of the chunk, then every
   principle specialist triggered by the sentence hit map. Apply the accepted
   findings in one batch and re-review only the touched sentences with their
   neighbours as context
   ([scoped-review.md](../physics-paper-editing/scoped-review.md)). When no
   sentence is pending, run one whole-chunk sentence review and one whole-chunk
   terminology-and-notation review of the final text (the close of the chunk).
   The sentence and terminology reviewers receive no source text.
7. Persist chunk quality axes, checked sentence IDs, principle hits, and the
   reviewed context revision and applicable object-ledger revision. Update the
   ledger only for deliberate,
   section-wide choices.
8. Apply the declared language coverage. Record every checked sentence under
   either coverage mode; exhaustive coverage includes every sentence. Never
   launch one reviewer per sentence.
9. Accept a verdict only when the sentence and its predecessor are unchanged
   and the recorded context revision and applicable object-ledger revision
   match. A text change makes the verdict of the changed sentence and of the
   sentence after it stale; a dependency change makes the affected results
   stale. A stale verdict triggers a scoped recheck, not a whole-chunk one.
   A sentence flagged a third time goes to the author as a decision.
10. Continue to another independent chunk only while no source-level scientific
    defect is awaiting the author.

## Stage E — Section integration

1. Read the assembled section as one argument.
2. Check the global physics spine, object identity, scope, factor conventions,
   cross-chunk transitions, claim strength, and applicable formal logic.
3. Compare the assembled text with the source, global context, and any project
   vocabulary registry. Resolve every newly introduced technical term,
   shortened name, abbreviation, or mathematical alias.
4. Run one section-wide holistic review. When formal content requires review,
   set an explicit `changed`, `dependency_closure`, or `all_in_scope` scope;
   use `none` only when the edited unit contains no relevant formal statement.
   High-risk section work uses `all_in_scope` for the affected unit.
5. Reopen only spans with a failed required axis; route those spans through the
   micro skill.
6. Recompute the assembled section hash and reject chunk or section reviews
   whose text, context, or ledger revision is stale.
7. Mark the round ready only when all applicable required axes pass, no review is running,
   every chunk has a current-round result, and the declared language coverage
   is complete on the current candidate snapshot.

Stage E is not a repetition of every chunk's local checks. It targets global
relationships that chunk review cannot see.
