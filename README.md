# physics-paper-editing-section

Cursor skill for editing a whole LaTeX section or longer passage in physics and mathematics papers. Its checks and workflows reflect editing conventions developed through work with Prof. Jens Koch.

## What it does

This skill applies **global edits and suggestions** at section scale, then **orchestrates local edits** through the micro skill — separating the section into shorter chunks and applying the edit-and-verify treatment for each chunk.

**Scope:** whole LaTeX section or any passage **>12 sentences**. For shorter material, use the companion **micro skill** [physics-paper-editing](https://github.com/Harrinive/physics-paper-editing).

## Install on [Cursor](https://cursor.com)

Requires [physics-paper-editing](https://github.com/Harrinive/physics-paper-editing) installed as a **sibling folder**. Clone both into your skills directory (see the [Cursor Skills docs](https://cursor.com/docs/context/skills) for more details) with the following commands:

```bash
git clone https://github.com/Harrinive/physics-paper-editing.git ~/.cursor/skills/physics-paper-editing
git clone https://github.com/Harrinive/physics-paper-editing-section.git ~/.cursor/skills/physics-paper-editing-section
```

## Entry point

Read **`SKILL.md`** first. Linked detail files (`stages.md`, `chunk-contract.md`, `disk-layout.md`, etc.) hold the full rules.

---

## Not Cursor? Adapt this skill

**This skill was made for Cursor Agent.** It references Cursor-specific tools (`AskQuestion`, `Task` subagents, compliance monitoring). Do not run it verbatim on other platforms — **adapt it** to your agent's tool surface and install layout. Adapt both skills together — the macro orchestrator depends on the micro skill for every chunk.

### How to adapt

Use your platform's skill-creation workflow first, then port the workflow logic (not copy-paste paths):

| Platform | Install path (typical) | Use this to adapt |
|----------|------------------------|-------------------|
| **Cursor** | `~/.cursor/skills/<name>/` | [Cursor Skills docs](https://cursor.com/docs/context/skills) — or run `/create-skill` in Agent chat |
| **Claude Code** | `~/.claude/skills/<name>/` or `.claude/skills/<name>/` | [Claude Code skills docs](https://code.claude.com/docs/en/skills) |
| **OpenAI Codex** | `~/.agents/skills/<name>/` or `.agents/skills/<name>/` (`~/.codex/skills/` legacy) | [Codex Agent Skills](https://developers.openai.com/codex/skills) — run **`$skill-creator`** in Codex to scaffold the port |
| **GitHub Copilot** | `~/.copilot/skills/<name>/` or `~/.agents/skills/<name>/`; project: `.github/skills/<name>/` or `.agents/skills/<name>/` | [Copilot: add skills](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-skills) |
| **Any agent (format reference)** | varies | [Agent Skills open spec](https://agentskills.io/specification) — shared `SKILL.md` frontmatter + body structure |

### Adaptation checklist

1. Read `SKILL.md` and linked detail files to understand the workflow.
2. Invoke your platform's skill-creation guide (table above) — do not hand-roll folder layout.
3. Map Cursor-only constructs: `AskQuestion` → interactive prompts; `Task` subagents → your platform's subagent/delegation model; `.physics-edit/` disk state paths → equivalent session storage.
4. Keep sibling install layout if using both micro + macro skills (`../physics-paper-editing/` links).
5. Test on a short LaTeX passage before relying on the full verifier pipeline.

## License

MIT — see [LICENSE](LICENSE).
