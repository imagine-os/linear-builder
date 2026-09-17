---
identifier: "PAP-185"
title: "Add expense capture with receipt OCR and ledger posting"
project: "business-core"
projectName: "Business Core: Payments, Finance & Payroll"
phase: "P2"
type: "Build"
priority: 3
surfaces: ["Staff"]
milestone: "Payroll adapter and cash dashboard"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-175", "PAP-179", "PAP-37"]
blocks: []
key: "business-core/expense-capture"
url: "https://linear.app/paperos/issue/PAP-185/add-expense-capture-with-receipt-ocr-and-ledger-posting"
source: "plan/specs/bucket-6.json (round-1 canonical spec JSON)"
---

# PAP-185: Add expense capture with receipt OCR and ledger posting

**Goal**

Turn receipts into journal entries: capture a receipt photo or PDF from web or mobile, extract vendor, date, totals, tax and line items with a vision model, let staff review and categorise, create an expense (or vendor bill) and post it to the ledger, with duplicate detection and an approval step for amounts above a threshold.

**Scope**

In:
- Tables `fin_expense`, `fin_expense_line`, `fin_expense_extraction`; oRPC `expenses.*`; extraction worker.
- Pages `/finance/expenses` (inbox grid, review panel), mobile capture flow in the Tauri app using the camera plugin, email-in address per tenant (`receipts+<tenant>@...`) via `collab/notifications` inbound if available, else deferred.
- Posting rules `expense.approved`, `expense.reimbursed`, `bill.created` (vendor bill from an invoice-like receipt).
- Category to account mapping with learning from past choices per vendor.

Out: corporate card feeds (bank sync is a future integration), mileage, per-diem policies, multi-currency reimbursements beyond FX capture.

**Spec**

- Capture: web drag-drop or file picker (images and PDF up to 20 MB) uploading via `data-layer/file-storage`; Tauri mobile uses `@tauri-apps/plugin-camera` (or `plugin-dialog` fallback) with client-side downscale to 2000 px; each upload creates `fin_expense (status: extracting)` and enqueues extraction.
- Extraction worker (`packages/finance/src/expenses/extract.ts`): calls the Claude API (model per the `claude-api` skill's current recommendation, temperature 0) with the image and a JSON schema tool `receipt_extraction` returning `{ vendorName, vendorTaxId?, date, currency, subtotalMinor, taxMinor, tipMinor?, totalMinor, paymentMethod?, lastFour?, lines: [{ description, quantity, unitMinor, amountMinor }], confidence: 0-1 per field }`; PDFs rasterised first page with `pdf-to-img`; fallback to `tesseract.js` text plus a text-only extraction when the vision call fails; store raw output in `fin_expense_extraction (expense_id, provider, model, raw jsonb, parsed jsonb, cost_usd, duration_ms)` for evaluation; budget alert if daily extraction spend exceeds a configured cap (`agents/cost-controls`).
- Review panel: image viewer (zoom, rotate) beside a form pre-filled from extraction with low-confidence fields highlighted; vendor matched to `fin_party` by fuzzy name (`pg_trgm` similarity above 0.6) or created; category select mapped to expense accounts; `paidBy: company|employee` (employee reimbursement creates a liability to the employee party); dimensions; notes; approve or reject.
- Duplicate detection: same `sha256` file, or same vendor plus total plus date within 2 days; flagged in the inbox with a link to the suspected original.
- Approval: threshold `fin_settings.expense_approval_threshold_minor` (default 500.00); above it, `expense.approve` permission required from a second user; below it the submitter's manager or finance can approve; agents can extract and propose but not approve.
- Posting on approve: debit expense account (net), debit `sales_tax_receivable` when tax is recoverable (tenant setting), credit `cash` or `credit_card` subtype when paid by company, or `employee_reimbursements_payable` when paid by employee; `expense.reimbursed` moves the payable to cash when a reimbursement is recorded (manual or via payroll adapter if capability exists).
- Learning: `fin_vendor.default_expense_account_id` updated on approval when the same account is chosen twice; suggestions ranked by frequency.
- Datasets: expenses register as a dataset so views, kanban by status and dashboards work.

**Definition of done**

- Extraction eval set of 40 receipts (varied layouts, currencies, crumpled, PDF) with labelled truth in `packages/finance/test/receipts/`; totals correct on at least 90 percent, dates on 95 percent; eval runs weekly through `agents/eval-harness`.
- Vitest for duplicate rules, approval routing, posting rule outputs.
- Playwright: upload, review, approve, ledger entry appears; mobile capture verified on Android emulator via `app-shell/tauri-mobile` smoke test; screenshots at 375, 768, 1024, 1440, 1920 in three themes.
- `docs/finance/expenses.md` including privacy note on sending images to the model; CHANGELOG entry; Linear comment with demo link and eval scores.

**Edge cases**

- Receipt in a currency other than functional: FX rate at receipt date fetched from a rates table (manual entry fallback) and captured on the expense.
- Total does not equal subtotal plus tax (tips, rounding): flag, let reviewer fix, keep raw values.
- Multi-receipt PDF: split pages into separate expenses with a "merge" action.
- Illegible image: extraction returns low confidence everywhere; inbox shows "needs manual entry".
- Vendor name in another script: fuzzy match on normalised transliteration; otherwise create.
- Approver is the submitter: blocked for above-threshold expenses.

**Dependencies**

- `business-core/ledger` (posting), `data-layer/file-storage` (uploads), `business-core/finance-data-model` (parties, accounts), `app-shell/tauri-mobile` (camera), `agents/cost-controls` and `agents/eval-harness`, `collab/notifications`.

**Agent**

Builder: Ledger (Bookkeeper) with Forge (Tauri Smith) for mobile capture. Reviewer: Sentinel (Security Auditor for uploads and model data flow, Edge Case Hunter with adversarial receipts).

**Size**

M: model extraction is quick to wire; review UX and eval discipline take the time.
