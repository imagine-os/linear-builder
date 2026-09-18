---
identifier: "PAP-835"
title: "Build permission-filtered retrieval over the search registry: chunking of records, docs, comments and files, hybrid ranking, citations and freshness"
project: "assistant"
projectName: "Tenant AI Assistant & Business Agents"
phase: "P2"
type: "Build"
priority: 2
surfaces: ["Staff"]
milestone: "Assistant contract and grounded chat"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-39", "PAP-43", "PAP-59", "PAP-228", "PAP-565", "PAP-567", "PAP-833", "PAP-834"]
blocks: ["PAP-837", "PAP-841", "PAP-846"]
key: "r4/assistant/retrieval-grounding"
url: "https://linear.app/paperos/issue/PAP-835/build-permission-filtered-retrieval-over-the-search-registry-chunking"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:51:48.843Z"
model: "claude-opus-5"
effort: "high"
estimate: 3
dueDate: "2026-10-01"
cycle: null
---

# PAP-835: Build permission-filtered retrieval over the search registry: chunking of records, docs, comments and files, hybrid ranking, citations and freshness

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Build M

**Goal**

Make the assistant answer from the tenant's own data without ever leaking a row the asker cannot read: a `RetrievalPort` that chunks searchable entities registered with PAP-39, keeps embeddings current through jobs, filters candidates by the human's PAP-228 SQL predicate before ranking, and returns chunks with `EntityRef` citations the UI can deep-link.

**Scope**

In: `packages/assistant/src/retrieval/`: `chunker` per entity kind (record → field-labelled text under 400 tokens; doc/comment → heading-aware chunks with overlap; file → extracted text from PAP-37 `text/*`, PDF via `pdf-parse`); table `assistant_chunk(entity_type, entity_id, chunk_ix, text, tsv, embedding vector(1024), acl_hint jsonb, updated_at)` with RLS. Freshness: PAP-39 `paperos.search_upsert` trigger also enqueues `assistant.chunk` (PAP-43) with `singletonKey` per entity; deletes cascade; nightly reconcile job. `ground(query, principal, { scopes, k, entityTypes })`: candidate set = `search.query(mode: hybrid)` top 50 ∩ rows visible under `compilePredicate(principal)` (PAP-228), re-ranked by reciprocal rank fusion plus recency; returns `Chunk[]` with `Citation` shapes and a `groundingReport` (counts filtered by permission, latency). `assistant.debugGrounding` procedure (staff `assistant.debug` permission) showing what was retrieved and what permission filtering removed, for support and Sentinel.

Out: Embedding provider hosting (PAP-39). Chunking of Yjs canvases (v0.3). Cross-tenant knowledge (never).

**Spec**

* Permission filtering happens in SQL (`WHERE` predicate from PAP-228 joined on the source table), not in application code, so a bug in ranking cannot leak; `acl_hint` is an optimisation only and never trusted
* Chunk text is stored redacted for `pii: secret` columns (PAP-355 annotations) and never for `encrypted()` columns (PAP-353)
* Top-k default 8, hard cap 20; total grounding budget 3k tokens; the report lists dropped chunks
* Citations carry `entityRef`, `route` (from the PAP-39 registry), `quote` (first 160 chars) and `score`; the UI renders them as chips that open the record panel (PAP-333) or doc
* Portal principals see only entities whose registry entry declares `audiences: [customer]` and pass the same predicate

**Interface contract**

Provides: `RetrievalPort` implementation, `assistant_chunk` table and jobs, `assistant.debugGrounding` procedure, `Chunk`/`groundingReport` fixtures for conformance. Consumes: search registry and `search.query` (PAP-39), `compilePredicate` (PAP-228), permission engine (PAP-59), jobs (PAP-43), files text extraction (PAP-37), `pii` annotations (PAP-355). Consumed by: PAP-836, PAP-837, PAP-841, engagement help center answers.

**Definition of done**

* Chunks exist for every registered entity type in the demo tenant within 60 s of a write; `ground()` p95 under 400 ms on the 100k-row benchmark dataset (PAP-337)
* Leak test: a principal restricted by an attribute policy to `region = EU` never receives a chunk from a US row across 1,000 randomised queries
* Grounding report visible in the debug procedure and attached to the prompt-log session (PAP-129)
* Every new page has a `page.spec.yaml` (PAP-114) that passes the validator, declared loading, empty, error and denied states, and Gate 3 screenshots at 375, 768, 1024 and 1920 in light and dark themes.
* Linear comment on the issue with the evidence links (PR, gate artefacts, recording or report) and the module docs page updated where the interface changed.

**Test plan**

* Unit: chunker boundaries (headings, 400-token cap, overlap), citation quote extraction, RRF ranking order with ties.
* Integration: trigger → job → chunk row; delete cascades; predicate filtering against three audiences (admin, staff with attribute policy, customer).
* Property: fast-check: for random principals and rows, every returned chunk's source row is readable via a direct `can()` call.
* Isolation: the PAP-34 cross-tenant harness auto-enrols every new table; one negative case per new oRPC procedure proves `NOT_FOUND` on a foreign tenant row.

**Demo**

Ask the debug procedure "what did we promise Acme?" as a sales rep and as a support agent; show the two grounding reports differ only by permission filtering and every citation opens the source record.

**Edge cases**

* Entity with 50k characters (a long doc): chunked into ≤120 chunks; embedding job batches 50 per call and resumes on failure
* Search registry entry without a `route`: citation renders without a link and the registry lint (PAP-39) warns the owner
* Embedding provider down: keyword-only grounding with a `degraded: true` flag in the report
* Module disabled for the tenant (PAP-266): routes return `MODULE_DISABLED` (409), slot fills unmount and the manifest declares the dependency so consumers fail closed rather than half-render.

**Dependencies**

PAP-834 (hard), PAP-39 (hard), PAP-228 and PAP-59 (hard), PAP-43 (hard), PAP-37 and PAP-355 (soft).

**Agent**

Builder: Nova. Reviewer: Sentinel (Security Auditor).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 4 round-4 file keys in this description to Linear identifiers: `r4/assistant/conversation-runtime` = PAP-836, `r4/assistant/model-and-provider-port` = PAP-834, `r4/assistant/portal-assistant` = PAP-841, `r4/assistant/staff-chat-panel` = PAP-837.
