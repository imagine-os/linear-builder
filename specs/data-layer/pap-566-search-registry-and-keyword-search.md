---
identifier: "PAP-566"
title: "Search registry and keyword search: `registerSearchable`, `search_document` with tsvector and trigram indexes, upsert triggers, deferred mode and `search.query` keyword mode with facets and `can()` post-filter"
project: "data-layer"
projectName: "Data Layer & Database"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Customer"]
milestone: "Local-first sync working"
state: "Backlog"
parent: "PAP-39"
children: []
blockedBy: ["PAP-33", "PAP-34", "PAP-35", "PAP-43", "PAP-59", "PAP-228", "PAP-229", "PAP-268", "PAP-269", "PAP-564", "PAP-565"]
blocks: ["PAP-138", "PAP-567"]
key: "r4/data-layer/search-keyword"
url: "https://linear.app/paperos/issue/PAP-566/search-registry-and-keyword-search-registersearchable-search-document"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:09.268Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: "2026-09-25"
cycle: null
---

# PAP-566: Search registry and keyword search: `registerSearchable`, `search_document` with tsvector and trigram indexes, upsert triggers, deferred mode and `search.query` keyword mode with facets and `can()` post-filter

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

First child of PAP-39: the part the command bar (PAP-151), knowledge search (PAP-138) and table filters (PAP-166) need before any embeddings exist. Packages register searchable entities once, triggers keep a `tsvector` and trigram title current, and `search.query` returns ranked, tenant-scoped, permission-filtered results with facet counts.

**Scope**

In: `packages/search/src/{registry,query,sanitize}.ts`, table `search_document (tenant_id, entity_type, entity_id, title, body, tsv, facets jsonb, route, updated_at)` with GIN on `tsv`, `pg_trgm` GIN on `title`, RLS; SQL function `paperos.search_upsert(entity_type, id)` and generated triggers; session var `app.search_mode` for deferred bulk imports; `search.query` keyword mode; core registrations `workspace`, `user`, `file`; `docs/data/search.md`.

Out: Embeddings, semantic and hybrid modes, `<SearchResults/>` (sibling PAP-567), cross-source UI (PAP-138), command palette (PAP-151).

**Spec**

* `registerSearchable({ entity, table, titleField, bodyFields, facets, weight, route })` validated at boot against Drizzle types and live columns; duplicate entity names error naming both packages.
* Language `english` default, per-tenant `settings.search.language`, `simple` fallback; body capped at 100 KB with a `truncated` flag; soft-deleted rows drop their document.
* `search.query({ q, entityTypes?, facets?, limit })` ranks with `ts_rank_cd` plus a trigram similarity boost on title; returns `{ items: [{ entityType, entityId, title, snippet, score, href, facets }], facetCounts }` with `ts_headline` snippets; empty query returns recent items.
* `can()` post-filter (PAP-229) drops hits the actor may not read; over-fetch factor 3 with a second page when filtering removes too many.
* Deferred mode: `SET LOCAL app.search_mode = 'deferred'` makes triggers enqueue ids into `search_pending`; `search.reindex(entity)` drains it (job in the sibling when PAP-43 is present, inline otherwise).
* Latency at 100k documents: keyword p95 under 80 ms on the `load` seed; bench committed.

**Interface contract**

Provides: `registerSearchable`, `SearchableDef`, `search.query` (keyword mode), `search.reindex`, table and triggers, session var `app.search_mode`, `search_pending`.

Consumes: Tables (PAP-33), RLS (PAP-34), routers (PAP-268), `can()` (PAP-229), `pg_trgm` (PAP-30, PAP-42). Consumed by PAP-138, PAP-151, PAP-166, PAP-189 and the sibling.

**Definition of done**

* "acme" on the demo seed returns the Acme workspace and members ranked sensibly; "acmee" still finds it (recording).
* Insert, update, soft-delete a workspace and `search_document` follows; deferred mode batches and reindex drains (integration).
* `callAs(tenantB)` never sees tenant A; a `can()` denial removes a hit; bench at 100k documents committed.
* `docs/data/search.md`; CHANGELOG; Linear comment with the recording.

**Test plan**

* Unit: registry rejects unknown columns and duplicates, query sanitiser for stop-word-only and operator injection, facet containment builder, over-fetch loop termination.
* E2E: CI compose: seed `demo`, query through `callAs` for two tenants, assert isolation and ranking of the fixture terms.

**Demo**

Reviewer runs `pnpm tsx examples/search.ts acme` and `... acmee`, sees the same top hit, then registers a scratch entity and watches boot validation reject a misspelled column. Under a minute.

**Edge cases**

* Non-English content under `english`: documented; `simple` per tenant.
* Very long titles: snippet truncated, full title returned separately.
* Entity registered twice from two packages: boot error naming both.
* Trigger storm on bulk import: deferred mode required by PAP-199; documented in the import engine.

**Dependencies**

Blocked by PAP-33, PAP-268, PAP-229 (hard). Soft: PAP-34, PAP-30, PAP-42, PAP-43. Blocks PAP-138; the sibling PAP-567 builds on it.

**Agent**

Builder: Forge (Schema Wright). Reviewer: Sentinel (Code Reviewer).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/data-layer/search-semantic` = PAP-567.
