---
identifier: "PAP-580"
title: "TOTP second factor with backup codes, the `/auth/recover` flow that requires TOTP or a code before a new passkey, and the new-device, two-factor-enabled and recovery-used emails"
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
blockedBy: ["PAP-57", "PAP-223", "PAP-224", "PAP-456"]
blocks: ["PAP-581", "PAP-595"]
key: "r4/identity/mfa-recovery"
url: "https://linear.app/paperos/issue/PAP-580/totp-second-factor-with-backup-codes-the-authrecover-flow-that"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:11.359Z"
model: "claude-opus-5"
effort: "high"
estimate: 3
dueDate: "2026-09-25"
cycle: null
---

# PAP-580: TOTP second factor with backup codes, the `/auth/recover` flow that requires TOTP or a code before a new passkey, and the new-device, two-factor-enabled and recovery-used emails

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Build M

**Goal**

First half of PAP-220: the way back in. Passkey-first sign-in (PAP-57) is only safe to rely on when a lost device does not lock a person out for good. This child adds TOTP and single-use recovery codes through Better Auth's `twoFactor()` plugin, a recovery flow that proves possession of a second factor before a new passkey may be registered, and the three security emails.

**Scope**

In: `twoFactor({ issuer: appName, otpOptions: { period: 30, digits: 6 }, backupCodes: { amount: 10, length: 10 } })` in `packages/auth/src/server.ts`, tables `twoFactor` and `backupCode` (hashed), pages `/auth/two-factor/setup`, `/auth/two-factor/verify`, `/auth/recover` with specs, `TwoFactorSetup` (QR via `qrcode`, confirm code, codes shown once, regenerate), React Email `new-device.tsx`, `two-factor-enabled.tsx`, `recovery-used.tsx` through `sendEmail` (PAP-370, soft), audit events `auth.2fa.enabled|disabled`, `auth.recovery.used`, rate limits on `/auth/recover`.

Out: Session and device listing, step-up and the `SecurityPage` (sibling PAP-581), SMS factors, hardware-key attestation policies, enterprise MFA enforcement (PAP-595).

**Spec**

* TOTP verification accepts one step either side (±30 s), never more; a used step cannot be replayed within its window; backup codes hashed with argon2id and single use; regeneration invalidates all previous codes.
* Recovery: email magic link first, then TOTP or a backup code, then passkey registration; every step audited with `request_id`; the flow cannot be started for an account without a second factor (it explains the support path).
* Rate limits: 5 verification attempts per 15 minutes per account and per IP (`rateLimit` from PAP-558, soft: plugin limiter until then); lockout emits `auth.lockout` (PAP-592).
* Emails carry device label, approximate location (country from IP only), time and a 'this was not me' link that opens the sessions page of the sibling.
* Enabling two-factor requires a recent authentication (`requireRecentAuth`, sibling; soft: re-prompt passkey inline until it lands).

**Interface contract**

Provides: Plugin config, tables above, pages and specs, `TwoFactorSetup`, `useTwoFactor()`, audit event kinds, email templates, `verifyTotp()` and `consumeBackupCode()` for the sibling's `ReauthDialog`.

Consumes: Better Auth server (PAP-223), auth pages and `authClient` (PAP-224), email (PAP-370, soft), rate limits (PAP-558, soft), audit (PAP-38, soft), primitives (PAP-67). Consumed by the sibling, PAP-62, PAP-63, PAP-595.

**Definition of done**

* Enable TOTP, sign out, sign in with magic link plus TOTP (Playwright with `oathtool`-style generator); a reused code is refused.
* Recovery: delete the only passkey in a test, recover with a backup code, register a new passkey; used codes cannot be reused; 6th attempt in 15 minutes is refused.
* Emails render in preview and arrive in Mailpit with the correct device label; audit events present.
* Screenshots of setup and recover pages at 375, 768, 1280 light and dark; axe clean; Sentinel Security Auditor signs off on hashing and limits; docs `docs/platform/account-security.md` sections 'Two-factor' and 'Recovery'.

**Test plan**

* Unit: TOTP window arithmetic with a fake clock, replay refusal, backup code hashing and single use, rate-limit counters, email props mapping.
* E2E: the enable, sign-in and recovery flows at 375 and 1280 on the ephemeral stack with Mailpit.

**Demo**

Sign in, enable two-factor with the QR, sign out and back in with a code, then run the recovery flow after deleting the passkey in a test account. Under two minutes.

**Edge cases**

* Authenticator time drift beyond one step: refused with a hint to check device time.
* User loses passkey and all codes: no self-service path; support impersonation cannot bypass; documented Needs Justin manual path.
* Tauri WebKitGTK without WebAuthn (PAP-225): TOTP becomes the primary second factor; setup page detects it.
* Email provider down: enabling two-factor still succeeds; the notice is queued (PAP-370 job).

**Dependencies**

Blocked by PAP-223 and PAP-224 (hard). Soft: PAP-370, PAP-38, PAP-67, PAP-558, PAP-592. Consumed by the sibling PAP-581.

**Agent**

Builder: Forge (Platform Engineer) with Iris on pages. Reviewer: Sentinel (Security Auditor).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 4 round-4 file keys in this description to Linear identifiers: `r4/data-layer/rate-limits` = PAP-558, `r4/identity/auth-abuse-controls` = PAP-592, `r4/identity/session-policy` = PAP-595, `r4/identity/sessions-stepup` = PAP-581.
