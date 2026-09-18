# Round 4 digest: Module System & Swap Tooling (`module-system`)

Benchmarks: OSGi (bundle lifecycle, service registry, semantic versioning); Backstage plugins and extension points; Nx enforce-module-boundaries and affected graph; Terraform providers (schema, versioning, registry, generators); Pact consumer-driven contracts and api-extractor / oasdiff; LaunchDarkly and Unleash flag-driven rollout; Webpack Module Federation; Changesets and semantic-release.

Feature matrix: 48 rows, 22 covered, 7 partial, 19 gap. New issues: 18 (5 children of existing issues, 13 gap issues, 1 deferred to v0.2). Amendments to existing specs: 8. Cross-project suggestions: 4.

## Feature matrix

| Feature | Covered by | Status | Note |
|---|---|---|---|
| Module manifest schema and validator with diagnostics | PAP-433 | covered | `lifecycle` and `secrets` extensions should be reserved (amendment). |
| Registry and DI container with typed ports and scopes | PAP-434 | covered | Runtime enforcement of `requires` and system-scope audit missing (amendment). |
| Host integrations: Hono middleware, React provider, worker scope, boot files | PAP-434 | partial | Child r4/module-system/kernel-integrations. |
| Flag-driven swap, shadow-run diffs, kill switch | PAP-435 | covered | Staff page split out (r4/module-system/modules-settings-page). |
| Event schema registry, upcasters, dual-publish | PAP-436 | covered |  |
| API gateway routing by contract, response adapters | PAP-437 | covered |  |
| UI slot and extension system | PAP-438 | covered |  |
| Dependency lint rules and committed dependency map | PAP-439 | covered |  |
| Contract compatibility matrix | PAP-440 | covered |  |
| Breaking-change detection and semver bump enforcement | PAP-440 | gap | The matrix trusts version numbers; nothing checks them against the change (r4/module-system/contract-diff). |
| Changesets for contract packages | PAP-52 | gap | Folded into r4/module-system/contract-diff. |
| Conformance runner, capability handling, artefact | PAP-441 | covered |  |
| Output normaliser and fixture lock shared with shadow diffs | PAP-441, PAP-435 | partial | Child r4/module-system/conformance-normaliser. |
| Reference sample module with good, bad and v2 implementations | PAP-441, PAP-442 | gap | Three issues test against a sample nobody owns (r4/module-system/sample-module). |
| Module scaffold generator | — | gap | Seventeen contract issues repeat a forty-file layout by hand (r4/module-system/module-scaffold). |
| Test kernel binding memory doubles for consumer tests | PAP-434, PAP-441 | gap | r4/module-system/test-kernel. |
| Schema-driven fixture factory and negative generator | PAP-441 | gap | r4/module-system/schema-fixture-factory. |
| Swap playbook CLI with gates and rollback | PAP-442 | covered | Linear integration split out (r4/module-system/swap-linear-umbrella). |
| Data migration adapter kit: tables, events, API | PAP-443 | covered |  |
| Yjs document schema versioning and converters | PAP-443 | partial | Child r4/module-system/ydoc-converter. |
| Config and secrets port | PAP-444 | covered |  |
| Tenant-level module settings forms from `settingsSchema` | PAP-444, PAP-264 | gap | r4/module-system/module-settings-ui. |
| Module docs generator | PAP-445 | covered |  |
| Shell swap drill | PAP-446 | covered | Success criteria should count `apps/web` edits and require PAP-84 (amendment). |
| Service-kind swap drill (forge to GitHub read adapter) | PAP-455 | gap | Deferred (r4/module-system/service-swap-drill). |
| Module lifecycle hooks and ordered graceful shutdown | PAP-434 | gap | OSGi lifecycle; r4/module-system/lifecycle-and-health. |
| Per-module health aggregated into /healthz and /readyz | PAP-269 | gap | Folded into r4/module-system/lifecycle-and-health. |
| Kernel observability: span per port call, per-module dashboards | PAP-40 | gap | r4/module-system/kernel-otel. |
| Port resilience: timeouts, circuit breakers, degraded fallbacks | PAP-438, PAP-368 | gap | Slot fills have error boundaries; ports have nothing (r4/module-system/port-resilience). |
| Chaos toggle proving module isolation on staging | PAP-253 | gap | Folded into r4/module-system/port-resilience. |
| Kernel devtools and inspector page | PAP-435 | gap | r4/module-system/kernel-devtools. |
| Slot overlay for debugging fills | PAP-438 | gap | Folded into r4/module-system/kernel-devtools. |
| Affected-module CI from the dependency map | PAP-439, PAP-78 | gap | r4/module-system/affected-module-ci. |
| Port usage tracking and `requires[].ports` derivation | PAP-440, PAP-439 | partial | Hand-maintained today (r4/module-system/port-usage-tracking). |
| Runtime enforcement of undeclared contract resolution | PAP-434, PAP-439 | partial | Lint only; amendment on PAP-434. |
| Module enable and disable per tenant with retained data | PAP-266 | covered | app-shell |
| Browser-side lazy module chunks and KernelProvider hydration | PAP-265, PAP-434 | partial | Amendment on PAP-434; route chunks amendment on PAP-16. |
| Kernel security: system scope with reason and audit, no tenant escalation | PAP-434, PAP-38 | partial | Amendment on PAP-434. |
| Per-module Postgres schema namespaces | PAP-265, PAP-32 | gap | Cross-project suggestion to data-layer. |
| Cross-module unit of work and transaction boundaries | PAP-448 | gap | Cross-project suggestion to data-layer. |
| Contract packages published to a registry for generated apps | PAP-430 | covered | r4/app-shell/upgrade-package-registry |
| Ownership and CODEOWNERS routing for contracts | PAP-305, PAP-439 | covered |  |
| Weekly drift audit between manifests and Linear | PAP-306 | covered | pm-linear |
| Deprecation windows and response adapters | PAP-440, PAP-437 | covered |  |
| Multi-window kernel instances | PAP-434 | covered | Edge case. |
| Conformance green as a release-candidate certification gate | PAP-254 | gap | Cross-project suggestion to quality. |
| Manifest-declared jobs, permissions and migrations per module | PAP-265 | covered | app-shell |
| Third-party modules outside the monorepo, plugin marketplace | — | covered | Explicit non-goal. |

