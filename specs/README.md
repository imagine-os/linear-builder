# Issue specs

One file per canonical issue of Linear team PAP (duplicates skipped). Frontmatter carries the Linear identifier, project, phase, type, priority, state, relations and URL; the body is the issue description.

Linear is the system of record: the 206 round-1 issues use the canonical spec JSON in `plan/specs/` as their body, the round-2 issues use the 2026-09-17T06:03Z snapshot of their Linear description. Round-2 rewrites and fixes FIX-1..FIX-8 changed live text after that; see `plan/round2/changes/`.

Files: 268. Ready for Claude at snapshot time: 25.


## Universal App Shell & Repo Template (`app-shell`, 30)

| Issue | Title | Phase | Type | State |
|---|---|---|---|---|
| [PAP-5](app-shell/pap-5-my-issue-is-that-the-startup-procedure-for-creating-new-apps.md) | My issue is that the startup procedure for creating new apps on the fly. Is inefficient. How quickly do we get from blank screen down the layers of abstraction to the electrons flowing through the circuits??? |  |  | Backlog |
| [PAP-13](app-shell/monorepo-scaffold.md) | Scaffold paperos-template monorepo with pnpm, Turborepo, strict TypeScript and a Vite React 19 web app | P0 | Build | Ready for Claude |
| [PAP-14](app-shell/device-matrix-research.md) | Research and document the target device matrix (phone, tablet, laptop, desktop, TV/kiosk, foldable) with breakpoints and test devices | P0 | Research | Ready for Claude |
| [PAP-15](app-shell/gh-pages-demo.md) | Set up GitHub Pages demo deploy for every app with per-PR preview URLs | P0 | Infra | Backlog |
| [PAP-16](app-shell/router-layouts.md) | Implement file-based router with layout slots (nav, sidebar, inspector, command bar) driven by page specs | P0 | Build | Backlog |
| [PAP-17](app-shell/env-config.md) | Define typed environment and config layer with per-target secret storage (web, desktop keychain, mobile secure storage) | P0 | Build | Backlog |
| [PAP-18](app-shell/pwa.md) | Ship installable PWA manifest, service worker and offline app shell | P0 | Build | Backlog |
| [PAP-19](app-shell/tauri-desktop.md) | Add Tauri 2 desktop target for Linux, macOS and Windows sharing the web bundle | P0 | Build | Backlog |
| [PAP-20](app-shell/tauri-mobile.md) | Add Tauri 2 mobile targets (iOS, Android) with platform capability shims | P1 | Build | Backlog |
| [PAP-21](app-shell/breakpoints-windows.md) | Build responsive breakpoint matrix and multi-monitor window manager that detaches panels into OS windows | P1 | Build | Backlog |
| [PAP-22](app-shell/create-cli.md) | Write `paperos create <app>` CLI that clones the template into an imagine-os repo and wires Forgejo mirror, CI, Pages and a Linear project | P1 | Build | Backlog |
| [PAP-23](app-shell/linux-kiosk.md) | Support Linux kiosk and parallel-browser mode launching synced windows across displays from one CLI flag | P2 | Build | Backlog |
| [PAP-24](app-shell/template-docs.md) | Write the repo template guide: folder conventions, how an agent adds a page, how to ship each target | P1 | Docs | Backlog |
| [PAP-25](app-shell/vps-coolify-bootstrap.md) | Provision the Hetzner VPS with Coolify, Caddy, DNS for the PaperOS domain, object storage, sops keys and the paperos-infra repo | P0 | Infra | Ready for Claude |
| [PAP-26](app-shell/app-deploy-pipeline.md) | Build the app deploy pipeline: Docker images for apps/web and apps/api, staging on merge to main, production on tag, per-PR previews and rollback via Coolify | P0 | Infra | Backlog |
| [PAP-27](app-shell/i18n-l10n.md) | Add internationalisation and localisation: ICU message catalogs, locale negotiation, Intl formatting helpers, RTL layout flip, pseudo-locale testing and an agent translation skill | P1 | Build | Backlog |
| [PAP-28](app-shell/feature-modules.md) | Make every platform capability a removable module: module manifests, `modules:` in app.spec.yaml, `paperos create --without`, per-tenant module toggles and dead-code checks | P1 | Build | Backlog |
| [PAP-29](app-shell/new-app-drill.md) | Run the blank-screen-to-running-app drill: time `paperos create` through first spec'd page, deploy and desktop build; record it; answer PAP-5 with numbers | P2 | Review | Backlog |
| [PAP-255](app-shell/pap-255-tauri-desktop-scaffold-capabilities-and-plugins-apps-desktop.md) | Tauri desktop scaffold, capabilities and plugins (apps/desktop, menu, tray, dev scripts) | P0 | Build | Backlog |
| [PAP-256](app-shell/pap-256-desktop-ci-installers-for-linux-macos-and-windows-via-tauri.md) | Desktop CI installers for Linux, macOS and Windows via tauri-action with draft release | P0 | Infra | Backlog |
| [PAP-257](app-shell/pap-257-desktop-updater-single-instance-guard-and-paperos-deep-links.md) | Desktop updater, single-instance guard and paperos:// deep links | P0 | Build | Backlog |
| [PAP-258](app-shell/pap-258-tauri-mobile-project-init-and-ci-builds-android-debug-apk-io.md) | Tauri mobile project init and CI builds (Android debug APK, iOS simulator app) | P1 | Build | Backlog |
| [PAP-259](app-shell/pap-259-native-capabilities-shim-packages-core-native-with-web-fallb.md) | Native capabilities shim (packages/core/native) with web fallbacks | P1 | Build | Backlog |
| [PAP-260](app-shell/pap-260-mobile-plugin-wiring-safe-areas-and-device-proofs-camera-hap.md) | Mobile plugin wiring, safe areas and device proofs (camera, haptics, biometrics, secure storage, share) | P1 | Build | Backlog |
| [PAP-261](app-shell/pap-261-container-query-breakpoints-and-layout-hooks-from-the-device.md) | Container-query breakpoints and layout hooks from the device matrix | P1 | Build | Backlog |
| [PAP-262](app-shell/pap-262-tauri-windowmanager-detach-dock-list-displays-and-topology-h.md) | Tauri WindowManager: detach, dock, list_displays and topology-hash persistence | P1 | Build | Backlog |
| [PAP-263](app-shell/pap-263-web-pop-out-fallback-panel-header-affordances-and-windows-do.md) | Web pop-out fallback, panel header affordances and windows documentation | P1 | Build | Backlog |
| [PAP-264](app-shell/pap-264-module-manifest-contract-and-registry-packages-core-modules.md) | Module manifest contract and registry (packages/core/modules) | P1 | Build | Backlog |
| [PAP-265](app-shell/pap-265-module-integration-route-tree-spec-validator-permissions-job.md) | Module integration: route tree, spec validator, permissions, jobs and per-module migrations | P1 | Build | Backlog |
| [PAP-266](app-shell/pap-266-paperos-create-without-tenant-module-toggles-and-the-ci-remo.md) | `paperos create --without`, tenant module toggles and the CI removal matrix | P1 | Build | Backlog |

