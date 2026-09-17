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
blocks: ["PAP-121", "PAP-298"]
key: "libraries/mcp-servers"
url: "https://linear.app/paperos/issue/PAP-210/catalog-and-configure-mcp-servers-and-connectors-linear-github-stripe"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T05:19:20.793Z"
---

# PAP-210: Catalog and configure MCP servers and connectors (Linear, GitHub, Stripe, Notion, Drive, Webflow, Miro, Gamma) for agents

**Goal**

Produce the catalog of every MCP server and connector agents can reach (Linear, GitHub, Forgejo, Stripe, Notion, Google Drive, Webflow, Miro, Gamma, Playwright, Postgres) with each tool's scope class, auth, rate limits and permitted characters, and commit working `.mcp.json` so a fresh Claude Code session has integrations on first boot. PAP-103 validates `mcpServers[]` against it and PAP-121 cross-checks connector files with it.

**Scope**

In:

* `.claude/mcp-catalog.yaml`, Zod 4 schema `packages/agents/src/mcp-catalog.ts`, generated `.claude/mcp-catalog.json` replacing the stub from PAP-103.
* Repo `.mcp.json` with env-var placeholders only; per-character overlays stay with PAP-106.
* Thin Forgejo MCP server `packages/agents/mcp/forgejo/` (stdio, `@modelcontextprotocol/sdk` 1.x): `listRepos`, `getFile`, `listPullRequests`, `createPullRequest`, `commentOnPullRequest`.
* `pnpm mcp check`: starts each stdio server or probes each remote, lists tools, diffs against the catalog, reports missing env vars.
* Weekly `.github/workflows/mcp-check.yml`; `docs/libraries/mcp-servers.md` with table and "adding a server" guide.

Out: enforcing allowlists (PAP-106), page-spec connector registry (PAP-121), end-user OAuth, servers beyond the Forgejo wrapper.

**Spec**

* Entry `{ id, name, kind: remote|stdio, package|url, version, auth: { kind, envVars[], headless, notes }, tools: [{ name, scope: read|write|destructive, description, rateLimitHint }], vendorRateLimit, budgetPerSession, sandbox: { available, how }, owner, allowedCharacters[], docsUrl, healthCheck, aliases[], prefer? }`.
* Owners: Linear and GitHub Atlas; Forgejo and Postgres Forge; Stripe Ledger; Notion and Drive Quill; Webflow, Miro, Gamma Beacon; Playwright Sentinel.
* Scope defaults: `read` to all; `write` to owner and Atlas; `destructive` denied and routed to Needs Justin (PAP-94). Missing class fails the schema.
* Rate limits from vendor docs (Linear about 1500 req/h per key, Stripe 100 req/s test, Notion 3 req/s) with `budgetPerSession` passed by PAP-96 to sessions.
* Sandboxes: Stripe test mode, Linear `PAP-SANDBOX` label, Webflow staging site, Notion `Sandbox` tree, Postgres staging.
* Secrets never committed; env names match PAP-17; interactive-only org connectors report `skipped`.

**Interface contract**

Provides: `McpCatalogSchema`, `mcp-catalog.json` (`{ servers[] }`), tool name grammar `mcp__<server>__<tool>`, `.mcp.json`, Forgejo server package `@paperos/mcp-forgejo`, `pnpm mcp check` exit codes (0 ok or skipped, 1 drift, 2 missing required env), doc page. Consumes: PAP-17 env names (soft), PAP-48 bot tokens for headless remotes (soft), PAP-44 `prefer: forgejo` decision. Consumers: PAP-103 validator, PAP-106 overlays, PAP-121 cross-check, PAP-96 budgets, PAP-217 pins the server versions in a Renovate group.

**Definition of done**

* Catalog with all 11 servers validates; generated JSON committed; comment on PAP-103 to switch the validator.
* `.mcp.json` boots in a fresh session; screenshot of `/mcp` listing Linear, GitHub, Stripe and Playwright attached.
* Forgejo wrapper: five tools tested against a mocked API (msw), README, pinned version.
* `pnpm mcp check` passes locally and weekly; a seeded renamed tool fails it in a test.
* Sentinel Security Auditor signs off every scope class in a PR comment.
* Docs page; CHANGELOG; Linear comment with table and screenshot.

**Test plan**

* Vitest: schema (missing scope rejected, known write verbs never `read`), catalog completeness (11 servers), alias expiry logic, Forgejo tools with msw including auth failure.
* Integration: `pnpm mcp check` against real stdio servers in CI with placeholder env; remote OAuth servers marked skipped.
* Manual: fresh Claude Code session `/mcp` screenshot.

**Demo**

Reviewer runs `pnpm mcp check` and reads the table of 11 servers with tool counts and env status, then opens `mcp-catalog.json` to find Stripe `create_payment_link` classed `write`. Under one minute.

**Edge cases**

* Remote OAuth in headless sessions: `headless: false`, token pre-provisioning per bot documented or API-key fallback.
* Vendor renames a tool: `aliases[]` valid 30 days; drift warns then fails.
* GitHub versus Forgejo PR overlap: `prefer: forgejo`.
* Misclassified mutating tool: review checklist plus verb test.
* Org connectors unavailable in CI: `skipped: interactive-only`, never green-washed.

**Dependencies**

None; ready now. Blocks PAP-121. Soft: PAP-48, PAP-17, PAP-44.

**Agent**

Built by Scout (Library Evaluator) with Atlas on Linear and GitHub specifics. Reviewed by Sentinel (Security Auditor) and Forge for the wrapper.

**Size**

M: cataloging is quick; the Forgejo wrapper and checker are real code with tests.
