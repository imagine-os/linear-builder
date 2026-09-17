import json,os,sys,time,re,urllib.request
KEY=os.environ.get("LINEAR_API_KEY","placeholder")
CH="changes-fix-FIX-3 child-blockers-umbrella-rule.json"
ch=json.load(open(CH)); 
def save(): json.dump(ch,open(CH,"w"),indent=1)
def gql(q,v=None):
    for attempt in range(6):
        req=urllib.request.Request("https://api.linear.app/graphql",data=json.dumps({"query":q,"variables":v}).encode(),headers={"Authorization":KEY,"Content-Type":"application/json"})
        try:
            with urllib.request.urlopen(req,timeout=90) as r: d=json.load(r)
        except urllib.error.HTTPError as e:
            txt=e.read().decode()
            if e.code==429 or "RATELIMITED" in txt: print("rate limited; sleeping 60s"); time.sleep(60); continue
            print("HTTP",e.code,txt[:800]); sys.exit(1)
        time.sleep(0.3)
        if d.get("errors"):
            if any(er.get("extensions",{}).get("code")=="RATELIMITED" for er in d["errors"]): time.sleep(60); continue
            print("GQL errors:",json.dumps(d["errors"])[:1500]); sys.exit(1)
        return d["data"]
UMBRELLA=("**Umbrella rule.** An issue with sub-issues is an umbrella. It is never moved to Ready for Claude and never claimed; the orchestrator skips it and the validator returns error `UMBRELLA_NOT_CLAIMABLE`. Children are claimed like any issue. When all children are Done, the session that finishes the last child runs the umbrella's integration test, attaches the evidence to the umbrella and moves it to In Review.")
def section_end(d,name):
    m=re.search(r'^\*\*'+name+r'\*\*\s*$',d,re.M)
    if not m: print("no section",name); sys.exit(1)
    n=re.search(r'^\*\*[^*\n]+\*\*\s*$',d[m.end():],re.M)
    return m.end()+n.start() if n else len(d)
def insert_at_section_end(d,name,text):
    p=section_end(d,name); head=d[:p].rstrip("\n"); return head+"\n"+text+"\n\n"+d[p:].lstrip("\n")
def must_replace(d,old,new,who):
    if old not in d: print("ANCHOR MISSING",who,old[:80]); sys.exit(1)
    return d.replace(old,new,1)
live=gql('{ a: issue(id:"PAP-92"){ id description } b: issue(id:"PAP-93"){ id description } c: issue(id:"PAP-96"){ id description } d: issue(id:"PAP-254"){ id description } }')
ups=[]
# PAP-92 playbook
a=live["a"]["description"]
if "UMBRELLA_NOT_CLAIMABLE" not in a:
    a=insert_at_section_end(a,"Spec","* "+UMBRELLA+" The playbook carries this paragraph verbatim in its claim step and in the FAQ (\"Why can I not claim PAP-67?\"). Relations: every child carries the external `blocks` relations it needs (added 2026-09-17, FIX-3), so a child in Ready for Claude is genuinely unblocked; the last child in build order also blocks whatever the umbrella blocks, so downstream readiness follows the real work.")
    a=insert_at_section_end(a,"Definition of done","* The playbook states the Umbrella rule verbatim (never claim an umbrella; last child's session runs the integration test and moves the umbrella to In Review).")
    ups.append(("PAP-92",live["a"]["id"],a))