## Data Layer & Database (`data-layer`, 21)

| Issue | Title | Phase | Type | State |
|---|---|---|---|---|
| [PAP-30](data-layer/postgres-provision.md) | Provision Postgres 17 on the self-hosted VPS with automated backups and point-in-time recovery | P0 | Infra | Backlog |
| [PAP-31](data-layer/sync-research.md) | Evaluate Zero, ElectricSQL, PowerSync and Replicache for local-first sync and write an ADR | P0 | Research | Ready for Claude |
| [PAP-32](data-layer/drizzle-schema.md) | Set up Drizzle ORM schema-as-code with migration workflow and seed scripts | P0 | Build | Backlog |
| [PAP-33](data-layer/core-entities.md) | Model core platform entities: tenant, workspace, user, membership, role, audit_event, file | P0 | Spec | Backlog |
| [PAP-34](data-layer/rls-tenancy.md) | Implement Postgres row-level security policies for multi-tenant isolation with a cross-tenant test harness | P0 | Build | Backlog |
| [PAP-35](data-layer/api-layer.md) | Expose a typed API via oRPC with Zod schemas generated from Drizzle | P0 | Build | Backlog |
| [PAP-36](data-layer/local-first-sync.md) | Integrate PGlite and ElectricSQL shapes for local-first reads with an offline write queue | P1 | Build | Backlog |
| [PAP-37](data-layer/file-storage.md) | Add S3-compatible object storage (MinIO) with signed uploads and image variants | P1 | Build | Backlog |
| [PAP-38](data-layer/audit-log.md) | Build append-only audit log with actor (human or agent), diff and reason fields | P1 | Build | Backlog |
| [PAP-39](data-layer/search.md) | Add full-text and vector search (tsvector + pgvector) over any entity through a search registry | P1 | Build | Backlog |
| [PAP-40](data-layer/observability.md) | Wire OpenTelemetry tracing, slow-query logging and Grafana dashboards for API and sync | P2 | Infra | Backlog |
| [PAP-41](data-layer/data-dictionary.md) | Generate a living data dictionary from the Drizzle schema into the docs system | P2 | Docs | Backlog |
| [PAP-42](data-layer/local-dev-stack.md) | Ship the local dev stack: docker compose with Postgres 17, MinIO, Mailpit and Hocuspocus, per-worktree databases and a SessionStart hook so parallel Claude sessions never share state | P0 | Infra | Backlog |
| [PAP-43](data-layer/jobs-queue.md) | Build the background jobs and scheduler package (pg-boss) with retries, idempotency keys, cron, dead-letter queue and an admin view | P1 | Build | Backlog |
| [PAP-267](data-layer/pap-267-api-server-middleware-chain-and-error-mapping-apps-api-on-ho.md) | API server, middleware chain and error mapping (apps/api on Hono 4) | P0 | Build | Backlog |
| [PAP-268](data-layer/pap-268-api-contract-package-core-routers-and-typed-client-with-call.md) | API contract package, core routers and typed client with callAs test utility | P0 | Build | Backlog |
| [PAP-269](data-layer/pap-269-openapi-docs-health-endpoints-and-staging-deploy-of-apps-api.md) | OpenAPI docs, health endpoints and staging deploy of apps/api | P0 | Infra | Backlog |
| [PAP-270](data-layer/pap-270-electric-service-deployment-and-tenant-scoped-shape-proxy-ap.md) | Electric service deployment and tenant-scoped shape proxy (/api/sync/shape) | P1 | Build | Backlog |
| [PAP-271](data-layer/pap-271-pglite-client-schema-generation-and-read-hooks-useshape-usel.md) | PGlite client, schema generation and read hooks (useShape, useLiveQuery) | P1 | Build | Backlog |
| [PAP-272](data-layer/pap-272-offline-write-outbox-replay-with-backoff-leader-election-and.md) | Offline write outbox, replay with backoff, leader election and SyncIndicator | P1 | Build | Backlog |
| [PAP-279](data-layer/gap-data-layer-filter-grammar.md) | Specify the shared filter and condition grammar (`packages/core/filter`): one Zod FilterTree with SQL and in-memory evaluators | P0 | Spec | Ready for Claude |

## Version Control & Forge Independence (`forge`, 17)

