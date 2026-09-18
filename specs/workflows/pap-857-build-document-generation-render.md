---
identifier: "PAP-857"
title: "Build document generation: render templates to PDF and DOCX, a generated documents library on the file entity, bulk generation jobs, attach to records and share links"
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
blockedBy: ["PAP-37", "PAP-43", "PAP-172", "PAP-235", "PAP-565", "PAP-624", "PAP-847", "PAP-856"]
blocks: ["PAP-858", "PAP-861"]
key: "r4/workflows/document-generation"
url: "https://linear.app/paperos/issue/PAP-857/build-document-generation-render-templates-to-pdf-and-docx-a-generated"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:51:48.843Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 3
dueDate: null
cycle: null
---

# PAP-857: Build document generation: render templates to PDF and DOCX, a generated documents library on the file entity, bulk generation jobs, attach to records and share links

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build M

**Goal**

Turn a template plus a record into a file people can send: PDF through the PAP-235 `renderPdf` and DOCX through `docx` so tenants can edit offline, a generated documents library backed by the `file` entity with versions and metadata, bulk generation as a job with progress, attachment to the source record, and share links with the PAP-172 token rules.

**Scope**

In: `DocumentTemplatePort.render(templateId, recordRef, { format: 'pdf'|'docx'|'html' })` and `generate` (persisting a `generated_document` row: `template_version`, `record`, `file_id`, `format`, `hash`, `generated_by`); PDF via headless Chromium (PAP-235), DOCX via `docx` 9.x mapping the Tiptap JSON; HTML for email bodies. Library page `/console/documents` (grid view on the `generated_document` dataset) with preview (PDF viewer), regenerate, download, share; record panel tab `documents` (PAP-333 slot) listing documents for a record. Bulk: `documents.generateBulk(templateId, viewId)` as a PAP-43 job with progress over PAP-381, a zip download and per-record attachment; used by the `document.generate` step kind. Share links `/d/:token` (PAP-172 token semantics, expiry, password) with a download audit row.

Out: Signing (next issue). Editing generated DOCX back into templates.

**Spec**

* Generation is deterministic for a given template version, record snapshot and locale; the `hash` lets e-sign prove what was signed
* Fonts: the print kit's font set plus a CJK fallback; PDF/A-2b output flag for archival templates
* Bulk jobs respect the tenant storage entitlement (PAP-178 `storageGb`) and stop with a clear message when exceeded
* Generated documents inherit the record's permissions for viewing; sharing outside requires `documents.share`

**Interface contract**

Provides: `DocumentTemplatePort.render|generate|generateBulk`, `generated_document` dataset and library page, record tab, `/d/:token`, `document.generated` event. Consumes: templates, print kit (PAP-235), files (PAP-37), jobs and progress (PAP-43, PAP-381), share tokens (PAP-172), record panel tabs (PAP-333), entitlements (PAP-178). Consumed by: PAP-858, step kind `document.generate`, commerce estimates and packing slips, engagement certificates, scheduled view delivery (PAP-639).

**Definition of done**

* PDF and DOCX generated for the five seed templates with identical content; bulk run over 200 records finishes under 3 minutes on staging with progress; share link audited
* Every new page has a `page.spec.yaml` (PAP-114) that passes the validator, declared loading, empty, error and denied states, and Gate 3 screenshots at 375, 768, 1024 and 1920 in light and dark themes.
* Linear comment on the issue with the evidence links (PR, gate artefacts, recording or report) and the module docs page updated where the interface changed.

**Test plan**

* Unit: Tiptap → DOCX mapping for every node type; hash stability; entitlement stop.
* Integration: bulk job resumes after a worker restart without duplicates; share token expiry; record permission inheritance.
* Isolation: the PAP-34 cross-tenant harness auto-enrols every new table; one negative case per new oRPC procedure proves `NOT_FOUND` on a foreign tenant row.

**Demo**

Generate a proposal PDF from a quote, download the DOCX, run a bulk generation of 50 renewal letters from a saved view, and share one with an expiring link.

**Edge cases**

* Template version retired between bulk start and finish: the job pins the version at start and finishes consistently
* Chromium crash mid-render: the job retries the item once, then marks it failed with the error in the run log
* Module disabled for the tenant (PAP-266): routes return `MODULE_DISABLED` (409), slot fills unmount and the manifest declares the dependency so consumers fail closed rather than half-render.

**Dependencies**

PAP-856 (hard), PAP-235 (hard), PAP-37, PAP-43 (hard), PAP-172, PAP-333, PAP-381 (soft).

**Agent**

Builder: Ledger. Reviewer: Sentinel (Code Reviewer).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 3 round-4 file keys in this description to Linear identifiers: `r4/tables/scheduled-view-delivery` = PAP-639, `r4/workflows/document-templates` = PAP-856, `r4/workflows/esign-core` = PAP-858.
