import os
import json, sys

OUT = os.environ.get("PAPEROS_PLAN_DIR", ".") + "/plan.json"

plan = {}

plan["vision"] = (
    "PaperOS Core Platform is the reusable foundation every future PaperOS app is generated from: one spec-driven "
    "TypeScript monorepo template that ships to web, desktop (Linux/macOS/Windows) and mobile with a shared data layer, "
    "design system, multiplayer, table/views engine, identity for every audience, and business plumbing (payments, ledger, payroll, CRM) already wired. "
    "It is built and reviewed primarily by a roster of Claude agent characters working from Linear, behind a four-gate automated quality pipeline, "
    "so that by 2026-10-01 a new app goes from blank screen to running product in hours, and Justin only ever reviews release candidates, not pull requests."
)

plan["decisions"] = [
  {"title": "Stack: TypeScript monorepo, React 19 + Vite, Tauri 2 for native",
   "decision": "One pnpm + Turborepo monorepo. Web is React 19 + Vite + TanStack Router. Desktop (Linux, macOS, Windows) and mobile (iOS, Android) are Tauri 2 wrapping the same web bundle. PWA is the zero-install baseline.",
   "why": "A single codebase reaches every device class the brief lists; Tauri gives real multi-window (multi-monitor) and OS integration with a tiny Rust core, and Claude agents are strongest in TypeScript, which maximizes credit efficiency."},
  {"title": "Hosting: self-hosted VPS via Coolify, GitHub Pages for demos",
   "decision": "Postgres, Forgejo, the API, the Yjs server and MinIO run in Docker on a Hetzner VPS managed by Coolify. Static demos and Storybook deploy to GitHub Pages. Vercel is not used for deploys (read-only).",
   "why": "Owns the data and the forge, costs tens of dollars a month, and avoids depending on a platform we cannot write to; Pages already exists as the public demo convention."},
  {"title": "Data: Postgres as source of truth, Drizzle schema-as-code, local-first sync",
   "decision": "Postgres 17 with row-level security for tenancy, Drizzle ORM for typed schema and migrations, ElectricSQL shapes + PGlite for local-first reads and an offline write queue. Yjs handles document/canvas CRDTs; records stay relational.",
   "why": "Relational data with RLS is the safest multi-tenant model for agent-written code; local-first sync gives instant UI on every device; separating documents (CRDT) from records (SQL) avoids reinventing either."},
  {"title": "Realtime: Yjs via Hocuspocus for documents and presence, Electric for records",
   "decision": "Self-hosted Hocuspocus server persists Yjs docs to Postgres and provides presence/awareness; Electric streams record changes. One WebSocket transport, auth via Better Auth session tokens.",
   "why": "Both are mature open-source pieces the brief's multiplayer, comments, canvas and multi-window requirements map onto directly; no custom sync protocol in two weeks."},
  {"title": "Auth and audiences: Better Auth, agents as first-class principals",
   "decision": "Better Auth (self-hosted, TypeScript) with passkeys, magic links and OAuth, organization/tenant plugin, plus a permission engine combining roles with attribute policies declared in page specs. Audiences are composable segments (customer tiers, staff roles, partners, admins, agents). Every agent gets a scoped API key and visible attribution.",
   "why": "Covers customer vs staff vs everything between without a vendor lock-in, and making agents principals is what makes audit logs, permissions and presence honest when most contributors are Claude."},
  {"title": "Repo template shape",
   "decision": "paperos-template contains apps/web, apps/desktop, apps/mobile, packages/{ui,core,spec,views,agents}, specs/ (app.spec.yaml + page specs), docs/, .claude/ (CLAUDE.md, agents, skills, rules), ops/ (compose, CI). `paperos create <app>` clones it into a pre-provisioned imagine-os repo and wires Forgejo mirror, CI, Pages and a Linear project.",
   "why": "Agents need a predictable place for everything; the template is the product, apps are instances."},
  {"title": "Version control: Git as the format, Forgejo as our forge, GitHub mirrored",
   "decision": "Do not build a VCS. Self-host Forgejo as the primary forge with bidirectional push mirroring to the GitHub org imagine-os, Forgejo Actions runners as CI fallback, and a disaster-recovery drill that rebuilds everything with GitHub offline.",
   "why": "The intent is independence from GitHub, not a new data format; Git + Forgejo delivers that in two days, while a custom VCS would eat the whole budget and break every tool agents rely on."},
  {"title": "Project management: Linear stays system of record, thin PM module syncs to it",
   "decision": "Linear is the queue through Oct 1 with states Backlog -> Ready for Claude -> In Progress -> In Review -> Needs Justin -> Done. PaperOS ships a PM data model mirroring Linear and a bidirectional sync; boards are rendered by the views engine. Rebuilding Linear is explicitly out of scope for this build.",
   "why": "The orchestrator needs a stable queue today; a mirrored data model preserves the option to cut over later at low cost."},
  {"title": "Spec-first: every page has a page.spec.yaml",
   "decision": "Each page declares purpose, logic, access, data, integrations, layout, components, states and edge cases. A validator blocks PRs without specs; codegen scaffolds pages; conformance and permission tests are derived from specs; the canvas UX-flow view is generated from them.",
   "why": "Specs are the contract between Justin and agents: they let many parallel sessions build consistently and let review be mechanical."},
  {"title": "Design system: DTCG tokens, Base UI/Radix primitives, Tailwind v4, Storybook",
   "decision": "Tokens in W3C DTCG JSON compile to CSS variables; components built on headless primitives with Tailwind v4; Storybook with a11y and interaction tests is the living doc; runtime theming per tenant.",
   "why": "Headless primitives give accessibility for free, tokens make per-tenant branding trivial, and Storybook gives the quality pipeline something to screenshot."},
  {"title": "Quality pipeline: four automated gates before anything reaches Justin",
   "decision": "Gate 1 static (typecheck, Biome, Vitest, build). Gate 2 three Claude reviewer agents (correctness, security, spec-conformance). Gate 3 Playwright screenshots + video replays across a 7-width breakpoint matrix and themes, inspected by a vision agent. Gate 4 edge-case hunter. Weekly release candidates land in Needs Justin with a one-page digest.",
   "why": "Justin is the only human reviewer; the budget is spent on machines reviewing machines so his queue stays under five items."},
  {"title": "Agent runtime: Claude Code sessions orchestrated from Linear",
   "decision": "An orchestrator polls Ready for Claude, spawns one Claude Code session per issue in its own git worktree, with the character's .claude/agents definition, skills and MCP allowlist, and moves the issue through states. Every prompt, response and tool call is logged to the prompt-log store.",
   "why": "Matches how the credits are spent (many parallel sessions) and makes the agent org observable, budgetable and auditable."},
  {"title": "Business core: Stripe for money movement, our own ledger, payroll via adapters",
   "decision": "Stripe Billing + Connect + Tax for payments; a double-entry ledger in Postgres we own; payroll behind a provider interface with Check or Gusto Embedded as the first adapter.",
   "why": "Money movement and payroll are regulated and not worth building; the ledger is the one finance primitive every business type shares and must be ours to report on."},
  {"title": "Libraries: borrow before build, ADR per adoption, license policy in CI",
   "decision": "A Scout character evaluates libraries and whole OSS products against a rubric; every adoption gets an ADR in the decision log; a CI license check blocks disallowed licenses.",
   "why": "The brief asks to find and factor in libraries; making that a governed, logged process keeps 20 parallel agents from importing 20 different table libraries."},
  {"title": "Credit stance: 30% of spend on automated review and QA",
   "decision": "Roughly 12% planning/specs, 45% building, 30% automated review/QA, 8% docs/knowledge, 5% research; per-character budgets and a kill switch enforce it.",
   "why": "Unreviewed agent code is the fastest way to waste the remaining 55%; review spend is what keeps Justin's queue small."},
]

plan["phases"] = [
  {"key": "P0", "name": "Foundation", "dates": "2026-09-17 to 2026-09-20",
   "goal": "Linear pipeline, orchestrator and agent roster live; template monorepo runs on web + desktop; Postgres, Forgejo mirror, auth, tokens, spec schema and CI gates 1-3 exist so parallel sessions can start safely."},
  {"key": "P1", "name": "Core systems", "dates": "2026-09-21 to 2026-09-26",
   "goal": "Spec builder, design system components, multiplayer, table/views engine, collaboration (comments, canvas, docs, prompt logs), multi-input and permission engine reach usable v1 with conformance tests."},
  {"key": "P2", "name": "Business layer + hardening", "dates": "2026-09-27 to 2026-10-01",
   "goal": "Payments, ledger, payroll adapter, CRM/growth, migration/import tools ship; load, DR and accessibility drills pass; first release candidate and handbook delivered to Justin."},
]

plan["budget"] = [
  {"area": "Planning, specs and ADRs", "share_pct": 12, "why": "Every page and system gets a spec before code; specs are what make parallel agent work coherent and reviewable."},
  {"area": "Building (code, infra, integrations)", "share_pct": 45, "why": "Seventeen projects and ~200 issues in two weeks; the bulk of tokens go to implementation sessions in worktrees."},
  {"area": "Automated review and QA", "share_pct": 30, "why": "Three reviewer agents, vision screenshot inspection, video replays, edge-case hunting and evals on every PR replace the human review Justin cannot supply."},
  {"area": "Docs, changelogs, prompt logs and handbooks", "share_pct": 8, "why": "Documentation is the memory of the agent org and the onboarding path for every future app."},
  {"area": "Research and library scouting", "share_pct": 5, "why": "Borrow-before-build saves far more than it costs, but research must be time-boxed and ADR-bound."},
]

def A(name, role, reportsTo, tools, access, plugins, subs):
    return {"name": name, "role": role, "reportsTo": reportsTo, "tools": tools, "access": access, "plugins": plugins,
            "subAgents": [{"name": n, "role": r} for n, r in subs]}

