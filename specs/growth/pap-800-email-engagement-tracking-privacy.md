---
identifier: "PAP-800"
title: "Email engagement tracking: privacy-respecting open pixel and click wrapping with per-tenant toggle, bot filtering, activity and segment feeds"
project: "growth"
projectName: "Growth: Marketing, Outreach & CRM"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Staff"]
milestone: "Acquisition analytics"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-194", "PAP-404"]
blocks: []
key: "r4/growth/email-engagement-tracking"
url: "https://linear.app/paperos/issue/PAP-800/email-engagement-tracking-privacy-respecting-open-pixel-and-click"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:45.585Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: null
cycle: null
---

# PAP-800: Email engagement tracking: privacy-respecting open pixel and click wrapping with per-tenant toggle, bot filtering, activity and segment feeds

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

Deferred to v0.2 by the Execution Schedule (NJ-14 stop-loss 09-27 can reinstate). Not claimable before 10-01.

Sequences and campaigns report sent and bounced; reps and marketers act on opened and clicked. A first-party tracker consistent with the PAP-194 privacy stance (no third-party, consent-aware, bot-filtered) closes the loop without inviting a compliance problem.

**Scope**

In: `/t/o/:token.gif` open pixel and `/t/c/:token` click redirect on the PAP-194 collector origin; token signed per message and link; `outreach_message.events` and `campaign_recipient.events` updated; `crm_activity kind email` gains `opened_at`, `clicked_at`; bot filtering (Apple Mail Privacy Protection proxy ranges and known scanners flagged `machine_open`); per-tenant toggles (opens, clicks, both off) and per-contact `essential-only` consent mode disables tracking; segment operators `opened email in last N days` via PAP-195 extension hook; links rewritten at render time in PAP-404 templates with an allowlist for untracked links.

Out: heatmaps, third-party pixels, ad platform pixels.

**Spec**

* Redirect resolves in under 50 ms from a signed token with no database write on the hot path (event queued to PAP-43).
* Opens from machine proxies are stored but excluded from 'opened' counts by default with a toggle.
* Tracking domain is the tenant's sending domain when DNS is set (CNAME), else the platform domain, so DMARC alignment holds.

**Interface contract**

Provides: tracking routes, `wrapLinks(html, messageId)`, events `email.opened|clicked`, segment operators, tenant settings. Consumes: templates and messages (PAP-404), collector origin and privacy modes (PAP-194), segments hook (PAP-195), consent centre, jobs (PAP-43), sending domain (PAP-405).

**Definition of done**

* Unit and integration green; latency test for the redirect; bot list fixtures; screenshots of the settings and a contact timeline with engagement at 375, 1024.
* `docs/growth/engagement-tracking.md` with the privacy notice text; CHANGELOG.

**Test plan**

* Unit: token signing, link rewriting with allowlist, bot classification, consent mode gating.
* E2E: send a sandbox sequence email, open the pixel and click a link from Playwright, see the activity update and a segment membership change.

**Demo**

Reviewer opens a sandbox email preview, clicks a tracked link and watches the contact timeline show the click. Under one minute.

**Edge cases**

* Link already tracked by an external tool: allowlisted domains left untouched.
* Token replay after 30 days: 404, no event.
* Tenant turns tracking off: existing wrapped links still redirect, record nothing.

**Dependencies**

Hard: PAP-404, PAP-194. Soft: PAP-195, PAP-405, PAP-43, PAP-791.

**Agent**

Builder: Beacon (Outreach Sequencer). Reviewer: Sentinel (Security Auditor for privacy).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/growth/consent-compliance-centre` = PAP-791.
