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
blockedBy: ["PAP-229", "PAP-38", "PAP-59"]
blocks: []
key: "identity/impersonation"
url: "https://linear.app/paperos/issue/PAP-61/add-staff-view-as-customer-impersonation-with-full-audit-trail"
source: "plan/specs/bucket-1.json (round-1 canonical spec JSON)"
---

# PAP-61: Add staff 'view as customer' impersonation with full audit trail

**Goal**

Let authorised staff see exactly what a specific customer sees, in read-only mode by default and with an explicit, reasoned, time-boxed write mode, while every action is recorded against both identities. Support and QA stop guessing, and customers can trust the audit trail.

**Scope**

- In: start and stop impersonation endpoints, permission and reason capture, session representation, the persistent banner, read-only enforcement, audit records with `impersonatorId`, customer-visible history, admin review page, tests.
- Out: agent impersonation of humans beyond the `onBehalfOf` marker (identity/agent-principals), and customer-initiated screen sharing (realtime/followmode covers live co-browsing).

**Spec**

In `imagine-os/paperos-template`:

- Permission: new actions `user.impersonate` (read-only) and `user.impersonate.write`, granted by built-in policy to `staff-support` and `admin` audiences respectively, further constrained by the tenant (staff may only impersonate customers of tenants they belong to). Both go through `can()` from identity/rbac-abac.
- Endpoints (oRPC, `apps/api/src/routes/impersonation.ts`): `impersonation.start({ targetUserId, reason: string (min 10 chars), mode: 'read' | 'write', ttlMinutes <= 60 })`, `impersonation.stop()`, `impersonation.current()`. Implementation uses Better Auth's `admin` plugin `impersonateUser` under the hood but wraps it so the resulting session stores `impersonatedBy`, `reason`, `mode`, `expiresAt`, `linearIssue?` in the session record; the original staff session is kept and restored on stop.
- Read-only enforcement: `withTenant` middleware inspects `session.impersonation.mode`; for `read`, any oRPC procedure tagged `mutation` returns 403 `IMPERSONATION_READ_ONLY` before executing; Electric write queue is disabled client-side and the UI shows disabled states via `useCan` returning false for all mutating actions.
- Banner: `ImpersonationBanner` in `packages/ui`, mounted in both shells (identity/customer-portal-shell, identity/staff-console-shell): fixed top, high-contrast warning colour token, text "Viewing as Ada Lovelace (customer) - read-only - 27:14 remaining - Stop", countdown, keyboard-accessible Stop button; persists across navigation and Tauri windows (realtime/multi-window-sync broadcast).
- Audit: every request during impersonation writes to data-layer/audit-log with `actorId = target`, `impersonatorId = staff`, `reason`, `impersonationId`; start and stop create `impersonation.started` and `impersonation.ended` events. Customers see a "Account access history" list on their security page (identity/customer-portal-shell) showing staff name, time and reason; tenants may disable customer visibility via a setting, defaulting to visible.
- Admin review page `/console/security/impersonations` (spec `specs/pages/console/impersonations.spec.yaml`): filterable list with grid view when tables/grid-view exists, else a simple table, linking each session to its audit events.
- Notifications: optional email to the customer on write-mode impersonation, on by default, using the auth email transport.

**Definition of done**

- Support user can start read-only impersonation, see the customer's portal, is blocked on a mutation with the specific error, and stops; write mode with reason allows the mutation and records both ids (Playwright e2e and Vitest).
- Session auto-expires at TTL; a request after expiry returns 401 and the banner reports expiry (test with faked clock).
- A `member` role user cannot start impersonation (403 with explain in dev).
- Banner screenshots at the seven widths, light and dark, in both shells; axe clean; countdown announced to screen readers every 5 minutes only.
- Audit events verified in the log with correct fields; customer history page shows the session.
- Docs `docs/platform/impersonation.md` with policy and privacy notes; changelog entry under "Identity"; Linear comment with video of the full flow.

**Edge cases**

- Impersonating another staff member or an admin: denied unless the actor is `owner`; never allow impersonating an owner.
- Nested impersonation attempt: `start` while already impersonating returns 409.
- Target user deleted or leaves the tenant mid-session: middleware ends the impersonation and returns 410.
- Staff opens the customer's Stripe customer portal link during impersonation: external links that carry authority are disabled in read mode and flagged in the UI.
- Realtime presence: the customer must not see a phantom presence cursor labelled with their own name; presence shows "Support (viewing as you)" to staff and is hidden from the customer (realtime/presence hook).
- Reason contains sensitive data: stored as-is but redacted in prompt logs via collab/prompt-log-store rules.

**Dependencies**

- identity/rbac-abac (actions and enforcement), data-layer/audit-log (records). Soft: identity/customer-portal-shell and identity/staff-console-shell (banner mount points), realtime/presence, realtime/multi-window-sync.

**Agent**

- Builds: Forge (lead) for endpoints and middleware; Iris (Component Crafter) for the banner.
- Reviews: Sentinel (Security Auditor mandatory, Visual Inspector, Edge Case Hunter).

**Size**

M: small surface but every path is security- and privacy-sensitive.
