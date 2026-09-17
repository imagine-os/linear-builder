---
identifier: "PAP-407"
title: "Referral programs, codes, /r/{code} route, attribution window and the qualification worker"
project: "growth"
projectName: "Growth: Marketing, Outreach & CRM"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Customer"]
milestone: "Acquisition analytics"
state: "Backlog"
parent: "PAP-196"
children: []
blockedBy: ["PAP-177", "PAP-484"]
blocks: ["PAP-408"]
key: "growth/referral/codes-attribution"
url: "https://linear.app/paperos/issue/PAP-407/referral-programs-codes-rcode-route-attribution-window-and-the"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T15:00:38.913Z"
model: "claude-sonnet-5"
effort: "low"
---

# PAP-407: Referral programs, codes, /r/{code} route, attribution window and the qualification worker

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / low — Deferred label (excluded from Oct-1 scope)

**Goal**

Attribute signups and first payments to referral codes reliably, within a program's rules.

**Scope**

In: `referral_program`, `referral_code`, `referral`; `/r/{code}` click route; `referralTokenFromRequest`; qualification worker on signup and `invoice.paid`. Out: rewards, payouts, UI (siblings). Deferred with the parent.

**Spec**

* Codes 8-character Crockford base32, vanity codes with a profanity filter; 30-day window, last click wins unless a code was entered at checkout.
* Click route records an `attr_event` (PAP-194 channel `affiliate`), sets the token, redirects; signup (PAP-57 children) and Checkout (PAP-177) stamp `referral`.
* Worker moves `signed_up` to `qualified` on the first paid invoice.

**Interface contract**

Provides: tables, `referrals.programs|codes.*`, route, `referralTokenFromRequest`, event `referral.qualified`. Consumes: PAP-194, PAP-57, PAP-177, PAP-187.

**Definition of done**

* Code and window tests; worker tests; click to qualified in an integration test.

**Test plan**

* Unit: code normalisation, precedence, window expiry.
* Integration: click, signup, `stripe trigger invoice.paid` yields `qualified`.

**Demo**

Open `/r/DEMO123`, sign up, trigger payment, see `qualified`.

**Edge cases**

* Existing customer as referee rejected; 1,000 signups a day pause rewards not signups (sibling).

**Dependencies**

PAP-177, PAP-187, PAP-194 (soft), PAP-57 children. Blocks siblings.

**Agent**

Builder: Beacon (CRM Builder). Reviewer: Sentinel.

**Size**

M: deferred.
