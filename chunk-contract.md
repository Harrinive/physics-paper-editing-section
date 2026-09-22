# Chunk contract

## Section to micro

```yaml
harness_version: 2
chunk_id: cNN
chunk_text: <at most 12 sentences>
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
execution_path: direct | guided | independent
verification_independence: independent | self_only | unavailable
quality:
  scientific_fidelity: PASS | FIX | USER_DECISION | N/A
  physics_lead: PASS | FIX | USER_DECISION | N/A
  formal_validity: PASS | FIX | USER_DECISION | N/A
  prose: PASS | FIX | USER_DECISION | N/A
completion: ready | needs_fix | needs_user
object_ledger_changes: []
summary: <one or two lines>
```

Persist review artifacts only when the selected path or resume requirements
need them. Direct chunks do not manufacture worker records.

## Write-back

Use stable anchors or version-2 sentinels from the micro
[job-state.md](../physics-paper-editing/job-state.md) when concurrent editing
requires them. Verify the live span before applying a reviewed replacement.
