---
identifier: "PAP-640"
title: "Geocoding job: fill geo fields from address fields through a provider adapter (Nominatim self-hosted or Mapbox) with caching and rate limits"
project: "tables"
projectName: "Table & Views Engine"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Staff"]
milestone: "View sharing, formulas, dashboards"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-43", "PAP-121", "PAP-565", "PAP-622"]
blocks: []
key: "r4/tables/geocoding-job"
url: "https://linear.app/paperos/issue/PAP-640/geocoding-job-fill-geo-fields-from-address-fields-through-a-provider"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:20:34.240Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: null
cycle: null
---

# PAP-640: Geocoding job: fill geo fields from address fields through a provider adapter (Nominatim self-hosted or Mapbox) with caching and rate limits

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

Deferred to v0.2 (NJ-19; reinstate via NJ-14). A map view is only useful if addresses become coordinates. Add a geocoding provider port and a job that fills `geo` fields from configured address fields, with caching so imports of 10k customers do not cost 10k calls.

**Scope**

In: `GeocodingPort { geocode(address) -> { lat, lng, precision } | null }` in `contract-tables`; adapters `nominatim` (self-hosted container in `ops/compose`, default) and `mapbox` (API key via PAP-121 connector); `geo` option `{ sourceFields: fieldId[], autoGeocode }`; job `fields.geocode` batched 50 with provider rate limits; `geocode_cache (hash, result)` table.

Out: reverse geocoding, address validation UI, routing, autocomplete inputs.

**Spec**

* On record create or update touching `sourceFields`, enqueue a geocode when `autoGeocode`; a "Geocode all" column-menu action runs the job over the view's rows (cap 10k per run, progress and cancel).
* Cache keyed by normalised address hash with 90-day TTL; results carry `precision` (`rooftop|street|city`) shown as a pin style; failures leave `geo` empty and write `geocode_failed` in a warnings column visible in the record panel.
* Provider rate limits per adapter (Nominatim 1 rps, Mapbox per key) enforced by PAP-43 concurrency and `pg-boss` throttling; costs recorded as connector usage (PAP-121).
* Privacy: addresses flagged `pii` (PAP-355) are geocoded only through the self-hosted adapter unless the tenant enables external providers.

**Interface contract**

Provides: `GeocodingPort`, adapters, job `fields.geocode`, `geo.sourceFields` option, `geocode_cache`. Consumes: `geo` type and map view (map issue), jobs (PAP-43), connector registry and secrets (PAP-121), PII annotations (PAP-355), compose stack (PAP-42).

**Definition of done**

* Port, two adapters and job green with recorded HTTP fixtures; Nominatim container in compose; `docs/views/geocoding.md`; CHANGELOG.

**Test plan**

* Unit: address normalisation and hashing; precision mapping; TTL expiry; PII routing rule.
* Integration: 1,000 records with 300 distinct addresses produce 300 provider calls; cancel mid-run leaves consistent rows.
* E2E: enable auto-geocode on the demo clients, edit an address, see the pin move on `/demo/map`.

**Demo**

Reviewer runs "Geocode all" on 50 demo clients and watches the map fill in. Under two minutes.

**Edge cases**

* Ambiguous address: lowest precision stored with a warning.
* Provider down: retries on the jobs schedule, banner in the map view.

**Dependencies**

Map issue (hard), PAP-43 (hard), PAP-121 (hard). Soft: PAP-355, PAP-42. Deferred; nothing waits on it.

**Agent**

Builder: Nova (Views Engineer) with Forge on the container. Reviewer: Sentinel (Security Auditor).

**Size**

S: half a session.
