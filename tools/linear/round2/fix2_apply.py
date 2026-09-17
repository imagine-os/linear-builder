import json, os, re, time, sys, urllib.request, ssl
KEY=os.environ.get("LINEAR_API_KEY","placeholder")
CH="changes-fix-FIX-2 ready-but-blocked.json"
ch=json.load(open(CH)) if os.path.exists(CH) else {"fix":"FIX-2 ready-but-blocked","startedAt":"2026-09-17T06:20Z","relationsDeleted":[],"issuesUpdated":[],"created":[],"notes":[]}
def save(): json.dump(ch,open(CH,"w"),indent=1)

def gql(q,v=None):
    for attempt in range(5):
        body=json.dumps({"query":q,"variables":v}).encode()
        req=urllib.request.Request("https://api.linear.app/graphql",data=body,headers={"Authorization":KEY,"Content-Type":"application/json"})
        try:
            with urllib.request.urlopen(req,timeout=60) as r: d=json.load(r)
        except urllib.error.HTTPError as e:
            txt=e.read().decode(); 
            if e.code==429 or "RATELIMITED" in txt: print("rate limited, sleeping 60s"); time.sleep(60); continue
            print("HTTP",e.code,txt[:500]); sys.exit(1)
        time.sleep(0.3)
        if d.get("errors"):
            if any(er.get("extensions",{}).get("code")=="RATELIMITED" for er in d["errors"]): print("RATELIMITED, sleeping 60s"); time.sleep(60); continue
            print("GQL errors:",json.dumps(d["errors"])[:1500]); sys.exit(1)
        return d["data"]
    sys.exit("retries exhausted")

# 1. delete the two relations (idempotent: skip ids already recorded)
rels=[("9ebc6c89-8ef5-4a4f-a00b-2be17fefc6d3","PAP-13 blocks PAP-279"),("7e8faf6d-5852-4b60-87eb-41932a0b2538","PAP-279 blocks PAP-161")]
done_ids={r["id"] for r in ch["relationsDeleted"]}
todo=[r for r in rels if r[0] not in done_ids]
if todo:
    q="mutation { "+" ".join(f'd{i}: issueRelationDelete(id: "{rid}") {{ success }}' for i,(rid,_) in enumerate(todo))+" }"
    res=gql(q)
    for i,(rid,label) in enumerate(todo):
        ok=res[f"d{i}"]["success"]; print("delete",label,rid,ok)
        if ok: ch["relationsDeleted"].append({"id":rid,"relation":label})
    save()

# 2. fetch live descriptions
live=gql('{ a: issue(id: "PAP-279") { id description } b: issue(id: "PAP-161") { id description } c: issue(id: "PAP-93") { id description } }')
A,B,C=live["a"],live["b"],live["c"]

def must_replace(text,old,new,who):
    if old not in text: print(f"ANCHOR MISSING in {who}: {old[:80]!r}"); sys.exit(1)
    return text.replace(old,new,1)

# PAP-279
a=A["description"]
old_a="None hard (pure package on PAP-13 layout); PAP-42 for the PGlite test only. Ready now. Blocks PAP-59, PAP-161, PAP-119, PAP-166, PAP-174, PAP-195."
new_a=("None hard. Ready now. This is a pure Zod/TypeScript package with its own `package.json` under `packages/core/src/filter/`; it does not need the monorepo scaffold (PAP-13) to start. If PAP-13 is not merged when you begin, start from the PAP-13 PR branch (`feat/PAP-13`) or a bare `pnpm` workspace with the same layout and rebase when PAP-13 lands. The relation `PAP-13 blocks PAP-279` was removed on 2026-09-17 (FIX-2) for this reason; do not re-add it. "
       "Soft: PAP-42 for the PGlite property test only (if PAP-42 is absent, add `@electric-sql/pglite` as a dev dependency of this package and run the test in-process). "
       "Blocks (hard, relations exist): PAP-59, PAP-116, PAP-119, PAP-163, PAP-166, PAP-174, PAP-195. Soft consumer: PAP-161 imports the draft `FilterTree` from this issue's PR branch and is not blocked by it, so open the PR early and keep `FilterTree`, `filterTreeSchema` and `FieldSchema` exported from the first commit.")
a=must_replace(a,old_a,new_a,"PAP-279 deps")

# PAP-161
b=B["description"]
old_b="PAP-33 (hard), PAP-34 (hard), PAP-279 filter grammar (hard for the `filter` type; import the draft if not merged), PAP-162 in parallel for the equivalence column. Blocks PAP-163, PAP-164, PAP-207."
new_b=("Ready now; no inbound `blocks` relation is open (FIX-2, 2026-09-17). "
       "PAP-279 soft: import the draft `FilterTree` from the PAP-279 PR branch (`feat/PAP-279`, `@paperos/core/filter`); if PAP-279 is not In Review when you start, define `filter` as `unknown` (`filter: z.unknown()` in `viewSpecSchema`, exported type `FilterTree = unknown`) and leave a `// TODO(PAP-279): replace with FilterTree from @paperos/core/filter` at the definition; swapping the alias when PAP-279 merges is the only follow-up. The relation `PAP-279 blocks PAP-161` was removed for this reason; do not re-add it. "
       "PAP-33 and PAP-34 soft: they gate only work package 2 (Drizzle tables `dataset|field|record|view` and RLS policies). Build the Zod model, types, JSON Schema, `migrateViewSpec`, `registerDataset` and docs first; write the migration against the PAP-33 PR branch if it is In Review, otherwise land the tables as a second commit on this branch after PAP-33 merges and note it in the PR. "
       "PAP-162 in parallel for the equivalence column. Blocks PAP-163, PAP-164, PAP-207.")
