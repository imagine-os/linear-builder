import json,re,collections
snap=json.load(open('linear-snapshot-2.json')); by={i['identifier']:i for i in snap['issues']}
live=json.load(open('_fix3_live.json'))
ms={m['id']:m for p in snap['projects'] for m in p['milestones']}
def mdate(k):
    mid=by[k].get('milestoneId'); return ms[mid]['targetDate'] if mid and mid in ms else None
P=lambda n:f"PAP-{n}"
# ---- Rule 1: parent blocker B -> child (text-named, finer child edge where text names a sibling-family child, else first child)
rule1=[  # (blocker, child, why)
 (P(13),P(255),"PAP-255 Dependencies names PAP-13 (hard)"),
 (P(255),P(258),"PAP-258 names 'PAP-19 child 1' -> finer edge to PAP-255 instead of umbrella PAP-19"),
 (P(14),P(258),"PAP-14 blocks PAP-20; no child names it -> first child"),
 (P(17),P(259),"PAP-259 names PAP-17 (hard)"),
 (P(17),P(260),"PAP-260 names PAP-17"),
 (P(14),P(261),"PAP-261 names PAP-14 (hard)"),
 (P(16),P(261),"PAP-261 names PAP-16 (hard)"),
 (P(19),P(262),"PAP-262 names PAP-19 (hard)"),
 (P(16),P(262),"PAP-262 names PAP-16"),
 (P(117),P(264),"PAP-264 names PAP-117"),
 (P(22),P(266),"PAP-266 names PAP-22"),
 (P(33),P(267),"PAP-267 names PAP-33 (hard)"),
 (P(33),P(268),"PAP-268 names PAP-33"),
 (P(267),P(270),"PAP-270 names 'PAP-35 child 1' -> finer edge to PAP-267"),
 (P(30),P(270),"PAP-270 names PAP-30 (hard)"),
 (P(34),P(270),"PAP-270 names PAP-34 (hard)"),
 (P(31),P(271),"PAP-271 names PAP-31"),
 (P(268),P(272),"PAP-272 names 'PAP-35 child 2' -> finer edge to PAP-268"),
 (P(25),P(273),"PAP-273 names PAP-25 (hard)"),
 (P(25),P(274),"PAP-274 names PAP-25"),
 (P(45),P(276),"PAP-276 names PAP-45 (hard)"),
 (P(16),P(277),"PAP-277 names PAP-16 (hard)"),
 (P(56),P(223),"PAP-223 names PAP-56 (hard)"),
 (P(33),P(223),"PAP-223 names PAP-33 (hard)"),
 (P(55),P(227),"PAP-227 names PAP-55 (hard)"),
 (P(279),P(227),"PAP-279 blocks PAP-59; no child names it -> first child (Condition imports FilterTree)"),
 (P(34),P(228),"PAP-228 names PAP-34 (hard for the harness)"),
 (P(58),P(230),"PAP-230 names PAP-58 (hard)"),
 (P(58),P(231),"PAP-231 names PAP-58 (hard)"),
 (P(66),P(236),"PAP-236 names PAP-66 (hard)"),
 (P(212),P(236),"PAP-212 blocks PAP-67; no child names it -> first child"),
 (P(78),P(243),"PAP-243 names PAP-78 (hard)"),
 (P(79),P(243),"PAP-243 names PAP-79 (hard)"),
 (P(78),P(246),"PAP-246 names PAP-78 (hard)"),
 (P(14),P(246),"PAP-246 names PAP-14 (hard)"),
 (P(114),P(249),"PAP-249 names PAP-114 (hard)"),
 (P(243),P(249),"PAP-249 names 'PAP-81 harness child' -> finer edge to PAP-243"),
 (P(239),P(249),"PAP-239 blocks PAP-85; no child names it -> first child"),
 (P(94),P(252),"PAP-252 names PAP-94 (hard)"),
 (P(94),P(254),"PAP-254 names PAP-94 (hard)"),
 (P(26),P(253),"PAP-253 names PAP-26 (hard)"),
 (P(82),P(253),"PAP-253 names PAP-82 (full gate run)"),
 (P(81),P(253),"PAP-81 blocks PAP-88; routed to the nightly full-gate-run child, not the policy document"),
 (P(242),P(253),"PAP-242 blocks PAP-88; routed to the nightly full-gate-run child (k6 smoke runs there)"),
]
# already-existing child inbound edges from earlier rounds that satisfy rule 1: PAP-239->243, PAP-240->247, PAP-239->248, PAP-240->250
# ---- extras: hard dependencies named in child text that are not parent blockers (no cycles, no umbrella)
extras=[
 (P(257),P(225),"PAP-225 names PAP-19 (hard for the desktop shell); PAP-257 is the deep-link child of PAP-19"),
 (P(268),P(276),"PAP-276 names PAP-35 (hard); PAP-268 is the routers/typed-client child of PAP-35"),
 (P(51),P(276),"PAP-276 names PAP-51 (hard)"),
]
# ---- Rule 2: last child -> D for every P blocks D
rule2=[]
def add(last,Ds,why):
    for D in Ds: rule2.append((last,D,why))
