# Round 4 digest: Library Discovery & Integration (`libraries`)

Features: 44 (26 covered, 6 partial, 12 gap). New issues: 12 (0 children, 12 gaps, 1 deferred to v0.2). Amendments: 7. Cross-project suggestions: 5.

Benchmarks: Renovate and Dependabot; FOSSA and ScanCode license scanning; Backstage software catalog; ADR tooling (adr-tools, log4brains); SBOM and CycloneDX; OpenSSF Scorecard and deps.dev; publint and arethetypeswrong; pnpm catalogs, syncpack, knip; npm and crates.io registries; Nx and Turborepo module boundary lint; Socket.dev supply-chain checks; Electron and Tauri About dialogs for attribution.

## What was missing and why it matters

1. Five research spikes (PAP-212, PAP-292, PAP-293, PAP-294, PAP-127) each describe the same Vite-plus-Playwright harness and seven issues cite a `compose-smoke` CI job that nothing builds; two Infra issues ship the harness kit and the reusable workflow so every spike measures the same way and the 6 GB budget table is generated from artefacts.
2. The registry says what we adopted; nothing tells a cold session how to use it here. Per-library usage notes with machine-readable `ban:` lines, generated lint guardrails from rejected and replaced entries, and a one-command `pnpm lib adopt` make borrow-before-build the default path for agents.
3. Twenty sessions running `pnpm add` will produce duplicate versions and unused dependencies within a week; pnpm catalogs, syncpack, dedupe and knip in Gate 1 keep the monorepo aligned, which also makes Renovate bumps one PR per group.
4. Facts stop at downloads and stars; OpenSSF Scorecard, deps.dev advisories, publint and arethetypeswrong add security and packaging evidence with a critical-advisory hard gate. An import census makes `migrationCostHours` a number with evidence and gives the swap playbook its step-one input.
5. Governance gaps around the edges: a patch and fork policy with registry rows and expiry, a dependency health page joining five CI artefacts, and the in-app open source licenses page that attribution licenses require; the software cost model is filed as v0.2.

## New issues

| Key | Title | Parent | Size | Model / effort | Priority | Milestone | Deferred |
|---|---|---|---|---|---|---|---|
| `r4/libraries/spike-harness-kit` | Spike harness kit: `spikes/_kit` with route-per-candidate Vite template, Playwright trace-to-FPS script, bundle analyzer output and the `pnpm spike` runner | - | S (2) | Sonnet 5 / high | 2 | Evaluation process |  |
| `r4/libraries/compose-smoke-workflow` | Reusable `compose-smoke` workflow: matrix over `ops/compose/**` and `spikes/oss-products/*`, health probes, `docker stats` capture, image cache and 20-minute cap | - | S (2) | Sonnet 5 / high | 2 | Core adoptions decided |  |
| `r4/libraries/facts-security-quality` | Extend `lib-facts` with OpenSSF Scorecard, deps.dev advisories, `publint` and `arethetypeswrong` checks feeding a `security` and a `packaging` rubric extra | - | S (2) | Sonnet 5 / medium | 3 | Core adoptions decided |  |
| `r4/libraries/dependency-hygiene` | Monorepo dependency hygiene: pnpm `catalog:` for shared versions, `syncpack` alignment, `pnpm dedupe --check`, `knip` unused dependencies in Gate 1 | - | M (3) | Sonnet 5 / medium | 2 | Registry live |  |
| `r4/libraries/library-usage-notes` | Adopted-library usage notes: one `docs/libraries/notes/<id>.md` per adopted library with import conventions, banned APIs, gotchas and version pin, linted against the registry | - | M (3) | Sonnet 5 / medium | 2 | Registry live |  |
| `r4/libraries/library-guardrails-lint` | Library guardrails as lint: generated `no-restricted-imports` from rejected and replaced registry entries plus `ban:` lines in usage notes, wired into Gate 1 | - | S (2) | Sonnet 5 / medium | 2 | Registry live |  |
| `r4/libraries/patch-fork-policy` | Patch and fork policy: `pnpm patch` rules, `patches/` entries in the registry with upstream PR link and expiry, CI check that every patch is registered | - | S (2) | Sonnet 5 / medium | 3 | Registry live |  |
| `r4/libraries/dependency-health-page` | Dependency health page: outdated versions, pending majors, advisories, license mix, bundle share and review-due entries rendered from the registry and CI reports | - | S (2) | Sonnet 5 / medium | 3 | Registry live |  |
| `r4/libraries/import-census` | Import census: `pnpm lib census` records which modules and files import each adopted library, refreshes migration-cost estimates and adds a swap-impact column to the registry | - | S (2) | Sonnet 5 / medium | 3 | Registry live |  |
| `r4/libraries/oss-licenses-page` | In-app open source licenses: public `/_public/licenses` page and desktop About dialog rendering `THIRD_PARTY_NOTICES.md` per bundle | - | S (2) | Sonnet 5 / medium | 3 | Registry live |  |
| `r4/libraries/adopt-workflow-cli` | Adoption workflow CLI: `pnpm lib adopt <pkg>` chains facts, scorecard, ADR draft, registry entry, usage note and guardrails in one guided run | - | S (2) | Sonnet 5 / medium | 3 | Registry live |  |
| `r4/libraries/library-cost-model` | Library and service cost model: paid tiers, seats, renewal dates and monthly cost per registry entry with a line in the daily burn report | - | S (2) | Sonnet 5 / medium | 4 | Registry live | yes |

