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
blockedBy: ["PAP-39", "PAP-128"]
blocks: []
key: "collab/knowledge-search"
url: "https://linear.app/paperos/issue/PAP-138/unify-search-across-docs-comments-specs-prompt-logs-and-issues"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T04:53:30.141Z"
---

# PAP-138: Unify search across docs, comments, specs, prompt logs and issues

**Goal**

One search box over everything the organisation knows: docs, ADRs, page specs, comments, prompt sessions, rules and skills and mirrored issues, with hybrid ranking, facets, audience-safe results and actions per hit, reachable from the command palette on every page.

**Scope**

In:

* Registrations in `packages/collab/search/registrations.ts` through PAP-39 `registerSearchable`: `doc`, `adr`, `page_spec`, `comment`, `prompt_session`, `rule_skill`, `issue`, each with title, body, facets and route builder.
* Indexers: `pnpm search:index-static` for docs, ADRs, specs and rules (hash upserts, delete vanished paths); registry triggers for comments and issues; prompt sessions on `ended_at` with a one-time 200-word Claude summary stored in `prompt_session.summary`.
* oRPC `search.query({ q, kinds?, facets?, cursor, mode })` wrapping the registry with an audience allowlist (customers: `doc`, `changelog`; staff: all but `prompt_session` and `rule_skill` unless `staff.admin`).
* UI: PAP-151 palette provider (`mod+k` "Search everything" with grouped top results) and `/_app/search` with facets, keyboard navigation, highlighted snippets and per-result actions; recents in `localStorage`.
* Admin `search:reindex --kind` and `/_app/dev/search-health`.

Out: the engine (PAP-39), external sources, Q&A chat.

**Spec**

* Snippets via `ts_headline`, 160 characters; vector hits fall back to the first matching sentence.
* Ranking: registry hybrid score, recency half-life 30 days for comments and issues, kind weights `doc` 1.0, `page_spec` 0.9, `issue` 0.9, `comment` 0.7, `prompt_session` 0.6.
* Operators `kind:`, `owner:`, `is:open` parsed client-side.
* p95 under 300 ms hybrid on 100k documents; 150 ms debounce.
* Only counts per kind are logged, never query text.

**Interface contract**

Exposes: `search.query` result `{ hits: [{ kind, id, title, snippet, route, facets, score }], facets: { kind: [{ value, count }], ... }, cursor }`; `SearchProvider` and `useSearch()`; palette command `search.open`; `registerSearchKind()` docs for module authors (PAP-28 modules register their own kinds); health page JSON. Consumes: `registerSearchable`, `search()` and `ts_headline` helpers from PAP-39; `renderMdx` text extraction from PAP-128; `adr-index.json` (PAP-130); `rules-index.json` (PAP-134); `comment` tables (PAP-131); `prompt_session` (PAP-129); PM mirror tables (PAP-100); `CommandPalette` provider slot (PAP-151).

**Definition of done**

* Seeded corpus (500 docs, 50 specs, 2k comments, 300 sessions, 1k issues) searchable from palette and page; customer actor sees only allowed kinds.
* Screenshots at 320, 375, 768, 1024, 1280, 1536 and 1920 in light and dark; benchmark committed with p95 under 300 ms.
* axe clean; `docs/collab/search.md` including how to register a kind; CHANGELOG entry; Linear comment with screenshots and benchmark; video of Justin finding a session by issue key.

**Test plan**

* Vitest: registrations validate at boot, operator parsing, allowlist per audience, ranking weights and recency boost, static indexer deletes vanished paths.
* Integration (Postgres with pgvector in CI): seeded corpus; `callAs(customer)` never returns `internal` comments even with `kinds: ['comment']`; reindex of one kind leaves others untouched.
* Benchmark: k6 or Vitest bench, 200 hybrid queries on the 100k corpus, p95 asserted under 300 ms; JSON committed.
* Playwright: `mod+k`, type "PAP-129", open the prompt session hit; on `/_app/search` filter by facet and open one result of each kind; run at 375 and 1280.
* Visual: Gate 3 baselines for palette and results page at the seven widths, both themes.

**Demo**

Press `mod+k`, type “Hocuspocus”, see grouped hits across docs, ADRs and comments, press `Enter` on the ADR; open `/_app/search?q=PAP-140`, filter to prompt sessions, open one and land in the replay. Under two minutes.

**Edge cases**

* Renamed doc: deleted by vanished path before upsert.
* Summary generation fails: session indexed by issue and character only.
* 2k-character query: truncated to 500 with a notice.
* Vector model changed: rows marked stale on the health page; keyword still works.
* Registry unmerged: temporary global `mod+k` handler with a TODO.

**Dependencies**

PAP-39, PAP-128 (hard, encoded). Soft: PAP-130, PAP-131, PAP-129, PAP-134, PAP-100, PAP-151. Consumed by PAP-109.

**Agent**

Built by Nova (Views Engineer) with Forge (Schema Wright) on indexers. Reviewed by Sentinel (Security Auditor for audience leakage, Visual Inspector) and Quill.

**Size**

M: the registry does the heavy lifting; seven registrations, indexers and the palette UI remain.
