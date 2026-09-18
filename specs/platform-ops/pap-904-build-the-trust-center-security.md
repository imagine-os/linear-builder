---
identifier: "PAP-904"
title: "Build the trust center: security overview, live control status, subprocessor register, policy documents from the docs engine, DPA and BAA template downloads, uptime from the status page, accessibility report link and change subscriptions"
project: "platform-ops"
projectName: "Platform Operations, Analytics & Compliance"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Customer"]
milestone: "Compliance evidence, residency and swap"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-128", "PAP-160", "PAP-221", "PAP-895", "PAP-896", "PAP-903"]
blocks: []
key: "r4/platform-ops/trust-center"
url: "https://linear.app/paperos/issue/PAP-904/build-the-trust-center-security-overview-live-control-status"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:30:07.127Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: null
cycle: null
---

# PAP-904: Build the trust center: security overview, live control status, subprocessor register, policy documents from the docs engine, DPA and BAA template downloads, uptime from the status page, accessibility report link and change subscriptions

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

Publish the answers: a public trust center at `trust.<PAPEROS_DOMAIN>` with a security overview, live control status from the evidence collector (pass counts, never raw evidence), a subprocessor register with change notifications, policy documents rendered from the docs engine (security, privacy, acceptable use, incident response summary), DPA and BAA templates for download (texts approved by Justin), uptime from the status page, the accessibility conformance report link (PAP-160), and a subscribe-to-changes form.

**Scope**

In: Public routes `/trust`, `/trust/controls`, `/trust/subprocessors`, `/trust/policies/:slug`, `/trust/documents` as static pages regenerated on change (same mechanism as the status page); `trust.sections` slot for modules to add sections (for example the assistant's model provider disclosure). `subprocessor` register (name, purpose, location, data categories, DPA link, added date) with a 30-day advance notification to subscribers on additions; policies are MDX in `docs/policies/**` (PAP-134 indexes them; PAP-128 renders); document downloads are versioned files with hashes. Tenant-facing: a `/console/settings/trust` page where a tenant downloads the signed DPA or BAA for their profile and sees which controls apply; per-tenant white-label of the trust center is out of scope.

Out: Questionnaire automation (SIG, CAIQ exports; v0.3). Legal text authoring.

**Spec**

* Control status shows counts and last-evaluated dates only; evidence stays behind `/admin`
* Every published policy page carries its version, effective date and a changelog; unpublished drafts never render
* Subprocessor notifications go through PAP-370 with double opt-in and unsubscribe
* Lighthouse ≥ 95 on performance, accessibility and SEO; no third-party scripts

**Interface contract**

Provides: trust center static pages, `subprocessor` register and notifications, `trust.sections` slot, document downloads, tenant trust settings page. Consumes: controls and evidence, status page uptime, docs engine and rules index (PAP-128, PAP-134), accessibility report (PAP-160), legal pages (PAP-221), email (PAP-370). Consumed by: sales and onboarding (link in the wizard), tenants (their customers ask them), PAP-89 digest.

**Definition of done**

* Trust center live on staging with ≥ 60 controls summarised, 8 subprocessors, 4 policies, DPA and BAA downloads marked draft until Justin approves; a subprocessor addition notifies a test subscriber
* Every new page has a `page.spec.yaml` (PAP-114) that passes the validator, declared loading, empty, error and denied states, and Gate 3 screenshots at 375, 768, 1024 and 1920 in light and dark themes.
* Linear comment on the issue with the evidence links (PR, gate artefacts, recording or report) and the module docs page updated where the interface changed.

**Test plan**

* Unit: static generation; register diff notification.
* E2E: public pages at 375 and 1920; subscribe with double opt-in; policy version display.

**Demo**

Open the trust center, show live control counts updating after last night's run, add a subprocessor in `/admin` and receive the 30-day notice email.

**Edge cases**

* Evidence run failed last night: the trust page shows the previous evaluation date rather than a false green
* Module disabled for the tenant (PAP-266): routes return `MODULE_DISABLED` (409), slot fills unmount and the manifest declares the dependency so consumers fail closed rather than half-render.

**Dependencies**

PAP-896, PAP-903, PAP-895 (hard), PAP-128, PAP-134, PAP-160, PAP-221 (soft), PAP-370 (hard).

**Agent**

Builder: Quill. Reviewer: Sentinel (Security Auditor).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 3 round-4 file keys in this description to Linear identifiers: `r4/platform-ops/compliance-controls` = PAP-896, `r4/platform-ops/evidence-automation` = PAP-903, `r4/platform-ops/status-page` = PAP-895.
