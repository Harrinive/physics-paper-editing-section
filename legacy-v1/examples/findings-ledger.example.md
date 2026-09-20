# Findings ledger: <section-slug>

<!-- Copy to .physics-edit/<section-slug>/findings-ledger.md at Stage B.
     Update through Stages C, D, E. Canonical schema: disk-layout.md § findings-ledger.md -->

## Structural review

**Completed:** `<YYYY-MM-DD>` (Stage B)

### Verifiers

| Verifier | Model | FAIL count |
|----------|-------|------------|
| Narrative | `<deep slug>` | `<N>` |
| Math | `<deep slug>` | `<N>` or N/A |

### Findings

| id | source | check | severity | summary | resolution | owner | status | resolved_at |
|----|--------|-------|----------|---------|------------|-------|--------|-------------|
| F-N01 | narrative | Framing alignment | high | Paragraph title references "version 2" outside scope | fixed_structural | B | resolved | B |
| F-N02 | narrative | Logical arc | high | "We formalize…" sentence appears after Definition | fixed_structural | B | resolved | B |
| F-N03 | narrative | Signposting | high | Lemma conclusion stated in prose before formal Lemma | fixed_structural | B | resolved | B |
| F-N04 | narrative | Cross-part consistency | medium | Flux jump not linked to operational invariance | deferred_prose | c01 | resolved | c01 |
| F-N05 | narrative | Cross-part consistency | medium | "decay" vs "dephasing" terminology drift | deferred_prose | c02 | open | — |
| F-M01 | math | Sufficiency witness | high | Wrong sign on flux-translation unitary in sufficiency | deferred_math | c06 | open | — |
| F-M02 | math | Notation | medium | Hat on c-number Δφ in Lemma statement | deferred_math | c04 | open | — |

**Resolution values:** `fixed_structural` | `deferred_prose` | `deferred_math` | `open` | `wontfix`

**Status values:** `open` | `resolved` | `wontfix`

**Owner values:** `B` (structural pass) | `c01`…`cNN` (chunk) | `E` (integration boundary fix)

**Finding IDs:** `F-N##` narrative · `F-M##` math · `F-I##` integration (Stage E)

---

## Structural edits applied

Structure-only `.tex` changes at Stage B (no new body prose):

1. Renamed `\paragraph{… version 2}` → `\paragraph{Operational definition of a flux jump}`
2. Removed backward signpost *"We formalize… First, we define operational invariance"* (appeared after Definition)
3. Removed lemma pre-statement prose (lines before `\begin{lemma}`)
4. Added `% [INSERT PROSE: bridge — …]` placeholder → owner **c03**

---

## Deferred to chunks

Routing finalized at Stage C (`manifest.json` → `findings_refs`):

| chunk_id | findings_refs | notes |
|----------|---------------|-------|
| c01 | F-N04, F-N07 | Intro self-containment |
| c02 | F-N05 | Definition terminology |
| c03 | (bridge placeholder) | Rewrite chunk |
| c04 | F-M02 | Lemma notation |
| c06 | F-M01 | Sufficiency sign |

---

## Integration review

**Completed:** `<YYYY-MM-DD>` (Stage E) or *pending*

### Verifiers

| Verifier | Model | FAIL count |
|----------|-------|------------|
| Narrative | `<deep slug>` | `<N>` |
| Math | `<deep slug>` | `<N>` or N/A |

### Findings

| id | source | check | severity | summary | resolution | owner | status | resolved_at |
|----|--------|-------|----------|---------|------------|-------|--------|-------------|
| F-I01 | integration | Transitions | medium | Weak bridge between Definition and Lemma | deferred_prose | c03 | open | — |

*(Add rows only for new integration-scope FAILs; do not duplicate resolved structural rows.)*

---

## Closure summary

<!-- Orchestrator mirrors `findings_open` in session.md from this section. -->

```
open: 4 | resolved: 4 | wontfix: 0
integration: pending
```

**SECTION DONE gate:** `open: 0` (or all remaining explicitly `wontfix`) **and** `integration: PASS`.