| Issue | Title | Phase | Type | State |
|---|---|---|---|---|
| [PAP-44](forge/vcs-decision-adr.md) | Write ADR: keep Git as the format, self-host Forgejo, mirror GitHub, defer any custom VCS | P0 | Spec | Ready for Claude |
| [PAP-45](forge/forgejo-deploy.md) | Deploy Forgejo on the VPS behind Caddy with SSO from Better Auth and nightly backups | P0 | Infra | Backlog |
| [PAP-46](forge/branch-policy.md) | Define branch protection, conventional commits and worktree-per-issue conventions for parallel agents | P0 | Spec | Ready for Claude |
| [PAP-47](forge/mirror.md) | Configure bidirectional push mirroring between Forgejo and the GitHub org imagine-os for all repos | P0 | Infra | Backlog |
| [PAP-48](forge/bot-accounts.md) | Create scoped bot accounts and deploy keys for each agent character on both forges | P0 | Infra | Backlog |
| [PAP-49](forge/pr-templates.md) | Author PR template linking Linear issue, page spec, screenshots and the review-gate checklist | P0 | Docs | Backlog |
| [PAP-50](forge/actions-runner.md) | Run Forgejo Actions runners so CI works even when GitHub is unavailable | P1 | Infra | Backlog |
| [PAP-51](forge/repo-bootstrap.md) | Script `forge bootstrap <repo>` to configure imagine-os repos with mirrors, secrets, labels and webhooks | P1 | Build | Backlog |
| [PAP-52](forge/release-tags.md) | Automate semantic release tags and changelog generation on merge to main | P1 | Build | Backlog |
| [PAP-53](forge/dr-drill.md) | Run a disaster-recovery drill rebuilding all repos and CI from Forgejo backups with GitHub offline | P2 | Review | Backlog |
| [PAP-54](forge/in-app-git.md) | Expose repo browsing, diffs and commit history inside PaperOS via the Forgejo API | P2 | Build | Backlog |
| [PAP-273](forge/pap-273-forgejo-compose-stack-behind-caddy-with-hardened-app-ini-acc.md) | Forgejo compose stack behind Caddy with hardened app.ini, accounts and org | P0 | Infra | Backlog |
| [PAP-274](forge/pap-274-forgejo-backups-with-restic-and-a-timed-restore-drill-into-a.md) | Forgejo backups with restic and a timed restore drill into a scratch stack | P0 | Infra | Backlog |
| [PAP-275](forge/pap-275-oidc-auth-source-preparation-upgrade-procedure-and-forgejo-r.md) | OIDC auth source preparation, upgrade procedure and Forgejo runbook | P0 | Docs | Backlog |
| [PAP-276](forge/pap-276-forge-client-orpc-forge-procedures-and-forge-read-permission.md) | Forge client, oRPC forge.* procedures and forge.read permission checks | P2 | Build | Backlog |
| [PAP-277](forge/pap-277-repo-list-file-tree-file-view-and-commit-list-pages-with-spe.md) | Repo list, file tree, file view and commit-list pages with specs | P2 | Build | Backlog |
| [PAP-278](forge/pap-278-commit-diff-view-pull-request-pages-and-linear-trailer-links.md) | Commit diff view, pull request pages and Linear trailer links | P2 | Build | Backlog |

## Identity, Roles & Audiences (`identity`, 25)

| Issue | Title | Phase | Type | State |
|---|---|---|---|---|
| [PAP-55](identity/audience-model.md) | Specify the audience model: customer tiers, staff roles, partners, admins, agents and composable segments in between | P0 | Spec | Ready for Claude |
| [PAP-56](identity/auth-research.md) | Compare Better Auth, Lucia, Clerk and Auth.js for self-hosting, organizations and passkeys; write ADR | P0 | Research | Ready for Claude |
| [PAP-57](identity/better-auth.md) | Install Better Auth with passkeys, magic link, Google/GitHub OAuth and sessions for web and Tauri | P0 | Build | Backlog |
| [PAP-58](identity/org-tenancy.md) | Implement organizations, workspaces, invitations and tenant switching | P0 | Build | Backlog |
| [PAP-59](identity/rbac-abac.md) | Build permission engine combining role-based grants with attribute policies declared in page specs | P0 | Build | Backlog |
| [PAP-60](identity/agent-principals.md) | Make agents first-class principals with scoped API keys, rate limits and visible attribution | P1 | Build | Backlog |
| [PAP-61](identity/impersonation.md) | Add staff 'view as customer' impersonation with full audit trail | P1 | Build | Backlog |
| [PAP-62](identity/customer-portal-shell.md) | Ship the customer-facing portal shell (login, profile, billing entry) separate from the staff console | P1 | Build | Backlog |
| [PAP-63](identity/staff-console-shell.md) | Ship the staff console shell with tenant switcher, audience filters and admin navigation | P1 | Build | Backlog |
| [PAP-64](identity/permission-tests.md) | Generate permission matrix tests from page specs covering who can see and do what on every page | P1 | Review | Backlog |
| [PAP-65](identity/sso-scim.md) | Add SAML/OIDC SSO and SCIM provisioning for enterprise tenants | P2 | Build | Backlog |
| [PAP-219](identity/threat-model.md) | Write the security threat model and hardening baseline: STRIDE per trust boundary, CSP and security headers, CSRF, secret rotation runbook, incident response playbook | P0 | Spec | Ready for Claude |
| [PAP-220](identity/session-device-management.md) | Build session and device management: list and revoke sessions, TOTP fallback for passkeys, account recovery codes | P1 | Build | Backlog |
| [PAP-221](identity/privacy-dsar.md) | Build privacy tooling: per-user data export and erasure (DSAR), consent records, privacy/terms/cookie pages in the portal | P2 | Build | Backlog |
| [PAP-222](identity/tenant-api-keys-webhooks.md) | Build tenant API keys and outbound webhooks for developers: scoped keys, per-key limits, signed webhook deliveries with retries, developer settings page and generated TypeScript SDK | P2 | Build | Backlog |
| [PAP-223](identity/better-auth-server-schema-session.md) | Better Auth server, Drizzle schema merge and session helpers | P0 | Build | Backlog |
| [PAP-224](identity/better-auth-ui-pages-email.md) | Auth UI pages and magic-link email delivery | P0 | Build | Backlog |
| [PAP-225](identity/better-auth-tauri-session.md) | Tauri deep-link and secure-token session flow | P0 | Build | Backlog |
| [PAP-226](identity/better-auth-oidc-provider.md) | OIDC provider endpoints for Forgejo SSO | P0 | Build | Backlog |
| [PAP-227](identity/rbac-abac-model-evaluator.md) | Policy model, evaluator and explain mode | P0 | Build | Backlog |
| [PAP-228](identity/rbac-abac-sql-compiler-rls.md) | SQL predicate compiler and RLS helpers | P0 | Build | Backlog |
| [PAP-229](identity/rbac-abac-adapter-middleware-hook.md) | Spec adapter, oRPC middleware and useCan hook | P0 | Build | Backlog |
| [PAP-230](identity/sso-scim-sso-plugin-domains.md) | SSO plugin: OIDC and SAML per tenant with domain verification | P2 | Build | Backlog |
| [PAP-231](identity/sso-scim-scim-server.md) | SCIM 2.0 server for Users and Groups | P2 | Build | Backlog |
| [PAP-232](identity/sso-scim-console-enforcement-docs.md) | Console SSO and SCIM settings pages, enforcement and enterprise docs | P2 | Build | Backlog |

## Design System (`design-system`, 18)

