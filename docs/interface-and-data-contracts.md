Status: v1, 2026-09-17. Owner: Data Layer & Database (Forge, reviewed by Sentinel). Companion to the Blueprint. This document fixes the shapes that parallel Claude sessions code against so that seventeen projects converge instead of drifting. Where an issue already owns a contract it is cited; where none did, a new Spec issue is named in section 6. Changes to anything here need an ADR (PAP-130) and a comment on the owning issue.

## 1. Conventions that apply everywhere

* Ids are UUIDv7 (`uuid_generate_v7()` from migration 0000, PAP-32); wire form is the lowercase string. Every tenant-scoped table has `tenant_id` first, `created_at`/`updated_at`/`deleted_at timestamptz`, soft delete by default (PAP-32). Timestamps are ISO-8601 UTC strings on the wire.
* Tenant isolation is Postgres RLS driven by `SET LOCAL app.tenant_id, app.actor_id, app.actor_kind, app.request_id, app.reason, app.bypass` (PAP-34, PAP-38). Missing context fails closed. The identity layer adds `app.principal_id, app.role, app.attrs` (PAP-58, PAP-59); PAP-58 must set both `app.actor_id` and `app.principal_id` to the same value until the two names are unified in the tenancy doc.
* `Principal` from `@paperos/core/audience` (PAP-55) is the canonical actor type: `{ id, type: 'human'|'agent'|'service'|'anonymous', tenantId, attributes }`. The API context `actor` (PAP-35, PAP-267) imports it; `user.kind` (PAP-33) and `principalType` (PAP-57, PAP-60) are storage views of the same enum. An `ActorRef = { id, type, character? }` is the projection stored on rows, events and comments.
* `Money = { amountMinor: bigint, currency }` in TypeScript, `amount_minor bigint + currency char(3)` in Postgres, and a decimal string (`"1999"`) in JSON because JSON has no bigint (PAP-175 wins over the `number` form in PAP-71 and PAP-164; PAP-187 renames `amount_cents` to `amount_minor`).
* Filters anywhere are the `FilterTree` from `@paperos/core/filter` (PAP-279): permissions `Condition`, view `FilterGroup`, spec data section, segments and automations are aliases of it.
* Zod 4 is the schema language; JSON Schema is generated, never hand-written (PAP-114, PAP-239, PAP-161). Every contract package exports both plus TypeScript types.

## 2. Shared data model

