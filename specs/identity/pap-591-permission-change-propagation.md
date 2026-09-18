---
identifier: "PAP-591"
title: "Permission change propagation: `permission.changed` topic, versioned server-side policy cache, client refetch of `permissions.mine`, Hocuspocus room re-check and Electric shape invalidation"
project: "identity"
projectName: "Identity, Roles & Audiences"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Developer"]
milestone: "Roles and audiences enforced end to end"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-229", "PAP-555", "PAP-578"]
blocks: []
key: "r4/identity/permission-propagation"
url: "https://linear.app/paperos/issue/PAP-591/permission-change-propagation-permissionchanged-topic-versioned-server"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:13.309Z"
model: "claude-opus-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-25"
cycle: null
---

# PAP-591: Permission change propagation: `permission.changed` topic, versioned server-side policy cache, client refetch of `permissions.mine`, Hocuspocus room re-check and Electric shape invalidation

**Model / Effort:** Opus 5 (`claude-opus-5`) / medium — Build S

**Goal**

Three consumers assume a signal nobody emits: PAP-140 re-checks room permissions 'on `permission.changed`', PAP-229 refetches policies 'on `session.updated` and tenant switch', and PAP-328 relies on the shape proxy returning 409 when access changes. Role edits, grant changes, membership removal and custom role updates all need to reach open sessions within seconds, or a removed staff member keeps a live shape and a room open.

**Scope**

In: Topic `permission.changed { tenantId, principalIds?: Uuid[], scope: 'tenant'|'principal'|'entity', entity?: EntityRef, policyVersion }` declared in `contract-identity` and published by membership, role, grant and impersonation changes; `policy_version` per tenant and per principal in a small `permission_version` table; server-side policy cache keyed by `(tenantId, principalId, version)` in `packages/permissions`; client: `PermissionProvider` subscribes through the push transport (PAP-599, soft) or polls `permissions.version` every 30 s and refetches `permissions.mine`; Hocuspocus subscription that re-runs `onAuthenticate` for affected connections and closes with `4403` when denied; shape proxy compares `policyVersion` in the shape handle and returns `409 shape-invalid`; docs section.

Out: The policy engine (PAP-227), the push transport itself, presence privacy (PAP-141).

**Spec**

* Publishers: `org.members.updateRole|remove`, `roles.update|archive` (PAP-588), `grants.*` (PAP-589), `impersonation.start|stop` (PAP-61), SCIM deactivation (PAP-231, deferred); each bumps the relevant version inside the same transaction and publishes through `publish(tx, ...)`.
* Server cache: `can()` callers pass the request's principal; the cache entry is invalidated by version mismatch, never by TTL alone; a 60 s TTL is the safety net.
* Client: on `permission.changed` matching the principal or tenant, refetch `permissions.mine`, re-render `useCan` consumers, remount shapes whose handle carries an older version (PAP-326 registry does it), and show 'Your access changed' once per 10 s.
* Hocuspocus (PAP-140): the collab server subscribes to the topic through the dispatcher's `inproc` sink in its own process (it shares `packages/core/events`); affected connections are re-authenticated within 2 s; `connection.readOnly` toggles without disconnect when only write access changed.
* Shape proxy (PAP-270): handles embed `pv=<policyVersion>`; a stale handle yields 409 and the client resubscribes (PAP-328).

**Interface contract**

Provides: Topic `permission.changed`, table `permission_version`, `bumpPermissionVersion(tx, scope)`, policy cache API, `permissions.version` procedure, collab-server subscription helper, shape handle version rule, docs.

Consumes: `can()` and `PermissionProvider` (PAP-227, PAP-229), tenancy procedures (PAP-578), event bus (PAP-555), push transport (PAP-599, soft), collab server hooks (PAP-140), shape proxy (PAP-270) and registry (PAP-326). Consumed by PAP-140, PAP-328, PAP-229, PAP-61, PAP-588, PAP-589.

**Definition of done**

* Revoke a member's role in one context: their open grid loses rows within one resubscribe (under 2 s), their open doc room closes with `4403`, and `useCan` hides the Delete button (Playwright with two contexts and the compose stack with Electric and Hocuspocus).
* Server cache hit ratio above 95 percent on the PAP-242 smoke with zero stale decisions (assert with a version bump mid-run).
* Docs; changelog under Identity; comments on PAP-140, PAP-229, PAP-328 pointing at the topic.

**Test plan**

* Unit: version bump inside the transaction (rolls back with it), cache keying and invalidation, client matching of scope to principal, handle version parsing.
* E2E: the two-context scenario above; impersonation start triggers the customer's presence to hide the staff cursor within 2 s.

**Demo**

Open the grid demo as a member in one window and the console as admin in another; remove the member's role and watch rows disappear, the doc room close and the button hide. Under two minutes.

**Edge cases**

* Burst of 1,000 grant changes (bulk share): one event per transaction with `principalIds` batched; clients coalesce refetches per 2 s.
* Push transport absent: 30 s poll is the ceiling; documented.
* Collab server restarted: it re-checks every connection on reconnect anyway (PAP-140).

**Dependencies**

Blocked by PAP-229, PAP-578, PAP-555 (hard). Soft: PAP-140, PAP-270, PAP-326, PAP-61, PAP-599, PAP-588, PAP-589.

**Agent**

Builder: Forge (Platform Engineer) with Nova (CRDT Engineer) on the collab hook. Reviewer: Sentinel (Security Auditor).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 5 round-4 file keys in this description to Linear identifiers: `r4/data-layer/events-core` = PAP-555, `r4/identity/custom-roles` = PAP-588, `r4/identity/resource-grants` = PAP-589, `r4/identity/tenancy-core` = PAP-578, `r4/realtime/live-events-channel` = PAP-599.
