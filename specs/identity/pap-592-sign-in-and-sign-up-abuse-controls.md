---
identifier: "PAP-592"
title: "Sign-in and sign-up abuse controls: Turnstile challenge on public auth and forms, disposable-domain list, progressive lockout per email and IP, and `auth.lockout` security events"
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
blockedBy: ["PAP-223", "PAP-224"]
blocks: []
key: "r4/identity/auth-abuse-controls"
url: "https://linear.app/paperos/issue/PAP-592/sign-in-and-sign-up-abuse-controls-turnstile-challenge-on-public-auth"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:13.401Z"
model: "claude-opus-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-25"
cycle: null
---

# PAP-592: Sign-in and sign-up abuse controls: Turnstile challenge on public auth and forms, disposable-domain list, progressive lockout per email and IP, and `auth.lockout` security events

**Model / Effort:** Opus 5 (`claude-opus-5`) / medium — Build S

**Goal**

PAP-223 limits sign-in to ten attempts a minute and PAP-304 bounds requests, but magic-link floods, sign-up spam from disposable domains and slow credential stuffing across IPs are how public auth actually gets abused, and every public form (`/pay`, support chat, referral) inherits the problem. Add the standard controls once, behind the Better Auth `captcha` plugin and one lockout table.

**Scope**

In: `captcha({ provider: 'cloudflare-turnstile' })` in `packages/auth` for magic-link request, sign-up and passkey registration start, `<Challenge/>` component rendering Turnstile only when the server asks (risk-based: after 3 attempts per IP or when the IP is on a denylist), site and secret keys via PAP-17; `email_domain_policy` list (disposable domains from a maintained list refreshed weekly by a job, plus tenant allow and deny lists), lockout table `auth_lockout (subject_kind: email|ip, subject, until, attempts)` with progressive delays 1, 5, 15, 60 minutes, decoy-safe responses (same message for unknown and locked accounts), security events `auth.lockout`, `auth.captcha_failed`, `auth.disposable_blocked` (PAP-356), docs section.

Out: Rate limiting itself (PAP-558), device fingerprinting, bot management at the edge, marketing form spam (PAP-193 reuses `<Challenge/>`).

**Spec**

* Challenge decisions come from the server: `auth.challengeRequired({ action, ip, email })`; the client shows Turnstile only then; tokens verified server-side with a 5-minute validity and single use.
* Lockout counts failed magic-link verifications, TOTP and backup-code attempts (PAP-580) and passkey ceremony failures; success resets the counter; locked subjects receive the same neutral message and a `Retry-After`.
* Disposable-domain block applies to sign-up and invitations by default; tenant owners may disable it or add domains; the list source and refresh job are documented.
* Every control has a `SEC-AUTH-*` id in PAP-219 `controls.yaml`; events route to PAP-356 with the pinned-issue escalation for bursts.
* Test mode (PAP-240) bypasses Turnstile with a documented header so e2e suites run unattended.

**Interface contract**

Provides: Plugin config, `<Challenge/>`, `challengeRequired()`, table `auth_lockout`, table `email_domain_policy` and job `auth.refreshDisposableList`, security events above, env `TURNSTILE_SITE_KEY`, `TURNSTILE_SECRET_KEY`.

Consumes: Better Auth server and pages (PAP-223, PAP-224), env schema (PAP-17), rate limits (PAP-558, soft), jobs (PAP-43, soft), security telemetry (PAP-356, soft), controls (PAP-219), test mode (PAP-240). Consumed by PAP-580, PAP-193 forms, PAP-396 public pay pages, PAP-411 chat capture.

**Definition of done**

* Fourth failed attempt from one IP triggers the challenge; a Turnstile failure is refused; test-mode bypass works (Playwright with the Turnstile test keys).
* Sign-up with a disposable domain refused; tenant allowlist overrides (tests); lockout escalates 1, 5, 15, 60 minutes and resets on success (fake clock).
* Events visible in the security dashboard; controls listed; docs; changelog under Security; Security Auditor signs off on the neutral-message behaviour.

**Test plan**

* Unit: challenge decision table, lockout schedule and reset, domain list matching including subdomains, token single-use.
* E2E: magic-link flood from one IP hits the challenge; sign-up with `mailinator.com` refused; locked account shows the neutral message.

**Demo**

Request five magic links for a fake address from the sign-in page, watch the challenge appear on the fourth, fail it and read the neutral message; then try a disposable domain on sign-up. Under two minutes.

**Edge cases**

* Shared NAT (school, office): lockout per email escalates faster than per IP; challenge rather than block for IP-only signals.
* Turnstile unreachable: fail open with an event and stricter lockout for the incident window; never a dead sign-in page.
* Tauri WebView: Turnstile renders in the system browser flow (PAP-225) not in-app.

**Dependencies**

Blocked by PAP-223 and PAP-224 (hard). Soft: PAP-17, PAP-43, PAP-219, PAP-240, PAP-356, PAP-558. Consumed by PAP-580, PAP-193, PAP-396, PAP-411.

**Agent**

Builder: Forge (Platform Engineer). Reviewer: Sentinel (Security Auditor).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 2 round-4 file keys in this description to Linear identifiers: `r4/data-layer/rate-limits` = PAP-558, `r4/identity/mfa-recovery` = PAP-580.
