---
identifier: "PAP-97"
title: "Set up Linear webhooks into the orchestrator and PR status back to Linear as comments with screenshots and review verdicts"
project: "pm-linear"
projectName: "Project Management & Claude Pipeline"
phase: "P0"
type: "Build"
priority: 1
surfaces: ["Agent"]
milestone: "Orchestrator claims and ships issues"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-96"]
blocks: ["PAP-101"]
key: "pm-linear/webhooks"
url: "https://linear.app/paperos/issue/PAP-97/set-up-linear-webhooks-into-the-orchestrator-and-pr-status-back-to"
source: "plan/specs/bucket-3.json (round-1 canonical spec JSON)"
---

# PAP-97: Set up Linear webhooks into the orchestrator and PR status back to Linear as comments with screenshots and review verdicts

**Goal**

Make Linear the only window Justin needs: Linear events reach the orchestrator instantly, and every PR event, CI gate result, screenshot set and reviewer verdict is written back to the issue as a structured comment with images. Nobody should have to open GitHub or Forgejo to know how an issue is doing.

**Scope**

In:
- Inbound receiver `POST /webhooks/linear` (Hono on Node 22, inside `imagine-os/paperos-orchestrator`): verifies `Linear-Signature` (HMAC-SHA256 of the raw body with the webhook secret), rejects payloads whose `webhookTimestamp` is older than 60 s, dedupes by `webhookId`, then dispatches on `type` (`Issue`, `Comment`, `IssueLabel`, `Project`) and `action` (`create`, `update`, `remove`) to handlers registered by other modules (`issue-contract`, `justin-queue`, `orchestrator` fast-poll).
- Inbound `POST /webhooks/github` and `POST /webhooks/forgejo`: PR opened/synchronised/closed/merged, `check_suite`/`workflow_run` completed, `pull_request_review` submitted; signature verification per forge (`X-Hub-Signature-256`; Forgejo uses the same header format).
- Outbound to Linear: `attachmentCreate` for the PR (title, subtitle with state, icon), a single "PR status" comment that is edited in place (`commentUpdate`) rather than appended, containing a gate table (Gate 1 static, Gate 2 reviewers, Gate 3 visual, Gate 4 edge cases) with pass/fail/pending, links, and inline screenshots.
- Screenshot upload: files from CI artifacts are uploaded with Linear's `fileUpload` mutation (get signed URL, PUT, then embed the asset URL in the comment markdown) so images render inside Linear.
- Review verdicts from `quality/review-agents` arrive as GitHub reviews; the handler summarises them (verdict, blocking findings count, link) into the status comment and adds label `changes-requested` or removes it.
- Registration script `pnpm webhooks:register` that creates the Linear webhook (`webhookCreate`, resource types Issue, Comment, IssueLabel, Project, all teams) and the repo webhooks via `forge/repo-bootstrap` hooks.

Out: the contents of the gate checks themselves (`quality/*`), notification fan-out (`collab/notifications`), the Linear sync of PM entities (`pm-linear/linear-sync`).

**Spec**

- Event bus: in-process typed emitter `events.on("linear.issue.update", handler)`; every event also persisted to `orchestrator.events` for replay (`pnpm events:replay --since`).
- Status comment template `src/webhooks/templates/pr-status.md`; the comment id is stored in `sessions.status_comment_id`; body ends with the `paperos-session` footer including `status: "in-review"`.
- Screenshot policy: up to 7 images (one per breakpoint from `quality/playwright-matrix`) plus a link to the full set; each image under 2 MB, resized with `sharp` if larger.
- Mapping PR to issue: branch name contains the Linear key (from `forge/branch-policy`); fallback to `Closes PAP-123` in the PR body.
- All outbound Linear calls go through the rate-limited `linearComment()` helper from the orchestrator; comment edits are debounced 5 s so rapid CI events collapse into one update.

**Definition of done**

- Signature verification tests for all three sources including tampered body and stale timestamp.
- Replaying 200 recorded events produces the same status comment (snapshot test).
- Live demo: open a PR on a toy repo, watch the Linear issue gain an attachment and a status comment with screenshots within 60 s of CI finishing; screen recording attached.
- Screenshots display inline in Linear web (1280 px) and the Linear mobile app (375 px); both screenshotted.
- Duplicate delivery test shows one comment, not two.
- Runbook section on rotating webhook secrets; changelog entry; Linear comment with recording.

**Edge cases**

- PR opened before the issue is claimed (a human or a stray session): still link it, set `In Review`, comment that no session record exists.
- One PR closes multiple issues: status comment on each.
- Screenshot upload fails (Linear file size or network): post comment with links only and retry uploads in the background.
- GitHub and Forgejo both fire for the same mirrored commit: dedupe by commit SHA and event kind.
- Comment edit fails because the comment was deleted: create a new one and update the stored id.
- Webhook secret rotation: accept the previous secret for 24 hours.
- Force-push rewrites history: mark previous gate results stale in the table.

**Dependencies**

- `pm-linear/orchestrator` (service, DB, helpers).
- Interfaces with `quality/playwright-matrix` (artifact naming `screenshots/<page>/<width>.png`) and `quality/review-agents` (review body JSON block); coordinate names via a shared `packages/contracts` in the orchestrator repo.

**Agent**

Built by Atlas (Dispatcher sub-agent); reviewed by Sentinel (Security Auditor) for signature handling and Nova for the comment rendering.

**Size**

M: three inbound sources, one carefully edited outbound comment, and file uploads.
