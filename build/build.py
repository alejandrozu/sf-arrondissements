import json, math, sys
from geo import *
from shapely.geometry import shape, LineString, Polygon, MultiPolygon, Point, mapping
from shapely.ops import unary_union, polygonize
FN=json.load(open('find_nbhd.geojson'))
NB={f['properties']['name']:shape(f['geometry']).buffer(0) for f in FN['features']}
LAND=unary_union(list(NB.values())).buffer(0.00003).buffer(-0.00003)
def S(name,p,q): return ('S',name,p,q)
def L(*pts): return ('L',list(pts))
def ring_coords(legs):
    out=[]
    for lg in legs:
        if lg[0]=='S': c=along(lg[1],lg[2],lg[3])
        else: c=lg[1]
        out+= [tuple(x) for x in c]
    return out
exec(open('spec.py').read())   # defines LINES (list of legs lists), SEEDS {id:(lon,lat)}, extra polys
lines=[]; BLINES=[]
for legs in LINES:
    c=ring_coords(legs)
    def ext(a,b,m=0.0015):
        dx,dy=b[0]-a[0],b[1]-a[1]; n=math.hypot(dx,dy) or 1
        return (b[0]+dx/n*m,b[1]+dy/n*m)
    c=[ext(c[1],c[0])]+c+[ext(c[-2],c[-1])]
    lines.append(LineString(c)); BLINES.append(c)
for name in EXTRA_RINGS:
    g=NB[name]; 
    for p in getattr(g,'geoms',[g]): lines.append(LineString(p.exterior.coords))
for p in getattr(LAND,'geoms',[LAND]): lines.append(LineString(p.exterior.coords))
merged=unary_union(lines)
faces=[f for f in polygonize(merged)]
faces0=[f.intersection(LAND) for f in faces]
faces=[]
for f in faces0:
    for p in getattr(f,'geoms',[f]):
        if p.geom_type=='Polygon': faces.append(p)
faces=[f for f in faces if not f.is_empty and f.area>1e-9]
lab=[None]*len(faces)
for i,f in enumerate(faces):
    for k,pts in SEEDS.items():
        for pt in pts:
            if f.contains(Point(pt)): lab[i]=k
lab0=list(lab)
from collections import defaultdict
own=defaultdict(set)
for k,pts in SEEDS.items():
    for pt in pts:
        for i,f in enumerate(faces):
            if f.contains(Point(pt)): own[i].add(k)
for i,ks in own.items():
    if len(ks)>1: print('CONFLICT face',i,sorted(ks))
# merge unlabeled into neighbour with longest shared border
changed=True
while changed:
    changed=False
    for i,f in enumerate(faces):
        if lab[i] is None:
            best=None
            for j,g in enumerate(faces):
                if lab[j] is None or i==j: continue
                l=0 if not f.buffer(2e-6).intersects(g) else f.buffer(2e-6).intersection(g.boundary).length
                if l>0 and (best is None or l>best[0]): best=(l,j)
            if best: lab[i]=lab[best[1]]; changed=True
ARR={}
for f,l in zip(faces,lab):
    if l is None: print('orphan face',f.representative_point()); continue
    ARR.setdefault(l,[]).append(f)
ALC=shape(json.load(open('alcatraz.geojson')))
ARR.setdefault('presidio',[]).append(ALC)
ARR={k:unary_union(v).buffer(0) for k,v in ARR.items()}
for nm,frm,to in OVERRIDES:
    from shapely.geometry import box as _box
    poly=_box(*nm) if isinstance(nm,tuple) else NB[nm]
    piece=ARR[frm].intersection(poly).buffer(0)
    if piece.is_empty: continue
    ARR[frm]=ARR[frm].difference(piece).buffer(0); ARR[to]=unary_union([ARR[to],piece]).buffer(0)
    print('override',nm,frm,'->',to, round(proj(piece).area/1e6,3),'km2')
def clean(g):
    g=g.buffer(0.000005).buffer(-0.000005)
    ps=[p for p in getattr(g,'geoms',[g]) if proj(p).area>1500]
    return unary_union(ps)
ARR={k:clean(v) for k,v in ARR.items()}
tot=0
for k,g in ARR.items():
    a=proj(g).area/1e6; tot+=a
    print(f'{k:22s} {a:6.2f} km2  parts={len(getattr(g,"geoms",[g]))}')
print('total',round(tot,2)); print('faces',len(faces),'unlabeled initially',sum(1 for x in lab0 if x is None))
json.dump({k:mapping(v) for k,v in ARR.items()},open('arr.json','w'))

json.dump(BLINES,open('blines.json','w'))
