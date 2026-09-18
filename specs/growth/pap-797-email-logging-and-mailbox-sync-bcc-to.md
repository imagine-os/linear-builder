---
identifier: "PAP-797"
title: "Email logging and mailbox sync: BCC-to-CRM address, Gmail and Microsoft Graph OAuth sync of threads with matched contacts, send-from-CRM with the rep's own mailbox"
project: "growth"
projectName: "Growth: Marketing, Outreach & CRM"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Staff"]
milestone: "Acquisition analytics"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-57", "PAP-226", "PAP-353", "PAP-790"]
blocks: []
key: "r4/growth/email-sync-gmail-outlook"
url: "https://linear.app/paperos/issue/PAP-797/email-logging-and-mailbox-sync-bcc-to-crm-address-gmail-and-microsoft"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:51:46.522Z"
model: "claude-opus-5"
effort: "high"
estimate: 3
dueDate: null
cycle: null
---

# PAP-797: Email logging and mailbox sync: BCC-to-CRM address, Gmail and Microsoft Graph OAuth sync of threads with matched contacts, send-from-CRM with the rep's own mailbox

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Build M

**Goal**

Deferred to v0.2 by the Execution Schedule (NJ-14 stop-loss 09-27 can reinstate). Not claimable before 10-01.

Sequences (PAP-191) send from the platform; reps still live in Gmail and Outlook. Logging one-to-one email against contacts, either by BCC or by mailbox sync, is table stakes in HubSpot, Attio and Twenty and the main reason CRMs are abandoned when missing.

**Scope**

In: per-tenant BCC address `log+<token>@<PAPEROS_DOMAIN>` parsed by the PAP-410 inbound pipeline into `crm_activity kind email`; `mailbox_connection (user_id, provider: gmail|microsoft, scopes, history_cursor, status)` with OAuth through PAP-57 generic providers and tokens encrypted via PAP-353; incremental sync (Gmail `history.list`, Graph delta queries) every 5 minutes for threads whose participants match CRM contacts, storing headers, snippet and sanitised body with attachments as references; per-user privacy controls (never sync domains list, per-thread 'do not log'); send-from-CRM composing through the rep's mailbox so replies thread; activity timeline rendering on PAP-189 pages.

Out: shared support mailboxes (PAP-197), calendar sync (booking issue), full mailbox search.

**Spec**

* Only threads with at least one participant that is a CRM contact are stored; internal-only threads are skipped; `never_sync_domains` defaults to the tenant's own domains.
* Bodies are sanitised with the PAP-410 allowlist and classified `pii()`; retention follows PAP-355; users can delete a logged thread which also blocks re-sync of it.
* Sync is idempotent on provider message id; token refresh 24 h before expiry; revoked tokens flag `reauth_required`.
* In CI the providers are `nock`-recorded; live sync requires the Google and Microsoft OAuth apps (NJ).

**Interface contract**

Provides: `mailboxes.connect|disconnect|status`, BCC logging, `crm.emails.send`, activity source `email.synced`, privacy settings page. Consumes: CRM schema, inbound parsing and sanitiser (PAP-410), OAuth (PAP-57), encryption (PAP-353), jobs (PAP-43), retention (PAP-355), outbound ledger for sends.

**Definition of done**

* Recorded-fixture tests for both providers; BCC path integration test; privacy rules tested; screenshots at 375, 1024, 1920 light and dark.
* `docs/growth/email-sync.md` with the OAuth app checklist and privacy notice; CHANGELOG.

**Test plan**

* Unit: participant matching, domain exclusions, delta cursor handling, sanitisation, idempotency.
* E2E: BCC a fixture email, see it on the contact timeline; connect a mocked Gmail, run sync, see two threads; mark one 'do not log' and confirm it disappears and stays gone.

**Demo**

Reviewer connects the mocked mailbox, syncs and opens a contact to read the threaded emails, then sends a reply from the CRM. Under two minutes.

**Edge cases**

* Contact email changes: earlier threads stay linked by contact id.
* Thread with a suppressed contact: logged (inbound) but send blocked by `canContact` transactional rules.
* Rep leaves: connection revoked, logged emails stay.

**Dependencies**

Hard: PAP-790, PAP-57, PAP-353. Soft: PAP-410, PAP-43, PAP-355, OAuth apps (NJ).

**Agent**

Builder: Beacon (CRM Builder). Reviewer: Sentinel (Security Auditor, Edge Case Hunter).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/growth/crm-schema-routers-page-specs` = PAP-790.