| Issue | Title | Phase | Type | State |
|---|---|---|---|---|
| [PAP-66](design-system/tokens.md) | Define design tokens (color, type, space, radius, motion, elevation) in DTCG JSON compiled to CSS variables | P0 | Build | Ready for Claude |
| [PAP-67](design-system/primitives.md) | Adopt Base UI/Radix primitives with Tailwind v4 and build 20 core components (Button, Input, Select, Dialog, Menu, Tabs, Toast, Tooltip, Popover...) | P0 | Build | Backlog |
| [PAP-68](design-system/icons-illustrations.md) | Choose the icon set (Lucide or Phosphor) and illustration style; build a tree-shaken Icon component | P0 | Build | Backlog |
| [PAP-69](design-system/storybook.md) | Set up Storybook with a11y, viewport and interaction-test addons deployed to GitHub Pages | P0 | Infra | Backlog |
| [PAP-70](design-system/layout-components.md) | Build layout components: AppFrame, SplitPane, Inspector, CommandBar, ResponsiveGrid | P1 | Build | Backlog |
| [PAP-71](design-system/data-display.md) | Build data display components: cell renderers, Badge, AvatarStack, Timeline, EmptyState, Skeleton | P1 | Build | Backlog |
| [PAP-72](design-system/motion.md) | Define the motion system (durations, easings, reduced-motion) and shared transition components | P1 | Build | Backlog |
| [PAP-73](design-system/a11y-audit.md) | Run axe and manual screen-reader audit on every component and fix to WCAG 2.2 AA | P1 | Review | Backlog |
| [PAP-74](design-system/component-spec-mapping.md) | Map every component to a spec-builder component ID with props schema so page specs reference real components | P1 | Spec | Backlog |
| [PAP-75](design-system/theming.md) | Implement light, dark and high-contrast themes plus per-tenant brand theming with runtime token override | P1 | Build | Backlog |
| [PAP-76](design-system/guidelines-docs.md) | Write design system guidelines (voice, density, spacing, when to use what) into the docs system | P2 | Docs | Backlog |
| [PAP-77](design-system/figma-sync.md) | Export tokens to Figma variables and document the round-trip, or record the decision to skip Figma | P2 | Research | Backlog |
| [PAP-233](design-system/date-pickers-forms.md) | Build date, time, date-range and calendar pickers plus form-state adapters (react-hook-form Field, arrays, async validation) | P1 | Build | Backlog |
| [PAP-234](design-system/state-components.md) | Build the state components codegen emits: ErrorState, DeniedState, OfflineBanner, IntegrationUnavailable, LoadingPage as spec-mapped `ui.*` components | P1 | Build | Backlog |
| [PAP-235](design-system/email-pdf-theme.md) | Build the email and PDF rendering theme: `brandingToInlineCss`, print stylesheet and a template kit shared by invoices, receipts, digests and the ACR export | P2 | Build | Backlog |
| [PAP-236](design-system/primitives-infra-form-controls.md) | Component infrastructure and form controls | P0 | Build | Backlog |
| [PAP-237](design-system/primitives-overlays.md) | Overlay components: Dialog, AlertDialog, Popover, Tooltip, Menu, Toast | P0 | Build | Backlog |
| [PAP-238](design-system/primitives-selection-navigation.md) | Selection and navigation components: Select, Combobox, Tabs, Avatar, Separator | P0 | Build | Backlog |

## Quality Pipeline (`quality`, 29)

| Issue | Title | Phase | Type | State |
|---|---|---|---|---|
| [PAP-78](quality/ci-gate1.md) | Set up CI gate 1: typecheck, Biome lint, Vitest unit tests and web build on every PR | P0 | Infra | Backlog |
| [PAP-79](quality/review-rubrics.md) | Write review rubrics and a severity taxonomy shared by all reviewer agents and humans | P0 | Spec | Ready for Claude |
| [PAP-80](quality/security-scans.md) | Add dependency audit, secret scanning, Semgrep SAST and container scanning to CI | P0 | Infra | Backlog |
| [PAP-81](quality/review-agents.md) | Build gate 2: three Claude reviewer agents (correctness, security, spec-conformance) posting structured PR reviews | P0 | Build | Backlog |
| [PAP-82](quality/playwright-matrix.md) | Build gate 3: Playwright screenshot suite across the 7-width breakpoint matrix, all themes and key pages with baseline diffs | P0 | Build | Backlog |
| [PAP-83](quality/video-replays.md) | Record video replays of critical flows per PR at each responsive size and attach them to the PR | P1 | Build | Backlog |
| [PAP-84](quality/screenshot-annotation.md) | Have a vision agent inspect screenshots for overflow, misalignment, contrast and truncation and post annotated findings | P1 | Build | Backlog |
| [PAP-85](quality/edge-case-hunter.md) | Build gate 4: edge-case hunter agent generating adversarial inputs, empty/huge/unicode states, network failure and slow-device scenarios from page specs | P1 | Build | Backlog |
| [PAP-86](quality/e2e-flows.md) | Write end-to-end flow tests for auth, tenant switch, CRUD and realtime presence | P1 | Build | Backlog |
| [PAP-87](quality/perf-budgets.md) | Enforce performance budgets (LCP, INP, bundle size) with Lighthouse CI | P1 | Infra | Backlog |
| [PAP-88](quality/release-train.md) | Define the release train: nightly staging deploy, weekly release candidate to Needs Justin with consolidated review report | P1 | Spec | Backlog |
| [PAP-89](quality/review-report.md) | Generate a one-page human review digest per release candidate: what changed, risks, screenshots, open questions | P1 | Build | Backlog |
| [PAP-90](quality/flake-quarantine.md) | Build flaky-test detection and quarantine so agents are not blocked by nondeterminism | P2 | Build | Backlog |
| [PAP-239](quality/gate-artifact-contract.md) | Specify the gate artifact contract: one schema package for gate1.json, security.json, visual.json, videos.json, vision.json, edgecases.json, finding IDs and artifact paths | P0 | Spec | Backlog |
| [PAP-240](quality/test-mode-seed.md) | Build test-mode seed and reset endpoints (`/__test/seed`, `/__test/reset`) with deterministic fixtures per audience, before Gate 3 | P0 | Build | Backlog |
| [PAP-241](quality/gate2-calibration.md) | Run Gate 2 calibration and false-negative tracking: weekly manual spot check of five verdicts, precision and recall trend, reviewer prompt tuning loop | P1 | Review | Backlog |
| [PAP-242](quality/api-perf-budgets.md) | Enforce API and database performance budgets: k6 smoke per release candidate, p95 per procedure, slow-query gate, `apps/api` image size | P1 | Infra | Backlog |
| [PAP-243](quality/review-agents-harness.md) | Review harness: SDK runner, input assembly, finding validation and posting | P0 | Build | Backlog |
| [PAP-244](quality/review-agents-correctness-spec.md) | Correctness and spec-conformance reviewer definitions | P0 | Build | Backlog |
| [PAP-245](quality/review-agents-security.md) | Security reviewer definition and security.json ingestion | P0 | Build | Backlog |
| [PAP-246](quality/playwright-matrix-projects-fixtures-stories.md) | Playwright project matrix, deterministic fixtures and Storybook story capture | P0 | Build | Backlog |
| [PAP-247](quality/playwright-matrix-pages-auth-baselines.md) | Page capture with authenticated audiences and baseline update workflow | P0 | Build | Backlog |
| [PAP-248](quality/playwright-matrix-reporter-sharding.md) | Contact-sheet reporter, 4-way sharding and the visual.json artifact | P0 | Build | Backlog |
| [PAP-249](quality/edge-case-hunter-planner.md) | Scenario planner from specs with fixture catalogue | P1 | Build | Backlog |
| [PAP-250](quality/edge-case-hunter-executor-oracles.md) | Playwright executor and generic oracles | P1 | Build | Backlog |
| [PAP-251](quality/edge-case-hunter-findings-repros-nightly.md) | Findings, generated repro tests and nightly library run | P1 | Build | Backlog |
| [PAP-252](quality/release-train-policy-environments.md) | Release train policy document and environments config | P1 | Spec | Backlog |
| [PAP-253](quality/release-train-nightly-staging.md) | Nightly staging workflow with full gate run | P1 | Build | Backlog |
| [PAP-254](quality/release-train-rc-certify-approve.md) | Release candidate cut, certification and Justin approval flow | P1 | Build | Backlog |

