# PaperOS Module System

Status: v1, 2026-09-17. Owner: Module System & Swap Tooling (Atlas owns the contract, Forge builds, Sentinel reviews). Companion to the [Blueprint](blueprint.md) and the [Interface & Data Contracts](interface-and-data-contracts.md). This document answers one question from Justin: if we rewrite the shell (or anything else) later, how does everything else reconnect without a rewrite of its own? The answer is that every one of the seventeen projects is a module, every module talks to the others only through a versioned contract package, and a thin kernel of middle tooling (registry, DI container, event bus, gateway, UI slots, conformance runner, swap CLI) is the only place a dependency is allowed to live. Changing anything here needs an ADR (PAP-130).

## 1. The module model

A module is the unit we swap. Each of the seventeen Linear projects is one module, plus `module-system` itself (the kernel) and the contract-zero primitives that already live in `@paperos/core`. A module has exactly three artefacts:

| Artefact | Where | What it holds |
| -- | -- | -- |
| Manifest | `packages/<module>/module.ts` (`defineModule()`, PAP-264) and the generated `module.manifest.json` beside it | Identity, version, `provides`, `requires`, capabilities, slots, events, owner, swap risk. Pure data, validated at boot and in CI. |
| Contract package | `packages/contracts/<module>` published as `@paperos/contract-<module>` | Types, Zod schemas, event topic definitions, oRPC route signatures, UI slot definitions, repository port interfaces, conformance suite, golden fixtures. No runtime, no React, no database. |
| Implementation package(s) | `packages/<module>` (or `apps/*`, `ops/*`, `.claude/*` for non-runtime modules) | Adapters that implement the module's own contract and consume other modules' contracts. Never imported by anyone else. |

Modules come in four kinds so the same rules apply to a Postgres package and to a CI pipeline: `runtime` (code that ships in the app: app-shell, data-layer, identity, design-system, tables, realtime, collab, input, business-core, growth, migration), `service` (a deployed process with an API: forge, realtime's Hocuspocus, the orchestrator side of pm-linear), `tooling` (quality gates, spec-builder codegen, agents' `.claude` definitions) and `process` (libraries: rubric, registry, Scout routine). A `process` module still publishes a contract, because the registry schema, the ADR frontmatter and the license policy are things other modules read.

### 1.1 Module table

