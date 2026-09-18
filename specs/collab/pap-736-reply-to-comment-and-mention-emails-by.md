---
identifier: "PAP-736"
title: "Reply to comment and mention emails by email: per-thread reply address, inbound parsing, attribution and loop guards"
project: "collab"
projectName: "In-App Collaboration & Knowledge"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Customer"]
milestone: "Knowledge surfaced everywhere"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-319", "PAP-370", "PAP-725"]
blocks: []
key: "r4/collab/comment-email-replies"
url: "https://linear.app/paperos/issue/PAP-736/reply-to-comment-and-mention-emails-by-email-per-thread-reply-address"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:33.464Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: null
cycle: null
---

# PAP-736: Reply to comment and mention emails by email: per-thread reply address, inbound parsing, attribution and loop guards

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

Deferred to v0.2 (stretch pool; NJ-14 can reinstate). Not claimable before 10-01.

Notion, Linear and GitHub let you answer a mention from your mail client. Customers especially will reply to 'Bo commented on your invoice' rather than sign in. Add a signed per-thread reply address and an inbound parser that posts the reply as a comment with correct attribution.

**Scope**

In: `Reply-To: thread+<signed token>@<tenant inbound domain>` set by the `EmailChannel` for `comment.*` kinds; inbound webhook `/api/webhooks/email-inbound` (Resend or Postal inbound per PAP-295 decision) verifying the provider signature; parser reusing PAP-410's quoted-text stripping and HTML sanitising when merged (a 60-line fallback here); `comments.create` as the sender after matching the `From` address to a tenant user and the token to a thread; attachments through PAP-37. Out: creating threads by email, support inbox (PAP-197), marketing replies (PAP-191).

**Spec**

* Token: HMAC of `(threadId, recipientId, kind)` with a 30-day validity; a reply from an address that does not match the recipient is rejected and the sender gets one bounce explaining why.
* Loop guards: ignore `Auto-Submitted`, `Precedence: bulk`, our own `Message-ID` domain, and any address on the tenant suppression list (PAP-405 when merged).
* Body limit 10k characters after quote stripping; over that, truncated with a link; images inline become attachments.
* Every inbound message stored raw for 7 days in MinIO for debugging, then purged (PAP-355 retention class `transient`).
* Attribution: `author_kind: human`, `source: email` on the comment; the thread shows an envelope icon.

**Interface contract**

Provides: reply address grammar, inbound webhook route, `parseInboundReply()`, comment `source` column. Consumes: `EmailChannel` (PAP-725), `comments.create` (PAP-317), thread deep links (PAP-319), email package inbound adapter (PAP-370), parsing helpers (PAP-410, soft), files (PAP-37), suppression list (PAP-405, soft), retention (PAP-355). Consumed by: PAP-197 (shares the inbound route).

**Definition of done**

* Reply from Mailpit to a mention email appears as a comment with the right author within 60 s in CI; forged token bounces; auto-reply ignored.
* `docs/collab/comments.md` gains Email replies; CHANGELOG entry; Linear comment with a screenshot of the envelope-marked comment.

**Test plan**

* Unit: token sign and verify, quote stripping fixtures (Gmail, Outlook, Apple Mail), loop-guard headers, body limit.
* Integration: webhook signature verification; RLS: reply lands in the right tenant only.
* E2E: none beyond the integration path (no UI).

**Demo**

Trigger a mention email, reply from Mailpit's UI, refresh the thread and see the comment marked as email. Under one minute.

**Edge cases**

* Sender uses an alias address: unmatched, bounce with instructions; no comment created.
* Thread resolved before the reply arrives: reopened with the reply (matches in-app behaviour).
* Provider retries the webhook: idempotent on `Message-ID`.

**Dependencies**

Hard: PAP-319, PAP-725, PAP-370. Soft: PAP-410, PAP-405, PAP-355, PAP-37. Deferred: v0.2.

**Agent**

Builder: Forge (Ops Runner). Reviewer: Sentinel (Security Auditor).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/collab/notification-core` = PAP-725.