plan["agents"] = [
  A("Atlas", "Chief Architect and Orchestrator: owns the master plan, decomposes work, dispatches Ready for Claude issues to characters, guards dependencies and budget", "Justin",
    ["Linear API", "GitHub/Forgejo API", "Claude Agent SDK", "credit-metering", "decision-log"],
    ["linear:admin", "forgejo:org-admin", "github:imagine-os admin", "budget:read-write", "prod:read-only"],
    ["linear-api", "github", "workflow-authoring"],
    [("Dispatcher", "Claims issues, spawns sessions in worktrees, moves Linear states"),
     ("Decomposer", "Splits epics into spec-complete issues with acceptance criteria"),
     ("Merger", "Rebases, resolves conflicts, merges green PRs, tags releases")]),
  A("Forge", "Platform Engineer: app shell, Tauri targets, data layer, forge/mirroring, hosting and CI infrastructure", "Atlas",
    ["Bash", "pnpm/Turborepo", "Tauri CLI", "Drizzle", "Docker/Coolify", "Forgejo API"],
    ["repo:write (all)", "vps:deploy", "postgres:migrate (staging)", "secrets:infra"],
    ["github", "session-start-hook"],
    [("Tauri Smith", "Desktop and mobile targets, multi-window, OS integration"),
     ("Schema Wright", "Drizzle schema, migrations, RLS policies, seeds"),
     ("Ops Runner", "VPS, Docker, backups, runners, observability")]),
  A("Iris", "Design Systems Lead: tokens, components, theming, motion, Storybook and accessibility of the component library", "Atlas",
    ["Storybook", "Tailwind v4", "axe-core", "Playwright screenshots", "Figma tokens export"],
    ["repo:write packages/ui", "storybook:deploy", "design-tokens:write"],
    ["artifact-design", "dataviz"],
    [("Token Keeper", "DTCG tokens, themes, per-tenant branding"),
     ("Component Crafter", "Headless primitives to production components with stories"),
     ("Motion and Input Stylist", "Transitions, reduced motion, focus and input-state styling")]),
  A("Quill", "Spec and Documentation Lead: page/app specs, docs engine content, changelogs, ADRs and prompt-log curation", "Atlas",
    ["spec validator CLI", "docs engine", "Notion API", "Google Drive API", "Linear API"],
    ["repo:write specs/ docs/", "notion:read-write", "drive:read", "linear:comment"],
    ["notion-api", "linear-api"],
    [("Page Spec Writer", "Interviews, drafts and validates page.spec.yaml files"),
     ("Changelog Scribe", "Turns merged PRs into human and tenant changelogs"),
     ("Prompt Logger", "Curates and redacts session logs into searchable knowledge")]),
  A("Sentinel", "Quality Lead: owns the four review gates, reviewer agents, visual and video inspection, edge-case discovery and release digests", "Atlas",
    ["Playwright", "Vitest", "Biome", "Semgrep", "vision model screenshot inspection", "Lighthouse CI"],
    ["repo:review + request-changes", "ci:admin", "artifacts:write", "linear:comment", "no merge rights"],
    ["code-review", "security-review", "simplify"],
    [("Code Reviewer", "Correctness and simplification review on every PR"),
     ("Security Auditor", "Auth, RLS, secrets, dependency and injection review"),
     ("Visual Inspector", "Screenshot and video-replay inspection across the breakpoint matrix"),
     ("Edge Case Hunter", "Adversarial inputs, empty/huge states, offline and slow-device scenarios")]),
  A("Nova", "Product Systems Engineer: multiplayer, collaboration surfaces, canvas, tables and views engine, multi-input control", "Atlas",
    ["Yjs/Hocuspocus", "ElectricSQL", "TanStack Table", "tldraw/React Flow", "Tiptap", "dnd-kit"],
    ["repo:write packages/views packages/collab apps/web", "yjs-server:deploy (staging)"],
    ["github"],
    [("CRDT Engineer", "Yjs rooms, presence, offline queue, conflict UX"),
     ("Views Engineer", "Grid, kanban, calendar, gallery, chart views and the query compiler"),
     ("Canvas Cartographer", "UX-flow canvas generated from specs, comments anchored to elements")]),
  A("Ledger", "Business Systems Lead: Stripe billing and Connect, double-entry ledger, invoicing, finance reports, payroll adapters", "Atlas",
    ["Stripe API (test mode)", "ledger service", "PDF generation", "payroll provider sandboxes"],
    ["stripe:test-mode write", "stripe:live read-only", "repo:write packages/finance", "ledger:post (staging)"],
    ["github"],
    [("Payments Integrator", "Stripe products, subscriptions, Connect, Tax, webhooks"),
     ("Bookkeeper", "Ledger, journal posting rules, P&L and cash-flow reports"),
     ("Payroll Adapter", "Provider interface and first Check/Gusto Embedded adapter")]),
  A("Beacon", "Growth Lead: CRM, outreach sequences, social scheduling, landing pages, attribution and support inbox", "Atlas",
    ["Webflow API", "Resend/Twilio", "social platform APIs", "Gamma", "Miro"],
    ["webflow:write", "crm:write", "email:send (sandbox until approved)", "repo:write packages/growth"],
    ["github"],
    [("Campaign Composer", "Drafts posts, emails and landing copy from changelogs and specs for approval"),
     ("CRM Builder", "Lead, contact, deal and segment models and views"),
     ("Outreach Sequencer", "Sequences, warmup, reply detection, compliance")]),
  A("Scout", "Library and Migration Researcher: evaluates libraries and OSS products, maintains the registry, builds importers and business templates", "Atlas",
    ["WebSearch/WebFetch", "npm/GitHub search", "license checker", "import framework", "Airtable/Notion/ClickUp/QuickBooks APIs"],
    ["repo:write docs/registry packages/import", "external-apis:read", "no prod write"],
    ["github"],
    [("Library Evaluator", "Rubric scoring, ADR drafts, license checks"),
     ("Import Mapper", "Schema mapping, dry runs, ID mapping for migrations"),
     ("Template Packager", "Business-type seed packs and demo data")]),
]

plan["labels"] = {"groups": [
  {"name": "Phase", "labels": [{"name": "P0", "color": "#EB5757"}, {"name": "P1", "color": "#F2994A"}, {"name": "P2", "color": "#F2C94C"}]},
  {"name": "Type", "labels": [{"name": "Research", "color": "#9B51E0"}, {"name": "Spec", "color": "#5E6AD2"}, {"name": "Build", "color": "#2F80ED"},
                               {"name": "Review", "color": "#27AE60"}, {"name": "Infra", "color": "#6B7280"}, {"name": "Docs", "color": "#56CCF2"}]},
  {"name": "Surface", "labels": [{"name": "Customer", "color": "#26B5CE"}, {"name": "Staff", "color": "#BB87FC"}, {"name": "Developer", "color": "#4CB782"}, {"name": "Agent", "color": "#F7C8E0"}]},
]}

plan["states"] = [
  {"name": "Ready for Claude", "type": "unstarted", "description": "Spec-complete and unblocked; the orchestrator may claim it and spawn a Claude Code session."},
  {"name": "In Review", "type": "started", "description": "PR open; automated gates (static, reviewer agents, visual/video, edge cases) running or awaiting merge."},
  {"name": "Needs Justin", "type": "started", "description": "Blocked on a human decision or release approval; kept under five open items at a time."},
]

# ---------------- projects ----------------
projects = []

class P:
    def __init__(self, key, name, color, icon, summary, description, phase, priority, dependsOn, milestones):
        self.d = {"key": key, "name": name, "color": color, "icon": icon, "summary": summary, "description": description,
                  "phase": phase, "priority": priority, "dependsOn": dependsOn,
                  "milestones": [{"name": m[0], "targetDate": m[1], "goal": m[2]} for m in milestones], "issues": []}
        self.key = key
        projects.append(self.d)
    def I(self, slug, title, oneLine, phase, priority, type_, surface, mi, deps=None, ready=False):
        deps = deps or []
        full = [d if "/" in d else f"{self.key}/{d}" for d in deps]
        self.d["issues"].append({"key": f"{self.key}/{slug}", "title": title, "oneLine": oneLine, "phase": phase,
            "priority": priority, "type": type_, "surface": surface, "milestone": self.d["milestones"][mi]["name"],
            "dependsOn": full, "readyNow": ready})

C, S, D, G = "Customer", "Staff", "Developer", "Agent"

# 1 app-shell
p = P("app-shell", "Universal App Shell & Repo Template", "#2F80ED", "Rocket",
  "The paperos-template monorepo that runs the same app on web, PWA, Linux/macOS/Windows desktop and iOS/Android with multi-window support.",
  "Goal: a single template repository that any new PaperOS app is generated from and that ships to every device class from day one. It is a pnpm + Turborepo monorepo with a React 19 + Vite web app, Tauri 2 desktop and mobile targets, an installable PWA, and a file-based router whose layouts are driven by page specs. It owns the responsive breakpoint matrix and a window manager that lets panels detach into separate OS windows across monitors, plus a Linux kiosk mode that launches synced windows on several displays. The `paperos create` CLI clones the template into a pre-provisioned imagine-os repo and wires the Forgejo mirror, CI, GitHub Pages demo and a Linear project. Non-goals: native Swift/Kotlin UI, Electron, or a custom bundler. It consumes the design system, data layer and identity packages and is the host for every other project's UI.",
  "P0", 1, ["design-system", "data-layer"],
  [("Template scaffolds and runs on web", "2026-09-19", "Monorepo builds, routes render, Pages demo live"),
   ("Desktop and mobile shells build", "2026-09-23", "Tauri desktop + mobile targets build from the same bundle"),
   ("Multi-monitor and PWA polish", "2026-09-29", "Window manager, kiosk mode, offline shell, template guide")])
p.I("monorepo-scaffold", "Scaffold paperos-template monorepo with pnpm, Turborepo, strict TypeScript and a Vite React 19 web app", "Create the root workspace, apps/web, packages/*, shared tsconfig and lint config.", "P0", 1, "Build", [D], 0, ready=True)
p.I("device-matrix-research", "Research and document the target device matrix (phone, tablet, laptop, desktop, TV/kiosk, foldable) with breakpoints and test devices", "Produces the 7-width breakpoint list the quality pipeline screenshots against.", "P0", 2, "Research", [D], 0, ready=True)
p.I("gh-pages-demo", "Set up GitHub Pages demo deploy for every app with per-PR preview URLs", "Static build of apps/web published on merge and on PR branches.", "P0", 2, "Infra", [D], 0, ready=True)
p.I("router-layouts", "Implement file-based router with layout slots (nav, sidebar, inspector, command bar) driven by page specs", "TanStack Router with typed routes and slot-based layouts that page specs fill.", "P0", 1, "Build", [D], 0, ["monorepo-scaffold"])
p.I("env-config", "Define typed environment and config layer with per-target secret storage (web, desktop keychain, mobile secure storage)", "Zod-validated config with target-specific secret backends.", "P0", 2, "Build", [D], 0, ["monorepo-scaffold"])
p.I("pwa", "Ship installable PWA manifest, service worker and offline app shell", "Workbox-based caching so the shell loads offline and installs on any browser.", "P0", 2, "Build", [C], 0, ["monorepo-scaffold"])
p.I("tauri-desktop", "Add Tauri 2 desktop target for Linux, macOS and Windows sharing the web bundle", "Cargo workspace, capability config, auto-update, signed builds in CI.", "P0", 1, "Build", [D], 1, ["monorepo-scaffold"])
p.I("tauri-mobile", "Add Tauri 2 mobile targets (iOS, Android) with platform capability shims", "Mobile builds plus shims for camera, haptics, secure storage.", "P1", 2, "Build", [C, D], 1, ["tauri-desktop"])
p.I("breakpoints-windows", "Build responsive breakpoint matrix and multi-monitor window manager that detaches panels into OS windows", "Container queries per breakpoint; panels pop out into Tauri windows and remember placement.", "P1", 1, "Build", [C, S], 1, ["tauri-desktop", "device-matrix-research"])
p.I("create-cli", "Write `paperos create <app>` CLI that clones the template into an imagine-os repo and wires Forgejo mirror, CI, Pages and a Linear project", "One command from blank screen to a running, tracked app.", "P1", 1, "Build", [D, G], 1, ["router-layouts", "forge/mirror", "pm-linear/configure-workspace"])
p.I("linux-kiosk", "Support Linux kiosk and parallel-browser mode launching synced windows across displays from one CLI flag", "Multi-display staff dashboards and signage from the same build.", "P2", 3, "Build", [S], 2, ["breakpoints-windows", "realtime/multi-window-sync"])
p.I("template-docs", "Write the repo template guide: folder conventions, how an agent adds a page, how to ship each target", "The first document every new session reads.", "P1", 2, "Docs", [D, G], 2, ["router-layouts", "tauri-desktop"])

