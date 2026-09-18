---
identifier: "PAP-858"
title: "Build e-signature core: signature requests, signer identity (email OTP, portal login), fields, sequential signing, the signing ceremony UI and the sealed PDF"
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
blockedBy: ["PAP-220", "PAP-352", "PAP-353", "PAP-370", "PAP-581", "PAP-856", "PAP-857"]
blocks: ["PAP-859"]
key: "r4/workflows/esign-core"
url: "https://linear.app/paperos/issue/PAP-858/build-e-signature-core-signature-requests-signer-identity-email-otp"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:51:19.717Z"
model: "claude-opus-5"
effort: "high"
estimate: 5
dueDate: null
cycle: null
---

# PAP-858: Build e-signature core: signature requests, signer identity (email OTP, portal login), fields, sequential signing, the signing ceremony UI and the sealed PDF

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Build L

**Goal**

Let tenants get things signed inside PaperOS: a signature request over a generated document with placed fields (signature, initials, date, text, checkbox), one or more signers in parallel or sequence, signer identity by email one-time code or portal login, a signing ceremony that works on a phone, and a sealed PDF with embedded signature images and a hash, built in-house after the PAP-352 Documenso evaluation records the mode.

**Scope**

In: `signature_request` (`document_id`, `status draft|sent|partially_signed|completed|declined|expired|voided`, `signers[]` with order, `expires`, `reminders`), `signature_field` (type, page, coordinates in PDF points, signer, required), `signature_event` (viewed, otp_sent, otp_verified, signed, declined, with IP hash, user agent, timestamp). Field placement UI on the PDF preview (drag from a palette, PAP-331) or from template `signatureField` placeholders (auto-placed); request composer with message, order, expiry, reminders schedule. Signing ceremony `/sign/:token`: identity step (email OTP through PAP-370 or portal session), review document, fill fields (draw, type in a script font, upload), consent checkbox to sign electronically, submit; phone-first layout; accessibility with keyboard and screen reader (PAP-156). Sealing: on completion, stamp signature images and a completion page into the PDF (`pdf-lib`), compute SHA-256, store as a new `file` version, notify all parties with the sealed copy; `signature.completed` event resumes workflows.

Out: Audit certificate, legal disclosures, verification page (next issue). Qualified signatures, digital certificates (v0.3). In-person signing on a shared device (v0.3).

**Spec**

* Tokens are single-signer, single-use per session, bound to the signer email and expire with the request; every view and action writes a `signature_event`
* OTP: 6 digits, 10 minutes, 5 attempts then lockout for an hour; portal signers skip OTP when their session email matches the signer
* The document cannot change after `sent`: the request pins `generated_document.hash`; voiding creates a new request
* Sequential signing notifies the next signer only after the previous completes; parallel requests seal once all sign
* Declines capture a reason and notify the requester; expired requests can be extended once before expiry only

**Interface contract**

Provides: `SignaturePort.request|sign|status|void`, tables, field placement UI, `/sign/:token` ceremony, sealed PDF version, events `signature.requested|signed|declined|completed`. Consumes: generated documents and templates, session and OTP primitives (PAP-220), email (PAP-370), encryption for signature images at rest (PAP-353), OSS mode decision (PAP-352), drag-and-drop (PAP-331), files (PAP-37). Consumed by: PAP-859, step kind `signature.request`, commerce estimates and contracts, engagement consent and membership agreements, business-core quote acceptance (PAP-395 gains a signed path).

**Definition of done**

* Two-signer sequential request completes on phone and desktop in the demo tenant; sealed PDF opens in three viewers with visible signatures; workflow resumes on completion; screenshots of the ceremony at 375 and 1024
* Every new page has a `page.spec.yaml` (PAP-114) that passes the validator, declared loading, empty, error and denied states, and Gate 3 screenshots at 375, 768, 1024 and 1920 in light and dark themes.
* Linear comment on the issue with the evidence links (PR, gate artefacts, recording or report) and the module docs page updated where the interface changed.

**Test plan**

* Unit: token binding and single use; OTP limits; hash pinning; sequential order.
* Integration: seal idempotency when the completion job runs twice; void after partial signing; reminder schedule.
* E2E: draw, type and upload signatures; decline path; screen reader ceremony (PAP-156).
* Isolation: the PAP-34 cross-tenant harness auto-enrols every new table; one negative case per new oRPC procedure proves `NOT_FOUND` on a foreign tenant row.

**Demo**

Send a service agreement to two signers; sign the first on a phone with an OTP, the second from the portal; open the sealed PDF and watch the workflow create the project.

**Edge cases**

* Signer email bounces (PAP-370 suppression): requester notified immediately with a fix action; the request stays `sent`
* Same person is two signers (owner and witness): each role gets its own token and field set
* Module disabled for the tenant (PAP-266): routes return `MODULE_DISABLED` (409), slot fills unmount and the manifest declares the dependency so consumers fail closed rather than half-render.

**Dependencies**

PAP-857 and PAP-856 (hard), PAP-220, PAP-370, PAP-353 (hard), PAP-352 (hard: mode decision), PAP-331 (soft).

**Agent**

Builder: Nova. Reviewer: Sentinel (Security Auditor).

**Size**

L: two sessions; split at the first natural seam if the first session does not reach the integration test.

*Round 4 critique fix (2026-09-18):* resolved 3 round-4 file keys in this description to Linear identifiers: `r4/workflows/document-generation` = PAP-857, `r4/workflows/document-templates` = PAP-856, `r4/workflows/esign-audit-compliance` = PAP-859.
