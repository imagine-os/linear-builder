import sys; sys.path.insert(0,'.')
from lin import *
TEAM="0ee78894-89f8-4376-a829-f8685dbc1868"
ids=load_ids()
team=json.load(open('_team.json'))
ids["team"]={"key":"PAP","id":TEAM,"name":"PaperOS"}
# existing
existing_states={s['name']:s['id'] for s in team['states']['nodes']}
for n,i in existing_states.items(): ids['states'].setdefault(n,{"id":i,"created":False})
existing_labels={l['name']:l for l in team['labels']['nodes']}
for n,l in existing_labels.items(): ids['labels'].setdefault(n,{"id":l['id'],"created":False})
save_ids(ids)

plan=json.load(open('plan.json'))
STATE_COLOR={"Ready for Claude":"#F2C94C","In Review":"#5E6AD2","Needs Justin":"#EB5757"}
STATE_POS={"Ready for Claude":1.5,"In Review":2.5,"Needs Justin":2.75}
M_STATE='mutation($i:WorkflowStateCreateInput!){workflowStateCreate(input:$i){success workflowState{id name type position}}}'
created_states=0
for s in plan['states']:
    if s['name'] in ids['states'] and ids['states'][s['name']].get('id'):
        print('skip state', s['name']); continue
    r=gql(M_STATE, {"i":{"teamId":TEAM,"name":s['name'],"type":s['type'],"color":STATE_COLOR[s['name']],
        "position":STATE_POS[s['name']],"description":s['description']}})['workflowStateCreate']
    assert r['success'], r
    ids['states'][s['name']]={"id":r['workflowState']['id'],"created":True}
    created_states+=1; save_ids(ids); print('state+', s['name'], r['workflowState']['id']); time.sleep(0.25)

M_LABEL='mutation($i:IssueLabelCreateInput!){issueLabelCreate(input:$i){success issueLabel{id name}}}'
created_labels=0; created_groups=0
for g in plan['labels']['groups']:
    gname=g['name']
    if gname in ids['labelGroups'] and ids['labelGroups'][gname].get('id'):
        gid=ids['labelGroups'][gname]['id']; print('skip group', gname)
    elif gname in existing_labels:
        gid=existing_labels[gname]['id']; ids['labelGroups'][gname]={"id":gid,"created":False}; save_ids(ids)
    else:
        r=gql(M_LABEL, {"i":{"teamId":TEAM,"name":gname,"color":"#6B7280","isGroup":True}})['issueLabelCreate']
        assert r['success'], r
        gid=r['issueLabel']['id']; created_groups+=1
        ids['labelGroups'][gname]={"id":gid,"created":True}; save_ids(ids); print('group+', gname, gid); time.sleep(0.25)
    for l in g['labels']:
        full=gname+'/'+l['name']
        if full in ids['labels'] and ids['labels'][full].get('id'):
            print('skip label', full); continue
        r=gql(M_LABEL, {"i":{"teamId":TEAM,"name":l['name'],"color":l['color'],"parentId":gid}})['issueLabelCreate']
        assert r['success'], r
        ids['labels'][full]={"id":r['issueLabel']['id'],"created":True}
        created_labels+=1; save_ids(ids); print('label+', full, r['issueLabel']['id']); time.sleep(0.25)
ids['counts']=ids.get('counts',{})
ids['counts']['statesCreated']=ids['counts'].get('statesCreated',0)+created_states
ids['counts']['labelsCreated']=ids['counts'].get('labelsCreated',0)+created_labels+created_groups
save_ids(ids)
print('DONE states',created_states,'groups',created_groups,'labels',created_labels)
