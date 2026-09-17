---
identifier: "PAP-39"
title: "Add full-text and vector search (tsvector + pgvector) over any entity through a search registry"
project: "data-layer"
projectName: "Data Layer & Database"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Customer", "Staff"]
milestone: "Local-first sync working"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-33", "PAP-34", "PAP-35", "PAP-43", "PAP-59", "PAP-228", "PAP-269"]
blocks: ["PAP-138"]
key: "data-layer/search"
url: "https://linear.app/paperos/issue/PAP-39/add-full-text-and-vector-search-tsvector-pgvector-over-any-entity"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:40:59.666Z"
model: "claude-sonnet-5"
effort: "high"
---

# PAP-39: Add full-text and vector search (tsvector + pgvector) over any entity through a search registry

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

One search API over any entity: packages register searchable fields once, Postgres keeps a `tsvector` and optional `pgvector` embedding current, and `search.query` returns ranked, tenant-scoped, permission-filtered results that the command bar, knowledge search and table filters reuse.

**Scope**

In:

* Registry `packages/search/src/registry.ts`: `registerSearchable({ entity, table, titleField, bodyFields, facets, weight, embed, route })`; core registrations `workspace`, `user`, `file`.
* Table `search_document` with `tsv` (GIN), `embedding vector(1024)` (HNSW), `pg_trgm` GIN on `title`, `facets jsonb`; RLS like any tenant table.
* Triggers calling `paperos.search_upsert(entity_type, id)`; embeddings via PAP-43 job through `EmbeddingProvider` (OpenAI-compatible endpoint, self-hosted `text-embeddings-inference` on staging).
* `search.query({ q, mode: 'keyword'|'semantic'|'hybrid', entityTypes?, facets?, limit })` with RRF fusion and a `can()` post-filter.
* `<SearchResults/>` in `@paperos/ui`.

Out: cross-source unification UI (PAP-138), command palette (PAP-151).

**Spec**

* Language `english` default; per-tenant `settings.search.language`; `simple` fallback.
* Body cap 100 KB with flag; model name stored per row; reindex when the model changes.
* Latency at 100k docs: keyword p95 under 80 ms, hybrid under 250 ms.
* Facets as jsonb containment; top 5 values per key returned.
* Soft-deleted rows drop their document.
* Registry validated at boot against Drizzle types and live columns.
* Bulk imports set `app.search_mode = 'deferred'` then reindex.

**Interface contract**

Provides (from `@paperos/search`):

* `registerSearchable(def)`, `SearchableDef` type, `search.query` procedure returning `{ items: [{ entityType, entityId, title, snippet, score, href, facets }], facetCounts }`.
* Job `search.embed` (PAP-43) and `EmbeddingProvider` interface `{ model, dims, embed(texts): Promise<number[][]> }`.
* Session var `app.search_mode` read by triggers.
* Component `SearchResults` with empty and error states.

Consumes: tables (PAP-33), RLS (PAP-34), API host (PAP-35), jobs (PAP-43), `can()` post-filter (PAP-59; allow-all stub until merged), `vector` and `pg_trgm` extensions (PAP-30, PAP-42).

**Definition of done**

* "acme" on the demo seed returns the Acme workspace and members ranked sensibly; "acmee" still finds it (recording).
* Semantic mode works against the staging embedding container.
* Vitest: registry validation, query builder, RRF; integration for triggers and post-filter (cross-tenant never appears).
* Bench at 100k docs committed.
* `<SearchResults/>` at 375, 768, 1280, 1920 including empty and error; `docs/data/search.md`; CHANGELOG; Linear comment.

**Test plan**

* Unit: registry rejects unknown columns and duplicate entities; RRF fusion determinism; query sanitiser for stop-word-only input.
* Integration (CI compose): insert, update, soft-delete a workspace and assert `search_document` follows; deferred mode batches; embeddings job with a fake provider.
* Permission: `callAs(tenantB)` never sees tenant A; `can()` denial removes a hit.
* Bench: `load` seed, keyword and hybrid p95 recorded.
* Visual: results, empty, error, loading at four widths.

**Demo**

Reviewer types "acme" into the search box on the dashboard, sees workspace and members grouped by type, misspells it as "acmee" and still gets the workspace, then switches to semantic mode and searches "billing team". Under a minute.

**Edge cases**

* Empty query returns recent items.
* Provider down: keyword results still return; job retries.
* Non-English content in `english` config documented; `simple` per tenant.
* Entity registered twice: boot error naming both packages.
* Very long titles truncated in snippets, full on hover.

**Dependencies**

PAP-33, PAP-43 (hard), PAP-34, PAP-35 and PAP-59 (now encoded). Consumed by PAP-138, PAP-151, PAP-166, PAP-189.

**Agent**

Built by Forge (Schema Wright) with Nova on hooks. Reviewed by Sentinel.

**Size**

M: registry, table, triggers, one procedure and a component.
