---
identifier: "PAP-414"
title: "Airtable connector: OAuth and PAT auth, metadata discovery, record streaming with 5 rps token bucket and expiring-attachment fetch"
project: "migration"
projectName: "Migration & Import Tools"
phase: "P2"
type: "Build"
priority: 2
surfaces: ["Staff"]
milestone: "Airtable, Notion, ClickUp importers"
state: "Backlog"
parent: "PAP-202"
children: []
blockedBy: ["PAP-199"]
blocks: ["PAP-415"]
key: "child/PAP-202/0"
url: "https://linear.app/paperos/issue/PAP-414/airtable-connector-oauth-and-pat-auth-metadata-discovery-record"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:05:50.203Z"
model: "claude-opus-5"
effort: "high"
---

# PAP-414: Airtable connector: OAuth and PAT auth, metadata discovery, record streaming with 5 rps token bucket and expiring-attachment fetch

**Goal**

Implement the `SourceConnector` for Airtable so bases, tables, fields, views and records stream into the framework reliably within Airtable's limits, with attachments fetched the moment they are seen because their URLs expire.

**Scope**

In: `connectors/airtable/{auth,discover,stream,attachments}.ts` using the Web API with fetch; OAuth 2 (`data.records:read`, `schema.bases:read`) with PAT fallback; `GET /v0/meta/bases` and `/tables`; `stream` with `pageSize 100`, `offset`, `returnFieldsByFieldId: true`; token bucket 5 rps per base, 30 s backoff on 429; incremental via `filterByFormula: LAST_MODIFIED_TIME() > '<cursor>'`; recorded fixtures from PAP-198.

Out: field and view mapping (children 2 and 3).

**Spec**

* `capabilities: { incremental: true, attachments: true, relations: true, rateLimit: { rps: 5, scope: 'base' } }`.
* Attachment refs carry `recordId` and `fieldId` so a stale URL can be refreshed by re-fetching the record once.
* Auth JSON stored encrypted through the data-layer secret helper; PAT never logged.

**Interface contract**

Provides: `registerConnector('airtable', ...)`, `AirtableSourceSchema` (raw field `type` and `options` preserved in `SourceField.options`), wizard step `AirtableBasePicker` registered via PAP-199 child 3. Consumes: PAP-199 child 1 interface, PAP-37 storage, PAP-198 fixtures and limits. Children 2 and 3 consume `options` verbatim.

**Definition of done**

* Discover and stream the PaperOS demo base (8 tables, 40 attachments) end to end with zero 429 failures in the log.
* Re-sync after edits fetches only changed records.
* Docs section in `docs/migration/airtable.md` on auth setup and scopes.

**Test plan**

* Vitest with msw: pagination, rate limiter timing, 429 backoff, PAT without schema scope error text, expired attachment URL refresh path.
* Integration against the demo base (credentials from the test-accounts issue), recorded run attached.
* Contract test: connector satisfies the framework's `connectorConformance()` suite.

**Demo**

Reviewer runs `pnpm paperos import --connector airtable --base appDEMO --dry` with the demo PAT and sees eight collections discovered, record counts, and attachments staged in storage. Under two minutes.

**Edge cases**

* Base over 50k rows in one table: incremental cursor required; first run warns about duration using the PAP-198 throughput table.
* Free-tier base without attachment API access: attachments skipped with a plan note.
* Symmetric link fields: both field ids recorded so child 2 creates one relation.

**Dependencies**

PAP-199 child 1 (hard), PAP-198 (fixtures), test-accounts issue (integration). Blocks children 2 and 3.

**Agent**

Built by Scout (Import Mapper). Reviewed by Sentinel (Code Reviewer, Security Auditor).

**Size**

M
