---
identifier: "PAP-185"
title: "Add expense capture with receipt OCR and ledger posting"
project: "business-core"
projectName: "Business Core: Payments, Finance & Payroll"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Staff"]
milestone: "Payroll adapter and cash dashboard"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-37", "PAP-175", "PAP-179", "PAP-394"]
blocks: []
key: "business-core/expense-capture"
url: "https://linear.app/paperos/issue/PAP-185/add-expense-capture-with-receipt-ocr-and-ledger-posting"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:41:49.458Z"
model: "claude-sonnet-5"
effort: "low"
---

# PAP-185: Add expense capture with receipt OCR and ledger posting

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / low — Deferred label (excluded from Oct-1 scope)

**Goal**

Deferred to v0.2 by the Execution Schedule (NJ-14 stop-loss 09-27 can reinstate). Not claimable before 10-01.

Turn receipts into journal entries: capture a photo or PDF from web or mobile, extract vendor, date, totals, tax and lines with a vision model, let staff review and categorise, create an expense or vendor bill, and post it to the ledger with duplicate detection and threshold approval.

**Scope**

In: tables `fin_expense`, `fin_expense_line`, `fin_expense_extraction`; procedures `expenses.*`; extraction worker; `/finance/expenses` inbox and review panel; Tauri mobile capture; posting rules `expense.approved`, `expense.reimbursed`, `bill.created`; vendor-to-account learning; email-in address when PAP-136 inbound exists.

Out: card feeds and bank sync, mileage and per diem, multi-currency reimbursement beyond FX capture.

**Spec**

* Capture: images and PDF to 20 MB via PAP-37; mobile through `@tauri-apps/plugin-camera` (PAP-260) with client downscale to 2000 px; each upload creates `fin_expense (status: extracting)` and enqueues a PAP-43 job.
* Extraction: Claude API per the `claude-api` skill recommendation, temperature 0, tool `receipt_extraction` returning vendor, tax id, date, currency, subtotal, tax, tip, total, payment method, last four, lines and per-field confidence; PDFs rasterised first page; fallback `tesseract.js` text extraction; raw and parsed output plus `cost_usd` stored in `fin_expense_extraction`; daily spend cap via PAP-111.
* Review panel: zoomable image beside a pre-filled form with low-confidence fields highlighted; vendor fuzzy-matched to `fin_party` (`pg_trgm` above 0.6) or created; category maps to expense accounts; `paidBy: company|employee`; dimensions; approve or reject.
* Duplicates: same file `sha256`, or same vendor, total and date within two days.
* Approval above `fin_settings.expense_approval_threshold_minor` (default 500.00) requires a second user with `expense.approve`; agents extract and propose only.
* Posting: debit expense account, debit `sales_tax_receivable` when recoverable, credit `cash` or `credit_card` or `employee_reimbursements_payable`; `expense.reimbursed` moves the payable to cash.
* Learning: `fin_vendor.default_expense_account_id` set after the same account is chosen twice.

**Interface contract**

Provides: `expenses.upload|list|get|review|approve|reject|recordReimbursement`, `ReceiptExtraction` Zod schema, dataset `finance.expenses`, `bill` documents created through PAP-180 for invoice-like receipts, event `expense.approved`. Consumes: posting (PAP-179), files (PAP-37), parties and accounts (PAP-175), camera shim (PAP-259, PAP-260), cost controls and eval harness (PAP-111, PAP-110), jobs (PAP-43), notifications (PAP-136 core). Consumed by PAP-183 AP aging (bills), PAP-186 payables block.

**Definition of done**

* Extraction eval set of 40 labelled receipts in `packages/finance/test/receipts/`: totals correct on 90 percent, dates on 95 percent; weekly run through PAP-110.
* Vitest, Playwright and the Android emulator smoke below green.
* `docs/finance/expenses.md` with the privacy note on model data flow; CHANGELOG; Linear comment with demo link and eval scores.

**Test plan**

* Unit: duplicate rules, approval routing including submitter-equals-approver, posting outputs for company-paid, employee-paid and recoverable tax, learning threshold.
* Integration: upload to extraction job to review row with recorded model fixtures; fallback path when the vision call fails; spend cap trips.
* E2E: upload, review with one corrected field, approve, journal entry appears; mobile capture on the Android emulator (PAP-258 pipeline).
* Visual: inbox and review panel at 375, 768, 1024, 1440, 1920 in three themes.

**Demo**

Reviewer drags a sample receipt into `/finance/expenses`, watches it move from extracting to review, corrects the highlighted tax field, approves it and opens the resulting journal entry from the activity tab. Under two minutes.

**Edge cases**

* Foreign-currency receipt: FX at receipt date from the rates table or manual entry.
* Total not equal to subtotal plus tax: flagged, reviewer fixes, raw kept.
* Multi-receipt PDF split into expenses with a merge action.
* Illegible image: "needs manual entry".
* Vendor name in another script: transliterated fuzzy match, else create.

**Dependencies**

PAP-179 (hard), PAP-37 (hard), PAP-175 (hard), PAP-180 (bills), PAP-260 (mobile capture), PAP-111, PAP-110, PAP-43, PAP-136 core (soft).

**Agent**

Builder: Ledger (Bookkeeper) with Forge (Tauri Smith) on mobile capture. Reviewer: Sentinel (Security Auditor for uploads and model data flow, Edge Case Hunter with adversarial receipts).

**Size**

M: extraction is quick to wire; review UX and eval discipline take the time.
