---
identifier: "PAP-222"
title: "Build tenant API keys and outbound webhooks for developers: scoped keys, per-key limits, signed webhook deliveries with retries, developer settings page and generated TypeScript SDK"
project: "identity"
projectName: "Identity, Roles & Audiences"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Developer"]
milestone: "Agent principals and enterprise"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-35", "PAP-43", "PAP-59", "PAP-229", "PAP-269", "PAP-303", "PAP-304", "PAP-353"]
blocks: []
key: "identity/tenant-api-keys-webhooks"
url: "https://linear.app/paperos/issue/PAP-222/build-tenant-api-keys-and-outbound-webhooks-for-developers-scoped-keys"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:41:59.741Z"
model: "claude-sonnet-5"
effort: "low"
---

# PAP-222: Build tenant API keys and outbound webhooks for developers: scoped keys, per-key limits, signed webhook deliveries with retries, developer settings page and generated TypeScript SDK

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / low — Deferred label (excluded from Oct-1 scope)

**Goal**

Deferred to v0.2 by the Execution Schedule (NJ-14 stop-loss 09-27 can reinstate). Not claimable before 10-01.

Give the developer audience a real surface: tenant-scoped API keys with scopes and limits, outbound webhooks with signed, retried deliveries, a developer settings page, and a generated TypeScript SDK from the OpenAPI document PAP-35 already serves. Agent keys (PAP-60) stay separate; this is for customers' own integrations.

**Scope**

* In: Better Auth `apiKey()` second key class with prefix `pos_live_` and `pos_test_`, scope model reusing `withScopes()` from PAP-60, per-key rate limits and daily quotas, `webhook_endpoint` and `webhook_delivery` tables, delivery worker on the jobs queue with HMAC signatures and exponential retries, developer page at `/console/developers`, SDK package `@paperos/sdk` generated with `openapi-typescript` plus a thin fetch client, docs.
* Out: OAuth apps and third-party marketplaces, GraphQL, per-key billing (business-core later).

**Spec**

* Keys: metadata `{ tenantId, name, scopes, environment: 'live' | 'test', createdBy }`; test keys hit the same API with `X-PaperOS-Env: test` and are limited to tenants flagged `sandbox`; scopes are `<entity>:<read|write>` strings validated against the registry of oRPC procedures (PAP-35 exposes `procedureScopes()`).
* Limits: plugin rate limit 600 requests per minute default, configurable per key; quota `requests_per_day` in `api_key.attributes`; 429 with `Retry-After`; usage counters in `api_key_usage (key_id, day, count)`.
* Webhooks: endpoint `{ id, tenant_id, url, secret, events: string[], active, failure_count }`; deliveries `{ id, endpoint_id, event, payload jsonb, attempt, status, response_code, next_at }`; signature header `PaperOS-Signature: t=<unix>,v1=<hmac-sha256>`; retries at 1 m, 5 m, 30 m, 2 h, 12 h then `active=false` with an email; events come from the domain event catalogue (`packages/core/events`, data-layer) filtered by tenant.
* Developer page: keys table (create with scope picker, shown once, revoke, last used), webhooks table (add, test-send, delivery log with redelivery), API reference link to Scalar docs.
* SDK: `pnpm sdk:build` runs `openapi-typescript` on `/api/openapi.json`, wraps in `createClient({ apiKey, baseUrl })` with typed errors and pagination helpers; published to the GitHub Packages registry per release (PAP-52).

**Interface contract**

* Provides: `requireApiKey(scopes)` oRPC middleware; `emitWebhook(event, payload, tenantId)`; `@paperos/sdk`; events `webhook.delivery.failed`.
* Requires: PAP-35 OpenAPI and procedure registry, PAP-59 `can()` and `withScopes()` via PAP-60, PAP-43 jobs, `packages/core/events` catalogue.
* Tables: `api_key` (plugin), `api_key_usage`, `webhook_endpoint`, `webhook_delivery`.

**Definition of done**

* Create a key with `invoice:read`, call the SDK, receive data; call `invoice.update` and receive 403 (Vitest integration).
* Webhook: subscribe a local receiver, trigger `invoice.paid` on the seeded tenant, receive a signed delivery; break the receiver, see five retries and deactivation (compressed schedule).
* Signature verification snippet in docs passes against real deliveries.
* Developer page screenshots at 375, 768, 1280, 1920 light and dark; axe clean.
* Sentinel Security Auditor signs off on key hashing and SSRF protections; docs `docs/platform/developers.md`; changelog under "Developer".

**Test plan**

* Unit: signature encode/verify, retry schedule, scope validation.
* Integration: quota counter rollover at midnight UTC; test key blocked on a live tenant.
* E2E: create key, test-send webhook, redeliver from the log.
* Visual: page stories at seven widths.

**Demo**

Open `/console/developers`, create a test key, run `npx tsx examples/list-invoices.ts` with it, then add a webhook to a `smee.io` URL and click Test send; the delivery appears with a 200. Under two minutes.

**Edge cases**

* Webhook URL points at private IPs or the API itself: rejected (SSRF allowlist of public ranges).
* Endpoint returns 200 slowly (over 10 s): counted as timeout, retried.
* Key used from a tenant the creator has left: keys belong to the tenant, keep working until revoked.
* Event payload contains PII of an erased user (privacy issue): deliveries older than 30 days are purged.
* SDK and API version skew: `X-PaperOS-Version` header, SDK warns on mismatch.

**Dependencies**

PAP-35, PAP-59, PAP-43 (hard). Soft: PAP-60 (scope helpers), PAP-63 (console host), data-layer events catalogue, PAP-52 (publishing).

**Agent**

Built by Forge (lead). Reviewed by Sentinel (Security Auditor) and Quill (SDK docs).

**Size**

M: two plugin-backed features and a generated SDK; the webhook worker is the only real service.
