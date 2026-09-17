---
identifier: "PAP-276"
title: "Forge client, oRPC forge.* procedures and forge.read permission checks"
project: "forge"
projectName: "Version Control & Forge Independence"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Developer", "Agent"]
milestone: "Disaster recovery proven"
state: "Backlog"
parent: "PAP-54"
children: []
blockedBy: ["PAP-268", "PAP-45", "PAP-51"]
blocks: ["PAP-277"]
key: "child/PAP-54/21"
url: "https://linear.app/paperos/issue/PAP-276/forge-client-orpc-forge-procedures-and-forgeread-permission-checks"
source: "Linear snapshot 2026-09-17T06:03Z (round-2 issue)"
---

# PAP-276: Forge client, oRPC forge.* procedures and forge.read permission checks

**Goal**

Build `packages/forge-client` on the generated Forgejo client from PAP-51 and expose read-only oRPC procedures `forge.repos.list|tree|file|commits|commit` and `forge.pulls.list|get`, each guarded by `can(actor, 'forge.read', { repo })`, with SHA-keyed caching, so the pages in the other children have a permission-safe backend.

**Scope**

In: client wrapper, DTO mappers, trailer parser for `Linear:` and `Character:`, cache with 30 s staleness for membership filtering, server-side `bot-scout` class token.

Out: pages (children 2 and 3).

**Spec**

* Token never leaves the server; procedures reject when the actor lacks `forge.read`.
* Cache key includes the ref's current SHA fetched cheaply first.
* `CommitDto.linearKeys` parsed from trailers; `author.character` from the PAP-48 identity convention.

**Interface contract**

Provides: procedures and DTOs, permission action `forge.read` registered with PAP-59, `packages/forge-client`. Consumes: Forgejo API (PAP-45), generated client (PAP-51), token (PAP-48), API host (PAP-35), `can()` (PAP-59).

**Definition of done**

* `callAs(customer)` forbidden on every procedure; developer sees only permitted repos.
* Integration tests against a Forgejo fixture container; trailer parser fixtures.

**Test plan**

* Unit: DTO mappers; trailer parser; cache key logic.
* Permission: `callAs` matrix for customer, developer, agent.
* Integration (CI compose): fixture Forgejo with two repos and one private.

**Demo**

Reviewer calls `forge.repos.commits` from the Scalar console as a developer and gets commits with `linearKeys`, then as a customer and gets 403. Under a minute.

**Edge cases**

* Forgejo unreachable: procedures return `UNAVAILABLE` with last cached payload flag.
* Force-push: cache key changes.

**Dependencies**

PAP-45, PAP-35, PAP-51 (hard). Soft: PAP-48, PAP-59. Blocks children 2 and 3.

**Agent**

Built by Forge. Reviewed by Sentinel (Security Auditor).

**Size**

M
