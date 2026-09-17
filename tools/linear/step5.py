import sys, glob; sys.path.insert(0,'.')
from lin import *
TEAM="0ee78894-89f8-4376-a829-f8685dbc1868"
ids=load_ids(); plan=json.load(open('plan.json'))
specs={}
for f in sorted(glob.glob('specs/bucket-*.json')):
    for i in json.load(open(f))['issues']: specs[i['key']]=i['description']
for i in json.load(open('specs/gaps.json'))['issues']: specs[i['key']]=i['description']
print('specs loaded',len(specs))
L=lambda n: ids['labels'][n]['id']
S_READY=ids['states']['Ready for Claude']['id']; S_BACK=ids['states']['Backlog']['id']
M='mutation($i:IssueCreateInput!){issueCreate(input:$i){success issue{id identifier url title}}}'
c=0
for pr in plan['projects']:
    pid=ids['projects'][pr['key']]['id']
    for iss in pr['issues']:
        k=iss['key']
        if k in ids['issues'] and ids['issues'][k].get('id'): continue
        desc=specs.get(k)
        if not desc:
            desc=iss['oneLine']; ids['notes'].append("issue %s: spec missing, used oneLine"%k)
        labs=[L('Phase/'+iss['phase']), L('Type/'+iss['type'])]+[L('Surface/'+s) for s in iss.get('surface',[])]
        inp={"teamId":TEAM,"title":iss['title'],"description":desc,"priority":iss['priority'],
             "labelIds":labs,"projectId":pid,"stateId":(S_READY if iss.get('readyNow') else S_BACK)}
        mk=pr['key']+'/'+iss['milestone']
        if mk in ids['milestones']: inp["projectMilestoneId"]=ids['milestones'][mk]['id']
        else: ids['notes'].append("issue %s: milestone %r not found"%(k,iss['milestone']))
        r=gql(M,{"i":inp})['issueCreate']
        assert r['success'], r
        o=r['issue']
        ids['issues'][k]={"id":o['id'],"identifier":o['identifier'],"url":o['url'],"title":o['title'],
                          "readyNow":bool(iss.get('readyNow'))}
        c+=1
        if c%10==0: save_ids(ids); print('..',c,o['identifier'],flush=True)
        time.sleep(0.25)
    save_ids(ids); print('project done',pr['key'],c,flush=True)
ids['counts']['issuesCreated']=ids['counts'].get('issuesCreated',0)+c
save_ids(ids); print('DONE issues',c)
