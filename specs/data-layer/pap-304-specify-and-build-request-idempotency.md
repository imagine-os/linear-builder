---
identifier: "PAP-304"
title: "Specify and build request idempotency and rate limiting: `Idempotency-Key` header, `idempotency_keys` table with replay semantics, `POST /api/v1/rpc/batch`, Postgres-backed token buckets per actor, API key and IP"
project: "data-layer"
projectName: "Data Layer & Database"
phase: "P0"
type: "Spec"
priority: 1
surfaces: ["Developer", "Customer"]
milestone: "Postgres + Drizzle baseline"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-267"]
blocks: ["PAP-148", "PAP-172", "PAP-193", "PAP-194", "PAP-222"]
key: "contracts/idempotency-rate-limits"
url: "https://linear.app/paperos/issue/PAP-304/specify-and-build-request-idempotency-and-rate-limiting-idempotency"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:42:22.572Z"
model: "claude-opus-5"
effort: "high"
---

# PAP-304: Specify and build request idempotency and rate limiting: `Idempotency-Key` header, `idempotency_keys` table with replay semantics, `POST /api/v1/rpc/batch`, Postgres-backed token buckets per actor, API key and IP

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Spec P0

**Goal**

Make retries safe and abuse bounded with one middleware pair that every route uses: an `Idempotency-Key` contract that stores and replays responses for 24 hours, a batch endpoint the offline outbox (PAP-148) needs, and Postgres-backed rate limits per actor, per API key and per IP so PAP-35's in-memory bucket, PAP-148's assumed `idempotency_keys` table and the hand-rolled limits in PAP-172, PAP-193 and PAP-194 collapse into one implementation. This issue supersedes the pending gap `gap/data-layer/rate-limit-idempotency` (merged here 2026-09-17, FIX-6; from it: financial procedures in PAP-179 and PAP-180 require the `Idempotency-Key` header, and per-actor overrides exist for `kind: 'agent'` principals).

**Scope**

In:

* `packages/api-contract/src/middleware/idempotency.ts`: reads `Idempotency-Key` (UUID or up to 128 chars), keys on `(tenant_id, actor_id, key)`, hashes the procedure name plus canonical JSON body, stores `{ status: in_flight|done, response, http_status, expires_at }`, replays `done` responses with header `Idempotent-Replayed: true`.
* `packages/db/src/schema/idempotency.ts`: `idempotency_keys (tenant_id, actor_id, key, request_hash, procedure, status, response jsonb, http_status, created_at, expires_at)` with a TTL job (PAP-43) and RLS.
* `POST /api/v1/rpc/batch`: `{ mutations: { id, procedure, input, idempotencyKey }[] }` up to 25, executed sequentially per entity in the order given, each in its own transaction, response `{ results: { id, ok, data | error }[] }`; partial success allowed and documented.
* `packages/api-contract/src/middleware/rate-limit.ts`: sliding-window counters in `rate_limit_bucket (scope, key, window_start, count)` with `INSERT ... ON CONFLICT DO UPDATE` in one statement; scopes `actor` (600/min default), `apiKey` (per-key from PAP-60/PAP-222 metadata), `ip` (60/min on public routes), `tenant` (optional plan cap from PAP-178); 429 with `Retry-After` and `RATE_LIMITED` body; headers `RateLimit-Limit`, `RateLimit-Remaining`, `RateLimit-Reset`.
* Public route registry: procedures marked `public: true` (`/pay`, `/doc`, `/r/<code>`, embeds, `/webhooks/*`) get the IP scope automatically.
* Configuration in `ops/api/limits.yml` validated with Zod; hot-reloaded on SIGHUP.

Out: WAF or edge limits (Caddy), per-tenant billing of usage (business-core usage-metering gap), Redis, CAPTCHA.

**Spec**

* Idempotency applies to every `create`, `archive`, `restore` and any `update` flagged `nonIdempotent`; missing header on those procedures is `VALIDATION` in production and a warning in dev; agents (PAP-60) must always send it.
* Same key, same hash while `in_flight`: 409 `CONFLICT` with `retryAfter: 1`; same key, different hash: 422 `VALIDATION` with `details[0].issue = 'idempotency-key-reused'`; expired key: treated as new.
* Stored response capped at 256 KB; larger responses store only `{ ref: EntityRef }` and replay a 303 to `get`.
* Rate-limit window is 60 s fixed-window plus previous-window weighting (sliding approximation); limits evaluated before auth for `ip`, after auth for `actor`/`apiKey`; one round trip per request via a single SQL function `paperos.rate_limit_hit(scope, key, limit)`.
* Failure mode: if the limits table is unavailable the middleware fails open for authenticated actors and closed for `ip`, logs `rate_limit_degraded` (PAP-40).
* Batch: total body 1 MB (PAP-267 limit); mutations for the same `entity` run in order, distinct entities may run concurrently up to 4; every item is idempotent by its own key; the batch itself carries an `Idempotency-Key` to replay the whole result.

