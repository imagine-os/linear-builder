---
identifier: "PAP-220"
title: "Build session and device management: list and revoke sessions, TOTP fallback for passkeys, account recovery codes"
project: "identity"
projectName: "Identity, Roles & Audiences"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Customer", "Staff"]
milestone: "Roles and audiences enforced end to end"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-57", "PAP-224", "PAP-456"]
blocks: []
key: "identity/session-device-management"
url: "https://linear.app/paperos/issue/PAP-220/build-session-and-device-management-list-and-revoke-sessions-totp"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T14:54:09.044Z"
model: "claude-sonnet-5"
effort: "high"
---

# PAP-220: Build session and device management: list and revoke sessions, TOTP fallback for passkeys, account recovery codes

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Give every user control and a way back in: a security page listing active sessions and devices with one-click revoke, TOTP as a second factor and as the fallback when a passkey device is lost, and single-use recovery codes. Passkey-first (PAP-57) stays the default; this issue makes it safe to rely on.

**Scope**

* In: Better Auth `twoFactor()` plugin (TOTP and backup codes), session listing and revocation through `authClient.listSessions` and `revokeSession`, device naming from user agent, `SecurityPage` component mounted in the portal (`/portal/security`, PAP-62) and console (`/console/settings/security`, PAP-63), step-up prompts for sensitive actions, email notices on new device sign-in.
* Out: SMS factors, hardware key attestation policies, enterprise MFA enforcement (PAP-65 `enforce`), impersonation history (PAP-61 owns it, the page embeds it).

**Spec**

* Server: add `twoFactor({ issuer: appName, otpOptions: { period: 30, digits: 6 }, backupCodes: { amount: 10, length: 10 } })` to `packages/auth/src/server.ts`; sessions table already has `userAgent`, `ipAddress`; add `deviceLabel` and `lastSeenAt` columns via a migration.
* Step-up: `requireRecentAuth(maxAgeSeconds = 300)` helper for oRPC procedures tagged `sensitive` (passkey delete, email change, recovery code regeneration, tenant deletion); UI opens a `ReauthDialog` that accepts passkey or TOTP.
* Recovery flow: `/auth/recover` accepts email, sends a magic link, then requires TOTP or a recovery code before allowing a new passkey to be registered; every step audited.
* Page sections: Passkeys (from PAP-57 `/auth/passkeys` component), Two-factor (enable with QR via `qrcode` package, confirm code, show codes once, regenerate), Sessions (table with device label, location from IP country only, last seen, current badge, Revoke and Revoke all others), Access history (PAP-61 embed), Sign-in alerts toggle.
* Emails: `new-device.tsx`, `two-factor-enabled.tsx`, `recovery-used.tsx` React Email templates.

**Interface contract**

* Provides: `requireRecentAuth()` in `packages/auth/src/server.ts`; `ReauthDialog` and `SecurityPage` in `packages/auth/src/ui/`; audit events `auth.session.revoked`, `auth.2fa.enabled`, `auth.recovery.used` (PAP-38 shape).
* Requires: PAP-57 server and client, `useSession`; PAP-62 and PAP-63 route slots; Resend transport from PAP-57.
* Tables: `session` (extended), `twoFactor` (plugin), `backupCode` (plugin, hashed).

**Definition of done**

* Enable TOTP, sign out, sign in with password-less magic link plus TOTP, revoke another session and see it end within one request (Playwright e2e).
* Recovery: delete the only passkey in a test, recover with a code, register a new passkey; used codes cannot be reused.
* Step-up: a sensitive procedure called with a 10-minute-old session returns 401 `REAUTH_REQUIRED`; after reauth it succeeds.
* Screenshots of the security page at 320, 375, 768, 1024, 1280, 1536, 1920 light and dark in both shells; axe clean.
* Sentinel Security Auditor signs off on code hashing and rate limits on `/auth/recover`; docs `docs/platform/account-security.md`; changelog under "Identity".

**Test plan**

* Unit: TOTP verification window (±1 step), backup code single use, device label parser for 10 user agents.
* Integration: session revocation invalidates cookie cache within `cookieCache.maxAge`; `requireRecentAuth` boundary at exactly 300 s with a fake clock.
* E2E: enable 2FA, recover, revoke; mobile 375 and desktop 1280.
* Visual: page stories at seven widths; RTL story.

**Demo**

Sign in, open `/portal/security`, enable two-factor with the QR (authenticator app or `oathtool`), open a second browser, revoke it from the first, watch it bounce to sign-in. Under two minutes.

**Edge cases**

* Time drift on the authenticator: accept one step either side, never more.
* User loses passkey and codes: support impersonation cannot bypass; documented owner-verified manual path via Needs Justin.
* Session list of 200 entries (agents): paginate, show agents in a separate tab.
* Revoking the current session: confirm dialog, then redirect to sign-in.
* Tauri bearer sessions: appear as devices with the OS name; revocation clears Stronghold on next launch.

**Dependencies**

PAP-57 (hard). Soft: PAP-62, PAP-63 (mount points), PAP-38 (audit), PAP-61 (access history embed).

**Agent**

Built by Forge (lead) with Iris (Component Crafter) on the page. Reviewed by Sentinel (Security Auditor, Visual Inspector).

**Size**

M: plugin wiring plus one dense settings page and a recovery flow.
