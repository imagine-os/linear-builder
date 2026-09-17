---
identifier: "PAP-210"
title: "Catalog and configure MCP servers and connectors (Linear, GitHub, Stripe, Notion, Drive, Webflow, Miro, Gamma) for agents"
project: "libraries"
projectName: "Library Discovery & Integration"
phase: "P0"
type: "Infra"
priority: 1
surfaces: ["Agent"]
milestone: "Evaluation process"
state: "Ready for Claude"
parent: null
children: []
blockedBy: []
blocks: ["PAP-121"]
key: "libraries/mcp-servers"
url: "https://linear.app/paperos/issue/PAP-210/catalog-and-configure-mcp-servers-and-connectors-linear-github-stripe"
source: "plan/specs/bucket-8.json (round-1 canonical spec JSON)"
---

# PAP-210: Catalog and configure MCP servers and connectors (Linear, GitHub, Stripe, Notion, Drive, Webflow, Miro, Gamma) for agents

**Goal**

Produce the catalog of every MCP server and connector agents can reach (Linear, GitHub, Forgejo, Stripe, Notion, Google Drive, Webflow, Miro, Gamma, Playwright, Postgres), with each tool's scope class, auth, rate limits and permitted characters, and commit working `.mcp.json` configs so a fresh Claude Code session in paperos-template has integrations on first boot. This is the catalog `agents/character-schema` validates `mcpServers[]` against and `spec-builder/integrations-section` cross-checks its connector files with.

**Scope**

In:
- Source `.claude/mcp-catalog.yaml`, Zod 4 schema `packages/agents/src/mcp-catalog.ts`, generated `.claude/mcp-catalog.json` (replaces the `mcp-catalog.stub.json` from `agents/character-schema`).
- Repo-level `.mcp.json` with env-var placeholders only; per-character overlay generation is left to `agents/tool-scopes` but the catalog carries the data it needs.
- Thin Forgejo MCP server `packages/agents/mcp/forgejo/` (stdio, TypeScript, `@modelcontextprotocol/sdk` 1.x) because no official one exists: tools `listRepos`, `getFile`, `listPullRequests`, `createPullRequest`, `commentOnPullRequest`.
- Smoke checker `pnpm mcp check`: starts each stdio server or probes each remote, lists tools, diffs against the catalog, reports missing env vars.
- Weekly workflow `.github/workflows/mcp-check.yml` and doc `docs/libraries/mcp-servers.md` with the catalog table and "adding a server" guide.

Out: enforcing allowlists (`agents/tool-scopes`), page-spec connector registry (`spec-builder/integrations-section`), OAuth flows for end users, new servers beyond the Forgejo wrapper.

**Spec**

- Catalog entry: `{ id, name, kind: remote|stdio, package|url, version, auth: { kind: oauth|apiKey|none, envVars[], headless: true|false, notes }, tools: [{ name (mcp__<server>__<tool>), scope: read|write|destructive, description, rateLimitHint }], vendorRateLimit, sandbox: { available, how }, owner (character), allowedCharacters[], docsUrl, healthCheck, aliases[] }`.
- Servers to catalog: Linear (official remote `https://mcp.linear.app/mcp`, OAuth; owner Atlas), GitHub (official remote or `@modelcontextprotocol/server-github`; owner Atlas), Forgejo (wrapper above; owner Forge), Stripe (`@stripe/mcp`, test-mode keys; owner Ledger), Notion (official remote; owner Quill), Google Drive (org connector, read scopes recorded; owner Quill), Webflow (org connector; note `webflow_guide_tool` once per session; owner Beacon), Miro and Gamma (org connectors; Gamma is generate-only, cannot edit; owner Beacon), Playwright (`@playwright/mcp`; owner Sentinel), Postgres (`@modelcontextprotocol/server-postgres` read-only against staging; owner Forge).
- Scope classes drive defaults: `read` allowed to all characters; `write` allowed to owner and Atlas; `destructive` (delete issue, refund, drop table, delete page) denied everywhere and routed to Needs Justin per `pm-linear/justin-queue`. Every tool must have a class; the schema rejects missing ones.
- Rate limits from vendor docs (Linear ~1500 req/h per key, Stripe 100 req/s test, Notion 3 req/s) stored as `vendorRateLimit` with a `budgetPerSession` hint the orchestrator (`pm-linear/orchestrator`) passes to sessions.
- Secrets never committed: env names only, matching `app-shell/env-config`; `pnpm mcp check` prints missing names and exits 0 with `skipped` for interactive-only org connectors.
- Sandbox column: Stripe test mode, Linear `PAP-SANDBOX` label on a sandbox project, Webflow staging site, Notion `Sandbox` page tree, Postgres staging DB.

**Definition of done**

- Catalog with all 11 servers validated in Vitest; generated JSON committed and `agents/character-schema` validator switched to it (comment on that issue).
- `.mcp.json` boots in a fresh session; screenshot of `/mcp` tool listing for Linear, GitHub, Stripe, Playwright attached to the PR.
- Forgejo wrapper: five tools with tests against a mocked API (msw), README, pinned version.
- `pnpm mcp check` passes locally and in the weekly workflow; a seeded drift (renamed tool) fails it in a test.
- Sentinel Security Auditor signs off on every scope class in a PR comment.
- Docs page rendered, CHANGELOG entry, Linear comment with the table and screenshot.

**Edge cases**

- Remote OAuth servers in headless orchestrator sessions: mark `headless: false`, document token pre-provisioning per bot account (`forge/bot-accounts`) or fall back to API-key servers.
- Vendor renames a tool: `aliases[]` keeps old names valid for 30 days; drift check warns then fails.
- Overlapping capability (GitHub vs Forgejo PRs): `prefer: forgejo` field per the `forge/vcs-decision-adr` decision.
- Unpinned server packages drift: exact pins; grouped by `libraries/upgrade-bot`.
- Tool misclassified as `read` but mutates (Stripe `create_payment_link`): checklist in the review; test asserts known write verbs are not `read`.
- Org connectors unavailable in CI: reported `skipped: interactive-only`, never green-washed.

**Dependencies**

None; ready now. Consumed by `agents/character-schema`, `agents/tool-scopes`, `spec-builder/integrations-section`, `pm-linear/orchestrator`. Soft: `forge/bot-accounts`, `app-shell/env-config`.

**Agent**

Built by Scout (Library Evaluator) with Atlas supplying Linear and GitHub specifics. Reviewed by Sentinel (Security Auditor) for scopes and Forge for the Forgejo wrapper.

**Size**

M: cataloging is quick, but the Forgejo wrapper and the smoke checker are real code with tests.
