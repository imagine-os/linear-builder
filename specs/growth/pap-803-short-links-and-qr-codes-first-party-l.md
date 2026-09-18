---
identifier: "PAP-803"
title: "Short links and QR codes: first-party /l/:code redirects with click attribution, optional Dub adapter, UTM builder and printable QR for offline campaigns"
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
blockedBy: ["PAP-188", "PAP-194"]
blocks: []
key: "r4/growth/short-links-and-qr"
url: "https://linear.app/paperos/issue/PAP-803/short-links-and-qr-codes-first-party-lcode-redirects-with-click"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:20:09.994Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: null
cycle: null
---

# PAP-803: Short links and QR codes: first-party /l/:code redirects with click attribution, optional Dub adapter, UTM builder and printable QR for offline campaigns

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

Deferred to v0.2 by the Execution Schedule (NJ-14 stop-loss 09-27 can reinstate). Not claimable before 10-01.

Social posts, printed menus, flyers and SMS need short trackable links. PAP-188 hypothesises Dub via API; whichever it decides, the CRM needs a link object whose clicks land in attribution and whose QR codes work on a restaurant table.

**Scope**

In: `short_link (code, target_url, utm jsonb, campaign_id?, owner, clicks, status, expires_at?)`; `/l/:code` redirect on the public routes with PAP-267 rate limits recording an `attr_event` (`link_clicked`) with channel classification; `ShortLinkPort` with `first_party` and `dub` adapters (Dub in `dryRun` until a key exists); UTM builder component used by PAP-401 composer, PAP-404 templates and campaigns; QR generation (`qrcode` package) as SVG and PNG with tenant colours and a print sheet; link analytics dataset.

Out: custom domains per tenant beyond a CNAME instruction, link retargeting pixels.

**Spec**

* Codes are 7-character Crockford base32, case-insensitive, profanity filtered (shared with PAP-407); vanity codes unique per tenant.
* Redirect is a 302 with no cookies; the click event carries `referrer_host` and `device_class` only (PAP-194 privacy rules).
* QR SVG passes a contrast check against the tenant background token.

**Interface contract**

Provides: `links.*`, redirect route, `ShortLinkPort`, `UtmBuilder`, `QrCode` component, dataset `growth.linkClicks`. Consumes: attribution collector and classification (PAP-194), stack decision (PAP-188), rate limits (PAP-267), composer and templates (PAP-401, PAP-404, soft), profanity filter (PAP-407, soft).

**Definition of done**

* Redirect latency under 50 ms in a bench; click events appear in `attr.channels`; QR decodes in a test with `jsqr`; screenshots at 375, 1024.
* `docs/growth/links.md`; CHANGELOG.

**Test plan**

* Unit: code generation and collisions, UTM merge precedence, QR contrast, expiry.
* E2E: create a link with UTM, print the QR sheet, scan it via a fixture decode, follow the redirect and see the click on the attribution report.

**Demo**

Reviewer creates `/l/menu`, downloads the QR, opens the link and sees one click in the channel report under `offline`. Under one minute.

**Edge cases**

* Target URL changed after clicks: history kept, new clicks go to the new target.
* Expired link: 410 page with tenant branding.
* Dub outage: first-party fallback records the click and syncs later.

**Dependencies**

Hard: PAP-194, PAP-188. Soft: PAP-267, PAP-401, PAP-404, PAP-407.

**Agent**

Builder: Beacon (Campaign Composer). Reviewer: Sentinel (Code Reviewer).

**Size**

S: half a session.
