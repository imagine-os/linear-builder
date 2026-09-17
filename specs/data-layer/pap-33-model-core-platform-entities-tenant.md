---
identifier: "PAP-33"
title: "Model core platform entities: tenant, workspace, user, membership, role, audit_event, file"
project: "data-layer"
projectName: "Data Layer & Database"
phase: "P0"
type: "Spec"
priority: 1
surfaces: ["Developer"]
milestone: "Postgres + Drizzle baseline"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-32"]
blocks: ["PAP-34", "PAP-35", "PAP-37", "PAP-38", "PAP-39", "PAP-57", "PAP-100", "PAP-129", "PAP-175", "PAP-187", "PAP-205", "PAP-223", "PAP-267", "PAP-268", "PAP-355", "PAP-420"]
key: "data-layer/core-entities"
url: "https://linear.app/paperos/issue/PAP-33/model-core-platform-entities-tenant-workspace-user-membership-role"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T04:05:38.875Z"
---

# PAP-33: Model core platform entities: tenant, workspace, user, membership, role, audit_event, file

**Goal**

Model the seven shared entities every app and project extends: `tenant`, `workspace`, `user`, `membership`, `role`, `audit_event`, `file`. Output is Drizzle schema, Zod types, an ER diagram and a written contract; the canonical `Principal` type is declared by PAP-55 in `packages/core` and this issue's `user.kind` maps onto it.

**Scope**

In:

* Tables in `packages/db/src/schema/core/*.ts` with relations, indexes, constraints and comments.
* `drizzle-zod` schemas in `packages/db/src/zod/core.ts` (insert, select, update).
* ER diagram and `docs/data/core-entities.md` with invariants and ownership.
* `demo` seeds; consumer notes for identity, audiences, files, audit.
* `tenant_module` reserved for PAP-28.

Out: RLS (PAP-34), API (PAP-35), UI, PM, finance and CRM entities.

**Spec**

* `tenant`: `id`, `slug` unique, `name`, `plan`, `settings jsonb`, `branding jsonb`, `locale`, `timezone`, timestamps, `deleted_at`.
* `workspace`: `tenant_id`, `slug` unique per tenant, `name`, `kind default|team|project`, `settings jsonb`; default workspace created by trigger.
* `user` (global): `email citext unique`, `name`, `avatar_file_id`, `locale`, `timezone`, `kind human|agent|service`, `agent_character`, `disabled_at`; `email` nullable only when `kind <> 'human'`. Better Auth owns credentials keyed to `user.id`.
* `membership`: `tenant_id`, `workspace_id` nullable, `user_id`, `role_id`, `status invited|active|suspended`, `invited_by`; unique `(tenant_id, workspace_id, user_id)`.
* `role`: `tenant_id` nullable for system roles, `key`, `name`, `permissions jsonb`, `is_system`; seeded `owner`, `admin`, `staff`, `customer`, `agent`, `viewer`.
* `audit_event`: uuidv7, `tenant_id`, actor columns, `action`, `entity_type`, `entity_id`, `before`, `after`, `diff`, `reason`, `request_id`, monthly partitions (PAP-38 fills behaviour).
* `file`: `tenant_id`, `key`, `size`, `sha256`, `mime`, `status pending|ready|failed`, `variants jsonb`, `uploaded_by`.

**Interface contract**

Provides:

* Drizzle exports `tenant`, `workspace`, `user`, `membership`, `role`, `auditEvent`, `file` and relations from `@paperos/db/schema/core`; Zod `TenantSelect`, `UserInsert` and friends from `@paperos/db/zod/core`.
* Invariants other projects rely on: every tenant row has one default workspace; `membership` rows never cross tenants; system roles are immutable through the app role.
* `user.kind` values equal `Principal['kind']` in PAP-55; `role.permissions` strings are `resource:action` in PAP-59's grammar.
* `file` columns are the contract PAP-37 completes; `audit_event` columns are the contract PAP-38 completes.

Consumes: helpers and `createDb` (PAP-32). Coordinates with PAP-55 and PAP-56 (audience tables reference `membership`).

**Definition of done**

* Migration generated and applied on staging; `db:check` clean.
* Vitest constraints: cross-tenant membership rejected, default workspace created, system role edit rejected, agent user without email accepted, human without email rejected.
* Zod schemas snapshot-tested; ER diagram renders; contract doc reviewed by Sentinel (Security Auditor) and Quill.
* Studio screenshots at 1280 and 1920; CHANGELOG; ADR `0006-core-entities.md`; consumers notified by comment.

**Test plan**

* Unit: pgTAP-style SQL tests for each CHECK and unique constraint; trigger test for the default workspace.
* Integration: seed `demo`, assert three tenants, 40 users, memberships consistent; `drizzle-zod` parse of every seeded row.
* Static: schema barrel exports snapshot; `@owner data-layer` tag present on every file (PAP-41 reads it).
* Visual: ER diagram rendered on GitHub and Studio screenshots at 1280 and 1920.

**Demo**

Reviewer runs `pnpm db:seed --profile demo && pnpm db:studio`, opens `membership` filtered to one tenant, tries to insert a row pointing at another tenant's workspace in Studio and receives the constraint error. Under 2 minutes.

**Edge cases**

* Email case and unicode normalised at the API; `citext` in storage.
* User with zero tenants: allowed; the onboarding wizard issue handles it.
* Tenant soft delete cascades logically; hard purge is the tenant-lifecycle issue.
* Missing future audit partition: PAP-38 creates three months ahead.
* File row without object: PAP-37 reconciliation.

**Dependencies**

PAP-32 (hard). Coordinates with PAP-55, PAP-56, PAP-57. Unblocks PAP-34, PAP-35, PAP-37, PAP-38, PAP-39, PAP-57, PAP-100, PAP-129, PAP-175, PAP-187, PAP-205.

**Agent**

Specified and built by Forge (Schema Wright) with Quill drafting the contract doc. Reviewed by Sentinel.

**Size**

M: seven tables and a document.
