import json,os,sys,time,re,urllib.request
os.chdir(os.environ.get("PAPEROS_PLAN_DIR", ".") + "/round2")
KEY=os.environ.get("LINEAR_API_KEY","placeholder")
CH="changes-fix-FIX-7 read-first-index.json"
DRY="--dry" in sys.argv
ch=json.load(open(CH)) if os.path.exists(CH) else {"fix":"FIX-7 read-first-index","startedAt":"2026-09-17T06:45Z","documentsUpdated":[],"issuesUpdated":[],"created":[],"relationsCreated":[],"notes":[]}
def save(): json.dump(ch,open(CH,"w"),indent=1)
def gql(q,v=None):
    for attempt in range(6):
        req=urllib.request.Request("https://api.linear.app/graphql",data=json.dumps({"query":q,"variables":v}).encode(),headers={"Authorization":KEY,"Content-Type":"application/json"})
        try:
            with urllib.request.urlopen(req,timeout=120) as r: d=json.load(r)
        except urllib.error.HTTPError as e:
            txt=e.read().decode()
            if e.code==429 or "RATELIMITED" in txt: print("rate limited; sleeping 60s"); time.sleep(60); continue
            print("HTTP",e.code,txt[:800]); sys.exit(1)
        time.sleep(0.3)
        if d.get("errors"):
            if any(er.get("extensions",{}).get("code")=="RATELIMITED" for er in d["errors"]): print("RATELIMITED; sleeping 60s"); time.sleep(60); continue
            print("GQL errors:",json.dumps(d["errors"])[:1500]); sys.exit(1)
        return d["data"]

U={
 "blueprint":"https://linear.app/paperos/document/paperos-core-platform-blueprint-0c2115fe48f1",
 "contracts":"https://linear.app/paperos/document/paperos-interface-and-data-contracts-d40e6a4d227c",
 "threat":"https://linear.app/paperos/document/paperos-security-and-threat-model-51fd5fd8929c",
 "golden":"https://linear.app/paperos/document/new-app-in-ten-minutes-the-golden-path-0f49429f566e",
 "schedule":"https://linear.app/paperos/document/paperos-execution-schedule-1fa3d38d6795",
 "roster":"https://linear.app/paperos/document/paperos-agent-roster-org-chart-and-character-index-fc7ea7f41ff3",
}
CHARS=[("Atlas","Chief Architect and Orchestrator","character-sheet-atlas-chief-architect-and-orchestrator-b4725358adc1"),
 ("Forge","Platform Engineer","character-sheet-forge-platform-engineer-6b19c5679dd0"),
 ("Iris","Design Systems Lead","character-sheet-iris-design-systems-lead-43ca4e29d4a9"),
 ("Quill","Spec and Documentation Lead","character-sheet-quill-spec-and-documentation-lead-1ba00329d4c8"),
 ("Sentinel","Quality Lead","character-sheet-sentinel-quality-lead-fc3ada07f9e3"),
 ("Nova","Product Systems Engineer","character-sheet-nova-product-systems-engineer-a736fa0dc023"),
 ("Ledger","Business Systems Lead","character-sheet-ledger-business-systems-lead-b876b4a0d809"),
 ("Beacon","Growth Lead","character-sheet-beacon-growth-lead-12b0b4eda18b"),
 ("Scout","Library and Migration Researcher","character-sheet-scout-library-and-migration-researcher-44cef400dbbc")]
