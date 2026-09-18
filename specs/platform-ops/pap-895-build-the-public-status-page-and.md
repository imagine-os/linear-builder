---
identifier: "PAP-895"
title: "Build the public status page and incident comms: components, incidents with updates, scheduled maintenance, subscribers by email, SMS and RSS, fed by observability alerts and security S0 events, with per-tenant embedding"
project: "platform-ops"
projectName: "Platform Operations, Analytics & Compliance"
phase: "P2"
type: "Build"
priority: 3
surfaces: ["Customer"]
milestone: "Ops contract, super-admin console and status page"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-26", "PAP-40", "PAP-136", "PAP-356", "PAP-370", "PAP-674", "PAP-725", "PAP-893"]
blocks: ["PAP-904", "PAP-907"]
key: "r4/platform-ops/status-page"
url: "https://linear.app/paperos/issue/PAP-895/build-the-public-status-page-and-incident-comms-components-incidents"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:51:37.704Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 3
dueDate: "2026-10-01"
cycle: null
---

# PAP-895: Build the public status page and incident comms: components, incidents with updates, scheduled maintenance, subscribers by email, SMS and RSS, fed by observability alerts and security S0 events, with per-tenant embedding

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build M

**Goal**

Tell customers the truth when something breaks: a public status page at `status.<PAPEROS_DOMAIN>` (and embeddable per tenant) listing components (web, API, sync, jobs, payments, email, desktop updates), incidents with timeline updates and templates, scheduled maintenance windows, subscriber notifications by email, SMS (when the channel exists) and RSS, and automatic incident drafts from PAP-40 alert rules and PAP-356 S0 events so the page is never silent while Grafana is red.

**Scope**

In: `packages/platform-ops/src/status/`: tables `status_component`, `status_incident` (severity, affected components, status investigating|identified|monitoring|resolved, updates\[\], postmortem link), `status_maintenance`, `status_subscriber` (email or phone, verified, components); `StatusPort` adapter; public routes `/status`, `/status/incidents/:id`, `/status/history`, `/status/rss` server-rendered static HTML with a 60 s cache, hosted from a separate static path so it stays up when the app is down (PAP-26 deploys it to Pages as well as the VPS). Feeds: Grafana alert webhook (PAP-40) and PAP-356 S0 events create a draft incident in `/admin/status` with the affected component pre-selected; a human publishes; auto-resolve suggestion when the alert clears; uptime per component computed from alert history and health checks (PAP-269 `/api/health`). Comms: templates per incident stage with plain-language guidance (Quill reviews), subscriber notifications through PAP-370 and the notification kinds registry (`status.incident.*`) with double opt-in; tenant embed `<StatusBadge/>` and a `/portal` banner hook when a component the tenant uses is degraded.

Out: Third-party status aggregation. Postmortem authoring (docs engine PAP-128 holds them; the page links).

**Spec**

* The status page has no dependency on the API at read time: it is regenerated as static files on every change and on a 5-minute schedule; a stale marker appears if regeneration fails
* Incident updates are append-only; corrections are new updates; resolved incidents stay in history for 90 days on the page and forever in the dataset
* Subscriber PII lives under PAP-355 rules; unsubscribe is one click; SMS requires the messaging channel module and consent
* Severity maps to PAP-79 taxonomy; S0 incidents also open the pinned Linear issue path (PAP-356) automatically

**Interface contract**

Provides: `StatusPort` default adapter, tables and dataset, public static status pages and RSS, admin incident editor, notification kinds `status.*`, `<StatusBadge/>`, `status.incident.*` events. Consumes: alerting (PAP-40), security S0 events (PAP-356), email (PAP-370), notifications (PAP-136), deploy pipeline and Pages (PAP-26), health endpoint (PAP-269), severity taxonomy (PAP-79), docs engine for postmortems (PAP-128). Consumed by: PAP-904 (uptime), PAP-89 release digest (incident section), tenants (embed and banner), quality release train (maintenance windows for RC deploys).

**Definition of done**

* Status page live on staging and Pages; a simulated PAP-40 alert drafts an incident, a human publishes two updates, subscribers receive them, RSS validates, badge renders in the portal; page loads with the API stopped
* Every new page has a `page.spec.yaml` (PAP-114) that passes the validator, declared loading, empty, error and denied states, and Gate 3 screenshots at 375, 768, 1024 and 1920 in light and dark themes.
* Linear comment on the issue with the evidence links (PR, gate artefacts, recording or report) and the module docs page updated where the interface changed.

**Test plan**

* Unit: uptime computation; static regeneration; template rendering.
* Integration: alert webhook → draft; S0 → draft plus pinned issue; double opt-in; unsubscribe.
* E2E: public page at 375 and 1920; admin editor flow; screenshots.

**Demo**

Fire a test alert for the sync component, publish the drafted incident with an update, receive the subscriber email in Mailpit, then stop the API container and reload the status page to show it still serves.

**Edge cases**

* Incident spans a maintenance window: the page shows both with the maintenance context; uptime excludes announced maintenance per the SLA definition (documented)
* Alert flapping: drafts are deduplicated per component per hour; the editor shows the flap count
* Module disabled for the tenant (PAP-266): routes return `MODULE_DISABLED` (409), slot fills unmount and the manifest declares the dependency so consumers fail closed rather than half-render.

**Dependencies**

PAP-893 (hard), PAP-40, PAP-356 (hard: feeds), PAP-370, PAP-136 (hard), PAP-26, PAP-269 (soft).

**Agent**

Builder: Forge. Reviewer: Sentinel (Code Reviewer).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 2 round-4 file keys in this description to Linear identifiers: `r4/platform-ops/contract-publish` = PAP-893, `r4/platform-ops/trust-center` = PAP-904.