## Project Management & Claude Pipeline (`pm-linear`, 12)

| Issue | Title | Phase | Type | State |
|---|---|---|---|---|
| [PAP-91](pm-linear/configure-workspace.md) | Add pipeline states (Ready for Claude, In Review, Needs Justin), label groups and project templates to Linear team PAP | P0 | Infra | Needs Justin |
| [PAP-92](pm-linear/session-playbook.md) | Write the session playbook: how a Claude session picks up an issue, what it must read, how it reports and ends | P0 | Docs | Ready for Claude |
| [PAP-93](pm-linear/issue-contract.md) | Define the issue contract (spec link, acceptance criteria, surfaces, definition of done) enforced by a Linear webhook validator | P0 | Spec | Backlog |
| [PAP-94](pm-linear/justin-queue.md) | Design the Needs Justin queue: batched decisions, one-click approve/reject comments, max five open items rule | P0 | Spec | Backlog |
| [PAP-95](pm-linear/pap5-decompose.md) | Decompose PAP-5 (startup procedure inefficiency) into this master plan's projects and close it with a summary comment | P0 | Docs | Backlog |
| [PAP-96](pm-linear/orchestrator.md) | Build the orchestrator that polls Ready for Claude, spawns one Claude Code session per issue in a git worktree and moves states | P0 | Build | Backlog |
| [PAP-97](pm-linear/webhooks.md) | Set up Linear webhooks into the orchestrator and PR status back to Linear as comments with screenshots and review verdicts | P0 | Build | Backlog |
| [PAP-98](pm-linear/credit-metering.md) | Track Claude credit spend per issue and project and post a daily burn report to Linear | P0 | Build | Backlog |
| [PAP-99](pm-linear/concurrency.md) | Implement concurrency controls: max parallel sessions, file-lock hints and dependency-aware scheduling from dependsOn | P1 | Build | Backlog |
| [PAP-100](pm-linear/pm-data-model.md) | Model PM entities in PaperOS (project, issue, cycle, milestone, comment, label) mirroring Linear's schema | P1 | Spec | Backlog |
| [PAP-101](pm-linear/linear-sync.md) | Build bidirectional Linear sync (GraphQL + webhooks) with conflict rule: Linear wins until cutover | P2 | Build | Backlog |
| [PAP-102](pm-linear/board-views.md) | Render PM board, list and timeline views using the tables/views engine | P2 | Build | Backlog |

## Agent Characters & Orgs (`agents`, 11)

| Issue | Title | Phase | Type | State |
|---|---|---|---|---|
| [PAP-103](agents/character-schema.md) | Define the character schema: name, role, reportsTo, tools, MCP servers, access scopes, plugins, skills, memory, escalation rules | P0 | Spec | Ready for Claude |
| [PAP-104](agents/roster-v1.md) | Write the nine lead characters and their sub-characters as .claude/agents definitions with system prompts | P0 | Build | Backlog |
| [PAP-105](agents/skills-library.md) | Build the shared skills library (page-from-spec, review-pr, screenshot-audit, write-adr, linear-update) as .claude/skills | P0 | Build | Backlog |
| [PAP-106](agents/tool-scopes.md) | Implement per-character MCP allowlists and permission modes and verify least privilege with an automated test | P0 | Build | Backlog |
| [PAP-107](agents/prompt-logging-hook.md) | Hook every session's prompts, responses and tool calls into the prompt-log store | P0 | Build | Backlog |
| [PAP-108](agents/handoffs.md) | Design the handoff protocol between characters: artifact contract, Linear comment format, escalation to Needs Justin | P1 | Spec | Backlog |
| [PAP-109](agents/memory.md) | Give characters persistent memory (project notes, decisions, gotchas) stored in the docs system and loaded at session start | P1 | Build | Backlog |
| [PAP-110](agents/eval-harness.md) | Create an eval harness with golden tasks per character, scored nightly, regressions flagged in Linear | P1 | Review | Backlog |
| [PAP-111](agents/cost-controls.md) | Add per-character budgets, max-turn limits and a kill switch | P1 | Build | Backlog |
| [PAP-112](agents/character-docs.md) | Publish the character handbook: who does what, how to summon them, what they may not do | P1 | Docs | Backlog |
| [PAP-113](agents/org-chart-ui.md) | Build the agent org chart UI showing characters, sub-agents, current tasks, tools and access | P2 | Build | Backlog |

