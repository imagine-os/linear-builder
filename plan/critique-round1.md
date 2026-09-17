# Completeness critique of plan.json and specs

Checked on 2026-09-17. Before this pass: 17 projects, 197 issues, 197 specs (no issue was missing a spec, no dependency cycles, no phase inversions, no bad milestone names). After this pass: 206 issues, 206 specs, still no cycles or inversions. New specs are in `specs/gaps.json`; edited rows are in `plan.json`; eight existing spec texts were touched in `specs/bucket-*.json` (dependency sections only, plus one Needs Justin routing).

## 1. Brief coverage: gaps found and fixed

Every sentence of the brief mapped to at least one issue except the items below, which are now issues.

| Brief text | Gap | New issue |
| --- | --- | --- |
| "We can always remove features" / "having everything ... built into the product" | Nothing made removal cheap: no module contract, no `paperos create --without`, no tenant toggle | `app-shell/feature-modules` (P1) |
| "adapts to every single type of business in the whole wide world" | No locale layer anywhere (RTL and multi-currency mentioned in passing by 20 specs, owned by none) | `app-shell/i18n-l10n` (P1) |
| same sentence | No declared place for industry, terminology, audiences, currency, tax regime; seed packs alone do not adapt pages | `spec-builder/business-profile` (P2) |
| "every feature that Airtable has ... Notion ... ClickUp" | All three ship automations; the tables project had none | `tables/automations` (P2) |
| PAP-5: "how quickly do we get from blank screen ... to electrons" | Decomposed but never measured | `app-shell/new-app-drill` (P2, Review) |

## 2. Hidden dependencies in the P0 ready set: found and fixed

- **No host.** `forge/forgejo-deploy`, `data-layer/postgres-provision`, `pm-linear/orchestrator`, `realtime/yjs-server`, Electric and the release train all deploy "on the Hetzner VPS under Coolify", but no issue created the VPS, installed Coolify, set the Caddy proxy, wired DNS for `PAPEROS_DOMAIN`, created the backup bucket, sops keys, tailnet or the Resend sending domain. Two "ready now" issues would each have provisioned a host or stalled on Justin. Added `app-shell/vps-coolify-bootstrap` (P0, ready now, batches every credential ask into one Needs Justin item) and made those five issues depend on it.
- **No app deploy.** `quality/release-train` schedules nightly staging deploys and production promotions; `quality/e2e-flows` and `realtime/load-test` need a staging URL; nothing built the images or Coolify apps. Added `app-shell/app-deploy-pipeline` (P0); release-train and e2e-flows depend on it.
- **Shared database across parallel sessions.** `data-layer/drizzle-schema` referenced `ops/compose/dev.yml` that no issue creates, and depended on the production VPS to start. Added `data-layer/local-dev-stack` (compose stack, per-worktree database names and ports, SessionStart hook, CI service containers). `drizzle-schema` now depends on it instead of `postgres-provision`, which shortens the critical path for core-entities, RLS, API, auth and Yjs.
- **Job runner assumed by eight specs.** file-storage, search, notifications, social-scheduler, outreach-sequences, attribution, import-framework and export all name pg-boss; `libraries/backend-landscape` still lists the job queue as undecided. Added `data-layer/jobs-queue` (P1) and made the eight consumers depend on it.
- **File collisions.** `quality/ci-gate1` and `app-shell/gh-pages-demo` were "ready now" but write `ci.yml` and `vite.config.ts`, the same files `app-shell/monorepo-scaffold` creates. Both now depend on the scaffold (an M-size issue that lands within hours). `design-system/tokens` stays ready because it only adds a new folder.

Ready-now set after fixes: 21 issues (was 24). Everything in it is research, specs, Linear configuration, the scaffold, or host bootstrap; none writes to a file another ready issue creates.

## 3. Duplication between projects

- `identity/permission-tests` and `spec-builder/conformance-tests` both generated the policy-level access matrix from page specs. Fixed: permission-tests now depends on conformance-tests, imports its compiled matrix, and owns only the HTTP and UI levels plus the report.
- `data-layer/local-first-sync` and `realtime/offline-queue` both describe an offline write outbox. Not a duplicate: offline-queue explicitly hardens the outbox local-first-sync introduces. Left as is.
- `quality/screenshot-annotation` (vision agent inspects screenshots) and `collab/screenshot-annotations` (humans annotate screenshots into issues) are different features with confusingly similar keys. Left as is; worth renaming the collab one when it is created in Linear.
- No project duplicates another at the project level. `pm-linear` vs `agents`, `collab` vs `realtime`, `business-core` vs `growth` have clean seams.

## 4. Justin's review load

31 specs mention Needs Justin; almost all are correct uses (release-candidate approval once a week, roster and new-character approvals, credential and account sign-ups, spend increases, license of own code, flipping outreach out of sandbox, S0 security waivers). Two were approvals that gates can handle: `realtime/conflict-ux` (a UX rule set) now rides in the weekly release digest instead of its own item. `input/a11y-statement` stays because it is external-facing wording, which the queue policy names. `spec-builder/business-profile` shares the single Needs Justin item that `migration/business-templates` already files rather than adding one. `app-shell/new-app-drill` posts to PAP-5 as information, no approval.

Expected distinct human decisions over the two weeks: roughly 12 one-off items plus one release candidate per week, comfortably inside the five-open-items rule.

## 5. Risks Justin should know about

1. **P0 is 68 issues in four days (09-17 to 09-20).** Even with parallel sessions, the dependency chain scaffold -> local stack -> Drizzle -> core entities -> RLS -> API -> Better Auth -> Yjs server is serial and each step is M-size. Expect P0 to spill into 09-22 or 09-23; the phase dates should be treated as targets for the ready set, not for the whole phase.
2. **Human account setup is on the critical path.** Hetzner (may need identity verification), a domain or Cloudflare, Resend, Apple developer program for signed macOS builds, Stripe live keys, a payroll sandbox. `vps-coolify-bootstrap` batches the first four into one Needs Justin item on day one; answer it the same day or every infra issue waits.
3. **The orchestrator and the Coolify host hold every credential.** `pm-linear/orchestrator` runs with Linear, forge, Coolify and sops access on one VPS. A compromised session prompt or leaked token there is a total compromise. `agents/tool-scopes`, `quality/security-scans` and the destructive-action deny list are the mitigations; do not let those slip to P1.
4. **Automated review replaces human review, but nobody has calibrated it yet.** Thirty percent of credits go to reviewer agents, vision inspection and edge-case hunting. Until `agents/eval-harness` and `quality/review-rubrics` produce a false-negative rate, treat the first release candidate as a smoke test rather than a release. Plan for a manual spot-check of gate 2 verdicts on five PRs in week one.
5. **P2 carries the business layer, growth, migration and hardening in five days.** Stripe Connect, ledger, payroll adapter, CRM, social scheduler and importers are each L-size. Something will not ship by 10-01. Decide now what the release candidate must contain (suggested: template + spec builder + tables + collab + identity + billing) and let the rest land after the deadline with remaining credits.
6. **Scope creep by design.** The brief says "go deep" and the plan obliges, but 206 issues with generous specs will burn credits on research and docs (17 percent of budget). Enforce the time boxes in the research issues (one session each, ADR or stop) and let `pm-linear/credit-metering` post the daily burn so the trade-off is visible by day three, not day ten.
