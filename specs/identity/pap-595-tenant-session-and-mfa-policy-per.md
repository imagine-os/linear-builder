---
identifier: "PAP-595"
title: "Tenant session and MFA policy: per-audience idle and absolute timeouts, MFA required for staff and admins, trusted devices, sign-up domain allowlist and IP allowlist for staff, enforced by `requireSession`"
project: "identity"
projectName: "Identity, Roles & Audiences"
phase: "P2"
type: "Build"
priority: 3
surfaces: ["Staff"]
milestone: "Agent principals and enterprise"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-578", "PAP-580", "PAP-581"]
blocks: []
key: "r4/identity/session-policy"
url: "https://linear.app/paperos/issue/PAP-595/tenant-session-and-mfa-policy-per-audience-idle-and-absolute-timeouts"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:13.745Z"
model: "claude-opus-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-30"
cycle: null
---

# PAP-595: Tenant session and MFA policy: per-audience idle and absolute timeouts, MFA required for staff and admins, trusted devices, sign-up domain allowlist and IP allowlist for staff, enforced by `requireSession`

**Model / Effort:** Opus 5 (`claude-opus-5`) / medium — Build S

**Goal**

Better Auth gives one global session length (30 days, PAP-223). A clinic wants staff sessions to expire after 15 idle minutes and admins to have MFA; a retail portal wants customers to stay signed in for a month. Auth0 and WorkOS expose these as tenant policies; without them every app patches `requireSession`.

**Scope**

In: `tenant.settings.sessionPolicy` Zod schema `{ byAudience: { [audienceId]: { idleMinutes, absoluteHours, requireMfa, trustedDeviceDays } }, signUpDomains?: { allow?: string[], deny?: string[] }, staffIpAllowlist?: CIDR[] }`, enforcement in `requireSession` and `withTenant` (`SESSION_EXPIRED_IDLE`, `MFA_REQUIRED`, `IP_NOT_ALLOWED` errors), `session.lastActivityAt` updates throttled to once a minute, trusted-device cookie signed per device after MFA, console settings section 'Security policy' (registered in PAP-582), docs section.

Out: TOTP itself (PAP-580), enterprise SSO enforcement (PAP-232), device attestation.

**Spec**

* Resolution: the strictest matching audience rule wins for a principal in several audiences; platform floors (customers at least 5 idle minutes, staff at most 30 days absolute) documented and enforced.
* `requireMfa: true` returns `MFA_REQUIRED` until the session has a second factor; the client routes to two-factor setup; agents are exempt (keys) but audited.
* Trusted devices: after MFA the client receives a signed device cookie valid `trustedDeviceDays`; revocation from the sessions page clears it.
* IP allowlist applies to staff and admin audiences only; evaluated from Caddy's forwarded address; owners are warned when enabling a list that would lock them out (current IP not included).
* Policy changes publish `permission.changed` so open sessions re-evaluate on the next request; changes are audited with reason.

**Interface contract**

Provides: Schema `SessionPolicy`, errors above, `resolveSessionPolicy(principal)`, trusted-device cookie helper, settings section, docs.

Consumes: Sessions and step-up (PAP-581), MFA (PAP-580), tenancy settings (PAP-578), audiences (PAP-55), console frame (PAP-582, soft), propagation (PAP-591, soft), audit (PAP-38). Consumed by PAP-62, PAP-63, PAP-232 enforcement later.

**Definition of done**

* Staff session idle past 15 minutes returns `SESSION_EXPIRED_IDLE` and the client redirects; customer session unaffected (fake clock, two audiences).
* `requireMfa` for admins blocks until setup; trusted device skips the prompt for the configured days; IP allowlist lockout warning shown (tests).
* Settings section at 768 and 1280; docs; changelog under Security.

**Test plan**

* Unit: strictest-rule resolution, floors, idle and absolute arithmetic, CIDR matching for IPv4 and IPv6, lockout warning logic.
* E2E: admin enables MFA requirement and a 15-minute idle timeout; a seeded staff member is prompted for setup and later expires; a customer stays signed in.

**Demo**

Set staff idle to 1 minute in the console, sign in as staff in another window, wait, click and land on sign-in; then require MFA for admins and see the setup prompt. Under two minutes.

**Edge cases**

* Policy tightened while a user is mid-flow: next request applies it; unsaved form data preserved by the shell's re-auth flow.
* Owner enables an IP allowlist that excludes them: refused with the current IP shown.
* Tauri bearer sessions: idle tracked the same way; absolute expiry clears Stronghold on next launch.

**Dependencies**

Blocked by PAP-581, PAP-580, PAP-578 (hard). Soft: PAP-55, PAP-38, PAP-582, PAP-591.

**Agent**

Builder: Forge (Platform Engineer). Reviewer: Sentinel (Security Auditor).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 5 round-4 file keys in this description to Linear identifiers: `r4/identity/console-frame` = PAP-582, `r4/identity/mfa-recovery` = PAP-580, `r4/identity/permission-propagation` = PAP-591, `r4/identity/sessions-stepup` = PAP-581, `r4/identity/tenancy-core` = PAP-578.
