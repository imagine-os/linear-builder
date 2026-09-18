---
identifier: "PAP-735"
title: "Ask PaperOS: retrieval-augmented answers over docs, ADRs, specs and journals with citations, from the command palette"
project: "collab"
projectName: "In-App Collaboration & Knowledge"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Staff"]
milestone: "Knowledge surfaced everywhere"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-39", "PAP-138", "PAP-567"]
blocks: []
key: "r4/collab/ask-paperos"
url: "https://linear.app/paperos/issue/PAP-735/ask-paperos-retrieval-augmented-answers-over-docs-adrs-specs-and"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:33.348Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 3
dueDate: null
cycle: null
---

# PAP-735: Ask PaperOS: retrieval-augmented answers over docs, ADRs, specs and journals with citations, from the command palette

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build M

**Goal**

Deferred to v0.2 (Execution Schedule stretch pool; NJ-14 can reinstate). Not claimable before 10-01.

PAP-138 lists Q&A chat as out of scope. Once the corpus is searchable, the obvious next step is the Intercom-style 'ask a question' that answers from docs, ADRs, specs and build journals with citations, for staff in-app and for agents through the docs MCP tool.

**Scope**

In: oRPC `ask.query({ q, kinds?, audience })` in `packages/collab/ask/`: hybrid retrieval through PAP-39 (`k=12`), one Claude call with a fixed answer prompt and the retrieved chunks, streamed answer with `[n]` citations resolved to routes; palette command `ask.open` (PAP-151) and `/_app/ask` page with history per user; MCP tool `mcp__paperos-docs__ask` (extends PAP-727); per-tenant daily budget and a `feedback` thumbs pair stored with the question. Out: writing docs from answers, external web search, customer-facing chat (PAP-197).

**Spec**

* Retrieval respects PAP-138's audience allowlist; customers are never offered the feature in v0.2 scope.
* Answer prompt forbids claims without a citation; an answer with zero retrieved chunks returns 'no source found' and the top three search hits instead.
* Chunking: docs by heading (PAP-128 `data-block-id`), specs by section, journals by section; embeddings through PAP-39's pgvector registration.
* Cost: `claude-sonnet-5`, 4k input cap, 600 output tokens, tenant budget default 200 questions per day, logged to the prompt log as character `Quill` sub-agent `Librarian` (PAP-129).
* Latency budget p95 under 6 s streamed; first token under 1.5 s.

**Interface contract**

Provides: `ask.query`, `/_app/ask`, command `ask.open`, MCP tool `ask`, table `ask_question(tenant_id, actor, q, answer, citations, feedback)`. Consumes: `search.query` and pgvector (PAP-39, PAP-138), docs block ids (PAP-128), journals (PAP-728), palette (PAP-151), prompt log ingest (PAP-129), budgets (PAP-111). Consumed by: PAP-109 memory (answers as candidates), PAP-380 help panel ('Ask a question' upgrade).

**Definition of done**

* Ten golden questions over the seeded corpus answered with correct citations (Vitest with recorded model responses); zero-source case handled.
* Screenshots at 375 and 1280 in light and dark; axe clean; `docs/collab/ask.md`; CHANGELOG entry.

**Test plan**

* Unit: chunking per source kind, citation resolution, budget enforcement, zero-source fallback.
* Integration: audience allowlist enforced for staff without `staff.admin` (no `prompt_session` chunks).
* E2E (Playwright): ask from the palette, click a citation, land on the doc block.

**Demo**

Press `mod+k`, type `? how do comments anchor to a doc block`, read the streamed answer, click citation \[1\]. Under one minute.

**Edge cases**

* Model unavailable: falls back to search results with a notice.
* Question contains a secret-looking token: redacted before storage (PAP-129 redactor).
* Corpus re-indexed mid-answer: citations resolved by block id, not offset.

**Dependencies**

Hard: PAP-138, PAP-39. Soft: PAP-728, PAP-727, PAP-151, PAP-129, PAP-111. Deferred: v0.2.

**Agent**

Builder: Nova with Quill on the prompt. Reviewer: Sentinel (Security Auditor for audience leakage).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 2 round-4 file keys in this description to Linear identifiers: `r4/collab/agent-readable-docs` = PAP-727, `r4/collab/build-journals` = PAP-728.
