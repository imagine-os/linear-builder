---
identifier: "PAP-808"
title: "In-app messages and announcements: banner, modal and tooltip messages targeted by segment and route, scheduling and approval, frequency caps and view or dismiss stats"
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
blockedBy: ["PAP-64", "PAP-195", "PAP-401"]
blocks: []
key: "r4/growth/in-app-messages-and-announcements"
url: "https://linear.app/paperos/issue/PAP-808/in-app-messages-and-announcements-banner-modal-and-tooltip-messages"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:20:07.099Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 3
dueDate: null
cycle: null
---

# PAP-808: In-app messages and announcements: banner, modal and tooltip messages targeted by segment and route, scheduling and approval, frequency caps and view or dismiss stats

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build M

**Goal**

Deferred to v0.2 by the Execution Schedule (NJ-14 stop-loss 09-27 can reinstate). Not claimable before 10-01.

PAP-195's demo shows a portal banner gated by `useInSegment`, but no issue lets a marketer create that banner. In-app messaging (Intercom, [Customer.io](<http://Customer.io>)) is the cheapest channel because it needs no consent for product updates and no deliverability; it needs a composer, targeting and stats.

**Scope**

In: `inapp_message (kind: banner|modal|tooltip|checklist_step, title, body_json, cta { label, url }, targeting { segmentId?, audiences[], routes[] }, schedule { starts_at, ends_at }, frequency { max_views, cooldown_days }, status: draft|pending_approval|live|ended)`; `inapp_impression (message_id, user_id, viewed_at, dismissed_at, clicked_at)`; delivery hook `<InAppMessages />` in the portal (PAP-64) and console shells via the `shell.banner` slot and route matching; targeting evaluation through PAP-195 `contains` under 20 ms; approval binding a content hash (PAP-401 pattern); stats dataset; composer with live preview at portal widths.

Out: mobile push (PAP-381 push transport is the future carrier), product tours with multi-step anchoring (v0.3), email fallback.

**Spec**

* Messages render from the design system components only (PAP-237 Dialog, Toast, banner) so they inherit theme and accessibility; no raw HTML.
* Frequency caps evaluated client-side from a per-user impression cache and enforced server-side on write.
* Content agent drafts land in `pending_approval` through `ContentDraftPort`.

**Interface contract**

Provides: `inapp.*`, `<InAppMessages />`, slot fill `shell.banner:inapp`, dataset `growth.inappStats`, event `inapp.message.viewed|clicked`. Consumes: segments (PAP-195), portal shell and slots (PAP-64, PAP-438 slot runtime), approval pattern (PAP-401), overlay components (PAP-237), content agent (PAP-192, soft), attribution (PAP-194, soft).

**Definition of done**

* Targeting and cap unit tests; Playwright: create, approve, see it as a segment member in the portal, dismiss, not see it again; screenshots at 320, 375, 768, 1024, 1920 light and dark; axe clean.
* `docs/growth/in-app-messages.md`; CHANGELOG.

**Test plan**

* Unit: route matching, schedule window, frequency caps, hash binding, targeting evaluation.
* E2E: the Playwright flow above with a portal user who is and is not in the segment.

**Demo**

Reviewer composes a banner for the 'Trial ending' segment, approves it, logs in as a member and sees it, dismisses it and reloads. Under two minutes.

**Edge cases**

* User in two overlapping messages: priority order, one banner at a time, modals never stack.
* Segment evaluation stale: the message uses the last known membership with a 'may be stale' indicator in stats.
* Message ended while open: dismissed on next route change.

**Dependencies**

Hard: PAP-195, PAP-64, PAP-401. Soft: PAP-438, PAP-237, PAP-192, PAP-194.

**Agent**

Builder: Beacon (Campaign Composer). Reviewer: Sentinel (Visual Inspector, Code Reviewer).

**Size**

M: one session.