| Entity | Owner | Table(s) | Key columns and invariants |
| -- | -- | -- | -- |
| Tenant | PAP-33, PAP-58 | `tenant` | `slug` unique, `plan`, `settings`, `branding jsonb` (theme tokens, PAP-75), `deleted_at` starts a 30-day purge grace (`gap/data-layer/tenant-lifecycle` owns the request flow; `security/retention-pii` owns the purge job). Better Auth `organization` maps onto this table, never a second one. |
| Organisation | PAP-58 | same as tenant | PaperOS uses "organisation" in UI copy and "tenant" in code; one entity. |
| Workspace | PAP-33, PAP-58 | `workspace` | `(tenant_id, slug)` unique, `kind default|team|project`; every tenant gets one default workspace by trigger; Better Auth `team` maps here. |
| User | PAP-33, PAP-57 | `user` (+ Better Auth credential tables) | Global, not tenant-scoped; `email citext` unique; `kind human|agent|service`; `agent_character`; `attributes jsonb` (tier, staffRole, character). |
| Membership / Role | PAP-33, PAP-58, PAP-59 | `membership`, `role` | `(tenant_id, workspace_id, user_id)` unique; `status invited|active|suspended`; `role.permissions` is `resource:action[]`; five base roles `owner|admin|staff|member|viewer` (PAP-55); system roles immutable. |
| Agent principal | PAP-60, PAP-103 | `user` rows with `kind='agent'`, `api_key` (Better Auth plugin) | Key metadata `{ character, issue?, session?, scopes[] }`; prefix `pos_agent_`; tenant API keys are the second class `pos_live_|pos_test_` (PAP-222). Session status `{ character, state, issueKey?, sessionId?, startedAt?, spentTodayUsd, dailyCapUsd, lastHeartbeat }` (PAP-113; heartbeat owner is the pending agents session-observability issue). |
| Page | PAP-114, PAP-117 | file `specs/pages/<id>.spec.yaml`, no table | `meta.id` equals filename; `route`, `surface`, `access`, `data`, `layout`, `components`, `states`, `events`, `edgeCases`; `status: ready` gate rules. Pages are code, versioned in git, not tenant data. |
| Component | PAP-74, PAP-114 | `packages/ui` registry, `specs/components/*.json` | Component id `ui.<name>` with props JSON Schema; codegen (PAP-120) only emits registered ids; state components `ui.errorState`, `ui.offlineBanner`, `ui.deniedState` (PAP-234). |
| View | PAP-161 | `view`, `dataset`, `field` | `ViewSpec` strict Zod; `dataset_ref jsonb` (`entity:key` or `custom:id`); `kind` enum of ten view kinds; `visibility personal|shared|public`; `spec.filter` is a `FilterTree`. |
| Record | PAP-161, PAP-164 | `record` for custom datasets; entity tables for code datasets | `record.data jsonb` validated by `FieldDef[]`; code datasets register with `registerDataset()`; record-level detail, trash and bulk ops are pending tables gap issues. |
| Document | PAP-128, PAP-140, PAP-142 | repo `docs/**.mdx` (no table); `yjs_document`, `yjs_updates` for live docs | Room name `<entityType>:<entityId>`; `state bytea` V2 update; 20 MB cap. Tenant-authored runtime docs are the pending collab runtime-docs-store issue. Heading anchors expose `data-block-id` for comments. |
| Comment | PAP-131 | `comment_thread`, `comment` | `anchor_key` grammar `entity:<type>:<id>`, `element:<route>:<specKey>`, `doc:<path>#<blockId>`, `canvas:<id>:<node>`, `shot:<fileId>:<frame>`; `author_kind`; `status open|resolved`; escalation stores `linear_issue_key`. PM comments (`pm_comment`, PAP-100) mirror Linear and carry `anchor jsonb` in the same grammar. |
| Event | new: event contract issue (section 6) | `outbox_event`, `event_subscription` | Envelope in section 3. Existing partial owners: orchestrator emitter (PAP-97), `stripe_event` inbox (PAP-177), `live_event` (pending realtime push-transport). |
| Job | PAP-43 | pg-boss schema `jobs`, `jobs.idempotency`, `jobs.dead_letter`, `jobs.schedules` | Name `domain.action`; Zod payload validated on enqueue and dequeue; `idempotencyKey` maps to `singletonKey`; tenant and actor propagated so audit records `actor_kind='system'`. |
| Audit event | PAP-33, PAP-38 | `audit_event` (monthly partitions) | Append-only; `action insert|update|delete|restore|bypass_read`; `before/after/diff`; `reason` required for agents; per-tenant hash chain. |
| File | PAP-33, PAP-37 | `file` | Key `<tenant>/<yyyy>/<mm>/<file_id>/<name>`; `status pending|ready|failed`; `sha256`; download URLs minted per request after an RLS-scoped row read. |
| Ledger entry | PAP-175, PAP-179 | `fin_transaction` (business event), `fin_journal_entry`, `fin_journal_line`, `fin_account_balance` | Lines balance in functional currency or `UNBALANCED`; posted entries immutable, reversed not edited; `ledger.postEvent(tx)` idempotent on `(source_type, source_id)`; accounts resolved by `subtype`, never code. |
| Notification | PAP-136 work package 1 (notification core) | `notification`, `notification_preference`, `notification_delivery` | Kinds registry; idempotency `(kind, source, recipient, bucket)`; produced by subscribing to the event bus. |

Cross-entity references use `EntityRef = { type, id }` where `type` is the dataset key from PAP-161's registry (for example `invoice`, `pm_issue`, `file`). Comments, notifications, search documents (PAP-39) and audit events all store it as two columns `entity_type`, `entity_id`.

## 3. Event bus

The bus is Postgres-native: a transactional outbox written in the same transaction as the row change, drained by the jobs worker (PAP-43), fanned out to in-process subscribers, jobs, `live_event` rows (push transport), tenant webhooks (PAP-222) and the orchestrator (PAP-97). No Kafka, no Redis. LISTEN/NOTIFY is only a wake-up hint (PAP-174 debounces it), never the delivery path.

Envelope (`@paperos/core/events`, Zod):

```ts
{ id: uuidv7, topic: 'invoice.paid', version: 1, occurredAt, tenantId, actor: ActorRef,
  subject: EntityRef, requestId?, causationId?, correlationId?, idempotencyKey?,
  payload: TopicPayload[topic] }
```

