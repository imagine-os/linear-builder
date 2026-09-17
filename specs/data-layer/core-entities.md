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
blocks: ["PAP-100", "PAP-129", "PAP-175", "PAP-187", "PAP-205", "PAP-223", "PAP-267", "PAP-268", "PAP-34", "PAP-35", "PAP-37", "PAP-38", "PAP-39", "PAP-57"]
key: "data-layer/core-entities"
url: "https://linear.app/paperos/issue/PAP-33/model-core-platform-entities-tenant-workspace-user-membership-role"
source: "plan/specs/bucket-0.json (round-1 canonical spec JSON)"
---

# PAP-33: Model core platform entities: tenant, workspace, user, membership, role, audit_event, file

**Goal**

Model the seven shared entities every PaperOS app and every other project extends: `tenant`, `workspace`, `user`, `membership`, `role`, `audit_event` and `file`. This is a Spec issue: the output is the Drizzle schema files, the ER diagram, and the written contract other projects code against.

**Scope**

In:
- Drizzle tables in `packages/db/src/schema/core/*.ts` with relations, indexes, constraints and comments (Drizzle column `.comment()` where supported, otherwise `COMMENT ON` in custom migration for `data-layer/data-dictionary`).
- Zod schemas via `drizzle-zod` exported from `packages/db/src/zod/core.ts` (insert/select/update).
- ER diagram (Mermaid) and a data contract doc `docs/data/core-entities.md` stating invariants and ownership.
- Seed data for the entities in the `demo` profile.
- Interface notes for consumers: identity (Better Auth tables map onto `user`/`membership`), audiences (`identity/audience-model` adds `audience` tables referencing `membership`), files (`data-layer/file-storage`), audit (`data-layer/audit-log`).

Out: RLS policies (`data-layer/rls-tenancy`), API endpoints, UI, PM/finance/CRM entities (other projects).

**Spec**

- `tenant`: `id`, `slug` unique, `name`, `plan` (text, entitlements later), `settings jsonb`, `branding jsonb` (theme tokens for `design-system/theming`), timestamps, soft delete.
- `workspace`: `id`, `tenant_id`, `slug` unique per tenant, `name`, `kind` (`default|team|project`), `settings jsonb`; every tenant gets one default workspace via trigger.
- `user`: `id`, `email citext unique`, `name`, `avatar_file_id`, `locale`, `timezone`, `kind` (`human|agent|service`), `agent_character` nullable (name from `agents/character-schema`), `disabled_at`. Global, not tenant-scoped; Better Auth owns credentials in its own tables keyed to `user.id`.
- `membership`: `id`, `tenant_id`, `workspace_id` nullable (null = tenant-wide), `user_id`, `role_id`, `status` (`invited|active|suspended`), `invited_by`, unique `(tenant_id, workspace_id, user_id)`.
- `role`: `id`, `tenant_id` nullable (null = system role), `key`, `name`, `permissions jsonb` (array of `resource:action` strings; engine in `identity/rbac-abac`), `is_system`. System roles seeded: `owner`, `admin`, `staff`, `customer`, `agent`, `viewer`.
- `audit_event`: `id uuidv7`, `tenant_id`, `actor_user_id`, `actor_kind`, `action`, `entity_type`, `entity_id`, `before jsonb`, `after jsonb`, `diff jsonb`, `reason text`, `request_id`, `session_id`, `created_at`; no `updated_at`; partitioned monthly by `created_at` (declarative partitioning set up in custom migration). Detailed behaviour in `data-layer/audit-log`.
- `file`: `id`, `tenant_id`, `workspace_id`, `owner_user_id`, `bucket`, `key`, `filename`, `mime`, `size_bytes`, `sha256`, `variants jsonb`, `status` (`pending|ready|failed`), `metadata jsonb`.
- Indexes: every `tenant_id`; `(tenant_id, slug)`; `audit_event (tenant_id, entity_type, entity_id, created_at desc)`; `file (tenant_id, sha256)`.
- Invariants written as CHECK constraints or triggers: membership tenant matches workspace tenant; system roles immutable.

**Definition of done**

- Migration generated and applied on staging; `pnpm db:check` clean.
- Vitest: constraint tests (cross-tenant membership rejected, default workspace created, system role edit rejected).
- `drizzle-zod` schemas exported and snapshot-tested.
- ER diagram renders; contract doc reviewed by identity (Sentinel Security Auditor) and Quill.
- Drizzle Studio screenshot of seeded data at 1280 and 1920.
- CHANGELOG; ADR `0006-core-entities.md`; Linear comment linking doc and PR; consumers' issues (`identity/audience-model`, `data-layer/file-storage`, `data-layer/audit-log`) notified by comment.

**Edge cases**

- Email case and unicode: `citext` plus normalisation at API.
- User belongs to zero tenants (just signed up): allowed; UI handles onboarding.
- Deleting a tenant: soft delete cascades logically, hard purge is a separate job (`migration/export` first).
- Agent users without email: `email` nullable only when `kind <> 'human'` (CHECK).
- Audit partitions missing for a future month: `pg_partman` or a monthly cron creates 3 months ahead.
- File row exists but object missing: `status` reconciliation job in `data-layer/file-storage`.

**Dependencies**

`data-layer/drizzle-schema` (hard). Coordinate with `identity/audience-model` and `identity/better-auth` (they extend `user`/`membership`). Unblocks `data-layer/rls-tenancy`, `data-layer/api-layer`, `data-layer/file-storage`, `data-layer/audit-log`, `data-layer/search`.

**Agent**

Specified and built by Forge (Schema Wright) with Quill drafting the contract doc. Reviewed by Sentinel (Security Auditor) and Atlas for cross-project fit.

**Size**

M: seven tables, but their shape is load-bearing for a dozen projects and must be argued in writing.
