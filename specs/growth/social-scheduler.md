---
identifier: "PAP-190"
title: "Build a social media scheduler with adapters (X, LinkedIn, Instagram, TikTok, YouTube) and an approval queue"
project: "growth"
projectName: "Growth: Marketing, Outreach & CRM"
phase: "P2"
type: "Build"
priority: 2
surfaces: ["Staff"]
milestone: "Campaigns and social"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-187", "PAP-188", "PAP-37", "PAP-43"]
blocks: []
key: "growth/social-scheduler"
url: "https://linear.app/paperos/issue/PAP-190/build-a-social-media-scheduler-with-adapters-x-linkedin-instagram"
source: "plan/specs/bucket-7.json (round-1 canonical spec JSON)"
---

# PAP-190: Build a social media scheduler with adapters (X, LinkedIn, Instagram, TikTok, YouTube) and an approval queue

**Goal**

Let a tenant plan, approve and publish posts to X, LinkedIn, Instagram, TikTok and YouTube from one calendar, with every post passing through an approval queue before any adapter is allowed to publish. Nothing leaves the system without an approved state; in this build, live publishing is enabled only for accounts Justin connects.

**Scope**

In:
- Drizzle schema `packages/growth/src/social/schema.ts`: `social_account` (`platform`, `external_id`, `handle`, `oauth jsonb` encrypted via `app-shell/env-config` secret helpers, `scopes`, `status`, `expires_at`), `social_post` (`body`, `media_file_ids uuid[]`, `link_url`, `status: draft|pending_approval|approved|scheduled|publishing|published|failed|rejected`, `scheduled_at`, `published_at`, `approved_by`, `rejected_reason`, `source: human|agent`, `campaign_id`), `social_post_target` (post x account, per-platform `variant_body`, `external_post_id`, `metrics jsonb`, `error`), `social_campaign`.
- Adapter interface `packages/growth/src/social/adapters/types.ts`: `validate(post) -> Issue[]` (length, media count, aspect ratio), `publish(target) -> { externalId, url }`, `fetchMetrics(target)`, `refreshAuth(account)`; adapters for X (API v2, `twitter-api-v2` 1.x), LinkedIn (Marketing API, UGC posts), Instagram (Graph API, container then publish), TikTok (Content Posting API), YouTube (Data API v3 resumable upload); each behind a `dryRun` flag that logs instead of calling.
- Scheduler worker on pg-boss 10.x: due `approved` posts move to `publishing`, call adapters, record results, retry three times with backoff, then `failed`.
- UI `apps/web/src/routes/_app/marketing/social/`: calendar view (`tables/calendar-timeline-gantt` view bound to `social_post`), composer with per-platform preview and variant tabs, media picker (`data-layer/file-storage`), approval queue list with approve/reject and diff of edits, account connection settings.
- Approval permission `social.approve` granted to `owner|admin` roles only; agents may create `pending_approval` posts (`growth/content-agent`).

Out: paid ads, DMs, comment moderation, analytics beyond per-post metrics (`growth/attribution` aggregates), Facebook Pages (follow-on).

**Spec**

- Character limits and media rules encoded per adapter and enforced in `validate` and live in the composer (X 280, LinkedIn 3000, Instagram requires media, TikTok video only, YouTube video with title under 100).
- OAuth connect flow via Better Auth generic OAuth or platform SDK; tokens stored encrypted; refresh 24 h before expiry; `status: reauth_required` surfaces a banner.
- State machine transitions are the only writes to `status`; illegal transitions throw `CONFLICT`.
- Every publish writes an `audit_event` and a `crm_activity` when the post links to a campaign contact list.
- Preview renders platform-faithful cards from `packages/ui` components, not iframes.
- Timezone: `scheduled_at` stored UTC, shown in tenant timezone; calendar day boundaries follow tenant.

**Definition of done**

- Vitest: state machine, each adapter's `validate` against fixtures, worker retry and failure paths with mocked adapters, permission checks.
- Integration: X and LinkedIn adapters exercised against sandbox or test accounts in `dryRun: false` once, recording attached; Instagram, TikTok and YouTube verified in `dryRun` with request payload snapshots (app reviews pending, see edge cases).
- Playwright: draft, submit, approve, schedule, worker publishes (mock), calendar shows result; screenshots at 320, 375, 768, 1024, 1280, 1536 and 1920 in light and dark for calendar, composer and queue.
- axe clean; composer keyboard-only usable.
- `docs/growth/social.md` (connecting accounts, adding an adapter, app review checklist); CHANGELOG entry; Linear comment with recording and screenshots.

**Edge cases**

- Token revoked at platform: publish fails once, account flagged `reauth_required`, post returns to `approved` with a banner, not `failed`.
- Post approved then edited: returns to `pending_approval`; approval is of exact content (hash stored).
- Scheduled time in the past on approval: publish immediately after confirmation dialog.
- Media over platform limit (LinkedIn 5 images, X 4): validation blocks scheduling.
- Worker crash mid-publish: `publishing` rows older than 10 min are re-checked via `externalId` lookup before retry to avoid duplicates.
- Platform rate limit (429): backoff honours `Retry-After`; other posts to the same account are delayed.

**Dependencies**

`growth/crm-model` (campaign to contact link) and `growth/growth-research` (adapter borrow-vs-build decision) are hard. `data-layer/file-storage`, `tables/calendar-timeline-gantt` (fallback: list view), `app-shell/env-config` (secret storage). Unblocks `growth/content-agent`.

**Agent**

Built by Beacon (Campaign Composer for UI, Outreach Sequencer for adapters). Reviewed by Sentinel (Security Auditor for OAuth token handling, Code Reviewer, Visual Inspector) and Atlas on the approval rule.

**Size**

L: five adapters with distinct APIs, a state machine, a worker and three screens.
