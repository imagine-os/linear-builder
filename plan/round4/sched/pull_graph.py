#!/usr/bin/env python3
"""Round 4 step 1: pull the live PAP issue graph for the schedule model.

Writes plan/round4/sched/graph.json: every non-archived PAP issue (excluding PAP-1..PAP-12, Duplicate/Canceled
states and Triage-state issues) with identifier, title, project, milestone target date, state, labels, estimate,
parent, children and `blocks` relations in both directions, plus the team's Chunk labels. Read-only.
"""
import json, os, sys, time, urllib.request, urllib.error, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "graph.json")
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
            try:
                data = json.loads(raw)
            except Exception:
                data = {"errors": [{"message": "HTTP %s %s" % (e.code, raw[:300])}]}
            if e.code == 429:
                time.sleep(60); continue
        except Exception as e:
            print("retry after", repr(e)[:200], file=sys.stderr); time.sleep(5); continue
        errs = data.get("errors")
        if errs:
            codes = [(x.get("extensions") or {}).get("code") for x in errs]
            if "RATELIMITED" in codes:
                print("rate limited, sleeping 60 s", file=sys.stderr); time.sleep(60); continue
            raise RuntimeError(json.dumps(errs)[:1200])
        return data["data"]
    raise RuntimeError("retries exhausted")


ISSUES_Q = """
query($cursor: String, $team: String!) {
  team(id: $team) {
    issues(first: 25, after: $cursor, orderBy: createdAt) {
      pageInfo { hasNextPage endCursor }
      nodes {
        id identifier title number estimate priority dueDate createdAt updatedAt
        state { name type }
        project { id name }
        projectMilestone { id name targetDate }
        labels { nodes { id name parent { name } } }
        parent { identifier }
        children { nodes { identifier } }
        relations { nodes { id type relatedIssue { identifier } } }
        inverseRelations { nodes { id type issue { identifier } } }
      }
    }
  }
}
"""

LABELS_Q = """
query($team: String!) {
  team(id: $team) {
    id key name
    labels(first: 250) { nodes { id name color parent { id name } isGroup } }
  }
}
"""


def main():
    taken = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    team = gql(LABELS_Q, {"team": TEAM})["team"]
    labels = team["labels"]["nodes"]
    cursor = None
    raw = []
    for page in range(200):
        d = gql(ISSUES_Q, {"cursor": cursor, "team": TEAM})["team"]["issues"]
        raw.extend(d["nodes"])
        print("page", page + 1, "issues so far", len(raw), file=sys.stderr)
        if not d["pageInfo"]["hasNextPage"]:
            break
        cursor = d["pageInfo"]["endCursor"]
        time.sleep(0.25)
    excluded = {"lowNumber": [], "duplicateOrCanceled": [], "triage": []}
    issues = {}
    for n in raw:
        num = n["number"]
        st = n["state"]["name"]; sty = n["state"]["type"]
        if num < 13:
            excluded["lowNumber"].append(n["identifier"]); continue
        if sty in ("canceled", "duplicate") or st in ("Duplicate", "Canceled"):
            excluded["duplicateOrCanceled"].append(n["identifier"]); continue
        if sty == "triage" or st == "Triage":
            excluded["triage"].append(n["identifier"]); continue
        labs = [l["name"] for l in n["labels"]["nodes"]]
        groups = {l["name"]: (l["parent"] or {}).get("name") for l in n["labels"]["nodes"]}
        def pick(prefix=None, names=None, group=None):
            for l in labs:
                if names and l in names: return l
                if prefix and l.startswith(prefix): return l
                if group and groups.get(l) == group: return l
            return None
        issues[n["identifier"]] = {
            "id": n["id"], "identifier": n["identifier"], "number": num, "title": n["title"],
            "project": n["project"]["name"] if n["project"] else None,
            "milestone": n["projectMilestone"]["name"] if n["projectMilestone"] else None,
            "milestoneTarget": n["projectMilestone"]["targetDate"] if n["projectMilestone"] else None,
            "state": st, "stateType": sty, "estimate": n["estimate"], "priority": n["priority"],
            "dueDate": n["dueDate"],
            "labels": labs,
            "phase": pick(names={"P0", "P1", "P2"}),
            "type": pick(names={"Spec", "Build", "Review", "Research", "Docs", "Infra"}),
            "model": pick(prefix="Model: "),
            "effort": pick(prefix="Effort: "),
            "deferred": "Deferred" in labs,
            "chunk": pick(group="Chunk") or pick(prefix="Chunk"),
            "parent": n["parent"]["identifier"] if n["parent"] else None,
            "children": sorted(c["identifier"] for c in n["children"]["nodes"]),
            "blocks": sorted({r["relatedIssue"]["identifier"] for r in n["relations"]["nodes"] if r["type"] == "blocks" and r["relatedIssue"]}),
            "blockedBy": sorted({r["issue"]["identifier"] for r in n["inverseRelations"]["nodes"] if r["type"] == "blocks" and r["issue"]}),
        }
    # restrict relations to the retained set and make them symmetric
    keep = set(issues)
    for i in issues.values():
        i["children"] = [c for c in i["children"] if c in keep]
        if i["parent"] not in keep: i["parent"] = None
    for i in issues.values():
        for b in i["blocks"]:
            if b in keep and i["identifier"] not in issues[b]["blockedBy"]:
                issues[b]["blockedBy"].append(i["identifier"])
        for b in i["blockedBy"]:
            if b in keep and i["identifier"] not in issues[b]["blocks"]:
                issues[b]["blocks"].append(i["identifier"])
    for i in issues.values():
        i["blocks"] = sorted(b for b in i["blocks"] if b in keep)
        i["blockedBy"] = sorted(b for b in i["blockedBy"] if b in keep)
    out = {
        "takenAt": taken, "team": {"id": team["id"], "key": team["key"], "name": team["name"]},
        "rawIssueCount": len(raw), "excluded": {k: sorted(v) for k, v in excluded.items()},
        "chunkLabels": [l for l in labels if (l["parent"] or {}).get("name") == "Chunk" or l["name"] == "Chunk"],
        "labels": [{"id": l["id"], "name": l["name"], "color": l["color"], "parent": (l["parent"] or {}).get("name"), "isGroup": l["isGroup"]} for l in labels],
        "issues": issues,
    }
    json.dump(out, open(OUT, "w"), indent=1)
    edges = sum(len(i["blocks"]) for i in issues.values())
    print("issues kept", len(issues), "edges", edges, "excluded", {k: len(v) for k, v in excluded.items()})


if __name__ == "__main__":
    main()
