import sys; sys.path.insert(0,os.environ.get("PAPEROS_PLAN_DIR", ".") + "/round2/fix4")
from common import *
ch=load_ch()
def must(text,old,new,who):
    if new in text: return text  # already applied
    if old not in text: print(f"ANCHOR MISSING in {who}: {old[:90]!r}"); sys.exit(1)
    return text.replace(old,new,1)

# ---- A. label
lab=[l for l in ch["labelsCreated"] if l["name"]=="Deferred"]
if not lab:
    d=gql('{ team(id:"0ee78894-89f8-4376-a829-f8685dbc1868") { labels(first:100, filter:{name:{eq:"Deferred"}}) { nodes { id name } } } }')
    nodes=d["team"]["labels"]["nodes"]
    if nodes:
        lab=[{"id":nodes[0]["id"],"name":"Deferred","note":"already existed"}]
    else:
        d=gql('mutation($input: IssueLabelCreateInput!) { issueLabelCreate(input:$input) { success issueLabel { id name } } }',
              {"input":{"teamId":"0ee78894-89f8-4376-a829-f8685dbc1868","name":"Deferred","color":"#8A8F98",
                        "description":"Deferred to v0.2 by the Execution Schedule. Not claimable before 10-01; NJ-14 stop-loss (09-27) can remove the label to reinstate."}})
        r=d["issueLabelCreate"]; assert r["success"], r
        lab=[{"id":r["issueLabel"]["id"],"name":"Deferred"}]
    ch["labelsCreated"]+=lab; save_ch(ch)
DEF_ID=lab[0]["id"]; print("Deferred label",DEF_ID)

# ---- B. delete relation PAP-190 -> PAP-192
REL="8e549412-cd75-437f-a21e-c1c16f02d1e4"
if REL not in {r["id"] for r in ch["relationsDeleted"]}:
    d=gql(f'mutation {{ issueRelationDelete(id:"{REL}") {{ success }} }}')
    assert d["issueRelationDelete"]["success"]
    ch["relationsDeleted"].append({"id":REL,"relation":"PAP-190 blocks PAP-192","nowSoft":True}); save_ch(ch)
    print("deleted relation",REL)

# ---- text edits
DEP190_OLD="platform OAuth apps (Needs Justin, one item covering all five). Blocks PAP-192."
DEP190_NEW=("platform OAuth apps (Needs Justin, one item covering all five). "
  "Consumed by PAP-192 (soft; the relation `PAP-190 blocks PAP-192` was removed on 2026-09-17, FIX-4, because this issue is Deferred to v0.2 while PAP-192 is scheduled for 09-28): "
  "the content agent only drafts, into `social.posts.create` when this issue exists and otherwise into its own `campaign_draft` approval queue, so it does not wait for this issue. "
  "Publishing anything PAP-192 drafts waits for this issue; when it ships, the composer imports approved `campaign_draft` rows and PAP-192 switches its length check to `validatePost`.")
DEP192_OLD="PAP-190 (hard), PAP-104 (hard), PAP-105, PAP-110, PAP-111, PAP-109, PAP-60, PAP-133, PAP-96, PAP-191 and PAP-193 (soft). Justin approves the character once via Needs Justin."
DEP192_NEW=("PAP-104 (hard), PAP-105, PAP-110, PAP-111, PAP-109, PAP-60, PAP-133, PAP-96. "
  "PAP-190 soft (relation `PAP-190 blocks PAP-192` removed on 2026-09-17, FIX-4; PAP-190 is labelled `Deferred`, v0.2): this agent drafts and never publishes, so it does not wait for the scheduler. "
  "If `social.posts.create` does not exist when you start, file social drafts through `campaign.drafts.create` into a `campaign_draft (id, tenant_id, channel, variant_body, media_slots jsonb, link_url, sources jsonb, confidence, status: pending_approval|approved|rejected, source: agent, source_hash, created_by_principal)` table owned by this issue, shown in the same approval queue UI, "
  "and enforce lengths with a `platformLimits` constant (X 280, LinkedIn 3000, YouTube title under 100) copied from the PAP-190 spec with a `// TODO(PAP-190): replace with validatePost` marker; PAP-190 imports approved rows when it ships. "
  "PAP-191 and PAP-193 soft (channel skipped if absent). Justin approves the character once via Needs Justin.")
