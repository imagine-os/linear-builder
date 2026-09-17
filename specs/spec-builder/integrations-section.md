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
blocks: ["PAP-174"]
key: "spec-builder/integrations-section"
url: "https://linear.app/paperos/issue/PAP-121/specify-the-integrations-section-stripe-linear-notion-drive-webflow"
source: "plan/specs/bucket-4.json (round-1 canonical spec JSON)"
---

# PAP-121: Specify the integrations section (Stripe, Linear, Notion, Drive, Webflow, Miro, Gamma) backed by a connector registry

**Goal**

Finalise the `integrations` section so a page declares which external systems and capabilities it touches, backed by a connector registry that knows each connector's auth, env vars, MCP server, modes and limits. Validation catches pages using connectors the app has not enabled, env-config knows which secrets to require, and the canvas can draw external systems.

**Scope**

In:
- Zod 4 `IntegrationsSection` in `packages/spec/src/schema/integrations.ts`:
  ```yaml
  integrations:
    - connector: stripe
      capabilities: [billing.readSubscription, checkout.createSession]
      mode: test        # live | test | mock
      onFailure: degrade   # degrade | block | queue
  ```
- Connector registry `packages/spec/src/integrations/registry.ts` (typed, generated from `packages/spec/integrations/*.connector.yaml`): `{ id, name, docsUrl, mcpServer, auth: { kind: apiKey|oauth|webhook, envVars[] }, capabilities: { id, description, scope, rateLimit }, modes: [live, test, mock], webhooks[], owner character }` seeded for `stripe`, `linear`, `notion`, `google-drive`, `webflow`, `miro`, `gamma`, `resend`, `twilio`, `github`, `forgejo`, sourced from `libraries/mcp-servers`.
- Validator rules: `INT_UNKNOWN_CONNECTOR`, `INT_UNKNOWN_CAPABILITY`, `INT_NOT_ENABLED` (not in `app.spec.yaml integrations`), `INT_MODE_UNSUPPORTED`, `INT_SCOPE_EXCEEDS_CHARACTER` (warn when `meta.owner` lacks the MCP scope per `agents/tool-scopes`).
- Generator `pnpm spec gen:integrations` writing `apps/web/src/generated/integrations.json` `{ connectors: [{ id, mode, capabilities, envVars }] }` consumed by `app-shell/env-config` (required secrets at boot) and `spec-builder/spec-to-canvas` (external nodes).
- Docs `docs/spec/integrations.md` plus a generated connector catalogue table.

Out: connector implementations and SDK wrappers (owned by business-core, growth, pm-linear), OAuth flows, webhook handlers.

**Spec**

- Capability ids are `<area>.<verbNoun>` in camelCase; each maps to a concrete SDK call or MCP tool named in the connector file so reviewers can trace it.
- `mode: mock` requires the connector to declare a mock module path (`packages/integrations/<id>/mock.ts`); Playwright and conformance tests run pages in mock mode by default.
- `onFailure` drives generated state wiring: `degrade` renders the page with the integration block replaced by `ui.integrationUnavailable`; `block` shows the error state; `queue` defers via the offline queue (`realtime/offline-queue`) and shows a pending badge.
- App-level `integrations[].mode` is the default; a page may only narrow (`live` app allows `test` page, not the reverse).
- Registry build validates every connector YAML against `ConnectorSchema` and fails on duplicate capability ids.

**Definition of done**

- Vitest: schema fixtures, registry build from YAML, each validator rule, mode narrowing logic, generated JSON snapshot.
- Eleven connector files committed with capabilities cross-checked against `libraries/mcp-servers` catalogue (reviewer confirms in comment).
- `env-config` boot check fails with a named missing variable when a page enables `stripe` in `live` mode without `STRIPE_SECRET_KEY` (test in CI).
- Example `customer-invoices` page runs in `mock` mode in Playwright with a mocked Stripe checkout; screenshot at 375 and 1280.
- `docs/spec/integrations.md`; CHANGELOG entry; Linear comment with catalogue link.

**Edge cases**

- Connector deprecated (for example a social platform API sunset): `deprecated: { since, replaceWith }` in the connector file produces a warning; error after the date.
- Page needs a capability the connector lacks (Notion write when only read is catalogued): validator error with a hint to open a `libraries/mcp-servers` issue.
- Same connector listed twice on one page: merged with a warning.
- Live mode in a preview deploy: `app-shell/gh-pages-demo` forces `mock` at build time via env, recorded in the generated JSON.
- Connector env var names collide across connectors: registry build fails.
- Webhook-only connectors (Stripe events) declared on a page: allowed, canvas draws an inbound edge.

**Dependencies**

`spec-builder/schema` (hard), `libraries/mcp-servers` (catalogue content; start from the plan's list if not merged). Soft: `agents/tool-scopes`, `app-shell/env-config`, `spec-builder/app-level-spec`. Consumed by `spec-builder/spec-to-canvas`, `business-core/stripe-billing`, `growth/landing-forms`.

**Agent**

Built by Quill (Page Spec Writer) with Scout (Library Evaluator) filling connector files. Reviewed by Sentinel (Security Auditor for scopes) and Atlas.

**Size**

M: small schema, but eleven accurate connector definitions and env wiring.