# PAP-93 contract
b=live["b"]["description"]
if "UMBRELLA_NOT_CLAIMABLE" not in b:
    b=must_replace(b,"`READY_BUT_BLOCKED` (error), `DESCRIPTION_TOO_LONG`.","`READY_BUT_BLOCKED` (error), `UMBRELLA_NOT_CLAIMABLE` (error), `DESCRIPTION_TOO_LONG`.","PAP-93 codes")
    b=insert_at_section_end(b,"Spec","* `UMBRELLA_NOT_CLAIMABLE` (error): the issue has at least one sub-issue (`children.nodes.length > 0`) and is in `Ready for Claude`, `In Progress` or is the target of a claim. "+UMBRELLA+" The `fix` text lists the children with their states and names the first child in build order (the child with no sibling blocker) as the thing to claim instead. On the webhook path the umbrella is moved back to `Backlog` like any other error, without a `needs-contract` label (the issue is well-formed, only unclaimable). Added 2026-09-17 (FIX-3); the 16 split parents PAP-19, 20, 21, 28, 35, 36, 45, 54, 57, 59, 65, 67, 81, 82, 85, 88 are the current umbrellas.")
    b=insert_at_section_end(b,"Test plan","* `UMBRELLA_NOT_CLAIMABLE`: an issue with two Backlog children moved to Ready fails and is bounced to Backlog; the same issue with all children Done and an integration-test attachment moved to In Review passes; a leaf issue never triggers the code.")
    ups.append(("PAP-93",live["b"]["id"],b))
# PAP-96 orchestrator
c=live["c"]["description"]
if "UMBRELLA_NOT_CLAIMABLE" not in c:
    c=insert_at_section_end(c,"Spec","* Claims: the poll never claims an issue that has sub-issues. "+UMBRELLA+" `pickNext()` filters `children.nodes.length === 0` before ordering; when the last child of an umbrella reaches Done, the orchestrator appends `UMBRELLA_CLOSE: <parent identifier>` to that session's prompt so the session runs the parent's integration test (the parent's Definition of done and Test plan), attaches the evidence to the parent and moves the parent to In Review; if the session ends without doing so, the orchestrator posts `umbrella-close pending` on the parent and re-queues one `umbrella-close` session against the parent (this is the only case in which a session is launched on an umbrella, and it must not change any child).")
    c=insert_at_section_end(c,"Test plan","* Umbrella rule: fixture with an umbrella in Ready for Claude and two leaf children (one Ready, one Backlog) — `pickNext()` returns the Ready leaf and never the umbrella; marking the second child Done triggers exactly one `UMBRELLA_CLOSE` prompt and, if that session ends without moving the parent, exactly one re-queued `umbrella-close` session.")
    ups.append(("PAP-96",live["c"]["id"],c))
# PAP-254: PAP-89 is a consumer, relation PAP-254 blocks PAP-89 now exists
d=live["d"]["description"]
old="Both sibling children (hard), PAP-94, PAP-89 (hard). Soft: PAP-97, PAP-52, PAP-133."
if old in d:
    d=d.replace(old,"Both sibling children (hard), PAP-94 (hard). PAP-89 is a consumer, not a dependency: the release train (PAP-88, and this child as its last step) blocks PAP-89; the certification flow links the digest when PAP-89 exists and until then the RC comment carries the gate summary itself. Soft: PAP-97, PAP-52, PAP-133. Relations added 2026-09-17 (FIX-3): PAP-94 blocks this issue; this issue blocks PAP-89.",1)
    ups.append(("PAP-254",live["d"]["id"],d))
elif "PAP-89 is a consumer" not in d:
    print("PAP-254 anchor missing; current deps:",re.search(r'\*\*Dependencies\*\*\s*\n+(.*?)\n\n',d,re.S).group(1)[:300])
done={u["identifier"] for u in ch["issuesUpdated"]}
ups=[u for u in ups if u[0] not in done]
print("updating:",[u[0] for u in ups])
if ups:
    q="mutation("+",".join(f"$in{j}: IssueUpdateInput!, $id{j}: String!" for j in range(len(ups)))+") { "+" ".join(f"u{j}: issueUpdate(id: $id{j}, input: $in{j}) {{ success }}" for j in range(len(ups)))+" }"
    v={}
    for j,(ident,iid,txt) in enumerate(ups): v[f"id{j}"]=iid; v[f"in{j}"]={"description":txt}
    res=gql(q,v)
    for j,(ident,iid,txt) in enumerate(ups):
        ok=res[f"u{j}"]["success"]; print(ident,ok,len(txt))
        if ok: ch["issuesUpdated"].append({"id":iid,"identifier":ident,"fields":["description"],"chars":len(txt)})
    save()
