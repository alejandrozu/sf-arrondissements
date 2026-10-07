import json, collections, itertools
from shapely.geometry import shape, LineString, Point, MultiLineString
from shapely.ops import unary_union, linemerge, substring
from shapely.strtree import STRtree
from geo import proj
d=json.load(open('mapdata.json')); NUM={a['id']:a['n'] for a in d['arr']}; NAME={a['id']:a['name'] for a in d['arr']}
AR={k:proj(shape(v)).buffer(0) for k,v in json.load(open('arr.json')).items() if k!='ggp'}
S=json.load(open('streets.json'))
EXC={'PAPER','PAPER_FWYS','PAPER_WATER','UPROW','PRIVATE','PRIVATE_PARKING','PSEUDO','FREEWAYS'}
segs=[];fwy=[]
for s in S:
    c=s['line']['coordinates']
    if len(c)<2: continue
    L=proj(LineString(c))
    if s['classcode']=='1' or (s['layer']=='FREEWAYS' and 'RAMP' not in s['streetname']): fwy.append(L); continue
    if s['layer'] in EXC or s['classcode']=='6': continue
    segs.append((s,L))
deg=collections.Counter(); NP={}; inc=collections.defaultdict(list)
for i,(s,L) in enumerate(segs):
    for nd,end in ((s['f_node_cnn'],0),(s['t_node_cnn'],-1)):
        deg[nd]+=1; NP[nd]=Point(L.coords[end]); inc[nd].append(i)
stree=STRtree([L for _,L in segs]); ftree=STRtree(fwy)
def near(tree,geoms,p,r):
    return any(geoms[j].distance(p)<=r for j in tree.query(p.buffer(r)))
SL=[L for _,L in segs]
pairs={}
ids=list(AR)
for a,b in itertools.combinations(ids,2):
    sh=AR[a].boundary.intersection(AR[b].buffer(2))
    if sh.length<20: continue
    lines=[g for g in getattr(sh,'geoms',[sh]) if g.geom_type in('LineString','MultiLineString')]
    u=unary_union(lines)
    try: u=linemerge(u) if u.geom_type=='MultiLineString' else u
    except Exception: pass
    pairs[(a,b)]=u
res=[]; allint=[]
for (a,b),ln in pairs.items():
    parts=getattr(ln,'geoms',[ln]); cls={'street':0,'fwy':0,'natural':0}
    street_pts=[];fwy_pieces=[]
    for P in parts:
        n=max(1,int(P.length/5))
        cur=None;start=0
        for i in range(n+1):
            p=P.interpolate(i/n,normalized=True)
            k='street' if near(stree,SL,p,8) else 'fwy' if near(ftree,fwy,p,16) else 'natural'
            if k!=cur:
                if cur: 
                    seg=substring(P,start,i/n,normalized=True); cls[cur]+=seg.length
                    (street_pts if cur=='street' else fwy_pieces if cur=='fwy' else []).append(seg)
                cur=k;start=i/n
        seg=substring(P,start,1,normalized=True); cls[cur]+=seg.length
        (street_pts if cur=='street' else fwy_pieces if cur=='fwy' else []).append(seg)
    SG=unary_union(street_pts) if street_pts else None; FG=unary_union(fwy_pieces) if fwy_pieces else None
    cand=[]
    if SG is not None and not SG.is_empty:
        for nd,c in deg.items():
            if c>=3 and NP[nd].distance(SG)<=10: cand.append(('x',NP[nd],nd))
    xs=[p for t,p,nd in cand]
    for j in stree.query(ln.buffer(2)):
        it=SL[j].intersection(ln); pts=[g for g in getattr(it,'geoms',[it]) if g.geom_type=='Point']
        for p in pts:
            if near(ftree,fwy,p,20) and not any(p.distance(q)<30 for q in xs): cand.append(('f',p,None))
    # cluster
    cl=[]
    for t,p,nd in cand:
        for c in cl:
            if c['p'].distance(p)<30 and c['t']==t: c['nodes'].append(nd); break
        else: cl.append({'t':t,'p':p,'nodes':[nd]})
    for c in cl:
        sides=set()
        for nd in c['nodes']:
            if nd is None: continue
            for i in inc[nd]:
                L=SL[i]; q=L.interpolate(min(20,L.length*0.6)) if Point(L.coords[0]).distance(NP[nd])<1 else L.interpolate(max(0,L.length-min(20,L.length*0.6)))
                if q.distance(ln)<6: continue
                for z in (a,b):
                    if AR[z].contains(q): sides.add(z)
        c['T']=c['t']=='x' and len(sides)<2
        c['sides']=sides
    nx_=sum(1 for c in cl if c['t']=='x'); nf=sum(1 for c in cl if c['t']=='f'); nt=sum(1 for c in cl if c['T'])
    res.append(dict(a=a,b=b,km_street=cls['street']/1000,km_fwy=cls['fwy']/1000,km_nat=cls['natural']/1000,inter=nx_,fx=nf,T=nt))
    for c in cl: allint.append((a,b,c))
res.sort(key=lambda r:(min(NUM[r['a']],NUM[r['b']]),max(NUM[r['a']],NUM[r['b']])))
for r in res:
    A,B=sorted([r['a'],r['b']],key=NUM.get)
    print(f"{NUM[A]:>2}-{NUM[B]:<2} street {r['km_street']:.2f}km fwy {r['km_fwy']:.2f} nat {r['km_nat']:.2f} | inters {r['inter']} (T {r['T']}) fwy-crossings {r['fx']}")
json.dump([dict(a=a,b=b,t=c['t'],T=c['T'],x=c['p'].x,y=c['p'].y) for a,b,c in allint],open('sticker_points.json','w'))
