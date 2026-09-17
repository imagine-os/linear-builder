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
blockedBy: ["PAP-228", "PAP-269", "PAP-33", "PAP-34", "PAP-35", "PAP-43", "PAP-59"]
blocks: ["PAP-138"]
key: "data-layer/search"
url: "https://linear.app/paperos/issue/PAP-39/add-full-text-and-vector-search-tsvector-pgvector-over-any-entity"
source: "plan/specs/bucket-0.json (round-1 canonical spec JSON)"
---

# PAP-39: Add full-text and vector search (tsvector + pgvector) over any entity through a search registry

**Goal**

Provide one search API over any entity: packages register searchable fields once, Postgres keeps a `tsvector` and (optionally) a `pgvector` embedding up to date, and a single `search.query` procedure returns ranked, tenant-scoped, permission-filtered results that the command bar, knowledge search and table filters all reuse.

**Scope**

In:
- Search registry `packages/search/src/registry.ts`: `registerSearchable({ entity, table, titleField, bodyFields[], facets[], weight, embed: boolean, route: (row) => href })`; core entities registered: `workspace`, `user` (name/email), `file` (filename, metadata).
- Storage: a central `search_document` table (`tenant_id`, `entity_type`, `entity_id`, `title`, `body`, `tsv tsvector generated`, `embedding vector(1024)` nullable, `facets jsonb`, `updated_at`) with GIN on `tsv`, HNSW on `embedding`, `pg_trgm` GIN on `title` for fuzzy; RLS as any tenant table.
- Indexing: triggers on source tables call `paperos.search_upsert(entity_type, id)` which builds the document via per-entity SQL functions generated from the registry; a pg-boss job computes embeddings asynchronously via a provider interface (`EmbeddingProvider`: `openai-compatible` default pointing at a self-hosted `text-embeddings-inference` container or a paid API, chosen via env; provider can be `none`).
- Query: `search.query({ q, types?, facets?, limit, mode: 'keyword'|'semantic'|'hybrid' })` doing `websearch_to_tsquery('english')` ranking with `ts_rank_cd`, trigram fallback for short/misspelled queries, hybrid via reciprocal rank fusion; highlights via `ts_headline`.
- Permission filter hook: results pass through `identity/rbac-abac` `can(actor,'read',resource)` post-filter with over-fetch factor 3.
- `useSearch()` hook and `<SearchResults/>` list; command bar integration point for `input/command-registry`.
- Reindex CLI `pnpm search:reindex --entity workspace`.

Out: search UI design beyond a basic list, external search engines (Meilisearch/Typesense; note as future via registry), document content extraction (PDF text) beyond a hook.

**Spec**

- Language: `english` config default; per-tenant `settings.search.language` used in generated function.
- Body field length cap 100 KB per document; larger bodies truncated with flag.
- Embeddings: 1024-dim default (bge-m3 or `text-embedding-3-small` at 1024); model name stored per row so mixed models are never compared; reindex when model changes.
- Latency targets on `load` seed (100k docs): keyword p95 under 80 ms, hybrid p95 under 250 ms; bench committed.
- Facets: `jsonb` containment filters, e.g. `{ status: 'active' }`; counts returned for the top 5 facet values per key.
- Deleted/soft-deleted rows remove their document (trigger on `deleted_at`).
- Registry validation at boot fails if a registered field does not exist (typecheck via Drizzle types plus runtime check).

**Definition of done**

- Searching "acme" on demo seed returns the Acme workspace and its members ranked sensibly; typo "acmee" still finds it (trigram); recording attached.
- Semantic mode returns relevant results with the local embedding container on staging (or documented paid provider).
- Vitest: registry validation, query builder, RRF fusion; integration test for triggers and permission post-filter (cross-tenant never appears).
- Bench results at 100k docs committed.
- `<SearchResults/>` screenshots at 375, 768, 1280, 1920 including empty and error states.
- `docs/data/search.md` (how to register an entity); CHANGELOG; Linear comment with preview URL.

**Edge cases**

- Empty or whitespace query: return recent items instead of error.
- Queries with only stop words: trigram path.
- Non-English content in an `english` config: documented limitation; `simple` config fallback per tenant.
- Embedding provider down: keyword results still return; job retries.
- Entity registered twice by two packages: boot error naming both.
- Massive bulk import: triggers batch via `app.search_mode = 'deferred'` and a reindex afterwards.

**Dependencies**

`data-layer/core-entities` (hard), `data-layer/rls-tenancy`, `data-layer/api-layer`, `identity/rbac-abac` (post-filter; stub allow-all until merged). Consumed by `collab/knowledge-search`, `input/command-registry`, `tables/filter-sort-group-ui`, `growth/crm-views`.

**Agent**

Built by Forge (Schema Wright) with Nova consulting on hook shape. Reviewed by Sentinel (Code Reviewer, Edge Case Hunter for query edge cases).

**Size**

M: Postgres provides the engines; the registry, triggers and hybrid ranking are the work.
