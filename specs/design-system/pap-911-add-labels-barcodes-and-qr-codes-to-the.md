---
identifier: "PAP-911"
title: "Add labels, barcodes and QR codes to the print kit: Barcode and QRCode components, label templates for Avery and thermal sizes, a barcode field type helper and scanner input handling"
project: "design-system"
projectName: "Design System"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Staff"]
milestone: "Themable per tenant with docs"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-150", "PAP-235", "PAP-260", "PAP-338"]
blocks: []
key: "r4/design-system/labels-barcodes-qr"
url: "https://linear.app/paperos/issue/PAP-911/add-labels-barcodes-and-qr-codes-to-the-print-kit-barcode-and-qrcode"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:19:54.973Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: null
cycle: null
---

# PAP-911: Add labels, barcodes and QR codes to the print kit: Barcode and QRCode components, label templates for Avery and thermal sizes, a barcode field type helper and scanner input handling

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

Let the product print and scan the physical world: `<Barcode/>` (Code 128, EAN-13, UPC-A via `bwip-js`) and `<QRCode/>` components in the PAP-235 print kit, label templates for common Avery sheets and 4×6 thermal labels with a print route, a `barcode` field type helper for the tables engine, and a scanner input handler that recognises keyboard-wedge scans and the PAP-260 native scanner through the PAP-150 input abstraction.

**Scope**

In: `packages/ui-print/src/{Barcode,QRCode,LabelSheet}.tsx` with SVG output, `labels.yaml` template registry (Avery 5160, 5163, 4×6 thermal, 2×1 shelf), `/print/labels` route taking a view query and a template. `barcode` field type (PAP-338 framework) validating symbology check digits and rendering the barcode in cells and record panels. `useScannerInput()` hook: detects wedge scans by inter-key timing and suffix, routes to the focused field or a `scan` command; native scanner via PAP-260 plugin.

Out: Printer drivers (browser print and PDF only; ESC/POS is the POS issue). Label design canvas.

**Spec**

* Barcodes render as SVG so they scale in PDF and on screen; QR payloads are signed by the caller, never here
* Label sheets align within 1 mm on the PDF (measured with a printed test sheet)
* Scanner detection never swallows normal typing (timing threshold configurable)

**Interface contract**

Provides: `<Barcode/>`, `<QRCode/>`, `<LabelSheet/>`, label templates and print route, `barcode` field type, `useScannerInput()`. Consumes: print kit (PAP-235), field framework (PAP-338), native scanner (PAP-260), input abstraction (PAP-150). Consumed by: commerce catalog and POS, engagement member cards, workflows document QR verification links, migration (Airtable barcode field mapping PAP-415).

**Definition of done**

* Print a sheet of 30 product labels aligned to Avery 5160 from a saved view; scan one back into a form with a wedge scanner simulation; QR verifies in a phone camera
* Every new page has a `page.spec.yaml` (PAP-114) that passes the validator, declared loading, empty, error and denied states, and Gate 3 screenshots at 375, 768, 1024 and 1920 in light and dark themes.
* Linear comment on the issue with the evidence links (PR, gate artefacts, recording or report) and the module docs page updated where the interface changed.

**Test plan**

* Unit: check digits; label geometry; wedge timing detection.
* E2E: print route PDF snapshot; scan into field.

**Demo**

Open the products view, print shelf labels for the selection, then scan one with a phone into the inventory adjust form.

**Edge cases**

* Right-to-left locale: label text flips, barcode does not (tested)

**Dependencies**

PAP-235, PAP-338 (hard), PAP-260, PAP-150 (soft).

**Agent**

Builder: Iris. Reviewer: Sentinel (Visual Inspector).

**Size**

S: half a session.
