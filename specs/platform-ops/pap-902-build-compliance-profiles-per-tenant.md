---
identifier: "PAP-902"
title: "Build compliance profiles per tenant: standard, gdpr, hipaa and student-privacy profiles from the business profile enforcing MFA, session timeouts, PHI access logging, encryption of phi columns, export restrictions and BAA acknowledgement"
project: "platform-ops"
projectName: "Platform Operations, Analytics & Compliance"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Staff"]
milestone: "Compliance evidence, residency and swap"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-38", "PAP-59", "PAP-126", "PAP-220", "PAP-229", "PAP-353", "PAP-355", "PAP-561", "PAP-581", "PAP-896"]
blocks: []
key: "r4/platform-ops/compliance-profiles"
url: "https://linear.app/paperos/issue/PAP-902/build-compliance-profiles-per-tenant-standard-gdpr-hipaa-and-student"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:51:43.804Z"
model: "claude-opus-5"
effort: "high"
estimate: 3
dueDate: null
cycle: null
---

# PAP-902: Build compliance profiles per tenant: standard, gdpr, hipaa and student-privacy profiles from the business profile enforcing MFA, session timeouts, PHI access logging, encryption of phi columns, export restrictions and BAA acknowledgement

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Build M

**Goal**

Make a clinic tenant safer than a bakery tenant by declaration: compliance profiles selected from the PAP-126 business profile (`standard`, `gdpr`, `hipaa`, `student-privacy`) that enforce settings the tenant cannot weaken: MFA required for staff, shorter session and idle timeouts, access logging of every read on `phi`-annotated data, encryption at rest for `phi` and `sensitive` columns through PAP-353, restricted exports and sharing, minimum retention, and a BAA or DPA acknowledgement step before the profile activates.

**Scope**

In: `CompliancePort.profileFor(tenant)` and `enforce()`: profiles in `profiles.yaml` (settings, controls required from `controls.yaml`, column classes affected); tenant setting from `app.spec.yaml business.compliance` (PAP-126) and the onboarding wizard (PAP-367) with a confirmation and the acknowledgement document (e-sign when present, else a recorded checkbox with version). Enforcement points: Better Auth hooks (PAP-220: MFA required, session max 8 h and idle 15 min for `hipaa`), permission engine attribute (PAP-59: `profile.hipaa` blocks public views and embeds PAP-172 for `phi` datasets), `phi` and `sensitive` column classes in the PAP-355 annotation set mapped to `encrypted()` (PAP-353) by a migration generator, read-access logging via a PAP-38 extension (`audit_read` for `phi` tables, 6-year retention), export (PAP-205, PAP-421) requires a platform-verified destination, assistant grounding excludes `phi` unless the profile allows with logging. Console `/console/settings/compliance`: current profile, enforced settings (read-only), acknowledgement history, control status from `controls.yaml`, request profile change (Needs Justin approval for downgrades).

Out: Legal texts (Needs Justin). Physical safeguards. Certification.

**Spec**

* A profile can only be strengthened by the tenant; weakening requires platform approval and is audited with the acknowledgement revoked
* Enforcement is server-side in every case; the UI mirrors it; conformance cases prove each setting cannot be bypassed via API
* `phi` read logging captures actor, purpose (from route spec `purpose`), rows touched (ids only) and is queryable for the "accounting of disclosures"
* Profiles are versioned; a new version applies after notification with a 30-day window unless it only strengthens
* The student-privacy profile hides guardian and student PII from other guardians via generated attribute policies and forbids third-party analytics scripts (none exist, asserted)

**Interface contract**

Provides: `CompliancePort.profileFor|enforce`, `profiles.yaml`, enforcement hooks, `phi` column class and read logging, compliance settings page, acknowledgement records. Consumes: controls framework, business profile (PAP-126), auth hooks and sessions (PAP-220), field encryption (PAP-353), audit (PAP-38), PII classes and retention (PAP-355), permission engine (PAP-59), sharing (PAP-172), exports (PAP-205, PAP-421), onboarding (PAP-367), e-sign (soft). Consumed by: packs (clinic, school defaults), assistant (grounding exclusions), engagement and commerce (profile-aware behaviour), trust center (profile list), PAP-221 DSAR (profile-driven SLAs).

**Definition of done**

* Clinic demo tenant on `hipaa`: staff without MFA is forced to enrol, idle session expires at 15 minutes, a `phi` read appears in `audit_read`, the `patients` dataset cannot be shared publicly, export requires verification; API bypass attempts fail in conformance tests
* Every new page has a `page.spec.yaml` (PAP-114) that passes the validator, declared loading, empty, error and denied states, and Gate 3 screenshots at 375, 768, 1024 and 1920 in light and dark themes.
* Linear comment on the issue with the evidence links (PR, gate artefacts, recording or report) and the module docs page updated where the interface changed.

**Test plan**

* Unit: profile resolution and versioning; strengthen-only rule; policy generation.
* Integration: each enforcement point via API without UI; read logging volume and retention; encryption migration generator on a fixture schema.
* E2E: onboarding selects clinic → profile prompt → acknowledgement → settings page reflects it.
* Isolation: the PAP-34 cross-tenant harness auto-enrols every new table; one negative case per new oRPC procedure proves `NOT_FOUND` on a foreign tenant row.

**Demo**

Switch the demo clinic to `hipaa`, sign the acknowledgement, log in as staff without MFA and get enrolled, open a patient record and show the read log entry, then try to publish a public view of patients and get the block.

**Edge cases**

* Tenant applies the clinic pack on `standard`: the pack recommends `hipaa` and the wizard explains the consequences; nothing is forced
* Profile strengthened while a public view exists: the view is disabled with a notification listing what changed
* Module disabled for the tenant (PAP-266): routes return `MODULE_DISABLED` (409), slot fills unmount and the manifest declares the dependency so consumers fail closed rather than half-render.

**Dependencies**

PAP-896 (hard), PAP-126, PAP-220, PAP-353, PAP-38, PAP-355, PAP-59 (hard), PAP-172, PAP-205, PAP-421, PAP-367 (soft).

**Agent**

Builder: Sentinel. Reviewer: Forge.

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/platform-ops/compliance-controls` = PAP-896.
