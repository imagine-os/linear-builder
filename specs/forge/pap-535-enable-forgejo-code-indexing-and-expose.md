---
identifier: "PAP-535"
title: "Enable Forgejo code indexing and expose `forge.search` in `ForgePort` for the in-app repo browser and agent sessions"
project: "forge"
projectName: "Version Control & Forge Independence"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Developer"]
milestone: "Disaster recovery proven"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-273", "PAP-449"]
blocks: []
key: "r4/forge/code-search"
url: "https://linear.app/paperos/issue/PAP-535/enable-forgejo-code-indexing-and-expose-forgesearch-in-forgeport-for"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:03.557Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: null
cycle: null
---

# PAP-535: Enable Forgejo code indexing and expose `forge.search` in `ForgePort` for the in-app repo browser and agent sessions

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

Deferred to v0.2 (past 2026-10-01). GitHub code search is what agents reach for when a symbol moves; PAP-138 unifies search over docs, comments, specs and issues but not code, and the deferred in-app browser (PAP-277) has no search box. Forgejo ships a bleve indexer; exposing it through the contract gives both the UI and the sessions one search API.

**Scope**

In:

* `app.ini` `[indexer] REPO_INDEXER_ENABLED=true` with bleve on a named volume; sizing documented (PAP-273 host memory).
* `ForgePort.search(query, { repo?, path?, lang? })` added to `@paperos/contract-forge` as a minor bump with fixtures; Forgejo adapter over `/api/v1/repos/{owner}/{repo}/search`; the GitHub adapter (PAP-554) marks it `unsupported`.
* PAP-138 registers a `code` source; PAP-277 gets a search box; the `review-pr` skill (PAP-105) may call `forge.search` for symbol lookups.
* oRPC procedure `forge.search` (PAP-276 shape) guarded by `can(actor, "forge.read", { repo })`, with a 30 s cache keyed by query and index timestamp; `paperos forge search <query>` CLI for sessions without the UI.
* Conformance: two search fixtures (single repo, org-wide) added to `@paperos/contract-forge/conformance` with the `unsupported` path exercised by the GitHub double.

Out: semantic code search, cross-repo refactoring tools.

**Spec**

* Search respects `forge.read` (PAP-276) per repo.
* Results capped at 50 with path, line and snippet; under 500 ms on the template repo.
* Index rebuild runbook after restore (PAP-53).

**Interface contract**

Provides: `ForgePort.search`, code source for unified search; consumed by PAP-138, PAP-277, PAP-105.

Consumes: contract (PAP-449), Forgejo config (PAP-273), permission action (PAP-276).

**Definition of done**

* Query for `composeRoutes` returns the defining file across two repos in the console and in `/dev/repos`; conformance fixture added; CHANGELOG; Linear comment.

**Test plan**

* Unit: query builder and result mapper against recorded responses.
* E2E: search from PAP-277 UI with mocked and live backends.

**Demo**

Reviewer types `defineModule` in the repo browser search and lands on `packages/core/src/modules/manifest.ts`. Under a minute.

**Edge cases**

* Index behind after a big push: results carry `indexedAt` and the UI shows a staleness hint.
* Private repo without `forge.read`: excluded silently.
* Query with regex metacharacters: escaped; Forgejo fuzzy mode off by default.
* Index volume full: Forgejo logs, alert through PAP-534.

**Dependencies**

Hard: PAP-449, PAP-273. Soft: PAP-276, PAP-138, PAP-277.

**Agent**

Builder: Forge (Platform Engineer). Reviewer: Sentinel (Code Reviewer).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 2 round-4 file keys in this description to Linear identifiers: `r4/forge/forge-observability` = PAP-534, `r4/module-system/service-swap-drill` = PAP-554.