## Spec Builder (`spec-builder`, 13)

| Issue | Title | Phase | Type | State |
|---|---|---|---|---|
| [PAP-114](spec-builder/schema.md) | Define the page.spec.yaml schema: purpose, logic, access, data, integrations, layout, components, states, events, edge cases | P0 | Spec | Ready for Claude |
| [PAP-115](spec-builder/validator.md) | Build the spec validator CLI and CI check that fails PRs whose pages lack or violate specs | P0 | Build | Backlog |
| [PAP-116](spec-builder/access-section.md) | Specify the access section format that compiles to permission-engine policies | P0 | Spec | Backlog |
| [PAP-117](spec-builder/app-level-spec.md) | Define app.spec.yaml (audiences, navigation, entities, integrations) that page specs inherit from | P1 | Spec | Backlog |
| [PAP-118](spec-builder/spec-authoring-skill.md) | Write the agent skill: interview -> draft page spec -> validate -> open Linear issue | P1 | Build | Backlog |
| [PAP-119](spec-builder/data-section.md) | Specify the data section (entities, queries, mutations, sync mode) and generate typed hooks from it | P1 | Build | Backlog |
| [PAP-120](spec-builder/layout-codegen.md) | Generate page scaffolds (layout, component tree, loading/empty/error states) from specs | P1 | Build | Backlog |
| [PAP-121](spec-builder/integrations-section.md) | Specify the integrations section (Stripe, Linear, Notion, Drive, Webflow, Miro, Gamma) backed by a connector registry | P1 | Spec | Backlog |
| [PAP-122](spec-builder/conformance-tests.md) | Generate conformance tests from specs (access matrix, required components, states) into CI gate 1 | P1 | Build | Backlog |
| [PAP-123](spec-builder/spec-to-canvas.md) | Emit the UX-flow graph (pages, transitions, roles) from specs for the canvas view | P1 | Build | Backlog |
| [PAP-124](spec-builder/spec-editor-ui.md) | Build the spec editor UI with form and YAML views and live preview | P2 | Build | Backlog |
| [PAP-125](spec-builder/spec-docs.md) | Document the spec builder with three fully specified example pages (customer list, staff dashboard, agent console) | P1 | Docs | Backlog |
| [PAP-126](spec-builder/business-profile.md) | Define the business profile section of app.spec.yaml: industry, audiences, terminology map, locale, currency and tax regime, enabled modules; codegen, templates and the migration agent read it | P2 | Spec | Backlog |

## In-App Collaboration & Knowledge (`collab`, 12)

| Issue | Title | Phase | Type | State |
|---|---|---|---|---|
| [PAP-127](collab/collab-research.md) | Evaluate tldraw vs React Flow for the canvas and Tiptap vs BlockNote for docs; write ADR | P0 | Research | Ready for Claude |
| [PAP-128](collab/docs-engine.md) | Build the docs engine: MDX docs stored in the repo, rendered in-app, searchable and versioned with git | P0 | Build | Backlog |
| [PAP-129](collab/prompt-log-store.md) | Create the prompt/response log store (session, character, issue, tokens, cost, tool calls) with redaction | P0 | Build | Backlog |
| [PAP-130](collab/decision-log.md) | Add an ADR/decision log with status, alternatives and links to issues | P0 | Build | Backlog |
| [PAP-131](collab/comments.md) | Implement in-app comments anchored to any entity, page element or doc block with mentions and resolve | P1 | Build | Backlog |
| [PAP-132](collab/canvas-view.md) | Build the canvas view (tldraw or React Flow) showing the UX flow of the whole app, generated from specs and editable | P1 | Build | Backlog |
| [PAP-133](collab/changelog.md) | Auto-generate changelogs from conventional commits and PR summaries, rendered per app and per tenant | P1 | Build | Backlog |
| [PAP-134](collab/rules-skills-registry.md) | Surface rules (CLAUDE.md, policies) and skills as browsable, editable objects in-app with version history | P1 | Build | Backlog |
| [PAP-135](collab/prompt-log-ui.md) | Build the prompt log browser: filter by issue or character, replay a session, link to the PR | P1 | Build | Backlog |
| [PAP-136](collab/notifications.md) | Build a notification center (in-app, email, Slack) with per-audience preferences | P2 | Build | Backlog |
| [PAP-137](collab/screenshot-annotations.md) | Allow annotating screenshots and video frames with comments that create Linear issues | P2 | Build | Backlog |
| [PAP-138](collab/knowledge-search.md) | Unify search across docs, comments, specs, prompt logs and issues | P2 | Build | Backlog |

## Multiplayer & Realtime (`realtime`, 11)

| Issue | Title | Phase | Type | State |
|---|---|---|---|---|
| [PAP-139](realtime/realtime-research.md) | Benchmark Yjs vs Automerge vs Loro for document CRDT and write an ADR | P0 | Research | Ready for Claude |
| [PAP-140](realtime/yjs-server.md) | Deploy a Hocuspocus (Yjs) server with auth hook, Postgres persistence and room-per-document | P0 | Infra | Backlog |
| [PAP-141](realtime/presence.md) | Build the presence layer: cursors, avatars, selections and 'who is viewing' across pages | P1 | Build | Backlog |
| [PAP-142](realtime/collab-text.md) | Add collaborative rich text (Tiptap + Yjs) as the shared editor for docs and comments | P1 | Build | Backlog |
| [PAP-143](realtime/record-sync.md) | Stream record changes via Electric shapes to all connected clients and reconcile with local writes | P1 | Build | Backlog |
| [PAP-144](realtime/conflict-ux.md) | Design conflict and stale-data UX: merge banners, last-writer indicators, undo | P1 | Spec | Backlog |
| [PAP-145](realtime/multi-window-sync.md) | Sync state across multiple OS windows and tabs of the same user via BroadcastChannel and Yjs | P1 | Build | Backlog |
| [PAP-146](realtime/agent-presence.md) | Show agents as live participants (typing, editing, reviewing) with distinct visual identity | P2 | Build | Backlog |
| [PAP-147](realtime/load-test.md) | Load test 500 concurrent users per room and 10k rooms; tune persistence and scaling | P2 | Review | Backlog |
| [PAP-148](realtime/offline-queue.md) | Implement the offline write queue with retry, ordering and user-visible sync status | P2 | Build | Backlog |
| [PAP-149](realtime/followmode.md) | Add follow mode and shared cursor sessions for support and pair review | P2 | Build | Backlog |