**Interface contract**

Provides: `idempotent()` and `rateLimit(scope)` oRPC middleware on the `os` builder (PAP-267), `publicProcedure` gains `.public()` marker, `POST /api/v1/rpc/batch`, headers `Idempotency-Key`, `Idempotent-Replayed`, `RateLimit-*`, `Retry-After`, tables `idempotency_keys`, `rate_limit_bucket`, SQL function `paperos.rate_limit_hit`, config `ops/api/limits.yml`, client helper `withIdempotencyKey()` in `packages/api-client` (PAP-268) that generates UUIDv7 keys and re-sends the same key on retry. Consumes: middleware chain and `ApiErrorCode` (PAP-267), `ApiErrorBody` and `EntityRef` (shared value types issue), jobs TTL (PAP-43), key metadata (PAP-60, PAP-222), entitlements (PAP-178, soft). Consumed by PAP-148, PAP-222, PAP-60, PAP-172, PAP-193, PAP-194, PAP-177 webhooks, every business router.

**Test plan**

* Unit: hash canonicalisation (key order, whitespace); state machine in_flight/done/expired; window math at boundaries; config schema.
* Integration (PAP-42 stack): 50 concurrent identical `create` calls produce one row and 49 replays or 409s; different body same key is 422; 601st call in a minute is 429 with correct `Retry-After`; `ip` scope applies to `/pay` without a session; batch of 25 with one failing item returns partial results and the failed item's error; replaying the batch key returns the stored result without re-executing.
* Security: key from tenant A cannot replay a response for tenant B (RLS); response bodies stored are redacted per `pii.json` (PAP-41) before insert.
* Perf: middleware adds under 3 ms p95 per request on the dev stack (autocannon, 200 rps); bench committed.

**Definition of done**

* Both middlewares mounted in the PAP-267 chain (order: rateLimit(ip), auth, rateLimit(actor|apiKey), idempotent) with the order test updated.
* Integration tests above green; bench under target.
* `packages/api-client` retries reuse the key (test); PAP-148 owner acknowledges the batch and 409 contract in a comment.
* `docs/data/api.md` sections "Idempotency" and "Rate limits" with copy-paste curl examples; ADR; CHANGELOG under "API"; Linear comment with the staging docs URL.

**Edge cases**

* Client crashes after send, retries with a new key: duplicate row; documented as client responsibility, `withIdempotencyKey()` persists keys in the outbox (PAP-148) to prevent it.
* Key reused after 24 h with the same body: executed again; consumers needing longer windows store their own natural keys (PAP-177 `stripe_event.id`).
* Clock change on the server: windows keyed by `floor(epoch/60)`; a backwards jump can allow one extra window, accepted.
* Shared office NAT hitting the `ip` limit on `/pay`: limit is per `ip + path`, and authenticated users bypass the `ip` scope.
* Table bloat: TTL job deletes expired keys hourly in batches of 10,000; `rate_limit_bucket` rows older than two windows are pruned by the same job.
* Agent key with `scopes` lacking a procedure: 403 from PAP-60, evaluated before the rate-limit counter increments so denied calls do not consume quota.

**Dependencies**

PAP-267 (hard: middleware chain and error mapping). Soft: PAP-268 client, shared value types issue, PAP-43 TTL job, PAP-60 and PAP-222 key metadata, PAP-41 `pii.json`. Blocks PAP-148, PAP-172, PAP-193, PAP-194, PAP-222.

**Agent**

Specified and built by Forge (Platform Engineer). Reviewed by Sentinel (Security Auditor).

**Size**

M

**Demo**

Reviewer runs the API locally, sends the same `curl -H 'Idempotency-Key: demo-1'` invoice create twice and sees one row plus `Idempotent-Replayed: true`, changes the body and gets 422, then runs `pnpm tsx examples/hammer.ts` which fires 700 requests and prints the first 429 with its `Retry-After`. Under two minutes.