Rules: topics are `<entity>.<past-tense-verb>` in `domain.action` style shared with job names; payloads are Zod schemas registered with `defineTopic(name, schema, { version })`; publishing an unregistered topic fails at boot; payloads carry ids and the changed fields only, never whole rows with PII (PAP-40 policy); `version` bumps on breaking change with a reader kept for 30 days (same rule as PAP-239); subscribers are idempotent on `event.id`; ordering is guaranteed per `subject` only; delivery is at-least-once.

Initial topic catalogue and producers: `tenant.created|deleted` (PAP-58); `membership.invited|accepted|removed` (PAP-58); `agent.session.started|finished|blocked`, `agent.quota.exceeded` (PAP-96, PAP-60, PAP-111); `issue.needs_justin`, `review.gate_failed`, `review.ready`, `release.candidate` (PAP-94, PAP-88, PAP-97, via PAP-239 gate reports); `record.created|updated|deleted` (audit trigger, PAP-38, filtered by dataset); `view.shared` (PAP-172); `comment.created|mentioned|resolved` (PAP-131); `doc.published`, `changelog.published` (PAP-128, PAP-133); `file.ready|failed` (PAP-37); `job.finished|failed` (PAP-43); `import.finished` (PAP-199); `invoice.issued|paid|voided`, `payment.succeeded|failed|refunded`, `subscription.updated`, `payroll.run.approved|paid`, `ledger.entry.posted|reversed` (PAP-177, PAP-180, PAP-179, PAP-184); `segment.entered|exited` (PAP-195); `webhook.delivery.failed` (PAP-222); `sync.conflict` (PAP-148). External inbound webhooks (Linear, Stripe, Forgejo, Airtable) are normalised into the same envelope by their receivers with `actor.type='service'`.

## 4. Internal API conventions

* Transport: oRPC 1.x on Hono 4 at `/api/v1/rpc/<router>.<procedure>` (PAP-35, PAP-267); the same routers are exposed as OpenAPI 3.1 REST at `/api/v1/<entity>` for external callers and the SDK (PAP-269, PAP-222). Better Auth owns `/api/auth/*` (PAP-57); Electric shapes `/api/sync/shape` (PAP-270); files never pass through RPC (PAP-37); webhooks live under `/api/webhooks/<source>`; Hocuspocus is a separate WebSocket origin (PAP-140).
* Auth headers: `Authorization: Bearer <session or api key>` (cookie session on web); `x-tenant: <slug>` or subdomain, required on tenant-scoped procedures (400 `VALIDATION` when missing, 412 `TENANT_REQUIRED` from PAP-58 is retired in favour of that one code); `X-PaperOS-Env: test` for sandbox keys (PAP-222); `Idempotency-Key` on every `create` and non-idempotent `update`; `X-PaperOS-Reason` for agent mutations (maps to `app.reason`, PAP-38); `traceparent` in, `x-request-id` and `X-PaperOS-Actor: agent:forge` out (PAP-40, PAP-60).
* Procedure shape: `router.<entity>.<list|get|create|update|archive|restore>`; list input `{ cursor?, limit<=100, filter?: FilterTree, sort?: { field, dir }[] }`, output `{ items, nextCursor }` with signed keyset cursors (PAP-268; tables compiler PAP-163 shares the cursor signer). Bulk endpoints take `{ ids[], patch }` capped at 500.
* Errors: `ORPCError` with `code` in `UNAUTHORIZED | FORBIDDEN | NOT_FOUND | CONFLICT | VALIDATION | RATE_LIMITED | PAYLOAD_TOO_LARGE | INTERNAL`, body `{ code, message, requestId, details?: { path, issue }[], retryAfter? }`; RLS `42501` maps to `NOT_FOUND` on reads and `FORBIDDEN` on writes; 409 bodies carry `{ code: 'CONFLICT', server: row }` for the outbox (PAP-148); non-production adds `explain` from `can()` (PAP-59).
* Idempotency and limits: `idempotency_keys (tenant_id, actor_id, key, request_hash, response, status, expires_at 24h)`; same key with a different body is 422; in-flight duplicate is 409; `POST /api/v1/rpc/batch` accepts up to 25 mutations, each with its own key. Rate limits: per actor 600/min, per API key configurable, per IP 60/min on public routes (`/pay`, `/r/<code>`, embeds), all Postgres-backed with `Retry-After`. Owned by the new idempotency and rate-limit issue (section 6); PAP-35's in-memory bucket is the interim.
* Versioning: `/api/v1` path; additive changes free; breaking changes need an ADR and a deprecation header for 30 days.

