---
identifier: "PAP-558"
title: "Postgres-backed rate limiting: `rate_limit_bucket`, `paperos.rate_limit_hit()`, actor, API-key, IP and tenant scopes, public-route registry and hot-reloaded `ops/api/limits.yml`"
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
blocks: ["PAP-148", "PAP-172", "PAP-193", "PAP-194", "PAP-222", "PAP-613", "PAP-623", "PAP-624", "PAP-793", "PAP-836", "PAP-841", "PAP-851", "PAP-855", "PAP-864", "PAP-900"]
key: "r4/data-layer/rate-limits"
url: "https://linear.app/paperos/issue/PAP-558/postgres-backed-rate-limiting-rate-limit-bucket-paperosrate-limit-hit"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:07.439Z"
model: "claude-opus-5"
effort: "high"
estimate: 3
dueDate: "2026-09-22"
cycle: null
---

# PAP-558: Postgres-backed rate limiting: `rate_limit_bucket`, `paperos.rate_limit_hit()`, actor, API-key, IP and tenant scopes, public-route registry and hot-reloaded `ops/api/limits.yml`

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Build M

**Goal**

Second half of PAP-304: bound abuse with one implementation so PAP-35's in-memory bucket, PAP-60's plugin limiter and the hand-rolled limits in PAP-172, PAP-193 and PAP-194 collapse into `rateLimit(scope)`. Sliding-window counters live in Postgres so two API replicas agree, limits are configuration, and `429` carries `Retry-After` and the `RateLimit-*` headers.

**Scope**

In: `packages/api-contract/src/middleware/rate-limit.ts`, SQL function `paperos.rate_limit_hit(scope, key, limit, window)` in `drizzle/custom/`, table `rate_limit_bucket (scope, key, window_start, count)`, `.public()` marker on `publicProcedure` and the public-route registry, `ops/api/limits.yml` with Zod schema and SIGHUP reload, docs section `docs/data/api.md#rate-limits`.

Out: Idempotency and batch (sibling); WAF or edge limits in Caddy; per-tenant usage billing (PAP-391); CAPTCHA (PAP-592).

**Spec**

* Scopes and defaults: `actor` 600/min after auth, `apiKey` per-key value from key metadata (PAP-60, PAP-222), `ip` 60/min before auth on public routes (`/pay`, `/doc`, `/r/<code>`, embeds, `/webhooks/*`, `/api/auth/*` sign-in), `tenant` optional plan cap from PAP-178 (soft).
* Sliding approximation: fixed 60 s windows weighted with the previous window; one round trip per request through `paperos.rate_limit_hit` using `INSERT ... ON CONFLICT DO UPDATE ... RETURNING`.
* Chain order: `rateLimit('ip')`, auth, `rateLimit('actor'|'apiKey')`, `idempotent()`; the PAP-267 order test is updated by whichever sibling merges second.
* Denied calls (403 from scopes or `can()`) are evaluated before the counter increments so they do not consume quota; `ip` scope keys on `ip + path`; authenticated users bypass the `ip` scope.
* 429 body `{ code: 'RATE_LIMITED', retryAfter }` plus headers `RateLimit-Limit`, `RateLimit-Remaining`, `RateLimit-Reset`, `Retry-After`.
* Failure mode: table unavailable fails open for authenticated actors for at most 60 s (then closed) and closed for `ip`; every degraded minute logs `rate_limit_degraded` and emits a security event (PAP-356).
* `limits.yml` entries `{ scope, match: procedure glob | route, limit, window }`; hot-reload on SIGHUP; `pnpm limits:check` validates in Gate 1; rows older than two windows pruned by the shared TTL job.

**Interface contract**

Provides: `rateLimit(scope)` middleware, `.public()` marker and `publicRoutes()` registry, SQL function and table above, config schema `LimitsConfig`, headers above, error `RATE_LIMITED`.

Consumes: Middleware chain (PAP-267), key metadata (PAP-60, PAP-222), entitlements (PAP-178, soft), security events (PAP-356, soft), TTL job (PAP-43, soft). Consumed by PAP-172, PAP-193, PAP-194, PAP-60 (replaces the plugin limiter), PAP-222, PAP-592.

**Definition of done**

* 601st call in a minute is 429 with correct `Retry-After` and headers; `ip` scope applies to `/pay` without a session; authenticated user is not limited by `ip` (compose stack).
* Two API replicas share one budget (test with two processes against one database); denied 403 calls do not consume quota.
* Degraded mode test: table locked, authenticated calls pass for 60 s then fail closed; `rate_limit_degraded` logged and security event emitted.
* Docs section with curl examples; `limits.yml` documented; PAP-60 and PAP-172 owners comment that they drop their own limiters; CHANGELOG under API.

**Test plan**

* Unit: window math at minute boundaries and across a backwards clock jump (one extra window accepted), config schema rejection cases, header rendering, scope key derivation for IPv6 and `X-Forwarded-For` behind Caddy.
* E2E: `pnpm tsx examples/hammer.ts` fires 700 requests against the dev API and prints the first 429 with its `Retry-After`; Playwright asserts the sign-in page shows the rate-limited message after the 11th attempt.

**Demo**

Reviewer runs the hammer script, reads the 429, then edits `limits.yml` to 20/min, sends SIGHUP and reruns to watch the limit change without a restart. Under two minutes.

**Edge cases**

* Shared office NAT on `/pay`: per `ip + path` limit and the authenticated bypass keep customers working; document the number.
* Webhook bursts from Stripe: `/webhooks/*` has its own higher limit and signature failures count double (PAP-356 alert on abuse).
* PgBouncer transaction mode: the function is a single statement, so no session state is needed.
* Key metadata changed mid-window: new limit applies to the next window.

**Dependencies**

Blocked by PAP-267 (hard). Soft: PAP-60, PAP-222, PAP-178, PAP-356, PAP-43. Blocks PAP-172, PAP-193, PAP-194; sibling PAP-557 shares the chain order test.

**Agent**

Builder: Forge (Platform Engineer). Reviewer: Sentinel (Security Auditor).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 2 round-4 file keys in this description to Linear identifiers: `r4/data-layer/idempotency-batch` = PAP-557, `r4/identity/auth-abuse-controls` = PAP-592.
