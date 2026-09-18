---
identifier: "PAP-804"
title: "NPS and CSAT surveys and review requests: one-question surveys after resolved conversations and paid invoices, response capture, detractor alerts and Google or Yelp review links"
project: "growth"
projectName: "Growth: Marketing, Outreach & CRM"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Customer"]
milestone: "Acquisition analytics"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-352", "PAP-370", "PAP-791"]
blocks: []
key: "r4/growth/nps-csat-and-review-requests"
url: "https://linear.app/paperos/issue/PAP-804/nps-and-csat-surveys-and-review-requests-one-question-surveys-after"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:46.781Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 3
dueDate: null
cycle: null
---

# PAP-804: NPS and CSAT surveys and review requests: one-question surveys after resolved conversations and paid invoices, response capture, detractor alerts and Google or Yelp review links

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build M

**Goal**

Deferred to v0.2 by the Execution Schedule (NJ-14 stop-loss 09-27 can reinstate). Not claimable before 10-01.

Every local business lives on reviews and every SaaS on NPS. Triggered one-question surveys after a support resolution or a paid invoice, with detractor alerts and a review-site handoff for promoters, close the loop between service and growth. PAP-352 decides whether Formbricks is embedded; this issue owns the CRM side either way.

**Scope**

In: `survey (kind: nps|csat|custom, trigger: support.conversation.resolved|invoice.paid|manual, delay_hours, channel: email|sms|in_app, question, follow_up_question, review_links jsonb { google, yelp, trustpilot }, status)`, `survey_response (survey_id, contact_id, score, comment, source_event, responded_at)`; public response page `/s/:token` (one click from the email) with follow-up comment; in-app variant through PAP-808 when present; sends through PAP-370 or PAP-405 SMS gated by `canContact('marketing'|'transactional' per tenant legal setting)`; detractor alert (score under 7) to the assignee via PAP-136; promoters see review links; datasets `growth.nps` with rolling 30-day score and a dashboard block; frequency cap per contact (one survey per 90 days).

Out: multi-question forms (PAP-169 forms), incentives for reviews (policy), public review widgets.

**Spec**

* Tokens are single-use per contact and survey; the response page stores no PII beyond the linked contact id.
* Whether NPS emails count as marketing or transactional is a tenant legal setting with jurisdiction defaults documented in `docs/growth/consent.md`.
* Formbricks adapter behind `SurveyPort` when PAP-352 says embed; `native` adapter otherwise; CI uses `native`.

**Interface contract**

Provides: `surveys.*`, response route, `SurveyPort`, datasets, block `growth.nps`, notification kind `survey.detractor`, activity source `survey.responded`. Consumes: consent centre, email (PAP-370), SMS (PAP-405, soft), OSS decision (PAP-352), support events (PAP-410, soft), invoice events (PAP-397, soft), notifications (PAP-136), dashboards (PAP-173).

**Definition of done**

* Trigger, delay, cap and gate tests; response round trip in sandbox; rolling NPS matches brute force; screenshots at 320, 375, 1024 light and dark for the response page (two brands) and the block.
* `docs/growth/surveys.md`; CHANGELOG.

**Test plan**

* Unit: trigger matching, delay scheduling, frequency cap, score maths, token single use.
* E2E: resolve a fixture conversation, advance the clock, open the sandbox email, click 9, see the promoter review links and the response on the contact.

**Demo**

Reviewer marks a conversation resolved, advances the clock, answers the survey from the outbound ledger preview and sees the NPS block update. Under two minutes.

**Edge cases**

* Contact answered 60 days ago: skipped by the cap with a log line.
* Score submitted twice: second ignored (single-use token).
* No review links configured: promoters see a thank-you only.

**Dependencies**

Hard: PAP-791, PAP-370, PAP-352. Soft: PAP-405, PAP-410, PAP-397, PAP-136, PAP-173, PAP-808.

**Agent**

Builder: Beacon (Campaign Composer). Reviewer: Sentinel (Security Auditor for the public route, Code Reviewer).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 2 round-4 file keys in this description to Linear identifiers: `r4/growth/consent-compliance-centre` = PAP-791, `r4/growth/in-app-messages-and-announcements` = PAP-808.
