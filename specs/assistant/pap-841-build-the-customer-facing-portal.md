---
identifier: "PAP-841"
title: "Build the customer-facing portal assistant: help-center grounding, account lookups, booking and payment handoffs, guardrails and escalation to the support inbox"
project: "assistant"
projectName: "Tenant AI Assistant & Business Agents"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Customer"]
milestone: "Actions, copilots and portal assistant"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-62", "PAP-304", "PAP-379", "PAP-411", "PAP-558", "PAP-585", "PAP-835", "PAP-838"]
blocks: ["PAP-842"]
key: "r4/assistant/portal-assistant"
url: "https://linear.app/paperos/issue/PAP-841/build-the-customer-facing-portal-assistant-help-center-grounding"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:51:41.818Z"
model: "claude-opus-5"
effort: "high"
estimate: 3
dueDate: null
cycle: null
---

# PAP-841: Build the customer-facing portal assistant: help-center grounding, account lookups, booking and payment handoffs, guardrails and escalation to the support inbox

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Build M

**Goal**

Give every tenant's customers a helpful, bounded assistant in the portal: grounded on the tenant's help center and the customer's own records (invoices, bookings, orders), able to hand off to booking and pay flows and to a human in the support inbox, and unable to see, say or do anything outside the customer audience.

**Scope**

In: `<PortalAssistant/>` filling `portal.assistant.widget` (bottom-right launcher, full-screen sheet on phones) in the PAP-62 portal, and an unauthenticated mode on public help-center pages limited to help-center grounding with email capture (PAP-411 pattern). Grounding scopes: help-center articles (PAP-379 published pages), the customer's own entities via the registry `audiences: [customer]`, tenant public FAQs; nothing else. Tools for customers: `read` lookups on own records, `openRoute` (navigate to invoice, booking), handoffs `startBooking` and `payInvoice` that open the existing flows (engagement booking pages, PAP-396 `/pay`), `escalate` that creates a support conversation with the transcript attached. Guardrails: refusal policy for out-of-scope topics with the tenant's escalation copy; rate limits per session and IP (PAP-304); tier-3 wrapping of everything; no memory across sessions for anonymous users. Tenant controls on `tenant_ai_settings`: `portalEnabled`, hours (outside hours the widget offers escalation only), languages, disclosure text ("You are chatting with an automated assistant").

Out: Staff features. Voice. Proactive outreach (never from the widget).

**Spec**

* Disclosure is always shown at conversation start and the assistant identifies itself as automated when asked; this is a conformance case (several jurisdictions require it)
* Escalation attaches the redacted transcript as an internal note (PAP-411 internal notes) and sets the conversation subject from the model summary; the customer sees "A person will reply" with the tenant SLA text
* Answer confidence: when grounding returns no chunk above the threshold the assistant says it does not know and offers escalation rather than improvising (eval-tested)
* Widget budget: under 40 KB gzipped, loads after the portal shell, no third-party scripts
* Anonymous sessions are keyed by a signed cookie, capped at 30 messages per hour and expire after 24 h; their transcripts are retained 7 days unless captured with an email

**Interface contract**

Provides: `<PortalAssistant/>`, `portal.assistant.widget` fill, customer tool set, `escalate` handoff, `assistant.escalated` event, unauthenticated help-center mode. Consumes: retrieval (own issue), action catalogue, portal shell (PAP-62), support chat widget and conversations (PAP-411, PAP-410), tenant docs (PAP-379), rate limits (PAP-304), pay pages (PAP-396). Consumed by: engagement help center and booking pages, commerce order lookups, growth support inbox.

**Definition of done**

* Customer in the demo tenant asks about an invoice, gets a cited answer, pays through the handoff, then escalates a second question which appears in the staff inbox with the transcript
* Leak test: 500 adversarial prompts (PAP-85 fixtures plus red-team set) produce zero staff-only or other-customer data; disclosure shown in 100 percent of sessions
* Every new page has a `page.spec.yaml` (PAP-114) that passes the validator, declared loading, empty, error and denied states, and Gate 3 screenshots at 375, 768, 1024 and 1920 in light and dark themes.
* Linear comment on the issue with the evidence links (PR, gate artefacts, recording or report) and the module docs page updated where the interface changed.

**Test plan**

* Unit: scope enforcement in grounding arguments; hours logic across timezones; anonymous rate limit and expiry.
* E2E: phone width full-screen sheet; keyboard and screen reader flow (PAP-156); escalation path; unauthenticated help-center mode with email capture.
* Isolation: the PAP-34 cross-tenant harness auto-enrols every new table; one negative case per new oRPC procedure proves `NOT_FOUND` on a foreign tenant row.

**Demo**

As a portal customer on a phone, ask "when is my next appointment and can I move it?"; the assistant answers with a citation and opens the reschedule flow; then ask about a refund and watch it hand off to a human.

**Edge cases**

* Customer belongs to two tenants (PAP-58): the widget is tenant-scoped by host and never mixes; switching tenants starts a new conversation
* Help center article updated during a conversation: subsequent turns cite the new version; earlier citations keep their chunk id and show "updated"
* Module disabled for the tenant (PAP-266): routes return `MODULE_DISABLED` (409), slot fills unmount and the manifest declares the dependency so consumers fail closed rather than half-render.

**Dependencies**

PAP-835 and PAP-838 (hard), PAP-62 (hard), PAP-411 and PAP-410 (hard for escalation), PAP-379 (soft: FAQs fallback), PAP-304 (hard).

**Agent**

Builder: Nova. Reviewer: Sentinel (Security Auditor).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 2 round-4 file keys in this description to Linear identifiers: `r4/assistant/action-catalogue` = PAP-838, `r4/assistant/retrieval-grounding` = PAP-835.
