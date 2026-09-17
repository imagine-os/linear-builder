---
identifier: "PAP-109"
title: "Give characters persistent memory (project notes, decisions, gotchas) stored in the docs system and loaded at session start"
project: "agents"
projectName: "Agent Characters & Orgs"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Agent"]
milestone: "Sub-agents, skills and evals live"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-104", "PAP-128"]
blocks: []
key: "agents/memory"
url: "https://linear.app/paperos/issue/PAP-109/give-characters-persistent-memory-project-notes-decisions-gotchas"
source: "plan/specs/bucket-3.json (round-1 canonical spec JSON)"
---

# PAP-109: Give characters persistent memory (project notes, decisions, gotchas) stored in the docs system and loaded at session start

**Goal**

Stop characters from repeating mistakes: each character (and each project) keeps a curated memory of notes, decisions and gotchas in the docs system, loaded into the session prompt at start and appended to at session end, with size limits and review so it stays useful rather than becoming a landfill of transcripts.

**Scope**

In:
- Memory files as MDX in the docs engine: `docs/memory/characters/<name>.md` (one per character, lead and sub), `docs/memory/projects/<project-key>.md` (one per Linear project), and `docs/memory/global.md` (org-wide gotchas), each with frontmatter (`owner`, `maxTokens`, `updated`).
- Structure inside each file: `## Working notes` (rolling, pruned), `## Decisions` (links to ADRs from `collab/decision-log`, one line each), `## Gotchas` (repo, tool and API traps with the fix), `## Do not` (explicit prohibitions learned the hard way), `## Open threads`.
- Loader `packages/agents/src/memory/load.ts`: given character and issue (project key from Linear), assembles global, project and character memory in that order, trims to the character's `memory.maxTokens` (default 6000; measured with the token-count endpoint or a cached estimate) by dropping oldest working notes first, and returns markdown the orchestrator injects into the session prompt under a `# Memory` heading.
- Writer path: at session end the session proposes memory updates in a fenced ` ```memory-update ` block (`add`/`remove` entries with section and text); the `linear-update` skill posts it in the footer and the orchestrator applies it as a commit to `docs/memory/**` on a `memory/<session>` branch merged automatically when the diff is under 40 lines and touches only memory files; larger diffs open a PR reviewed by Quill's Prompt Logger.
- Pruning job (weekly, Quill): merges duplicates, moves stale working notes to `docs/memory/archive/`, checks every gotcha still applies (linked file or command exists).
- Search: memory files indexed by `data-layer/search` so a session can query `memory: "drizzle enum migration"` through the docs engine API.

Out: vector long-term memory, per-user memory, transcript storage (`collab/prompt-log-store`), automatic extraction from transcripts (a later Prompt Logger routine).

**Spec**

- Entry format is one bullet per item, max 300 characters, with a trailing `(PAP-123, 2026-09-21)` provenance; the loader strips provenance when trimming to save tokens but keeps it in the file.
- Token budget split default: global 1000, project 2000, character 3000; configurable per character in the schema (`memory.maxTokens`).
- Loader output is deterministic for a given file state so prompt caching (`pm-linear/orchestrator`) benefits: memory goes after the stable system prompt and before the issue body.
- Frontmatter `pinned: true` entries are never trimmed.
- All writes attributed to the character principal in git author (`Forge (agent) <forge@paperos.bot>`).

**Definition of done**

- Loader tests: trimming order, pinned preservation, missing files, token estimate within 10 percent of `count_tokens` on 5 samples.
- Writer tests: apply add/remove blocks, reject entries over 300 characters or without provenance, auto-merge threshold.
- Live run: two consecutive sessions of Forge on related issues; the second session's transcript shows it used a gotcha recorded by the first (transcript excerpt in the comment).
- Memory pages render in the docs engine with a "last updated by" line; screenshot at 375 and 1280 px.
- `docs/agents/memory.md` explains structure, budgets, pruning; changelog entry; Linear comment with the excerpt and screenshots.

**Edge cases**

- Two sessions update the same memory file concurrently: memory branches rebase; on conflict the later one appends rather than fails (entries are order-independent bullets).
- A session proposes a memory entry containing a secret: the redaction from `agents/prompt-logging-hook` runs on the block; redacted entries are dropped with a note.
- Gotcha becomes wrong after a refactor: pruning job flags entries whose referenced paths no longer exist; Quill confirms removal.
- Character has no memory file yet: loader creates an empty template on first write; no failure on read.
- Memory grows past budget with only pinned entries: loader warns in `/status`; Quill must curate.
- Project key changes (project renamed): memory keyed by Linear project id in frontmatter, filename is a slug.

**Dependencies**

- `agents/roster-v1` (character list and `memory` schema field).
- `collab/docs-engine` (MDX storage, rendering, versioning); `collab/decision-log` for decision links; `data-layer/search` optional.

**Agent**

Built by Quill (Prompt Logger sub-agent) with Atlas wiring the loader into the orchestrator; reviewed by Sentinel (Code Reviewer) and Forge as a consuming character.

**Size**

M: loader, writer, auto-merge rule and a two-session proof.
