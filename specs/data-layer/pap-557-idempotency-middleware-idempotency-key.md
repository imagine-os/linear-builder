---
identifier: "PAP-557"
title: "Idempotency middleware: `Idempotency-Key` contract, `idempotency_keys` table with replay semantics, `withIdempotencyKey()` client helper and `POST /api/v1/rpc/batch`"
project: "data-layer"
projectName: "Data Layer & Database"
phase: "P0"
type: "Build"
priority: 1
surfaces: ["Developer"]
milestone: "Postgres + Drizzle baseline"
state: "Backlog"
parent: "PAP-304"
children: []
blockedBy: ["PAP-267"]
blocks: ["PAP-148", "PAP-222"]
key: "r4/data-layer/idempotency-batch"
url: "https://linear.app/paperos/issue/PAP-557/idempotency-middleware-idempotency-key-contract-idempotency-keys-table"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:07.317Z"
model: "claude-opus-5"
effort: "high"
estimate: 3
dueDate: "2026-09-22"
cycle: null
---

# PAP-557: Idempotency middleware: `Idempotency-Key` contract, `idempotency_keys` table with replay semantics, `withIdempotencyKey()` client helper and `POST /api/v1/rpc/batch`

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Build M

**Goal**

First half of PAP-304, what the offline outbox (PAP-148) and every financial procedure need: safe retries. One `idempotent()` middleware stores and replays responses for 24 hours keyed on tenant, actor and key, a client helper re-sends keys, and the batch endpoint executes up to 25 mutations with per-item keys and partial results.

**Scope**

In: `packages/api-contract/src/middleware/idempotency.ts`, `packages/db/src/schema/idempotency.ts` (`idempotency_keys` with RLS and TTL job), `apps/api/src/routes/batch.ts`, `packages/api-client/src/idempotency.ts` (`withIdempotencyKey()`), procedure marker `nonIdempotent`, docs section `docs/data/api.md#idempotency`.

Out: Rate limiting and `limits.yml` (sibling PAP-558); outbox persistence of keys (PAP-148).

**Spec**

* Header `Idempotency-Key` (UUID or up to 128 chars) required on every `create`, `archive`, `restore` and `update` flagged `nonIdempotent`; missing header is `VALIDATION` in production, a warning in dev; agents (PAP-60) must always send it.
* Row `(tenant_id, actor_id, key, request_hash, procedure, status in_flight|done, response jsonb, http_status, created_at, expires_at)`; `request_hash = sha256(procedure + canonical JSON body)` with sorted keys and normalised whitespace.
* Same key and hash while `in_flight`: 409 `CONFLICT` with `retryAfter: 1`; same key, different hash: 422 `VALIDATION` with `details[0].issue = 'idempotency-key-reused'`; `done`: replay with header `Idempotent-Replayed: true`; expired: treated as new.
* Stored response capped at 256 KB; larger responses store `{ ref: EntityRef }` and replay a 303 to the `get` procedure.
* Batch `POST /api/v1/rpc/batch { mutations: [{ id, procedure, input, idempotencyKey }] }`, up to 25 items, 1 MB body; items for the same `entity` run in order, distinct entities up to 4 concurrently, each in its own transaction; response `{ results: [{ id, ok, data | error }] }`; the batch carries its own `Idempotency-Key` to replay the whole result.
* Stored responses are redacted with `pii.json` (PAP-559, soft) before insert; RLS keeps tenant A from replaying tenant B.
* TTL job (PAP-43, soft) deletes expired keys hourly in batches of 10,000.

**Interface contract**

Provides: `idempotent()` middleware on the `os` builder, `.nonIdempotent()` marker, `POST /api/v1/rpc/batch`, headers `Idempotency-Key` and `Idempotent-Replayed`, table `idempotency_keys`, client `withIdempotencyKey()` generating UUIDv7 keys and re-sending them on retry.

Consumes: Middleware chain (PAP-267), `ApiErrorBody`/`EntityRef` (PAP-302), client link (PAP-268), jobs TTL (PAP-43, soft). Consumed by PAP-148, PAP-222, PAP-60, PAP-177, PAP-179, PAP-180 and every business router.

**Definition of done**

* Mounted in the PAP-267 chain after auth with the order test updated; 50 concurrent identical `create` calls produce one row and 49 replays or 409s (compose stack).
* Different body, same key is 422; batch of 25 with one failing item returns partial results; replaying the batch key returns the stored result without re-executing (assert row counts).
* `packages/api-client` retries reuse the key (test); middleware overhead under 3 ms p95 at 200 rps (autocannon, bench committed).
* `docs/data/api.md` Idempotency section with curl examples; PAP-148 owner acknowledges the batch and 409 contract in a comment; CHANGELOG under API.

**Test plan**

* Unit: hash canonicalisation (key order, whitespace, unicode), state machine in_flight/done/expired with a fake clock, 256 KB cap path, batch grouping by entity.
* E2E: Playwright against the dev stack: the sync demo replays a queued write twice after a simulated network drop and the server shows one row plus `Idempotent-Replayed: true` in the network panel.

**Demo**

Reviewer sends the same `curl -H 'Idempotency-Key: demo-1'` create twice and sees one row plus the replay header, changes the body and reads the 422, then posts a 3-item batch with one bad item and reads the partial result. Under two minutes.

**Edge cases**

* Client crashes after send and retries with a new key: duplicate row, documented as client responsibility; `withIdempotencyKey()` persists keys in the PAP-148 outbox to prevent it.
* Key reused after 24 h with the same body: executed again; longer windows use natural keys (PAP-177 `stripe_event.id`).
* Batch item depends on an earlier item's generated id: `tmp_` id remapping is PAP-148's job; the batch executes in the given order so it works when the client rewrites inputs.

**Dependencies**

Blocked by PAP-267 (hard: middleware chain and error mapping). Soft: PAP-268, PAP-302, PAP-43, PAP-559. Blocks PAP-148, PAP-222; sibling PAP-558 shares the chain order test.

**Agent**

Builder: Forge (Platform Engineer). Reviewer: Sentinel (Security Auditor; Edge Case Hunter for concurrency).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 2 round-4 file keys in this description to Linear identifiers: `r4/data-layer/pii-registry` = PAP-559, `r4/data-layer/rate-limits` = PAP-558.