PENDING=[("contracts (4)","Data Layer & Database","round-2-pending-issues-contracts-4-734961df9c59","shared value types (`Money`, `ActorRef`, `EntityRef`, cursors), domain event contract and outbox, idempotency and rate limiting, package boundary map (issues A-D of Contracts §6)"),
 ("security (11)","Quality Pipeline","round-2-pending-issues-security-11-27d8ebfcd8d0","agent deny list, prompt-injection defences, credential broker, field encryption, platform DR drill, retention and PII, security telemetry, DAST, founder break-glass, supply chain, PCI SAQ-A posture (Threat Model §9)"),
 ("golden path (8)","Universal App Shell & Repo Template","round-2-pending-issues-golden-path-8-98e27ab16f4f","app interview, entity pages, generation pipeline, starter surfaces, `paperos create` driver, provisioning, acceptance test, template upgrade (Golden Path §8)"),
 ("pm-linear (9)","Project Management & Claude Pipeline","round-2-pending-issues-pm-linear-9-d4829fc00859","workspace reconcile (merged into PAP-91), weekly plan re-audit, inbound triage, the three PAP-96 orchestrator children, the three PAP-101 Linear-sync children"),
 ("agents (9)","Agent Characters & Orgs","round-2-pending-issues-agents-9-85624b15630d","runtime sandbox, session observability, the four PAP-104 roster children, the three eval-harness children"),
 ("spec-builder (11)","Spec Builder","round-2-pending-issues-spec-builder-11-c314e290076b","spec i18n, spec versioning (folded into PAP-114), children of PAP-119 data section, PAP-120 layout codegen and PAP-124 spec editor"),
 ("tables (24)","Table & Views Engine","round-2-pending-issues-tables-24-86486d9b99cc","custom dataset schema editor, record-level features, bulk ops and trash, and 21 children of the compiler, field types, grid, calendar/timeline/gantt, formulas, dashboards and automations"),
 ("business-core (11)","Business Core: Payments, Finance & Payroll","round-2-pending-issues-business-core-11-7c8c2526b3c9","usage metering, recurring invoices and dunning (folded into PAP-180), and 9 children of the ledger, invoicing and payroll umbrellas"),
 ("growth (13)","Growth: Marketing, Outreach & CRM","round-2-pending-issues-growth-13-3fd4406e8012","consent and marketing compliance centre (folded into PAP-187), and 12 children of social scheduling, outreach, referrals and support inbox"),
 ("migration (20)","Migration & Import Tools","round-2-pending-issues-migration-20-6cb063cc1be6","importer test accounts (folded into PAP-198), Monday and HubSpot CSV recipes, and 18 children of the import engine, Airtable, Notion, export, Stripe, QuickBooks/Xero and template packs"),
 ("libraries (9)","Library Discovery & Integration","round-2-pending-issues-libraries-9-63c73eed632d","table, chart, map, canvas and editor spikes with ADRs; jobs, email, PDF, search, observability, flags and storage decisions; OSS product spikes (NocoDB, Baserow, Plane, Twenty, Chatwoot, Listmonk, Postiz, Cal.com, Formbricks)")]
def pu(slug): return "https://linear.app/paperos/document/"+slug

# ---------- Blueprint section ----------
BP_MARK="## Documents (read in this order)"
def blueprint_section():
    L=[]
    L.append(BP_MARK); L.append("")
    L.append("Updated 2026-09-17 (round 2). Every Claude Code session reads these in this order before writing code; the session playbook (PAP-92) repeats the list and the orchestrator prompt (PAP-96, PAP-104) links it. Documents hold the decisions; issue bodies say what to build. If an issue body and a document disagree, the document wins and the difference is filed as an ADR (PAP-130) with a comment on the owning issue.")
    L.append("")
    L.append(f"1. **This Blueprint** ([link]({U['blueprint']})): vision, key decisions, phases, credit budget, agent roster, pipeline.")
    L.append(f"2. **[PaperOS Interface & Data Contracts]({U['contracts']})**: ids and RLS session variables, `Principal` and `ActorRef`, `Money`, `FilterTree`, the shared data model, the event envelope and topic catalogue, API conventions (paths, headers, errors, idempotency), monorepo package boundaries, and the provide/consume matrix per issue. Owned by Data Layer (Forge, reviewed by Sentinel).")
    L.append("3. **Your project's `Contract` section**: the Linear project content of the project your issue belongs to lists what each issue provides and consumes; read it after the Contracts document and before your issue's Interface contract.")
    L.append(f"4. **[PaperOS Agent Roster]({U['roster']})** and your **character sheet**: org chart, routing (who picks up which issue), shared rules every session obeys, escalation matrix. Character sheets: " + ", ".join(f"[{n}]({pu(s)}) ({r})" for n,r,s in CHARS) + ".")
    L.append(f"5. **[PaperOS Security & Threat Model]({U['threat']})**: STRIDE per trust boundary, destructive-action deny list for agents, secrets handling, prompt-injection tiers T0-T4, backup and DR, compliance posture, gap register. Mandatory for identity, quality, agents, infra, business-core and any issue that touches secrets, payments or personal data; PAP-219 turns it into `controls.yaml`.")
    L.append(f"6. **[PaperOS Execution Schedule]({U['schedule']})**: scheduling rules including the branch-start rule, day-by-day claims 09-17 to 10-01, capacity curve, RC0-RC3 checkpoints, numbered Needs Justin items, credit burn model and stop-loss. Find your issue's start half-day before claiming.")
    L.append(f"7. **[New App in Ten Minutes: the golden path]({U['golden']})**: the end-to-end experience the platform exists for (the answer to PAP-5): what `paperos create` asks, generates and deploys, and the acceptance test. Read it if your issue is in app-shell, spec-builder, forge, design-system or touches the CLI.")
    L.append("")
    L.append("**Waiting on the issue cap.** Linear refused about 165 `issueCreate` calls on 2026-09-17 (`USAGE_LIMIT_EXCEEDED`, free plan). Their full specs live in these documents and are created in the order given on PAP-91 (Needs Justin NJ-1) once the plan is upgraded; until then a live issue that cites a bracketed key such as `[agents/runtime-sandbox]` means \"see the pending document for that project\", and umbrella issues carry their work packages inline. Four pending specs were folded into live issues instead (test accounts into PAP-198, consent centre into PAP-187, recurring dunning into PAP-180, spec versioning into PAP-114); their documents say so at the entry.")
    L.append("")
    for name,proj,slug,what in PENDING:
        L.append(f"* [Round 2 pending issues: {name}]({pu(slug)}) ({proj}): {what}.")
    L.append("")
    return "\n".join(L)

