---
identifier: "PAP-121"
title: "Specify the integrations section (Stripe, Linear, Notion, Drive, Webflow, Miro, Gamma) backed by a connector registry"
project: "spec-builder"
projectName: "Spec Builder"
phase: "P1"
type: "Spec"
priority: 2
surfaces: ["Developer"]
milestone: "Codegen and conformance tests"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-114", "PAP-210"]
blocks: ["PAP-174", "PAP-389"]
key: "spec-builder/integrations-section"
url: "https://linear.app/paperos/issue/PAP-121/specify-the-integrations-section-stripe-linear-notion-drive-webflow"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:41:27.911Z"
model: "claude-sonnet-5"
effort: "high"
---

# PAP-121: Specify the integrations section (Stripe, Linear, Notion, Drive, Webflow, Miro, Gamma) backed by a connector registry

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Spec P1

**Goal**

Finalise the `integrations` section so a page declares which external systems and capabilities it touches, backed by a connector registry that knows each connector's auth, env vars, MCP server, modes and limits. Validation catches pages using connectors the app has not enabled, env-config knows which secrets to require, and the canvas can draw external systems.

**Scope**

* In: Zod `IntegrationsSection`, connector registry built from `packages/spec/integrations/*.connector.yaml`, eleven connector files, validator rules, mode narrowing, generated `integrations.json`, `docs/spec/integrations.md`.
* Out: connector implementations (`packages/integrations/<id>` owned by consuming projects), MCP server catalogue content (PAP-210), automation triggers (PAP-174 consumes).

**Spec**

* Page shape: `integrations[] { connector, capabilities[], mode: live | test | mock, onFailure: degrade | block | queue }`.
* Connector file: `{ id, name, docsUrl, mcpServer, auth: { kind: apiKey | oauth | webhook, envVars[] }, capabilities[] { id, description, scope, rateLimit, maps: sdkCall | mcpTool }, modes[], webhooks[], mock?, owner, deprecated? }`; seeded for `stripe`, `linear`, `notion`, `google-drive`, `webflow`, `miro`, `gamma`, `resend`, `twilio`, `github`, `forgejo`.
* Capability ids `<area>.<verbNoun>`; `mode: mock` requires a mock module; app-level mode is the default and a page may only narrow (`live` app allows `test` page, not the reverse); registry build fails on duplicate capability ids or colliding env var names.
* `onFailure` drives PAP-120 wiring: `degrade` renders `IntegrationUnavailable` (PAP-234), `block` shows the error state, `queue` defers via PAP-148 with a pending badge.
* Rules: `INT_UNKNOWN_CONNECTOR`, `INT_UNKNOWN_CAPABILITY`, `INT_NOT_ENABLED`, `INT_MODE_WIDENING`, `INT_MOCK_MISSING`, `INT_DEPRECATED` (warn, error after date), `INT_DUP_CONNECTOR` (warn).

**Interface contract**

* Provides: `IntegrationsSectionSchema`, `ConnectorSchema`, `registry: Record<ConnectorId, Connector>`, `requiredEnvVars(app, pages): string[]`, generated `integrations.json`, `pnpm spec gen:integrations`.
* Consumers: PAP-17 env-config boot check (`requiredEnvVars`), PAP-120 wiring, PAP-123 external nodes and inbound webhook edges, PAP-106 (MCP server ids per character cross-check), PAP-174 triggers, PAP-177 Stripe billing pages, PAP-193 landing forms, PAP-15 forces `mock` in Pages builds.
* Requires: PAP-114 schema, PAP-210 catalogue (start from the plan's list if not merged), PAP-117 app-level `integrations`.

**Definition of done**

* Vitest: schema fixtures, registry build, each rule, narrowing logic, generated JSON snapshot.
* Eleven connector files cross-checked against the PAP-210 catalogue (reviewer confirms).
* CI test: enabling `stripe` in `live` mode without `STRIPE_SECRET_KEY` fails boot with the variable named.
* `customer-invoices` runs in `mock` mode in Playwright with a mocked Stripe checkout; screenshots at 375 and 1280 px.
* Docs; changelog; Linear comment with catalogue link.

**Test plan**

* Unit: rules with fixtures, narrowing matrix (app x page modes), env var collision detection, deprecation date logic with fake clock.
* Integration: registry build from the eleven files; `requiredEnvVars` against the template app.
* e2e: example page in mock mode at 375 and 1280 px.
* Visual: `IntegrationUnavailable` degrade state screenshot at 375 and 1280 px.

**Demo**

Set the app-level `stripe` mode to `test` and a page to `live`, run `pnpm spec:validate` and read `INT_MODE_WIDENING`; then run the example in mock mode and click "Pay" to see the mocked checkout. One minute.

**Edge cases**

* Connector deprecated: warning until the date, then error with `replaceWith`.
* Capability missing from a connector: error hinting a PAP-210 issue.
* Connector listed twice on a page: merged with warning.
* Preview deploy: forced `mock` recorded in generated JSON.
* Webhook-only connector on a page: allowed; canvas draws an inbound edge.

**Dependencies**

Blocked by PAP-114, PAP-210. Soft: PAP-117, PAP-17, PAP-106. Blocks PAP-174.

**Agent**

Built by Quill (Page Spec Writer) with Scout (Library Evaluator) on connector facts; reviewed by Sentinel (Security Auditor) for env handling.

**Size**

M