# 2 data-layer
p = P("data-layer", "Data Layer & Database", "#27AE60", "Database",
  "Postgres 17 with row-level security, Drizzle schema-as-code, a typed API, local-first sync, files, search and audit.",
  "Goal: every app gets a production-grade, multi-tenant data foundation without writing infrastructure. Postgres is the single source of truth, Drizzle defines the schema and migrations in TypeScript, and RLS policies enforce tenant isolation even against buggy agent-written queries. A typed RPC layer generates Zod schemas from the database so front-end hooks are always in sync. ElectricSQL shapes and PGlite give local-first reads and an offline write queue on every target. Core entities (tenant, workspace, user, membership, role, audit event, file) are shared by all other projects. Object storage, full-text plus vector search, an append-only audit log and OpenTelemetry observability round it out. Non-goals: multi-database support or a custom query language.",
  "P0", 1, [],
  [("Postgres + Drizzle baseline", "2026-09-19", "Database provisioned, schema and migrations flowing, core entities modelled"),
   ("Local-first sync working", "2026-09-24", "Electric shapes and PGlite deliver offline reads and queued writes"),
   ("Tenant-safe and observable", "2026-09-30", "RLS tested, audit log, search, tracing and data dictionary live")])
p.I("postgres-provision", "Provision Postgres 17 on the self-hosted VPS with automated backups and point-in-time recovery", "Coolify-managed Postgres with WAL archiving to object storage.", "P0", 1, "Infra", [D], 0, ready=True)
p.I("sync-research", "Evaluate Zero, ElectricSQL, PowerSync and Replicache for local-first sync and write an ADR", "Benchmark on the core entities and decide the sync engine.", "P0", 1, "Research", [D], 0, ready=True)
p.I("drizzle-schema", "Set up Drizzle ORM schema-as-code with migration workflow and seed scripts", "drizzle-kit migrations run in CI and on deploy; seeds for local dev.", "P0", 1, "Build", [D], 0, ["postgres-provision"])
p.I("core-entities", "Model core platform entities: tenant, workspace, user, membership, role, audit_event, file", "The shared tables every other project extends.", "P0", 1, "Spec", [D], 0, ["drizzle-schema"])
p.I("rls-tenancy", "Implement Postgres row-level security policies for multi-tenant isolation with a cross-tenant test harness", "Every table gets tenant_id policies; tests attempt cross-tenant reads and must fail.", "P0", 1, "Build", [D, S], 0, ["core-entities"])
p.I("api-layer", "Expose a typed API via oRPC with Zod schemas generated from Drizzle", "End-to-end types from database to React hooks.", "P0", 1, "Build", [D], 0, ["core-entities"])
p.I("local-first-sync", "Integrate PGlite and ElectricSQL shapes for local-first reads with an offline write queue", "Instant UI on every device; writes replay when online.", "P1", 1, "Build", [C, D], 1, ["api-layer", "sync-research"])
p.I("file-storage", "Add S3-compatible object storage (MinIO) with signed uploads and image variants", "Files table plus presigned upload flow and thumbnail generation.", "P1", 2, "Build", [C], 1, ["core-entities"])
p.I("audit-log", "Build append-only audit log with actor (human or agent), diff and reason fields", "Every mutation records who, what changed and why.", "P1", 2, "Build", [S, G], 1, ["core-entities"])
p.I("search", "Add full-text and vector search (tsvector + pgvector) over any entity through a search registry", "Entities register searchable fields; one search API.", "P1", 2, "Build", [C, S], 1, ["core-entities"])
p.I("observability", "Wire OpenTelemetry tracing, slow-query logging and Grafana dashboards for API and sync", "See latency and errors per route and per tenant.", "P2", 2, "Infra", [D], 2, ["api-layer"])
p.I("data-dictionary", "Generate a living data dictionary from the Drizzle schema into the docs system", "Tables, columns, relations and policies rendered in-app.", "P2", 3, "Docs", [D], 2, ["drizzle-schema", "collab/docs-engine"])

# 3 forge
p = P("forge", "Version Control & Forge Independence", "#6B7280", "GitBranch",
  "Git stays the format; a self-hosted Forgejo becomes our forge, mirrored both ways with GitHub, with its own CI runners and a proven recovery drill.",
  "Goal: PaperOS is never hostage to GitHub while keeping every Git-based tool agents rely on. We deploy Forgejo on our VPS behind Caddy with SSO, mirror every imagine-os repo bidirectionally, run Forgejo Actions runners so CI survives a GitHub outage, and script repo bootstrap so pre-provisioned repos get mirrors, secrets, labels and webhooks automatically. Branch protection, conventional commits and worktree-per-issue conventions make parallel agent work safe. A disaster-recovery drill rebuilds everything from Forgejo backups with GitHub offline. Non-goal: a from-scratch version control system; the ADR records why. Later, repo browsing and diffs surface inside PaperOS via the Forgejo API.",
  "P0", 1, [],
  [("Forgejo live and mirrored", "2026-09-19", "Forgejo deployed, all repos mirrored, bot accounts and branch policy in place"),
   ("CI runs on both forges", "2026-09-24", "Actions runners, bootstrap script and release automation"),
   ("Disaster recovery proven", "2026-09-30", "Drill passes; in-app git browsing")])
p.I("vcs-decision-adr", "Write ADR: keep Git as the format, self-host Forgejo, mirror GitHub, defer any custom VCS", "Records the pragmatic route and the criteria that would reopen the decision.", "P0", 1, "Spec", [D], 0, ready=True)
p.I("forgejo-deploy", "Deploy Forgejo on the VPS behind Caddy with SSO from Better Auth and nightly backups", "Our own forge with TLS, backups and org structure mirroring imagine-os.", "P0", 1, "Infra", [D], 0, ready=True)
p.I("branch-policy", "Define branch protection, conventional commits and worktree-per-issue conventions for parallel agents", "Rules that let 20 sessions commit without stepping on each other.", "P0", 1, "Spec", [D, G], 0, ready=True)
p.I("mirror", "Configure bidirectional push mirroring between Forgejo and the GitHub org imagine-os for all repos", "Either forge can be primary; commits land on both within a minute.", "P0", 1, "Infra", [D], 0, ["forgejo-deploy"])
p.I("bot-accounts", "Create scoped bot accounts and deploy keys for each agent character on both forges", "Least-privilege identities so commits are attributable to characters.", "P0", 2, "Infra", [G], 0, ["forgejo-deploy"])
p.I("pr-templates", "Author PR template linking Linear issue, page spec, screenshots and the review-gate checklist", "Every PR carries what reviewers and Justin need.", "P0", 2, "Docs", [D, G], 0, ["branch-policy"])
p.I("actions-runner", "Run Forgejo Actions runners so CI works even when GitHub is unavailable", "Same workflow files run on either forge.", "P1", 2, "Infra", [D], 1, ["forgejo-deploy"])
p.I("repo-bootstrap", "Script `forge bootstrap <repo>` to configure imagine-os repos with mirrors, secrets, labels and webhooks", "Turns pre-provisioned empty repos into ready ones in one command.", "P1", 2, "Build", [D, G], 1, ["mirror", "bot-accounts"])
p.I("release-tags", "Automate semantic release tags and changelog generation on merge to main", "Conventional commits produce versions and release notes.", "P1", 2, "Build", [D], 1, ["branch-policy", "collab/changelog"])
p.I("dr-drill", "Run a disaster-recovery drill rebuilding all repos and CI from Forgejo backups with GitHub offline", "Proves independence; documents recovery time.", "P2", 2, "Review", [D], 2, ["mirror", "actions-runner"])
p.I("in-app-git", "Expose repo browsing, diffs and commit history inside PaperOS via the Forgejo API", "Developers and agents see code history next to specs and issues.", "P2", 3, "Build", [D], 2, ["forgejo-deploy", "app-shell/router-layouts"])

# 4 identity
p = P("identity", "Identity, Roles & Audiences", "#BB87FC", "Shield",
  "Better Auth with passkeys and organizations, a role+attribute permission engine driven by page specs, and audiences from customer tiers to staff to agents.",
  "Goal: any app knows exactly who is acting, which tenant they belong to and what they may do, whether they are a customer, a staff member, a partner, an admin or a Claude agent. Better Auth provides passkeys, magic links, OAuth and organizations across web and Tauri. The audience model treats segments as composable so 'everything in between' is a configuration, not a rewrite. The permission engine combines roles with attribute policies declared in page specs, backed by Postgres RLS, and permission matrix tests are generated from those specs. Agents are first-class principals with scoped keys and visible attribution. Separate customer portal and staff console shells demonstrate the split. Non-goals: building our own auth protocol or password storage.",
  "P0", 1, ["data-layer"],
  [("Auth works across web and desktop", "2026-09-20", "Sign-in, sessions, organizations and audience model defined"),
   ("Roles and audiences enforced end to end", "2026-09-25", "Permission engine, impersonation, portal and console shells"),
   ("Agent principals and enterprise", "2026-09-30", "Agent keys, permission tests, SSO/SCIM")])
