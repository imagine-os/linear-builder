#!/usr/bin/env python3
"""Round 4 critique step 1: fresh read of every PAP issue (excluding PAP-1..12 and Duplicate/Canceled).
Writes plan/round4/critique-snapshot.json. Read-only."""
import json, os, sys, time, urllib.request, urllib.error, datetime
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "critique-snapshot.json")
URL = "https://api.linear.app/graphql"
KEY = os.environ.get("LINEAR_API_KEY") or "placeholder"
TEAM = "0ee78894-89f8-4376-a829-f8685dbc1868"

def gql(query, variables=None, retries=6):
    body = json.dumps({"query": query, "variables": variables or {}}).encode()
    for attempt in range(retries):
        req = urllib.request.Request(URL, data=body, headers={"Authorization": KEY, "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                data = json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            raw = e.read().decode()
            try: data = json.loads(raw)
            except Exception: data = {"errors": [{"message": "HTTP %s %s" % (e.code, raw[:300])}]}
            if e.code == 429: time.sleep(60); continue
        except Exception as e:
            print("retry after", repr(e)[:200], file=sys.stderr); time.sleep(5); continue
        errs = data.get("errors")
        if errs:
            codes = [(x.get("extensions") or {}).get("code") for x in errs]
            if "RATELIMITED" in codes: print("rate limited, sleeping 60 s", file=sys.stderr); time.sleep(60); continue
            raise RuntimeError(json.dumps(errs)[:1200])
        return data["data"]
    raise RuntimeError("retries exhausted")

Q = """
query($cursor: String, $team: String!) {
  team(id: $team) {
    issues(first: 20, after: $cursor, orderBy: createdAt) {
      pageInfo { hasNextPage endCursor }
      nodes {
        id identifier title number estimate priority dueDate createdAt updatedAt description
        state { id name type }
        project { id name }
        projectMilestone { id name targetDate }
        cycle { id number }
        labels { nodes { id name parent { name } } }
        parent { id identifier }
        children { nodes { id identifier } }
        relations { nodes { id type relatedIssue { identifier } } }
        inverseRelations { nodes { id type issue { identifier } } }
      }
    }
  }
}
"""
META = """
query($team: String!) {
  team(id: $team) { id key issueCount
    labels(first: 250) { nodes { id name parent { id name } isGroup } }
    states { nodes { id name type } }
  }
  projects(first: 50) { nodes { id name targetDate status { name }
    projectMilestones(first: 20) { nodes { id name targetDate } } } }
}
"""

def main():
    taken = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    meta = gql(META, {"team": TEAM})
    cursor = None; raw = []; pages = 0
    while pages < 200:
        d = gql(Q, {"cursor": cursor, "team": TEAM})["team"]["issues"]
        raw.extend(d["nodes"]); pages += 1
        if not d["pageInfo"]["hasNextPage"]: break
        cursor = d["pageInfo"]["endCursor"]
        if not cursor: break
        time.sleep(0.25)
    issues = []
    for n in raw:
        if n["number"] <= 12: continue
        if n["state"]["type"] in ("duplicate", "canceled"): continue
        issues.append({
            "id": n["id"], "identifier": n["identifier"], "number": n["number"], "title": n["title"],
            "estimate": n["estimate"], "priority": n["priority"], "dueDate": n["dueDate"],
            "createdAt": n["createdAt"], "updatedAt": n["updatedAt"], "description": n["description"] or "",
            "state": n["state"]["name"], "stateType": n["state"]["type"], "stateId": n["state"]["id"],
            "project": (n["project"] or {}).get("name"), "projectId": (n["project"] or {}).get("id"),
            "milestone": (n["projectMilestone"] or {}).get("name"), "milestoneId": (n["projectMilestone"] or {}).get("id"),
            "milestoneDate": (n["projectMilestone"] or {}).get("targetDate"),
            "cycle": (n["cycle"] or {}).get("number"),
            "labels": [{"id": l["id"], "name": l["name"], "group": (l["parent"] or {}).get("name")} for l in n["labels"]["nodes"]],
            "parent": (n["parent"] or {}).get("identifier"),
            "children": [c["identifier"] for c in n["children"]["nodes"]],
            "relations": [{"id": r["id"], "type": r["type"], "to": r["relatedIssue"]["identifier"] if r["relatedIssue"] else None} for r in n["relations"]["nodes"]],
            "inverseRelations": [{"id": r["id"], "type": r["type"], "from": r["issue"]["identifier"] if r["issue"] else None} for r in n["inverseRelations"]["nodes"]],
        })
    out = {"takenAt": taken, "teamIssueCount": meta["team"]["issueCount"], "rawCount": len(raw), "count": len(issues),
           "states": meta["team"]["states"]["nodes"], "labels": meta["team"]["labels"]["nodes"],
           "projects": meta["projects"]["nodes"], "issues": issues}
    json.dump(out, open(OUT, "w"), indent=1)
    print("taken", taken, "raw", len(raw), "kept", len(issues), "pages", pages)

if __name__ == "__main__":
    main()
