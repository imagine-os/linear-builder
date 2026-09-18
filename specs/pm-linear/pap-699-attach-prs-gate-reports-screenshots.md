---
identifier: "PAP-699"
title: "Attach PRs, gate reports, screenshots, recordings and the digest to Linear issues as native attachments, and give sessions `pnpm evidence attach` to satisfy Definition-of-done evidence"
project: "pm-linear"
projectName: "Project Management & Claude Pipeline"
phase: "P0"
type: "Build"
priority: 2
surfaces: ["Agent"]
milestone: "Orchestrator claims and ships issues"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-97"]
blocks: ["PAP-89", "PAP-254"]
key: "r4/pm-linear/issue-attachments-and-evidence-bundle"
url: "https://linear.app/paperos/issue/PAP-699/attach-prs-gate-reports-screenshots-recordings-and-the-digest-to"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:28.653Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-22"
cycle: null
---

# PAP-699: Attach PRs, gate reports, screenshots, recordings and the digest to Linear issues as native attachments, and give sessions `pnpm evidence attach` to satisfy Definition-of-done evidence

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

No issue in the workspace has an attachment; PAP-97 creates one for the PR and everything else lands as links in comments that scroll away. Most Definitions of done say "recording attached" or "screenshot attached" without a tool that does it. Native attachments give the issue sidebar a stable evidence list and give PAP-254 certification and the umbrella integration test something to check.

**Scope**

* In: `attach(issueId, { url, title, subtitle, iconUrl, metadata })` in the orchestrator's Linear client with dedupe by URL, attachment kinds and titles per artefact (`PR #n`, `Gate 1 report`, `Visual contact sheets`, `Replays`, `Vision findings`, `Edge cases`, `Security`, `Release digest`, `Recording: <name>`), automatic attachment from PAP-97 gate events, the `linear-update attach` script extension (PAP-105) and `pnpm evidence attach --kind recording --file demo.mp4` uploading to MinIO (PAP-37) with a 180-day lifecycle, `EVIDENCE_REQUIRED` warning in PAP-93 when a DoD mentions attachments and none exist at In Review, docs section.
* Out: rendering attachments inside PaperOS (PAP-102, PM sync of `pm_attachment` is the deferred sync extension), Linear's paid integrations, images inline in comments (PAP-97 keeps those).

**Spec**

* Kinds table `ops/pm/attachment-kinds.yaml`: `kind -> { title, iconUrl, source: gate artefact or manual }`; every `GateReport` posted through PAP-97 attaches its Pages or run URL once per PR (updated in place on re-runs via `attachmentUpdate`); the digest attaches to the RC issue; recordings and screenshots attach on demand.
* `pnpm evidence attach --kind <kind> --file <path> | --url <url> [--title]` uploads files to MinIO `evidence/<issue>/<sha>/` through the broker, then calls `attach`; refuses files over 200 MB; returns the attachment id in the JSON last line (skill contract).
* Dedupe by `(issue, url)`; metadata carries `{ kind, sha, pr, gate, expiresAt }` so PAP-89 and PAP-254 can list evidence per RC without parsing comments.
* PAP-93 gains `EVIDENCE_REQUIRED` (warn at In Review): DoD text matches `attached|recording|screenshot` and the issue has no attachment of a matching kind; the bounce comment lists the missing kinds; PAP-254 `certify.ts` requires the gate attachments on the RC issue.
* Umbrella closing (PAP-281 `UMBRELLA_CLOSE`) attaches the integration-test evidence to the parent using the same command.

**Interface contract**

* Provides: `attach()`, `attachment-kinds.yaml`, `pnpm evidence attach`, `linear-update attach` extension, validator code `EVIDENCE_REQUIRED`, `evidenceFor(issue): Attachment[]` for PAP-89 and PAP-254.
* Consumes: PAP-97 events and Linear client, PAP-239 artefact URLs, PAP-37 MinIO signed uploads, PAP-300 broker, PAP-105 skill scripts, PAP-93 validator, PAP-254 certification.

**Definition of done**

* A sandbox PR produces attachments for every gate on its issue, updated in place on re-run (screenshot of the sidebar).
* `pnpm evidence attach --kind recording --file demo.mp4` from a session attaches and the playbook (PAP-92) gains the step; `EVIDENCE_REQUIRED` fixture passes.
* PAP-254 certification reads `evidenceFor()` on a rehearsal RC; docs; changelog; Linear comment with the sidebar screenshot.

**Test plan**

* Unit: kinds table validation, dedupe, metadata shape, DoD regex on 30 fixtures.
* E2E: sandbox PR gate events; live attach from a rehearsal session through the broker.

**Demo**

Open the seeded PR's issue: the sidebar lists PR, Gate 1 report, Visual contact sheets and a Recording; click the recording to play the MinIO URL. Under one minute.

**Edge cases**

* Pages URL expires (30 days): metadata `expiresAt` shown; PAP-89 re-signs MinIO links, Pages links stay as history.
* Same artefact for several issues (one PR closes two): attached to each.
* Attachment limit per issue (Linear caps are generous but finite): gate attachments update in place so the count stays under twenty.
* MinIO unavailable: the file is kept in the run artefacts and a link attachment posted with `pending-upload` metadata; retried nightly.

**Dependencies**

Hard: PAP-97, PAP-239. Soft: PAP-37, PAP-300, PAP-105, PAP-93, PAP-254, PAP-89.

* Soft dependency (round 4): PAP-239 is a soft dependency, not a `blocks` relation, because its milestone (2026-09-25) is later than this issue's (2026-09-22); build against its interface and reconcile when it lands.
  **Agent**

Builder: Atlas (Dispatcher). Reviewer: Sentinel (Code Reviewer).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* PAP-239 appears in the Hard list above and in a round-4 soft note; it is soft (no `blocks` relation). Read the Hard list without it.