p.I("audience-model", "Specify the audience model: customer tiers, staff roles, partners, admins, agents and composable segments in between", "The vocabulary every spec and policy uses for who.", "P0", 1, "Spec", [C, S, G], 0, ready=True)
p.I("auth-research", "Compare Better Auth, Lucia, Clerk and Auth.js for self-hosting, organizations and passkeys; write ADR", "Confirms the auth choice before wiring it everywhere.", "P0", 2, "Research", [D], 0, ready=True)
p.I("better-auth", "Install Better Auth with passkeys, magic link, Google/GitHub OAuth and sessions for web and Tauri", "One auth server, cookie sessions on web, secure token storage on native.", "P0", 1, "Build", [C, S], 0, ["data-layer/core-entities", "auth-research"])
p.I("org-tenancy", "Implement organizations, workspaces, invitations and tenant switching", "Multi-tenant membership flows on top of Better Auth.", "P0", 1, "Build", [S], 0, ["better-auth"])
p.I("rbac-abac", "Build permission engine combining role-based grants with attribute policies declared in page specs", "One `can(actor, action, resource)` used by API, RLS and UI.", "P0", 1, "Build", [D], 0, ["audience-model", "data-layer/rls-tenancy"])
p.I("agent-principals", "Make agents first-class principals with scoped API keys, rate limits and visible attribution", "Agent actions are permissioned and attributed like any user.", "P1", 1, "Build", [G], 2, ["rbac-abac"])
p.I("impersonation", "Add staff 'view as customer' impersonation with full audit trail", "Support and QA see exactly what a customer sees.", "P1", 2, "Build", [S], 1, ["rbac-abac", "data-layer/audit-log"])
p.I("customer-portal-shell", "Ship the customer-facing portal shell (login, profile, billing entry) separate from the staff console", "Reference customer surface every app inherits.", "P1", 2, "Build", [C], 1, ["org-tenancy", "app-shell/router-layouts"])
p.I("staff-console-shell", "Ship the staff console shell with tenant switcher, audience filters and admin navigation", "Reference staff surface every app inherits.", "P1", 2, "Build", [S], 1, ["org-tenancy", "app-shell/router-layouts"])
p.I("permission-tests", "Generate permission matrix tests from page specs covering who can see and do what on every page", "Turns access sections into failing tests when policies drift.", "P1", 1, "Review", [D], 2, ["rbac-abac", "spec-builder/access-section"])
p.I("sso-scim", "Add SAML/OIDC SSO and SCIM provisioning for enterprise tenants", "Enterprise readiness without touching app code.", "P2", 3, "Build", [S], 2, ["org-tenancy"])

# 5 design-system
p = P("design-system", "Design System", "#F2994A", "Palette",
  "DTCG tokens compiled to CSS variables, accessible components on headless primitives with Tailwind v4, themes per tenant, and Storybook as the living document.",
  "Goal: every page an agent generates looks like one product and passes accessibility by default. Tokens for color, type, space, radius, motion and elevation live in W3C DTCG JSON and compile to CSS variables, enabling light, dark, high-contrast and per-tenant brand themes at runtime. Components are built on Base UI/Radix primitives with Tailwind v4, covering primitives, layout (AppFrame, SplitPane, Inspector, CommandBar) and data display. Storybook with a11y, viewport and interaction addons deploys to GitHub Pages and is what the quality pipeline screenshots. Every component maps to a spec-builder component ID so page specs reference real parts. Non-goals: a bespoke CSS-in-JS runtime or pixel-perfect Figma parity on day one.",
  "P0", 1, [],
  [("Tokens and primitives", "2026-09-20", "Token pipeline, 20 core components, icons, Storybook live"),
   ("Component library covers app shell needs", "2026-09-25", "Layout and data-display components, motion, a11y audit"),
   ("Themable per tenant with docs", "2026-09-30", "Runtime theming, guidelines, spec mapping, Figma decision")])
p.I("tokens", "Define design tokens (color, type, space, radius, motion, elevation) in DTCG JSON compiled to CSS variables", "Style Dictionary build feeding Tailwind v4 theme.", "P0", 1, "Build", [D], 0, ready=True)
p.I("primitives", "Adopt Base UI/Radix primitives with Tailwind v4 and build 20 core components (Button, Input, Select, Dialog, Menu, Tabs, Toast, Tooltip, Popover...)", "Accessible, themable building blocks with stories and tests.", "P0", 1, "Build", [D], 0, ["tokens", "libraries/ui-landscape"])
p.I("icons-illustrations", "Choose the icon set (Lucide or Phosphor) and illustration style; build a tree-shaken Icon component", "Consistent iconography across all surfaces.", "P0", 3, "Build", [D], 0, ["tokens"])
p.I("storybook", "Set up Storybook with a11y, viewport and interaction-test addons deployed to GitHub Pages", "Living documentation and screenshot target.", "P0", 2, "Infra", [D], 0, ["primitives"])
p.I("layout-components", "Build layout components: AppFrame, SplitPane, Inspector, CommandBar, ResponsiveGrid", "The frames page specs place components into.", "P1", 1, "Build", [D], 1, ["primitives", "app-shell/router-layouts"])
p.I("data-display", "Build data display components: cell renderers, Badge, AvatarStack, Timeline, EmptyState, Skeleton", "Shared visuals for tables, dashboards and feeds.", "P1", 2, "Build", [D], 1, ["primitives"])
p.I("motion", "Define the motion system (durations, easings, reduced-motion) and shared transition components", "Consistent, accessible animation.", "P1", 3, "Build", [C], 1, ["tokens"])
p.I("a11y-audit", "Run axe and manual screen-reader audit on every component and fix to WCAG 2.2 AA", "No component ships below AA.", "P1", 1, "Review", [C], 1, ["primitives", "storybook"])
p.I("component-spec-mapping", "Map every component to a spec-builder component ID with props schema so page specs reference real components", "Bridges design system and codegen.", "P1", 1, "Spec", [D, G], 1, ["primitives", "spec-builder/schema"])
p.I("theming", "Implement light, dark and high-contrast themes plus per-tenant brand theming with runtime token override", "Tenants upload a logo and palette; the whole app rethemes.", "P1", 2, "Build", [C, S], 2, ["tokens"])
p.I("guidelines-docs", "Write design system guidelines (voice, density, spacing, when to use what) into the docs system", "Rules agents follow when specs leave room.", "P2", 2, "Docs", [D], 2, ["storybook", "collab/docs-engine"])
p.I("figma-sync", "Export tokens to Figma variables and document the round-trip, or record the decision to skip Figma", "Decide whether a design tool is in the loop.", "P2", 4, "Research", [D], 2, ["tokens"])

# 6 quality
p = P("quality", "Quality Pipeline", "#EB5757", "CheckCircle",
  "Four automated gates: static checks, three Claude reviewer agents, screenshot and video replay across the breakpoint matrix, and edge-case hunting; weekly release digests for Justin.",
  "Goal: nothing reaches Justin unless machines have already reviewed it several ways. Gate 1 runs typecheck, Biome, Vitest and builds. Gate 2 runs three Claude reviewer agents (correctness, security, spec-conformance) against shared rubrics and posts structured reviews. Gate 3 captures Playwright screenshots and video replays of key flows across seven widths and all themes, diffs them against baselines and has a vision agent annotate layout defects. Gate 4 is an edge-case hunter that derives adversarial scenarios from page specs. Performance budgets, security scans and flake quarantine keep the pipeline trustworthy. A release train produces weekly candidates with a one-page digest into Needs Justin. Non-goal: manual QA as a routine step.",
  "P0", 1, ["app-shell"],
  [("Gates 1 and 2 on every PR", "2026-09-20", "Static checks, reviewer agents, rubrics, security scans, screenshot matrix"),
   ("Visual and video gates", "2026-09-25", "Video replays, vision inspection, edge-case hunter, e2e flows, perf budgets"),
   ("Edge-case hunting and release trains", "2026-09-30", "Release train, review digest, flake quarantine")])
p.I("ci-gate1", "Set up CI gate 1: typecheck, Biome lint, Vitest unit tests and web build on every PR", "The fast gate that runs in under 3 minutes.", "P0", 1, "Infra", [D], 0, ready=True)
p.I("review-rubrics", "Write review rubrics and a severity taxonomy shared by all reviewer agents and humans", "Blocker/major/minor definitions and per-domain checklists.", "P0", 1, "Spec", [G], 0, ready=True)
p.I("security-scans", "Add dependency audit, secret scanning, Semgrep SAST and container scanning to CI", "Catch leaked keys and vulnerable packages before review.", "P0", 2, "Infra", [D], 0, ["ci-gate1"])
p.I("review-agents", "Build gate 2: three Claude reviewer agents (correctness, security, spec-conformance) posting structured PR reviews", "Agents review every PR against the rubrics and block on blockers.", "P0", 1, "Build", [G, D], 0, ["ci-gate1", "review-rubrics"])
p.I("playwright-matrix", "Build gate 3: Playwright screenshot suite across the 7-width breakpoint matrix, all themes and key pages with baseline diffs", "Visual regression on every PR.", "P0", 1, "Build", [D], 0, ["ci-gate1", "app-shell/device-matrix-research"])
p.I("video-replays", "Record video replays of critical flows per PR at each responsive size and attach them to the PR", "Reviewers and Justin watch, not read.", "P1", 2, "Build", [D], 1, ["playwright-matrix"])
p.I("screenshot-annotation", "Have a vision agent inspect screenshots for overflow, misalignment, contrast and truncation and post annotated findings", "Turns pixels into review comments.", "P1", 1, "Build", [G], 1, ["playwright-matrix"])
p.I("edge-case-hunter", "Build gate 4: edge-case hunter agent generating adversarial inputs, empty/huge/unicode states, network failure and slow-device scenarios from page specs", "Finds what happy-path tests miss.", "P1", 1, "Build", [G], 1, ["spec-builder/schema", "review-agents"])
p.I("e2e-flows", "Write end-to-end flow tests for auth, tenant switch, CRUD and realtime presence", "Smoke coverage for the core platform.", "P1", 2, "Build", [D], 1, ["identity/org-tenancy"])
p.I("perf-budgets", "Enforce performance budgets (LCP, INP, bundle size) with Lighthouse CI", "Regressions in speed fail the PR.", "P1", 2, "Infra", [D], 1, ["ci-gate1"])
p.I("release-train", "Define the release train: nightly staging deploy, weekly release candidate to Needs Justin with consolidated review report", "Justin reviews releases, not PRs.", "P1", 1, "Spec", [D, G], 2, ["review-agents", "playwright-matrix"])
p.I("review-report", "Generate a one-page human review digest per release candidate: what changed, risks, screenshots, open questions", "The single artifact Justin reads.", "P1", 1, "Build", [S, G], 2, ["release-train"])
p.I("flake-quarantine", "Build flaky-test detection and quarantine so agents are not blocked by nondeterminism", "Retries, flake scoring, auto-quarantine with an issue.", "P2", 3, "Build", [D], 2, ["e2e-flows"])