add(P(257),[P(24),P(21),P(20)],"last child of PAP-19")
add(P(260),[P(154)],"last child of PAP-20")
add(P(263),[P(145),P(23)],"last child of PAP-21")
add(P(266),[P(29),P(126)],"last child of PAP-28")
add(P(269),[P(193),P(39),P(129),P(242),P(222),P(163),P(119),P(40),P(36)],"last child of PAP-35")
add(P(272),[P(143)],"last child of PAP-36")
add(P(273),[P(50),P(48),P(47)],"PAP-273 text: 'Blocks PAP-47, PAP-48, PAP-50' (compose stack is the real dependency, not the last child)")
add(P(275),[P(54)],"last child of PAP-45")
add(P(224),[P(86),P(240),P(220),P(140),P(58)],"PAP-57 has three leaf children; the auth UI child is the one that completes end-to-end login, which each dependent needs")
add(P(228),[P(39),P(163)],"PAP-59 leaf: SQL predicate compiler feeds search and the view compiler")
add(P(229),[P(163),P(140),P(116),P(222),P(178),P(172),P(131),P(64),P(61),P(60)],"PAP-59 leaf: spec adapter, oRPC middleware and useCan are the integration surface")
add(P(238),[P(164),P(233),P(151),P(74),P(73),P(71),P(70),P(69)],"last child of PAP-67")
add(P(244),[P(241),P(88),P(85)],"PAP-81 leaf (correctness and spec reviewers); gate 2 is complete only with both reviewer children")
add(P(245),[P(241),P(88),P(85)],"PAP-81 leaf (security reviewer)")
add(P(248),[P(88),P(84),P(83)],"last child of PAP-82")
add(P(254),[P(89),P(29)],"last child of PAP-88 (PAP-254 Dependencies text softened: PAP-89 is a consumer)")
edges=[(b,c,"rule1",w) for b,c,w in rule1]+[(b,c,"extra",w) for b,c,w in extras]+[(b,c,"rule2",w) for b,c,w in rule2]
# ---- existing graph (live for the 68 fetched, snapshot elsewhere, minus FIX-2 deletions)
G=collections.defaultdict(set)
for i in snap['issues']:
    for r in i['relations']:
        if r['type']=='blocks': G[i['identifier']].add(r['related'])
G['PAP-13'].discard('PAP-279'); G['PAP-279'].discard('PAP-161')
for k,v in live.items():
    G[v['identifier']]={x['relatedIssue']['identifier'] for x in v['relations']['nodes'] if x['type']=='blocks'}
dups=[(b,c) for b,c,_,_ in edges if c in G[b]]
seen=set(); internal=[e for e in edges if (e[0],e[1]) in seen or seen.add((e[0],e[1]))]
print("duplicates with live/snapshot:",dups); print("duplicate within plan:",internal)
for b,c,_,_ in edges: G[b].add(c)
# cycle check
def cyc():
    color={}
    def dfs(u,stack):
        color[u]=1; stack.append(u)
        for v in G[u]:
            if color.get(v)==1: return stack[stack.index(v):]+[v]
            if v not in color:
                r=dfs(v,stack)
                if r: return r
        color[u]=2; stack.pop()
    for u in list(G):
        if u not in color:
            r=dfs(u,[])
            if r: return r
print("cycle:",cyc())
inv=[(b,mdate(b),c,mdate(c)) for b,c,_,_ in edges if mdate(b) and mdate(c) and mdate(b)>mdate(c)]
print("milestone inversions:",len(inv)); [print("  ",x) for x in inv]
# zero-blocker children after
kids=[i['identifier'] for i in snap['issues'] if i.get('parent') in {P(n) for n in [19,20,21,28,35,36,45,54,57,59,65,67,81,82,85,88]}]
inb=collections.defaultdict(set)
for u,vs in G.items():
    for v in vs: inb[v].add(u)
fam=set(kids)
print("children:",len(kids),"with no external blocker after:",[k for k in kids if not (inb[k]-fam)])
print("children with zero blockers after:",[k for k in kids if not inb[k]])
print("edges:",len(edges),"rule1",len(rule1),"extra",len(extras),"rule2",len(rule2))
json.dump([{"blocker":b,"blocked":c,"rule":r,"why":w,"blockerId":by[b]['id'],"blockedId":by[c]['id']} for b,c,r,w in edges],open('_fix3_edges.json','w'),indent=1)
