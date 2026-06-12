# Scope parameter & section-scoped verifiers

**Read with the Read tool** for Stages B and E.

Section-scoped review reuses the micro skill's checklists **verbatim**:

- [narrative-checks.md](../physics-paper-editing/narrative-checks.md)
- [math-checks.md](../physics-paper-editing/math-checks.md)

Do **not** fork or edit those files. The macro skill adds a **`Scope:` header** so verifiers know which unit "the whole" refers to (the checklists already support section scale).

## Scope values

| Scope | When | Unit under review |
|-------|------|-------------------|
| `section` | Stages B, E | Full target `\section{...}` block (+ brief) |
| `chunk` | Stage D | Handled inside micro skill (default there) |

Do **not** add `Scope:` to the micro skill's own prompts — only macro-launched Tasks use `Scope: section`.

## When to launch

| Stage | Tasks | readonly |
|-------|-------|----------|
| B — macro structural | 1 narrative + 0–1 math (if math present) | yes |
| E — integration | 1 narrative + 0–1 math, boundary-focused | yes |

Use `verifier_profile.deep` from `session.md` § Verifier model profile (or section-brief when confirmed). Launch in parallel when practical.

**Hard stop:** if `session.md` `user_confirmed: false`, run Stage A AskQuestion before launching section verifier Tasks.

## Narrative verifier prompt (Scope: section)

```text
Task(
  subagent_type: "generalPurpose",
  readonly: true,
  model: <deep slug from section brief>,
  description: "Section narrative verify: Stage <B|E>",
  prompt: <template below>
)
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
Read narrative-checks.md (Read tool). Run every group and bullet.
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
Task(
  subagent_type: "generalPurpose",
  readonly: true,
  model: <deep slug from section brief>,
  description: "Section math verify: Stage <B|E>",
  prompt: <template below>
)
```

```text
You are a math/logic verifier for a physics paper. You did NOT write this text.

## Scope
section

## Passage summary
<identical to narrative Task>

## Text under review
<full section LaTeX>

## Stage context
<Stage B or E focus as above>

## Instructions
Read math-checks.md (Read tool). Run Step 0, then type-specific checks.
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

**No new prose** in Stage B. Placeholders are filled and verified per chunk in Stage D.

Stage B does **not** require a separate CHECKS block — lean approach: mechanical structural moves + chunk verification covers prose. Record structural changes in the stage report.

## Stage E integration PASS

Integration PASS = narrative + math verifiers report no unresolved FAIL items on boundary-focused review **and** any boundary fixes have passed micro Phase 2.

Emit `<!-- SECTION DONE ... -->` per [SKILL.md](SKILL.md) § Response format.
