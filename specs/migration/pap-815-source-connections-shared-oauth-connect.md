---
identifier: "PAP-815"
title: "Source connections: shared OAuth connect flow, encrypted token storage, refresh and revocation for every import connector, with a connections settings page"
project: "migration"
projectName: "Migration & Import Tools"
phase: "P2"
type: "Build"
priority: 2
surfaces: ["Staff"]
milestone: "Airtable, Notion, ClickUp importers"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-57", "PAP-226", "PAP-347", "PAP-353"]
blocks: ["PAP-823"]
key: "r4/migration/source-oauth-connections-and-token-refresh"
url: "https://linear.app/paperos/issue/PAP-815/source-connections-shared-oauth-connect-flow-encrypted-token-storage"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:51:46.522Z"
model: "claude-opus-5"
effort: "high"
estimate: 3
dueDate: "2026-09-30"
cycle: null
---

# PAP-815: Source connections: shared OAuth connect flow, encrypted token storage, refresh and revocation for every import connector, with a connections settings page

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Build M

**Goal**

PAP-414 (Airtable), PAP-417 (Notion), PAP-424 (QuickBooks, Xero), PAP-200 (Google) and the Linear and ClickUp children each describe their own OAuth flow and 'encrypted' token storage. One `import_connection` model with a generic connect flow, refresh job and revoke UI is the middle tooling that lets a connector be swapped without touching auth, and the place the Security Auditor reviews once.

**Scope**

In: table `import_connection (tenant_id, source, kind: oauth|pat|api_key, external_account_id, display_name, scopes[], credentials encrypted via PAP-353, expires_at, refresh_status, created_by, last_used_at, status: active|reauth_required|revoked)`; `connections.start(source)` building the provider authorization URL from a `SourceAuthSpec` each connector declares (`authorizeUrl`, `tokenUrl`, `scopes`, `pkce`), callback route `/api/import/oauth/callback` with state binding to tenant and actor, PAT and API-key paths with validation call; refresh job (PAP-43) 24 h before expiry; `connections.revoke` calling the provider's revocation endpoint when it exists; settings page `_app/settings/connections` listing connections with scopes, last use and reauth banners; `SourceConnector.auth` receives a `CredentialHandle` (never raw tokens in connector code; the framework injects headers).

Out: Better Auth login providers (PAP-57 owns identity OAuth), outbound webhooks and tenant API keys (PAP-222), social platform OAuth (PAP-403 keeps its own because tokens belong to posting accounts).

**Spec**

* Tokens never leave the server; connectors call `credentials.fetch(url)` which the framework signs, so a connector cannot log or export a token (lint forbids reading `credentials.raw`).
* State parameter is a signed 10-minute token bound to tenant, actor and source; callback rejects mismatches with `FORBIDDEN` and audits the attempt.
* Scopes requested are the minimum each connector declares; the settings page shows them in plain language from the PAP-198 sheets.
* Provider secrets (client id and secret) come from the PAP-17 env schema via the credential broker (PAP-300); test-account credentials from PAP-813.

**Interface contract**

Provides: `import_connection`, `connections.*`, callback route, `SourceAuthSpec`, `CredentialHandle`, refresh job, settings page, event `import.connection.changed`. Consumes: connector interface (PAP-347), OAuth plumbing patterns (PAP-57), encryption (PAP-353), jobs (PAP-43), env and broker (PAP-17, PAP-300), audit (PAP-38). Consumed by PAP-414, PAP-417, PAP-424, PAP-200 (Google), the Linear and ClickUp children (all soft: they may keep inline auth and migrate).

**Definition of done**

* Mocked-provider Playwright connect, refresh and revoke flows; state tampering rejected in a test; lint rule against raw token reads; `pnpm db:scan-secrets` shows the credentials column as encrypted.
* Screenshots at 375, 1024, 1920 light and dark; `docs/migration/connections.md`; CHANGELOG; comments on the consuming connector issues.

**Test plan**

* Unit: state token signing and expiry, PKCE, refresh scheduling, revocation mapping, scope minimisation.
* E2E: connect a mocked Airtable OAuth provider, run a dry import through the handle, expire the token in the fixture and see the reauth banner, revoke and confirm the connector fails closed.

**Demo**

Reviewer connects a mocked source from Settings, runs a dry run, then revokes it and sees the connector refuse with `reauth_required`. Under two minutes.

**Edge cases**

* Provider without refresh tokens (PATs): `expires_at` null, health check on `last_used_at` weekly.
* Two staff connect the same external account: one connection, second attempt links to it.
* Tenant deleted: connections revoked at the provider during purge (PAP-355 hook).

**Dependencies**

Hard: PAP-347, PAP-57, PAP-353. Soft: PAP-43, PAP-17, PAP-300, PAP-38, PAP-355. Consumers adopt softly.

**Agent**

Builder: Scout (Import Mapper) with Forge on the callback route. Reviewer: Sentinel (Security Auditor).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/migration/importer-test-accounts-and-fixture-workspaces` = PAP-813.
