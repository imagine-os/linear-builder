#!/usr/bin/env python3
"""Round 4 read-only snapshot of Linear team PAP.

Writes plan/linear-snapshot-live.json (same top-level shape as the round-3 snapshot: takenAt, team, subscription,
states, labels, projects, issues; plus cycles, initiatives, templates, views, documents, projectUpdates and a
teamSettings block) and plan/round4/snapshot-summary.md (counts). Re-runnable; never mutates Linear.

  python3 tools/linear/round4/snapshot4.py            # writes into the repo
  PAPEROS_REPO=/path/to/repo OUT=/tmp/snap.json SUMMARY=/tmp/summary.md python3 tools/linear/round4/snapshot4.py

Key from LINEAR_API_KEY (raw value in the Authorization header). Paginates every connection, checks .errors, retries
on RATELIMITED, and keeps every request far under the 10k complexity cap (a page of 100 full issues costs about 500).
"""
import json, os, re, sys, time, urllib.request, urllib.error
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get("PAPEROS_REPO") or os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OUT = os.environ.get("OUT") or os.path.join(ROOT, "plan", "linear-snapshot-live.json")
SUMMARY = os.environ.get("SUMMARY") or os.path.join(ROOT, "plan", "round4", "snapshot-summary.md")
URL = "https://api.linear.app/graphql"
KEY = os.environ.get("LINEAR_API_KEY") or "placeholder"
TEAM = "0ee78894-89f8-4376-a829-f8685dbc1868"
PAGE_SLEEP = 0.25

MODEL_LABELS = {"Model: Fable 5.1", "Model: Opus 5", "Model: Sonnet 5", "Model: Haiku 4.5"}
SURFACES = ["Customer", "Staff", "Developer", "Agent"]
TYPES = ["Spec", "Build", "Review", "Research", "Docs", "Infra"]


