# v3: Golden Gate Heights, Forest Hill and West Portal join the 9th; the 12th and 13th merge; renumber 14-16 -> 13-15.
# The 9th's western edge follows 17th Avenue down to Rivera, then 15th Avenue to Sloat; east of Funston, Lawton is the line. Idempotent: always starts from arr_v5.json.
import json, math
from shapely.geometry import shape, mapping
from shapely.ops import unary_union, polylabel
src=open('gen.py').read().split('# ---------- assemble')[0]
exec(src.replace("open('arr.json')","open('arr_v5.json')"))   # A (pre-v3), classify, boundary_streets, popof, poly_d, tp, P ...
MOVE=['Golden Gate Heights','Forest Hill','West Portal']
G=json.load(open('gaz.json'))
mv=unary_union([shape(o['g']) for o in G['nb'] if o['name'] in MOVE])
eps=2e-6
def clean(g,minarea=2e-7):
    g=g.buffer(eps,join_style=2).buffer(-eps,join_style=2)
    parts=[p for p in getattr(g,'geoms',[g]) if p.geom_type=='Polygon' and p.area>minarea]
    return unary_union(parts)
hills=clean(unary_union([A['hills'],mv]))
sunset=clean(unary_union([A['sunset'],A['parkside']]).difference(hills))
# 16th Avenue as the western edge of the 9th, from Lawton down to Sloat
from shapely.geometry import LineString, Polygon
from shapely.ops import linemerge
NLAT,SLAT=37.7593,37.7300
seg=[LineString(x['line']['coordinates']) for x in S if x['streetname']=='16TH AVE']
l16=unary_union(seg).intersection(Polygon([(-122.6,SLAT),(-122.3,SLAT),(-122.3,NLAT),(-122.6,NLAT)]))
l16=linemerge(l16) if l16.geom_type=='MultiLineString' else l16
if l16.geom_type=='MultiLineString': l16=max(l16.geoms,key=lambda g:g.length)
cs=list(l16.coords)
if cs[0][1]<cs[-1][1]: cs=cs[::-1]                 # north -> south
# south of Rivera Street the line moves one block east to 15th Avenue
RLAT=37.74692
c15=sorted({(round(x,6),round(y,6)) for x_ in S if x_['streetname']=='15TH AVE' for x,y in x_['line']['coordinates'] if 37.7375<y<37.7469 and -122.4725<x<-122.4705},key=lambda p:-p[1])
c17=sorted({(round(x,6),round(y,6)) for x_ in S if x_['streetname']=='17TH AVE' for x,y in x_['line']['coordinates'] if RLAT<y<NLAT+0.003},key=lambda p:-p[1])
cs=c17+[(-122.47382,37.74687),(-122.47274,RLAT),(-122.47132,37.74698)]+c15     # 17th Ave north of Rivera, Rivera, 15th Ave south of Rivera
cs=[p for p in cs if p[1]<=NLAT]; cs=[(cs[0][0],NLAT)]+cs+[(cs[-1][0],SLAT)]         # clip/extend to the band edges
east=Polygon(cs+[(-122.40,SLAT),(-122.40,NLAT)]).buffer(0)
west=Polygon(cs+[(-122.60,SLAT),(-122.60,NLAT)]).buffer(0)
hills=clean(unary_union([hills,sunset.intersection(east)]).difference(west))
sunset=clean(unary_union([sunset,A['hills'].intersection(west),mv.intersection(west)]).difference(hills))
# east of Funston Avenue, Lawton Street divides the 9th from the 12th (up to 7th Avenue)
FX,X7=-122.47024,-122.46378
law=unary_union([LineString(x['line']['coordinates']) for x in S if x['streetname']=='LAWTON ST']).intersection(Polygon([(FX,37.755),(X7,37.755),(X7,37.761),(FX,37.761)]))
law=linemerge(law) if law.geom_type=='MultiLineString' else law
if law.geom_type=='MultiLineString': law=max(law.geoms,key=lambda g:g.length)
lc=sorted(law.coords)                                   # west -> east
lc=[(FX,lc[0][1])]+lc+[(X7,lc[-1][1])]
north=Polygon(lc+[(X7,37.7612),(FX,37.7612)]).buffer(0)
moved=hills.intersection(north)
hills=clean(hills.difference(north)); sunset=clean(unary_union([sunset,moved]).difference(hills))
A['hills']=hills; A['sunset']=sunset; del A['parkside']
# give any leftover slivers to whoever borders them most -- check coverage
old=unary_union([shape(v) for k,v in json.load(open('arr_v5.json')).items()])
new=unary_union(list(A.values()))
print('coverage diff km2', round(proj(old.symmetric_difference(new)).area/1e6,4))
json.dump({k:mapping(v) for k,v in A.items()},open('arr.json','w'))
d=json.load(open('mapdata.json'))
d['arr']=[a for a in d['arr'] if a['id']!='parkside']
RENUM={'lakemerced':13,'excelsior':14,'bayview':15}
for a in d['arr']:
    if a['id'] in RENUM: a['n']=RENUM[a['id']]
    if a['id'] in ('hills','sunset'):
        g=A[a['id']]; big=max(getattr(g,'geoms',[g]),key=lambda p:p.area); lab=polylabel(tp(big),tolerance=0.5)
        area=proj(g).area/1e6
        a.update(d=poly_d(g,0.2),km2=round(area,2),mi2=round(area/2.58999,2),pop=popof(g),bounds=boundary_streets(g),lx=round(lab.x,1),ly=round(lab.y,1))
        print(a['id'],a['mi2'],a['pop'],a['bounds'])
    g=A[a['id']]
    a['neigh']=[k2 for k2,g2 in A.items() if k2!=a['id'] and k2!='ggp' and g.buffer(0.00005).intersection(g2.boundary).length*88000>60]
