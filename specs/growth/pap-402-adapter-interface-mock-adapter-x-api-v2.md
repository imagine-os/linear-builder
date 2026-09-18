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
blockedBy: ["PAP-43", "PAP-401", "PAP-565"]
blocks: ["PAP-403", "PAP-812"]
key: "growth/social/adapter-mock-x"
url: "https://linear.app/paperos/issue/PAP-402/adapter-interface-mock-adapter-x-api-v2-adapter-and-the-pg-boss"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:28:54.658Z"
model: "claude-sonnet-5"
effort: "low"
estimate: 3
dueDate: null
cycle: null
---

# PAP-402: Adapter interface, mock adapter, X API v2 adapter and the pg-boss publishing worker

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / low — Deferred label (excluded from Oct-1 scope)

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

*Round 4 amendment (2026-09-18):*
Round 4: the merge gate is the mock-adapter worker run plus X `validate` unit tests and a recorded (`nock`) publish fixture; the single real X publish is optional evidence, requires the NJ item for the X developer account and the tenant's live flag, and is reported as `skipped: no-credentials` otherwise (Security Model section 4 forbids live publishing outside an approved queue item). Record the attempt in PAP-792.

**Test plan**

* Unit: retry, duplicate protection, 429 handling, X `validate`.
* Integration: end-to-end publish with mock; one recorded real publish.

**Demo**

Approve a post scheduled one minute ahead and watch the worker publish it via the mock, then show the X recording.

**Edge cases**

* Worker crash mid-publish does not duplicate; account rate limit delays queue.

**Dependencies**

Model child (hard), PAP-43, PAP-17, X developer account (Needs Justin).

*Round 4 (2026-09-18): PAP-491 soft: this issue no longer blocks PAP-491 because PAP-402 is deferred to v0.2 and must not block scheduled work; PAP-491 proceeds (wire growth with the CRM core (PAP-189) and the contract stubs for social; the X adapter and publishing worker join when PAP-402 is reinstated) and reconciles when this issue lands.*

**Agent**

Builder: Beacon (Outreach Sequencer). Reviewer: Sentinel (Security Auditor).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/growth/outbound-sandbox-ledger` = PAP-792.
