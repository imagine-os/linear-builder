---
identifier: "PAP-900"
title: "Build abuse and signup-fraud controls: CaptchaPort, disposable-email and velocity checks, verification gates, tenant quarantine, outbound sending reputation guard, report-abuse endpoint and review queue"
project: "platform-ops"
projectName: "Platform Operations, Analytics & Compliance"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Staff"]
milestone: "Product analytics, experiments and abuse controls"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-57", "PAP-226", "PAP-304", "PAP-356", "PAP-405", "PAP-432", "PAP-558", "PAP-674", "PAP-893", "PAP-894"]
blocks: ["PAP-907"]
key: "r4/platform-ops/abuse-controls"
url: "https://linear.app/paperos/issue/PAP-900/build-abuse-and-signup-fraud-controls-captchaport-disposable-email-and"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:51:46.522Z"
model: "claude-opus-5"
effort: "high"
estimate: 3
dueDate: null
cycle: null
---

# PAP-900: Build abuse and signup-fraud controls: CaptchaPort, disposable-email and velocity checks, verification gates, tenant quarantine, outbound sending reputation guard, report-abuse endpoint and review queue

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Build M

**Goal**

Keep free signups and public forms from turning PaperOS into a spam relay or a fraud tool: a `CaptchaPort` (Turnstile adapter) on signup, public forms and booking pages, disposable-email and velocity checks at signup, email verification before any outbound sending, a tenant risk score that quarantines suspicious tenants (no outbound email, SMS, webhooks or Connect payouts until reviewed), an outbound reputation guard that pauses sending on bounce and complaint spikes (extending PAP-405 warmup), a `report-abuse` endpoint on every public page and email footer, and a review queue in `/admin`.

**Scope**

In: `packages/platform-ops/src/abuse/`: `CaptchaPort` (`turnstile`, `noop`), `checkSignup({ email, ip, userAgent, fingerprintHash })` scoring disposable domains (maintained list plus MX heuristics), velocity per IP and ASN (PAP-304 counters), known-bad lists; `tenant_risk` (score, factors, state normal|watch|quarantined|banned, reviewer notes). Gates: signup (PAP-57 hooks) requires captcha above a risk threshold and email verification always before outbound capabilities; quarantined tenants get `FORBIDDEN_QUARANTINED` on `sendEmail` (PAP-370), outreach (PAP-404), webhooks (PAP-222), payouts (PAP-181) with a banner explaining review; public forms and booking pages call the captcha port when the tenant or the platform enables it. Reputation guard: per-tenant bounce and complaint rates from PAP-370 suppression events and PAP-405 metrics; thresholds pause sending and notify; recovery requires a review or a cool-down. `POST /api/v1/public/report-abuse` with a token identifying the message or page; review queue `/admin/abuse` with evidence, actions (quarantine, ban, clear), audit; security events `abuse.flagged|quarantined` (PAP-356).

Out: Payment fraud (Stripe Radar and PAP-408 rules). Content moderation of tenant data beyond reports.

**Spec**

* Risk scoring is explainable: every score lists its factors; no opaque third-party score in v0.2
* Quarantine never deletes or hides tenant data and never blocks the tenant's own users from logging in; it blocks outbound side effects only
* False-positive path: quarantined tenants can request review in-app; SLA 1 business day with a Needs Justin escalation on day 2
* Captcha is invisible-first (Turnstile managed mode); accessibility fallback documented; never on authenticated staff flows
* All lists (disposable domains, bad ASNs) are versioned files reviewed by Scout monthly (PAP-218 routine)

**Interface contract**

Provides: `AbusePort` and `CaptchaPort` default adapters, `tenant_risk`, signup and outbound gates, reputation guard, report-abuse endpoint, `/admin/abuse` queue, `abuse.*` events. Consumes: super-admin console, rate limits (PAP-304), outreach compliance and warmup (PAP-405), security telemetry (PAP-356), auth hooks (PAP-57), tenant lifecycle states (PAP-432), email suppression (PAP-370), webhooks (PAP-222), payouts (PAP-181). Consumed by: workflows forms publishing (`CaptchaPort`), engagement booking pages and feedback board, growth outreach (reputation guard), business-core payouts (quarantine gate), identity signup (PAP-57).

**Definition of done**

* Signup with a disposable email from a high-velocity IP is challenged and then quarantined on staging; quarantined tenant cannot send email or trigger webhooks and sees the banner; a bounce spike pauses sending; a report lands in the queue and is cleared with audit
* Every new page has a `page.spec.yaml` (PAP-114) that passes the validator, declared loading, empty, error and denied states, and Gate 3 screenshots at 375, 768, 1024 and 1920 in light and dark themes.
* Linear comment on the issue with the evidence links (PR, gate artefacts, recording or report) and the module docs page updated where the interface changed.

**Test plan**

* Unit: risk factors and score; thresholds; list parsing.
* Integration: gates on `sendEmail`, outreach, webhooks, payouts; reputation pause and recovery; report token validation.
* E2E: signup challenge flow with Turnstile test keys; review queue actions.
* Isolation: the PAP-34 cross-tenant harness auto-enrols every new table; one negative case per new oRPC procedure proves `NOT_FOUND` on a foreign tenant row.

**Demo**

Sign up five tenants from one IP with throwaway addresses; watch the fourth get a captcha and the fifth land in quarantine; try to send a campaign from it and see the block; clear it from the queue.

**Edge cases**

* Legitimate agency creating many client tenants: an allow-listed platform partner flag bypasses velocity but not verification
* Shared corporate NAT IP: velocity uses IP plus fingerprint plus email domain, and the threshold for known corporate ASNs is higher
* Module disabled for the tenant (PAP-266): routes return `MODULE_DISABLED` (409), slot fills unmount and the manifest declares the dependency so consumers fail closed rather than half-render.

**Dependencies**

PAP-894 (hard), PAP-304, PAP-405, PAP-356 (hard), PAP-57, PAP-432, PAP-370 (hard), PAP-222, PAP-181 (soft).

**Agent**

Builder: Sentinel. Reviewer: Forge.

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/platform-ops/superadmin-console` = PAP-894.
