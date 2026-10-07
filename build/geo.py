import json, math, collections
import networkx as nx
from shapely.geometry import shape, LineString, Point, MultiLineString, Polygon
from shapely.ops import unary_union, polygonize, linemerge, transform
import pyproj
_P=pyproj.Transformer.from_crs(4326,26910,always_xy=True).transform
def proj(g): return transform(_P,g)
S=json.load(open('streets.json'))
G=collections.defaultdict(nx.Graph)   # per street name
NODEPT={}
for s in S:
    c=s['line']['coordinates']
    if len(c)<2: continue
    a=s['f_node_cnn']; b=s['t_node_cnn']
    NODEPT[a]=tuple(c[0]); NODEPT[b]=tuple(c[-1])
    L=proj(LineString(c)).length
    G[s['streetname']].add_edge(a,b,w=L,coords=c,a=a)
def nodes_near(name, pt):
    g=G[name]; best=None
    for n in g.nodes:
        x,y=NODEPT[n]; d=(x-pt[0])**2+((y-pt[1])*1.26)**2
        if best is None or d<best[0]: best=(d,n)
    return best[1]
def X(a,b,near=None):
    """intersection point of streets a and b (shared node)."""
    common=set(G[a].nodes)&set(G[b].nodes)
    if not common:
        ga=unary_union([LineString(G[a].edges[e]['coords']) for e in G[a].edges])
        gb=unary_union([LineString(G[b].edges[e]['coords']) for e in G[b].edges])
        it=ga.intersection(gb)
        pts=[p for p in getattr(it,'geoms',[it]) if p.geom_type=='Point']
        if not pts: raise ValueError(f'no intersection {a} & {b}')
        if near: pts.sort(key=lambda p:(p.x-near[0])**2+(p.y-near[1])**2)
        return (pts[0].x,pts[0].y)
    cs=list(common)
    if near: cs.sort(key=lambda n:(NODEPT[n][0]-near[0])**2+(NODEPT[n][1]-near[1])**2)
    elif len(cs)>1: print('WARN multiple intersections',a,b,[NODEPT[n] for n in cs])
    return NODEPT[cs[0]]
def along(name, p, q):
    """coords along street `name` from point p to q (shortest path)."""
    g=G[name]; a=nodes_near(name,p); b=nodes_near(name,q)
    path=nx.shortest_path(g,a,b,weight='w')
    out=[NODEPT[path[0]]]
    for u,v in zip(path,path[1:]):
        e=g.edges[u,v]; c=[tuple(x) for x in e['coords']]
        if e['a']!=u: c=c[::-1]
        out+=c[1:]
    return out
_bridged=set()
def bridge(name, maxd=0.006):
    if name in _bridged: return
    _bridged.add(name); g=G[name]
    while True:
        comps=list(nx.connected_components(g))
        if len(comps)<2: return
        best=None
        for i in range(len(comps)):
            for j in range(i+1,len(comps)):
                for a in comps[i]:
                    ax,ay=NODEPT[a]
                    for b in comps[j]:
                        bx,by=NODEPT[b]; d=math.hypot(ax-bx,(ay-by)*1.26)
                        if best is None or d<best[0]: best=(d,a,b)
        if best[0]>maxd: return
        d,a,b=best
        g.add_edge(a,b,w=d*88000,coords=[NODEPT[a],NODEPT[b]],a=a)
_along=along
def along(name,p,q):
    bridge(name); return _along(name,p,q)
from shapely.ops import substring
def along(name,p,q):
    bridge(name); g=G[name]
    def near_edge(pt):
        P=Point(pt); best=None
        for u,v,e in g.edges(data=True):
            d=LineString(e['coords']).distance(P) if len(e['coords'])>1 else 1
            if best is None or d<best[0]: best=(d,u,v)
        return best[1],best[2]
    u1,v1=near_edge(p); u2,v2=near_edge(q)
    best=None
    for a in (u1,v1):
        for b in (u2,v2):
            try:
                c=_along(name,NODEPT[a],NODEPT[b]) if a!=b else [NODEPT[a]]
            except Exception: continue
            # prefer path covering both projections: longest among candidates
            Lc=LineString(c) if len(c)>1 else None
            if Lc is None: continue
            score=Lc.length
            if best is None or score>best[0]: best=(score,c)
    c=best[1]; Lc=LineString(c)
    s1=Lc.project(Point(p)); s2=Lc.project(Point(q))
    sub=substring(Lc,s1,s2)
    out=list(sub.coords)
    if len(out)<2: out=[p,q]
    return out
