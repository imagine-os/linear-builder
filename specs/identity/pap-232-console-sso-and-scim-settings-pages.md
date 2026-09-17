---
identifier: "PAP-232"
title: "Console SSO and SCIM settings pages, enforcement and enterprise docs"
project: "identity"
projectName: "Identity, Roles & Audiences"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Staff"]
milestone: "Agent principals and enterprise"
state: "Backlog"
parent: "PAP-65"
children: []
blockedBy: ["PAP-230", "PAP-231"]
blocks: []
key: "identity/sso-scim/console-enforcement-docs"
url: "https://linear.app/paperos/issue/PAP-232/console-sso-and-scim-settings-pages-enforcement-and-enterprise-docs"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T06:23:19.381Z"
model: "claude-sonnet-5"
effort: "low"
---

# PAP-232: Console SSO and SCIM settings pages, enforcement and enterprise docs

**Goal**

Deferred to v0.2 by the Execution Schedule (NJ-14 stop-loss 09-27 can reinstate). Not claimable before 10-01.

Make SSO and SCIM self-serve: console pages for IdP setup, domain verification, SCIM tokens and group mapping, the `enforce` option with a break-glass path, and Okta and Entra guides.

**Scope**

* In: `/console/settings/sso` and `/console/settings/scim` pages with specs, enforcement logic on sign-in, break-glass for owners with passkeys, sync log view, `docs/platform/enterprise-sso-scim.md`.
* Out: protocol implementations (siblings).

**Spec**

* SSO page: choose type, paste metadata URL or XML, download SP metadata, domain list with verification status and TXT instructions, Test login button (opens a popup, reports claims received), Enforce toggle with lockout warning.
* SCIM page: generate token (shown once), base URL, group-to-role mapping editor (grid if PAP-165 exists, else list), sync log of last 100 requests with status.
* Enforcement: when `enforce` is on for a verified domain, magic links and OAuth for that domain are refused with a message; owners with a registered passkey may still sign in locally (break-glass), audited as `auth.breakglass`.
* Docs: setup guides with screenshots for Okta and Entra, troubleshooting table.

**Interface contract**

* Provides: pages, `sso.enforcement.check(email)` used by the sign-in form, audit events `auth.breakglass`.
* Requires: sibling SSO and SCIM children, PAP-63 console host, PAP-67 components.

**Definition of done**

* Owner configures OIDC and SAML in the console and logs in via each with mock IdPs (Playwright video).
* Enforcement refuses a magic link for an enforced domain; owner break-glass works (tests).
* Screenshots of both pages at seven widths, light and dark; axe clean.
* Docs merged; changelog under "Identity".

**Test plan**

* E2E: configure, verify, test login, enforce, break-glass.
* Unit: enforcement decision table (domain verified or not, enforce on or off, owner passkey or not).
* Visual: two pages at seven widths.

**Demo**

Open `/console/settings/sso`, paste the mock IdP metadata, click Test login, see the claims; toggle Enforce and try a magic link for that domain on the sign-in page. Under two minutes.

**Edge cases**

* Enforce turned on with zero owners holding passkeys: blocked with instructions.
* Mapping editor with 500 groups: search and paging.
* Token generation twice: previous token revoked with confirmation.

**Dependencies**

Both sibling children (hard), PAP-63 (soft: mount under a temporary route if the console is late).

**Agent**

Built by Iris (Component Crafter) with Forge on enforcement. Reviewed by Sentinel (Security Auditor, Visual Inspector); Quill reviews docs.

**Size**

M.
