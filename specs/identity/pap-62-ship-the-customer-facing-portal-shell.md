---
identifier: "PAP-62"
title: "Ship the customer-facing portal shell (login, profile, billing entry) separate from the staff console"
project: "identity"
projectName: "Identity, Roles & Audiences"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Customer"]
milestone: "Agent principals and enterprise"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-16", "PAP-58", "PAP-438", "PAP-447"]
blocks: []
key: "identity/customer-portal-shell"
url: "https://linear.app/paperos/issue/PAP-62/ship-the-customer-facing-portal-shell-login-profile-billing-entry"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T15:11:29.637Z"
model: "claude-sonnet-5"
effort: "high"
---

# PAP-62: Ship the customer-facing portal shell (login, profile, billing entry) separate from the staff console

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Ship the reference customer-facing surface every app inherits: a portal at `/portal` with login, home, profile, security, billing entry and notification preferences, separate from the staff console so the two audiences never share navigation by accident. Every page has a spec and renders from shared layout slots.

**Scope**

* In: `portal.layout.tsx`, `PortalNav`, six pages with specs, all declared states, responsive behaviour at every width, PWA install prompt placement, theming hooks, tests and screenshots.
* Out: real billing (PAP-177 fills the stub), notification delivery (PAP-136), session and 2FA logic (PAP-220 provides the components this page embeds), marketing pages (PAP-193).

**Spec**

* Route group `/portal` on PAP-16 layouts: top bar (tenant logo, title, `ActorBadge` avatar menu), bottom tab bar under 768 px and left rail at 768 px and above, no inspector, `banner` slot for `ImpersonationBanner` (PAP-61). Access: `audiences: [customer]`, `anonymous` for `/portal/login`; staff may visit and see a "You are staff - open console" link.
* Pages and specs (`specs/pages/portal/*.spec.yaml`): `/portal/login` (PAP-224 `SignInForm` with tenant branding, guest option only when the app spec enables anonymous access); `/portal` home (greeting, `AccountStatusCard`, quick links from `app.spec.yaml` `portal.quickLinks`); `/portal/profile` (name, avatar via PAP-37, email change with verification, locale and timezone, contact method; optimistic save via PAP-36 with a saved indicator); `/portal/security` (embeds PAP-220 `SecurityPage`, PAP-61 `AccessHistoryList`, delete account with 30-day grace); `/portal/billing` (plan, payment method, invoices; without PAP-177 renders `EmptyState` "Billing is not configured" with `data-stub`); `/portal/notifications` (channel toggles stored in `user.attributes.notificationPrefs` until PAP-136).
* Components: `PortalNav`, `AccountStatusCard`, `SettingRow`, `DangerZone` from PAP-67 and PAP-71; copy in `apps/web/src/portal/copy.ts`.
* States: loading (Skeleton), empty, error, offline via PAP-234 components; forms validate with Zod shared with the API; unsaved-changes prompt; PWA install banner on home after the second visit (PAP-18).
* Theming: PAP-75 runtime theme when present, else default tokens; logo falls back to app name.

**Interface contract**

* Provides: `portal.layout.tsx` slot names `topbar`, `nav`, `main`, `banner`; `PortalNav` reading `app.spec.yaml` `navigation.portal`; `portal.quickLinks` app-spec key; `data-stub` attribute convention for stubbed sections; `SettingRow` and `DangerZone` for module settings pages.
* Requires: PAP-58 membership and switcher, PAP-16 layouts, PAP-224 sign-in form, PAP-67, PAP-71, PAP-234 states, PAP-75 (soft), PAP-37 (soft), PAP-220 and PAP-61 embeds (soft: placeholders if late), PAP-18 install hook.
* Consumers: PAP-177 (billing page), PAP-136 (preferences page), PAP-180 (invoices list), PAP-221 (legal pages), PAP-193 (sign-up handoff).

**Definition of done**

* Six specs validate; conformance tests (PAP-122 or draft runner) pass.
* Screenshots of every page at 320, 375, 768, 1024, 1280, 1536, 1920 light, dark and high-contrast; video of login, profile edit, security, sign out.
* PAP-84 vision inspection reports no overflow or truncation; axe zero serious or critical.
* Staff principal sees the console link; anonymous principal is redirected from `/portal/profile` to login with return URL (tests).
* Offline read works with the indicator; Lighthouse performance and accessibility above 90 at 375 and 1280.
* Docs `docs/product/customer-portal.md` (how an app extends the portal); changelog under "Customer".

**Test plan**

* Unit: nav generation from app spec, quick-link defaults, stub detection.
* Integration: profile save round-trip through the write queue; email-change verification path.
* E2E: the recorded flow; redirect for anonymous; multi-tenant customer sees the tenant picker.
* Visual: seven widths × three themes; RTL and 80-character-name stories.

**Demo**

Open the Pages preview as the seeded customer: land on home, edit the display name and watch the saved indicator, open Security and see passkeys and access history, open Billing and see the honest stub. Under two minutes.

**Edge cases**

* No tenant logo or palette: default theme, no broken image.
* Customer in several tenants: tenant picker card on home using a customer-friendly `TenantSwitcher` variant.
* Email already used elsewhere: server rejects; UI says only "cannot use this email".
* Session revoked elsewhere: next request 401, redirect preserving path.
* Deletion with an active subscription: blocked with guidance (hook for PAP-177).

**Dependencies**

PAP-58, PAP-16 (hard). Soft: PAP-224, PAP-67, PAP-71, PAP-234, PAP-75, PAP-37, PAP-18, PAP-220, PAP-61, PAP-177.

**Agent**

Quill (Page Spec Writer) writes the six specs first; Iris (Component Crafter) builds. Reviewed by Sentinel (Visual Inspector across the matrix, Code Reviewer, Edge Case Hunter).

**Size**

M.
