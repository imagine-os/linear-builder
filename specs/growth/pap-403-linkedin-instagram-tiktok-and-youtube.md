---
identifier: "PAP-403"
title: "LinkedIn, Instagram, TikTok and YouTube adapters in dryRun with payload snapshots, OAuth connect flows and re-auth banners"
project: "growth"
projectName: "Growth: Marketing, Outreach & CRM"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Staff"]
milestone: "Campaigns and social"
state: "Backlog"
parent: "PAP-190"
children: []
blockedBy: ["PAP-402"]
blocks: []
key: "growth/social/adapters-review-gated"
url: "https://linear.app/paperos/issue/PAP-403/linkedin-instagram-tiktok-and-youtube-adapters-in-dryrun-with-payload"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:42:51.364Z"
model: "claude-sonnet-5"
effort: "low"
---

# PAP-403: LinkedIn, Instagram, TikTok and YouTube adapters in dryRun with payload snapshots, OAuth connect flows and re-auth banners

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / low — Deferred label (excluded from Oct-1 scope)

**Goal**

Implement the remaining adapters and account connection so they are ready the day each platform's app review clears, verified by payload snapshots meanwhile.

**Scope**

In: `adapters/{linkedin,instagram,tiktok,youtube}.ts`, OAuth connect via Better Auth generic OAuth or SDK, encrypted token storage, refresh 24 hours before expiry, `reauth_required` banner, app-review checklist doc.

**Spec**

* LinkedIn UGC posts; Instagram container then publish; TikTok Content Posting API; YouTube Data API v3 resumable upload with title under 100.
* Each adapter's `validate` encodes limits; `publish` in `dryRun` writes the exact request payload to a snapshot; live mode enabled per account by Justin.
* Tokens encrypted via PAP-353 or PAP-17 helpers.

**Interface contract**

Provides: four adapters, `social.accounts.connect|disconnect|refresh`, settings page, `docs/growth/social.md` checklist. Consumes: adapter child, PAP-57 OAuth plumbing, PAP-17, platform apps (Needs Justin).

**Definition of done**

* Payload snapshots for all four; connect flow Playwright with a mocked provider; banner state; checklist filed as one Needs Justin item.

**Test plan**

* Unit: `validate` per platform; payload snapshots.
* E2E: connect, expiry banner, disconnect.

**Demo**

Connect a mocked LinkedIn account, schedule a post in `dryRun`, open the payload snapshot.

**Edge cases**

* Expired refresh token surfaces banner without failing posts; disconnect keeps history.

**Dependencies**

Adapter child (hard), PAP-57 children, PAP-17; app reviews (external, weeks).

**Agent**

Builder: Beacon (Outreach Sequencer). Reviewer: Sentinel (Security Auditor).

**Size**

M: ships in dryRun.
