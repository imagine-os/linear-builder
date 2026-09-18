---
identifier: "PAP-581"
title: "Session and device listing with revoke, `requireRecentAuth()` step-up with `ReauthDialog`, sign-in alerts and the `SecurityPage` mounted in portal and console"
project: "identity"
projectName: "Identity, Roles & Audiences"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Customer"]
milestone: "Roles and audiences enforced end to end"
state: "Backlog"
parent: "PAP-220"
children: []
blockedBy: ["PAP-223", "PAP-224", "PAP-580"]
blocks: ["PAP-595", "PAP-858", "PAP-894", "PAP-902", "PAP-913"]
key: "r4/identity/sessions-stepup"
url: "https://linear.app/paperos/issue/PAP-581/session-and-device-listing-with-revoke-requirerecentauth-step-up-with"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:11.491Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: "2026-09-25"
cycle: null
---

# PAP-581: Session and device listing with revoke, `requireRecentAuth()` step-up with `ReauthDialog`, sign-in alerts and the `SecurityPage` mounted in portal and console

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Second half of PAP-220: control. Every user sees the devices signed in as them, can end any of them, and sensitive actions demand a fresh proof of identity. The `SecurityPage` composes passkeys (PAP-224), two-factor (sibling), sessions and the access history embed from PAP-61 into one page both shells mount.

**Scope**

In: Migration adding `session.deviceLabel` and `session.lastSeenAt`, device label parser from user agent, `authClient.listSessions|revokeSession|revokeOtherSessions` wiring, `requireRecentAuth(maxAgeSeconds = 300)` helper for procedures tagged `sensitive`, error `REAUTH_REQUIRED` (401), `ReauthDialog` accepting passkey or TOTP, `SecurityPage` in `packages/auth/src/ui/` with sections Passkeys, Two-factor, Sessions, Access history (PAP-61 embed), Sign-in alerts toggle; mounts at `/portal/security` (PAP-62) and `/console/settings/security` (PAP-63); audit `auth.session.revoked`; spec `specs/pages/account/security.spec.yaml`.

Out: TOTP, codes, recovery and emails (sibling), tenant-wide session policy (PAP-595), impersonation history content (PAP-61).

**Spec**

* Sessions table shows device label, OS, browser, country from IP only, last seen, `current` badge, Revoke and Revoke all others; agents' sessions (PAP-60 keys) in a separate tab, paginated.
* Revocation invalidates the cookie cache within `cookieCache.maxAge` (5 min worst case, PAP-223) and immediately for bearer sessions; `session.revoked` event published (PAP-555, soft) so PAP-572 can wipe and PAP-140 can close rooms.
* `requireRecentAuth` compares `session.lastAuthenticatedAt` (set by sign-in, passkey and TOTP verification) with the limit; procedures tagged `sensitive`: passkey delete, email change, code regeneration, tenant deletion, API key creation.
* `ReauthDialog` opens on `REAUTH_REQUIRED`, offers passkey (conditional UI) then TOTP (`verifyTotp` from the sibling), retries the original call on success.
* Sign-in alerts toggle stored in `user.attributes.signInAlerts` (default on); the sibling's `new-device.tsx` honours it.
* Tauri bearer sessions appear as devices with the OS name; revocation clears Stronghold on next launch (PAP-225).

**Interface contract**

Provides: `requireRecentAuth()`, error `REAUTH_REQUIRED`, `ReauthDialog`, `SecurityPage`, `useSessions()`, device label parser, event `session.revoked`, spec above.

Consumes: Better Auth server and client (PAP-223, PAP-224), TOTP verification (sibling), access history embed (PAP-61, soft), shells (PAP-62, PAP-63, soft mount points), events (PAP-555, soft), audit (PAP-38, soft), primitives (PAP-67). Consumed by PAP-62, PAP-63, PAP-222 (key creation is `sensitive`), PAP-595.

**Definition of done**

* Open a second browser, revoke it from the first, watch it bounce to sign-in within one request; revoke-all-others keeps the current session (Playwright).
* Sensitive procedure with a 10-minute-old session returns 401 `REAUTH_REQUIRED`; after `ReauthDialog` it succeeds (fake clock test at exactly 300 s).
* Screenshots of the page at 320, 375, 768, 1024, 1280, 1536, 1920 light and dark in both shells; axe clean; RTL story.
* Docs sections 'Sessions' and 'Step-up'; changelog under Identity.

**Test plan**

* Unit: device label parser for ten user agents, `requireRecentAuth` boundary, revoke-current confirmation logic, alerts toggle default.
* E2E: revoke flows at 375 and 1280; step-up on passkey delete; agent sessions tab with 200 seeded keys paginates.

**Demo**

Open `/portal/security`, see two devices, revoke the other, then try to delete a passkey and complete the re-auth dialog with a passkey. Under two minutes.

**Edge cases**

* Revoking the current session: confirm dialog, then redirect to sign-in.
* Session list of 200 entries (agents): paginated; agent tab only for staff.
* Clock skew between API instances: `lastAuthenticatedAt` is a database timestamp.
* Passkey unavailable in the dialog (Linux Tauri): TOTP only; if no TOTP, the dialog explains and links to setup.

**Dependencies**

Blocked by PAP-580 and PAP-223 (hard). Soft: PAP-224, PAP-61, PAP-62, PAP-63, PAP-38, PAP-67, PAP-555.

**Agent**

Builder: Forge (Platform Engineer) with Iris (Component Crafter) on the page. Reviewer: Sentinel (Security Auditor; Visual Inspector).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 4 round-4 file keys in this description to Linear identifiers: `r4/data-layer/events-core` = PAP-555, `r4/data-layer/local-data-protection` = PAP-572, `r4/identity/mfa-recovery` = PAP-580, `r4/identity/session-policy` = PAP-595.
