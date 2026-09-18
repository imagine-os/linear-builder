---
identifier: "PAP-593"
title: "Internal service principals: `service` users for the worker, collab server, Electric proxy and orchestrator, short-lived signed service tokens through `SecretsPort`, `requireService()` middleware and the service call matrix"
project: "identity"
projectName: "Identity, Roles & Audiences"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Developer"]
milestone: "Agent principals and enterprise"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-223", "PAP-267"]
blocks: []
key: "r4/identity/service-principals"
url: "https://linear.app/paperos/issue/PAP-593/internal-service-principals-service-users-for-the-worker-collab-server"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:13.530Z"
model: "claude-opus-5"
effort: "high"
estimate: 3
dueDate: "2026-09-30"
cycle: null
---

# PAP-593: Internal service principals: `service` users for the worker, collab server, Electric proxy and orchestrator, short-lived signed service tokens through `SecretsPort`, `requireService()` middleware and the service call matrix

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Build M

**Goal**

`PrincipalType` has `service` and the audit log has `actor_kind = 'system'`, but nothing says how the collab server calls the API to check a room, how the orchestrator posts status, or how the worker acts without a human. Today each would share the database role or a long-lived key. Give internal services their own principals, short-lived signed tokens minted from a secret the kernel hands out, and a matrix of who may call what.

**Scope**

In: `users` rows with `kind = 'service'` seeded for `worker`, `collab-server`, `electric-proxy`, `orchestrator`, `dr-drill`; `packages/auth/src/service.ts` with `mintServiceToken(service, { ttl: '5m', audience })` (HS256 over a `SERVICE_TOKEN_SECRET` obtained through `SecretsPort`, PAP-444, soft: env) and `verifyServiceToken()`; oRPC `requireService(names)` middleware and `serviceProcedure`; matrix `ops/security/service-matrix.yaml` (`{ service, mayCall: [procedure globs], mayActAs: tenant-scoped boolean }`) validated in Gate 1 and enforced by the middleware; audit rows with `actor_kind = 'service'` and `service` name; rotation with a 10-minute overlap; docs `docs/platform/service-principals.md`.

Out: Agent keys (PAP-60 children), tenant API keys (PAP-222), mutual TLS between containers, orchestrator credential broker (PAP-300).

**Spec**

* Tokens: `{ iss: 'paperos', sub: 'service:collab-server', aud: 'api', exp, jti }`; `jti` cached for replay refusal within the TTL; clock skew tolerance 30 s; secret from `SecretsPort` with `SERVICE_TOKEN_SECRET_PREVIOUS` honoured during rotation.
* `requireService(['collab-server'])` resolves a `Principal { type: 'service', id, attributes: { service } }`; tenant-scoped calls require an explicit `tenantId` argument and `mayActAs: true` in the matrix; `withTenant` then sets the RLS variables with `app.actor_kind = 'service'`.
* Matrix examples: `collab-server` may call `permissions.check`, `presence.filter`; `worker` may call nothing over HTTP (it uses the database with `withTenant`) except `files.getUrl`; `orchestrator` may call `agents.status.*`, `agents.key.*`; `dr-drill` may call `health` and `smoke.*`.
* Denied calls emit a security event (`service.denied`, PAP-356) and never fall back to a human session.
* Tokens never appear in logs; a Semgrep rule (PAP-80) flags `SERVICE_TOKEN_SECRET` reads outside `packages/auth`.

**Interface contract**

Provides: `mintServiceToken`, `verifyServiceToken`, `requireService`, `serviceProcedure`, matrix schema and `pnpm security:service-matrix --check`, seeded service users, security event `service.denied`.

Consumes: Better Auth server (PAP-223), middleware chain (PAP-267), `SecretsPort` (PAP-444, soft), tenancy middleware (PAP-578), audit (PAP-38), security telemetry (PAP-356, soft), Semgrep rules (PAP-80, soft). Consumed by PAP-140, PAP-270, PAP-96, PAP-43 workers, PAP-563, PAP-288 status.

**Definition of done**

* Collab server calls `permissions.check` with a minted token (200); calling `invoice.update` is 403 with `service.denied` emitted; expired and replayed tokens refused (compose tests).
* Rotation: new secret set, old honoured for 10 minutes, then refused; matrix check fails a PR that adds a procedure without a matrix entry.
* Audit rows show `actor_kind = 'service'` with the service name; docs with the matrix; changelog under Security.

**Test plan**

* Unit: token claims and expiry, `jti` replay cache, matrix glob matching, `mayActAs` enforcement, rotation window.
* E2E: the collab server container authenticates a room through the API using a service token on the compose stack; the orchestrator stub posts status.

**Demo**

Run `pnpm tsx examples/service-token.ts collab-server` to mint a token, call `permissions.check` with it (200) and `invoice.update` (403), then rotate the secret and repeat. Under two minutes.

**Edge cases**

* Service needs a new procedure: PR adds the matrix entry; reviewer (Sentinel) owns the file via CODEOWNERS.
* Secret missing at boot: services refuse to start (fail closed).
* Service acting for a tenant that was purged: `withTenant` fails with `tenant-gone`.

**Dependencies**

Blocked by PAP-223 and PAP-267 (hard). Soft: PAP-444, PAP-38, PAP-356, PAP-80, PAP-578. Consumed by PAP-140, PAP-270, PAP-96, PAP-43, PAP-288.

**Agent**

Builder: Forge (Platform Engineer). Reviewer: Sentinel (Security Auditor).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 2 round-4 file keys in this description to Linear identifiers: `r4/data-layer/platform-dr-drill` = PAP-563, `r4/identity/tenancy-core` = PAP-578.