# 7 pm-linear
p = P("pm-linear", "Project Management & Claude Pipeline", "#5E6AD2", "Kanban",
  "Linear configured as the agent queue, an orchestrator that turns Ready for Claude issues into sessions and PRs, and a thin PM module that syncs with Linear.",
  "Goal: Linear becomes the queue many parallel Claude Code sessions build from, and Justin's own queue stays tiny. We add the pipeline states, label groups and project templates to team PAP, define an issue contract enforced by a webhook validator, and build an orchestrator that claims issues, spawns sessions in git worktrees, posts PR status and screenshots back, and meters credit spend. Concurrency controls respect dependencies and file-lock hints. Inside PaperOS a PM data model mirrors Linear and a bidirectional sync keeps both in step, with boards rendered by the views engine. Non-goal: replacing Linear before Oct 1; the sync preserves the option. PAP-5 is decomposed into this plan and closed.",
  "P0", 1, [],
  [("Linear configured for the pipeline", "2026-09-18", "States, labels, projects, issue contract, Justin queue design, playbook"),
   ("Orchestrator claims and ships issues", "2026-09-22", "Sessions spawn from Linear, webhooks round-trip, credits metered"),
   ("PM module syncs both ways", "2026-09-30", "PM entities, Linear sync, board views")])
p.I("configure-workspace", "Add pipeline states (Ready for Claude, In Review, Needs Justin), label groups and project templates to Linear team PAP", "The Linear setup this plan assumes.", "P0", 1, "Infra", [G], 0, ready=True)
p.I("session-playbook", "Write the session playbook: how a Claude session picks up an issue, what it must read, how it reports and ends", "The contract every character follows.", "P0", 1, "Docs", [G], 0, ready=True)
p.I("issue-contract", "Define the issue contract (spec link, acceptance criteria, surfaces, definition of done) enforced by a Linear webhook validator", "Issues cannot enter Ready for Claude without it.", "P0", 1, "Spec", [G], 0, ["configure-workspace"])
p.I("justin-queue", "Design the Needs Justin queue: batched decisions, one-click approve/reject comments, max five open items rule", "Protects the single human reviewer.", "P0", 1, "Spec", [S], 0, ["configure-workspace"])
p.I("pap5-decompose", "Decompose PAP-5 (startup procedure inefficiency) into this master plan's projects and close it with a summary comment", "Links the origin issue to the plan.", "P0", 2, "Docs", [G], 0, ["configure-workspace"])
p.I("orchestrator", "Build the orchestrator that polls Ready for Claude, spawns one Claude Code session per issue in a git worktree and moves states", "The engine that turns Linear into running agents.", "P0", 1, "Build", [G], 1, ["configure-workspace", "forge/branch-policy", "session-playbook"])
p.I("webhooks", "Set up Linear webhooks into the orchestrator and PR status back to Linear as comments with screenshots and review verdicts", "Two-way visibility without opening GitHub.", "P0", 1, "Build", [G], 1, ["orchestrator"])
p.I("credit-metering", "Track Claude credit spend per issue and project and post a daily burn report to Linear", "Keeps the $10K on plan.", "P0", 2, "Build", [G], 1, ["orchestrator"])
p.I("concurrency", "Implement concurrency controls: max parallel sessions, file-lock hints and dependency-aware scheduling from dependsOn", "Avoid merge storms and blocked work.", "P1", 1, "Build", [G], 1, ["orchestrator"])
p.I("pm-data-model", "Model PM entities in PaperOS (project, issue, cycle, milestone, comment, label) mirroring Linear's schema", "The thin PM layer's tables.", "P1", 2, "Spec", [S, D], 2, ["data-layer/core-entities"])
p.I("linear-sync", "Build bidirectional Linear sync (GraphQL + webhooks) with conflict rule: Linear wins until cutover", "Same issues visible in both tools.", "P2", 2, "Build", [S], 2, ["pm-data-model", "webhooks"])
p.I("board-views", "Render PM board, list and timeline views using the tables/views engine", "Project management inside the product.", "P2", 2, "Build", [S], 2, ["pm-data-model", "tables/kanban-view"])

# 8 agents
p = P("agents", "Agent Characters & Orgs", "#F7C8E0", "Bot",
  "The character roster: lead agents with sub-characters, each with explicit tools, access, plugins, skills, memory, budgets and handoff rules, visible as an org chart in-app.",
  "Goal: the people building PaperOS are Claude characters, and they must be as legible as human staff. A character schema defines name, role, reportsTo, tools, MCP servers, access scopes, plugins, skills, memory and escalation rules. Nine leads and their sub-characters are installed as .claude/agents definitions with a shared skills library. Per-character MCP allowlists and permission modes are verified for least privilege. Persistent memory, a handoff protocol, an eval harness with golden tasks, budgets with a kill switch and prompt logging make the org safe to run unattended. An org chart UI shows who is doing what with which access. Non-goal: autonomous hiring of new characters without a Needs Justin approval.",
  "P0", 1, ["pm-linear"],
  [("Roster defined and installed", "2026-09-20", "Schema, nine leads with sub-characters, skills library, tool scopes, logging hook"),
   ("Sub-agents, skills and evals live", "2026-09-25", "Memory, handoffs, eval harness, cost controls, handbook"),
   ("Agent org visible in app", "2026-09-30", "Org chart UI with live tasks and access")])
p.I("character-schema", "Define the character schema: name, role, reportsTo, tools, MCP servers, access scopes, plugins, skills, memory, escalation rules", "The typed shape of an agent.", "P0", 1, "Spec", [G], 0, ready=True)
p.I("roster-v1", "Write the nine lead characters and their sub-characters as .claude/agents definitions with system prompts", "Atlas, Forge, Iris, Quill, Sentinel, Nova, Ledger, Beacon, Scout.", "P0", 1, "Build", [G], 0, ["character-schema"])
p.I("skills-library", "Build the shared skills library (page-from-spec, review-pr, screenshot-audit, write-adr, linear-update) as .claude/skills", "Reusable procedures every character can invoke.", "P0", 1, "Build", [G], 0, ["character-schema"])
p.I("tool-scopes", "Implement per-character MCP allowlists and permission modes and verify least privilege with an automated test", "No character can do more than its schema says.", "P0", 1, "Build", [G], 0, ["roster-v1", "forge/bot-accounts"])
p.I("prompt-logging-hook", "Hook every session's prompts, responses and tool calls into the prompt-log store", "Complete record of how the product was built.", "P0", 1, "Build", [G], 0, ["collab/prompt-log-store"])
p.I("handoffs", "Design the handoff protocol between characters: artifact contract, Linear comment format, escalation to Needs Justin", "Clean baton passes between sessions.", "P1", 1, "Spec", [G], 1, ["roster-v1"])
p.I("memory", "Give characters persistent memory (project notes, decisions, gotchas) stored in the docs system and loaded at session start", "Characters stop repeating mistakes.", "P1", 2, "Build", [G], 1, ["roster-v1", "collab/docs-engine"])
p.I("eval-harness", "Create an eval harness with golden tasks per character, scored nightly, regressions flagged in Linear", "Quality of the agents themselves is measured.", "P1", 1, "Review", [G], 1, ["roster-v1", "skills-library"])
p.I("cost-controls", "Add per-character budgets, max-turn limits and a kill switch", "Spend is bounded per character and per issue.", "P1", 2, "Build", [G], 1, ["pm-linear/credit-metering"])
p.I("character-docs", "Publish the character handbook: who does what, how to summon them, what they may not do", "Reference for Justin and future humans.", "P1", 2, "Docs", [G, S], 1, ["roster-v1"])
p.I("org-chart-ui", "Build the agent org chart UI showing characters, sub-agents, current tasks, tools and access", "The agent org as a first-class page.", "P2", 2, "Build", [S, G], 2, ["roster-v1", "collab/canvas-view"])

# 9 spec-builder
p = P("spec-builder", "Spec Builder", "#9B51E0", "FileText",
  "A page.spec.yaml schema describing logic, access, data, integrations, layout, components and edge cases, with a validator, codegen, conformance tests and an editor UI.",
  "Goal: every page in every app is specified before it is built, and the spec drives code, tests and diagrams. The schema captures purpose, logic, access rules, data queries and mutations, integrations, layout, component tree, states, events and edge cases; an app.spec.yaml holds shared audiences, navigation and entities. A validator CLI and CI check block unspecified pages. Codegen scaffolds layouts and typed data hooks from specs; conformance and permission tests are derived automatically; the canvas view is generated from spec transitions. A spec editor UI with form and YAML views lets Justin and agents edit specs in-app, and an authoring skill lets agents interview and draft specs. Non-goal: a full visual app builder.",
  "P1", 1, ["design-system", "data-layer"],
  [("Spec schema and validator", "2026-09-22", "Schema, validator, access and app-level spec, authoring skill"),
   ("Codegen and conformance tests", "2026-09-26", "Data hooks, layout codegen, integrations registry, conformance tests, canvas emit"),
   ("Spec editor UI", "2026-09-30", "In-app editor and worked examples")])
p.I("schema", "Define the page.spec.yaml schema: purpose, logic, access, data, integrations, layout, components, states, events, edge cases", "JSON Schema plus TypeScript types.", "P0", 1, "Spec", [D, G], 0, ready=True)
p.I("validator", "Build the spec validator CLI and CI check that fails PRs whose pages lack or violate specs", "Specs become mandatory.", "P0", 1, "Build", [D], 0, ["schema"])
p.I("access-section", "Specify the access section format that compiles to permission-engine policies", "Who can see and do what, per page, machine-readable.", "P0", 1, "Spec", [D], 0, ["schema"])
p.I("app-level-spec", "Define app.spec.yaml (audiences, navigation, entities, integrations) that page specs inherit from", "App-wide context so page specs stay short.", "P1", 1, "Spec", [D], 0, ["schema"])
p.I("spec-authoring-skill", "Write the agent skill: interview -> draft page spec -> validate -> open Linear issue", "How specs get written at scale.", "P1", 1, "Build", [G], 0, ["validator", "agents/skills-library"])
p.I("data-section", "Specify the data section (entities, queries, mutations, sync mode) and generate typed hooks from it", "Pages declare data; hooks are generated.", "P1", 1, "Build", [D], 1, ["schema", "data-layer/api-layer"])
p.I("layout-codegen", "Generate page scaffolds (layout, component tree, loading/empty/error states) from specs", "Spec in, working page skeleton out.", "P1", 1, "Build", [D], 1, ["schema", "design-system/component-spec-mapping"])
p.I("integrations-section", "Specify the integrations section (Stripe, Linear, Notion, Drive, Webflow, Miro, Gamma) backed by a connector registry", "Pages declare which external systems they touch.", "P1", 2, "Spec", [D], 1, ["schema", "libraries/mcp-servers"])
p.I("conformance-tests", "Generate conformance tests from specs (access matrix, required components, states) into CI gate 1", "Spec drift fails the build.", "P1", 1, "Build", [D], 1, ["validator", "quality/ci-gate1"])
p.I("spec-to-canvas", "Emit the UX-flow graph (pages, transitions, roles) from specs for the canvas view", "Specs draw the map of the app.", "P1", 2, "Build", [D], 1, ["schema", "collab/canvas-view"])
p.I("spec-editor-ui", "Build the spec editor UI with form and YAML views and live preview", "Edit specs in-app without touching files.", "P2", 2, "Build", [D, S], 2, ["schema", "design-system/layout-components"])
p.I("spec-docs", "Document the spec builder with three fully specified example pages (customer list, staff dashboard, agent console)", "Worked examples agents copy.", "P1", 2, "Docs", [D], 2, ["validator"])