## 5. Monorepo package boundaries

`paperos-template` (PAP-13) is one pnpm + Turborepo workspace. Ownership means the project whose issues may create files there; other projects add files only through the owner's registration API. Optional modules may import only `@paperos/core`, `@paperos/db`, `@paperos/ui`, `@paperos/spec`, `@paperos/views` and events (PAP-28); a lint rule bans other cross-module imports.

| Package | Owner | Contents and registration points |
| -- | -- | -- |
| `apps/web`, `apps/desktop`, `apps/mobile` | app-shell (PAP-13, PAP-19, PAP-20) | Shell, router slots (PAP-16), `AppShell`, `useLayout`; modules register routes through `composeRoutes` (PAP-264). |
| `apps/api`, `apps/worker` | data-layer (PAP-267, PAP-43) | Middleware chain, router mount, worker entry; routers registered by packages. |
| `apps/collab-server` | realtime (PAP-140) | Hocuspocus. |
| `packages/core` | app-shell owns the index (PAP-13); sub-folders: `audience` identity (PAP-55), `filter` data-layer (PAP-279), `events` data-layer (new), `types` data-layer (new), `modules` app-shell (PAP-264), `pwa`, `windows`, `native`, `flags` app-shell, `i18n` app-shell (PAP-27) | Pure TypeScript, no React, no database. |
| `packages/db` | data-layer (PAP-32, PAP-33, PAP-34, PAP-38) | Schema barrel; other packages add `src/schema/<module>.ts` files and RLS through the generator. |
| `packages/api-contract`, `packages/api-client` | data-layer (PAP-268) | Routers and client; business routers are contributed files. |
| `packages/sync` | data-layer (PAP-36, PAP-270-272), realtime extends (PAP-143, PAP-148) | Shapes, PGlite, outbox, live events. |
| `packages/auth`, `packages/permissions` | identity (PAP-57, PAP-59, PAP-60) | Better Auth server and client; `can()`, `useCan`, `withScopes`. |
| `packages/ui`, `packages/tokens` | design-system (PAP-66, PAP-67, PAP-74) | Components with registered ids. |
| `packages/spec` | spec-builder (PAP-114-PAP-126) | Page and app spec schemas, validator, codegen. |
| `packages/views` | tables (PAP-161-PAP-174) | View model, compiler, field types, automations. |
| `packages/collab` | collab and realtime (PAP-128, PAP-131, PAP-141, PAP-145) | Docs engine, comments, presence, window bus. |
| `packages/jobs`, `packages/files`, `packages/search`, `packages/email` | data-layer (PAP-43, PAP-37, PAP-39, email gap) | Runtime services with `define*/register*` APIs. |
| `packages/finance`, `packages/crm`, `packages/pm`, `packages/import` | business-core (PAP-175), growth (PAP-187), pm-linear (PAP-100, moved out of `core`), migration (PAP-199) | Optional modules with `module.ts` manifests. |
| `packages/agents`, `packages/contracts` | agents (PAP-103, PAP-108), quality (PAP-239) | Character schema, handoff, gate artifacts. |
| `.claude/`, `specs/`, `docs/`, `ops/` | agents, spec-builder, collab, app-shell/forge | Agent definitions and skills; page specs; MDX docs; compose and CI files. |

## 6. Provide and consume matrix

