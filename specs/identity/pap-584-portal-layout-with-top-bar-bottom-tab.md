---
identifier: "PAP-584"
title: "Portal layout with top bar, bottom tab bar and left rail, `PortalNav` from `app.spec.yaml`, login and home pages with specs, states and the PWA install placement"
project: "identity"
projectName: "Identity, Roles & Audiences"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Customer"]
milestone: "Agent principals and enterprise"
state: "Backlog"
parent: "PAP-62"
children: []
blockedBy: ["PAP-16", "PAP-58", "PAP-224", "PAP-438", "PAP-447", "PAP-578", "PAP-579", "PAP-658", "PAP-661"]
blocks: ["PAP-585"]
key: "r4/identity/portal-frame"
url: "https://linear.app/paperos/issue/PAP-584/portal-layout-with-top-bar-bottom-tab-bar-and-left-rail-portalnav-from"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:11.896Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: "2026-09-30"
cycle: null
---

# PAP-584: Portal layout with top bar, bottom tab bar and left rail, `PortalNav` from `app.spec.yaml`, login and home pages with specs, states and the PWA install placement

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

First half of PAP-62: the customer surface frame. A route group `/portal` on the shell layouts with its own navigation, a login page carrying tenant branding, a home page with quick links, the banner slot PAP-61 mounts into, and the states every page inherits, so the account pages (sibling) and later modules (billing, invoices, legal) drop in.

**Scope**

In: `apps/web/src/portal/portal.layout.tsx` (top bar with tenant logo, title, `ActorBadge` avatar menu; bottom tab bar under 768 px; left rail at 768 px and above; no inspector; `banner` slot), `PortalNav` reading `navigation.portal`, `portal.quickLinks` app-spec key, pages and specs `specs/pages/portal/{login,home}.spec.yaml`, `AccountStatusCard`, tenant picker card for multi-tenant customers, access `audiences: [customer]` with `anonymous` for login and a 'You are staff, open console' link, states via PAP-234, PWA install banner after the second visit (PAP-18), copy in `apps/web/src/portal/copy.ts`.

Out: Profile, security, billing stub and notification pages (sibling PAP-585), real billing (PAP-177), legal pages (PAP-221), marketing sign-up (PAP-193).

**Spec**

* Login: `SignInForm` (PAP-224) with tenant branding; guest option only when the app spec enables anonymous access; return URL preserved through sign-in.
* Home: greeting, `AccountStatusCard`, quick links from `portal.quickLinks` (defaults: profile, security, billing when configured), multi-tenant picker using the customer variant of `TenantSwitcher`.
* Anonymous principal on any other portal route redirects to login with the return URL; staff sees the console link; agents are denied.
* Theming from PAP-75 when present, default tokens otherwise; logo falls back to the app name; offline read works with the sync indicator (PAP-272).
* Lighthouse performance and accessibility above 90 at 375 and 1280 on home.

**Interface contract**

Provides: `portal.layout.tsx` slot names `topbar`, `nav`, `main`, `banner`; `PortalNav`; `portal.quickLinks` key; `AccountStatusCard`; copy file; specs above.

Consumes: Routes and layouts (PAP-16), sign-in form (PAP-224), tenancy hook and switcher (PAP-579), states (PAP-234), primitives (PAP-67), theming (PAP-75, soft), PWA install hook (PAP-18, soft), sync indicator (PAP-272, soft), `ActorBadge` (PAP-60, soft). Consumed by the sibling, PAP-61 banner, PAP-177, PAP-136, PAP-180, PAP-221, PAP-193.

**Definition of done**

* Two specs validate; anonymous redirect and staff link tested; screenshots of login and home at 320, 375, 768, 1024, 1280, 1536, 1920 in light, dark and high contrast; axe zero serious or critical.
* PAP-84 vision inspection reports no overflow; Lighthouse numbers in the PR; docs `docs/product/customer-portal.md` section 'Frame'; changelog under Customer.

**Test plan**

* Unit: nav generation from app spec, quick-link defaults, redirect logic per audience, install banner visit counter.
* E2E: Playwright: anonymous to `/portal/profile` redirects and returns after sign-in; staff sees the console link; multi-tenant customer sees the picker; 375 and 1280.

**Demo**

Open the Pages preview as the seeded customer: land on home, open the avatar menu, resize to 375 for the tab bar, sign out and see the branded login. Under two minutes.

**Edge cases**

* No tenant logo or palette: default theme, no broken image.
* Customer in several tenants: picker card on home.
* Session revoked elsewhere: next request 401, redirect preserving the path.

**Dependencies**

Blocked by PAP-16, PAP-579 and PAP-224 (hard). Soft: PAP-234, PAP-67, PAP-75, PAP-18, PAP-272, PAP-60. Blocks the sibling PAP-585.

**Agent**

Builder: Quill (Page Spec Writer) writes specs; Iris (Component Crafter) builds. Reviewer: Sentinel (Visual Inspector; Edge Case Hunter).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 2 round-4 file keys in this description to Linear identifiers: `r4/identity/portal-account-pages` = PAP-585, `r4/identity/tenancy-ui` = PAP-579.