| Module (project key) | Kind | Owner agent | Provides (contract package) | Requires | Swap risk |
| -- | -- | -- | -- | -- | -- |
| app-shell | runtime host | Forge | `contract-app-shell`: shell slots, route contribution, layout, window manager, config and secrets, flags, i18n, native capability ports | identity, design-system, spec-builder | critical |
| data-layer | runtime core | Forge | `contract-data-layer`: tenant context, repository and unit-of-work ports, event bus, jobs, files, search, audit, sync, email, idempotency, API conventions; pins `@paperos/core/types|filter|events` | identity | critical |
| forge | service | Forge | `contract-forge`: `ForgePort` (repos, trees, commits, PRs, mirror status), webhook envelopes, bootstrap spec, CI runner artefact contract | identity, quality | medium |
| identity | runtime core | Forge (Sentinel reviews) | `contract-identity`: `Principal`, auth, permission (`can`, `explain`, SQL predicate), tenant and membership, audiences, impersonation ports | data-layer | critical |
| design-system | runtime | Iris | `contract-design-system`: component id registry with props schemas, DTCG token set, theme port, icon port, motion tokens, state component ids | none hard | high |
| quality | tooling | Sentinel | `contract-quality`: gate artefact schemas (gate1, security, visual, review, edge, conformance), finding and severity taxonomy, gate runner port, RC manifest | forge, pm-linear | medium |
| pm-linear | service + runtime | Atlas | `contract-pm-linear`: issue contract and states, PM entities, `PmSourcePort` (list, claim, transition, comment), queue port, webhook envelope | data-layer, tables, collab | high |
| agents | tooling | Atlas | `contract-agents`: character schema, handoff artefact, session status, agent runtime port, budget port, prompt-log sink, skill manifest, MCP allowlist | identity, pm-linear, collab | medium |
| spec-builder | tooling + runtime | Quill | `contract-spec-builder`: `PageSpec`, `AppSpec`, validator port, generator plugin interface, flow graph, component refs | design-system, identity, data-layer, app-shell | high |
| collab | runtime | Nova (Quill consults) | `contract-collab`: comment anchors and port, docs port, prompt-log port, changelog port, notification kinds and port, ADR record | data-layer, identity, realtime, design-system | medium |
| realtime | runtime + service | Nova | `contract-realtime`: collab doc rooms, presence, live records, reconciler and conflict events, push transport, window bus | data-layer, identity | high |
| input | runtime | Nova | `contract-input`: input event abstraction, command registry, keymap presets, focus, drag-and-drop sensors, voice routing | app-shell, design-system | low |
| tables | runtime | Nova | `contract-tables`: `ViewSpec`, `FieldDef`, dataset registration, view query port, view renderer registry, field type plugin, formula and automation trigger ports | data-layer, identity, design-system, input | high |
| business-core | runtime | Ledger | `contract-business-core`: finance model, ledger port, posting rules, billing, payments, tax and payroll provider ports, document port, entitlements | data-layer, identity, tables | high |
| growth | runtime | Beacon | `contract-growth`: CRM entities, social adapter, outreach provider, landing page publisher, attribution events, segment and support channel ports | tables, data-layer, business-core, collab, agents | medium |
| migration | runtime | Scout | `contract-migration`: `SourceConnector`, mapping model, import run states, external id map, export archive v1, template pack schema | tables, data-layer, collab, business-core, pm-linear | low |
| libraries | process | Scout | `contract-libraries`: library record, rubric scores, ADR frontmatter, license policy, MCP connector record, Renovate groups | collab, quality | low |
| module-system | kernel | Atlas / Forge | `@paperos/kernel`: registry, DI, flag swap, gateway, slots runtime, conformance runner, swap CLI, migration adapter kit | contract-zero only | critical |

Swap risk is declared, not computed: `critical` means a swap needs the full playbook with shadow-run; `high` needs conformance plus canary; `medium` conformance only; `low` a version bump and a green CI.

### 1.2 Manifest schema

The manifest extends the PAP-264 `ModuleManifest` (id, title, version, routes, navItems, entities, permissions, jobs, settingsSchema, integrations, dependsOn, optional) with the fields the swap tooling needs. It is a Zod schema in `packages/core/src/modules/manifest.ts`; the JSON Schema is generated (`pnpm gen:schemas`) into `packages/core/src/modules/manifest.schema.json` and is never hand-edited. Excerpt of the generated schema:

```json
{
  "$id": "https://paperos.dev/schema/module-manifest/1",
  "type": "object",
  "required": ["id", "kind", "version", "owner", "provides", "requires", "swapRisk"],
  "properties": {
    "id": { "type": "string", "pattern": "^[a-z][a-z0-9-]+$" },
    "kind": { "enum": ["runtime", "service", "tooling", "process", "kernel"] },
    "version": { "type": "string", "description": "semver of the implementation" },
    "owner": { "type": "object", "required": ["agent", "project"],
      "properties": { "agent": { "enum": ["Atlas","Forge","Iris","Quill","Sentinel","Nova","Ledger","Beacon","Scout"] },
                      "project": { "type": "string" } } },
    "provides": { "type": "array", "items": { "type": "object", "required": ["contract", "version"],
      "properties": { "contract": { "type": "string", "pattern": "^@paperos/contract-[a-z-]+$" },
                      "version": { "type": "string" }, "impl": { "type": "string", "default": "default" } } } },
    "requires": { "type": "array", "items": { "type": "object", "required": ["contract", "range"],
      "properties": { "contract": { "type": "string" }, "range": { "type": "string" },
                      "optional": { "type": "boolean", "default": false },
                      "ports": { "type": "array", "items": { "type": "string" } } } } },
    "capabilities": { "type": "array", "items": { "type": "string" } },
    "slots": { "properties": { "exposes": { "type": "array" },
      "fills": { "type": "array", "items": { "required": ["slot", "component"],
        "properties": { "slot": {}, "component": {}, "order": { "type": "integer" }, "when": { "type": "string" } } } } } },
    "events": { "properties": { "publishes": { "type": "array" }, "subscribes": { "type": "array" } } },
    "swapRisk": { "enum": ["low", "medium", "high", "critical"] },
    "optional": { "type": "boolean", "default": true },
    "dependsOn": { "type": "array", "deprecated": true }
  },
  "additionalProperties": false
}
```

