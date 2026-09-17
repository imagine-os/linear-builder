import os
"""Append a Contract section to the three project descriptions (content field)."""
import sys, json
sys.path.insert(0, os.environ.get("PAPEROS_PLAN_DIR", ".") + "/round2/agent1")
import r2
DRY = "--dry" in sys.argv
ch = r2.load_changes()
cur = json.load(open(r2.R2 + "/_proj_content_1.json"))

CONTRACTS = {
"identity": """

## Contract

**Provides**

* `@paperos/core/audience` (PAP-55): `Principal`, `TenantRole`, `Audience`, `Segment`, `matches()`, `BUILTIN_AUDIENCES` - the canonical actor type every other project imports.
* `@paperos/auth` (PAP-57, children PAP-223 to PAP-226): `requireSession()`, `useSession()`, `<SignInForm>`, routes `/api/auth/*`, bearer exchange for Tauri, OIDC provider for Forgejo.
* Tenancy (PAP-58): `withTenant` middleware setting `app.tenant_id`, `app.principal_id`, `app.role`, `app.attrs`; `useTenant()`, `TenantSwitcher`; events `tenant.created`, `membership.changed`.
* `@paperos/permissions` (PAP-59, children PAP-227 to PAP-229): `can()`, `explain()`, `toPredicate()`, `toRlsPolicy()`, `authorize()` middleware, `useCan()`, `accessToPolicies()`.
* Agent principals (PAP-60): `withScopes()`, `ActorBadge`, `pnpm agents:key`, header `X-PaperOS-Actor`.
* Impersonation (PAP-61), portal shell (PAP-62), console shell (PAP-63) with `fromAppSpec()` navigation, permission matrix report (PAP-64), enterprise SSO/SCIM (PAP-65, children PAP-230 to PAP-232).
* Security baseline (PAP-219): `securityHeaders()`, `controls.yaml` with `SEC-*` ids, rotation runbook, incident playbook. Session and device management (PAP-220), privacy DSAR (PAP-221), tenant API keys, webhooks and SDK (PAP-222).

**Requires**

* data-layer: `users`, `tenants`, `workspaces`, `membership` tables (PAP-33), migrations (PAP-32), RLS harness and session variables (PAP-34), oRPC (PAP-35), audit log (PAP-38), jobs (PAP-43), file storage (PAP-37), server-side secret encryption helper.
* app-shell: env schema and `SecretStore` (PAP-17), routes and layouts (PAP-16), Tauri deep links (PAP-19).
* design-system: primitives (PAP-67 children), layout (PAP-70), data display (PAP-71), states (PAP-234), theming (PAP-75).
* spec-builder: access section format (PAP-116), app-level spec (PAP-117), `data-action` attributes (PAP-120).
* libraries: auth decision inputs (PAP-214); quality: test-mode `login-as` (PAP-240) for every e2e.

**Milestone exit criteria**

* Auth works across web and desktop (2026-09-20): PAP-55, PAP-56, PAP-219 merged; PAP-223 and PAP-224 merged so a human signs in on the web with passkey and magic link; PAP-227 merged; PAP-58 `withTenant` sets RLS variables in the PAP-34 harness. PAP-225 (Tauri) and PAP-226 (OIDC) may land up to 2026-09-22.
* Roles and audiences enforced end to end (2026-09-25): PAP-59 umbrella test green; portal and console shells screenshotted at seven widths; impersonation e2e passes; PAP-220 security page live.
* Agent principals and enterprise (2026-09-30): nine agent users with scoped keys; permission matrix report in CI; PAP-221 and PAP-222 merged; PAP-65 children may slip past 2026-10-01 without blocking anything else.
""",
"design-system": """

## Contract

**Provides**

* Tokens (PAP-66): `@paperos/ui/styles/tokens.css`, `theme.css`, `tokens`, `rawTokens`, semantic names (`color.bg.surface`, `color.fg.muted`, ...), `--pos-` prefix, `data-theme` attribute contract.
* Twenty primitives (PAP-67, children PAP-236 to PAP-238) with spec IDs `ui.button` ... `ui.separator`, `cn()`, `defineComponentMeta`, `getPortalRoot()`, `ToastProvider`.
* Icons and illustrations (PAP-68): `Icon`, `IconName`, `Illustration`. Storybook (PAP-69): Pages URLs, `index.json`, `visual` and `proposal` tags, viewport names matching Gate 3 projects.
* Layout (PAP-70): `AppFrame`, `SplitPane`, `Inspector`, `CommandBar`, `ResponsiveGrid`, slot names `nav | sidebar | main | inspector | statusbar | commandbar | banner`.
* Data display (PAP-71): cell renderer registry (`registerCell`, `getCell`, `CellType`), `Badge`, `AvatarStack`, `Timeline`, `EmptyState`, `Skeleton`, `Money`, `RelativeTime`.
* Motion (PAP-72): `Presence`, `Collapse`, `useReducedMotion`, preset names, the motion lint rule. Accessibility audit (PAP-73): `a11y-report.json`, ARIA snapshot baselines, `meta.a11y`.
* Spec mapping (PAP-74): `registry.json`, `components.ts`, `resolveComponent()`, `validateComponentUsage()`. Theming (PAP-75): `ThemeProvider`, `generateBrandTheme()`, `brandingToInlineCss()`, `Logo`, `TenantBranding`.
* Guidelines (PAP-76): `rules.json` with `DS-*` ids and `checkable` flags. Design tooling decision (PAP-77).
* Pickers and forms (PAP-233): `DatePicker`, `DateRangePicker`, `RelativeDatePicker`, `useAppForm`, `FieldArray`. State components (PAP-234): `ErrorState`, `DeniedState`, `OfflineBanner`, `IntegrationUnavailable`, `LoadingPage`, `stateComponents` map. Print and email kit (PAP-235): `renderPdf()`, `renderEmail()`, `print.*` blocks.

**Requires**

* app-shell: `packages/ui` folder (PAP-13), `breakpoints.json` (PAP-14), Pages branch strategy (PAP-15), layout slot contract (PAP-16).
* libraries: primitive library decision (PAP-212) by 2026-09-19, else Base UI proceeds.
* spec-builder: final spec key names (PAP-114). data-layer: `tenant.branding` column (PAP-33), file storage (PAP-37), shared filter grammar for `RelativeRange`, `Money` type agreement with business-core (PAP-175).
* identity: `useCan` for `can` props and `DeniedState` (PAP-59), branding permission. quality: Gate 1 job slots (PAP-78), Gate 3 screenshots (PAP-82), rubric severities (PAP-79). collab: docs engine for guidelines (PAP-128).

**Milestone exit criteria**

* Tokens and primitives (2026-09-20): `tokens:build` and `tokens:check` green in CI; PAP-236 merged with Button under 6 KB; Storybook live on Pages with `index.json`; PAP-237 and PAP-238 merged by 2026-09-21; PAP-68 decided; PAP-70 and PAP-71 (moved here) merged by 2026-09-23 so tables and input are unblocked.
* Component library covers app shell needs (2026-09-25): a11y scan zero serious across 21 combinations; `registry.json` drift-checked; motion presets retrofitted on overlays; PAP-233 pickers and PAP-234 state components merged so codegen and field types can consume them.
* Themable per tenant with docs (2026-09-30): tenant branding re-themes the console live with no flash; twelve guideline pages and `rules.json` referenced by the spec-conformance reviewer; PAP-235 renders a branded invoice PDF and email; PAP-77 ADR recorded.
""",
"quality": """

## Contract

**Provides**

* `packages/contracts` (PAP-239): `Finding`, `GateReport<K>`, `ArtifactRef`, `GATE_STATUSES`, `findingId()`, `validateArtifact()`, JSON Schemas for every gate artifact.
* Gate 1 (PAP-78): `web-dist` artifact, `gate1.json`, status `gate/1-static`, composite actions `setup` and `sticky-comment`, `workflow_run` trigger. Security scans (PAP-80): `security.json`, `gate/1-security`, waivers file, SBOM. Web perf (PAP-87) and API perf (PAP-242): `perf.json`, `gate/1-perf`.
* Rubrics (PAP-79): `RUB-*` ids, severities S0-S3, calibration set, review comment template. Gate 2 (PAP-81, children PAP-243 to PAP-245): `runReview()`, `ReviewerDefinition`, statuses `gate/2-*`, `review-cost.json`. Calibration (PAP-241): `calibration.json`, `Introduced-By:` trailer.
* Test mode (PAP-240): `/__test/seed|reset|login-as|clock`, `testUsers`, Playwright fixtures `seed`, `loginAs`, `reset`, `clock`, `PAPEROS_TEST_MODE` guard.
* Gate 3 (PAP-82, children PAP-246 to PAP-248): project names `xs-320` ... `3xl-1920`, screenshot ID grammar, `visual.json`, contact sheets, `update-baselines` label, `gate/3-visual`. Videos (PAP-83): `FlowSpec`, `videos.json`, `gate/3-video`. Vision (PAP-84): `vision.json`, annotated images, `dom-metrics.json`, `gate/3-vision`. E2E (PAP-86): `functional` project, test-id convention, `ops/compose/preview.yml`, `gate/3-e2e`.
* Gate 4 (PAP-85, children PAP-249 to PAP-251): `ScenarioPlan`, oracles, `edgecases.json`, repro test convention, `gate/4-edge`.
* Release train (PAP-88, children PAP-252 to PAP-254): `environments.yaml`, `deployToEnvironment`, `certification.json`, release records, `promote.yml` webhook contract, `pnpm release:rollback`. Digest (PAP-89): `buildDigest()`, `/releases/<version>/`. Flakes (PAP-90): `flakes-delta.json`, `isQuarantined()`, `qa_flakes`.

**Requires**

* app-shell: `ci.yml` skeleton (PAP-13), `breakpoints.json` (PAP-14), Pages hosting (PAP-15), images and Coolify deploy (PAP-26), VPS (PAP-25).
* forge: branch policy and trailers (PAP-46), bot accounts (PAP-48), PR template (PAP-49), runners with Chromium, ffmpeg and LFS (PAP-50, PAP-45), tags (PAP-52).
* identity: auth server (PAP-223) for session minting, tenancy (PAP-58), threat model controls (PAP-219). data-layer: schema and seeds (PAP-32), oRPC procedure registry (PAP-35), `pg_stat_statements` (PAP-40), backups (PAP-30).
* design-system: Storybook `index.json` (PAP-69), `registry.json` (PAP-74), `rules.json` (PAP-76), print kit for the digest (PAP-235). spec-builder: spec schema (PAP-114) and validator (PAP-115). pm-linear: command grammar (PAP-94), webhooks (PAP-97), credit metering (PAP-98). collab: changelog (PAP-133).

**Milestone exit criteria**

* Gates 1 and 2 on every PR (2026-09-20): Gate 1 under 3 minutes warm on the sandbox PR; `packages/contracts` published; security workflow green with the four seeded findings; PAP-243 harness posts a stub review; PAP-246 story baselines committed at 21 combinations. PAP-244, PAP-245 and PAP-240 may land up to 2026-09-22.
* Visual and video gates (2026-09-25): authenticated page baselines via test mode; six flows recorded at four widths; vision calibration at precision 0.85 and recall 0.7; Gate 4 catches the four seeded defects; `@smoke` e2e under 5 minutes; web perf table posts with deltas.
* Edge-case hunting and release trains (2026-09-30): three nightly staging runs; one rehearsal RC approved through Needs Justin with the digest Justin confirmed; API perf smoke in certification; first weekly calibration report; flake quarantine demonstrated on a seeded flake.
""",
}

for key, pid in r2.PROJECTS.items():
    if pid in ch["projectsUpdated"]:
        print("skip", key); continue
    content = (cur[pid]["content"] or "")
    if "## Contract" in content:
        print("already has contract", key); continue
    new_content = content.rstrip() + CONTRACTS[key]
    print(key, "words", r2.words(new_content))
    if DRY: continue
    d = r2.gql("mutation($id: String!, $i: ProjectUpdateInput!) { p: projectUpdate(id: $id, input: $i) { success } }", {"id": pid, "i": {"content": new_content}})
    if d["p"]["success"]:
        ch["projectsUpdated"].append(pid); r2.save_changes(ch); print("updated project", key)
