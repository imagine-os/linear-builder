import json
from r2lib import *
ch=load_changes()
CUR=json.load(open("project_current.json"))
byk={c["key"]:c["identifier"] for c in ch["created"]}
def k(key, fallback): return byk.get(key, fallback)
kids=lambda p: ", ".join(c["identifier"] for c in ch["created"] if c["parent"]==p)
FG=k("gap/data-layer/filter-grammar","filter grammar (pending)")
C={}
C["app-shell"]=(CUR["app-shell"]["content"] or "")+"""

**Contract**

Provides: the `paperos-template` monorepo and package names `@paperos/{ui,core,spec,views,agents,config-ts,config-biome}` (PAP-13); the `packages/core` barrel and sub-folder ownership table; the seven-width `BREAKPOINTS` and `ops/ci/breakpoints.json` (PAP-14); Pages and Coolify preview URL conventions (PAP-15, PAP-26); `AppShell`, slots, `useLayout`, `useSpec` and the route-file convention (PAP-16); `publicEnv`, `serverEnv`, `SecretStore`, `getTarget()` and every env var name (PAP-17); PWA hooks and `OfflineBanner` (PAP-18); Tauri commands, `paperos://` deep links and desktop release artifacts (PAP-19: """+kids("PAP-19")+"""); `Capabilities` shim and `--safe-*` tokens (PAP-20: """+kids("PAP-20")+"""); `WindowManager` and container-query hooks (PAP-21: """+kids("PAP-21")+"""); `paperos create|doctor|upgrade|kiosk` CLI (PAP-22); `ModuleManifest`, `defineModule`, `composeRoutes` (PAP-28: """+kids("PAP-28")+"""); `@paperos/i18n` formatting with `Money = { amountMinor: bigint }` (PAP-27); host, domain, sops and Coolify token (PAP-25); images, `/healthz`, `/__version` and rollback (PAP-26).

Requires: design tokens (PAP-66), `Principal` (PAP-55), `createDb` and core entities (PAP-32, PAP-33), oRPC host (PAP-35), `can()` (PAP-59), Better Auth sessions (PAP-57), event bus and `FilterTree` (data-layer, """+FG+"""), `forge bootstrap` (PAP-51), release tags (PAP-52), Linear labels and states (PAP-91).

Pending gap issues (blocked by the workspace issue cap, inputs in `round2/gaps-pending-0.json`): runtime feature flags, first-run onboarding wizard, client error handling and crash reporting, code signing and notarisation, per-tenant custom domains.

Exit criteria per milestone:
* Template scaffolds and runs on web (09-19): PAP-13, PAP-14, PAP-15, PAP-16, PAP-17, PAP-18, PAP-25, PAP-26 Done; `pnpm check` green from a fresh clone under 3 minutes; Pages preview and staging URL live with matching SHAs; three example routes render at all seven widths.
* Desktop and mobile shells build (09-23): PAP-19 and PAP-20 children Done; installers for three OSes on a draft release; APK and simulator app from CI; PAP-22 creates a demo app end to end; PAP-27 renders `en`, `es`, `ar`, `en-XA`.
* Multi-monitor and PWA polish (09-29): PAP-21 two-display test recorded; PAP-23 kiosk on two displays; PAP-24 guide passes the unassisted agent trial; PAP-28 CI removal matrix green; PAP-29 first drill report published with all five checkpoints and a comment on PAP-5.
"""
C["data-layer"]=(CUR["data-layer"]["content"] or "")+"""

**Contract**

Provides: Postgres roles, env var names, extensions and backup repo (PAP-30); the local stack, `pnpm stack *` and per-worktree databases (PAP-42); `createDb`, `withTenant`, `TenantContext` and column helpers (PAP-32); the seven core tables and their Zod types (PAP-33); the `app.*` session-variable contract, `expectTenantIsolation` harness and policy generator (PAP-34); `AppRouter`, `createClient`, `tenantProcedure`, `callAs`, `ApiErrorCode` and `/api/*` endpoints (PAP-35: """+kids("PAP-35")+"""); `defineShape`, `useShape`, `useLiveQuery`, `mutate`, `SyncIndicator` and `/api/sync/shape` (PAP-36: """+kids("PAP-36")+"""); `files.*` procedures, `uploadFile`, `FileDrop` (PAP-37); audit trigger, hash chain, `AuditTrail` (PAP-38); `registerSearchable` and `search.query` (PAP-39); span attributes, `/api/otel`, six dashboards (PAP-40); `dictionary.json` and `pii.json` (PAP-41); `defineJob`, `enqueue`, `schedule`, `withIdempotency` (PAP-43); the canonical `FilterTree` grammar with SQL and in-memory evaluators ("""+FG+""").

Requires: host and sops (PAP-25), monorepo layout (PAP-13), `Principal` (PAP-55), sessions (PAP-57), `can()` (PAP-59), docs engine (PAP-128), backend library decision (PAP-214), sync ADR (PAP-31).

Pending gap issues (blocked by the workspace issue cap, inputs in `round2/gaps-pending-0.json`): domain event bus and outbox, transactional email package, server-side field encryption, rate limiting and idempotency, object-storage backups and platform DR drill, tenant lifecycle and quotas, retention and PII enforcement.

Exit criteria per milestone:
* Postgres + Drizzle baseline (09-19): PAP-30, PAP-31, PAP-32, PAP-33, PAP-34, PAP-42 and the filter grammar Done; PAP-35 children Done; `db:migrate && db:seed --profile demo` under 30 s; RLS harness green on every tenant table; `users.me` renders on staging through the typed client.
* Local-first sync working (09-24): PAP-36 children Done with the offline edit replay recording; PAP-37 upload with variants; PAP-38 chain verification; PAP-39 "acmee" finds Acme; PAP-43 1,000 jobs with zero duplicate effects.
* Tenant-safe and observable (09-30): PAP-40 click-to-SQL trace and six dashboards; PAP-41 dictionary with 100 percent core coverage and `pii.json` consumed by audit and OTel; pending lifecycle, retention and DR issues scheduled once created.
"""
C["forge"]=(CUR["forge"]["content"] or "")+"""

**Contract**

Provides: ADR-0001 and the decision-log index format (PAP-44); `https://git.PAPEROS_DOMAIN`, SSH 2222, the container and npm registries, org `imagine-os`, `FORGEJO_ADMIN_TOKEN`, backups and `restore.sh` (PAP-45: """+kids("PAP-45")+"""); branch names, commit trailers `Linear:` and `Character:`, `ownership.json`, rulesets and `worktree.sh` (PAP-46); `repos.yml`, mirror functions and drift monitor (PAP-47); bot identities, `access-matrix.yml` and `mintGithubToken` (PAP-48); PR template headings and `pr-body.ts` (PAP-49); runner labels, `secrets-manifest.yml` and the portability checker (PAP-50); `forge bootstrap` and `.paperos/repo.json` (PAP-51); tag format `<component>-v<semver>` and `releases/feed.json` (PAP-52); DR `report.json` and the snapshot manifest (PAP-53); `forge.*` procedures, `DiffView` and `CommitLink` (PAP-54: """+kids("PAP-54")+""").

Requires: host, DNS, sops and buckets (PAP-25), Gate 1 workflow (PAP-78), Better Auth OIDC (PAP-57), Linear webhook receiver (PAP-97), roster (PAP-104), changelog feed shape agreement (PAP-133).

Pending gap issues (blocked by the workspace issue cap, inputs in `round2/gaps-pending-0.json`): non-Linux CI runners (hosted macOS, Windows VM), template upgrade path and `@paperos/*` registry.

Exit criteria per milestone:
* Forgejo live and mirrored (09-19): PAP-44, PAP-46, PAP-47, PAP-48, PAP-49 Done; PAP-45 children Done with the restore drill timed; every imagine-os repo mirrored with zero drift and 60 s propagation both ways; nine bots audited against the matrix; direct pushes to `main` rejected on both forges.
* CI runs on both forges (09-24): PAP-50 smoke workflow green on Forgejo with no `github.com` access; PAP-51 bootstrap idempotent on the fixture repo; PAP-52 release PR creates tags on both forges; pending runner and upgrade-path issues created and scheduled.
* Disaster recovery proven (09-30): PAP-53 drill report with RTO and RPO and a Gate 1 PR passing on the restored forge; PAP-54 children Done or explicitly deferred with no downstream impact.
"""
for pk,desc in C.items():
    pid=PROJECTS[PKEY[pk]]["id"]
    r=gql('mutation($id:String!,$d:String!){ projectUpdate(id:$id,input:{content:$d}){ success project{ id name } } }',{"id":pid,"d":desc})
    print(pk,r["projectUpdate"]["success"],wc(desc),"words")
    if pid not in ch.setdefault("projectsUpdated",[]): ch["projectsUpdated"].append(pid)
save_changes(ch)
