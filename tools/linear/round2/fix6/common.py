import json, os, sys, time
sys.path.insert(0, os.environ.get("PAPEROS_PLAN_DIR", ".") + "")
from lin import gql as _gql
R2 = os.environ.get("PAPEROS_PLAN_DIR", ".") + "/round2"
HERE = os.path.join(R2, "fix6")
CH = os.path.join(R2, "changes-fix-FIX-6 pending-docs-dedupe.json")
def gql(q, v=None):
    time.sleep(0.3)
    return _gql(q, v)
def load_changes():
    if os.path.exists(CH): return json.load(open(CH))
    return {"fix": "FIX-6 pending-docs-dedupe", "startedAt": "2026-09-17T06:30Z", "documentsUpdated": [], "issuesUpdated": [], "projectsUpdated": [], "filesEdited": [], "merges": [], "notes": []}
def save_changes(ch):
    tmp = CH + ".tmp"; json.dump(ch, open(tmp, "w"), indent=1); os.replace(tmp, CH)
