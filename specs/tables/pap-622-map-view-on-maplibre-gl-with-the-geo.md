---
identifier: "PAP-622"
title: "Map view on MapLibre GL with the geo field type, clustering, bounds filter and rectangle select"
project: "tables"
projectName: "Table & Views Engine"
phase: "P2"
type: "Build"
priority: 3
surfaces: ["Staff"]
milestone: "All view types"
state: "Backlog"
parent: "PAP-170"
children: []
blockedBy: ["PAP-293", "PAP-338", "PAP-621"]
blocks: ["PAP-173", "PAP-386", "PAP-640", "PAP-885"]
key: "r4/tables/map-view-maplibre-and-geo-field"
url: "https://linear.app/paperos/issue/PAP-622/map-view-on-maplibre-gl-with-the-geo-field-type-clustering-bounds"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:18.633Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 3
dueDate: "2026-09-29"
cycle: null
---

# PAP-622: Map view on MapLibre GL with the geo field type, clustering, bounds filter and rectangle select

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build M

**Goal**

Map half of PAP-170: register the `geo` field type and a map view plotting records on vector tiles with clustering, a compiled bounding-box filter and cross-filter emission, so field-service, retail and clinic templates can see records on a map.

**Scope**

In: `packages/views/src/fields/geo.ts` (`{ lat, lng, label? }`); `views/map/{MapView,cluster,bounds,register}.tsx`; btree indexes on `lat|lng` casts; `isWithin` filter op; PNG export; no-WebGL fallback list.

Out: geocoding of address fields (PAP-640), choropleths, custom tile hosting beyond a PMTiles hook, routing.

**Spec**

* `geo` type: value `{ lat: number, lng: number, label?: string }`, parse from "lat, lng" strings and GeoJSON points, cell shows a static thumbnail or `lat, lng`, editor is a pin-drop mini map plus inputs; ops `isEmpty|isNotEmpty|isWithin(bounds)`; `sql.cast` extracts `(data->'location'->>'lat')::float8`.
* Map options `{ geoField, labelField?, colorField?, cluster: boolean, fitToData, basemap: 'light'|'dark'|'auto' }`; MapLibre GL JS 4.x with the OpenFreeMap `liberty` style, `basemap: auto` follows `data-theme`; hook `tiles.url` in config for self-hosted PMTiles.
* Data via `views.query` with the visible bounds compiled as `isWithin` on indexed casts (PAP-335 `ensureIndex`); page 2,000 points; `cluster: true` uses MapLibre clustering; above 50,000 matching rows the view asks for a filter first.
* Click a pin opens `RecordPanel`; Shift+drag rectangle emits `onFilter({ fieldId: geoField, op: 'isWithin', value: bounds })`; keyboard: Tab to the map, arrows pan, `+`/`-` zoom, Enter on a focused pin opens; `aria-label` lists visible count.
* Export: canvas PNG (`preserveDrawingBuffer` only during export); registered as `kind: 'map'` with `requiredFieldTypes: ['geo']`, lazy chunk.

**Interface contract**

Provides: `geo` FieldType, `<MapView />`, `mapOptionsSchema`, `isWithin` op, `boundsToFilter(bounds)`, registration. Consumes: field framework and cells (PAP-338), compiler ops and `ensureIndex` (PAP-335), `views.query` (PAP-337), `RecordPanel` (PAP-343), MapLibre ADR (PAP-293), export helpers and registration pattern (chart sibling), `ViewHost` registry. Consumed by PAP-386 dashboards, PAP-427 business packs (clinic, retail).

**Definition of done**

* Vitest and Playwright green with WebGL enabled in the Playwright image; stories at 375, 768, 1024, 1440, 1920 in three themes; map chunk lazy and under 400 KB gzip.
* `docs/views/map.md` with the tile hosting note; CHANGELOG; Linear comment with `/demo/map`.

**Test plan**

* Unit: geo parse from string and GeoJSON; bounds filter compilation; cluster option validation; theme-to-basemap mapping.
* Integration: bounds query uses the btree index (`EXPLAIN`); 10,000 seeded points cluster within 500 ms client time.
* E2E: open `/demo/map`, click a cluster to zoom, Shift-drag a rectangle and see the filter chip, open a pin's record, switch theme and see the basemap follow.

**Demo**

Reviewer opens `/demo/map`, clicks a cluster, draws a rectangle around a city and watches the grid block (in `/demo/dashboard`) filter to those rows. Under two minutes.

**Edge cases**

* No WebGL (kiosks, CI without GPU): static coordinate list with an explanation and the same `onFilter` from a bounds form.
* Records without coordinates: counted in an "unplaced" chip, filterable.
* Antimeridian-crossing bounds: split into two ranges.
* Tile server unreachable: pins still render on a blank canvas with a banner.

**Dependencies**

PAP-621 (hard, shared helpers), PAP-338 (hard), PAP-293 (hard, MapLibre ADR; default MapLibre if not merged by 09-26). Soft: PAP-343. Blocks PAP-386.

**Agent**

Builder: Nova (Views Engineer). Reviewer: Sentinel (Visual Inspector).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 2 round-4 file keys in this description to Linear identifiers: `r4/tables/chart-view-echarts` = PAP-621, `r4/tables/geocoding-job` = PAP-640.