`dependsOn` stays for PAP-264 compatibility and is derived from `requires`; a manifest that lists both and disagrees fails. `requires[].ports` names the ports a module uses (for example `["ViewQueryPort", "registerDataset"]`) so the compatibility matrix can say which change breaks whom.

## 2. Contract packages

One package per module, `@paperos/contract-<module>`, at `packages/contracts/<module>`. The existing `packages/contracts` (PAP-239 gate artefacts) becomes `packages/contracts/quality`, so the directory has one meaning. A contract package may contain only:

* TypeScript types and Zod 4 schemas (JSON Schema generated, section 1 of the contracts document);
* `defineTopic()` event definitions with versioned payload schemas;
* oRPC route signatures as contract routers (input and output schemas, no handlers);
* UI slot definitions: slot id, props schema, allowed component kinds;
* port interfaces (`XxxPort`) for anything another module calls, including repositories;
* a `conformance/` folder (section 5) and `fixtures/` golden data;
* pure helpers with no I/O (formatters, parsers of the module's own grammar).

Banned: React components, Drizzle tables, network calls, environment reads. A lint rule (`R9` below) enforces it, and `size-limit` caps each contract at 50 KB minified so nobody hides an implementation inside.

### 2.1 Semver rules

| Change | Version | Consumers |
| -- | -- | -- |
| New optional field, new port method with default, new topic, new slot | minor | Nothing to do; ranges are `^major.minor`. |
| Widening an input type, narrowing an output type, new enum value that consumers switch on | major | ADR, deprecation window, upcaster if it touches events or stored data. |
| Removing or renaming anything, changing a route path, changing slot props | major | Same, plus the compatibility matrix turns red until every consumer bumps. |
| Fix to a schema that was wrong (never accepted the documented value) | patch | None. |

Pre-1.0 (the whole Oct 1 build) uses `0.x`, where minor is breaking and patch is additive, exactly as npm treats `^0.x`. Every module ships `v0.1` of its contract during this build; `v1.0` is cut at the first release candidate that passes the shell swap drill (section 6).

### 2.2 Compatibility matrix

CI job `compat` (module-system issue 8) reads every `module.manifest.json`, resolves each `requires` range against the provider's declared `provides.version`, and writes `docs/platform/compat-matrix.md` and `compat-matrix.json`: rows are consumers, columns are contracts, cells are `ok`, `ahead` (consumer requires a newer version than provided: build fails), `behind` (provider moved major: warning during the deprecation window, failure after) and `-`. The job fails a PR that introduces `ahead` or an expired `behind`. The matrix is also the input the Blueprint's dependency views render.

### 2.3 How the contracts document maps onto packages

| Contracts document section | Contract package | Notes |
| -- | -- | -- |
| §1 conventions (ids, timestamps, `Principal`, `Money`, `FilterTree`, Zod) | `@paperos/core/types`, `core/filter`, `core/events` (PAP-302, PAP-279, PAP-303) re-exported and pinned by `contract-data-layer` | Contract-zero: the only code every contract may import. |
| §2 shared data model rows Tenant, Workspace, User, Membership, Agent principal | `contract-identity` | Tables stay in `packages/db`; the contract holds the types and ports. |
| §2 rows Page, Component | `contract-spec-builder`, `contract-design-system` | |
| §2 rows View, Record | `contract-tables` | `registerDataset()` is the port other modules call. |
| §2 rows Document, Comment, Notification | `contract-collab` (rooms grammar from `contract-realtime`) | |
| §2 rows Event, Job, Audit, File | `contract-data-layer` | |
| §2 row Ledger entry | `contract-business-core` | |
| §3 event bus | `core/events` envelope; topics declared in the publishing module's contract | Schema registry aggregates them (section 4). |
| §4 API conventions | `contract-data-layer` (error body, list shape, headers); routers per module contract | Gateway routes by contract (section 4). |
| §5 package boundaries | `ownership.json` (PAP-305) plus rules R7-R9 here | |
| §6 provide and consume matrix | Generated from manifests from now on | The hand-written table is frozen as the v0 baseline. |

## 3. Ports and adapters

The rule is one sentence: a module imports `@paperos/core`, any `@paperos/contract-*`, and its own package; nothing else. Everything a module offers is a port in its contract; the module's package holds the adapter. Consumers get the adapter from the kernel at boot, never by import.

Rules added to the PAP-305 dependency-cruiser config (generated from `ownership.json`, one source of truth):

| Rule | Statement |
| -- | -- |
| R7 | Any package may import any `@paperos/contract-*`. |
| R8 | No package imports another module's implementation package (`packages/<module>/**`), including type-only imports; `apps/*` compose modules through the kernel only. |
| R9 | `packages/contracts/**` imports only `@paperos/core/*` and other contract packages; the contract graph must be acyclic (checked). |
| R10 | `packages/kernel` imports `@paperos/core` and contracts, never a module. |
| R11 | A module may import its own contract's `conformance/` only from test files. |

`pnpm gen:dep-map` walks the manifests and the actual import graph, writes `docs/platform/dependency-map.json` (nodes: modules and contracts; edges: `requires`, `fills`, `publishes`, `subscribes`, each with the Linear identifiers of the issues that own them) and a Mermaid rendering. The file is committed; Gate 1 fails when the committed map is stale or when the import graph contains an edge the manifests do not declare ("undeclared dependency: tables -> collab via packages/views/src/comments.ts").

## 4. Middle tooling: `@paperos/kernel`

| Piece | Contract it serves | Behaviour |
| -- | -- | -- |
| Registry and DI container | every manifest | `createKernel({ appSpec, manifests })` validates manifests, resolves `requires` topologically, refuses cycles and version conflicts with module ids, and exposes `kernel.resolve(token)`. Tokens are typed: `const ViewQuery = port<ViewQueryPort>('@paperos/contract-tables', 'ViewQueryPort')`. Scopes: `singleton`, `request` (carries tenant and actor from PAP-34's session variables), `transient`. Two implementations bind side by side: `kernel.bind(ViewQuery, v1).bind(ViewQuery, v2, { impl: 'v2' })`; selection is by flag (next row). |
| Flag-driven swap | PAP-366 flags | Reserved flag family `module.<id>.impl` (variant flag, values are `impl` names). The container reads it per request, so a flip changes implementation within the 5 s PAP-366 guarantees, per tenant or globally. `shadow: true` runs both, returns the primary and diffs the secondary into `swap_shadow_diff` rows. |
| Event bus and schema registry | PAP-303 envelope | Topics from every contract are aggregated into `topics.json` (name, version, JSON Schema, publisher module, subscribers). `defineUpcaster(topic, fromVersion, toVersion, fn)` lets a v2 subscriber read v1 events during the window; `dualPublish(topic, [v1, v2])` during a swap; publishing an undeclared or unregistered topic fails at boot, as today. |
| API gateway / BFF routing | PAP-267, PAP-268 | Contract routers mount by contract name, not by module: `mountContract(kernel, '@paperos/contract-tables')` looks up the bound implementation per request and forwards to its handlers. `X-PaperOS-Impl: v2` (staff and agents only) forces an implementation for canary testing; the response echoes `X-PaperOS-Impl` so screenshots and gate artefacts record which one ran. |
| UI slot / extension system | `contract-app-shell` | The shell exposes named slots with Zod props (`shell.nav`, `shell.sidebar`, `shell.inspector`, `shell.commandBar`, `shell.header.actions`, `shell.userMenu`, `shell.tenantSwitcher`, `shell.settings.sections`, `record.panel.tabs`, `view.toolbar`, `dashboard.blocks`). Modules fill slots in their manifest with a registered `ui.<component>` id (PAP-74) or a lazy import, an `order` and a `when` guard (`can('...')` or `flag('...')`). `<Slot name="shell.nav" />` renders whatever is registered; an unknown slot or invalid props fails at boot in dev and renders nothing in production with a telemetry event. A new shell only has to expose the same slot ids and props. |
| Data-access ports | `contract-*` repositories | Repositories are interfaces in contracts (`CommentRepository`, `ViewRepository`, `LedgerRepository`); Drizzle implementations live in module packages; `InMemoryXxxRepository` doubles live in `conformance/` so any implementation can be tested without Postgres. Modules never import `@paperos/db` tables of another module. |
| Config and secrets port | `contract-app-shell` `ConfigPort`, `SecretsPort` | A module declares `settingsSchema` (config) and `secrets: ['STRIPE_SECRET_KEY']` (names only). The kernel validates config at boot with PAP-17's typed layer and hands out `secrets.get(name)`; the credential broker (PAP-300) is one adapter, `.env` another. No module reads `process.env`. |
| Migration adapter kit | data shapes | `defineMigrationAdapter({ contract, from, to, upcast, downcast?, backfill? })` covers four shapes: event payloads (upcasters), API responses during a deprecation window (response adapters at the gateway), tables (expand-contract: add, dual-write, backfill job on pg-boss, verify, contract) and Yjs documents (schema version in the doc meta plus a converter run on open). The kit generates the checklist the swap CLI enforces. |

`@paperos/kernel` is small on purpose: registry, container and slots are perhaps 1,500 lines; the bus, gateway and flags reuse PAP-303, PAP-267 and PAP-366. The value is that these are the only five places a cross-module dependency can exist, so a swap is a search of five places, not the whole repo.

## 5. Conformance tests

Every contract ships `conformance/`: `defineConformanceSuite<T>(name, (factory: () => Promise<T>) => void)` producing a Vitest suite parametrised by an implementation factory. The suite is the executable meaning of the contract: for `ViewQueryPort` it compiles the ten golden `ViewSpec` fixtures and compares rows, cursors and aggregates; for `ShellSlots` it mounts each slot with each golden fill and asserts render, order, guard and props validation; for `LedgerPort` it posts the fixture transactions and checks balances and immutability.

Rules: a module's own implementation runs its suite in Gate 1 (`pnpm conformance`); during a swap the runner (`paperos module conformance <id> --impl v1,v2`) runs the same suite against both and produces `conformance.json`, a PAP-239 gate artefact with pass, fail and a per-case diff. Golden fixtures live in `fixtures/*.json`, are validated against the contract's schemas in CI, and are the shared truth for shadow-run diffs. Adding a fixture is a minor bump; changing one is a major bump.

## 6. Swap playbook

Generic steps, enforced by `paperos module swap <id> --to <impl>` (module-system issue 10), which refuses to advance a step whose gate is red:

| Step | Gate |
| -- | -- |
| 1 Propose | ADR in `docs/adr/` (PAP-130) naming the contract version implemented, the swap risk and the rollback; a Linear issue per step for `critical` risk. |
| 2 Fork behind flag | New package (or new `impl` in the same package) declares `provides: [{ contract, version, impl: 'v2' }]`; flag `module.<id>.impl` exists, default `v1`; CI builds both. |
| 3 Pass conformance | `conformance.json` green for v2 on every port and fixture; compatibility matrix unchanged (same contract version) or every consumer bumped (new major). |
| 4 Shadow-run | `shadow: true` on staging for at least one nightly gate run: diff count under threshold, no v2-only errors, performance budget (PAP-242) met. Events dual-published; subscribers idempotent on `event.id`. |
| 5 Canary flip | Flag rule for the demo tenant, then staff tenants, each for one release train (PAP-88); Gate 3 screenshots carry `X-PaperOS-Impl`. |
| 6 Flip default | Flag default `v2`; v1 stays bound; deprecation window starts (30 days, same as the API rule). |
| 7 Remove | After the window: unbind v1, delete package, `knip` clean, matrix regenerated, ADR status `superseded`. |

Rollback at steps 4-6 is the flag: flip back, under five seconds, no deploy. Data rollback is guaranteed by expand-contract: no column, table, topic version or slot is removed before step 7, so v1 always finds its shapes. A swap that needs a destructive migration before step 7 is not a swap; it is a new module, and it goes to Needs Justin.

Rewriting the shell specifically: `app-shell` is the module that provides `contract-app-shell` (slots, route contribution, layout, window manager, config, flags). A new shell is `apps/web-next` (or a new renderer inside `apps/web`) that provides the same contract version. Steps 3-5 are concrete: the shell conformance suite mounts every registered slot fill from every module, composes every module's routes and asserts the route table is identical, runs the window manager and config port fixtures, then Gate 3 captures the seven-width screenshot matrix for both shells and the vision agent (PAP-84) diffs them. Modules change nothing: their manifests already say which slots they fill and which routes they contribute. The shell swap drill (module-system issue 13) rehearses this with a deliberately minimal second shell before Oct 1, so the claim is tested, not asserted.

## 7. Dependency ownership rules

* **Ownership.** A contract is owned by its module's owner agent and project (table 1.1); `ownership.json` (PAP-305) gains a `contracts` section and CODEOWNERS routes contract PRs to the owner plus Atlas. The owner alone may bump a contract version.
* **Proposing a breaking change.** ADR with the diff of the contract, the new major version, the list of affected consumers from the compatibility matrix, the upcaster or adapter plan, and the removal date. Atlas approves; a change that touches `critical` modules is a Needs Justin card. The deprecation window is 30 days from the flip of the default; during it both versions are provided and the matrix shows `behind` as a warning.
* **Consumers.** A consumer pins `^0.minor` (or `^major.minor` after 1.0) and lists the ports it uses; it may only widen what it accepts. A consumer that needs something a contract lacks opens a Spec issue on the provider's project, never a workaround import.
* **Linear mirrors the manifests.** For every `requires` edge from module A to module B, the issue "Publish `@paperos/contract-B` v0.1" blocks A's Build issues that consume it, and A's "Wire A behind the module registry" issue is blocked by B's contract and conformance issues. The weekly re-audit (PAP-306) regenerates the dependency map, compares it with the Linear `blocks` graph and opens a drift issue for every edge present in one and missing in the other. The Blueprint's dependency views render the same `dependency-map.json`, so the picture Justin sees, the graph the orchestrator promotes from and the imports the lint allows are the same graph.
* **Umbrellas.** An umbrella issue carries the module's "Module boundary" paragraph (which contract it implements, what it may import); its children inherit it. No child may add a dependency its umbrella does not declare.

## 8. What this adds to the plan

Three issues per module (publish contract v0.1 with manifest; conformance suite; wire behind the registry with an adapter and flag), fourteen issues in the new project Module System & Swap Tooling (the fourteen pieces named in sections 1.2 to 6, ending with the shell swap drill), and a "Module boundary" paragraph on each module's umbrella or main Build issue. Full specs: `round3/module-issues.json`.
