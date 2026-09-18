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
blockedBy: ["PAP-104", "PAP-128", "PAP-287", "PAP-299", "PAP-713", "PAP-714", "PAP-716", "PAP-717"]
blocks: []
key: "agents/memory"
url: "https://linear.app/paperos/issue/PAP-109/give-characters-persistent-memory-project-notes-decisions-gotchas"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T13:56:29.613Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: "2026-09-25"
cycle: null
---

# PAP-109: Give characters persistent memory (project notes, decisions, gotchas) stored in the docs system and loaded at session start

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Stop characters repeating mistakes: each character and each project keeps a curated memory of notes, decisions and gotchas in the docs system, loaded into the prompt at session start and appended at session end, with token budgets and review so it stays useful instead of becoming a landfill.

**Scope**

* In: memory MDX files, the loader, the writer with auto-merge rules, pruning job, `docs/agents/memory.md`.
* Out: raw transcripts (PAP-107), decision records themselves (PAP-130), search (PAP-138 optional).

**Spec**

* Files: `docs/memory/characters/<name>.md`, `docs/memory/projects/<key>.md`, `docs/memory/global.md`; frontmatter `owner`, `linearProjectId`, `maxTokens`, `updated`, `pinned[]`.
* Sections: `## Working notes` (rolling), `## Decisions` (one line each linking ADRs), `## Gotchas`, `## Do not`, `## Open threads`. One bullet per item, max 300 characters, trailing provenance `(PAP-123, 2026-09-21)`.
* Loader `packages/agents/src/memory/load.ts`: assembles global, project, character in that order; trims to `memory.maxTokens` (default 6000, split 1000/2000/3000) dropping oldest working notes first, never pinned; deterministic output placed after the system prompt and before the issue body so prompt caching holds.
* Writer `write.ts`: a session ends with a fenced ```` ```paperos-memory ```` block of `add:` and `remove:` entries in its final comment; the orchestrator applies it on a `memory/<session>` branch; entries pass PAP-107 redaction; auto-merge when under five entries and lint passes, else a PR to Quill.
* Pruning weekly: entries whose referenced paths no longer exist are flagged for Quill.

**Interface contract**

* Provides: `loadMemory({ character, projectKey, maxTokens }): { markdown, tokens, dropped[] }`, `applyMemoryBlock(sessionId, block)`, Zod `MemoryEntry`, the `paperos-memory` block grammar, git author convention `Forge (agent) <forge@paperos.bot>`.
* Consumers: PAP-96 prompt rendering calls `loadMemory`; PAP-105 `linear-update` validates the memory block; PAP-112 links memory files per character; PAP-110 checks that a second session used a recorded gotcha; PAP-128 renders the pages.
* Requires: PAP-104 `memory` field, PAP-128 docs engine (repo markdown fallback), PAP-130 for decision links, PAP-107 `redact`.

**Definition of done**

* Loader tests: trimming order, pinned preservation, missing files, token estimate within 10 percent of `count_tokens` on five samples.
* Writer tests: apply add and remove, reject over-long or provenance-less entries, auto-merge threshold.
* Live: two consecutive Forge sessions; the second's transcript uses a gotcha from the first (excerpt in comment).
* Memory pages render with "last updated by"; screenshots at 375 and 1280 px.
* Docs page; changelog; Linear comment with excerpt and screenshots.

**Test plan**

* Unit: loader determinism (same files, same bytes), split budgets, provenance parsing, redaction pass-through.
* Integration: writer against a temp git repo with concurrent branches rebasing (order-independent bullets).
* e2e: two-session live run on staging.
* Visual: docs engine memory page at 375 and 1280 px.

**Demo**

Run `pnpm memory load --character forge --project data-layer` and read the assembled block with token count; append a gotcha through `pnpm memory apply fixtures/block.md`, re-run load and see it first. One minute.

**Edge cases**

* Concurrent updates: later branch appends rather than fails.
* Entry containing a secret: redacted entries dropped with a note.
* No memory file yet: empty template created on first write.
* Only pinned entries exceed budget: warn in `/status`; Quill curates.
* Project renamed: keyed by Linear project id in frontmatter.

**Dependencies**

Blocked by PAP-104, PAP-128. Soft: PAP-130, PAP-138.

**Agent**

Built by Quill (Prompt Logger sub-agent) with Atlas wiring the loader; reviewed by Sentinel.

**Size**

M
