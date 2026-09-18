---
identifier: "PAP-589"
title: "Per-resource grants and share links: `resource_grant` table, `hasRelation` policy operator compiled to SQL, `ShareDialog` primitive and signed guest links for anonymous access with expiry and passcode"
project: "identity"
projectName: "Identity, Roles & Audiences"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Customer"]
milestone: "Roles and audiences enforced end to end"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-227", "PAP-228", "PAP-578"]
blocks: []
key: "r4/identity/resource-grants"
url: "https://linear.app/paperos/issue/PAP-589/per-resource-grants-and-share-links-resource-grant-table-hasrelation"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:13.002Z"
model: "claude-opus-5"
effort: "high"
estimate: 3
dueDate: "2026-09-25"
cycle: null
---

# PAP-589: Per-resource grants and share links: `resource_grant` table, `hasRelation` policy operator compiled to SQL, `ShareDialog` primitive and signed guest links for anonymous access with expiry and passcode

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Build M

**Goal**

Roles and attributes say who may act on a kind of thing; sharing says who may act on this thing. Views (PAP-172), tenant docs (PAP-379), canvases and records all need 'share with Ada as editor' and 'anyone with the link can view', and each would invent its own table. This is Zanzibar-lite: one grants table, one policy operator, one dialog, and one signed guest token that gives the `anonymous` principal a narrow relation.

**Scope**

In: Table `resource_grant (tenant_id, entity_type, entity_id, subject_kind: principal|audience|link, subject_id, relation: viewer|commenter|editor|owner, granted_by, expires_at, created_at)` with RLS; policy condition op `hasRelation` (`{ path: 'resource', op: 'hasRelation', value: ['editor','owner'] }`) evaluated in memory and compiled to an `EXISTS` subquery by PAP-228; procedures `grants.list|add|remove|createLink|revokeLink`; `ShareDialog` component (people picker, role per person, link toggle with expiry and passcode, copy); guest tokens `gl_<id>.<sig>` resolved by middleware into an `anonymous` principal carrying `attributes.grantId`; route `/s/<token>`; audit of grants; docs `docs/platform/sharing.md`.

Out: View-specific share UI copy (PAP-172 consumes), public pay pages (PAP-396 keeps its own tokens), enterprise link policies, SCIM.

**Spec**

* Relations are ordered `viewer < commenter < editor < owner`; `hasRelation(['editor'])` matches editor or owner; a grant on a parent (`workspace`) may be inherited when the entity registers `parentOf` in the dataset registry (PAP-161), one level only.
* Built-in policies gain `share` verbs: `<entity>.share` allowed for owners of the entity and admins; granting a relation higher than one's own is refused.
* Guest links: HMAC over `{ grantId, entity, relation, exp }` with `CURSOR_SECRET`-style key rotation (PAP-302 pattern); optional passcode hashed; rate-limited per IP (PAP-558); the `anonymous` principal from a link matches only `hasRelation` policies, never role policies; presence shows 'Guest' (PAP-141).
* `permission.changed` published on every grant change (PAP-591) so shapes and rooms refresh; grants expire by `expires_at` (retention job removes them).
* Entitlement hook: `sharing.publicLinks` may be gated by plan (PAP-178, soft).

**Interface contract**

Provides: Table `resource_grant`, op `hasRelation`, procedures `grants.*`, `ShareDialog`, `useGrants(entity)`, guest link middleware and route, event `grant.changed`, docs.

Consumes: Policy model (PAP-227), SQL compiler (PAP-228), tenancy (PAP-578), dataset registry for `parentOf` (PAP-161, soft), rate limits (PAP-558, soft), propagation (PAP-591, soft), presence (PAP-141, soft), entitlements (PAP-178, soft), primitives (PAP-67, PAP-238). Consumed by PAP-172, PAP-379, PAP-321, PAP-333, PAP-131.

**Definition of done**

* Share a record with a seeded member as editor: they can edit, a non-shared member cannot see it (list returns empty through RLS) (compose test through `callAs`).
* Guest link with passcode and 1-hour expiry opens the entity read-only in a private window; expired or wrong passcode refused; link revocation immediate.
* Property test agreement between `can()` and `toPredicate()` extended with `hasRelation` cases; `ShareDialog` at 375 and 1280 light and dark; axe clean; docs; changelog under Identity.

**Test plan**

* Unit: relation ordering, inheritance one level, token signing and rotation, passcode check, refusal to over-grant.
* E2E: Playwright: share, open as the other member, open the guest link in a private context, revoke and reload.

**Demo**

Open a record, click Share, add Ada as editor and create a link with a passcode, open the link in a private window, enter the passcode, then revoke it. Under two minutes.

**Edge cases**

* Entity deleted: grants cascade with it; guest link resolves to `NOT_FOUND`.
* Grant to an audience (`staff-support`): evaluated with `matches()`; audience renamed in the app spec breaks nothing because the id is stored.
* Ten thousand grants on one entity (public template): list paginates; `hasRelation` uses the `(entity_type, entity_id, subject_id)` index.

**Dependencies**

Blocked by PAP-227, PAP-228 and PAP-578 (hard). Soft: PAP-161, PAP-178, PAP-141, PAP-67, PAP-238, PAP-558, PAP-591. Consumed by PAP-172, PAP-379, PAP-321, PAP-333.

**Agent**

Builder: Forge (Platform Engineer) with Iris on the dialog. Reviewer: Sentinel (Security Auditor; Edge Case Hunter).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 3 round-4 file keys in this description to Linear identifiers: `r4/data-layer/rate-limits` = PAP-558, `r4/identity/permission-propagation` = PAP-591, `r4/identity/tenancy-core` = PAP-578.