def update_blueprint():
    if any(d.get("id")=="91be37cd-6998-490c-8309-31817f4859c0" for d in ch["documentsUpdated"]): print("blueprint already updated (changes file)"); return
    d=gql('{ document(id:"91be37cd-6998-490c-8309-31817f4859c0"){ id content updatedAt } }')["document"]
    c=d["content"]
    if BP_MARK in c: print("blueprint already has section (live)"); ch["documentsUpdated"].append({"id":d["id"],"title":"PaperOS Core Platform Blueprint","change":"section already present","chars":len(c)}); save(); return
    anchor="Risks and the full per-issue index are on the blueprint page:"
    sec=blueprint_section()
    if anchor in c:
        i=c.index(anchor); new=c[:i].rstrip("\n")+"\n\n"+sec+"\n"+c[i:]
    else:
        new=c.rstrip("\n")+"\n\n"+sec
    open("_fix7_blueprint_new.md","w").write(new)
    if DRY: print("DRY blueprint chars",len(new)); return
    r=gql('mutation($id:String!,$in:DocumentUpdateInput!){ documentUpdate(id:$id,input:$in){ success document{ id updatedAt } } }',{"id":d["id"],"in":{"content":new}})
    print("blueprint update",r["documentUpdate"]["success"],len(new))
    if r["documentUpdate"]["success"]:
        ch["documentsUpdated"].append({"id":d["id"],"title":"PaperOS Core Platform Blueprint","url":U["blueprint"],"change":"added 'Documents (read in this order)' section: 7 documents + 9 character sheets + 11 pending-issue documents","chars":len(new),"previousUpdatedAt":d["updatedAt"]}); save()

# ---------- issue text ----------
def section_span(d,name):
    m=re.search(r'^\*\*'+re.escape(name)+r'\*\*\s*$',d,re.M)
    if not m: return None
    n=re.search(r'^\*\*[^*\n]+\*\*\s*$',d[m.end():],re.M)
    return (m.end(), m.end()+n.start() if n else len(d))
def insert_at_section_end(d,name,text):
    sp=section_span(d,name)
    if not sp: raise RuntimeError("no section "+name)
    p=sp[1]; head=d[:p].rstrip("\n"); tail=d[p:].lstrip("\n")
    return head+"\n\n"+text+("\n\n"+tail if tail else "\n")

C=U["contracts"]; T=U["threat"]
def RF(extra):
    return (f"**Read first.** Read before coding: [Blueprint]({U['blueprint']}) → [Interface & Data Contracts]({C}) → your project's `Contract` section (Linear project content) → your character sheet ([Roster]({U['roster']})) → [Execution Schedule]({U['schedule']}) for your start day and the branch-start rule. "+extra).strip()
