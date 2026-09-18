---
identifier: "PAP-869"
title: "Build surveys, NPS and CSAT: templates on the forms runtime, triggers from bookings, tickets and orders through workflows, scoring, response views and Formbricks borrow notes"
project: "engagement"
projectName: "Scheduling, Messaging & Customer Engagement"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Customer"]
milestone: "Messaging channels, help center and surveys"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-136", "PAP-173", "PAP-195", "PAP-352", "PAP-387", "PAP-725"]
blocks: ["PAP-870"]
key: "r4/engagement/surveys-nps"
url: "https://linear.app/paperos/issue/PAP-869/build-surveys-nps-and-csat-templates-on-the-forms-runtime-triggers"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:51:34.463Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 3
dueDate: null
cycle: null
---

# PAP-869: Build surveys, NPS and CSAT: templates on the forms runtime, triggers from bookings, tickets and orders through workflows, scoring, response views and Formbricks borrow notes

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build M

**Goal**

Ask customers how it went without a third tool: NPS, CSAT and custom survey templates defined on the forms runtime, sent by email, SMS or shown in the portal after a booking completes, a ticket closes or an order ships (workflow triggers), with throttling so nobody is asked twice a month, scoring (NPS formula, CSAT averages), response datasets, dashboard blocks and segment feeds (PAP-195), borrowing the UX patterns the PAP-352 Formbricks spike recorded.

**Scope**

In: `survey` (template ref → `FormDefinition` with survey block types `nps`, `rating`, `csat`, `openText`; `trigger` config; `throttle`; `channels`), `survey_invite` (contact, token, channel, status), responses stored as form submissions tagged `survey_id` with derived `score` columns. Triggers: workflow step kind `survey.send` and standalone rules (`booking.completed`, `support.conversation.closed`, `order.fulfilled`) with delay; throttle per contact (default 30 days) and per tenant daily cap; consent via `canContact`. Delivery: email (PAP-370) with a one-click NPS row that records the score on click, SMS via messaging channels when present, portal card via `portal.home.cards`; token-authenticated public response page `/s/:token`. Analytics: datasets `survey_responses` with NPS score computed (promoters − detractors), CSAT average, trend chart blocks (PAP-173), verbatims view; low scores raise `survey.low_score` for follow-up workflows; `segments` rules can use last NPS score.

Out: Product-analytics style in-app micro-surveys targeting by behaviour (platform-ops experiments cover targeting; v0.3). Review sites (next issue).

**Spec**

* One-click email scoring is idempotent per invite; the follow-up question page loads with the score prefilled
* Responses are pseudonymous when the tenant enables `anonymousNps`: contact link dropped at write time, only segment attributes kept
* Throttle and consent checks happen at send time, not at trigger time, so a late unsubscribe is honoured
* NPS uses the standard 0 to 10 scale and formula; CSAT 1 to 5; both exposed as dataset fields so views and formulas (PAP-171) work

**Interface contract**

Provides: `SurveyPort.define|trigger|responses|score`, survey block types, `/s/:token`, datasets and dashboard blocks, `survey.responded|low_score` events, step kind `survey.send`. Consumes: forms runtime (PAP-854), OSS spike (PAP-352), notifications and email (PAP-136, PAP-370), dashboards (PAP-173), segments (PAP-195), messaging channels (soft), consent (PAP-187). Consumed by: PAP-870, growth segments and sequences, platform-ops tenant health (NPS as a signal), assistant summaries of verbatims.

**Definition of done**

* After a demo booking completes, an NPS email arrives, one click records a 9 and opens the follow-up; dashboard shows the trend; a low score triggers a follow-up task; throttle proven
* Every new page has a `page.spec.yaml` (PAP-114) that passes the validator, declared loading, empty, error and denied states, and Gate 3 screenshots at 375, 768, 1024 and 1920 in light and dark themes.
* Linear comment on the issue with the evidence links (PR, gate artefacts, recording or report) and the module docs page updated where the interface changed.

**Test plan**

* Unit: NPS and CSAT math; throttle windows; anonymisation.
* E2E: email one-click → follow-up page on a phone; portal card; verbatims view.
* Isolation: the PAP-34 cross-tenant harness auto-enrols every new table; one negative case per new oRPC procedure proves `NOT_FOUND` on a foreign tenant row.

**Demo**

Complete a booking in the demo tenant, receive the NPS email in Mailpit, click 9, add a comment, then watch the dashboard update and a detractor fixture open a follow-up task.

**Edge cases**

* Contact replies to an expired invite: the page thanks them and records nothing; the invite stays expired
* Same contact completes two bookings in a day: one invite, throttled correctly
* Module disabled for the tenant (PAP-266): routes return `MODULE_DISABLED` (409), slot fills unmount and the manifest declares the dependency so consumers fail closed rather than half-render.

**Dependencies**

PAP-854 (hard), PAP-136, PAP-370 (hard), PAP-352 (soft: borrowed patterns), PAP-173, PAP-195 (soft).

**Agent**

Builder: Beacon. Reviewer: Sentinel (Code Reviewer).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 2 round-4 file keys in this description to Linear identifiers: `r4/engagement/reviews-requests` = PAP-870, `r4/workflows/forms-schema-runtime` = PAP-854.
