---
identifier: "PAP-402"
title: "Adapter interface, mock adapter, X API v2 adapter and the pg-boss publishing worker"
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
blockedBy: ["PAP-43", "PAP-401"]
blocks: ["PAP-403"]
key: "growth/social/adapter-mock-x"
url: "https://linear.app/paperos/issue/PAP-402/adapter-interface-mock-adapter-x-api-v2-adapter-and-the-pg-boss"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:05:47.457Z"
---

# PAP-402: Adapter interface, mock adapter, X API v2 adapter and the pg-boss publishing worker

**Goal**

Publish for real on one platform through a worker that is safe against duplicates and rate limits, with a mock adapter the rest of the system tests against.

**Scope**

In: `adapters/types.ts`, `adapters/mock.ts`, `adapters/x.ts` (`twitter-api-v2` 1.x), worker on pg-boss, metrics fetch. Out: the other four adapters (sibling).

**Spec**

* Interface `validate`, `publish`, `fetchMetrics`, `refreshAuth`, `dryRun` flag.
* Worker: due `approved` posts to `publishing`, adapter call, `published` with external id and url, three retries with backoff, `failed`; `publishing` rows older than 10 minutes re-checked via `externalId` lookup before retry; 429 honours `Retry-After` and delays the account's other posts.
* Token revocation flags `reauth_required` and returns the post to `approved`.

**Interface contract**

Provides: `SocialAdapter`, `adapters.mock`, `adapters.x`, `validatePost`, worker job `social.publish`, events `social.post.published|failed`. Consumes: model child, PAP-43 conventions, secrets (PAP-17).

**Definition of done**

* Worker tests with the mock; one real X publish in `dryRun: false` recorded; metrics fetched.

**Test plan**

* Unit: retry, duplicate protection, 429 handling, X `validate`.
* Integration: end-to-end publish with mock; one recorded real publish.

**Demo**

Approve a post scheduled one minute ahead and watch the worker publish it via the mock, then show the X recording.

**Edge cases**

* Worker crash mid-publish does not duplicate; account rate limit delays queue.

**Dependencies**

Model child (hard), PAP-43, PAP-17, X developer account (Needs Justin).

**Agent**

Builder: Beacon (Outreach Sequencer). Reviewer: Sentinel (Security Auditor).

**Size**

M: one session.
