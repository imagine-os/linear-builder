import sys; sys.path.insert(0,'.')
from lin import *
TEAM="0ee78894-89f8-4376-a829-f8685dbc1868"
ids=load_ids(); plan=json.load(open('plan.json'))
done=set(ids.get('relations',[]))

# ---- step 6: blocking relations
M_REL='mutation($i:IssueRelationCreateInput!){issueRelationCreate(input:$i){success issueRelation{id}}}'
c=0
for pr in plan['projects']:
    for iss in pr['issues']:
        for dep in iss.get('dependsOn',[])[:3]:
            tag=dep+'>>'+iss['key']
            if tag in done: continue
            a=ids['issues'].get(dep); b=ids['issues'].get(iss['key'])
            if not a or not b:
                ids['notes'].append('relation skipped, missing issue: '+tag); continue
            try:
                r=gql(M_REL,{"i":{"issueId":a['id'],"relatedIssueId":b['id'],"type":"blocks"}})['issueRelationCreate']
                assert r['success'], r
            except RuntimeError as e:
                ids['notes'].append('relation failed %s: %s'%(tag,str(e)[:200])); save_ids(ids); continue
            done.add(tag); ids['relations']=sorted(done); c+=1
            if c%20==0: save_ids(ids); print('..rel',c,flush=True)
            time.sleep(0.25)
ids['counts']['relationsCreated']=len(done)
save_ids(ids); print('relations total',len(done),'new',c)

# ---- step 7: PAP-5
appshell=ids['projects']['app-shell']
lines=["This issue is the origin of the whole **PaperOS Core Platform** plan. Justin's question — how fast can we get from a blank screen, down through the layers of abstraction, to electrons flowing through the circuits — became the brief for a 17-project, %d-issue programme that builds the reusable foundation (universal app shell, data layer, self-hosted version control, identity, design system, quality gates, agent roster, spec builder, collaboration, realtime, multi-input, tables/views, business core, growth, migration and a vetted library set) before any individual app is built. Everything below descends from this issue." % len(ids['issues']),
 "", "**Projects**", ""]
order=[p['key'] for p in plan['projects']]
for k in order:
    pj=ids['projects'][k]; ph=pj.get('phase','')
    lines.append("- [%s](%s) — %s" % (pj['name'], pj['url'], ph))
body="\n".join(lines)
M_UP='mutation($id:String!,$i:IssueUpdateInput!){issueUpdate(id:$id,input:$i){success issue{identifier url title state{name} project{name}}}}'
r=gql(M_UP,{"id":"PAP-5","i":{"projectId":appshell['id'],"stateId":ids['states']['Backlog']['id'],
     "priority":2,"description":body}})['issueUpdate']
print('PAP-5', r['success'], json.dumps(r['issue']))
ids['pap5']=r['issue']; save_ids(ids)

# ---- step 8: template
TPL = """## Goal

## Scope
In:
- 
Out:
- 

## Design / Approach

## Page spec (logic, access, data, integrations, layout, components)

## Interfaces & contracts

## Acceptance criteria
- [ ] 

## Verification
- Automated checks:
- Visual / responsive evidence:

## Edge cases & failure modes

## Dependencies & risks

## Artifacts to produce
"""
M_T='mutation($i:TemplateCreateInput!){templateCreate(input:$i){success template{id name}}}'
try:
    r=gql(M_T,{"i":{"name":"PaperOS Spec","type":"issue","teamId":TEAM,
        "description":"Standard PaperOS issue spec sections.",
        "templateData":json.dumps({"description":TPL,"title":""})}})['templateCreate']
    print('template', r)
    ids['template']={"id":r['template']['id'],"name":r['template']['name']} if r['success'] else None
except RuntimeError as e:
    print('template FAILED', str(e)[:400])
    ids['template']=None; ids['notes'].append('templateCreate failed: '+str(e)[:300])
save_ids(ids); print('ALLDONE')
