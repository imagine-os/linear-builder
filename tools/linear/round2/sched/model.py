import os
import json,re,collections
R2=os.environ.get("PAPEROS_PLAN_DIR", ".") + '/round2'
snap=json.load(open(R2+'/linear-snapshot.json'))
new=json.load(open(R2+'/_new_full.json'))
live=json.load(open(R2+'/_live_rel.json'))
PKEY={"Universal App Shell & Repo Template":"app-shell","Data Layer & Database":"data-layer","Version Control & Forge Independence":"forge","Identity, Roles & Audiences":"identity","Design System":"design-system","Quality Pipeline":"quality","Project Management & Claude Pipeline":"pm-linear","Agent Characters & Orgs":"agents","Spec Builder":"spec-builder","In-App Collaboration & Knowledge":"collab","Multiplayer & Realtime":"realtime","Multi-Input Control & Accessibility":"input","Table & Views Engine":"tables","Business Core: Payments, Finance & Payroll":"business-core","Growth: Marketing, Outreach & CRM":"growth","Migration & Import Tools":"migration","Library Discovery & Integration":"libraries"}
issues={}
for i in snap['issues']+new:
    n=int(i['identifier'].split('-')[1])
    if n<13: continue
    issues[i['identifier']]=i
livemap={n['identifier']:n for n in live}
def size_of(desc):
    m=re.search(r'\*\*Size\*\*\s*\n+\s*\**([SML])\b',desc or '')
    if m: return m.group(1)
    m=re.search(r'\*\*Size\*\*[^\n]*?\b([SML])\b',desc or '')
    return m.group(1) if m else 'M'
for k,i in issues.items():
    lv=livemap.get(k)
    if lv:
        i['state']=lv['state']['name']; i['labels']=[l['name'] for l in lv['labels']['nodes']]
        i['milestone']=lv['projectMilestone']['name'] if lv['projectMilestone'] else None
        i['milestoneId']=lv['projectMilestone']['id'] if lv['projectMilestone'] else None
        i['blocks']=sorted({r['relatedIssue']['identifier'] for r in lv['relations']['nodes'] if r['type']=='blocks'})
    else:
        i['blocks']=sorted({r['related'] for r in i['relations'] if r['type']=='blocks'})
    i['pkey']=PKEY.get(i['projectName'])
    i['phase']=next((l for l in i['labels'] if l in('P0','P1','P2')),None)
    i['type']=next((l for l in i['labels'] if l in('Research','Spec','Build','Review','Infra','Docs')),None)
    i['size']=size_of(i['description'])
for k,i in issues.items(): i['children']=sorted(c for c,ci in issues.items() if ci.get('parent')==k)
# blockedBy
for i in issues.values(): i['blockedBy']=[]
for k,i in issues.items():
    for b in i['blocks']:
        if b in issues: issues[b]['blockedBy'].append(k)
# umbrella handling: parents with children are not scheduled; children inherit parent blockers; dependents of parent depend on all children
parents={k for k,i in issues.items() if i['children']}
def eff_blockers(k):
    i=issues[k]; out=set()
    src=set(i['blockedBy'])
    if i.get('parent') in issues: src|=set(issues[i['parent']]['blockedBy'])
    for b in src:
        if b==k or b==i.get('parent'): continue
        if b in parents: out|=set(issues[b]['children'])
        else: out.add(b)
    # sibling ordering: children split sequentially in spec numbering? keep explicit relations only
    return sorted(out-{k})
for k in issues: issues[k]['eff']=eff_blockers(k)
sched_units={k for k in issues if k not in parents}
if __name__=='__main__':
    c=collections.Counter((i['phase'],i['type'],i['size']) for k,i in issues.items() if k in sched_units)
    tot=collections.Counter()
    for (p,t,s),n in sorted(c.items(),key=lambda x:str(x)): tot[(p,t)]+=n
    for (p,t),n in sorted(tot.items(),key=str): print(p,t,n)
    print('units',len(sched_units),'parents',len(parents), sorted(parents))
    print(collections.Counter(i['size'] for k,i in issues.items() if k in sched_units))
    print(collections.Counter(i['state'] for k,i in issues.items() if k in sched_units))
    # cycle check
    import sys
    sys.setrecursionlimit(10000)
    seen={};
    def dfs(k,stack):
        if k in stack: print('CYCLE',stack[stack.index(k):]+[k]); return
        if k in seen: return
        stack.append(k)
        for b in issues[k]['eff']: dfs(b,stack)
        stack.pop(); seen[k]=1
    for k in sched_units: dfs(k,[])
    print('ready now (no eff blockers):',sorted(k for k in sched_units if not issues[k]['eff']))