SPEC192_OLD="* Limits from PAP-190 `validatePost`; drafts never exceed platform lengths."
SPEC192_NEW="* Limits from PAP-190 `validatePost` when it exists, otherwise the `platformLimits` constant (see Dependencies); drafts never exceed platform lengths."
IFACE192_OLD="draft procedures (PAP-190 hard; PAP-191 and PAP-193 soft, channel skipped if absent)"
IFACE192_NEW="draft procedures (PAP-190 soft, with the `campaign_draft` fallback in Dependencies; PAP-191 and PAP-193 soft, channel skipped if absent)"
SPEC96_OLD="* Character resolution: `Character/*` label, else project default from `roster.json`, else `Needs Justin`."
SPEC96_NEW=(SPEC96_OLD+"\n* Claim filter: never claim an issue labelled `Deferred` (the Execution Schedule's v0.2 set, 28 issues on 2026-09-17; NJ-14 on 09-27 can reinstate one by removing the label). "
  "`claimNext()` adds `labels: { none: { name: { eq: \"Deferred\" } } }` to the Linear filter and re-checks the fetched issue's labels before writing the claim; a `Deferred` issue found in `Ready for Claude` is skipped with a `linearComment` `not claimable: labelled Deferred (Execution Schedule v0.2)` once per issue and left for PAP-93 to bounce. The same exclusion applies to promotion and to any stretch-pool claim until the label is gone.")
EDGE96_OLD="* Branch exists on origin: check out and rebase rather than fail."
EDGE96_NEW=EDGE96_OLD+"\n* Label added after fetch: an issue labelled `Deferred` between poll and claim is caught by the pre-claim re-check, not by the `updatedAt` guard alone."

done_ids={u["identifier"] for u in ch["issuesUpdated"]}
targets=[k for k in DEFERRED_IDS+["PAP-192","PAP-96"] if k not in done_ids]
print("to update:",len(targets))
for i in range(0,len(targets),10):
    chunk=targets[i:i+10]
    # re-fetch live right before writing
    q="{ "+" ".join(f'i{j}: issue(id:"{k}") {{ id identifier priority description labels {{ nodes {{ id name }} }} }}' for j,k in enumerate(chunk))+" }"
    live=gql(q)
    vars={}; parts=[]; decl=[]
    for j,k in enumerate(chunk):
        it=live[f"i{j}"]; desc=it["description"]; inp={}
        if k in DEFERRED_IDS:
            if NOTE not in desc: desc=desc.replace("**Goal**\n\n","**Goal**\n\n"+NOTE+"\n\n",1)
            inp["priority"]=4
            if DEF_ID not in {l["id"] for l in it["labels"]["nodes"]}: inp["addedLabelIds"]=[DEF_ID]
        if k=="PAP-190": desc=must(desc,DEP190_OLD,DEP190_NEW,k)
        if k=="PAP-192":
            desc=must(desc,DEP192_OLD,DEP192_NEW,k); desc=must(desc,SPEC192_OLD,SPEC192_NEW,k); desc=must(desc,IFACE192_OLD,IFACE192_NEW,k)
        if k=="PAP-96":
            desc=must(desc,SPEC96_OLD,SPEC96_NEW,k); desc=must(desc,EDGE96_OLD,EDGE96_NEW,k)
        if desc!=it["description"]: inp["description"]=desc
        if not inp: print(k,"nothing to do"); ch["issuesUpdated"].append({"id":it["id"],"identifier":k,"fields":[],"note":"already applied"}); continue
        vars[f"id{j}"]=it["id"]; vars[f"in{j}"]=inp
        decl+= [f"$id{j}: String!", f"$in{j}: IssueUpdateInput!"]
        parts.append(f'u{j}: issueUpdate(id:$id{j}, input:$in{j}) {{ success issue {{ id identifier priority labels {{ nodes {{ name }} }} }} }}')
    if not parts: save_ch(ch); continue
    res=gql("mutation("+", ".join(decl)+") { "+" ".join(parts)+" }",vars)
    for j,k in enumerate(chunk):
        if f"u{j}" not in res: continue
        r=res[f"u{j}"]; assert r["success"], (k,r)
        ch["issuesUpdated"].append({"id":r["issue"]["id"],"identifier":k,"fields":sorted(vars[f"in{j}"].keys()),"priorityAfter":r["issue"]["priority"],"labelsAfter":[l["name"] for l in r["issue"]["labels"]["nodes"]]})
        print("updated",k,sorted(vars[f"in{j}"].keys()),r["issue"]["priority"],[l["name"] for l in r["issue"]["labels"]["nodes"]])
    save_ch(ch)

