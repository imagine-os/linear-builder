---
identifier: "PAP-757"
title: "Adopted-library usage notes: one `docs/libraries/notes/<id>.md` per adopted library with import conventions, banned APIs, gotchas and version pin, linted against the registry"
project: "libraries"
projectName: "Library Discovery & Integration"
phase: "P1"
type: "Docs"
priority: 2
surfaces: ["Developer"]
milestone: "Registry live"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-216"]
blocks: ["PAP-758", "PAP-763"]
key: "r4/libraries/library-usage-notes"
url: "https://linear.app/paperos/issue/PAP-757/adopted-library-usage-notes-one-docslibrariesnotesidmd-per-adopted"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:39.078Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 3
dueDate: "2026-09-30"
cycle: null
---

# PAP-757: Adopted-library usage notes: one `docs/libraries/notes/<id>.md` per adopted library with import conventions, banned APIs, gotchas and version pin, linted against the registry

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Docs M

**Goal**

The registry says what we adopted and why; it does not tell a cold session how to use it here: which import path, which APIs are off limits, which version quirk cost a day last time. Agent-friendliness is a rubric criterion for the library; this issue is the agent-friendliness of our adoption. One short note per adopted library, generated as a skeleton, filled by the adopting issue, linted so none is missing.

**Scope**

In: `docs/libraries/notes/<registryId>.md` with frontmatter `{ library, version (from lockfile), owner, adr, llmsTxt?, updated }` and fixed sections `Use it for`, `Import`, `Do not`, `Gotchas`, `Patterns` (links to our code), `Upgrade notes`; `pnpm lib notes scaffold <id>` writing the skeleton from the registry entry and facts (`docsUrl`, `llms.txt` when the package publishes one); registry check rule `adopted` without notes is a warning for 7 days then an error; notes rendered in the PAP-128 docs engine under Reference and included in `llms-full.txt` (PAP-727); the first twenty notes for the current production dependencies. Out: full API docs (link out), the registry itself.

**Spec**

* `Do not` lines are machine-readable: `- ban: lodash` or `- ban: moment#format` so PAP-758 can generate lint rules from them.
* Notes are under 400 words; `docs:lint` (PAP-128) enforces the section list and the word cap; `version` is refreshed by `pnpm lib registry build` and a stale note (version behind the lockfile by a major) is flagged `needs-review`.
* Skeleton fills `Use it for` from the registry `reasons`, `Import` from the package `exports` map (deep imports listed), `Upgrade notes` from PAP-217's last summary comment when one exists.
* The PAP-109 memory loader and PAP-92 playbook point sessions at `docs/libraries/notes/` before they write code against a library; PAP-105's `page-from-spec` skill lists the relevant notes for the components a spec uses.
* Twenty seed notes cover at least: react, @tanstack/router, @tanstack/react-query, drizzle-orm, zod, @orpc/server, better-auth, yjs, @hocuspocus/provider, @tiptap/core, @xyflow/react, tailwindcss, @base-ui-components/react (or the PAP-212 winner), vitest, playwright, pg-boss, electric-sql, biome, storybook, @modelcontextprotocol/sdk.

**Interface contract**

Provides: notes folder and frontmatter schema, `pnpm lib notes scaffold|check`, `ban:` grammar, registry check rule, twenty seed notes. Consumes: registry entries and facts (PAP-216, PAP-209), docs engine and lint (PAP-128), lockfile versions, Renovate summaries (PAP-217, soft). Consumed by: PAP-758, PAP-109 memory, PAP-92 playbook, PAP-105 skills, PAP-218 (notes for new adoptions), PAP-727.

**Definition of done**

* Twenty notes merged, lint clean, rendered in the docs engine (screenshots at 375 and 1280); a registry entry without notes trips the check on a fixture.
* Sentinel reviews five notes for accuracy against the current code; `docs/libraries/notes/README.md`; CHANGELOG entry; comments on PAP-92 and PAP-109.

**Test plan**

* Unit: skeleton generation from a fixture entry, section lint, `ban:` parsing, staleness detection.
* Integration: `pnpm lib registry check` with and without notes.
* E2E: none.

**Demo**

Run `pnpm lib notes scaffold @xyflow/react`, fill two gotchas, run `pnpm docs:lint`, open the note in `/_app/docs/reference/libraries`. Under two minutes.

**Edge cases**

* Library adopted but only used in `dev` context: notes still required, shorter template.
* Two registry entries for one npm scope (`@radix-ui/*` unified): one note per registry id with aliases.
* Note contradicts an ADR: lint cannot know; reviewer checklist item in PAP-79.

**Dependencies**

Hard: PAP-216. Soft: PAP-128, PAP-209, PAP-217, PAP-109, PAP-92, PAP-105.

**Agent**

Builder: Scout (Library Evaluator) with Quill. Reviewer: Sentinel (Code Reviewer) and Nova (accuracy of five notes).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 2 round-4 file keys in this description to Linear identifiers: `r4/collab/agent-readable-docs` = PAP-727, `r4/libraries/library-guardrails-lint` = PAP-758.