## Feature matrix

| Feature | Status | Covered by | Note |
|---|---|---|---|
| Evaluation rubric with anchors, weights, hard gates and scorecards | covered | PAP-209 | Ready for Claude. |
| Facts collector (downloads, maintenance, license, types, size) | covered | PAP-209 |  |
| Security and packaging facts (OpenSSF Scorecard, advisories, publint, attw) | gap | r4/libraries/facts-security-quality |  |
| ADR template with alternatives and re-open criteria | covered | PAP-209, PAP-130 |  |
| License policy tiers by context, CI check, waivers, notices, cargo-deny | covered | PAP-211 |  |
| In-app open source licenses page and About dialog | gap | r4/libraries/oss-licenses-page | Attribution licenses require visibility. |
| SBOM (CycloneDX) and vulnerability audit | covered | PAP-80 | quality. |
| Supply-chain integrity (pinning, min release age, provenance) | covered | PAP-358 | forge. |
| UI primitives survey and ADR | covered | PAP-212 | Default Base UI after 09-19. |
| Table, chart, map library spikes and ADRs | covered | PAP-292, PAP-293 |  |
| Canvas and editor shortlist handed to collab | covered | PAP-294, PAP-127 |  |
| Backend building blocks (jobs, email, PDF, search, observability, flags, storage, validation, runtime) | covered | PAP-295, PAP-296, PAP-297 |  |
| Whole OSS products evaluated with modes (embed, fork, borrow, reject) | covered | PAP-350, PAP-351, PAP-352 |  |
| Shared spike harness (Vite routes, FPS traces, bundle JSON, screenshots) | gap | r4/libraries/spike-harness-kit | Five spikes describe the same harness. |
| `compose-smoke` CI workflow with health probes and docker stats | gap | r4/libraries/compose-smoke-workflow | Named by seven issues, built by none. |
| Resource budget table under 6 GB | covered | PAP-296, r4/libraries/compose-smoke-workflow | Generated from smoke artefacts. |
| Embed contracts for OSS products (SSO, theming, tenant mapping) | partial | PAP-352 | Contracts written; no implementation kit; cross-project suggestion to app-shell. |
| Registry of adopted, trialing, rejected libraries with drift check | covered | PAP-216 |  |
| Registry seeded with every production dependency | covered | PAP-216 | In its DoD. |
| Per-library usage notes for cold sessions (imports, banned APIs, gotchas) | gap | r4/libraries/library-usage-notes | Agent-friendliness of our adoption. |
| Lint guardrails from registry status and banned APIs | gap | r4/libraries/library-guardrails-lint |  |
| Import census and swap-impact per library | gap | r4/libraries/import-census | Makes migrationCostHours evidence-based. |
| One-command adoption workflow | gap | r4/libraries/adopt-workflow-cli | Five CLIs across four issues today. |
| Renovate grouped upgrades with agent summaries and automerge | covered | PAP-217 |  |
| Version alignment, catalogs, dedupe, unused dependencies | gap | r4/libraries/dependency-hygiene | Twenty sessions running pnpm add. |
| Patch, vendoring and fork policy with registry rows and expiry | gap | r4/libraries/patch-fork-policy |  |
| Dependency health dashboard | gap | r4/libraries/dependency-health-page | Five artefacts, no page. |
| Paid tiers, renewals and monthly software cost | gap | r4/libraries/library-cost-model | Deferred v0.2. |
| Weekly Scout scan for new libraries | covered | PAP-218 | Deferred. |
| Scout scan also covers MCP servers and Claude skills | partial | PAP-218 | Amendment proposed. |
| MCP server and connector catalogue with scope classes | covered | PAP-210 | Ready for Claude. |
| MCP server security review (tool descriptions, injection surface) | partial | PAP-210, PAP-299 | Sentinel sign-off per scope class; no rubric extra. Not issued. |
| Major upgrade playbooks (codemod-driven) | partial | PAP-217, PAP-430 | Majors become Backlog issues; not issued. |
| Bundle weight attribution per dependency | covered | PAP-87, r4/libraries/dependency-health-page |  |
| Rust crate and Docker image evaluation | covered | PAP-209, PAP-211 | Non-npm rules in the rubric. |
| Fonts, icons and asset licenses | covered | PAP-211 |  |
| WebView (webkit2gtk, WKWebView) compatibility as a gate | covered | PAP-209, PAP-212 |  |
| Internal software catalog (modules, contracts, services) | covered | PAP-445, PAP-439 | module-system. |
| Time-box and budget guard for research sessions | covered | PAP-111 | agents. |
| Registry rendered through the views engine | partial | PAP-216 | Plain table by design; swap later. Not issued. |
| Third-party API terms and rate limits tracking | partial | PAP-210, PAP-121 | vendorRateLimit in the catalog; ToS not tracked. Not issued. |
| Deprecation tracking and runtime warnings | covered | PAP-216, r4/libraries/library-guardrails-lint | Status plus lint warnings window. |
| Contract package, conformance suite, kernel wiring | covered | PAP-493, PAP-495, PAP-497 |  |
| Golden task for Scout evaluations | covered | PAP-218, PAP-110 |  |

