# v4: a new 1st arrondissement, Downtown: the Financial District (with Union Square east of Kearny), the Embarcadero,
# New Montgomery (Yerba Buena east of 3rd Street), the East Cut and Rincon Hill. Jackson Square and Golden Gateway join Northport.
# Renumber: 1 Downtown, 2 Northport, 3 NoMa, 4 SoMa, 5-9 Ring 2, and The Hills move to Ring 3 as the 14th.
# Idempotent: always starts from arr_v6.json (the v3 output).
import json, math
from shapely.geometry import shape, mapping, Point, LineString, box
from shapely.ops import unary_union, polylabel, linemerge, split
src=open('gen.py').read().split('# ---------- assemble')[0]
exec(src.replace("open('arr.json')","open('arr_v6.json')"))
GZ={o['name']:shape(o['g']).buffer(0) for o in json.load(open('gaz.json'))['nb']}
eps=2e-6
def clean(g,minarea=2e-7):
    g=g.buffer(eps,join_style=2).buffer(-eps,join_style=2)
    return unary_union([p for p in getattr(g,'geoms',[g]) if p.geom_type=='Polygon' and p.area>minarea])
BOX=box(-122.43,37.76,-122.37,37.81)
def street(name,bb):
    l=linemerge(unary_union([shape(x['line']) for x in S if x['streetname']==name]).intersection(box(*bb)))
    if l.geom_type=='MultiLineString': l=max(l.geoms,key=lambda g:g.length)
    c=list(l.coords)
    def ext(p,q): dx,dy=q[0]-p[0],q[1]-p[1]; L=math.hypot(dx,dy); return (q[0]+dx/L*0.1,q[1]+dy/L*0.1)
    return LineString([ext(c[1],c[0])]+c+[ext(c[-2],c[-1])])
def side(line,ref): return [p for p in split(BOX,line).geoms if p.contains(Point(ref))][0]
eK=side(street('KEARNY ST',(-122.41,37.787,-122.40,37.80)),(-122.398,37.793))     # east of Kearny
e3=side(street('03RD ST',(-122.41,37.775,-122.39,37.788)),(-122.395,37.787))      # east of 3rd
north=unary_union([GZ['Financial District'],GZ['Embarcadero'],GZ['Union Square'].intersection(eK)])
south=unary_union([GZ['East Cut'],GZ['Rincon Hill'],GZ['Yerba Buena'].intersection(e3)])
json.dump({'eK':mapping(eK),'e3':mapping(e3)},open('v4_lines.json','w'))
core=clean(unary_union([north.intersection(A['downtown']),south.intersection(A['soma'])]))
toNP=clean(unary_union([GZ['Jackson Square'],GZ['Golden Gateway']]).intersection(A['downtown']).difference(core))
A['downtown']=clean(A['downtown'].difference(core).difference(toNP))
A['soma']=clean(A['soma'].difference(core))
A['northbeach']=clean(unary_union([A['northbeach'],toNP]))
A['core']=core
# hand leftover slivers (old ring-1 land not in any new piece) to the neighbor sharing the longest edge
old=unary_union([shape(v) for k,v in json.load(open('arr_v6.json')).items() if k in ('downtown','soma','northbeach')])
left=old.difference(unary_union([A[k] for k in ('downtown','soma','northbeach','core')]))
for p in getattr(left,'geoms',[left]):
    if p.geom_type!='Polygon' or p.area<1e-12: continue
    k=max(('downtown','soma','northbeach','core'),key=lambda k:p.buffer(2e-5).intersection(A[k]).area)
    A[k]=unary_union([A[k],p])
new=unary_union(list(A.values())); allold=unary_union([shape(v) for v in json.load(open('arr_v6.json')).values()])
print('coverage diff km2',round(proj(allold.symmetric_difference(new)).area/1e6,5))
for k in ('core','downtown','soma','northbeach'): print(k,round(proj(A[k]).area/2.58999e6,3),'mi2',A[k].geom_type,len(getattr(A[k],'geoms',[A[k]])))
json.dump({k:mapping(v) for k,v in A.items()},open('arr.json','w'))
d=json.load(open('mapdata_v12.json'))
NUM={'core':1,'northbeach':2,'downtown':3,'soma':4,'marina':5,'westernaddition':6,'castro':7,'mission':8,'missionbay':9,
     'presidio':10,'richmond':11,'sunset':12,'lakemerced':13,'hills':14,'excelsior':15,'bayview':16}
tmpl=next(a for a in d['arr'] if a['id']=='soma')
core_rec={k:v for k,v in tmpl.items()}; core_rec.update(id='core',name='Downtown',long='Financial District & Rincon Hill',cn='Brown',hex='#974e06',why='The brown hulls of the gold-rush ships abandoned in Yerba Buena Cove, now buried beneath the Financial District.')
d['arr'].append(core_rec)
for a in d['arr']:
    a['n']=NUM[a['id']]
    if a['id']=='excelsior': a.update(cn='Aubergine',hex='#7a067a',why='Ube, for the Filipino community of the Excelsior and the Outer Mission.')
    if a['id'] in ('core','downtown','soma','northbeach'):
        g=A[a['id']]; big=max(getattr(g,'geoms',[g]),key=lambda p:p.area); lab=polylabel(tp(big),tolerance=0.5)
        area=proj(g).area/1e6
        a.update(d=poly_d(g,0.2),km2=round(area,2),mi2=round(area/2.58999,2),pop=popof(g),bounds=boundary_streets(g),lx=round(lab.x,1),ly=round(lab.y,1))
        print(a['id'],a['mi2'],a['pop'],a['bounds'],a['lx'],a['ly'])
    g=A[a['id']]
    a['neigh']=[k2 for k2,g2 in A.items() if k2!=a['id'] and g.buffer(0.00005).intersection(g2.boundary).length*88000>60]
d['arr'].sort(key=lambda a:a['n'])
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
