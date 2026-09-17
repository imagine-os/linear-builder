---
identifier: "PAP-138"
title: "Unify search across docs, comments, specs, prompt logs and issues"
project: "collab"
projectName: "In-App Collaboration & Knowledge"
phase: "P2"
type: "Build"
priority: 2
surfaces: ["Staff"]
milestone: "Knowledge surfaced everywhere"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-128", "PAP-39"]
blocks: []
key: "collab/knowledge-search"
url: "https://linear.app/paperos/issue/PAP-138/unify-search-across-docs-comments-specs-prompt-logs-and-issues"
source: "plan/specs/bucket-4.json (round-1 canonical spec JSON)"
---

# PAP-138: Unify search across docs, comments, specs, prompt logs and issues

**Goal**

One search box over everything the organisation knows: docs, ADRs, page specs, comments, prompt sessions, rules and skills, and Linear-mirrored issues, with hybrid keyword and vector ranking, facets by kind, audience-safe results and actions on each hit. Reachable from the command palette on every page.

**Scope**

In:
- Registrations through `data-layer/search` `registerSearchable(...)` in `packages/collab/search/registrations.ts`: `doc` (title, body from MDX text, facets `audience`, `tags`, `owner`; route `/_app/docs/<slug>`), `adr` (from `collab/decision-log` index; facets `status`, `tags`), `page_spec` (title, purpose, route, edge-case text; facets `surface`, `status`, `owner`; route to `spec-builder/spec-editor-ui`), `comment` (body_text with thread anchor label; facets `status`, `anchorType`; route deep link with `?thread=`), `prompt_session` (issue key, character, summary; facets `character`, `status`; route to `collab/prompt-log-ui`), `rule_skill` (from `collab/rules-skills-registry`), `issue` (from `pm-linear/pm-data-model` mirror; facets `state`, `project`, `labels`; route to the issue page and Linear URL).
- Indexers: build-time script `pnpm search:index-static` for docs, ADRs, specs and rules (rows owned by the platform tenant, re-run on deploy with hash-based upserts and deletion of vanished paths); database triggers already provided by the search registry for comments and issues; prompt sessions indexed on `ended_at` set by `collab/prompt-log-store` with a summary generated once by a Claude call (200 words, redaction-safe) stored in `prompt_session.summary`.
- oRPC `search.query({ q, kinds?, facets?, cursor, mode: hybrid|keyword })` wrapping the registry's search function with audience filtering (RLS plus a `kinds` allowlist per audience: customers get `doc` and `changelog` only; staff get all but `prompt_session` and `rule_skill` unless `staff.admin`).
- UI: command palette provider registered with `input/command-registry` (`Cmd/Ctrl+K`, "Search everything" mode with grouped top results and "see all"), and `/_app/search?q=&kinds=` page with result list, facet sidebar (kind, owner, status, surface, date), keyboard navigation, snippets with highlighted matches, per-result actions (open, copy link, comment, open in Linear or Forgejo); recent searches per user in `localStorage`.
- `search:reindex --kind <k>` admin command and a `/_app/dev/search-health` page showing document counts per kind, last index time and stale counts.

Out: the search engine itself (`data-layer/search`), external search over Notion or Drive (imports later), semantic Q&A chat.

**Spec**

- Snippets from `ts_headline` with 160-character windows; vector results fall back to the first matching sentence.
- Ranking: registry hybrid score plus recency boost for comments and issues (half-life 30 days) and a kind weight (`doc` 1.0, `page_spec` 0.9, `issue` 0.9, `comment` 0.7, `prompt_session` 0.6).
- Queries under 2 characters return recents; operators `kind:doc`, `owner:Quill`, `is:open` parsed client-side into facets.
- Latency: p95 under 300 ms for hybrid on 100k documents; palette shows results after 150 ms debounce.
- Audit: searches are not logged with text, only counts per kind (privacy).

**Definition of done**

- Vitest: registrations validate at boot, operator parsing, kind allowlist per audience, ranking weights.
- Seeded corpus (500 docs, 50 specs, 2k comments, 300 sessions, 1k issues): Playwright searches from the palette and the page, filters by facet, opens a result of each kind; customer actor sees only allowed kinds; screenshots at 320, 375, 768, 1024, 1280, 1536 and 1920 in light and dark.
- Benchmark committed showing p95 under 300 ms.
- axe clean for palette and results; `docs/collab/search.md` including how to register a new kind; CHANGELOG entry; Linear comment with screenshots and benchmark.
- Justin finds a prompt session by issue key from the palette (video).

**Edge cases**

- Same document indexed twice after a rename: static indexer deletes by vanished path before upsert.
- Comment visibility `internal` and a customer search: RLS excludes it even if the kind were allowed.
- Prompt summary generation fails: session indexed with issue key and character only.
- Very long query (2k characters): truncated to 500 with a notice.
- Vector model changed: registry marks rows stale; health page shows the count; keyword still works.
- Command registry not merged: a temporary global `Cmd/Ctrl+K` handler is installed with a TODO.

**Dependencies**

`data-layer/search` and `collab/docs-engine` (hard). Soft: `collab/decision-log`, `collab/comments`, `collab/prompt-log-store`, `collab/rules-skills-registry`, `pm-linear/pm-data-model`, `input/command-registry`. Consumed by `agents/memory` (characters query it at session start).

**Agent**

Built by Nova (Views Engineer) with Forge (Schema Wright) on indexers. Reviewed by Sentinel (Security Auditor for audience leakage, Visual Inspector) and Quill.

**Size**

M: registry does the heavy lifting; seven registrations, indexers and the palette UI remain.
