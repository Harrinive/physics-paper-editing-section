# Scope parameter & section-scoped verifiers

**For agents:** Start with [SKILL.md](SKILL.md) § Agent read order. **Read with the Read tool** for Stages B and E.

Section-scoped review uses **`physics-paper-principles`** **verbatim**:

- [narrative.md](../physics-paper-principles/narrative.md)
- [math.md](../physics-paper-principles/math.md)
- named objects: [physical-lead.md](../physics-paper-principles/physical-lead.md)

Severity mapping (BLOCKER vs SUGGEST) is [severity.md](../physics-paper-editing/severity.md). Do **not** fork those files. This skill adds a **`Scope:` header** so verifiers know which unit "the whole" refers to (the narrative file already supports section scale).

## Scope values

| Scope | When | Unit under review |
|-------|------|-------------------|
| `section` | Stages B, E | Full target `\section{...}` block (+ brief) |
| `chunk` | Stage D | Handled inside micro skill (default there) |

Do **not** add `Scope:` to the micro skill's own prompts — only macro-launched section verifiers use `Scope: section`.

## When to launch

| Stage | Verifier assignments | write policy |
|-------|-------|----------|
| B — macro structural | 1 narrative + 0–1 math (if math present) | yes |
| E — integration | 1 narrative + 0–1 math, boundary-focused | yes |

Use the confirmed `deep` role from `session.md` § Verifier model profile. Schedule runtime-aware waves and harvest result shards the same way as micro jobs if the user keeps editing.

If `user_confirmed: false`, collect the session-level model-profile choice before delegation ([cross-skill.md](cross-skill.md) § Verifier model profile).

## Narrative verifier prompt (Scope: section)

```text
role: narrative
scope: section
model_role: deep
write_policy: no-source-edits
completion: asynchronous-when-supported
prompt: template below
```

```text
You are a narrative verifier for a physics paper. You did NOT write this text.

## Scope
section

## Passage summary
<from section-brief.md + section role>

## Text under review
<full section LaTeX after structural moves (Stage B) or assembled section (Stage E)>

## Stage context
<Stage B: structural review only — flag argument order, motivation gaps, redundancy, notation drift, misplaced material>
<Stage E: integration — focus on chunk boundaries, transitions, cross-chunk notation, new redundancy>

## Adjacent context (if helpful)
<1–3 sentences from neighboring sections, or omit>

## Instructions
Read ../physics-paper-principles/narrative.md (Read tool). Run every group and bullet.
Scope: section — "the whole" means this entire section block.
Do not edit the text. Report each group in file order.

## Output format
### Narrative verification (Scope: section)
**Group 1 — Core message and framing:** <findings or PASS>
**Group 2 — Logical arc and motivation:** <findings or PASS>
**Group 3 — Consistency and economy:** <findings or PASS>
**Group 4 — Claims and audience:** <findings or PASS>

**FAIL items:** <bulleted list with check name and one-line reason; or "none">
```

## Math verifier prompt (Scope: section)

```text
role: math
scope: section
model_role: deep
write_policy: no-source-edits
completion: asynchronous-when-supported
prompt: template below
```

```text
You are a math/logic verifier for a physics paper. You did NOT write this text.

## Scope
section

## Passage summary
<identical to the narrative verifier summary>

## Text under review
<full section LaTeX>

## Stage context
<Stage B or E focus as above>

## Instructions
Read ../physics-paper-principles/math.md (Read tool). Run Step 0, then type-specific checks.
Named objects: also physical-lead.md.
Scope: section — classify every statement in this section block.
If no math: state N/A and complete the report.

## Output format
### Math verification (Scope: section)
**Step 0 — Classifications:** <list or "no math statements">

**Per-statement / per-type findings:** <findings in file order>

**FAIL items:** <bulleted list; or "none">
```

## Applying Stage B findings

The **orchestrator** (not verifiers) applies **structure-only** fixes:

- Reorder / split paragraphs
- Add or move signposts, `\label{}`, forward/back references
- Mark `[INSERT PROSE: …]` placeholders for Stage D
- Assess physical meaning and definition choice. Flag weak motivation as a presentation suggestion; identify essential scientific ambiguity separately. Constructions are allowed. Do not author new physical interpretation in Stage B.

**No new prose** in Stage B. Placeholders are filled and verified per chunk in Stage D. A chunk that introduces a named physical object still runs the micro definition halt before drafting.

Stage B does **not** require a separate CHECKS block — lean approach: mechanical structural moves + chunk verification covers prose. Record structural changes in the stage report.

## Stage E integration PASS

Integration PASS = narrative + math verifiers report no unresolved FAIL items on boundary-focused review **and** any boundary fixes have passed micro Phase 2.

Emit `<!-- SECTION DONE ... -->` per [SKILL.md](SKILL.md) § Response format.