## New issues

| Key | Title | Parent | Type | Size | Model / effort | Priority | Milestone | Deferred |
|---|---|---|---|---|---|---|---|---|
| `r4/module-system/kernel-integrations` | Kernel host integrations: Hono request-scope middleware, React `KernelProvider` and `useKernel`, worker job scope and the `apps/*/src/kernel.ts` boot files | PAP-434 | Build P0 | S (2) | Sonnet 5 / medium | 1 | Kernel and lint live (2026-09-22) |  |
| `r4/module-system/modules-settings-page` | `/settings/modules` staff page: bound implementations per module, tenant overrides, shadow toggle and diff counts, kill switch with reason and the audit trail | PAP-435 | Build P1 | S (2) | Sonnet 5 / medium | 2 | Contracts and conformance wired (2026-09-27) |  |
| `r4/module-system/swap-linear-umbrella` | Swap CLI Linear integration: umbrella and per-step issues through `PmSourcePort`, evidence comments per gate and the Needs Justin card before `flip` for critical-risk modules | PAP-442 | Build P1 | S (2) | Sonnet 5 / medium | 2 | Shell swap drill passes (2026-10-01) |  |
| `r4/module-system/ydoc-converter` | Yjs document schema versioning: `ydocVersion` in the document meta, converter run on open through `CollabDocPort`, snapshot retention and the 20 MB guard | PAP-443 | Build P1 | S (2) | Sonnet 5 / medium | 2 | Shell swap drill passes (2026-10-01) |  |
| `r4/module-system/conformance-normaliser` | Conformance output normaliser and fixture lock: placeholder rules for UUIDv7, timestamps and signed cursors, set ordering, per-port overrides and `fixtures.lock` hashing shared with shadow diffs | PAP-441 | Build P0 | S (2) | Sonnet 5 / medium | 1 | Kernel and lint live (2026-09-22) |  |
| `r4/module-system/sample-module` | Reference module `sample`: `@paperos/contract-sample` with `good`, `bad` and `v2` implementations, fixtures, conformance suite and manifests used by the runner, swap CLI, drill rehearsal and scaffold | — | Build P0 | S (2) | Opus 5 / high | 1 | Kernel and lint live (2026-09-22) |  |
| `r4/module-system/module-scaffold` | `paperos module new <id>`: scaffold the contract package, manifest, conformance skeleton, fixtures, memory double, docs stub, ownership entry and `kernel.ts` registration | — | Build P1 | M (3) | Sonnet 5 / medium | 1 | Contracts and conformance wired (2026-09-27) |  |
| `r4/module-system/contract-diff` | `pnpm contract:diff` breaking-change detector: compare Zod schemas, port signatures, topics and slot props between the base branch and the PR, require the matching semver bump and a changeset | — | Infra P1 | M (3) | Opus 5 / high | 1 | Contracts and conformance wired (2026-09-27) |  |
| `r4/module-system/test-kernel` | Kernel test kit: `createTestKernel({ modules, doubles, tenant, actor })` wiring memory doubles from every contract's `conformance/memory`, `withImpl`, request-scope helpers and Vitest matchers | — | Build P1 | S (2) | Sonnet 5 / medium | 1 | Contracts and conformance wired (2026-09-27) |  |
| `r4/module-system/lifecycle-and-health` | Module lifecycle and health: `onBoot`, `onReady`, `onStop` hooks in `bind`, ordered graceful shutdown, per-module health checks aggregated into `/healthz` and a boot timing report | — | Build P1 | M (3) | Sonnet 5 / medium | 2 | Contracts and conformance wired (2026-09-27) |  |
| `r4/module-system/kernel-otel` | Kernel instrumentation: one OpenTelemetry span per port call tagged with module, implementation and contract version, per-module latency and error dashboards, and cost attribution hooks | — | Build P1 | S (2) | Sonnet 5 / medium | 2 | Shell swap drill passes (2026-10-01) |  |
| `r4/module-system/port-resilience` | Port resilience: timeouts, circuit breaker and degraded fallbacks for optional ports in kernel resolve wrappers, `MODULE_DEGRADED` telemetry and the chaos toggle for staging | — | Build P1 | M (3) | Sonnet 5 / medium | 2 | Shell swap drill passes (2026-10-01) |  |
| `r4/module-system/kernel-devtools` | Kernel devtools: `/dev/modules` page with the dependency graph, bindings and scopes, a slot overlay highlighting fills by module, topic flow and flag state, plus `paperos module explain <port>` | — | Build P1 | M (3) | Sonnet 5 / medium | 2 | Shell swap drill passes (2026-10-01) |  |
| `r4/module-system/affected-module-ci` | Affected-module CI: derive changed modules from the dependency map and the diff, run only their Gate 1 steps plus their consumers' conformance suites, with a full run on `main` and nightly | — | Infra P1 | S (2) | Sonnet 5 / medium | 2 | Contracts and conformance wired (2026-09-27) |  |
| `r4/module-system/schema-fixture-factory` | Schema fixture factory: `fixtureFor(schema, { seed, overrides })` generating valid instances for any contract Zod schema, `invalidFor(schema)` for negatives, used by conformance doubles, Gate 4 and the test kernel | — | Build P1 | S (2) | Sonnet 5 / medium | 2 | Contracts and conformance wired (2026-09-27) |  |
| `r4/module-system/port-usage-tracking` | Port usage tracking: derive `requires[].ports` from static analysis of `kernel.resolve` and `usePort` calls, compare with runtime `kernel.describe()` counters, and fail on manifest drift | — | Build P2 | S (2) | Sonnet 5 / medium | 3 | Shell swap drill passes (2026-10-01) |  |
| `r4/module-system/module-settings-ui` | Auto-generated module settings forms from `settingsSchema` at `/settings/modules/<id>`: Zod to form fields, tenant scope, validation, secret-name display and audit | — | Build P2 | S (2) | Sonnet 5 / medium | 3 | Shell swap drill passes (2026-10-01) |  |
| `r4/module-system/service-swap-drill` | Second swap drill: swap the forge module to a read-only GitHub adapter behind `module.forge.impl`, walk the playbook for a `service`-kind module and record findings | — | Review P2 | M (3) | Opus 5 / high | 4 | Shell swap drill passes (2026-10-01) | yes |

