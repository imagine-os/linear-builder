#!/usr/bin/env python3
"""Regenerate specs/<project-key>/pap-N-slug.md and specs/README.md from plan/linear-snapshot-live.json.

One file per canonical issue (PAP-13 upward, state not Duplicate, non-archived) with frontmatter (identifier, project,
phase, type, priority, surfaces, milestone, state, relations, key, URL, source, updatedAt, model, effort, and since
round 4 estimate, dueDate, cycle) and the live Linear description as body. Reproduces the round-3 file format
byte for byte apart from the added keys and the snapshot date in `source:`.

  python3 tools/linear/gen_specs.py                       # regenerate specs/ in the repo (deletes stale spec files)
  OUT=/tmp/specs SNAPSHOT=/path/snap.json python3 tools/linear/gen_specs.py
  python3 tools/linear/gen_specs.py --no-new-keys         # legacy format without estimate/dueDate/cycle (format check)

Project keys: snapshot projects[].key, then plan/round4/gaps/cross-cutting.json newProjects[].key by project name.
Section order in the README: plan/plan.json projects, then module-system, then the round-4 projects in
cross-cutting order, then anything else alphabetically.
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get("PAPEROS_REPO") or os.path.abspath(os.path.join(HERE, "..", ".."))
SNAPSHOT = os.environ.get("SNAPSHOT") or os.path.join(ROOT, "plan", "linear-snapshot-live.json")
OUT = os.environ.get("OUT") or os.path.join(ROOT, "specs")
NEW_KEYS = "--no-new-keys" not in sys.argv
ROUND_NOTE = os.environ.get("ROUND_NOTE") or (
    "after round 4 (2026-09-18) created the gap and sub-feature issues from the per-project feature matrices, the five new "
    "projects (Tenant AI Assistant, Workflows & Documents, Scheduling & Engagement, Commerce & Operations, Platform Operations) "
    "and turned on estimates, due dates, cycles and triage; see `plan/round4/` and `docs/linear-features.md`")

MODEL_ID = {"Model: Fable 5.1": "claude-fable-5-1", "Model: Opus 5": "claude-opus-5", "Model: Sonnet 5": "claude-sonnet-5", "Model: Haiku 4.5": "claude-haiku-4-5"}


def j(v):
    return json.dumps(v, ensure_ascii=False)


def jlist(v):
    return "[" + ", ".join(j(x) for x in v) + "]"


def slug(title):
    s = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    if len(s) > 40:
        s = s[:40]
        if not s.endswith("-"):
            s = s.rsplit("-", 1)[0]
        s = s.rstrip("-")
    return s


def num(ident):
    return int(ident.split("-")[1])


def load(rel, default=None):
    p = os.path.join(ROOT, rel)
    return json.load(open(p)) if os.path.exists(p) else default


def main():
    snap = json.load(open(SNAPSHOT))
    plan = load("plan/plan.json", {"projects": []})
    cross = load("plan/round4/gaps/cross-cutting.json", {}) or {}
    module_key_by_title = {x["title"]: x["key"] for x in (load("plan/module-issues.json", {}) or {}).get("issues", []) if x.get("title") and x.get("key")}
    taken_min = snap["takenAt"][:16] + "Z"
    source = f"Linear snapshot {taken_min} (plan/linear-snapshot-live.json)"

    key_by_name = {p["name"]: p.get("key") for p in snap["projects"]}
    for p in cross.get("newProjects", []) or []:
        key_by_name.setdefault(p["name"], p["key"])
        if not key_by_name.get(p["name"]):
            key_by_name[p["name"]] = p["key"]
    order = [p["key"] for p in plan["projects"]] + ["module-system"] + [p["key"] for p in cross.get("newProjects", []) or []]
    proj_keys = {}
    for p in snap["projects"]:
        k = key_by_name.get(p["name"])
        if k:
            proj_keys[k] = p["name"]
    for k in sorted(proj_keys):
        if k not in order:
            order.append(k)

    issues = [i for i in snap["issues"] if num(i["identifier"]) >= 13 and i["state"] != "Duplicate" and not i.get("archivedAt")]
    ident_set = {i["identifier"] for i in snap["issues"]}
    valid = lambda ids: [x for x in ids if x in ident_set]

    written = set()
    files = []
    for i in issues:
        pkey = i.get("projectKey") or key_by_name.get(i.get("projectName") or "") or "no-project"
        pname = i.get("projectName") or ""
        model = (i.get("model") or [None])[0]
        effort = (i.get("effort") or [None])[0]
        cyc = i.get("cycle")
        fm = [
            ("identifier", j(i["identifier"])), ("title", j(i["title"])), ("project", j(pkey)), ("projectName", j(pname)),
            ("phase", j(i.get("phase") or "")), ("type", j(i.get("type") or "")), ("priority", j(i.get("priority"))),
            ("surfaces", jlist(i.get("surfaces") or [])), ("milestone", j(i.get("milestone"))), ("state", j(i["state"])),
            ("parent", j(i.get("parent"))), ("children", jlist(i.get("children") or [])),
            ("blockedBy", jlist(valid(i.get("blockedBy") or []))), ("blocks", jlist(valid(i.get("blocks") or []))),
            ("key", j(i.get("key") or module_key_by_title.get(i["title"]))), ("url", j(i["url"])), ("source", j(source)), ("updatedAt", j(i["updatedAt"])),
            ("model", j(MODEL_ID.get(model) if model else None)), ("effort", j(effort.replace("Effort: ", "") if effort else None)),
        ]
        if NEW_KEYS:
            fm += [("estimate", j(i.get("estimate"))), ("dueDate", j(i.get("dueDate"))),
                   ("cycle", j({"number": cyc["number"], "name": cyc["name"], "startsAt": cyc["startsAt"][:10], "endsAt": cyc["endsAt"][:10]} if cyc else None))]
        text = "---\n" + "".join(f"{k}: {v}\n" for k, v in fm) + "---\n\n" + f"# {i['identifier']}: {i['title']}\n\n" + (i.get("description") or "").rstrip("\n") + "\n"
        fname = f"pap-{num(i['identifier'])}-{slug(i['title'])}.md"
        d = os.path.join(OUT, pkey)
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, fname), "w") as f:
            f.write(text)
        written.add(os.path.join(pkey, fname))
        files.append((pkey, i, fname))

    # remove stale spec files (issues renamed or re-projected) so the folder mirrors the snapshot
    for root, _, fs in os.walk(OUT):
        for fn in fs:
            rel = os.path.relpath(os.path.join(root, fn), OUT)
            if fn.startswith("pap-") and fn.endswith(".md") and rel not in written:
                os.remove(os.path.join(root, fn))

    # README index
    ready = sorted([i["identifier"] for i in issues if i["state"] == "Ready for Claude"], key=num)
    states = {}
    for i in issues:
        states[i["state"]] = states.get(i["state"], 0) + 1
    umb = sum(1 for i in issues if i.get("children"))
    deferred = sum(1 for i in issues if i.get("deferred"))
    other_states = "".join(f" {s}: {n}." for s, n in sorted(states.items(), key=lambda kv: -kv[1]) if s not in ("Ready for Claude", "Backlog"))
    fm_note = ("Frontmatter carries the Linear identifier, project, phase, type, priority, surfaces, milestone, state, relations, key, URL, `updatedAt`, "
               + ("" if NEW_KEYS else "and ") + "the `model` and `effort` for the builder session (read from the issue's `Model` and `Effort` labels, the same values as `plan/model-effort.json`; "
               "umbrellas carry `model: null`, see `docs/cost-and-duration-estimate.md` section 4b)"
               + (", and since round 4 the Linear `estimate` (Fibonacci points), `dueDate` and `cycle`" if NEW_KEYS else "") + "; the body is the live Linear description.")
    esc = lambda s: s.replace("|", "\\|")
    out = ["# Issue specs", "",
           "One file per canonical issue of Linear team PAP: every non-archived issue from PAP-13 upward whose state is not Duplicate (PAP-1..PAP-12 are Justin's brief, archived strays and duplicates and are skipped). " + fm_note, "",
           f"Linear is the system of record. Every file here is regenerated from `plan/linear-snapshot-live.json`, taken {snap['takenAt']} {ROUND_NOTE}. File name: `<identifier>-<short title slug>.md` under the project key.", "",
           f"Files: {len(files)}. Ready for Claude at snapshot time: {len(ready)} ({', '.join(ready)}). Backlog: {states.get('Backlog', 0)}.{other_states} Umbrellas (issues with sub-issues): {umb}. Deferred label: {deferred}.", ""]
    for pk in order:
        rows = sorted([(i, fn) for (k, i, fn) in files if k == pk], key=lambda t: num(t[0]["identifier"]))
        if not rows:
            continue
        pname = proj_keys.get(pk) or rows[0][0].get("projectName") or pk
        out += ["", f"## {pname} (`{pk}`, {len(rows)})", "", "| Issue | Title | State | Phase | Type | Link |", "|---|---|---|---|---|---|"]
        for i, fn in rows:
            out.append(f"| [{i['identifier']}]({pk}/{fn}) | {esc(i['title'])} | {i['state']} | {i.get('phase') or ''} | {i.get('type') or ''} | [Linear]({i['url']}) |")
    with open(os.path.join(OUT, "README.md"), "w") as f:
        f.write("\n".join(out) + "\n")
    print(f"wrote {len(files)} specs in {len([k for k in order if any(f[0] == k for f in files)])} project folders to {OUT}; ready {len(ready)}, umbrellas {umb}, deferred {deferred}")


if __name__ == "__main__":
    main()