| Contract | Provider (issue) | Consumers (issues) |
| -- | -- | -- |
| Core entities and Zod types | data-layer PAP-33 | identity PAP-57, PAP-58; every module schema; PAP-100, PAP-175, PAP-187, PAP-161 |
| RLS session-variable contract | data-layer PAP-34 | PAP-58, PAP-59, PAP-38, PAP-270, PAP-163, PAP-174 |
| `Principal` and audiences | identity PAP-55 | PAP-35/267, PAP-59, PAP-60, PAP-114, PAP-136, PAP-141, PAP-195 |
| `can()` and SQL predicates | identity PAP-59 | PAP-35, PAP-140, PAP-141, PAP-163, PAP-172, PAP-64, PAP-128 |
| `FilterTree` | data-layer PAP-279 | PAP-59, PAP-161, PAP-119, PAP-163, PAP-166, PAP-172, PAP-174, PAP-195, PAP-268 |
| Shared value types (`Money`, `ActorRef`, `EntityRef`, cursors, error body) | data-layer, new issue A | PAP-71, PAP-164, PAP-175, PAP-27, PAP-268, PAP-131, PAP-136 |
| Domain event envelope, catalogue, outbox | data-layer, new issue B | PAP-28, PAP-97, PAP-136 (work package 1), PAP-174, PAP-179, PAP-195, PAP-222, push-transport, PAP-113 |
| Idempotency keys, rate limits, batch | data-layer, new issue C | PAP-148, PAP-222, PAP-60, PAP-172, PAP-193, PAP-194, PAP-177 |
| API middleware, error codes, headers | data-layer PAP-267 | every router; PAP-57, PAP-38, PAP-40 |
| Routers, client, pagination | data-layer PAP-268 | PAP-119, PAP-163, PAP-36, PAP-16, business routers |
| Sync shapes and outbox | data-layer PAP-270-272 | PAP-143, PAP-148, PAP-145, PAP-163, PAP-58 (`useTenant` remount) |
| Jobs (`defineJob`, `enqueue`) | data-layer PAP-43 | PAP-37, PAP-39, PAP-136 (work package 1), PAP-190, PAP-191, PAP-194, PAP-199, PAP-205, PAP-222 |
| Audit trigger and `reason` | data-layer PAP-38 | PAP-60, PAP-61, PAP-174, PAP-179, PAP-37, PAP-135 |
| File upload and download | data-layer PAP-37 | PAP-131, PAP-180, PAP-185, PAP-202, PAP-137, PAP-58 logos |
| Search registry | data-layer PAP-39 | PAP-138, PAP-129, PAP-128, PAP-151, PAP-166 |
| Page and app spec schema | spec-builder PAP-114, PAP-117 | PAP-16, PAP-59, PAP-64, PAP-120, PAP-122, PAP-123, PAP-141, PAP-43 admin page |
| Component id registry | design-system PAP-74 | PAP-114, PAP-120, PAP-124, PAP-234 |
| Design tokens and branding | design-system PAP-66, PAP-75 | PAP-33 `branding`, PAP-235, PAP-136 email, PAP-180 PDF |
| View model | tables PAP-161 | PAP-163-PAP-174, PAP-102, PAP-119, PAP-183, PAP-189 |
| Yjs rooms and auth hook | realtime PAP-140 | PAP-141, PAP-142, PAP-132, PAP-145, PAP-147, PAP-149 |
| Comment anchors | collab PAP-131 | PAP-137, PAP-100, PAP-142, PAP-128, PAP-197 |
| Module manifest | app-shell PAP-264 | every optional package; PAP-28, PAP-22, PAP-117 |
| Package boundary map and import lint | app-shell, new issue D | PAP-13, PAP-24, PAP-28, PAP-100, PAP-78 (lint in Gate 1) |
| Finance model and ledger posting | business-core PAP-175, PAP-179 | PAP-177, PAP-180, PAP-181, PAP-184, PAP-185, PAP-196, PAP-206 |
| Gate artifacts | quality PAP-239 | PAP-78-PAP-90, PAP-97, PAP-137, PAP-110 |
| Handoff and character schema | agents PAP-103, PAP-108 | PAP-96, PAP-104, PAP-113, PAP-60, PAP-92 |
| Linear issue contract and states | pm-linear PAP-91, PAP-93 | PAP-96, PAP-97, PAP-101, PAP-118, PAP-137 |

New issues (letters used in the matrix): A shared value types, B domain event contract, C idempotency and rate limiting (all data-layer, Type Spec, Phase P0), D package boundary map (app-shell, Type Spec, Phase P0). A and B are pure packages on the PAP-13 layout and enter Ready for Claude on creation; C waits for PAP-267 and D for PAP-13. Linear refused `issueCreate` with `USAGE_LIMIT_EXCEEDED` on 2026-09-17, so their full specs (Goal through Demo, labels, milestones, blocks) are published in [Round 2 pending issues: contracts (4)](https://linear.app/paperos/document/round-2-pending-issues-contracts-4-734961df9c59) and in `round2/pending-issues-contracts.json`; B and C supersede the earlier pending gaps `gap/data-layer/event-bus` and `gap/data-layer/rate-limit-idempotency`. The other pending issues named above (session observability, notification-core, push transport, runtime docs store, tenant lifecycle) are specified in their projects' "Round 2 pending issues" documents and blocked only by the same cap.
