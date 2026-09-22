# Chunk contract

## Section to micro

```yaml
harness_version: 2
round_id: <current round>
chunk_id: cNN
chunk_text: <at most 12 sentences>
section_snapshot_id: <sha256>
chunk_snapshot_id: <sha256>
language_coverage: selective | exhaustive
edit_intent: copyedit | substantive
model_tier: strong | economy | unknown
tier_source: adapter | user | inherited | fallback
scientific_risk: low | medium | high
user_constraints: <verbatim relevant constraints>
reviewer_model_profile: <user-confirmed section profile, when workers are used>
section_physics_spine: <current spine>
global_object_ledger: <current ledger>
adjacent_context: <one to three sentences each side>
tex_anchor: <stable source span>
```

The micro editor may raise risk, flag an unresolved scientific choice, or
propose a ledger update. It may not silently redefine a global object.

## Micro to section

```yaml
chunk_id: cNN
round_id: <current round>
chunk_snapshot_id: <reviewed sha256>
execution_path: direct | guided | independent
verification_independence: independent | self_only | unavailable
review_model_metadata: <role, requested model, resolved model, reasoning effort>
quality:
  scientific_fidelity: PASS | FIX | USER_DECISION | N/A
  physics_lead: PASS | FIX | USER_DECISION | N/A
  formal_validity: PASS | FIX | USER_DECISION | N/A
  prose: PASS | FIX | USER_DECISION | N/A
completion: ready | needs_fix | needs_user
language_review:
  coverage: selective | exhaustive
  status: PASS | FIX | USER_DECISION
  sentence_results: <required for exhaustive; omitted for selective>
object_ledger_changes: []
summary: <one or two lines>
```

For exhaustive coverage, `sentence_results` contains every current sentence ID,
its exact-span hash, and `PASS | FIX | USER_DECISION`. One reviewer may check
the whole chunk; do not create one worker per sentence. Persist review artifacts
only when the selected path, coverage contract, or resume requirements need
them. Direct chunks do not manufacture worker records.

## Write-back

Use stable anchors or version-2 sentinels from the micro
[job-state.md](../physics-paper-editing/job-state.md) when concurrent editing
requires them. Verify the live span before applying a reviewed replacement.
After write-back, recompute the chunk snapshot. Any mismatch makes the prior
result stale and requires the affected checks to run again.
