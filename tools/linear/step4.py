import sys; sys.path.insert(0,'.')
from lin import *
TEAM="0ee78894-89f8-4376-a829-f8685dbc1868"
TODAY="2026-09-17"
ids=load_ids(); plan=json.load(open('plan.json'))
M_PROJ='mutation($i:ProjectCreateInput!){projectCreate(input:$i){success project{id name url slugId}}}'
M_MS='mutation($i:ProjectMilestoneCreateInput!){projectMilestoneCreate(input:$i){success projectMilestone{id name}}}'
cp=0; cm=0
for pr in plan['projects']:
    key=pr['key']
    if key in ids['projects'] and ids['projects'][key].get('id'):
        pid=ids['projects'][key]['id']; print('skip proj',key)
    else:
        desc=pr['description']
        inp={"name":pr['name'],"description":pr['summary'][:255],"content":desc,"color":pr['color'],
             "teamIds":[TEAM],"state":("started" if pr['phase']=="P0" else "planned"),
             "startDate":TODAY,"targetDate":pr['milestones'][-1]['targetDate'],"icon":pr.get('icon')}
        try:
            r=gql(M_PROJ,{"i":inp})['projectCreate']
        except RuntimeError as e:
            if 'icon' in str(e).lower():
                ids['notes'].append("project %s: icon %r rejected, created without icon"%(key,pr.get('icon')))
                inp.pop('icon'); r=gql(M_PROJ,{"i":inp})['projectCreate']
            else: raise
        assert r['success'], r
        p=r['project']; pid=p['id']
        ids['projects'][key]={"id":pid,"name":p['name'],"url":p['url'],"phase":pr['phase'],"issueCount":len(pr['issues'])}
        cp+=1; save_ids(ids); print('proj+',key,pid); time.sleep(0.25)
    for ms in pr['milestones']:
        mk=key+'/'+ms['name']
        if mk in ids['milestones'] and ids['milestones'][mk].get('id'): continue
        r=gql(M_MS,{"i":{"projectId":pid,"name":ms['name'],"targetDate":ms['targetDate'],"description":ms['goal']}})['projectMilestoneCreate']
        assert r['success'], r
        ids['milestones'][mk]={"id":r['projectMilestone']['id']}
        cm+=1; save_ids(ids); time.sleep(0.25)
    print('  milestones ok', key)
ids['counts']['projectsCreated']=ids['counts'].get('projectsCreated',0)+cp
ids['counts']['milestonesCreated']=ids['counts'].get('milestonesCreated',0)+cm
save_ids(ids); print('DONE projects',cp,'milestones',cm)
