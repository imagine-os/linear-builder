---
identifier: "PAP-854"
title: "Build the forms builder schema and runtime: multi-page forms, conditional logic, field types from the tables engine, validation, uploads, submissions to a dataset or a workflow"
project: "workflows"
projectName: "Workflows, Approvals, Forms, Documents & E-Signature"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Staff"]
milestone: "Forms builder and document templates"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-37", "PAP-169", "PAP-233", "PAP-338", "PAP-339", "PAP-620", "PAP-660", "PAP-847", "PAP-848"]
blocks: ["PAP-855", "PAP-861"]
key: "r4/workflows/forms-schema-runtime"
url: "https://linear.app/paperos/issue/PAP-854/build-the-forms-builder-schema-and-runtime-multi-page-forms"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:51:26.667Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: null
cycle: null
---

# PAP-854: Build the forms builder schema and runtime: multi-page forms, conditional logic, field types from the tables engine, validation, uploads, submissions to a dataset or a workflow

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Grow the PAP-169 form view into a real forms product without a second field system: a `FormDefinition` with pages, sections and logic over the tables field types, a renderer that works in the portal, in public pages and embedded, server-side validation, uploads through PAP-37, and a submission pipeline that writes to any dataset, starts a workflow, or both.

**Scope**

In: `packages/workflows/src/forms/`: `FormDefinition` (`pages[]`, `blocks[]` of `field | text | image | divider | payment | signature`, `logic[]` rules `when FilterTree → show|hide|require|jumpTo`, `submitTo: { dataset?, mapping, workflow? }`, `settings` for confirmations, limits, languages), `form_submission` (`payload`, `files[]`, `status received|processed|failed|spam`, `source`, `submitter`). Renderer `<FormRunner/>` on PAP-233 form-state adapters and the PAP-338/339 field editors in `form` mode; autosave drafts for signed-in users; progress bar; i18n through PAP-27 with per-language copy fields (PAP-375 pattern). Builder page `/console/forms/:id/edit`: page list, block palette, field settings panel (shared `FieldSettingsPanel` PAP-339), logic editor on the PAP-166 filter builder, preview at widths. Submission pipeline: server validation against the definition, PAP-37 file completion, mapping into `records.create` (PAP-342 path) or `workflows.start` with `form` trigger; `form.submitted` event.

Out: Publishing, embeds, anti-spam and payments (next issue). Survey analytics (engagement).

**Spec**

* Logic evaluates client-side for UX and server-side for truth with the PAP-279 in-memory evaluator; a hidden required field is never required
* Mapping supports constant values, submitter identity, UTM and referrer (PAP-194) and expression transforms; unmapped fields stay in `payload`
* Uploads: presigned direct upload, per-form size and type limits, files attached to the created record (PAP-339 attachment type) and scanned by PAP-574 when present
* Accessibility: one question per focus, error summary at the top, labels bound, keyboard and screen reader tested (PAP-156)
* Drafts for signed-in submitters persist 30 days; anonymous drafts stay in `localStorage` only

**Interface contract**

Provides: `FormPort.define|submit|submissions`, `FormDefinition` and `form_submission` schemas, `<FormRunner/>`, builder page, `form` workflow trigger, `form.submitted` event. Consumes: form view baseline (PAP-169), field types and settings panel (PAP-338, PAP-339), files (PAP-37), form adapters (PAP-233), filter builder and evaluator (PAP-166, PAP-279), i18n (PAP-27, PAP-375), record create path (PAP-342). Consumed by: PAP-855, engagement surveys and intake, commerce work-order checklists, growth landing forms (PAP-193 migrates to `FormRunner`), human task forms.

**Definition of done**

* A three-page intake form with logic creates a patient record and starts a workflow in the demo tenant; the builder round-trips the definition; axe clean; screenshots at 375 and 1024
* Every new page has a `page.spec.yaml` (PAP-114) that passes the validator, declared loading, empty, error and denied states, and Gate 3 screenshots at 375, 768, 1024 and 1920 in light and dark themes.
* Linear comment on the issue with the evidence links (PR, gate artefacts, recording or report) and the module docs page updated where the interface changed.

**Test plan**

* Unit: logic evaluation parity client/server over 30 rule fixtures; mapping transforms; draft expiry.
* E2E: fill with a screen reader script (PAP-156), upload two files, submit, verify record and run; resume a draft after reload.
* Isolation: the PAP-34 cross-tenant harness auto-enrols every new table; one negative case per new oRPC procedure proves `NOT_FOUND` on a foreign tenant row.

**Demo**

Build a clinic intake form with a conditional allergies page, publish internally, fill it on a phone with two photo uploads, and watch the record and workflow appear.

**Edge cases**

* Definition changed after a draft was saved: the runner migrates the draft by field id and shows what was dropped
* Dataset field type converted (PAP-340) after mapping: submission fails validation visibly and the builder flags the mapping
* Module disabled for the tenant (PAP-266): routes return `MODULE_DISABLED` (409), slot fills unmount and the manifest declares the dependency so consumers fail closed rather than half-render.

**Dependencies**

PAP-848 (hard), PAP-169, PAP-338, PAP-339 (hard), PAP-37, PAP-233 (hard), PAP-27, PAP-375 (soft).

**Agent**

Builder: Nova. Reviewer: Sentinel (Edge Case Hunter).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 3 round-4 file keys in this description to Linear identifiers: `r4/data-layer/file-scanning-previews` = PAP-574, `r4/workflows/forms-publishing` = PAP-855, `r4/workflows/workflow-model` = PAP-848.
