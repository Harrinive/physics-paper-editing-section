# Version-2 stages

## Stage A — Intake and session

1. Read the section, immediate neighbors, and enough introduction/abstract
   context to identify the promised result.
2. Infer `edit_intent`; ask only if copyedit versus substantive work is genuinely
   ambiguous and changes scope.
3. Resolve model tier through the runtime adapter and classify initial risk.
4. If subagents will be used, ask for one model profile before the first launch,
   following the micro [runtime contract](../physics-paper-editing/runtime-contract.md).
5. Create version-2 state using [disk-layout.md](disk-layout.md).
6. Preserve user constraints and manuscript conventions.

## Stage B — Physics architecture

Before moving paragraphs or drafting prose:

1. Write the section physics spine: situation → mechanism → relevant quantities
   → principal result.
2. Build the global object ledger using
   [physical-lead.md](../physics-paper-principles/physical-lead.md).
3. Record every object's category, scope, units/scaling, included factors,
   normalization, first use, later payoff, and disposition.
4. Identify missing links, duplicate objects, conflicting normalizations, and
   unresolved scientific choices.
5. Make structure-level moves only after the physics architecture is coherent.

An unresolved essential meaning becomes `needs_user`; do not ask a reviewer to
guess it.

## Stage C — Argument-sized chunks

1. Split at physical subclaims, derivation steps, or paragraph boundaries.
2. Keep each chunk at most 12 typographic sentences.
3. Do not split inside equations, citations, references, definitions, or a
   definition's immediate interpretation.
4. Assign each chunk its edit intent, initial risk, object-ledger dependencies,
   and adjacent context.

Prefer coherent argument units over uniform sentence counts.

## Stage D — Adaptive chunk editing

For each pending chunk:

1. Read the current section spine and global object ledger.
2. Route through the micro skill's `direct`, `guided`, or `independent` path.
3. A strong section editor may draft the chunk directly. An economy editor uses
   [scaffolded-mode.md](../physics-paper-editing/scaffolded-mode.md).
4. Reconcile every new or changed object with the global ledger before writing.
5. Persist chunk quality axes and update the ledger only for deliberate,
   section-wide choices.
6. Continue to another independent chunk when safe; do not wait on low-value
   ceremony.

## Stage E — Section integration

1. Read the assembled section as one argument.
2. Check the global physics spine, object identity, scope, factor conventions,
   cross-chunk transitions, claim strength, and applicable formal logic.
3. Run one section-wide holistic review. Add math review only when formal
   content warrants it.
4. Reopen only spans with a failed required axis; route those spans through the
   micro skill.
5. Mark the session ready when all required axes pass and no review is running.

Stage E is not a repetition of every chunk's local checks. It targets global
relationships that chunk review cannot see.