## Amendments to existing specs

* **PAP-434** (Spec): * Runtime enforcement of `requires`: `kernel.resolve` from a module scope refuses a contract the module's manifest does not list (`REQUIRES_UNDECLARED`, throws in dev, telemetry and `undefined` in production for optional-shaped tokens), so lint R8 and the kernel agree. * `kernel.system(reason)` is the only way to obtain a scope without a tenant; it writes a PAP-38 audit row with the reason and caller module, and lint forbids it outside `packages/jobs`, `packages/sync` and `apps/*/src/kernel.ts`. * Browser: module implementation packages are loaded through `import()` per enabled module (`kernel.ts` uses dynamic imports keyed by manifest id) so the initial bundle carries the kernel and contracts only; `KernelProvider` renders `ui.skeleton` until the modules the current route needs have loaded.
* **PAP-441** (Dependencies): * The sample suite and its two implementations are delivered by `r4/module-system/sample-module` (hard); the normaliser and `fixtures.lock` by `r4/module-system/conformance-normaliser` (hard, shared with PAP-435). Blocks `r4/module-system/test-kernel` and `r4/module-system/module-scaffold`.
* **PAP-442** (Spec): * `--dry-run` evaluates every gate for the current step and prints the verdicts without writing the state file. * The scripted sample swap uses `r4/module-system/sample-module` (`good` to `v2`); Linear umbrella, step issues and the Needs Justin card are delivered by `r4/module-system/swap-linear-umbrella` (soft; `--no-linear` until it lands). * `contract:diff` (`r4/module-system/contract-diff`) output is required evidence for step 1 when the contract version changed.
* **PAP-446** (Spec): * Success criteria also count lines changed in `apps/web` (must be zero outside the kernel boot file) and in `packages/contracts/app-shell` (must be zero, or the drill is a contract change, not a swap). * PAP-84 vision diff is a hard dependency for the screenshot classification; PAP-82 alone gives contact sheets without verdicts. * Rehearsal: the drill is first run end to end on `r4/module-system/sample-module` (`good` to `v2`) the day before, so CLI defects surface before the shell run.
* **PAP-433** (Spec): * Reserved extension fields validated when present: `secrets: string[]` (PAP-444), `lifecycle: { startupBudgetMs, healthIntervalMs, drainTimeoutMs }` (`r4/module-system/lifecycle-and-health`), `resilience` per port (`r4/module-system/port-resilience`) and `issues: string[]` (PAP-439 map); unknown fields still fail. `pnpm modules:validate --fix` is reserved for `r4/module-system/port-usage-tracking`.
* **PAP-436** (Test plan): * Conformance case shared with every subscriber contract: a duplicate delivery of the same `event.id` (as happens under `dualPublish`) must be a no-op, asserted by the runner for each subscriber double; `dualPublish` and PAP-304 idempotency keys are cross-referenced in `docs/platform/events.md`.
* **PAP-438** (Edge cases): * Fill throws during render: the per-fill error boundary reports through PAP-368 with `slot` and `module`, renders `ui.errorState` inline and the rest of the slot renders; a fill that throws three times in a minute is unregistered for the session (`slot.fill_disabled` telemetry). * Fills are landmarks: `shell.nav` fills render inside `<nav>` with `aria-label` from the manifest `title`, checked by the PAP-73 audit.
* **PAP-445** (Spec): * Generated pages include a "Health and swaps" section reading `/healthz.modules` (`r4/module-system/lifecycle-and-health`), the bound implementations and last shadow diff count (PAP-435) and the last `contract-diff` verdict (`r4/module-system/contract-diff`), so the module page is the one place a session checks before touching a module.

