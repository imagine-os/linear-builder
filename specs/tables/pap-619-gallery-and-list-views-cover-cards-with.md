---
identifier: "PAP-619"
title: "Gallery and list views: cover cards with virtualised rows, dense phone list with swipe actions and grouped headers"
project: "tables"
projectName: "Table & Views Engine"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Customer"]
milestone: "All view types"
state: "Backlog"
parent: "PAP-169"
children: []
blockedBy: ["PAP-163", "PAP-337", "PAP-339", "PAP-614", "PAP-615", "PAP-645", "PAP-652"]
blocks: ["PAP-620"]
key: "r4/tables/gallery-and-list-views"
url: "https://linear.app/paperos/issue/PAP-619/gallery-and-list-views-cover-cards-with-virtualised-rows-dense-phone"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:17.611Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: "2026-09-29"
cycle: null
---

# PAP-619: Gallery and list views: cover cards with virtualised rows, dense phone list with swipe actions and grouped headers

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

First half of PAP-169: the two presentation views. Gallery is the card grid with covers directories and catalogues use; list is the dense vertical feed that makes every dataset usable at 320 px and inside sidebars, and whose rows the calendar agenda (PAP-344) reuses.

**Scope**

In: `packages/views/src/views/gallery/{GalleryView,GalleryCard,register}.tsx`, `views/list/{ListView,ListRow,register}.tsx`; options schemas; `onFilter` on group headers; Storybook stories.

Out: form view and public submission (sibling), card template editor beyond field pick (PAP-167 `CardTemplateEditor` reused), attachment lightbox (design-system).

**Spec**

* Gallery options `{ coverField?, coverFit: 'cover'|'contain', cardSize: 'sm'|'md'|'lg', cardFields (max 6), titleField?, showEmptyFields, colorField? }`; CSS `grid-template-columns: repeat(auto-fill, minmax(200|280|360px, 1fr))`, rows virtualised with `@tanstack/react-virtual`; cover from an attachment's `variants.md` (PAP-37) or a url field; click opens `RecordPanel` (PAP-343); keyboard grid navigation.
* List options `{ titleField, subtitleField?, metaFields (max 3), avatarField?, dense }`; rows 56 or 72 px; grouped sticky headers with counts from `views.groups`; two configurable swipe actions (leading, trailing) via `SwipeableRow` (PAP-154) with the same actions in an overflow Menu; works at 320 px.
* Both register through `registerViewKind` with `requiredFieldTypes: []`, `supports: { groups: true, onFilter: true, embedded: true }`; pages of 50 with "Load more" and prefetch.
* Group header click emits `onFilter({ fieldId, op: 'is', value })` for dashboards; empty states from PAP-71 with the `empty` illustration.

**Interface contract**

Provides: `<GalleryView />`, `<ListView />`, `ListRow` (reused by PAP-344 agenda), options schemas `galleryOptionsSchema`, `listOptionsSchema`, registrations. Consumes: `views.query|groups` (PAP-337), cells and attachment variants (PAP-339, PAP-37), `RecordPanel` (PAP-343), `SwipeableRow` (PAP-154, soft: overflow Menu only until it lands), `ViewHost` registry (PAP-614), `EmptyState` (PAP-71). Consumed by PAP-344, PAP-189 contacts, PAP-62 portal lists.

**Definition of done**

* Vitest and Playwright below green; stories at 320, 375, 768, 1024, 1440, 1920 in three themes; axe clean.
* `docs/views/gallery-list.md`; CHANGELOG; Linear comment with `/demo/gallery` and `/demo/list`.

**Test plan**

* Unit: options validation; card field truncation; row height selection; swipe action config; group header aggregation.
* Integration: 10k-record seed renders gallery with under 60 DOM cards and list with under 40 DOM rows; group headers match `views.groups`.
* E2E: scroll the gallery to card 5,000 under 2 s, open a record, switch to list at 375 px, swipe a row to archive (touch emulation) and undo from the toast; keyboard-only run.

**Demo**

Reviewer opens `/demo/gallery`, resizes cards to large, switches to list on a phone viewport and swipes a row. Under two minutes.

**Edge cases**

* Missing or failed cover: placeholder illustration, no layout shift.
* Title field archived: falls back to the first text field with a banner.
* RTL: swipe directions and card order flip.
* Offline: cached pages render, swipe actions queue through the outbox (PAP-272) with a pending badge.

**Dependencies**

PAP-337 (hard), PAP-339 (hard, attachment cells), PAP-614 (hard). Soft: PAP-154, PAP-343, PAP-272. Feeds PAP-344 agenda rows (soft); blocks the form sibling (shared card styles).

**Agent**

Builder: Nova (Views Engineer); Iris on card styling. Reviewer: Sentinel (Visual Inspector).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/tables/view-renderer-registry-and-host` = PAP-614.