## Amendments to existing specs

- **PAP-216** (Spec): Entry gains optional `patches[]` (`r4/libraries/patch-fork-policy`), `census` and `swapImpact` (`r4/libraries/import-census`) and `cost` (`r4/libraries/library-cost-model`, deferred); `version` is read from the pnpm `catalog:` when `r4/libraries/dependency-hygiene` lands. Check rule: `adopted` without `docs/libraries/notes/<id>.md` warns for 7 days after adoption, then errors.
- **PAP-218** (Spec): Scan sources include MCP servers (npm keyword `mcp`, the official registry when public) and Claude Code skills or plugins relevant to open issues; candidates of those kinds are routed to PAP-210 (catalog entry) and PAP-105 (skills) instead of the library registry, with the same one-comment-per-issue rule.
- **PAP-214** (Spec): `compose-smoke` is the reusable workflow from `r4/libraries/compose-smoke-workflow`; children declare `x-paperos.healthcheck` and `x-paperos.warmupSeconds` in their compose files so the budget table is generated from artefacts. If the workflow is unmerged when a child starts, run the same commands by hand and record numbers in `results/backend-*.json` in the workflow's result schema.
- **PAP-352** (Scope): Time-box guard: if the two spikes consume the 4 hours, write the ADR with provisional modes for Cal.com and Formbricks and mark the borrow reference docs and embed contracts for those two as follow-up comments on PAP-188 and PAP-100 rather than exceeding the box; the nine-row matrix must still be complete.
- **PAP-212** (Spec): Build the five candidates on the shared harness (`r4/libraries/spike-harness-kit`) when merged: `spikes/ui-kits/candidates/<lib>/`, `pnpm spike ui-kits --bench --shots`; results in `results/summary.json` feed `pnpm lib score --facts-from`. If the kit is unmerged on 09-17, build inline and move the routes into the kit shape before closing.
- **PAP-217** (Spec): Renovate `pnpm.catalog` support enabled so catalog bumps (`r4/libraries/dependency-hygiene`) arrive as one PR per group; PRs touching a package listed in registry `patches[]` get label `needs-patch-review` and never automerge (`r4/libraries/patch-fork-policy`).
- **PAP-209** (Spec): Optional extras `security` (OpenSSF Scorecard, advisories) and `packaging` (`publint`, `attw`) from `r4/libraries/facts-security-quality`; hard gate `openAdvisory: critical`. `pnpm lib score --facts-from <dir>` reads spike-kit `results/summary.json` so measured FPS and bundle numbers populate `facts` without retyping.

## Cross-project suggestions

- **app-shell**: Embedded OSS product kit: SSO from Better Auth to an embedded service, iframe or API embed slot, theming hand-off and tenant mapping. PAP-352 writes embed contracts for every `embed` verdict (Chatwoot, Listmonk likely); no project owns the runtime that honours them.
- **quality**: PAP-80 emits `security.json` advisories per direct dependency and a CycloneDX SBOM path the registry health page can read. r4/libraries/dependency-health-page and the census join on package name and version.
- **agents**: PAP-105 `page-from-spec` skill lists the usage notes for the libraries a spec's components depend on. r4/libraries/library-usage-notes only helps if sessions read them before coding.
- **pm-linear**: PAP-306 weekly re-audit reads `pnpm lib health --json`, guardrail waiver counts and expiring patches. Three libraries issues produce machine-readable health; the re-audit is where drift becomes issues.
- **module-system**: PAP-442 swap playbook consumes `swapImpact` and named-import counts from the library census for library-level swaps. Swapping a library follows the same seven steps as swapping a module; the census gives step 1 its evidence.
