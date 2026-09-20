# physics-paper-editing-section

Portable Agent Skill for editing a complete LaTeX physics or mathematics section,
or any passage longer than 12 sentences. It structures and chunks the section,
then invokes the sibling short-passage workflow for each draft-and-verify round.
The prose canon is [physics-paper-principles](https://github.com/Harrinive/physics-paper-principles).

## Install

Install all three public repositories as siblings under the portable Agent Skills
location:

```bash
git clone https://github.com/Harrinive/physics-paper-principles.git ~/.agents/skills/physics-paper-principles
git clone https://github.com/Harrinive/physics-paper-editing.git ~/.agents/skills/physics-paper-editing
git clone https://github.com/Harrinive/physics-paper-editing-section.git ~/.agents/skills/physics-paper-editing-section
```

Hosts may also discover skills from their own user or project paths. Preserve the
sibling layout: this parent imports the short-passage runtime contract and the
physics-writing canon.

## Runtime support

The runtime adapters live with the short-passage workflow and cover
[Cursor](../physics-paper-editing/runtime-cursor.md),
[OpenAI Codex](../physics-paper-editing/runtime-codex.md), and
[Claude Code](../physics-paper-editing/runtime-claude.md). The shared
[runtime contract](../physics-paper-editing/runtime-contract.md) defines the
confirmed session profile, concurrency waves, result shards, and resume rules.

## Entry point

Read [SKILL.md](SKILL.md), [stages.md](stages.md), and
[cross-skill.md](cross-skill.md). Stage A obtains the one session-level
model-profile choice unless it inherits a user-confirmed parent profile. Later
chunks reuse that profile without re-asking.

## License

MIT — see [LICENSE](LICENSE).
