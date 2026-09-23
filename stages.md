# Version-2 stages

## Stage A — Intake and session

1. In the first reply of every new conversation, ask which models to use if
   subagents are needed. Offer the recommended role-based mapping, parent-model
   inheritance, and a custom choice in ordinary language. Wait for an explicit
   answer before substantive editing. Ask again in a new conversation even
   when resuming saved work; chunks in the same section conversation inherit
   the answer and do not ask again.
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
7. Record the conversation-confirmed model choice following the micro
   [runtime contract](../physics-paper-editing/runtime-contract.md).
8. Create version-2 round state using [disk-layout.md](disk-layout.md), including
   a unique `round_id`, starting source hash, and `round_status: active`.
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
6. Make structure-level moves only after the physics architecture is coherent.

An unresolved essential meaning becomes `needs_user`; do not ask a reviewer to
guess it.

## Stage C — Argument-sized chunks

1. Split at physical subclaims, derivation steps, or paragraph boundaries.
2. Keep each chunk at most 12 typographic sentences.
3. Preserve the source format. Do not split inside equations, citations,
   references, definitions, or a definition's immediate interpretation.
4. Assign each chunk its edit intent, initial risk, object-ledger dependencies,
   adjacent context, current snapshot identifier, and stable sentence IDs.
5. Set every chunk's current-round quality and language results to pending.

Prefer coherent argument units over uniform sentence counts.

## Stage D — Adaptive chunk editing

For each pending chunk:

1. Read the current section spine and global object ledger.
2. Route through the micro skill's `direct`, `guided`, or `independent` path.
3. A strong section editor may draft the chunk directly. An economy editor uses
   [scaffolded-mode.md](../physics-paper-editing/scaffolded-mode.md).
4. Reconcile every new or changed object with the global ledger before writing.
5. Apply canon closure from the micro skill. Every changed or newly written
   sentence receives all 15 sentence checks; every other applicable canon
   principle is also mandatory.
6. Persist chunk quality axes and update the ledger only for deliberate,
   section-wide choices.
7. Apply the declared language coverage. Under exhaustive coverage, one editor
   or one language reviewer checks all sentences in the chunk and records a
   verdict for each; never launch one worker per sentence.
8. Accept results only for the live chunk snapshot. Any source change makes the
   affected result stale and triggers the required recheck.
9. Continue to another independent chunk when safe; do not wait on low-value
   ceremony.

## Stage E — Section integration

1. Read the assembled section as one argument.
2. Check the global physics spine, object identity, scope, factor conventions,
   cross-chunk transitions, claim strength, and applicable formal logic.
3. Compare the assembled text with the source, global context, and any project
   vocabulary registry. Resolve every newly introduced technical term,
   shortened name, abbreviation, or mathematical alias.
4. Run one section-wide holistic review. Add math review only when formal
   content warrants it.
5. Reopen only spans with a failed required axis; route those spans through the
   micro skill.
6. Recompute the assembled section hash and reject stale chunk or section
   reviews.
7. Mark the round ready only when all required axes pass, no review is running,
   every chunk has a current-round result, and the declared language coverage
   is complete on the current source.

Stage E is not a repetition of every chunk's local checks. It targets global
relationships that chunk review cannot see.