# 10 collab
p = P("collab", "In-App Collaboration & Knowledge", "#56CCF2", "MessageSquare",
  "Comments anchored anywhere, a canvas UX-flow view, an in-app docs engine, changelogs, a prompt/response log and browsable rules and skills.",
  "Goal: the product contains its own documentation, discussion and memory. A docs engine renders repo-stored MDX in-app with search and git versioning. A prompt-log store records every agent session (prompts, responses, tool calls, tokens, cost) with redaction, and a browser lets Justin replay any session and jump to its PR. Comments anchor to entities, page elements, doc blocks and screenshots and can spawn Linear issues. The canvas view shows the UX flow of the whole app generated from specs and editable in realtime. Changelogs are generated per app and per tenant; rules and skills are browsable and versioned objects. A decision log holds ADRs. Non-goal: replacing Notion for external documents; the docs engine can import from it.",
  "P1", 1, ["realtime", "data-layer"],
  [("Docs and prompt log stores", "2026-09-21", "Docs engine, prompt-log store, decision log, canvas/editor research"),
   ("Comments and canvas", "2026-09-26", "Comments, canvas view, changelog, rules/skills registry, prompt log UI"),
   ("Knowledge surfaced everywhere", "2026-09-30", "Notifications, screenshot annotations, unified search")])
p.I("collab-research", "Evaluate tldraw vs React Flow for the canvas and Tiptap vs BlockNote for docs; write ADR", "Pick the canvas and editor foundations.", "P0", 2, "Research", [D], 0, ready=True)
p.I("docs-engine", "Build the docs engine: MDX docs stored in the repo, rendered in-app, searchable and versioned with git", "Documentation lives in the product.", "P0", 1, "Build", [D, S], 0, ["app-shell/router-layouts"])
p.I("prompt-log-store", "Create the prompt/response log store (session, character, issue, tokens, cost, tool calls) with redaction", "The system of record for how agents built the product.", "P0", 1, "Build", [G], 0, ["data-layer/core-entities"])
p.I("decision-log", "Add an ADR/decision log with status, alternatives and links to issues", "Every big choice is recorded and findable.", "P0", 2, "Build", [D], 0, ["docs-engine"])
p.I("comments", "Implement in-app comments anchored to any entity, page element or doc block with mentions and resolve", "Discussion lives next to the thing.", "P1", 1, "Build", [C, S], 1, ["realtime/yjs-server", "identity/rbac-abac"])
p.I("canvas-view", "Build the canvas view (tldraw or React Flow) showing the UX flow of the whole app, generated from specs and editable", "The map of the system.", "P1", 1, "Build", [S, D], 1, ["spec-builder/schema", "realtime/yjs-server", "collab-research"])
p.I("changelog", "Auto-generate changelogs from conventional commits and PR summaries, rendered per app and per tenant", "Users and staff see what changed.", "P1", 2, "Build", [C, S], 1, ["forge/branch-policy"])
p.I("rules-skills-registry", "Surface rules (CLAUDE.md, policies) and skills as browsable, editable objects in-app with version history", "Rules and skills are product objects.", "P1", 2, "Build", [G, D], 1, ["docs-engine", "agents/skills-library"])
p.I("prompt-log-ui", "Build the prompt log browser: filter by issue or character, replay a session, link to the PR", "Justin can audit any agent decision.", "P1", 2, "Build", [S, G], 1, ["prompt-log-store", "tables/grid-view"])
p.I("notifications", "Build a notification center (in-app, email, Slack) with per-audience preferences", "Mentions and changes reach people where they are.", "P2", 2, "Build", [C, S], 2, ["comments"])
p.I("screenshot-annotations", "Allow annotating screenshots and video frames with comments that create Linear issues", "Bugs go from picture to ticket in one step.", "P2", 3, "Build", [S], 2, ["comments", "quality/video-replays"])
p.I("knowledge-search", "Unify search across docs, comments, specs, prompt logs and issues", "One search box for all knowledge.", "P2", 2, "Build", [S], 2, ["data-layer/search", "docs-engine"])

# 11 realtime
p = P("realtime", "Multiplayer & Realtime", "#26B5CE", "Users",
  "Yjs via Hocuspocus for documents, presence and multi-window sync; Electric shapes for live records; conflict and offline UX.",
  "Goal: every PaperOS app is multiplayer by default, for humans and agents. A self-hosted Hocuspocus server persists Yjs documents to Postgres with auth hooks, powering collaborative rich text, canvas and presence (cursors, avatars, selections, who is viewing). Record changes stream through Electric shapes and reconcile with local writes; a conflict UX handles stale data and merges. State syncs across multiple OS windows and tabs, agents appear as live participants, and follow mode supports support and pair review. Load tests and an offline write queue harden it. Non-goal: a custom CRDT or peer-to-peer transport.",
  "P1", 1, ["identity", "data-layer"],
  [("Yjs server and presence", "2026-09-22", "Hocuspocus deployed, CRDT ADR, presence, collaborative text"),
   ("Record sync and conflict UX", "2026-09-26", "Electric record streaming, conflict UX, multi-window sync"),
   ("Scale and offline tested", "2026-09-30", "Agent presence, load test, offline queue, follow mode")])
p.I("realtime-research", "Benchmark Yjs vs Automerge vs Loro for document CRDT and write an ADR", "Confirms the CRDT choice with numbers.", "P0", 2, "Research", [D], 0, ready=True)
p.I("yjs-server", "Deploy a Hocuspocus (Yjs) server with auth hook, Postgres persistence and room-per-document", "The multiplayer backbone.", "P0", 1, "Infra", [D], 0, ["identity/better-auth"])
p.I("presence", "Build the presence layer: cursors, avatars, selections and 'who is viewing' across pages", "See who is here, everywhere.", "P1", 1, "Build", [C, S], 0, ["yjs-server"])
p.I("collab-text", "Add collaborative rich text (Tiptap + Yjs) as the shared editor for docs and comments", "One editor everywhere.", "P1", 1, "Build", [C, S], 0, ["yjs-server", "collab/collab-research"])
p.I("record-sync", "Stream record changes via Electric shapes to all connected clients and reconcile with local writes", "Tables and lists update live.", "P1", 1, "Build", [D], 1, ["data-layer/local-first-sync"])
p.I("conflict-ux", "Design conflict and stale-data UX: merge banners, last-writer indicators, undo", "Users understand what happened when edits collide.", "P1", 2, "Spec", [C, S], 1, ["record-sync"])
p.I("multi-window-sync", "Sync state across multiple OS windows and tabs of the same user via BroadcastChannel and Yjs", "Multi-monitor setups stay coherent.", "P1", 2, "Build", [S], 1, ["yjs-server", "app-shell/breakpoints-windows"])
p.I("agent-presence", "Show agents as live participants (typing, editing, reviewing) with distinct visual identity", "Agents are visible collaborators.", "P2", 2, "Build", [G, S], 2, ["presence", "identity/agent-principals"])
p.I("load-test", "Load test 500 concurrent users per room and 10k rooms; tune persistence and scaling", "Know the limits before customers do.", "P2", 2, "Review", [D], 2, ["yjs-server"])
p.I("offline-queue", "Implement the offline write queue with retry, ordering and user-visible sync status", "Work continues without a connection.", "P2", 2, "Build", [C], 2, ["record-sync"])
p.I("followmode", "Add follow mode and shared cursor sessions for support and pair review", "Support can guide a customer live.", "P2", 3, "Build", [S], 2, ["presence"])

# 12 input
p = P("input", "Multi-Input Control & Accessibility", "#F2C94C", "Keyboard",
  "Keyboard, mouse, touch, pen, gamepad and voice through one command registry and input abstraction, with focus management and screen-reader conformance.",
  "Goal: every app is controllable by every input method and usable by every person. A global command registry powers keyboard shortcuts, a command palette and per-page scoping, with user-customizable keymaps. A unified input abstraction lets components handle mouse, touch, pen and gamepad uniformly; touch gestures and haptics work on mobile, pen pressure on the canvas, spatial focus for TV and kiosk. Voice commands and dictation route through the same registry. Focus management, accessible drag-and-drop and screen-reader testing across NVDA, VoiceOver and TalkBack complete it, with an accessibility statement per app. Non-goal: eye tracking or BCI in this build.",
  "P1", 2, ["design-system"],
  [("Keyboard and command system", "2026-09-23", "Command registry, input abstraction, focus management"),
   ("Touch, pen, gamepad", "2026-09-27", "Keymaps, touch gestures, drag-and-drop, screen reader fixes"),
   ("Voice and accessibility certification", "2026-09-30", "Voice, pen, gamepad, accessibility statement")])
p.I("input-abstraction", "Design a unified input event abstraction so components handle mouse, touch, pen and gamepad uniformly", "One pointer/press model across devices.", "P0", 2, "Spec", [D], 0, ready=True)
p.I("command-registry", "Build the global command registry with keyboard shortcuts, command palette and per-page scoping", "Everything is a command; commands are discoverable.", "P0", 1, "Build", [C, S], 0, ["design-system/primitives"])
p.I("focus-management", "Implement robust focus management, roving tabindex and skip links across all layouts", "Keyboard users never get lost.", "P1", 1, "Build", [C], 0, ["design-system/layout-components"])
p.I("keymaps", "Support user-customizable keymaps with presets (default, Vim-style, Linear-like) synced per user", "Power users bring their habits.", "P1", 2, "Build", [S], 1, ["command-registry"])
p.I("touch-gestures", "Implement a touch gesture system (swipe, pinch, long-press) with haptics on mobile targets", "Mobile feels native.", "P1", 2, "Build", [C], 1, ["app-shell/tauri-mobile", "input-abstraction"])
p.I("drag-drop", "Build accessible drag-and-drop (dnd-kit) for tables, kanban and canvas with a keyboard alternative", "Reordering works for everyone.", "P1", 2, "Build", [C, S], 1, ["input-abstraction"])
p.I("screen-reader", "Test and fix the screen reader experience (NVDA, VoiceOver, TalkBack) for core flows", "Real assistive tech, not just axe.", "P1", 1, "Review", [C], 1, ["focus-management"])
p.I("pen", "Support pen and stylus input with pressure for canvas and annotation", "Sketch and mark up on tablets.", "P2", 3, "Build", [S], 2, ["collab/canvas-view", "input-abstraction"])
p.I("gamepad", "Add gamepad and TV-remote navigation for kiosk and TV modes with spatial focus", "10-foot UI works.", "P2", 3, "Build", [C], 2, ["focus-management"])
p.I("voice", "Integrate voice commands and dictation (Web Speech with Whisper fallback) routed through the command registry", "Talk to the app.", "P2", 2, "Build", [C, S], 2, ["command-registry"])
p.I("a11y-statement", "Publish an accessibility statement and conformance report template per app", "Compliance evidence out of the box.", "P2", 3, "Docs", [C], 2, ["screen-reader"])