READ_FIRST={
 "PAP-92": RF(f"Also the [Security & Threat Model]({T}) (§4 deny list, §6 prompt tiers) and the [Golden Path]({U['golden']}). The playbook you write carries this exact reading order and links every document in the Blueprint section \"Documents (read in this order)\"."),
 "PAP-13": RF("Contracts §5 (Monorepo package boundaries) fixes the package list, owners and registration points this scaffold creates, and §1 fixes UUIDv7 ids and Zod 4 as the schema language; the sub-folder ownership table in `packages/core/README.md` must match §5."),
 "PAP-91": RF(f"Also [Security & Threat Model]({T}) §4 (Linear deny list: never archive or delete anything, never move to Done or Canceled, never touch PAP-1..PAP-12 or views) and the Execution Schedule's Needs Justin table (NJ-1 is this issue)."),
 "PAP-103": RF("The Roster and the nine character sheets linked from it are the fixtures `validateRoster` must accept unchanged; Contracts §2 row \"Agent principal\" fixes the key metadata `{ character, issue?, session?, scopes[] }` and the session status shape your schema feeds."),
 "PAP-114": RF(f"Contracts §2 rows \"Page\" and \"Component\" fix `meta.id`, the section list and `status: ready`; §1 makes Zod 4 the schema language with JSON Schema generated, never hand-written; [Golden Path]({U['golden']}) §4 shows what is generated from the spec."),
 "PAP-219": RF(f"The [Security & Threat Model]({T}) is v1 of the document this issue owns: §3 STRIDE by boundary, §4 deny list, §5 secrets handling, §6 prompt-injection tiers, §7 backup and DR, §8 compliance posture, §9 gap register. Treat it as the draft baseline, give every control an `SEC-*` id in `controls.yaml`, and file any disagreement as an ADR rather than silently diverging."),
 "PAP-279": RF("Contracts §1 (the `FilterTree` bullet: permissions `Condition`, view `FilterGroup`, spec data section, segments and automations are aliases of this type) and §6 row `FilterTree` list every consumer; §4 fixes the list input `filter?: FilterTree`."),
 "PAP-96": RF(f"Also Contracts §3 (topics `agent.session.started|finished|blocked`, `agent.quota.exceeded`, `issue.needs_justin`, `review.*`) and §2 row \"Agent principal\"; [Security & Threat Model]({T}) §4 (deny list), §5 (broker placeholders, Linear key never leaves the orchestrator), §6 (only T0 rendered prompts and T1 Justin comments instruct an agent); Roster section \"Routing: who picks up an issue\"; Execution Schedule §1 for the branch-start rule the orchestrator must implement."),
 "PAP-25": RF(f"Also [Security & Threat Model]({T}) §5 (sops and age layout, two recipients, Coolify secret mirror) and §7 (the backup rows owned by PAP-25 and PAP-30); the Execution Schedule's NJ-2 batch is the single credential ask this issue files."),
}
def CS(text): return f"* Contract source: [Interface & Data Contracts]({C}) "+text
GATE_COMMON=(f"§5 (`packages/contracts` is owned by quality through PAP-239: every `reports/*.json` named above is a `GateReport<kind>` validated by `validateArtifact()`, JSON Schema generated from Zod 4 per §1); §3 (gate results reach the bus as `review.gate_failed` and `review.ready` through PAP-97; artifact `version` bumps keep a reader for 30 days); §6 row \"Gate artifacts\" (provider PAP-239; consumers PAP-78 to PAP-90, PAP-97, PAP-137, PAP-110). Until PAP-239 merges, write the shape exactly as its Interface contract states and import the schema when it lands.")
CONTRACT={
 "PAP-55": CS("§1 (`Principal = { id, type: 'human'|'agent'|'service'|'anonymous', tenantId, attributes }` from `@paperos/core/audience` is the canonical actor type; `ActorRef = { id, type, character? }` is its projection stored on rows, events and comments; `user.kind` in PAP-33 and `principalType` in PAP-57/PAP-60 are storage views of the same enum); §2 row \"Membership / Role\" (five base roles `owner|admin|staff|member|viewer` come from this issue); §6 row \"`Principal` and audiences\" (consumers PAP-35/267, PAP-59, PAP-60, PAP-114, PAP-136, PAP-141, PAP-195). This issue is the provider: export exactly that shape and change it only through an ADR (PAP-130)."),
 "PAP-35": CS("§1 (`Principal` is imported from `@paperos/core/audience` for `Context.actor`, never redefined here); §4 Internal API conventions (transport `/api/v1/rpc/<router>.<procedure>` plus OpenAPI 3.1 REST, auth and tenant headers, procedure shape with `filter?: FilterTree` and signed keyset cursors, `ORPCError` codes, `/api/v1` versioning; the in-memory rate limit here is the interim until pending contracts issue C); §6 rows \"API middleware, error codes, headers\" and \"Routers, client, pagination\"."),
 "PAP-267": CS("§1 (`Principal` from `@paperos/core/audience` is the type of `Context.actor`; RLS context is set with `SET LOCAL app.tenant_id, app.actor_id, app.actor_kind, app.request_id, app.reason, app.bypass`, and `app.actor_id` equals `app.principal_id` until the names are unified); §4 (headers `x-tenant`, `Idempotency-Key`, `X-PaperOS-Reason`, `X-PaperOS-Env`, `traceparent` in and `x-request-id`, `X-PaperOS-Actor` out; error body `{ code, message, requestId, details?, retryAfter? }`; RLS `42501` maps to `NOT_FOUND` on reads and `FORBIDDEN` on writes; `TENANT_REQUIRED` is retired in favour of 400 `VALIDATION`); §6 row \"API middleware, error codes, headers\"."),
 "PAP-59": CS("§1 (`Principal` is the `actor` argument of `can()`; `Condition` is an alias of `FilterTree` from `@paperos/core/filter` (PAP-279), with `{ $var: 'principal.id' }` variables resolved at evaluation; identity adds `app.principal_id, app.role, app.attrs` to the RLS session variables); §4 (non-production error bodies carry `explain` from `can()`); §6 rows \"`can()` and SQL predicates\" and \"`Principal` and audiences\"."),
 "PAP-71": CS("§1 (`Money = { amountMinor: bigint, currency }` at runtime and a decimal string such as `\"1999\"` on the wire; the earlier `number` form in this issue is superseded by PAP-175's shape); `formatMoney` and `ui.money` accept exactly that type, and `formatDate` takes the ISO-8601 UTC strings of §1; §6 row \"Shared value types\" (provider: pending contracts issue A `contracts/shared-value-types` in `@paperos/core/types`; until it exists import `Money` from PAP-175's `moneySchema`)."),
 "PAP-164": CS("§1 (`Money = { amountMinor: bigint, currency }` in TypeScript, `amount_minor bigint + currency char(3)` in Postgres, decimal string on the wire; the `currency` field type must store and cast exactly that and never a float; ids are UUIDv7 strings; timestamps ISO-8601 UTC); §2 row \"Record\" (`record.data jsonb` validated by `FieldDef[]`); §6 row \"Shared value types\" (provider: pending contracts issue A; interim import from PAP-175)."),
 "PAP-175": CS("§1 (the `Money` bullet is decided in this issue's favour: `{ amountMinor: bigint, currency }` at runtime, `amount_minor bigint + currency char(3)` in Postgres, decimal string in JSON; PAP-71, PAP-164 and PAP-187 conform to it); §2 row \"Ledger entry\" (`fin_transaction`, `fin_journal_entry`, `fin_journal_line`, `fin_account_balance`; lines balance in functional currency or `UNBALANCED`; posted entries immutable and reversed, never edited; `ledger.postEvent(tx)` idempotent on `(source_type, source_id)`; accounts resolved by `subtype`, never code); §3 topics `invoice.*`, `payment.*`, `subscription.updated`, `payroll.run.*`, `ledger.entry.posted|reversed`; §6 row \"Finance model and ledger posting\". `moneySchema` here is the reference implementation until pending contracts issue A moves it into `@paperos/core/types`."),
 "PAP-180": CS("§1 (`Money` from PAP-175: `amountMinor` bigint at runtime, string on the wire, never floats in totals or tax lines); §3 (the catalogue names these topics `invoice.issued|paid|voided` and `payment.succeeded|failed|refunded`; register the `document.*` events above under those topic names with `defineTopic`, payloads carry ids and changed fields only, `subject` is the `EntityRef` of the invoice); §2 row \"File\" (PDFs go through PAP-37's `file` table and per-request download URLs); §6 rows \"Finance model and ledger posting\" and \"Design tokens and branding\" (PDF theme from PAP-235)."),
 "PAP-187": CS("§1 (`Money`: rename `amount_cents` to `amount_minor bigint` with `currency char(3)` per PAP-175; segment definitions are `FilterTree` from `@paperos/core/filter` (PAP-279), not a CRM-local grammar); §2 (`EntityRef = { type, id }` for activity links where `type` is the PAP-161 dataset key); §3 (register `crm.deal.stage_changed`, `crm.lead.converted`, `crm.contact.created` with `defineTopic`; `segment.entered|exited` belongs to PAP-195); §6 rows \"Core entities and Zod types\" and \"`FilterTree`\"."),
 "PAP-279": CS("§1 (the `FilterTree` bullet: permissions `Condition`, view `FilterGroup`, the spec data section, segments and automations are aliases of this one type; Zod 4 schema with generated JSON Schema); §4 (list procedures take `filter?: FilterTree`); §6 row \"`FilterTree`\" (provider: this issue; consumers PAP-59, PAP-161, PAP-119, PAP-163, PAP-166, PAP-172, PAP-174, PAP-195, PAP-268). This issue is the provider: any operator or shape change is an ADR."),
 "PAP-161": CS("§1 (`spec.filter` is a `FilterTree` from `@paperos/core/filter`, PAP-279; `FilterGroup` is an alias, not a copy); §2 rows \"View\" (`ViewSpec` strict Zod, `dataset_ref jsonb` as `entity:key` or `custom:id`, ten view kinds, `visibility personal|shared|public`) and \"Record\" (`record.data jsonb` validated by `FieldDef[]`, code datasets via `registerDataset()`); `EntityRef.type` used by comments, notifications, search and audit is the dataset key from this registry; §6 row \"View model\"."),
 "PAP-116": CS("§1 (permissions `Condition` is an alias of `FilterTree` (PAP-279), so `rows:` conditions in the access section are FilterTree literals with `{ $var: 'principal.id' }` variables; the subject is the §1 `Principal`, audience ids come from PAP-55); §6 rows \"`FilterTree`\", \"`Principal` and audiences\" and \"Page and app spec schema\" (this issue compiles the spec side of the `can()` contract owned by PAP-59)."),
 "PAP-119": CS("§1 (query `where` clauses are `FilterTree` from `@paperos/core/filter` (PAP-279); the local copy with a TODO is removed); §4 (generated hooks call the procedure shape `{ cursor?, limit<=100, filter?: FilterTree, sort?: { field, dir }[] }` returning `{ items, nextCursor }`, and mutations send `Idempotency-Key` and `X-PaperOS-Reason` for agents); §6 rows \"`FilterTree`\", \"Routers, client, pagination\" and \"Page and app spec schema\"."),
 "PAP-28": CS("§3 (module `emit` publishes the outbox envelope `{ id: uuidv7, topic, version, occurredAt, tenantId, actor: ActorRef, subject: EntityRef, requestId?, causationId?, correlationId?, idempotencyKey?, payload }`; topics are `<entity>.<past-tense-verb>` registered with `defineTopic`, publishing an unregistered topic fails at boot); §5 (optional modules import only `@paperos/core`, `@paperos/db`, `@paperos/ui`, `@paperos/spec`, `@paperos/views` and events; a lint rule bans other cross-module imports); §6 rows \"Module manifest\" and \"Domain event envelope\" (provider: pending contracts issue B `contracts/domain-events`; until it exists, implement `emit` against the §3 envelope verbatim in `packages/core/events`)."),
 "PAP-97": CS("§3 (the orchestrator is both a bus consumer and the producer of `issue.needs_justin`, `review.gate_failed`, `review.ready` and `release.candidate`; inbound Linear and Forgejo webhooks are normalised into the §3 envelope with `actor.type='service'`; delivery is at-least-once and handlers are idempotent on `event.id`); `PrStatus.gates` and `verdicts` are read from the PAP-239 `GateReport` artifacts (§6 row \"Gate artifacts\"); §6 row \"Domain event envelope\" (provider: pending contracts issue B; the `events` emitter here uses the same envelope so the swap is one import)."),
 "PAP-136": CS("§2 row \"Notification\" (`notification`, `notification_preference`, `notification_delivery`; kinds registry; idempotency on `(kind, source, recipient, bucket)`; produced by subscribing to the event bus); §3 (envelope and the topics this consumes: `issue.needs_justin`, `review.gate_failed`, `review.ready`, `release.candidate`, `comment.created|mentioned|resolved`, `changelog.published`, `import.finished`, `payment.failed`); §1 (`Principal` audiences from PAP-55, `ActorRef` on the notification row); §6 row \"Domain event envelope\". The interim in-process emitter in `packages/collab/notifications/bus.ts` must use the §3 envelope shape so the move to `@paperos/core/events` is a one-import change."),
 "PAP-174": CS("§3 (LISTEN/NOTIFY is only a wake-up hint and this issue debounces it; the outbox is the delivery path; record triggers subscribe to `record.created|updated|deleted` and register `automation.run.finished` with `defineTopic`; subscribers are idempotent on `event.id`, ordering is per `subject` only, delivery at-least-once); §1 (conditions are `FilterTree` from PAP-279, never a local grammar); §6 rows \"Domain event envelope\" and \"RLS session-variable contract\" (runs execute under `app.actor_kind='system'` with the triggering actor in `app.reason`)."),
 "PAP-177": CS("§3 (`stripe_event` is an inbox whose rows are normalised into the §3 envelope with `actor.type='service'`; the catalogue topics are `subscription.updated` and `payment.succeeded|failed|refunded`, so register `billing.subscription.changed` under `subscription.updated` or declare the alias in `defineTopic`); §4 (idempotency keys and rate limits are owned by pending contracts issue C; interim: idempotent on `stripe_event.id`); §6 rows \"Finance model and ledger posting\" and \"Idempotency keys, rate limits, batch\". Also [Security & Threat Model]("+T+") §8 (PCI SAQ-A: card data only in Checkout, Elements and the Customer Portal; restricted test keys; live mode is a hard-block Needs Justin decision)."),
 "PAP-78": CS(GATE_COMMON+" Also §5 and §6 row \"Package boundary map and import lint\": Gate 1 runs the cross-package import lint once pending contracts issue D lands (soft; Biome `noImportCycles` is the interim)."),
 "PAP-80": CS(GATE_COMMON+" Also [Security & Threat Model]("+T+") §5 (gitleaks on every diff and nightly over history; suppressions expire) and §8 (Semgrep blocks PAN-shaped fields and `sk_live_` literals; SAST, secret, dependency and container scans per PR gate release candidates), and PAP-219 `controls.yaml` for the `SEC-*` ids."),
 "PAP-82": CS(GATE_COMMON+" `reports/visual.json` is `GateReport<'visual'>` with `data.images`; screenshot naming `screenshots/<page>/<width>.png` is consumed by PAP-97 status comments."),
 "PAP-83": CS(GATE_COMMON+" `reports/videos.json` is a `GateReport<'videos'>`; recordings are stored through the §2 \"File\" contract (PAP-37) and linked, never inlined."),
 "PAP-84": CS(GATE_COMMON+" `reports/vision.json` is `GateReport<'vision'>`; findings use the shared finding schema with `findingId()` so PAP-85 can dedupe by id and bbox."),
 "PAP-85": CS(GATE_COMMON+" `reports/edgecases.json` is `GateReport<'edgecases'>` with `data.matrix`; the spec it reads is the §2 \"Page\" contract (PAP-114)."),
 "PAP-89": CS(GATE_COMMON+" The digest is a pure reader of `GateReport` artifacts and emits `release.candidate` (§3) through PAP-97; the Linear body variant must render through the §2 \"Notification\" contract once PAP-136 work package 1 exists."),
 "PAP-239": CS("§5 (`packages/contracts` row: owned by quality, contents \"gate artifacts\"; every other project adds shapes only through this package's registration); §1 (Zod 4 is the schema language, JSON Schema generated, never hand-written; agent authors on findings are the §1 `ActorRef`); §3 (the 30-day reader rule for `version` bumps is shared with the event envelope); §6 row \"Gate artifacts\" (consumers PAP-78 to PAP-90, PAP-97, PAP-137, PAP-110). This issue is the provider."),
 "PAP-219": CS("§1 (RLS session variables and `app.bypass` are the controls the harness in PAP-34 proves) and §4 (auth headers and error codes the hardening baseline covers). Threat Model source: [PaperOS Security & Threat Model]("+T+") §3 STRIDE by boundary, §4 deny list, §5 secrets handling, §6 prompt-injection tiers, §7 backup and DR, §8 compliance posture; `controls.yaml` must give every control named there an `SEC-*` id, and §9's gap register names the pending security issues that extend this baseline."),
 "PAP-81": CS(GATE_COMMON+" Also [Security & Threat Model]("+T+") §6 (PR diffs, fork PRs and imported documents are T3 and are wrapped in `<untrusted source= tier=>` blocks; only the orchestrator's rendered prompt and Justin's comments instruct the reviewer) and §3 (the security reviewer checks the STRIDE rows and PAP-219 `controls.yaml`, reading PAP-80 `security.json` as its baseline)."),
 "PAP-106": CS("§2 row \"Agent principal\" (`user` rows with `kind='agent'`, API-key metadata `{ character, issue?, session?, scopes[] }`, prefix `pos_agent_`) and §5 (`.claude/` is owned by agents; `packages/agents` holds the bundles). Threat Model source: [PaperOS Security & Threat Model]("+T+") §4 (the deny list in `ops/security/agent-deny.yaml` is enforced by this issue's PreToolUse hook and by removing `destructive`-scoped MCP tools from every character except Atlas, with a server-side backstop for every S0 rule) and §5 (per-agent scoped tokens, `broker:*` placeholders injected by the egress proxy, `secretsFor` is the only path a secret reaches a session)."),
}

