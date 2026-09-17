---
identifier: "PAP-61"
title: "Add staff 'view as customer' impersonation with full audit trail"
project: "identity"
projectName: "Identity, Roles & Audiences"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Staff"]
milestone: "Roles and audiences enforced end to end"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-38", "PAP-59", "PAP-229", "PAP-456"]
blocks: []
key: "identity/impersonation"
url: "https://linear.app/paperos/issue/PAP-61/add-staff-view-as-customer-impersonation-with-full-audit-trail"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T14:54:09.044Z"
model: "claude-sonnet-5"
effort: "high"
---

# PAP-61: Add staff 'view as customer' impersonation with full audit trail

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Let authorised staff see exactly what a customer sees, read-only by default and with an explicit, reasoned, time-boxed write mode, while every action is recorded against both identities and the customer can see who looked.

**Scope**

* In: `impersonation.start/stop/current` procedures, permission actions, session representation, read-only enforcement, `ImpersonationBanner`, audit records with `impersonatorId`, customer-visible access history, admin review page, optional customer email on write mode, tests.
* Out: agent `onBehalfOf` semantics beyond the marker (PAP-60), live co-browsing (PAP-149).

**Spec**

* Actions `user.impersonate` (read) and `user.impersonate.write`, granted by built-in policy to `staff-support` and `admin`, constrained to customers of tenants the actor belongs to; both evaluated by PAP-59 `can()`.
* Procedures in `apps/api/src/routes/impersonation.ts`: `start({ targetUserId, reason (min 10 chars), mode: 'read' | 'write', ttlMinutes <= 60, linearIssue? })`, `stop()`, `current()`; wraps Better Auth `admin` plugin `impersonateUser`; the session stores `impersonation: { impersonatedBy, reason, mode, expiresAt, id }`; the staff session is kept and restored on stop.
* Read-only: `withTenant` (PAP-58) rejects procedures tagged `mutation` with 403 `IMPERSONATION_READ_ONLY` when mode is `read`; the client disables the Electric write queue and `useCan` returns false for mutating actions; external authority-bearing links (Stripe portal) are disabled.
* Banner: `ImpersonationBanner` in `packages/ui`, mounted in the `banner` slot of both shells: fixed top, warning tokens, "Viewing as Ada Lovelace (customer) - read-only - 27:14 remaining - Stop", countdown announced every 5 minutes, persists across navigation and Tauri windows (PAP-145 broadcast).
* Audit: every request during impersonation writes `actorId = target`, `impersonatorId = staff`, `reason`, `impersonationId` (PAP-38); `impersonation.started` and `impersonation.ended` events; customers see "Account access history" on `/portal/security` (PAP-62, PAP-220); tenants may hide it, default visible.
* Review page `/console/security/impersonations` (spec `specs/pages/console/impersonations.spec.yaml`) listing sessions with links to audit events.

**Interface contract**

* Provides: procedures above; `useImpersonation()` hook (`{ active, target, mode, expiresAt, stop }`); `ImpersonationBanner`; `AccessHistoryList` component for PAP-220's page; audit event kinds; session field `impersonation`.
* Requires: PAP-59 actions and `useCan`, PAP-58 `withTenant`, PAP-38 audit, PAP-57 admin plugin, shells PAP-62 and PAP-63 (soft mount points), PAP-145 (soft).
* Consumers: PAP-60 (`onBehalfOf` marker semantics), PAP-141 presence (hide phantom cursor), PAP-89 (impersonation counts in digest, optional).

**Definition of done**

* Support user starts read-only impersonation, sees the customer's portal, is blocked on a mutation with the specific error, stops; write mode with reason allows the mutation and records both ids (Playwright e2e plus Vitest).
* TTL expiry: request after expiry returns 401 and the banner reports expiry (faked clock).
* `member` cannot start (403 with explain in dev); owners can never be impersonated; nested start returns 409.
* Banner screenshots at seven widths light and dark in both shells; axe clean.
* Audit events verified; customer history shows the session; docs `docs/platform/impersonation.md`; changelog under "Identity"; video of the full flow.

**Test plan**

* Unit: permission decision table (actor role × target role × mode), TTL clamp, reason length.
* Integration: mutation rejection in read mode across three tagged procedures; audit rows for start, action, stop; expiry.
* E2E: full flow at 1280; banner on mobile 375.
* Visual: banner stories in both shells, RTL.

**Demo**

As seeded support staff open Members, choose Ada, "View as customer" with a reason, browse her portal with the banner counting down, try to save her profile and read the read-only error, press Stop; then open Ada's security page to see the access entry. Under two minutes.

**Edge cases**

* Target leaves the tenant mid-session: middleware ends impersonation, 410.
* Presence: customer never sees a cursor with their own name; staff sees "Support (viewing as you)".
* Reason contains sensitive text: stored, redacted in prompt logs by PAP-129 rules.
* Staff session expires first: impersonation ends with it.

**Dependencies**

PAP-59, PAP-38 (hard). Soft: PAP-62, PAP-63, PAP-141, PAP-145, PAP-220.

**Agent**

Forge for procedures and middleware; Iris (Component Crafter) for the banner. Reviewed by Sentinel (Security Auditor mandatory, Visual Inspector, Edge Case Hunter).

**Size**

M.
