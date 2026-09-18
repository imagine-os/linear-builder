---
identifier: "PAP-856"
title: "Build document templates: template model with merge fields, conditional sections and repeating rows over datasets, a Tiptap template editor and versioning"
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
blockedBy: ["PAP-142", "PAP-235", "PAP-389", "PAP-395", "PAP-604", "PAP-848"]
blocks: ["PAP-857", "PAP-858"]
key: "r4/workflows/document-templates"
url: "https://linear.app/paperos/issue/PAP-856/build-document-templates-template-model-with-merge-fields-conditional"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:51:34.463Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 3
dueDate: null
cycle: null
---

# PAP-856: Build document templates: template model with merge fields, conditional sections and repeating rows over datasets, a Tiptap template editor and versioning

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build M

**Goal**

Let tenants write proposals, contracts, letters and certificates once and fill them from data: a `DocumentTemplate` edited in the PAP-142 editor with merge fields bound to a dataset and its relations, conditional sections, repeating rows for line items, branding from PAP-235, and versions, so PAP-395 invoices stay the specialised case while everything else uses this.

**Scope**

In: `document_template` (`name`, `dataset`, `body: Tiptap JSON`, `variables`, `version`, `status`, `pageSettings`), Tiptap extensions `mergeField` (`{{ contact.name }}` with picker over dataset fields and one-hop relations), `conditionalSection` (FilterTree on the record), `repeatingTable` (over a relation or view query), `signatureField` placeholder (consumed by e-sign), `pageBreak`. Editor page `/console/documents/templates/:id` with the field picker, sample-record preview (renders with a chosen record), branding preview from PAP-235 `PdfLayout`, version history and diff. Expression support through the PAP-389 template language for formatting (`money`, `date`, `upper`) and computed values; locale-aware via PAP-27. Template gallery seeded per business pack (PAP-427 `documents[]`): proposal, service agreement, consent, letter, certificate.

Out: Rendering and generation (next issue). Invoice layouts (PAP-396 owns).

**Spec**

* Merge fields resolve with the generating user's permissions; a field the user cannot read renders as a redaction marker, and the generation report lists them
* Repeating tables are bounded (1,000 rows) and paginate with header repeat in print
* Templates are immutable per version; generated documents record `template_version`
* The editor validates every merge path against the dataset schema on save; a renamed or converted field (PAP-340) marks the template `needs review`

**Interface contract**

Provides: `DocumentTemplatePort.define`, template schema and editor, Tiptap extensions, pack `documents[]` schema and five seed templates. Consumes: editor (PAP-142), print kit and branding (PAP-235), document numbering pattern (PAP-395), template expressions (PAP-389), locale helpers (PAP-27), dataset schema (PAP-161, PAP-340). Consumed by: PAP-857, PAP-858, commerce (estimates, work orders), engagement (consent forms, certificates), business packs.

**Definition of done**

* Five seed templates render with sample records; a renamed field flags the template; editor screenshots at 1024 and 1920
* Every new page has a `page.spec.yaml` (PAP-114) that passes the validator, declared loading, empty, error and denied states, and Gate 3 screenshots at 375, 768, 1024 and 1920 in light and dark themes.
* Linear comment on the issue with the evidence links (PR, gate artefacts, recording or report) and the module docs page updated where the interface changed.

**Test plan**

* Unit: merge path validation; conditional and repeating evaluation; redaction marker for unreadable fields.
* E2E: edit a template, insert a repeating table over invoice lines, preview with a record, publish a version, diff against the previous one.
* Isolation: the PAP-34 cross-tenant harness auto-enrols every new table; one negative case per new oRPC procedure proves `NOT_FOUND` on a foreign tenant row.

**Demo**

Open the proposal template, add a repeating table of quote lines and a conditional discount paragraph, preview with a real quote, publish.

**Edge cases**

* Record missing a relation (no company on a contact): sections referencing it collapse cleanly and the preview lists the empty paths
* Module disabled for the tenant (PAP-266): routes return `MODULE_DISABLED` (409), slot fills unmount and the manifest declares the dependency so consumers fail closed rather than half-render.

**Dependencies**

PAP-848 (soft: shares the module), PAP-142 (hard), PAP-235 (hard: layout kit; if still deferred, a minimal `PdfLayout` is built here and handed back), PAP-395, PAP-389 (soft).

**Agent**

Builder: Ledger. Reviewer: Sentinel (Code Reviewer).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 3 round-4 file keys in this description to Linear identifiers: `r4/workflows/document-generation` = PAP-857, `r4/workflows/esign-core` = PAP-858, `r4/workflows/workflow-model` = PAP-848.
