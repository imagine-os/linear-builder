---
identifier: "PAP-859"
title: "Add the e-signature audit certificate, tamper-evident hash chain, public verification page, legal disclosures (ESIGN, eIDAS simple), reminders and retention"
project: "workflows"
projectName: "Workflows, Approvals, Forms, Documents & E-Signature"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Customer"]
milestone: "E-signature, canvas editor and swap"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-136", "PAP-221", "PAP-355", "PAP-393", "PAP-561", "PAP-725", "PAP-858"]
blocks: []
key: "r4/workflows/esign-audit-compliance"
url: "https://linear.app/paperos/issue/PAP-859/add-the-e-signature-audit-certificate-tamper-evident-hash-chain-public"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:51:34.463Z"
model: "claude-opus-5"
effort: "high"
estimate: 3
dueDate: null
cycle: null
---

# PAP-859: Add the e-signature audit certificate, tamper-evident hash chain, public verification page, legal disclosures (ESIGN, eIDAS simple), reminders and retention

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Build M

**Goal**

Make signatures defensible: a completion certificate appended to the sealed PDF listing every event with hashes, a per-tenant hash chain over signature events (PAP-393 pattern) verified nightly, a public verification page where anyone with the document can confirm it is unaltered, the consumer disclosures ESIGN and eIDAS simple electronic signatures expect, reminder and expiry jobs, and retention aligned with PAP-355.

**Scope**

In: Certificate page generator (PAP-235 `PdfLayout`): request id, document hash before and after sealing, per-signer identity method, events with timestamps (UTC and signer timezone), IP hash, user agent, consent text version; appended as the final pages and stored separately as `signature_certificate`. Hash chain: `signature_event.prev_hash` per tenant, `pnpm esign:verify` and nightly job reusing the PAP-393 verifier; `/verify/:hash` public page: upload or paste a hash → status, signer count, completion time (no PII). Disclosures: consent-to-electronic-records text with versioning and tenant-editable jurisdiction addenda (PAP-221 legal pages), shown before signing and recorded per signer; paper-copy request path. Jobs: reminders per the request schedule (PAP-136 kind `signature.reminder`), expiry, retention (certificates immutable 7 years by default per PAP-355 profile; documents follow the record's retention).

Out: Qualified/advanced signatures with certificates (v0.3). Legal advice: the disclosure texts are templates Justin approves (Needs Justin item).

**Spec**

* The certificate is generated from stored events only, never from request-time memory; regenerating it yields byte-identical output for the same events
* Verification page rate-limited (PAP-304) and returns the same shape for unknown and known hashes with a timing guard
* Chain verification failure raises an S0 security event (PAP-356) and locks new requests for the tenant until reviewed
* Disclosure acceptance stores text version, timestamp, signer token and locale; a changed text creates a new version, never edits

**Interface contract**

Provides: certificate generator, `signature_certificate`, hash chain and verifier, `/verify/:hash`, disclosure versions, reminder and expiry jobs. Consumes: e-sign core, hash chain and verifier pattern (PAP-393), retention (PAP-355), legal pages (PAP-221), notifications (PAP-136), print kit (PAP-235), rate limits (PAP-304), security events (PAP-356). Consumed by: commerce and engagement signed documents, platform-ops compliance evidence (signature integrity as a control).

**Definition of done**

* Certificate appended and verifiable for the demo agreements; a tampered PDF fails verification; nightly chain verification green; disclosure texts filed to Needs Justin for approval
* Every new page has a `page.spec.yaml` (PAP-114) that passes the validator, declared loading, empty, error and denied states, and Gate 3 screenshots at 375, 768, 1024 and 1920 in light and dark themes.
* Linear comment on the issue with the evidence links (PR, gate artefacts, recording or report) and the module docs page updated where the interface changed.

**Test plan**

* Unit: certificate determinism; chain hash; disclosure versioning.
* Integration: tamper a stored file byte → verification fails and S0 path fires; reminders honour quiet hours (PAP-324).
* Isolation: the PAP-34 cross-tenant harness auto-enrols every new table; one negative case per new oRPC procedure proves `NOT_FOUND` on a foreign tenant row.

**Demo**

Open a completed agreement, show the certificate pages, paste its hash into `/verify`, then alter one byte in a copy and show the failure.

**Edge cases**

* Signer timezone unknown (no portal account): certificate shows UTC only and says so
* Tenant purge (PAP-355) with signed documents under legal retention: documents move to the archive tier, not deleted, per the retention profile
* Module disabled for the tenant (PAP-266): routes return `MODULE_DISABLED` (409), slot fills unmount and the manifest declares the dependency so consumers fail closed rather than half-render.

**Dependencies**

PAP-858 (hard), PAP-393 (hard: pattern), PAP-355, PAP-221 (soft), PAP-136, PAP-235 (soft).

**Agent**

Builder: Nova. Reviewer: Sentinel (Security Auditor).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/workflows/esign-core` = PAP-858.
