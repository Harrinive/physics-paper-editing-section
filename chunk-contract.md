# Chunk contract

## Section to micro

```yaml
harness_version: 2
round_id: <current round>
chunk_id: cNN
chunk_text: <normally at most 12 sentences; oversized section-owned unit allowed>
original_source_id: <round-start source sha256>
section_candidate_snapshot_id: <sha256>
chunk_snapshot_id: <sha256>
context_revision: <sha256 or monotonic id>
object_ledger_revision: <sha256 or monotonic id>
language_coverage: selective | exhaustive
edit_intent: copyedit | substantive
model_tier: strong | economy | unknown
tier_source: adapter | user | inherited | fallback
scientific_risk: low | medium | high
user_constraints: <verbatim relevant constraints>
role_model_policy: <active section policy; standing or user-selected>
section_physics_spine: <current spine>
global_object_ledger: <current ledger>
adjacent_context: <one to three sentences each side>
source_anchor: <stable source span>
```

The micro editor may raise risk, flag an unresolved scientific choice, or
propose a ledger update. It may not silently redefine a global object.

## Micro to section

```yaml
chunk_id: cNN
round_id: <current round>
chunk_snapshot_id: <reviewed sha256>
context_revision: <reviewed revision>
object_ledger_revision: <reviewed revision>
execution_path: direct | reviewed
review_profile: standard | high_risk
formal_review_scope: none | changed | dependency_closure | all_in_scope
verification_independence: independent | self_only | unavailable
review_model_metadata: <role, requested model, resolved model, reasoning effort>
quality:
  scientific_fidelity: PASS | FIX | USER_DECISION | N/A
  physics_lead: PASS | FIX | USER_DECISION | N/A
  formal_validity: PASS | FIX | USER_DECISION | N/A
  terminology_notation: PASS | FIX | USER_DECISION | N/A
  prose: PASS | FIX | USER_DECISION | N/A
completion: ready | needs_fix | needs_user
language_review:
  coverage: selective | exhaustive
  status: PASS | FIX | USER_DECISION
  checked_sentence_ids: <required for both modes>
  sentence_results: <all checked sentences; exhaustive includes every sentence>
  principle_hits: <P01--P15 statuses and affected sentence IDs>
terminology_review: <whole-unit status and delta disposition>
triggered_specialists: []
object_ledger_changes: []
summary: <one or two lines>
```

For selective coverage, `checked_sentence_ids` and `sentence_results` contain
every changed, newly written, or diagnosed sentence. For exhaustive coverage,
they contain every current sentence. Each recorded result includes the exact-
span hash when snapshot evidence is required. One reviewer checks the whole
chunk; do not create one reviewer per sentence. Persist review artifacts when the
coverage contract or lifecycle requires them. Direct chunks do not manufacture
reviewer records, but direct routing does not exempt resumable or concurrent
work from state.

## Write-back

Use stable anchors or version-2 sentinels from the micro
[job-state.md](../physics-paper-editing/job-state.md) when concurrent editing
requires them. Verify the live span before applying a reviewed replacement.
After write-back, recompute the chunk snapshot. A mismatch in text,
context_revision, or object_ledger_revision makes the prior result stale and
requires the affected checks to run again.