# 13 tables
p = P("tables", "Table & Views Engine", "#4CB782", "Table",
  "A view model that is a superset of Airtable, Notion and ClickUp views, compiled to SQL, with grid, kanban, calendar, timeline, Gantt, gallery, list, form, map and chart views, rich field types and formulas.",
  "Goal: any dataset in any app can be viewed, sorted, filtered, grouped and edited as well as in Airtable, Notion or ClickUp, and those views compose into dashboards. A view model spec defines data source, fields, filters, sorts, groups, aggregations, permissions and sharing; a query compiler turns it into SQL and Electric shapes with server-side pagination. Views include a virtualized editable grid, kanban with swimlanes, calendar/timeline/Gantt, gallery/list/form, map and chart. Field types cover text through relations, lookups, rollups and formulas with a formula engine. Saved, shared and public views plus dashboard blocks with cross-filters complete it. A parity audit against Airtable, Notion, ClickUp, Baserow and NocoDB tracks coverage. Non-goal: a spreadsheet grid with arbitrary cell formulas.",
  "P1", 1, ["data-layer", "design-system", "input"],
  [("Grid with sort, filter, group", "2026-09-23", "View model, parity audit, query compiler, field types, grid, filter UI"),
   ("All view types", "2026-09-27", "Kanban, calendar/timeline/Gantt, gallery/list/form, map/chart"),
   ("View sharing, formulas, dashboards", "2026-09-30", "Formula engine, saved and public views, dashboard blocks")])
p.I("view-model-spec", "Specify the view model: data source, fields, filters, sorts, groups, aggregations, permissions and sharing as a superset of Airtable, Notion and ClickUp", "The schema all views render from.", "P0", 1, "Spec", [S, D], 0, ready=True)
p.I("feature-parity-audit", "Audit Airtable, Notion, ClickUp, Baserow and NocoDB view features into a parity checklist", "Know exactly what 'every feature' means.", "P0", 2, "Research", [S], 0, ready=True)
p.I("query-compiler", "Build the view query compiler from view model to SQL and Electric shapes with server-side pagination", "Views become efficient queries.", "P1", 1, "Build", [D], 0, ["view-model-spec", "data-layer/api-layer"])
p.I("field-types", "Implement field types: text, number, currency, date, select, multi-select, relation, lookup, rollup, formula, attachment, user, checkbox, rating, URL, email, phone", "Rich cells with validation and renderers.", "P1", 1, "Build", [D], 0, ["view-model-spec"])
p.I("grid-view", "Build the virtualized grid view (TanStack Table) with inline edit, column resize/reorder, freeze and cell types", "The workhorse view.", "P1", 1, "Build", [C, S], 0, ["query-compiler", "field-types", "design-system/data-display"])
p.I("filter-sort-group-ui", "Build the filter builder (AND/OR groups), multi-sort and multi-level grouping UI with aggregates", "Airtable-class controls.", "P1", 1, "Build", [S], 0, ["grid-view"])
p.I("kanban-view", "Build the kanban board view with swimlanes, WIP limits and drag-and-drop", "Boards for any entity.", "P1", 1, "Build", [S], 1, ["query-compiler", "input/drag-drop"])
p.I("calendar-timeline-gantt", "Build calendar, timeline and Gantt views with dependencies", "Time-based views for scheduling.", "P1", 2, "Build", [S], 1, ["query-compiler"])
p.I("gallery-list-form", "Build gallery, list and form views", "Card, feed and data-entry presentations.", "P1", 2, "Build", [C, S], 1, ["query-compiler"])
p.I("map-chart-views", "Build map view and chart view (bar, line, pie, number) bound to view aggregations", "Geo and analytics views.", "P2", 2, "Build", [S], 1, ["query-compiler"])
p.I("formula-engine", "Build a formula engine compatible with common Airtable and Notion functions", "Computed fields users already know.", "P2", 2, "Build", [D], 2, ["field-types"])
p.I("view-sharing", "Add saved views, personal vs shared views, public embeds and per-audience defaults", "Views are permissioned objects.", "P2", 2, "Build", [C, S], 2, ["grid-view", "identity/rbac-abac"])
p.I("dashboard-blocks", "Compose views into dashboard pages with drag-arranged blocks and cross-filters", "Incredible ways to view data, on one page.", "P2", 2, "Build", [S], 2, ["map-chart-views", "grid-view", "input/drag-drop"])

# 14 business-core
p = P("business-core", "Business Core: Payments, Finance & Payroll", "#219653", "DollarSign",
  "Stripe Billing, Connect and Tax for money movement, a double-entry ledger we own, invoicing and finance reports, and a payroll provider adapter.",
  "Goal: every business built on PaperOS can take payments, keep books and run payroll from day one. Stripe Billing handles plans, subscriptions and the customer portal; Connect lets tenants accept payments and receive payouts; Stripe Tax handles sales tax. A double-entry ledger in Postgres is the finance primitive we own, feeding invoices, quotes, receipts, P&L, balance sheet, cash flow and aging reports rendered by the views engine. Payroll sits behind a provider interface with Check or Gusto Embedded as the first adapter. Plan entitlements are enforced by the permission engine. Non-goals: being a payment processor or a payroll provider ourselves.",
  "P2", 1, ["identity", "tables"],
  [("Stripe billing live", "2026-09-27", "Finance data model, payroll ADR, Stripe Billing, entitlements"),
   ("Ledger and reports", "2026-09-29", "Ledger, invoicing, Connect, Tax, finance reports"),
   ("Payroll adapter and cash dashboard", "2026-10-01", "Payroll adapter, expenses, cash-flow dashboard")])
p.I("finance-data-model", "Specify the finance data model: customers, vendors, employees, accounts, transactions and periods across all business types", "The entities payments, ledger and payroll share.", "P1", 1, "Spec", [S], 0, ["data-layer/core-entities"])
p.I("payroll-research", "Research payroll APIs (Check, Gusto Embedded, Deel, Rippling) for embeddability and pricing; write ADR", "Choose the first payroll provider.", "P1", 2, "Research", [S], 0)
p.I("stripe-billing", "Integrate Stripe Billing: products, prices, subscriptions, customer portal and webhooks", "Charge customers for plans.", "P1", 1, "Build", [C], 0, ["identity/org-tenancy", "finance-data-model"])
p.I("entitlements", "Map plans to feature entitlements enforced by the permission engine", "Paid features gate themselves.", "P2", 1, "Build", [C, D], 0, ["stripe-billing", "identity/rbac-abac"])
p.I("ledger", "Build a double-entry ledger (accounts, journal entries, periods) in Postgres with immutability guarantees", "The finance primitive we own.", "P2", 1, "Build", [S], 1, ["finance-data-model"])
p.I("invoicing", "Implement invoices, quotes and receipts with PDF generation and Stripe payment links", "Bill anyone for anything.", "P2", 2, "Build", [C, S], 1, ["stripe-billing", "ledger"])
p.I("stripe-connect", "Add Stripe Connect so tenants can accept payments and receive payouts", "Marketplace-ready money movement.", "P2", 2, "Build", [C, S], 1, ["stripe-billing"])
p.I("tax-compliance", "Handle sales tax and VAT via Stripe Tax and store tax evidence", "Compliance without spreadsheets.", "P2", 3, "Build", [S], 1, ["stripe-billing"])
p.I("finance-reports", "Generate P&L, balance sheet, cash flow and AR/AP aging as table views", "Books you can read.", "P2", 2, "Build", [S], 1, ["ledger", "tables/grid-view"])
p.I("payroll-adapter", "Define the payroll provider interface and implement the first adapter (Check or Gusto Embedded)", "Run payroll from inside the app.", "P2", 2, "Build", [S], 2, ["ledger", "payroll-research"])
p.I("expense-capture", "Add expense capture with receipt OCR and ledger posting", "Receipts become journal entries.", "P2", 3, "Build", [S], 2, ["ledger", "data-layer/file-storage"])
p.I("cash-dashboard", "Build the cash-flow dashboard (in, out, runway, upcoming payroll) as the first dashboard-blocks consumer", "The founder's one screen.", "P2", 2, "Build", [S], 2, ["finance-reports", "tables/dashboard-blocks"])

# 15 growth
p = P("growth", "Growth: Marketing, Outreach & CRM", "#EB5757", "Megaphone",
  "A CRM on the tables engine, social scheduling, outreach sequences, landing pages via Webflow, attribution and a support inbox, with a content agent drafting for approval.",
  "Goal: every business gets customer acquisition machinery, not just an app. CRM entities (lead, contact, company, deal, activity, segment) live on the tables engine with pipeline and contact views. A social scheduler with platform adapters and an approval queue, outreach sequences over email and SMS with reply detection, Webflow-published landing pages capturing forms, and a privacy-first attribution pipeline cover acquisition. Segments from CRM plus product usage drive campaigns and in-app targeting; a referral program pays out through Stripe Connect; a support inbox links conversations to contacts. A content agent drafts posts and emails from changelogs and specs for human approval. Non-goal: sending anything without approval in this build.",
  "P2", 2, ["tables", "business-core"],
  [("CRM core", "2026-09-28", "CRM model, OSS research, pipeline and contact views"),
   ("Campaigns and social", "2026-09-30", "Social scheduler, outreach sequences, content agent, landing forms"),
   ("Acquisition analytics", "2026-10-01", "Attribution, segments, referrals, support inbox")])
p.I("crm-model", "Model CRM entities: lead, contact, company, deal, pipeline stage, activity, segment", "The customer graph.", "P1", 2, "Spec", [S], 0, ["data-layer/core-entities"])
p.I("growth-research", "Survey open-source CRM and marketing stacks (Twenty, Postiz, Listmonk, Dub) for reuse vs build; write ADR", "Borrow what exists.", "P1", 2, "Research", [S], 0)
p.I("crm-views", "Build CRM pipeline (kanban), contact list and company views on the tables engine", "Sales workflow out of the box.", "P2", 2, "Build", [S], 0, ["crm-model", "tables/kanban-view"])
p.I("social-scheduler", "Build a social media scheduler with adapters (X, LinkedIn, Instagram, TikTok, YouTube) and an approval queue", "Post everywhere from one place.", "P2", 2, "Build", [S], 1, ["crm-model", "growth-research"])
p.I("outreach-sequences", "Build email and SMS outreach sequences (Resend, Twilio) with warmup and reply detection", "Automated, compliant outreach.", "P2", 2, "Build", [S], 1, ["crm-model"])
p.I("content-agent", "Create the content agent character that drafts posts and emails from changelogs and specs for human approval", "Marketing that writes itself, approved by humans.", "P2", 2, "Build", [G], 1, ["social-scheduler", "agents/roster-v1"])
p.I("landing-forms", "Publish landing pages via the Webflow API and capture forms into the CRM", "Pages to leads in one flow.", "P2", 3, "Build", [C], 1, ["crm-model"])
p.I("attribution", "Track acquisition analytics (UTM, referral, funnel) with a privacy-first event pipeline", "Know what works.", "P2", 3, "Build", [S], 2, ["crm-model"])
p.I("segments", "Build audience segments from CRM and product usage that feed campaigns and in-app targeting", "Right message, right people.", "P2", 3, "Build", [S], 2, ["crm-model", "tables/filter-sort-group-ui"])
p.I("referral-program", "Implement a referral and affiliate program with Stripe Connect payouts", "Customers recruit customers.", "P2", 4, "Build", [C], 2, ["business-core/stripe-connect"])
p.I("support-inbox", "Build a shared support inbox (email and in-app chat) linked to CRM contacts", "Support conversations in context.", "P2", 3, "Build", [S], 2, ["crm-model", "collab/comments"])

