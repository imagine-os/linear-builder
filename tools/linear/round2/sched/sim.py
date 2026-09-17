import sys,json,collections,datetime
sys.path.insert(0,os.environ.get("PAPEROS_PLAN_DIR", ".") + '/round2/sched')
from model import *
D0=datetime.date(2026,9,17); NDAYS=15
SLOTS={'S':1,'M':2,'L':4}
PRICE={'S':10,'M':22,'L':50}   # builder allowance per session size (credits, USD)
BUCKET={'Build':'build','Infra':'build','Spec':'plan','Research':'research','Docs':'docs','Review':'qa'}
# deferred / stretch pool (not scheduled before 10-01)
DEFER=set(sys.argv[1].split(',')) if len(sys.argv)>1 and sys.argv[1] else set()
CAP=[int(x) for x in sys.argv[2].split(',')] if len(sys.argv)>2 else [8]*NDAYS
units=[k for k in sched_units if k not in DEFER]
U=set(units)
# critical path length (slots) to sinks
memo={}
def cp(k):
    if k in memo: return memo[k]
    downs=[d for d in units if k in issues[d]['eff']]
    memo[k]=SLOTS[issues[k]['size']]+1+(max((cp(d) for d in downs),default=0))
    return memo[k]
for k in units: cp(k)
import os
REVIEW_LAG=int(os.environ.get("LAG","1"))
start={};finish={};ready_at={}
def blockers_done(k,slot):
    for b in issues[k]['eff']:
        if b in DEFER: continue   # deferred blockers: treat as soft (flag)
        if b not in finish or finish[b]+REVIEW_LAG>slot: return False
    return True
running=[]  # (end_slot,k)
ORD=os.environ.get('ORD','cp')
_live=json.load(open(os.environ.get("PAPEROS_PLAN_DIR", ".") + '/round2/_live_milestones.json'))
_md={(PKEY[p['project']],m['name']):m['targetDate'] for p in _live for m in p['milestones']}
def due_slot(k):
    d=_md.get((issues[k]['pkey'],issues[k]['milestone']),'2026-10-01')
    return (datetime.date.fromisoformat(d)-D0).days*2+2
def slack(k): return due_slot(k)-cp(k)
order=(lambda k:(-cp(k),issues[k]['phase'],issues[k]['priority'] or 3,-SLOTS[issues[k]['size']])) if ORD=='cp' else (lambda k:(slack(k),issues[k]['priority'] or 3,-SLOTS[issues[k]['size']])) if ORD=='slack' else (lambda k:(issues[k]['phase'],-cp(k),issues[k]['priority'] or 3,-SLOTS[issues[k]['size']]))
for slot in range(NDAYS*2):
    day=slot//2
    running=[(e,k) for e,k in running if e>slot]
    cap=CAP[day]
    cands=[k for k in units if k not in start and blockers_done(k,slot)]
    cands.sort(key=order)
    for k in cands:
        if len(running)>=cap: break
        start[k]=slot; finish[k]=slot+SLOTS[issues[k]['size']]; running.append((finish[k],k))
unsched=[k for k in units if k not in start]
def dstr(slot): return (D0+datetime.timedelta(days=slot//2)).isoformat()+('am' if slot%2==0 else 'pm')
out={'start':start,'finish':finish,'unscheduled':unsched,'defer':sorted(DEFER),'cap':CAP}
json.dump(out,open(os.environ.get("PAPEROS_PLAN_DIR", ".") + '/round2/sched/sim_out.json','w'),indent=0)
if __name__=='__main__':
    print('unscheduled',len(unsched),unsched[:40])
    late=[(k,dstr(finish[k])) for k in start if finish[k]>NDAYS*2]
    print('finish after 10-01:',late)
    # per-day table
    cum=collections.Counter()
    for day in range(NDAYS):
        s0,s1=day*2,day*2+1
        started=[k for k in start if start[k] in (s0,s1)]
        inflight=[k for k in start if start[k]<=s1 and finish[k]>s0]
        done=[k for k in finish if finish[k] in (s0+1,s1+1)]
        cost=collections.Counter()
        for k in started: cost[BUCKET[issues[k]['type']]]+=PRICE[issues[k]['size']]
        peak=max(len([k for k in start if start[k]<=s and finish[k]>s]) for s in (s0,s1))
        ph=collections.Counter(issues[k]['phase'] for k in started)
        print((D0+datetime.timedelta(days=day)).isoformat(),'start',len(started),dict(ph),'peak',peak,'done',len(done),dict(cost))
    # milestone finish
    ms=collections.defaultdict(list)
    for k in start: ms[(issues[k]['pkey'],issues[k]['milestone'])].append(finish[k])
    live=json.load(open(os.environ.get("PAPEROS_PLAN_DIR", ".") + '/round2/_live_milestones.json'))
    md={(PKEY[p['project']],m['name']):(m['targetDate'],m['id']) for p in live for m in p['milestones']}
    for key,fs in sorted(ms.items()):
        f=max(fs); d=(D0+datetime.timedelta(days=(f-1)//2)).isoformat()
        cur=md.get(key,('?',''))[0]
        flag='' if d<=cur else 'LATE'
        print(key,cur,'->',d,flag)
    tot=collections.Counter()
    for k in start: tot[BUCKET[issues[k]['type']]]+=PRICE[issues[k]['size']]
    print(dict(tot))