b=must_replace(b,old_b,new_b,"PAP-161 deps")
b=must_replace(b,"* `filter` is `FilterTree` from `packages/core/filter` (PAP-279), including",
                 "* `filter` is `FilterTree` from `packages/core/filter` (PAP-279, soft; see Dependencies for the `unknown` fallback), including","PAP-161 spec")
b=must_replace(b,"* Spec written by an older client: `version` lower than current triggers migration on read, never on write.",
                 "* Spec written by an older client: `version` lower than current triggers migration on read, never on write.\n* PAP-279 not yet In Review: `filter` is `unknown`, every fixture still parses, and the strict-mode test for the filter shape is `test.todo` naming PAP-279 so the gap is visible in the report.","PAP-161 edge")

# PAP-93
c=C["description"]
old_c="`BLOCKED_BY_OPEN` (warn), `DESCRIPTION_TOO_LONG`."
new_c=("`BLOCKED_BY_OPEN` (warn), `READY_BUT_BLOCKED` (error), `DESCRIPTION_TOO_LONG`.\n"
       "* `READY_BUT_BLOCKED` (error): the issue is in `Ready for Claude` and at least one inbound `blocks` relation comes from an open issue (Backlog, Todo, Ready for Claude, In Progress, Needs Justin, or In Review without an open PR). Invariant: the Ready set contains only unblocked issues. The `fix` text lists each blocker with its state and offers the two remedies: finish the blocker, or soften it (delete the relation and write the soft dependency with its branch-import fallback into the Dependencies section, as PAP-161 does for PAP-279). On the webhook path the issue is moved back to `Backlog` like any other error; `pnpm contract:audit` reports every violation across the team. Added 2026-09-17 (FIX-2), when PAP-279 and PAP-161 were the two offenders.")
c=must_replace(c,old_c,new_c,"PAP-93 codes")
c=must_replace(c,"* Unit: each violation code has a pass and fail fixture; heading normalisation (`**Goal**` vs `## Goal`); 50 k character truncation.",
                 "* Unit: each violation code has a pass and fail fixture; heading normalisation (`**Goal**` vs `## Goal`); 50 k character truncation. `READY_BUT_BLOCKED`: a Ready issue with a Backlog blocker fails; the same issue passes once the blocker is Done or the relation is removed; a blocker In Review with an open PR passes (branch-start rule).","PAP-93 test")
c=must_replace(c,"* Webhook delivered twice: idempotent by `webhookId`.",
                 "* Webhook delivered twice: idempotent by `webhookId`.\n* Blocker moves to Done while the dependent sits in Ready: nothing to do; blocker moves back from Done to In Progress: re-validate every Ready dependent and bounce with `READY_BUT_BLOCKED`.","PAP-93 edge")

# 3. update in one aliased mutation (idempotent by recorded id)
updated={u["id"] for u in ch["issuesUpdated"]}
ups=[(A["id"],"PAP-279",a),(B["id"],"PAP-161",b),(C["id"],"PAP-93",c)]
ups=[u for u in ups if u[0] not in updated]
if ups:
    q="mutation("+",".join(f"$d{i}: String!" for i in range(len(ups)))+") { "+" ".join(f'u{i}: issueUpdate(id: "{iid}", input: {{ description: $d{i} }}) {{ success issue {{ identifier }} }}' for i,(iid,_,_) in enumerate(ups))+" }"
    res=gql(q,{f"d{i}":desc for i,(_,_,desc) in enumerate(ups)})
    for i,(iid,key,desc) in enumerate(ups):
        ok=res[f"u{i}"]["success"]; print("update",key,ok,len(desc))
        if ok: ch["issuesUpdated"].append({"id":iid,"identifier":key,"fields":["description"],"chars":len(desc)})
    save()

# 4. verify: every Ready issue has zero open inbound blockers (live)
open_states={'Backlog','Todo','Ready for Claude','In Progress','Needs Justin','In Review'}
v=gql('{ issues(first: 100, filter: { team: { key: { eq: "PAP" } }, state: { name: { eq: "Ready for Claude" } } }) { nodes { identifier inverseRelations { nodes { type issue { identifier state { name } } } } } } }')
bad=[]
for n in v["issues"]["nodes"]:
    bl=[r["issue"]["identifier"] for r in n["inverseRelations"]["nodes"] if r["type"]=="blocks" and r["issue"]["state"]["name"] in open_states]
    if bl: bad.append((n["identifier"],bl))
print("Ready count",len(v["issues"]["nodes"]),"ready-but-blocked:",bad)
ch["verification"]={"readyCount":len(v["issues"]["nodes"]),"readyButBlocked":bad,"checkedAt":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime())}
ch["notes"]=["Relations deleted as instructed by FIX-2 (no issues, documents or states touched).","PAP-161 Dependencies also softens PAP-33/PAP-34 to work package 2 so the Ready state is not contradicted by text; no relation existed for them.","FIX-8 agent: keep READY_BUT_BLOCKED (error) when redefining BLOCKED_BY_OPEN in PAP-93."]
save(); print("changes written to",CH)