# 16 migration
p = P("migration", "Migration & Import Tools", "#F2994A", "Download",
  "An import framework with schema mapping, dry runs and rollback; importers for CSV, Airtable, Notion, ClickUp, Linear, Stripe and QuickBooks; full export; business templates.",
  "Goal: any business can move into a PaperOS app without losing data or lock-in. The import framework provides source connectors, a schema-mapping UI, dry runs, validation, rollback and persistent external-ID mappings for incremental re-sync. Importers cover spreadsheets, Airtable bases, Notion databases and pages, ClickUp and Linear workspaces, Stripe customers and QuickBooks/Xero charts of accounts. Full export to open formats guarantees no lock-in. Business-type seed packs (agency, retail, SaaS, clinic, restaurant) make a new app useful in minutes, and a migration agent interviews users and runs the imports. Non-goal: live two-way sync with every source.",
  "P2", 2, ["tables", "collab"],
  [("Import framework and CSV", "2026-09-28", "Format research, framework, CSV/Excel, ID mapping"),
   ("Airtable, Notion, ClickUp importers", "2026-09-30", "Table and PM importers, export"),
   ("Business migrations", "2026-10-01", "Stripe/QuickBooks import, templates, migration agent")])
p.I("format-research", "Catalog export formats and API limits of Airtable, Notion, ClickUp, Monday, HubSpot and QuickBooks", "Know what can be pulled and how fast.", "P1", 3, "Research", [S], 0)
p.I("import-framework", "Build the import framework: source connector, schema-mapping UI, dry run, validation, rollback", "One pipeline every importer uses.", "P1", 2, "Build", [S, D], 0, ["tables/field-types"])
p.I("csv-excel", "Import CSV, Excel and Google Sheets with type inference", "The universal on-ramp.", "P2", 2, "Build", [C, S], 0, ["import-framework"])
p.I("id-mapping", "Persist external ID mappings for re-sync and incremental imports", "Import twice without duplicates.", "P2", 2, "Build", [D], 0, ["import-framework"])
p.I("airtable", "Import Airtable bases (tables, views, relations, attachments)", "Airtable users move in whole.", "P2", 2, "Build", [S], 1, ["import-framework"])
p.I("notion", "Import Notion databases and pages into tables and docs", "Notion content and data preserved.", "P2", 2, "Build", [S], 1, ["import-framework", "collab/docs-engine"])
p.I("clickup-linear", "Import ClickUp and Linear workspaces into the PM module", "Bring project history along.", "P2", 3, "Build", [S], 1, ["import-framework", "pm-linear/pm-data-model"])
p.I("export", "Export everything (tables, docs, files, ledger) to open formats", "No lock-in, ever.", "P2", 2, "Build", [C], 1, ["import-framework"])
p.I("stripe-quickbooks", "Import Stripe customers and subscriptions and QuickBooks/Xero charts of accounts into the ledger", "Finance history arrives intact.", "P2", 3, "Build", [S], 2, ["import-framework", "business-core/ledger"])
p.I("business-templates", "Ship business-type templates (agency, retail, SaaS, clinic, restaurant) as importable seed packs", "One-size-fits-all adapts on day one.", "P2", 3, "Build", [C, S], 2, ["tables/view-model-spec", "import-framework"])
p.I("migration-agent", "Create the migration agent character that interviews users about current tools and runs the imports", "Migration as a conversation.", "P2", 2, "Build", [G], 2, ["import-framework", "agents/roster-v1"])

# 17 libraries
p = P("libraries", "Library Discovery & Integration", "#9B51E0", "Package",
  "A governed borrow-before-build process: evaluation rubric, landscape surveys, OSS product evaluation, a registry with ADRs, license policy in CI, MCP connector catalog and a Scout routine.",
  "Goal: the platform is assembled from the best existing libraries and products, chosen deliberately and recorded. A rubric (license, maintenance, bundle size, accessibility, TypeScript quality, agent-friendliness) and ADR template govern every adoption. Landscape surveys cover UI kits, data/canvas/editor/chart libraries and backend building blocks; whole OSS products (Twenty, NocoDB, Baserow, Plane, Cal.com, Formbricks, Postiz) are evaluated for embedding or forking. A registry in the docs system tracks adopted, trialing and rejected libraries; a license policy is enforced in CI; MCP servers and connectors are cataloged for agents; Renovate keeps dependencies fresh; a weekly Scout routine scans for new options. Non-goal: adopting anything without an ADR.",
  "P0", 2, [],
  [("Evaluation process", "2026-09-19", "Rubric, license policy, MCP catalog"),
   ("Core adoptions decided", "2026-09-24", "UI, data and backend landscape ADRs, OSS product evaluation"),
   ("Registry live", "2026-09-30", "Registry, Renovate, Scout routine")])
p.I("eval-rubric", "Define the library evaluation rubric (license, maintenance, bundle size, a11y, TS quality, agent-friendliness) and ADR template", "How we decide what to borrow.", "P0", 1, "Spec", [D], 0, ready=True)
p.I("mcp-servers", "Catalog and configure MCP servers and connectors (Linear, GitHub, Stripe, Notion, Drive, Webflow, Miro, Gamma) for agents", "Every integration agents can reach, documented and scoped.", "P0", 1, "Infra", [G], 0, ready=True)
p.I("license-policy", "Set the license policy (allow MIT/Apache/BSD, review AGPL, block SSPL) enforced by a CI license check", "No surprise licenses.", "P0", 2, "Infra", [D], 0, ["eval-rubric"])
p.I("ui-landscape", "Survey UI kits and headless libraries (Base UI, Radix, React Aria, shadcn, Ark) and recommend", "Pick the component foundation.", "P0", 2, "Research", [D], 1, ["eval-rubric"])
p.I("data-landscape", "Survey table, canvas, editor and chart libraries (TanStack, AG Grid, tldraw, Tiptap, ECharts, visx) and recommend", "Pick the data and canvas foundations.", "P0", 2, "Research", [D], 1, ["eval-rubric"])
p.I("backend-landscape", "Survey backend building blocks (Better Auth, Drizzle, Electric, Hocuspocus, Inngest, Resend) and recommend", "Pick the server foundations.", "P0", 2, "Research", [D], 1, ["eval-rubric"])
p.I("oss-products", "Evaluate whole OSS products to embed or fork (Twenty CRM, NocoDB, Baserow, Plane, Cal.com, Formbricks, Postiz)", "Sometimes borrow a product, not a library.", "P1", 2, "Research", [D, S], 1, ["eval-rubric"])
p.I("registry", "Build the library registry in the docs system: adopted, trialing, rejected with reasons and owners", "One place to see what we use and why.", "P1", 2, "Build", [D], 2, ["eval-rubric", "collab/docs-engine"])
p.I("upgrade-bot", "Set up Renovate with grouped upgrades and agent-reviewed changelog summaries", "Dependencies stay current safely.", "P1", 3, "Infra", [D], 2, ["quality/ci-gate1"])
p.I("scout-agent", "Create the Scout character routine: weekly scan for new libraries relevant to open issues", "Discovery never stops.", "P2", 3, "Build", [G], 2, ["registry", "agents/roster-v1"])

plan["projects"] = projects

# ---------------- validation ----------------
errors = []
issue_keys = {}
for pr in projects:
    for i in pr["issues"]:
        if i["key"] in issue_keys: errors.append(f"dup issue {i['key']}")
        issue_keys[i["key"]] = i
proj_keys = {pr["key"] for pr in projects}
for pr in projects:
    for d in pr["dependsOn"]:
        if d not in proj_keys: errors.append(f"project {pr['key']} depends on unknown {d}")
    ms = {m["name"] for m in pr["milestones"]}
    if not (2 <= len(ms) <= 3): errors.append(f"{pr['key']} milestones {len(ms)}")
    if not (8 <= len(pr["issues"]) <= 14): errors.append(f"{pr['key']} has {len(pr['issues'])} issues")
    for i in pr["issues"]:
        if i["milestone"] not in ms: errors.append(f"{i['key']} bad milestone")
        for d in i["dependsOn"]:
            if d not in issue_keys: errors.append(f"{i['key']} depends on unknown {d}")
        if i["readyNow"] and (i["dependsOn"] or i["phase"] != "P0"): errors.append(f"{i['key']} readyNow invalid")
        if i["key"] in i["dependsOn"]: errors.append(f"{i['key']} self-dep")
# cycle check
import functools
state = {}
def visit(k, stack):
    if state.get(k) == 1: errors.append("cycle: " + " -> ".join(stack + [k])); return
    if state.get(k) == 2: return
    state[k] = 1
    for d in issue_keys[k]["dependsOn"]: visit(d, stack + [k])
    state[k] = 2
for k in issue_keys: visit(k, [])
total = len(issue_keys)
ready = sum(1 for i in issue_keys.values() if i["readyNow"])
p0 = sum(1 for i in issue_keys.values() if i["phase"] == "P0")
if not (150 <= total <= 220): errors.append(f"total {total}")
if not (15 <= ready <= 25): errors.append(f"ready {ready}")
if not (14 <= len(projects) <= 18): errors.append(f"projects {len(projects)}")
if sum(b["share_pct"] for b in plan["budget"]) != 100: errors.append("budget != 100")
if not (8 <= len(plan["decisions"]) <= 15): errors.append("decisions count")
if not (6 <= len(plan["agents"]) <= 9): errors.append("agents count")
if errors:
    print("\n".join(errors)); sys.exit(1)
with open(OUT, "w") as f: json.dump(plan, f, indent=2, ensure_ascii=False)
print(f"OK projects={len(projects)} issues={total} ready={ready} p0={p0} decisions={len(plan['decisions'])} agents={len(plan['agents'])}")
for pr in projects: print(f"  {pr['key']}: {len(pr['issues'])}")