## Multi-Input Control & Accessibility (`input`, 11)

| Issue | Title | Phase | Type | State |
|---|---|---|---|---|
| [PAP-150](input/input-abstraction.md) | Design a unified input event abstraction so components handle mouse, touch, pen and gamepad uniformly | P0 | Spec | Ready for Claude |
| [PAP-151](input/command-registry.md) | Build the global command registry with keyboard shortcuts, command palette and per-page scoping | P0 | Build | Backlog |
| [PAP-152](input/focus-management.md) | Implement robust focus management, roving tabindex and skip links across all layouts | P1 | Build | Backlog |
| [PAP-153](input/keymaps.md) | Support user-customizable keymaps with presets (default, Vim-style, Linear-like) synced per user | P1 | Build | Backlog |
| [PAP-154](input/touch-gestures.md) | Implement a touch gesture system (swipe, pinch, long-press) with haptics on mobile targets | P1 | Build | Backlog |
| [PAP-155](input/drag-drop.md) | Build accessible drag-and-drop (dnd-kit) for tables, kanban and canvas with a keyboard alternative | P1 | Build | Backlog |
| [PAP-156](input/screen-reader.md) | Test and fix the screen reader experience (NVDA, VoiceOver, TalkBack) for core flows | P1 | Review | Backlog |
| [PAP-157](input/pen.md) | Support pen and stylus input with pressure for canvas and annotation | P2 | Build | Backlog |
| [PAP-158](input/gamepad.md) | Add gamepad and TV-remote navigation for kiosk and TV modes with spatial focus | P2 | Build | Backlog |
| [PAP-159](input/voice.md) | Integrate voice commands and dictation (Web Speech with Whisper fallback) routed through the command registry | P2 | Build | Backlog |
| [PAP-160](input/a11y-statement.md) | Publish an accessibility statement and conformance report template per app | P2 | Docs | Backlog |

## Table & Views Engine (`tables`, 14)

| Issue | Title | Phase | Type | State |
|---|---|---|---|---|
| [PAP-161](tables/view-model-spec.md) | Specify the view model: data source, fields, filters, sorts, groups, aggregations, permissions and sharing as a superset of Airtable, Notion and ClickUp | P0 | Spec | Ready for Claude |
| [PAP-162](tables/feature-parity-audit.md) | Audit Airtable, Notion, ClickUp, Baserow and NocoDB view features into a parity checklist | P0 | Research | Ready for Claude |
| [PAP-163](tables/query-compiler.md) | Build the view query compiler from view model to SQL and Electric shapes with server-side pagination | P1 | Build | Backlog |
| [PAP-164](tables/field-types.md) | Implement field types: text, number, currency, date, select, multi-select, relation, lookup, rollup, formula, attachment, user, checkbox, rating, URL, email, phone | P1 | Build | Backlog |
| [PAP-165](tables/grid-view.md) | Build the virtualized grid view (TanStack Table) with inline edit, column resize/reorder, freeze and cell types | P1 | Build | Backlog |
| [PAP-166](tables/filter-sort-group-ui.md) | Build the filter builder (AND/OR groups), multi-sort and multi-level grouping UI with aggregates | P1 | Build | Backlog |
| [PAP-167](tables/kanban-view.md) | Build the kanban board view with swimlanes, WIP limits and drag-and-drop | P1 | Build | Backlog |
| [PAP-168](tables/calendar-timeline-gantt.md) | Build calendar, timeline and Gantt views with dependencies | P1 | Build | Backlog |
| [PAP-169](tables/gallery-list-form.md) | Build gallery, list and form views | P1 | Build | Backlog |
| [PAP-170](tables/map-chart-views.md) | Build map view and chart view (bar, line, pie, number) bound to view aggregations | P2 | Build | Backlog |
| [PAP-171](tables/formula-engine.md) | Build a formula engine compatible with common Airtable and Notion functions | P2 | Build | Backlog |
| [PAP-172](tables/view-sharing.md) | Add saved views, personal vs shared views, public embeds and per-audience defaults | P2 | Build | Backlog |
| [PAP-173](tables/dashboard-blocks.md) | Compose views into dashboard pages with drag-arranged blocks and cross-filters | P2 | Build | Backlog |
| [PAP-174](tables/automations.md) | Build table automations: triggers (record change, schedule, form, inbound webhook), filter-tree conditions and actions (update record, notify, outbound webhook, connector call, create Linear issue) with a run log | P2 | Build | Backlog |

## Business Core: Payments, Finance & Payroll (`business-core`, 12)

| Issue | Title | Phase | Type | State |
|---|---|---|---|---|
| [PAP-175](business-core/finance-data-model.md) | Specify the finance data model: customers, vendors, employees, accounts, transactions and periods across all business types | P1 | Spec | Backlog |
| [PAP-176](business-core/payroll-research.md) | Research payroll APIs (Check, Gusto Embedded, Deel, Rippling) for embeddability and pricing; write ADR | P1 | Research | Ready for Claude |
| [PAP-177](business-core/stripe-billing.md) | Integrate Stripe Billing: products, prices, subscriptions, customer portal and webhooks | P1 | Build | Backlog |
| [PAP-178](business-core/entitlements.md) | Map plans to feature entitlements enforced by the permission engine | P2 | Build | Backlog |
| [PAP-179](business-core/ledger.md) | Build a double-entry ledger (accounts, journal entries, periods) in Postgres with immutability guarantees | P2 | Build | Backlog |
| [PAP-180](business-core/invoicing.md) | Implement invoices, quotes and receipts with PDF generation and Stripe payment links | P2 | Build | Backlog |
| [PAP-181](business-core/stripe-connect.md) | Add Stripe Connect so tenants can accept payments and receive payouts | P2 | Build | Backlog |
| [PAP-182](business-core/tax-compliance.md) | Handle sales tax and VAT via Stripe Tax and store tax evidence | P2 | Build | Backlog |
| [PAP-183](business-core/finance-reports.md) | Generate P&L, balance sheet, cash flow and AR/AP aging as table views | P2 | Build | Backlog |
| [PAP-184](business-core/payroll-adapter.md) | Define the payroll provider interface and implement the first adapter (Check or Gusto Embedded) | P2 | Build | Backlog |
| [PAP-185](business-core/expense-capture.md) | Add expense capture with receipt OCR and ledger posting | P2 | Build | Backlog |
| [PAP-186](business-core/cash-dashboard.md) | Build the cash-flow dashboard (in, out, runway, upcoming payroll) as the first dashboard-blocks consumer | P2 | Build | Backlog |

