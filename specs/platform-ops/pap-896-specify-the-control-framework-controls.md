---
identifier: "PAP-896"
title: "Specify the control framework: controls.yaml mapping SOC 2 trust criteria, GDPR articles and HIPAA safeguards to the issues, artefacts and evidence the platform already produces, with the gap list"
project: "platform-ops"
projectName: "Platform Operations, Analytics & Compliance"
phase: "P2"
type: "Spec"
priority: 2
surfaces: ["Developer"]
milestone: "Ops contract, super-admin console and status page"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-38", "PAP-160", "PAP-219", "PAP-354", "PAP-355", "PAP-356", "PAP-359", "PAP-561", "PAP-563", "PAP-674"]
blocks: ["PAP-902", "PAP-903", "PAP-904"]
key: "r4/platform-ops/compliance-controls"
url: "https://linear.app/paperos/issue/PAP-896/specify-the-control-framework-controlsyaml-mapping-soc-2-trust"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:51:16.200Z"
model: "claude-opus-5"
effort: "high"
estimate: 3
dueDate: "2026-10-01"
cycle: null
---

# PAP-896: Specify the control framework: controls.yaml mapping SOC 2 trust criteria, GDPR articles and HIPAA safeguards to the issues, artefacts and evidence the platform already produces, with the gap list

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Spec M

**Goal**

Answer the security questionnaire before it arrives: one `controls.yaml` that names each control PaperOS claims (access control, change management, encryption, logging and monitoring, backup and recovery, vendor management, incident response, data subject rights, PHI safeguards), maps it to SOC 2 trust services criteria, GDPR articles and HIPAA safeguards, points at the issue that implements it and the artefact that evidences it (gate files, audit tables, backup reports, DAST results), and lists the gaps honestly as issues on the owning projects.

**Scope**

In: `docs/compliance/controls.yaml` with a Zod schema (`packages/platform-ops/src/compliance/schema.ts`): `Control` (`id`, `title`, `statement`, `frameworks: { soc2: ['CC6.1'], gdpr: ['Art. 32'], hipaa: ['164.312(a)(1)'] }`, `owner agent`, `implementedBy: PAP ids`, `evidence: [{ kind: artefact|table|report|policy, source, frequency }]`, `status implemented|partial|gap|not-applicable`, `testProcedure`). Coverage: at minimum the SOC 2 common criteria CC1 to CC9 and A1, GDPR Articles 5, 15 to 22, 25, 28, 30, 32 to 35, HIPAA administrative, physical and technical safeguards relevant to a SaaS with no physical PHI; each mapped to existing work (PAP-34 RLS, PAP-38 audit, PAP-219 baseline, PAP-220 MFA, PAP-221 DSAR, PAP-300 broker, PAP-353 encryption, PAP-354 DR, PAP-355 retention, PAP-356 telemetry, PAP-357 DAST, PAP-358 supply chain, PAP-359 PCI, PAP-80 SAST, PAP-88 release train, PAP-160 a11y) or marked `gap`. `docs/compliance/gap-list.md` with one proposed issue per gap (vendor and subprocessor register, access review procedure, incident response runbook, security awareness for agent characters, BAA process, risk assessment cadence) filed as `crossProjectSuggestions` or issues in this project. `pnpm compliance:lint` validating the file, checking every `implementedBy` id exists in the Linear snapshot and every `evidence.source` path pattern resolves in the repo or artefact catalogue (PAP-239).

Out: Running an audit. Writing policies (templates in the trust center issue). Evidence collection automation (own issue).

**Spec**

* Control statements are written in plain language a customer's security reviewer can read, and each has a test procedure an agent can execute (query, artefact check, screenshot)
* Framework mappings cite the exact criterion identifiers; a control may map to several; `not-applicable` requires a rationale
* The file is the single source for the trust center, the evidence collector and the compliance profiles; nothing else hard-codes a control
* Every `gap` has an owner project and a target version; the lint fails on a gap without one

**Interface contract**

Provides: `controls.yaml`, its schema, `compliance:lint`, the gap list and proposed issues, `compliance_controls` dataset registration. Consumes: threat model and baseline (PAP-219), PCI posture (PAP-359), retention and PII (PAP-355), DR (PAP-354), security telemetry (PAP-356), audit (PAP-38), privacy tooling (PAP-221), accessibility report (PAP-160), gate artefacts (PAP-239), Linear snapshot (PAP-306 tooling). Consumed by: PAP-902, PAP-903, PAP-904, PAP-89 (compliance section), sales conversations.

**Definition of done**

* `controls.yaml` merged with ≥ 60 controls, lint green, every SOC 2 common criterion touched, gap list filed; Atlas approves the mapping and Justin sees a one-page summary in Needs Justin (informational, not blocking)
* Linear comment on the issue with the evidence links (PR, gate artefacts, recording or report) and the module docs page updated where the interface changed.

**Test plan**

* Static: schema validation; id existence against the snapshot; source pattern resolution.
* Review: Sentinel (Security Auditor) and Atlas walk every `implemented` control against the cited issue's Definition of done; any overclaim becomes `partial`.

**Demo**

Open the controls file filtered to HIPAA technical safeguards; show `164.312(b)` audit controls mapped to PAP-38 with its evidence query, then the gap entry for the BAA process with its owner.

**Edge cases**

* An implementing issue is deferred to v0.2: the control becomes `partial` automatically when the lint reads the `Deferred` label from the snapshot

**Dependencies**

PAP-219, PAP-359, PAP-355, PAP-354, PAP-356, PAP-38 (hard: the things being mapped), PAP-221, PAP-160 (soft), PAP-239, PAP-306 (soft).

* Soft dependency (round 4): PAP-221 is a soft dependency, not a `blocks` relation, because it is deferred to v0.2; build against its interface and reconcile when it lands.
  **Agent**

Builder: Sentinel. Reviewer: Atlas (Merger).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 3 round-4 file keys in this description to Linear identifiers: `r4/platform-ops/compliance-profiles` = PAP-902, `r4/platform-ops/evidence-automation` = PAP-903, `r4/platform-ops/trust-center` = PAP-904.
