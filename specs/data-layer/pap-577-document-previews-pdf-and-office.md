---
identifier: "PAP-577"
title: "Document previews: PDF and office thumbnails and page renders through a `files.preview` job, preview variants in `FileDto` and a viewer fallback"
project: "data-layer"
projectName: "Data Layer & Database"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Customer"]
milestone: "Tenant-safe and observable"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-37", "PAP-43", "PAP-565"]
blocks: []
key: "r4/data-layer/document-previews"
url: "https://linear.app/paperos/issue/PAP-577/document-previews-pdf-and-office-thumbnails-and-page-renders-through-a"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:09.985Z"
model: "claude-sonnet-5"
effort: "low"
estimate: 2
dueDate: null
cycle: null
---

# PAP-577: Document previews: PDF and office thumbnails and page renders through a `files.preview` job, preview variants in `FileDto` and a viewer fallback

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / low — Build S

**Goal**

Deferred to v0.2 (past 2026-10-01): PAP-37 renders image variants only, so invoices, contracts and imported Notion exports show a generic icon in attachments, the support inbox and record pages. Notion, Airtable and Drive all show a first-page thumbnail; this adds it with one more job behind the same `variants` shape.

**Scope**

In: Job `files.preview` rendering page 1 (and up to 5 pages on demand) of PDFs with `pdfium` (via `@hyzyla/pdfium` or `pdf-to-img`) and office documents through a LibreOffice headless container (`ops/compose/office.yml`, staging only, 1 GB budget noted), `FileDto.variants.preview` (`thumb`, `page1`) in WebP, `<FilePreview/>` component with a PDF.js viewer fallback for the browser, docs section.

Out: Editing documents, OCR and text extraction for search (a later `files.extract` job), video thumbnails.

**Spec**

* `files.preview` enqueued after `ready` (and after PAP-574 when present) for `application/pdf` and office MIME types under 50 MB; output keys under `<file>/preview/`; failures leave `variants.preview` empty and the icon fallback.
* Office conversion: LibreOffice `--convert-to pdf` then the PDF path; container absent in dev leaves office files without previews and a log line.
* Time box 60 s per file; concurrency 2; EXIF and metadata stripped from renders; previews served through the same 15-minute signed URLs.
* `<FilePreview file />`: thumbnail, click opens the PDF.js viewer for PDFs or downloads otherwise; keyboard and screen-reader labels from PAP-71 conventions.

**Interface contract**

Provides: Job `files.preview`, `variants.preview` shape, component `FilePreview`, compose service `office`.

Consumes: Files and variants (PAP-37), jobs (PAP-43), scanning status (PAP-574, soft), UI primitives (PAP-71), resource budget (PAP-214). Consumed by PAP-131 attachments, PAP-333 attachments tab, PAP-412 inbox, PAP-180 documents.

**Definition of done**

* A 20-page PDF shows a first-page thumbnail within 10 s of upload; a `.docx` renders on staging through the office container; failures fall back to the icon (recording).
* `<FilePreview/>` at 375, 768, 1280 in both themes; axe clean; docs; CHANGELOG; Linear comment.

**Test plan**

* Unit: MIME eligibility, output key layout, time box handling, viewer fallback selection.
* E2E: CI compose: PDF fixture through upload, complete, preview; assert variant keys and a signed URL that serves WebP.

**Demo**

Reviewer uploads the sample invoice PDF, sees the thumbnail appear in the attachments list and opens the viewer. Under a minute.

**Edge cases**

* Encrypted PDF: no preview, icon with a lock badge.
* Malformed office file crashes LibreOffice: container restarts; job fails once and stops (no retry loop).
* Huge page sizes (A0 drawings): render capped at 2048 px on the long edge.

**Dependencies**

Blocked by PAP-37 and PAP-43 (hard). Soft: PAP-574, PAP-71, PAP-214. Deferred to v0.2; not claimable before 10-01.

**Agent**

Builder: Forge (Platform Engineer). Reviewer: Sentinel (Code Reviewer).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/data-layer/upload-scanning` = PAP-574.
