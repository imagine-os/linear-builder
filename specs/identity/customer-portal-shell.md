---
identifier: "PAP-62"
title: "Ship the customer-facing portal shell (login, profile, billing entry) separate from the staff console"
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
blockedBy: ["PAP-16", "PAP-58"]
blocks: []
key: "identity/customer-portal-shell"
url: "https://linear.app/paperos/issue/PAP-62/ship-the-customer-facing-portal-shell-login-profile-billing-entry"
source: "plan/specs/bucket-1.json (round-1 canonical spec JSON)"
---

# PAP-62: Ship the customer-facing portal shell (login, profile, billing entry) separate from the staff console

**Goal**

Ship the reference customer-facing surface every PaperOS app inherits: a portal shell at `/portal` with login, profile, security, billing entry and notifications pages, deliberately separate from the staff console so the two audiences never share navigation or affordances by accident. Every page has a spec and is rendered from the shared layout slots.

**Scope**

- In: portal layout, navigation, five pages with specs, empty and error states, responsive behaviour at all widths, PWA install prompt placement, theming hooks, tests and screenshots.
- Out: real billing (business-core/stripe-billing fills the billing page; here it is an entry point with a stub state), notification delivery (collab/notifications), marketing pages (growth/landing-forms).

**Spec**

In `imagine-os/paperos-template` (apps/web plus specs):

- Route group `/portal` using app-shell/router-layouts with layout `portal.layout.tsx`: top bar (logo from tenant theme, page title, `ActorBadge`/avatar menu), bottom tab bar under 768 px and left rail at 768 px and above, no inspector slot, optional `ImpersonationBanner` slot (identity/impersonation). Access: `audiences: [customer, anonymous for /portal/login]` in every spec; staff visiting `/portal` are allowed (they may be customers too) but see a subtle "You are staff - open console" link.
- Pages and specs (`specs/pages/portal/*.spec.yaml`, each with purpose, access, data, layout, components, states and edge cases):
  1. `/portal/login` - reuses auth components from identity/better-auth with tenant branding and a "Continue as guest" option only when the app spec enables anonymous access.
  2. `/portal` (Home) - greeting, account status card, quick links from `app.spec.yaml` `portal.quickLinks` (default: Profile, Billing, Support).
  3. `/portal/profile` - name, avatar upload (data-layer/file-storage), email (change requires verification), locale and timezone, preferred contact method; optimistic save via Electric write queue with a saved indicator.
  4. `/portal/security` - passkeys list and add (identity/better-auth `/auth/passkeys` embedded), active sessions with revoke, connected OAuth accounts, account access history (identity/impersonation), delete account with 30-day grace.
  5. `/portal/billing` - plan card, payment method and invoices list; without business-core/stripe-billing it renders the `EmptyState` "Billing is not configured for this app yet" with a `data-stub` attribute so conformance tests distinguish stub from failure.
  6. `/portal/notifications` - preference toggles per channel (in-app, email, SMS) stored in `user.attributes.notificationPrefs` until collab/notifications provides its table.
- Components: `PortalNav`, `AccountStatusCard`, `SettingRow`, `DangerZone`, built from design-system primitives and data-display; all copy in `apps/web/src/portal/copy.ts`.
- Behaviour: every page has loading (Skeleton), empty, error and offline states; forms validate with Zod schemas shared with the API; unsaved changes prompt on navigation; PWA install banner appears on Home after the second visit (app-shell/pwa hook).
- Theming: uses tenant runtime theme from design-system/theming when present, else default tokens; logo falls back to app name text.

**Definition of done**

- Six page specs validate with `spec validate`; conformance tests generated (spec-builder/conformance-tests when available, else the draft runner) and passing.
- Playwright screenshots for every page at 320, 375, 768, 1024, 1280, 1536, 1920 in light, dark and high-contrast; video of login -> profile edit -> security -> sign out.
- Vision inspection (quality/screenshot-annotation) reports no overflow or truncation; axe has zero serious or critical issues.
- Permission test: a `staff` principal without customer membership sees the console link; an `anonymous` principal is redirected from `/portal/profile` to `/portal/login` with return URL.
- Works offline for read (cached shell and last data) with a visible offline indicator.
- Lighthouse performance and accessibility above 90 at 375 and 1280.
- Docs `docs/product/customer-portal.md` describing how an app extends the portal; changelog entry under "Customer"; Linear comment with Pages demo link and screenshots.

**Edge cases**

- Tenant has no logo or brand palette: default theme; no broken image.
- Customer belongs to several tenants: Home shows a tenant picker card; the switcher from identity/org-tenancy is reused in a customer-friendly variant.
- Email change to an address already used by another account: server rejects; UI explains without revealing whether the other account exists beyond "cannot use this email".
- Very long names or RTL locales: layout tested with 80-character names and `ar` locale in a story.
- Account deletion requested while an active subscription exists: blocked with guidance until billing cancels (hook for business-core).
- Session revoked from another device while the page is open: next request returns 401 and the shell redirects to login preserving the path.

**Dependencies**

- identity/org-tenancy (membership, switcher), app-shell/router-layouts (layouts). Soft: identity/better-auth, design-system/layout-components, design-system/theming, data-layer/file-storage, app-shell/pwa, business-core/stripe-billing (fills billing later).

**Agent**

- Builds: Iris (Component Crafter) for pages and components; Quill (Page Spec Writer) writes the six specs first.
- Reviews: Sentinel (Visual Inspector across the matrix, Code Reviewer, Edge Case Hunter).

**Size**

M: six spec-driven pages on an existing layout system with an exhaustive visual matrix.