def gql(query, variables=None, retries=6):
    body = json.dumps({"query": query, "variables": variables or {}}).encode()
    for attempt in range(retries):
        req = urllib.request.Request(URL, data=body, headers={"Authorization": KEY, "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                data = json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            raw = e.read().decode()
            try:
                data = json.loads(raw)
            except Exception:
                data = {"errors": [{"message": "HTTP %s %s" % (e.code, raw[:300])}]}
            if e.code == 429:
                time.sleep(60); continue
        except Exception as e:  # network hiccup
            print("retry after", repr(e)[:200], file=sys.stderr); time.sleep(5); continue
        errs = data.get("errors")
        if errs:
            codes = [(x.get("extensions") or {}).get("code") for x in errs]
            if "RATELIMITED" in codes:
                print("rate limited, sleeping 60 s", file=sys.stderr); time.sleep(60); continue
            raise RuntimeError(json.dumps(errs)[:1200])
        return data["data"]
    raise RuntimeError("retries exhausted")


def paged(query, path, variables=None, first=100, max_pages=200):
    """Yield nodes of a connection at `path` (dotted) with cursor pagination."""
    cursor = None
    for _ in range(max_pages):
        v = dict(variables or {}); v["cursor"] = cursor; v["first"] = first
        d = gql(query, v)
        for k in path.split("."):
            d = d[k]
        for n in d["nodes"]:
            yield n
        if not d["pageInfo"]["hasNextPage"] or not d["pageInfo"]["endCursor"]:
            return
        cursor = d["pageInfo"]["endCursor"]; time.sleep(PAGE_SLEEP)


def load_json(rel, default=None):
    p = os.path.join(ROOT, rel)
    if os.path.exists(p):
        with open(p) as f:
            return json.load(f)
    return default


def main():
    taken = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    prev = load_json("plan/linear-snapshot-live.json", {}) or {}
    prev_issues = {i["identifier"]: i for i in prev.get("issues", [])}
    ids = load_json("plan/linear-ids.json", {}) or {}
    r4ids = load_json("plan/round4/r4-ids.json", {}) or {}
    cross = load_json("plan/round4/gaps/cross-cutting.json", {}) or {}

    # ---- issue keys: round 1 (linear-ids), round 2 pending table, round 4 (r4-ids), then carry-over ----
    key_by_ident = {}
    for k, v in (ids.get("issues") or {}).items():
        if isinstance(v, dict) and v.get("identifier"):
            key_by_ident[v["identifier"]] = k
    pend = os.path.join(ROOT, "docs", "pending", "README.md")
    if os.path.exists(pend):
        for m in re.finditer(r"^\|\s*`([^`]+)`\s*\|\s*\[(PAP-\d+)\]", open(pend).read(), re.M):
            key_by_ident.setdefault(m.group(2), m.group(1))
    for k, v in r4ids.items():
        if isinstance(v, dict) and v.get("identifier"):
            key_by_ident.setdefault(v["identifier"], k)
    for ident, i in prev_issues.items():
        if i.get("key"):
            key_by_ident.setdefault(ident, i["key"])
    # round 3 module-system issues: plan/module-issues.json records key and title, not the identifier (matched by title below)
    module_key_by_title = {x["title"]: x["key"] for x in (load_json("plan/module-issues.json", {}) or {}).get("issues", []) if x.get("title") and x.get("key")}

    # ---- project keys: linear-ids projects (round 1), module-system, new round-4 projects ----
    proj_key_by_name = {v["name"]: k for k, v in (ids.get("projects") or {}).items() if isinstance(v, dict) and v.get("name")}
    proj_key_by_name.setdefault("Module System & Swap Tooling", "module-system")
    for p in cross.get("newProjects", []) or []:
        proj_key_by_name.setdefault(p["name"], p["key"])
    for p in prev.get("projects", []):
        if p.get("key"):
            proj_key_by_name.setdefault(p["name"], p["key"])

    # ---- team, settings, states, cycles ----
    t = gql('''query($t:String!){ team(id:$t){ id key name issueCount
        issueEstimationType issueEstimationAllowZero issueEstimationExtended defaultIssueEstimate
        cyclesEnabled cycleDuration cycleCooldownTime cycleStartDay upcomingCycleCount cycleIssueAutoAssignStarted cycleIssueAutoAssignCompleted cycleLockToActive
        triageEnabled triageIssueState{ id name type } defaultIssueState{ id name } activeCycle{ id number }
        states{ nodes{ id name type position } }
        cycles(first:50){ nodes{ id number name description startsAt endsAt completedAt progress } } }
      organization{ subscription{ type } } }''', {"t": TEAM})
    team = t["team"]
    settings = {k: team[k] for k in ["issueEstimationType", "issueEstimationAllowZero", "issueEstimationExtended", "defaultIssueEstimate",
                                     "cyclesEnabled", "cycleDuration", "cycleCooldownTime", "cycleStartDay", "upcomingCycleCount",
                                     "cycleIssueAutoAssignStarted", "cycleIssueAutoAssignCompleted", "cycleLockToActive", "triageEnabled"]}
    settings["triageIssueState"] = team["triageIssueState"]
    settings["defaultIssueState"] = team["defaultIssueState"]
    settings["activeCycle"] = team["activeCycle"]
    states = sorted([{"id": s["id"], "name": s["name"], "type": s["type"]} for s in team["states"]["nodes"]], key=lambda s: [x["position"] for x in team["states"]["nodes"] if x["id"] == s["id"]][0])
    cycles = sorted([{"id": c["id"], "number": c["number"], "name": c["name"], "description": c["description"], "startsAt": c["startsAt"], "endsAt": c["endsAt"],
                      "completedAt": c["completedAt"], "progress": c["progress"], "active": bool(team["activeCycle"] and team["activeCycle"]["id"] == c["id"])}
                     for c in team["cycles"]["nodes"]], key=lambda c: c["number"])
    subscription = (t["organization"]["subscription"] or {}).get("type")
    time.sleep(PAGE_SLEEP)

    # ---- labels (workspace and team, with group) ----
    labels = []
    for l in paged('''query($cursor:String,$first:Int){ issueLabels(first:$first, after:$cursor){ pageInfo{hasNextPage endCursor} nodes{ id name color isGroup parent{ id name } team{ key } } } }''', "issueLabels"):
        labels.append({"id": l["id"], "name": l["name"], "color": l["color"], "isGroup": l["isGroup"], "parent": {"name": l["parent"]["name"]} if l["parent"] else None,
                       "group": l["parent"]["name"] if l["parent"] else None, "team": l["team"]["key"] if l["team"] else None})
    label_group = {l["name"]: l["group"] for l in labels}
    time.sleep(PAGE_SLEEP)

    # ---- projects (team PAP only) ----
    projects = []
    PROJ_Q = '''query($cursor:String,$first:Int){ projects(first:$first, after:$cursor){ pageInfo{hasNextPage endCursor}
      nodes{ id name description content url color icon priority health progress startDate targetDate completedAt createdAt updatedAt
        status{ name type } lead{ id name } teams{ nodes{ id } }
        projectMilestones(first:20){ nodes{ id name description targetDate } }
        externalLinks{ nodes{ id label url } }
        projectUpdates(first:1){ nodes{ id body health createdAt url user{ name } } }
        initiatives{ nodes{ id name } }
        documents(first:20){ nodes{ id title url } } } } }'''
    for n in paged(PROJ_Q, "projects", first=20):
        if not any(x["id"] == TEAM for x in n["teams"]["nodes"]):
            continue
        upd = n["projectUpdates"]["nodes"]
        projects.append({
            "id": n["id"], "name": n["name"], "key": proj_key_by_name.get(n["name"]), "description": n["description"], "content": n["content"], "url": n["url"],
            "color": n["color"], "icon": n["icon"], "priority": n["priority"], "health": n["health"], "progress": n["progress"],
            "startDate": n["startDate"], "targetDate": n["targetDate"], "completedAt": n["completedAt"], "createdAt": n["createdAt"], "updatedAt": n["updatedAt"],
            "status": n["status"]["name"] if n["status"] else None, "statusType": n["status"]["type"] if n["status"] else None,
            "state": {"name": n["status"]["name"], "type": n["status"]["type"]} if n["status"] else None,
            "lead": n["lead"]["name"] if n["lead"] else None,
            "milestones": sorted([{"id": m["id"], "name": m["name"], "description": m["description"], "targetDate": m["targetDate"]} for m in n["projectMilestones"]["nodes"]], key=lambda m: (m["targetDate"] or "9", m["name"])),
            "links": [{"id": l["id"], "label": l["label"], "url": l["url"]} for l in n["externalLinks"]["nodes"]],
            "latestUpdate": {"id": upd[0]["id"], "body": upd[0]["body"], "health": upd[0]["health"], "createdAt": upd[0]["createdAt"], "url": upd[0]["url"], "user": (upd[0]["user"] or {}).get("name")} if upd else None,
            "initiatives": [{"id": x["id"], "name": x["name"]} for x in n["initiatives"]["nodes"]],
            "documents": [{"id": d["id"], "title": d["title"], "url": d["url"]} for d in n["documents"]["nodes"]],
        })
    proj_by_id = {p["id"]: p for p in projects}
    time.sleep(PAGE_SLEEP)

    # ---- issues ----
    ISSUE_Q = '''query($cursor:String,$first:Int,$team:ID!){ issues(first:$first, after:$cursor, orderBy:createdAt, filter:{team:{id:{eq:$team}}}){
      pageInfo{hasNextPage endCursor}
      nodes{ id identifier title description priority estimate dueDate url archivedAt createdAt updatedAt completedAt canceledAt startedAt sortOrder
        state{ id name type } labels{ nodes{ id name parent{ name } } } project{ id name } projectMilestone{ id name targetDate }
        cycle{ id number name startsAt endsAt } parent{ id identifier } children{ nodes{ identifier } } assignee{ name }
        relations{ nodes{ id type relatedIssue{ identifier } } } inverseRelations{ nodes{ id type issue{ identifier } } }
        attachments{ nodes{ id title subtitle url sourceType createdAt } } } } }'''
    issues = []
    for n in paged(ISSUE_Q, "issues", {"team": TEAM}, first=100):
        if n.get("archivedAt"):
            continue
        names = [l["name"] for l in n["labels"]["nodes"]]
        labels_full = [{"name": l["name"], "group": l["parent"]["name"] if l["parent"] else label_group.get(l["name"])} for l in n["labels"]["nodes"]]
        rel = [{"id": r["id"], "type": r["type"], "related": r["relatedIssue"]["identifier"]} for r in n["relations"]["nodes"] if r["relatedIssue"]]
        inv = [{"id": r["id"], "type": r["type"], "from": r["issue"]["identifier"]} for r in n["inverseRelations"]["nodes"] if r["issue"]]
        proj = n["project"]
        chunk = next((x for x in names if re.fullmatch(r"Chunk \d+", x)), None)
        issues.append({
            "identifier": n["identifier"], "id": n["id"], "title": n["title"], "description": n["description"],
            "state": n["state"]["name"], "stateId": n["state"]["id"], "stateType": n["state"]["type"],
            "priority": n["priority"], "estimate": n["estimate"], "dueDate": n["dueDate"],
            "cycle": {"id": n["cycle"]["id"], "number": n["cycle"]["number"], "name": n["cycle"]["name"], "startsAt": n["cycle"]["startsAt"], "endsAt": n["cycle"]["endsAt"]} if n["cycle"] else None,
            "labels": names, "labelIds": {l["name"]: l["id"] for l in n["labels"]["nodes"]}, "labelsFull": labels_full,
            "phase": next((x for x in names if x in ("P0", "P1", "P2")), None),
            "type": next((x for x in names if x in TYPES), None),
            "model": [x for x in names if x in MODEL_LABELS], "effort": [x for x in names if x.startswith("Effort: ")],
            "surfaces": [x for x in names if x in SURFACES], "deferred": "Deferred" in names, "chunk": chunk,
            "projectId": proj["id"] if proj else None, "projectName": proj["name"] if proj else None,
            "projectKey": proj_by_id.get(proj["id"], {}).get("key") if proj else None,
            "milestone": n["projectMilestone"]["name"] if n["projectMilestone"] else None, "milestoneId": n["projectMilestone"]["id"] if n["projectMilestone"] else None,
            "milestoneDate": n["projectMilestone"]["targetDate"] if n["projectMilestone"] else None,
            "projectMilestone": {"name": n["projectMilestone"]["name"], "targetDate": n["projectMilestone"]["targetDate"]} if n["projectMilestone"] else None,
            "parent": n["parent"]["identifier"] if n["parent"] else None, "children": [c["identifier"] for c in n["children"]["nodes"]],
            "blockedBy": sorted([r["from"] for r in inv if r["type"] == "blocks"], key=lambda s: int(s.split("-")[1])),
            "blocks": sorted([r["related"] for r in rel if r["type"] == "blocks"], key=lambda s: int(s.split("-")[1])),
            "relations": rel, "inverseRelations": inv,
            "attachments": [{"id": a["id"], "title": a["title"], "subtitle": a["subtitle"], "url": a["url"], "sourceType": a["sourceType"], "createdAt": a["createdAt"]} for a in n["attachments"]["nodes"]],
            "commentCount": 0, "assignee": n["assignee"]["name"] if n["assignee"] else None,
            "key": key_by_ident.get(n["identifier"]) or module_key_by_title.get(n["title"]), "url": n["url"],
            "createdAt": n["createdAt"], "updatedAt": n["updatedAt"], "startedAt": n["startedAt"], "completedAt": n["completedAt"], "canceledAt": n["canceledAt"],
        })
        if len(issues) % 100 == 0:
            print("issues so far", len(issues), file=sys.stderr)
    by_ident = {i["identifier"]: i for i in issues}
    time.sleep(PAGE_SLEEP)

    # ---- comment counts (one paged query over the team's comments; far cheaper than nesting comments per issue) ----
    cc = Counter()
    for c in paged('''query($cursor:String,$first:Int,$team:ID!){ comments(first:$first, after:$cursor, filter:{issue:{team:{id:{eq:$team}}}}){ pageInfo{hasNextPage endCursor} nodes{ id issue{ identifier } } } }''', "comments", {"team": TEAM}, first=250):
        if c["issue"]:
            cc[c["issue"]["identifier"]] += 1
    for ident, n in cc.items():
        if ident in by_ident:
            by_ident[ident]["commentCount"] = n
    time.sleep(PAGE_SLEEP)

    # ---- initiatives, templates, views, documents, project updates ----
    initiatives = []
    for n in paged('''query($cursor:String,$first:Int){ initiatives(first:$first, after:$cursor){ pageInfo{hasNextPage endCursor} nodes{ id name description content url status targetDate icon color createdAt updatedAt owner{ name } projects(first:50){ nodes{ id name } } } } }''', "initiatives", first=50):
        initiatives.append({"id": n["id"], "name": n["name"], "description": n["description"], "content": n["content"], "url": n["url"], "status": n["status"],
                            "targetDate": n["targetDate"], "icon": n["icon"], "color": n["color"], "owner": n["owner"]["name"] if n["owner"] else None,
                            "createdAt": n["createdAt"], "updatedAt": n["updatedAt"],
                            "projects": [{"id": p["id"], "name": p["name"], "key": proj_by_id.get(p["id"], {}).get("key")} for p in n["projects"]["nodes"]]})
    time.sleep(PAGE_SLEEP)
    tpl = gql('{ templates{ id name type description createdAt updatedAt team{ key } } }')["templates"]
    templates = [{"id": x["id"], "name": x["name"], "type": x["type"], "description": x["description"], "team": x["team"]["key"] if x["team"] else None, "createdAt": x["createdAt"], "updatedAt": x["updatedAt"]} for x in tpl]
    time.sleep(PAGE_SLEEP)
    views = []
    for n in paged('''query($cursor:String,$first:Int){ customViews(first:$first, after:$cursor){ pageInfo{hasNextPage endCursor} nodes{ id name description slugId icon color shared createdAt updatedAt team{ key } filterData } } }''', "customViews", first=50):
        slug = n["slugId"] or ""
        views.append({"id": n["id"], "name": n["name"], "description": n["description"], "slugId": slug,
                      "url": f"https://linear.app/paperos/view/{slug}" if slug else None, "icon": n["icon"], "color": n["color"], "shared": n["shared"],
                      "team": n["team"]["key"] if n["team"] else None, "filter": n["filterData"], "createdAt": n["createdAt"], "updatedAt": n["updatedAt"]})
    time.sleep(PAGE_SLEEP)
    documents = []
    for n in paged('''query($cursor:String,$first:Int){ documents(first:$first, after:$cursor){ pageInfo{hasNextPage endCursor} nodes{ id title url createdAt updatedAt project{ id name } initiative{ name } content } } }''', "documents", first=30):
        documents.append({"id": n["id"], "title": n["title"], "url": n["url"], "createdAt": n["createdAt"], "updatedAt": n["updatedAt"],
                          "project": n["project"]["name"] if n["project"] else None, "projectKey": proj_by_id.get((n["project"] or {}).get("id"), {}).get("key"),
                          "initiative": n["initiative"]["name"] if n["initiative"] else None, "contentLength": len(n["content"] or "")})
    time.sleep(PAGE_SLEEP)
    updates = []
    for n in paged('''query($cursor:String,$first:Int){ projectUpdates(first:$first, after:$cursor){ pageInfo{hasNextPage endCursor} nodes{ id body health createdAt url user{ name } project{ id name } } } }''', "projectUpdates", first=50):
        updates.append({"id": n["id"], "body": n["body"], "health": n["health"], "createdAt": n["createdAt"], "url": n["url"], "user": (n["user"] or {}).get("name"),
                        "project": n["project"]["name"] if n["project"] else None, "projectKey": proj_by_id.get((n["project"] or {}).get("id"), {}).get("key")})

    snap = {
        "takenAt": taken, "round": 4,
        "team": {"id": team["id"], "key": team["key"], "name": team["name"], "issueCount": team["issueCount"]},
        "subscription": subscription, "teamSettings": settings, "states": states, "labels": labels, "cycles": cycles,
        "projects": projects, "initiatives": initiatives, "templates": templates, "views": views, "documents": documents, "projectUpdates": updates,
        "issues": issues,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(snap, f, indent=1)

    # ---- summary ----
    canon = [i for i in issues if int(i["identifier"].split("-")[1]) >= 13 and i["state"] != "Duplicate"]
    leaves = [i for i in canon if not i["children"]]
    pts = lambda xs: sum(i["estimate"] or 0 for i in xs)
    by_state = Counter(i["state"] for i in issues)
    by_cycle = Counter((i["cycle"] or {}).get("name") or "(no cycle)" for i in canon)
    pts_cycle = {k: pts([i for i in canon if ((i["cycle"] or {}).get("name") or "(no cycle)") == k]) for k in by_cycle}
    by_proj = Counter(i["projectName"] or "(no project)" for i in canon)
    blocks = sum(len(i["blocks"]) for i in issues)
    dups = sum(1 for i in issues for r in i["relations"] if r["type"] == "duplicate")
    prev_n = len(prev.get("issues", [])) if prev else None
    prev_ids = set(prev_issues)
    new_ids = sorted([i["identifier"] for i in issues if i["identifier"] not in prev_ids], key=lambda s: int(s.split("-")[1]))
    est_hist = Counter(i["estimate"] for i in leaves)
    lines = [f"# Linear snapshot summary ({taken})", "",
             f"Written by `tools/linear/round4/snapshot4.py` to `plan/linear-snapshot-live.json`. Team **{team['key']}** ({team['name']}), plan `{subscription}`, team `issueCount` {team['issueCount']}.", "",
             "## Counts", "",
             f"* Issues (non-archived): **{len(issues)}**" + (f" (previous snapshot {prev.get('takenAt')}: {prev_n}; {len(new_ids)} new identifiers" + (f", {new_ids[0]}..{new_ids[-1]}" if new_ids else "") + ")" if prev_n else ""),
             f"* Canonical (PAP-13 upward, not Duplicate): **{len(canon)}**; leaves {len(leaves)}; umbrellas {len(canon) - len(leaves)}; Deferred {sum(1 for i in canon if i['deferred'])}",
             f"* By state: " + ", ".join(f"{k} {v}" for k, v in by_state.most_common()),
             f"* Relations: `blocks` {blocks}, `duplicate` {dups}; issues with a parent {sum(1 for i in issues if i['parent'])}",
             f"* Estimates: {sum(1 for i in canon if i['estimate'] is not None)} issues estimated, **{pts(canon)} points** (leaves {pts(leaves)}); histogram " + ", ".join(f"{k if k is not None else 'none'}: {v}" for k, v in sorted(est_hist.items(), key=lambda kv: (kv[0] is None, kv[0] or 0))),
             f"* Due dates: {sum(1 for i in canon if i['dueDate'])} issues; most common " + ", ".join(f"{k} ({v})" for k, v in Counter(i['dueDate'] for i in canon if i['dueDate']).most_common(4)),
             f"* Cycles: " + ", ".join(f"{k} {v} issues / {pts_cycle[k]} pts" for k, v in sorted(by_cycle.items())),
             f"* Chunk labels: " + (", ".join(f"{k} {v}" for k, v in sorted(Counter(i['chunk'] for i in canon if i['chunk']).items())) or "none"),
             f"* Attachments: {sum(len(i['attachments']) for i in issues)}; comments: {sum(cc.values())} on {len(cc)} issues",
             f"* Projects (team PAP): **{len(projects)}**; milestones {sum(len(p['milestones']) for p in projects)}; project updates {len(updates)}; project links {sum(len(p['links']) for p in projects)}",
             f"* Initiatives: {len(initiatives)} (" + ", ".join(f"{x['name']} -> {len(x['projects'])} projects" for x in initiatives) + ")",
             f"* Templates: {len(templates)} ({sum(1 for x in templates if x['type'] == 'issue')} issue, {sum(1 for x in templates if x['type'] == 'project')} project); views: {len(views)}; documents: {len(documents)}",
             f"* Team settings: estimation `{settings['issueEstimationType']}`, cycles {'on' if settings['cyclesEnabled'] else 'off'} ({settings['cycleDuration']} week, start day {settings['cycleStartDay']}), triage {'on' if settings['triageEnabled'] else 'off'} (state {settings['triageIssueState']['name'] if settings['triageIssueState'] else 'none'}), active cycle {settings['activeCycle']['number'] if settings['activeCycle'] else 'none'}",
             "", "## Issues per project", "", "| Project | Key | Canonical issues | Points | Ready | Deferred |", "|---|---|---|---|---|---|"]
    for p in sorted(projects, key=lambda p: p["name"]):
        mine = [i for i in canon if i["projectId"] == p["id"]]
        lines.append(f"| {p['name']} | `{p['key']}` | {len(mine)} | {pts(mine)} | {sum(1 for i in mine if i['state'] == 'Ready for Claude')} | {sum(1 for i in mine if i['deferred'])} |")
    no_proj = [i for i in canon if not i["projectId"]]
    if no_proj:
        lines.append(f"| (no project) | | {len(no_proj)} | {pts(no_proj)} | | |")
    lines += ["", "## Cycles", "", "| # | Name | Starts | Ends | Issues | Points | Active |", "|---|---|---|---|---|---|---|"]
    for c in cycles:
        mine = [i for i in canon if i["cycle"] and i["cycle"]["id"] == c["id"]]
        lines.append(f"| {c['number']} | {c['name']} | {c['startsAt'][:10]} | {c['endsAt'][:10]} | {len(mine)} | {pts(mine)} | {'yes' if c['active'] else ''} |")
    lines.append("")
    os.makedirs(os.path.dirname(SUMMARY), exist_ok=True)
    with open(SUMMARY, "w") as f:
        f.write("\n".join(lines))
    print("\n".join(lines[4:22]))
    print("wrote", OUT, "and", SUMMARY)


if __name__ == "__main__":
    main()