## Cross-project suggestions

* **data-layer**: Per-module Postgres schema namespaces (`CREATE SCHEMA <module>`) with RLS defaults, so a module's tables are physically grouped and a swap can expand-contract inside one schema. PAP-265 applies migrations per module but tables share `public`; swap safety and `pnpm modules:purge` (PAP-266) become simpler with namespaces.
* **data-layer**: Cross-module unit of work: `UnitOfWorkPort` in `contract-data-layer` that lets a request span repositories from two modules in one transaction with the outbox. Business-core posting rules (PAP-394) and tables automations (PAP-388) both need it; today each module opens its own transaction.
* **quality**: Release-candidate certification (PAP-254) requires `conformance.json` green for every registered suite and a clean `contract-diff` report, and the digest (PAP-89) lists modules whose shadow diff count is non-zero. The module system produces the artefacts; the release train does not yet read them.
* **realtime**: Window bus contract (`contract-realtime` `WindowBusPort`) as the only cross-window channel the kernel permits, with a conformance fixture for two windows. PAP-434 names the window bus as the single cross-window channel but PAP-145 and PAP-262 both define `BroadcastChannel('paperos-windows')` payloads independently.

## What was missing and why it matters

* Three kernel issues test against a sample module nobody builds; `r4/module-system/sample-module` (contract, good, bad and v2 implementations) is the fixture the runner, the swap CLI, the drill rehearsal and the scaffold all need first.
* The module system had no generator and no test kit: seventeen contract issues repeat a forty-file layout by hand and every consumer test either imports another module (forbidden by R8) or hand-rolls a fake, when the contracts already ship memory doubles.
* Semver was a rule, not a check: the compatibility matrix trusts version numbers, so a PR that narrows an output with a patch bump merges; `contract:diff` classifies changes against the §2.1 table and requires the matching bump and a changeset.
* Modules had `bind` but no lifecycle, health, spans or containment: a hanging growth adapter would take the shell down, `/healthz` could not say which module was broken, and the playbook's performance gate had no per-port latency to read.
* Operability was missing for developers and staff alike: a devtools page with the dependency graph and a slot overlay, affected-module CI that uses the dependency map we already commit, and schema-driven settings forms so eighteen modules do not each need a bespoke settings page.
