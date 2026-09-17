---
identifier: "PAP-190"
title: "Build a social media scheduler with adapters (X, LinkedIn, Instagram, TikTok, YouTube) and an approval queue"
project: "growth"
projectName: "Growth: Marketing, Outreach & CRM"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Staff"]
milestone: "Campaigns and social"
state: "Backlog"
parent: null
children: ["PAP-401", "PAP-402", "PAP-403"]
blockedBy: ["PAP-37", "PAP-43", "PAP-187", "PAP-188", "PAP-353"]
blocks: []
key: "growth/social-scheduler"
url: "https://linear.app/paperos/issue/PAP-190/build-a-social-media-scheduler-with-adapters-x-linkedin-instagram"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:06:11.592Z"
model: null
effort: null
---

# PAP-190: Build a social media scheduler with adapters (X, LinkedIn, Instagram, TikTok, YouTube) and an approval queue

**Goal**

Deferred to v0.2 by the Execution Schedule (NJ-14 stop-loss 09-27 can reinstate). Not claimable before 10-01.

Let a tenant plan, approve and publish posts to X, LinkedIn, Instagram, TikTok and YouTube from one calendar, with every post passing an approval queue before any adapter publishes. Nothing leaves without an approved state; live publishing only for accounts Justin connects. Umbrella for three children.

**Scope**

Children (same milestone, Backlog):

* PAP-401 (M) Schema, approval state machine, composer with per-platform variants, queue and calendar (list fallback).
* PAP-402 (M) Adapter interface, mock adapter, X API v2 adapter, pg-boss publishing worker with retries and duplicate protection.
* PAP-403 (M) LinkedIn, Instagram, TikTok and YouTube adapters in `dryRun` with payload snapshots, OAuth connect flows, re-auth banners, app-review checklist.

Out: paid ads, DMs, comment moderation, analytics beyond per-post metrics, Facebook Pages.

**Spec**

Decisions binding all children:

* `social_account (platform, external_id, handle, oauth jsonb encrypted via PAP-353 (security pending document; absorbed the data-layer gap) or PAP-17 helpers, scopes, status, expires_at)`; `social_post (body, media_file_ids, link_url, status: draft|pending_approval|approved|scheduled|publishing|published|failed|rejected, scheduled_at, published_at, approved_by, approved_hash, rejected_reason, source: human|agent, campaign_id)`; `social_post_target (post x account, variant_body, external_post_id, metrics jsonb, error)`; `social_campaign`.
* Adapter interface `validate(post) -> Issue[]`, `publish(target) -> { externalId, url }`, `fetchMetrics(target)`, `refreshAuth(account)`, all behind `dryRun`.
* State transitions are the only writes to `status`; approval binds to a content hash; edits return to `pending_approval`.
* `social.approve` for owner and admin only; agents create `pending_approval` only.
* Limits per adapter (X 280, LinkedIn 3000, Instagram media required, TikTok video only, YouTube title under 100) enforced in `validate` and live in the composer.
* `scheduled_at` stored UTC, displayed in the tenant timezone.

**Interface contract**

Provides: `social.posts.create|update|submit|approve|reject|schedule|list`, `social.accounts.connect|list|disconnect`, `SocialAdapter` interface and `adapters[platform]`, `validatePost(post, platforms)` reused by PAP-192 for length limits, events `social.post.published|failed`, calendar view binding for PAP-168. Consumes: schema (PAP-187), decision (PAP-188), files (PAP-37), jobs (pg-boss via PAP-43 conventions), secrets (PAP-17), calendar (PAP-168, list fallback), audit (PAP-38). Consumed by PAP-192, PAP-195 campaign audiences.

**Definition of done**

* All three children Done.
* X and LinkedIn exercised once against test accounts with `dryRun: false`, recording attached; the other three verified in `dryRun` with payload snapshots.
* Screenshots at 320, 375, 768, 1024, 1280, 1536, 1920 in light and dark for calendar, composer and queue; axe clean; composer keyboard-only.
* `docs/growth/social.md` (connecting accounts, adding an adapter, app-review checklist); CHANGELOG; Linear comment with recording.

**Test plan**

Umbrella `social.e2e.spec.ts`: draft a post with two platform variants, submit, approve as admin, schedule for one minute ahead, run the worker with the mock adapter, assert `published` with an external id and a calendar entry; edit an approved post and assert it returns to `pending_approval`; revoke the mock token and assert `reauth_required` with the post back in `approved`; kill the worker mid-publish and assert the `externalId` lookup prevents a duplicate; hit a mocked 429 and assert `Retry-After` is honoured.

**Demo**

Reviewer writes a post in the composer, watches the X counter turn red past 280, trims it, submits, approves it from the queue as admin, schedules it and sees it appear on the calendar and publish through the mock adapter. Under two minutes.

**Edge cases**

* Token revoked: one failure, account flagged, post stays `approved`.
* Scheduled time already past on approval: publish after a confirmation.
* Media over platform limits blocks scheduling.
* Worker crash: `publishing` rows older than 10 minutes re-checked before retry.
* Rate limit: other posts to the same account delayed.

**Dependencies**

PAP-187 (hard), PAP-188 (hard), PAP-37 (hard), PAP-43, PAP-17, PAP-168 (soft), platform OAuth apps (Needs Justin, one item covering all five). Consumed by PAP-192 (soft; the relation `PAP-190 blocks PAP-192` was removed on 2026-09-17, FIX-4, because this issue is Deferred to v0.2 while PAP-192 is scheduled for 09-28): the content agent only drafts, into `social.posts.create` when this issue exists and otherwise into its own `campaign_draft` approval queue, so it does not wait for this issue. Publishing anything PAP-192 drafts waits for this issue; when it ships, the composer imports approved `campaign_draft` rows and PAP-192 switches its length check to `validatePost`.

**Agent**

Builder: Beacon (Campaign Composer for UI, Outreach Sequencer for adapters). Reviewer: Sentinel (Security Auditor for token handling, Code Reviewer, Visual Inspector), Atlas on the approval rule.

**Size**

L, split into three M children; the third waits on app reviews and ships in `dryRun`.

**Pending issues**

Bracketed references above are fully specified work packages that Linear refused to create on 2026-09-17 (`USAGE_LIMIT_EXCEEDED`, free-plan issue cap). Their specs live in the project document(s) data-layer, [growth](<https://linear.app/paperos/document/round-2-pending-issues-growth-13-3fd4406e8012>) and they are created as issues by `round2/agent4/create_issues.py` once the workspace plan is upgraded.
