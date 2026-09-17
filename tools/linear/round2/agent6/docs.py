"""Publish the threat model document and the pending-issues document to the Quality Pipeline project (idempotent)."""
import sys, os, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lin, specs
ch=lin.load_changes(); ch.setdefault("documents",[])
created={c["key"]:c["identifier"] for c in ch.get("created",[])}
def resolve(desc): return re.sub(r"\{\{([^}]+)\}\}", lambda m: created.get(m.group(1), f"[{m.group(1)}]"), desc)
QP=lin.PROJECTS["Quality Pipeline"]["id"]
here=os.path.dirname(os.path.abspath(__file__))
# 1. pending issues document
pend=[it for it in specs.ISSUES if it["key"] not in created]
title_p=f"Round 2 pending issues: security ({len(pend)})"
if not any(d["title"]==title_p for d in ch["documents"]) and pend:
    parts=[f"# {title_p}\n", "> Created 2026-09-17 by the round-2 security planning session. Linear refused `issueCreate` with `USAGE_LIMIT_EXCEEDED` (free plan, team PAP at 275 issues). Each issue below is fully specified (Goal, Scope, Spec, Interface contract, Definition of done, Test plan, Demo, Edge cases, Dependencies, Agent, Size) and is created idempotently by `round2/agent6/create_issues.py` with labels, milestone, priority and `blocks` relations once the plan is upgraded. The PaperOS Security & Threat Model document cites them as `[security/<key>]`.\n", "## Contents\n"]
    for it in pend: parts.append(f"* `{it['key']}` - {it['title']} ({it['project']}, Phase/{it['phase']}, priority {it['priority']})")
    parts.append("")
    for it in pend:
        parts.append(f"## {it['title']}\n")
        parts.append(f"`{it['key']}` | project: {it['project']} | milestone: {it['milestone']} | Phase/{it['phase']}, Type/{it['type']}, {', '.join(it['surfaces'])} | priority {it['priority']} | size {it['size']} | state: {it['state']} | blocked by: {', '.join(it['blockedBy']) or 'none'} | blocks: {', '.join(it['blocks']) or 'none'}\n")
        parts.append(resolve(it["description"]).strip()+"\n")
    content="\n".join(parts)
    print("pending doc chars", len(content))
    d=lin.gql("mutation($i: DocumentCreateInput!){ d: documentCreate(input:$i){ success document{ id url title } } }",{"i":{"title":title_p,"content":content,"projectId":QP}})
    doc=d["d"]["document"]; ch["documents"].append({"project":"Quality Pipeline","id":doc["id"],"url":doc["url"],"title":doc["title"],"pendingKeys":[it["key"] for it in pend]}); lin.save_changes(ch); print("created", doc["url"])
else: print("pending doc exists or nothing pending")
# 2. threat model document
title_t="PaperOS Security & Threat Model"
tm=open(os.path.join(here,"threat-model.md")).read()
pdoc=[d for d in ch["documents"] if d["title"].startswith("Round 2 pending issues: security")]
if pdoc:
    tm=tm.replace('the companion document "Round 2 pending issues: security (11)"', f'the companion document [Round 2 pending issues: security (11)]({pdoc[0]["url"]})')
tm=resolve(tm.replace("[security/","{{security/").replace("]",  "]")) if False else tm
if not any(d["title"]==title_t for d in ch["documents"]):
    d=lin.gql("mutation($i: DocumentCreateInput!){ d: documentCreate(input:$i){ success document{ id url title } } }",{"i":{"title":title_t,"content":tm,"projectId":QP}})
    doc=d["d"]["document"]; ch["documents"].append({"project":"Quality Pipeline","id":doc["id"],"url":doc["url"],"title":doc["title"]}); lin.save_changes(ch); print("created", doc["url"])
else: print("threat model doc exists")
print(json.dumps(ch["documents"],indent=1))