d['arr'].sort(key=lambda a:a['n'])
# boundary street labels (same rules as gen.py)
labs=[]; keys=list(A.keys())
for i in range(len(keys)):
    for j in range(i+1,len(keys)):
        sh=A[keys[i]].buffer(0.00004).intersection(A[keys[j]].boundary)
        for ln in getattr(sh,'geoms',[sh]):
            if ln.geom_type!='LineString' or ln.length*88000<300: continue
            L=ln.length; n=max(2,int(L/0.0002)); pts=[ln.interpolate(k*L/n) for k in range(n+1)]; cl=[classify(p) for p in pts]; k=0
            while k<len(pts):
                m=k
                while m+1<len(pts) and cl[m+1]==cl[k]: m+=1
                if cl[k] and m-k>=2 and (m-k)*L/n*88000>380 and cl[k] not in ('The Bay','Pacific Ocean','Golden Gate','County line','Presidio boundary','McLaren Park','Islais Creek','Mission Creek'):
                    a_=pts[(k+m)//2]; p0=P(pts[k].x,pts[k].y); p1=P(pts[m].x,pts[m].y)
                    ang=math.degrees(math.atan2(p1[1]-p0[1],p1[0]-p0[0]))
                    if ang>90: ang-=180
                    if ang<-90: ang+=180
                    x,y=P(a_.x,a_.y); labs.append((cl[k],round(x,1),round(y,1),round(ang,1),(m-k)*L/n*88000))
                k=m+1
labs.sort(key=lambda t:-t[4]); keep=[]
for t in labs:
    if all(not(u[0]==t[0] and math.hypot(u[1]-t[1],u[2]-t[2])<90) for u in keep) and all(math.hypot(u[1]-t[1],u[2]-t[2])>18 for u in keep): keep.append(t)
d['labels']=[t[:4] for t in keep]; print('labels',len(keep))
json.dump(d,open('mapdata.json','w'),separators=(',',':'))