PAP92_READING_OLD="* Required reading order: issue body sections, linked `specs/**` files, `CLAUDE.md`, character memory (PAP-109), last two Linear comments, ADRs touched."
PAP92_READING_NEW=(f"* Required reading order: (1) the documents in the Blueprint section \"Documents (read in this order)\": [Blueprint]({U['blueprint']}), [Interface & Data Contracts]({C}), the project's `Contract` section, [Roster]({U['roster']}) and the session's character sheet, [Security & Threat Model]({T}), [Execution Schedule]({U['schedule']}), [Golden Path]({U['golden']}) when relevant; (2) the issue body sections, linked `specs/**` files, `CLAUDE.md`, character memory (PAP-109), the last two Linear comments, the ADRs touched. The playbook links each document and says in one line what to take from it.")
PAP92_DOD_NEW=("* The playbook links every document in the Blueprint section \"Documents (read in this order)\" (Blueprint, Contracts, Threat Model, Roster and the nine character sheets, Execution Schedule, Golden Path, the pending-issue documents) and states the umbrella, promotion and deferred rules verbatim: umbrella (above); promotion (how a Backlog issue reaches Ready for Claude when its blockers are Done or In Review with a PR, the branch-start rule, PAP-96 promotion package and PAP-93 `BLOCKED_BY_OPEN`); deferred (an issue with the `Deferred` label or a \"deferred\" note in its body is never claimed and never promoted until Justin removes the deferral).")