## Growth: Marketing, Outreach & CRM (`growth`, 11)

| Issue | Title | Phase | Type | State |
|---|---|---|---|---|
| [PAP-187](growth/crm-model.md) | Model CRM entities: lead, contact, company, deal, pipeline stage, activity, segment | P1 | Spec | Backlog |
| [PAP-188](growth/growth-research.md) | Survey open-source CRM and marketing stacks (Twenty, Postiz, Listmonk, Dub) for reuse vs build; write ADR | P1 | Research | Ready for Claude |
| [PAP-189](growth/crm-views.md) | Build CRM pipeline (kanban), contact list and company views on the tables engine | P2 | Build | Backlog |
| [PAP-190](growth/social-scheduler.md) | Build a social media scheduler with adapters (X, LinkedIn, Instagram, TikTok, YouTube) and an approval queue | P2 | Build | Backlog |
| [PAP-191](growth/outreach-sequences.md) | Build email and SMS outreach sequences (Resend, Twilio) with warmup and reply detection | P2 | Build | Backlog |
| [PAP-192](growth/content-agent.md) | Create the content agent character that drafts posts and emails from changelogs and specs for human approval | P2 | Build | Backlog |
| [PAP-193](growth/landing-forms.md) | Publish landing pages via the Webflow API and capture forms into the CRM | P2 | Build | Backlog |
| [PAP-194](growth/attribution.md) | Track acquisition analytics (UTM, referral, funnel) with a privacy-first event pipeline | P2 | Build | Backlog |
| [PAP-195](growth/segments.md) | Build audience segments from CRM and product usage that feed campaigns and in-app targeting | P2 | Build | Backlog |
| [PAP-196](growth/referral-program.md) | Implement a referral and affiliate program with Stripe Connect payouts | P2 | Build | Backlog |
| [PAP-197](growth/support-inbox.md) | Build a shared support inbox (email and in-app chat) linked to CRM contacts | P2 | Build | Backlog |

## Migration & Import Tools (`migration`, 11)

| Issue | Title | Phase | Type | State |
|---|---|---|---|---|
| [PAP-198](migration/format-research.md) | Catalog export formats and API limits of Airtable, Notion, ClickUp, Monday, HubSpot and QuickBooks | P1 | Research | Ready for Claude |
| [PAP-199](migration/import-framework.md) | Build the import framework: source connector, schema-mapping UI, dry run, validation, rollback | P1 | Build | Backlog |
| [PAP-200](migration/csv-excel.md) | Import CSV, Excel and Google Sheets with type inference | P2 | Build | Backlog |
| [PAP-201](migration/id-mapping.md) | Persist external ID mappings for re-sync and incremental imports | P2 | Build | Backlog |
| [PAP-202](migration/airtable.md) | Import Airtable bases (tables, views, relations, attachments) | P2 | Build | Backlog |
| [PAP-203](migration/notion.md) | Import Notion databases and pages into tables and docs | P2 | Build | Backlog |
| [PAP-204](migration/clickup-linear.md) | Import ClickUp and Linear workspaces into the PM module | P2 | Build | Backlog |
| [PAP-205](migration/export.md) | Export everything (tables, docs, files, ledger) to open formats | P2 | Build | Backlog |
| [PAP-206](migration/stripe-quickbooks.md) | Import Stripe customers and subscriptions and QuickBooks/Xero charts of accounts into the ledger | P2 | Build | Backlog |
| [PAP-207](migration/business-templates.md) | Ship business-type templates (agency, retail, SaaS, clinic, restaurant) as importable seed packs | P2 | Build | Backlog |
| [PAP-208](migration/migration-agent.md) | Create the migration agent character that interviews users about current tools and runs the imports | P2 | Build | Backlog |

## Library Discovery & Integration (`libraries`, 10)

| Issue | Title | Phase | Type | State |
|---|---|---|---|---|
| [PAP-209](libraries/eval-rubric.md) | Define the library evaluation rubric (license, maintenance, bundle size, a11y, TS quality, agent-friendliness) and ADR template | P0 | Spec | Ready for Claude |
| [PAP-210](libraries/mcp-servers.md) | Catalog and configure MCP servers and connectors (Linear, GitHub, Stripe, Notion, Drive, Webflow, Miro, Gamma) for agents | P0 | Infra | Ready for Claude |
| [PAP-211](libraries/license-policy.md) | Set the license policy (allow MIT/Apache/BSD, review AGPL, block SSPL) enforced by a CI license check | P0 | Infra | Backlog |
| [PAP-212](libraries/ui-landscape.md) | Survey UI kits and headless libraries (Base UI, Radix, React Aria, shadcn, Ark) and recommend | P0 | Research | Backlog |
| [PAP-213](libraries/data-landscape.md) | Survey table, canvas, editor and chart libraries (TanStack, AG Grid, tldraw, Tiptap, ECharts, visx) and recommend | P0 | Research | Backlog |
| [PAP-214](libraries/backend-landscape.md) | Survey backend building blocks (Better Auth, Drizzle, Electric, Hocuspocus, Inngest, Resend) and recommend | P0 | Research | Backlog |
| [PAP-215](libraries/oss-products.md) | Evaluate whole OSS products to embed or fork (Twenty CRM, NocoDB, Baserow, Plane, Cal.com, Formbricks, Postiz) | P1 | Research | Backlog |
| [PAP-216](libraries/registry.md) | Build the library registry in the docs system: adopted, trialing, rejected with reasons and owners | P1 | Build | Backlog |
| [PAP-217](libraries/upgrade-bot.md) | Set up Renovate with grouped upgrades and agent-reviewed changelog summaries | P1 | Infra | Backlog |
| [PAP-218](libraries/scout-agent.md) | Create the Scout character routine: weekly scan for new libraries relevant to open issues | P2 | Build | Backlog |