# ---- E. schedule document
if not any(u.get("documentId")==SCHED_DOC and u.get("success") for u in ch["documentUpdates"]):
    d=gql(f'{{ document(id:"{SCHED_DOC}") {{ id content updatedAt }} }}')
    c=d["document"]["content"]
    OLD1="($812 of allowances). Nothing scheduled depends on them."
    NEW1=("($812 of allowances). Each carries the team label `Deferred`, priority 4 and a deferral line under Goal (FIX-4, 2026-09-17); PAP-96 never claims a `Deferred` issue and promotion skips them. "
          "Two scheduled issues used to depend on this set and both edges were made soft on 2026-09-17: PAP-235 → PAP-180 (FIX-1; invoices render PDFs with their own template until the theme lands) and PAP-190 → PAP-192 (FIX-4; the content agent drafts into its own `campaign_draft` queue and never publishes). "
          "After those two deletions no `blocks` edge runs from a deferred issue to a scheduled one; the only edges out of the set stay inside it (PAP-230/231 → 232, PAP-276 → 277 → 278).")
    OLD2="4. **Stretch pool.** Deferred issues are claimable only after NJ-14 says go and while the plan line is under 100 percent; cheapest first, never an L."
    NEW2="4. **Stretch pool.** Deferred issues are claimable only after NJ-14 says go and while the plan line is under 100 percent; cheapest first, never an L. Reinstating one means Atlas removes its `Deferred` label, restores its priority and deletes the deferral line under Goal; until then PAP-96 refuses to claim it."
    c2=must(c,OLD1,NEW1,"sched doc"); c2=must(c2,OLD2,NEW2,"sched doc")
    if c2!=c:
        r=gql('mutation($id: String!, $input: DocumentUpdateInput!) { documentUpdate(id:$id, input:$input) { success document { id updatedAt } } }',{"id":SCHED_DOC,"input":{"content":c2}})
        assert r["documentUpdate"]["success"]
        ch["documentUpdates"].append({"documentId":SCHED_DOC,"title":"PaperOS Execution Schedule","section":"1. Deferred to v0.2 bullet; 5. Stretch pool","success":True,"verifiedUpdatedAt":r["documentUpdate"]["document"]["updatedAt"]})
        open(R2+"/fix4/_sched_doc_after.md","w").write(c2)
        print("doc updated",r["documentUpdate"]["document"]["updatedAt"])
    else:
        ch["documentUpdates"].append({"documentId":SCHED_DOC,"success":True,"note":"already applied"})
    save_ch(ch)
ch["requestsUsed"]=ch.get("requestsUsed",0)+REQ["n"]
save_ch(ch); print("requests this run",REQ["n"])