def transform(ident,d):
    changed=[]
    if ident in READ_FIRST and "**Read first.**" not in d:
        d=insert_at_section_end(d,"Goal",READ_FIRST[ident]); changed.append("read-first")
    if ident in CONTRACT and "Contract source:" not in d:
        d=insert_at_section_end(d,"Interface contract",CONTRACT[ident]); changed.append("contract-source")
    if ident=="PAP-92":
        if PAP92_READING_OLD in d: d=d.replace(PAP92_READING_OLD,PAP92_READING_NEW,1); changed.append("reading-order")
        elif "Documents (read in this order)" not in d: print("PAP-92 reading-order anchor missing")
        sp=section_span(d,"Definition of done")
        if sp and "Documents (read in this order)" not in d[sp[0]:sp[1]]:
            d=insert_at_section_end(d,"Definition of done",PAP92_DOD_NEW); changed.append("dod-links")
    return d,changed

ORDER=list(dict.fromkeys(list(READ_FIRST)+list(CONTRACT)))
def run_issues():
    done={u["identifier"]:u for u in ch["issuesUpdated"]}
    todo=[k for k in ORDER if k not in done]
    print("issues to process:",len(todo))
    for i in range(0,len(todo),10):
        chunk=todo[i:i+10]
        q="{ "+" ".join(f'i{k.split("-")[1]}: issue(id:"{k}"){{ id identifier updatedAt description }}' for k in chunk)+" }"
        live=gql(q)
        ups=[]
        for k in chunk:
            n=live["i"+k.split("-")[1]]
            new,changed=transform(k,n["description"])
            if not changed: print(k,"nothing to change (already present)"); ch["issuesUpdated"].append({"id":n["id"],"identifier":k,"fields":[],"note":"already present"}); continue
            open(f"_fix7_preview_{k}.md","w").write(new)
            ups.append((k,n["id"],new,changed,n["updatedAt"]))
        if DRY:
            for k,iid,new,changed,_ in ups: print("DRY",k,changed,len(new))
            continue
        if not ups: save(); continue
        mq="mutation("+",".join(f"$in{j}: IssueUpdateInput!, $id{j}: String!" for j in range(len(ups)))+") { "+" ".join(f"u{j}: issueUpdate(id: $id{j}, input: $in{j}) {{ success issue {{ updatedAt }} }}" for j in range(len(ups)))+" }"
        v={}
        for j,(k,iid,new,changed,_) in enumerate(ups): v[f"id{j}"]=iid; v[f"in{j}"]={"description":new}
        res=gql(mq,v)
        for j,(k,iid,new,changed,prev) in enumerate(ups):
            ok=res[f"u{j}"]["success"]; print(k,ok,changed,len(new))
            if ok: ch["issuesUpdated"].append({"id":iid,"identifier":k,"fields":["description"],"changes":changed,"chars":len(new),"previousUpdatedAt":prev})
        save()

update_blueprint()
run_issues()
save()
print("done; changes file:",CH)
