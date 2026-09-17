---
identifier: "PAP-333"
title: "Build record-level features shared by every module: record detail page and panel routing, activity timeline, attachments tab, per-record comments and field history with undo"
project: "tables"
projectName: "Table & Views Engine"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Staff", "Customer"]
milestone: "All view types"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-38", "PAP-165", "PAP-483"]
blocks: ["PAP-102", "PAP-189"]
key: "gap/tables/record-detail"
url: "https://linear.app/paperos/issue/PAP-333/build-record-level-features-shared-by-every-module-record-detail-page"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T15:00:32.576Z"
model: "claude-sonnet-5"
effort: "high"
---

# PAP-333: Build record-level features shared by every module: record detail page and panel routing, activity timeline, attachments tab, per-record comments and field history with undo

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Give every dataset one record surface, `/records/$table/$id`, that CRM, PM, finance and custom tables reuse: header, fields form, activity timeline, attachments, comments and field history with undo, so no module builds its own detail page.

**Scope**

In: routes `/records/$dataset/$id` and the `?r=` panel mode; `packages/views/src/record/` (`RecordPage`, `RecordHeader`, `RecordFields`, `ActivityTimeline`, `AttachmentsTab`, `FieldHistory`); procedures `records.history|undo|related`; page spec `specs/pages/tables/record.page.spec.yaml` with per-dataset overrides. Out: module-specific layouts beyond slots (PAP-189 adds CRM slots), comment engine (PAP-131), audit storage (PAP-38).

**Spec**

* Layout via PAP-70 `SplitPane` and `Inspector`: header (title field, status chip, owner, actions), left fields form using PAP-164 editors grouped by `FieldGroup`, right tabs Activity, Comments, Attachments, History; under `md` tabs stack and the panel becomes a drawer.
* Activity merges `audit_event` rows (PAP-38), comments (PAP-131) and module events (`crm_activity`, `document.*`) through a `registerActivitySource(dataset, fn)` hook into one PAP-71 `Timeline`.
* History: per-field diff list from audit rows; `records.undo({ recordId, auditEventId })` writes the previous value as a new update with reason `undo:<eventId>`; only the latest change per field is undoable by default.
* Attachments tab lists every attachment field's files with upload and preview (PAP-37).
* Related records: `records.related` lists inverse relations grouped by dataset as embedded views (PAP-165 embedded mode).
* Deep links `?r=<id>` open the panel on any view; `/records/...` is the full page; both share state.
* Permissions from the dataset (`<entity>.read|update`); history visible to `update` holders.

**Interface contract**

Provides: `RecordPage`, `RecordPanel` (supersedes the PAP-165 stub), `registerActivitySource`, `registerRecordSlot(dataset, slot, component)`, procedures `records.history|undo|related`, route pattern `/records/$dataset/$id`. Consumes: editors (PAP-164), grid embedded mode (PAP-165), audit (PAP-38), comments (PAP-131), files (PAP-37), layouts (PAP-70), `Timeline` (PAP-71), conflict UX (PAP-144). Consumed by PAP-189 company and deal pages, PAP-102 issue detail, PAP-180 document detail, PAP-334 (restore from history).

**Definition of done**

* Vitest, integration and Playwright below green.
* Screenshots at 375, 768, 1024, 1440, 1920 in three themes for page and panel; axe clean.
* `docs/views/record-detail.md` (adding a slot or activity source); CHANGELOG; Linear comment with demo link.

**Test plan**

* Unit: history diff builder, undo eligibility, activity merge ordering, slot registry.
* Integration: undo writes the prior value and an audit row with the reason; related records respect RLS; activity source from a module appears in order.
* E2E: open a record from the grid, edit two fields, undo one from History, upload an attachment, add a comment, open the same record via `/records/...` and `?r=`.
* Visual: matrix above.

**Demo**

Reviewer expands a row in `/demo/grid`, edits a field in the panel, opens History and clicks Undo, then switches to the full page and adds a comment that appears in the timeline. Under two minutes.

**Edge cases**

* Record deleted while open: removed state with restore if trashed.
* Field changed by two users: undo targets the actor's own change and warns about the newer one.
* 10k audit rows: history paginated by field.
* Dataset without a title field uses the id and suggests setting one.
* Customer audience opening a staff record: 403 page via `can()`.

**Dependencies**

PAP-165 (hard), PAP-38 (hard), PAP-164, PAP-70, PAP-71, PAP-131 and PAP-37 (soft slots), PAP-144. Blocks PAP-189, PAP-102 detail pages.

**Agent**

Builder: Nova (Views Engineer) with Iris on layout. Reviewer: Sentinel (Visual Inspector, Code Reviewer).

**Size**

M: composition of existing pieces plus history and undo semantics.
