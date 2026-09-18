---
identifier: "PAP-571"
title: "Per-tenant sequences and human-readable keys: `defineSequence`, gapless and prefixed formats, `recordKey()` column helper, reservation API and yearly reset"
project: "data-layer"
projectName: "Data Layer & Database"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Developer"]
milestone: "Local-first sync working"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-32", "PAP-33"]
blocks: []
key: "r4/data-layer/tenant-sequences"
url: "https://linear.app/paperos/issue/PAP-571/per-tenant-sequences-and-human-readable-keys-definesequence-gapless"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:20:45.421Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-25"
cycle: null
---

# PAP-571: Per-tenant sequences and human-readable keys: `defineSequence`, gapless and prefixed formats, `recordKey()` column helper, reservation API and yearly reset

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

Invoices need `INV-2026-0042`, issues need `PAP-123`, tickets, quotes, purchase orders and employee numbers all need a per-tenant, human-readable, sometimes gapless counter, and finance law cares about gaps. Nothing owns it, so PAP-180, PAP-100 and PAP-197 would each invent one. This issue ships the primitive once, with the concurrency semantics spelled out.

**Scope**

In: `packages/db/src/sequence/{define,next,format}.ts`, table `tenant_sequence (tenant_id, name, current bigint, prefix, pad, reset: never|yearly, year, gapless boolean)`, SQL function `paperos.next_key(tenant, name)` using `UPDATE ... RETURNING` under row lock, `recordKey('key', { sequence: 'invoice' })` column helper that assigns on insert via trigger, reservation API for gapless sequences, staff settings section for prefixes, `docs/data/sequences.md`.

Out: Global ids (UUIDv7, PAP-302), Linear issue keys mirrored from Linear (PAP-100 uses the mirror value), formatting for display beyond the pattern.

**Spec**

* `defineSequence({ name: 'invoice', pattern: '{prefix}-{yyyy}-{n:4}', prefix: 'INV', reset: 'yearly', gapless: true })` registered at boot; per-tenant overrides of `prefix` and `pad` in settings, validated against the pattern.
* `next_key` increments under the row lock in the caller's transaction; for `gapless: true` the increment happens in the committing transaction of the row insert (trigger), so a rollback leaves no gap; for `gapless: false` a reservation `reserve(name, count)` may hand out numbers ahead of time (bulk import).
* Yearly reset compares `year` with `extract(year from now() at time zone tenant.timezone)` (PAP-33) and restarts at 1 inside the same lock.
* Uniqueness: unique index on `(tenant_id, key)` for every table using `recordKey()`; concurrent inserts serialise per tenant per sequence only.
* Backfill helper assigns keys to existing rows in `created_at` order (used by importers, PAP-347, and PAP-334 restore keeps the original key).
* Audit: prefix or pad changes recorded with reason; changing a gapless sequence's prefix mid-year is refused with guidance.

**Interface contract**

Provides: `defineSequence`, `nextKey(tx, tenantId, name)`, `reserve`, `recordKey()` column helper, SQL function `paperos.next_key`, table `tenant_sequence`, settings section `sequences`.

Consumes: Schema helpers and `withTenant` (PAP-32), tenant timezone (PAP-33), audit (PAP-38, soft), settings page slot (PAP-63, soft). Consumed by PAP-180 invoices and quotes, PAP-197 tickets, PAP-399 employees, PAP-347 imports, PAP-334 restore.

**Definition of done**

* 100 concurrent inserts on one tenant produce keys 1 to 100 with no gaps or duplicates (compose test); a rolled-back insert on a gapless sequence leaves no gap.
* Yearly reset proven with a fake clock across the tenant's timezone boundary; prefix override round-trips through settings.
* Backfill assigns keys to 10k seeded rows in `created_at` order; docs; CHANGELOG; Linear comment with the concurrency test output.

**Test plan**

* Unit: pattern parser and formatter (`{n:4}`, `{yyyy}`, `{yy}`), reset arithmetic, override validation, refusal cases.
* E2E: CI compose: two API replicas insert invoices concurrently against the seeded tenant; assert contiguous keys; importer reservation path.

**Demo**

Reviewer creates three demo invoices, reads `INV-2026-0001..0003`, rolls one back in a transaction script and creates a fourth to see `0004` with no gap, then changes the prefix in settings. Under a minute.

**Edge cases**

* Two tenants share a prefix: fine, keys are unique per tenant only; public URLs use the UUID.
* Timezone change mid-year: reset uses the tenant timezone at the moment of increment; documented.
* Sequence renamed in code: registry migration required; refuse silent drop.
* Very high throughput (1,000 inserts per second on one tenant): row lock serialises; documented as the accepted limit, non-gapless sequences may use `reserve` batches.

**Dependencies**

Blocked by PAP-32 and PAP-33 (hard). Soft: PAP-38, PAP-63. Consumed by PAP-180, PAP-197, PAP-399, PAP-347, PAP-334.

**Agent**

Builder: Forge (Schema Wright). Reviewer: Sentinel (Edge Case Hunter for concurrency; Ledger reviews gapless semantics).

**Size**

S: half a session.
