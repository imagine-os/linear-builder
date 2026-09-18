---
identifier: "PAP-885"
title: "Build assets and work orders: asset registry with locations and warranties, maintenance schedules on the recurrence engine, work orders with checklists, parts and labour, mobile technician flow with photos, signatures and invoicing"
project: "commerce"
projectName: "Commerce, Operations & Vertical Packs"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Staff"]
milestone: "Orders, POS, purchasing, projects and HR"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-170", "PAP-260", "PAP-395", "PAP-622", "PAP-879", "PAP-883"]
blocks: ["PAP-889"]
key: "r4/commerce/assets-work-orders"
url: "https://linear.app/paperos/issue/PAP-885/build-assets-and-work-orders-asset-registry-with-locations-and"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:51:26.667Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 3
dueDate: null
cycle: null
---

# PAP-885: Build assets and work orders: asset registry with locations and warranties, maintenance schedules on the recurrence engine, work orders with checklists, parts and labour, mobile technician flow with photos, signatures and invoicing

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build M

**Goal**

Serve trades, field service, facilities and property management: an asset registry (equipment, units, vehicles) with locations, QR labels and warranties, maintenance schedules on the recurrence engine that generate work orders, work orders with checklists (forms runtime), parts from inventory and labour from time entries, a phone-first technician flow with photos, customer signature and status updates, and invoicing of completed work through PAP-395.

**Scope**

In: `AssetsPort`: `assets` (kind, location or property unit, customer owner `fin_party`, serial, purchase and warranty, custom fields via PAP-332), `schedules` (RRULE-based preventive maintenance creating work orders N days ahead), `workOrders` (status new|scheduled|in_progress|on_hold|completed|invoiced, assignee, scheduled window via the booking engine when present, checklist form, parts lines reserving stock, labour via time entries, photos, customer signature via e-sign or an in-app signature capture fallback). Pages: `/assets` (grid, map view PAP-170 by location, asset detail with history), `/work-orders` (board and calendar), technician mobile route `/wo/:id` (offline-capable via PAP-148: checklist, camera PAP-260, parts scan, signature, complete); customer portal shows their assets and work order history. Invoicing: `completeAndInvoice` builds a PAP-395 invoice from parts (catalog prices) and labour (rate card) with the checklist and photos attached; estimates as quotes (PAP-395 quote → acceptance via e-sign).

Out: Route optimisation and dispatch boards beyond assignment and map (v0.3). IoT telemetry ingestion (webhook trigger only).

**Spec**

* Parts used on a work order are `sale` movements from the technician's van location or the main store; unused reserved parts release on completion
* Checklists are form definitions; a work order type binds a form version; completion requires required items; photos are attached to answers
* Preventive schedules generate work orders idempotently per `(schedule, occurrence)`; skipped occurrences are recorded
* Customer-facing status updates use notification kinds `workorder.scheduled|en_route|completed` with quiet hours

**Interface contract**

Provides: `AssetsPort` default adapter, tables and datasets, pages and technician route, portal views, `workorder.*` events, schedule job. Consumes: catalog and inventory (parts), projects (labour), recurrence engine, camera and geolocation (PAP-260), offline outbox (PAP-148), map view (PAP-170), documents and quotes (PAP-395), forms runtime and e-sign (workflows, soft), custom fields (PAP-332), booking engine (soft). Consumed by: packs (trades, construction, property management, gym equipment), assistant ("when was the boiler last serviced?"), platform-ops (none).

**Definition of done**

* Plumber demo: 30 assets across 10 properties on the map, a quarterly schedule generating work orders, a technician completes one on a phone offline with two photos, parts and a signature, syncs, and invoices it; portal shows the history
* Every new page has a `page.spec.yaml` (PAP-114) that passes the validator, declared loading, empty, error and denied states, and Gate 3 screenshots at 375, 768, 1024 and 1920 in light and dark themes.
* Linear comment on the issue with the evidence links (PR, gate artefacts, recording or report) and the module docs page updated where the interface changed.

**Test plan**

* Unit: schedule occurrence idempotency; checklist completion rules; parts movement and release.
* E2E: technician route at 375 offline then online; map view; invoice from work order.
* Isolation: the PAP-34 cross-tenant harness auto-enrols every new table; one negative case per new oRPC procedure proves `NOT_FOUND` on a foreign tenant row.

**Demo**

Open the work-order board, take the boiler service on a phone, go offline, tick the checklist, photograph the serial plate, scan a part, get the customer's signature, reconnect, and invoice.

**Edge cases**

* Asset transferred to another customer: history stays with the asset; open work orders re-bind to the new owner only with confirmation
* Technician completes offline while the office cancels the work order: on sync the completion wins with a conflict flag (PAP-144 banner) for the office to resolve
* Module disabled for the tenant (PAP-266): routes return `MODULE_DISABLED` (409), slot fills unmount and the manifest declares the dependency so consumers fail closed rather than half-render.

**Dependencies**

PAP-879 and PAP-883 (hard), PAP-260, PAP-148, PAP-170, PAP-395 (hard), PAP-908 (hard), workflows forms and e-sign (soft).

**Agent**

Builder: Nova. Reviewer: Sentinel (Edge Case Hunter).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 3 round-4 file keys in this description to Linear identifiers: `r4/commerce/catalog-inventory` = PAP-879, `r4/commerce/projects-time-billing` = PAP-883, `r4/data-layer/recurrence-engine` = PAP-908.
