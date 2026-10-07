import json, math, re, collections
from shapely.geometry import shape, Point, LineString, Polygon, MultiPolygon, mapping, box
from shapely.ops import unary_union, polygonize, polylabel, transform
from shapely.strtree import STRtree
from geo import proj
A={k:shape(v) for k,v in json.load(open('arr.json')).items()}
FN=json.load(open('find_nbhd.geojson'))
NB={f['properties']['name']:shape(f['geometry']).buffer(0) for f in FN['features']}
NB['Alcatraz Island']=shape(json.load(open('alcatraz.geojson')))
LAND=unary_union(list(NB.values())).buffer(0.00003).buffer(-0.00003)
S=json.load(open('streets.json'))
CREEK=LineString(json.load(open('creek.json')))
ISL=LineString(json.load(open('islais.json')))
# ---------- projection to SVG units
LON0,LAT0=-122.5155,37.8335; K=math.cos(math.radians(37.765))
SC=1000/((-122.355-LON0)*K)   # 1000 units wide
def P(lon,lat): return ((lon-LON0)*K*SC,(LAT0-lat)*SC)
H=P(-122.355,37.7055)[1]
print('viewbox 1000 x',H, 'units per m', SC/ (111320))
def tp(g): return transform(lambda x,y,z=None:P(x,y),g)
def ring_d(coords):
    pts=[f'{x:.1f},{y:.1f}' for x,y in coords]
    # dedupe consecutive
    out=[];
    for p in pts:
        if not out or out[-1]!=p: out.append(p)
    return 'M'+'L'.join(out)+'Z'
def poly_d(g,tol=0.25):
    g=tp(g).simplify(tol)
    d=''
    for p in getattr(g,'geoms',[g]):
        if p.is_empty or p.geom_type!='Polygon': continue
        d+=ring_d(p.exterior.coords)
        for r in p.interiors: d+=ring_d(r.coords)
    return d
def line_d(coords):
    out=[]
    for x,y in coords:
        s=f'{x:.1f},{y:.1f}'
        if not out or out[-1]!=s: out.append(s)
    return 'M'+'L'.join(out) if len(out)>1 else ''
# ---------- meta
META=[
('northbeach',1,'North Beach','North Beach, Telegraph Hill, Russian Hill and Fisherman\u2019s Wharf, everything north of Broadway and east of Van Ness.'),
('downtown',2,'NoMa','North of Market: Union Square, the Financial District, Chinatown, Nob Hill, the Tenderloin, Civic Center and the Ferry Building.'),
('soma',3,'SoMa','South of Market, from the Embarcadero to South Van Ness, down to Townsend and Division Streets.'),
('marina',4,'Pacific Heights & Marina','The Marina, Cow Hollow, Pacific Heights, Japantown and Fort Mason.'),
('westernaddition',5,'Greater Western Addition','Hayes Valley, Alamo Square, the Fillmore, Lower Haight, NoPa, Anza Vista, Haight-Ashbury, Cole Valley, Ashbury Heights, Buena Vista and Corona Heights.'),
('castro',6,'Castro & Noe Valley','Duboce Triangle south of Duboce Avenue, the Castro, Eureka Valley, Dolores Heights, Noe Valley, the east side of Diamond Heights, Fairmount and Glen Park.'),
('mission',7,'Mission & Bernal Heights','The Mission District and Bernal Heights, from Market down to I-280, between Dolores, Guerrero and San Jose Avenue on the west and Potrero Avenue and US-101 on the east.'),
('missionbay',8,'Potrero & Mission Bay','Mission Bay south of Townsend Street (including the ballpark), Showplace Square, Potrero Hill, Dogpatch and the Central Waterfront down to Islais Creek.'),
('hills',9,'The Hills','Twin Peaks, Midtown Terrace, Clarendon Heights, Parnassus Heights with Mount Sutro and UCSF, Forest Knolls, the Forest Hill Extension, the west side of Diamond Heights, Glen Canyon, Miraloma Park, Sherwood Forest, St. Francis Wood, Monterey Heights, Westwood Highlands, Mount Davidson and Sunnyside north of Monterey Boulevard. Working name.'),
('presidio',10,'Presidio & the Islands','The Presidio from Crissy Field to Baker Beach, plus Alcatraz, Treasure Island and Yerba Buena Island.'),
('richmond',11,'Richmond','The Inner and Outer Richmond, Laurel Heights, Presidio Heights, Lone Mountain, Seacliff, Lake Street, Lincoln Park, Lands End and Sutro Heights.'),
('sunset',12,'Sunset','The Sunset north of Ortega Street, plus everything east of 14th Avenue up to Taraval: the Inner Sunset, Golden Gate Heights and Forest Hill.'),
('parkside',13,'Parkside','The Sunset south of Ortega Street (and of Taraval east of 14th Avenue): Parkside, the Outer Sunset\u2019s southern half and West Portal.'),
('lakemerced',14,'Lake Merced & Ingleside','Lake Merced, Fort Funston, Parkmerced, Stonestown, SF State, Merced Manor and the Zoo, plus Ingleside, Oceanview, Merced Heights, Balboa Terrace, Westwood Park, Mount Davidson Manor and Sunnyside south of Monterey Boulevard, all west of I-280.'),
('excelsior',15,'Excelsior & Visitacion Valley','Everything between I-280 and US-101: the Outer Mission, Mission Terrace, the Excelsior, Crocker-Amazon, the Portola, McLaren Park, Visitacion Valley and Sunnydale.'),
('bayview',16,'Bayview & Hunters Point','Everything east of US-101 south of Islais Creek: Bayview, Hunters Point, India Basin, Silver Terrace, Little Hollywood and Candlestick Point.'),
]
# ---------- street index for boundary naming
def pretty(n):
    if n is None: return None
    if 'I-280' in n: return 'I-280'
    if '101' in n or n.startswith('BAY SHORE'): return 'US-101' if '101' in n else 'Bayshore Blvd'
    if 'I-80' in n: return 'I-80'
    if n.startswith('HWY 1 ') or n.startswith('PARK PRESIDIO'): return 'Park Presidio Blvd'
    special={'THE EMBARCADERO':'The Embarcadero','OSHAUGHNESSY BLVD':"O'Shaughnessy Blvd",'BROADWAY':'Broadway','GREAT HWY':'Great Highway'}
    if n in special: return special[n]
    w=[]
    for t in n.split():
        m=re.match(r'0*(\d+)(ST|ND|RD|TH)$',t)
        if m: w.append(m.group(1)+m.group(2).lower())
        else: w.append(t.capitalize())
    return ' '.join(w)
segs=[];names=[]
for s in S:
    c=s['line']['coordinates']
    if len(c)<2: continue
    segs.append(LineString(c)); names.append(s['streetname'])
tree=STRtree(segs)
PRES=NB['Presidio National Park'].boundary; MCL=NB['McLaren Park'].boundary
LANDB=LAND.boundary
def classify(pt):
    if LANDB.distance(pt)<0.00025:
        if pt.y<37.7095 and pt.x>-122.505 and pt.x<-122.39: return 'County line'
        if pt.x<-122.475: return 'Pacific Ocean'
        if pt.y>37.802 and pt.x<-122.447: return 'Golden Gate'
        return 'The Bay'
    if CREEK.distance(pt)<0.0002: return 'Mission Creek'
    if ISL.distance(pt)<0.0003: return 'Islais Creek'
    if MCL.distance(pt)<0.0002: return 'McLaren Park'
    i=tree.nearest(pt); d=segs[i].distance(pt)
    if PRES.distance(pt)<0.00025 and d>0.00012: return 'Presidio boundary'
    if d<0.0003: return pretty(names[i])
    if PRES.distance(pt)<0.0004: return 'Presidio boundary'
    return pretty(names[i]) if d<0.0008 else None
def boundary_streets(g):
    runs=[]
    for p in getattr(g,'geoms',[g]):
        ring=p.exterior; L=ring.length; n=max(40,int(L/0.00015))
        for k in range(n):
            pt=ring.interpolate(k*L/n); c=classify(pt)
            if runs and runs[-1][0]==c: runs[-1][1]+=L/n
            else: runs.append([c,L/n])
    # wrap
    if len(runs)>1 and runs[0][0]==runs[-1][0]: runs[0][1]+=runs.pop()[1]
    tot=collections.Counter()
    for c,l in runs:
        if c: tot[c]+=l*88000
    keep=[c for c,l in tot.items() if l>230]
    # order by first appearance of a long run
    order=[]
    for c,l in runs:
        if c in keep and c not in order: order.append(c)
    return order
BLK=[(Point(float(b['attributes']['INTPTLON']),float(b['attributes']['INTPTLAT'])),b['attributes']['POP100']) for b in json.load(open('blocks.json'))['features']]
def popof(g): return sum(n for p,n in BLK if g.contains(p))
# ---------- assemble
out={'vb':[1000,round(H,1)],'arr':[],'nb':[],'streets':{},'parks':'','water':'','land':'','labels':[]}
out['land']=poly_d(LAND,0.3)
nbassign={}
for n,g in NB.items():
    best=max(A.items(),key=lambda kv: kv[1].intersection(g).area)
    nbassign[n]=best[0]
for key,num,name,blurb in META:
    g=A[key]
    big=max(getattr(g,'geoms',[g]),key=lambda p:p.area)
    lab=polylabel(tp(big),tolerance=0.5)
    area=proj(g).area/1e6
    nbs=sorted([n for n,a in nbassign.items() if a==key])
    neigh=[]
    for k2,g2 in A.items():
        if k2!=key and g.buffer(0.00005).intersection(g2.boundary).length*88000>60: neigh.append(k2)
    out['arr'].append({'id':key,'n':num,'name':name,'blurb':blurb,'d':poly_d(g,0.2),'lx':round(lab.x,1),'ly':round(lab.y,1),
        'km2':round(area,2),'mi2':round(area/2.58999,2),'pop':popof(g),'ring':(1 if num<=3 else 2 if num<=8 else 3),'nb':nbs,'bounds':boundary_streets(g),'neigh':neigh})
    print(num,name,round(area,2),out['arr'][-1]['bounds'])
g=A['ggp']
_gl=polylabel(tp(g),tolerance=0.5)
out['ggp']={'lx':round(_gl.x,1),'ly':round(_gl.y,1),'d':poly_d(g,0.2),'km2':round(proj(g).area/1e6,2),'bounds':boundary_streets(g)}
for n,g in NB.items():
    c=polylabel(tp(max(getattr(g,'geoms',[g]),key=lambda p:p.area)),tolerance=0.5)
    out['nb'].append({'name':n.replace(' / ','/'),'d':poly_d(g,0.3),'x':round(c.x,1),'y':round(c.y,1),'arr':nbassign[n]})
# boundary street labels on map
labs=[]
keys=list(A.keys())
for i in range(len(keys)):
    for j in range(i+1,len(keys)):
        sh=A[keys[i]].buffer(0.00004).intersection(A[keys[j]].boundary)
        for ln in getattr(sh,'geoms',[sh]):
            if ln.geom_type!='LineString' or ln.length*88000<300: continue
            L=ln.length; n=max(2,int(L/0.0002)); run=[]
            pts=[ln.interpolate(k*L/n) for k in range(n+1)]
            cl=[classify(p) for p in pts]
            k=0
            while k<len(pts):
                m=k
                while m+1<len(pts) and cl[m+1]==cl[k]: m+=1
                if cl[k] and m-k>=2 and (m-k)*L/n*88000>380 and cl[k] not in ('The Bay','Pacific Ocean','Golden Gate','County line','Presidio boundary','McLaren Park','Islais Creek','Mission Creek'):
                    a=pts[(k+m)//2]; p0=P(pts[k].x,pts[k].y); p1=P(pts[m].x,pts[m].y)
                    ang=math.degrees(math.atan2(p1[1]-p0[1],p1[0]-p0[0]))
                    if ang>90: ang-=180
                    if ang<-90: ang+=180
                    x,y=P(a.x,a.y); labs.append((cl[k],round(x,1),round(y,1),round(ang,1),(m-k)*L/n*88000))
                k=m+1
labs.sort(key=lambda t:-t[4]); keep=[]
for t in labs:
    if all(not(u[0]==t[0] and math.hypot(u[1]-t[1],u[2]-t[2])<90) for u in keep) and all(math.hypot(u[1]-t[1],u[2]-t[2])>18 for u in keep): keep.append(t)
out['labels']=[t[:4] for t in keep]; print('labels',len(keep))
# streets merged per class
from shapely.prepared import prep
LANDBUF=prep(LAND.buffer(0.0005))
cls=collections.defaultdict(list)
for s in S:
    c=s['line']['coordinates']; cc=s.get('classcode','5'); lay=s.get('layer','')
    if lay in ('PAPER','PAPER_WATER','PAPER_FWYS','PSEUDO'): continue
    k='hwy' if cc in ('1',) else 'major' if cc in ('2','3') else 'minor' if cc=='4' else 'local'
    if cc=='6': k='hwy'
    l=tp(LineString(c)).simplify(0.25)
    if not LANDBUF.intersects(LineString(c)): continue
    cls[k].append(line_d(l.coords))
for k,v in cls.items(): out['streets'][k]=''.join(v); print(k,len(out['streets'][k]))
# parks & water from OSM
G=json.load(open('osm_green.json'))
parks=[];water=[]
for e in G['elements']:
    t=e.get('tags',{})
    polys=[]
    if e['type']=='way' and 'geometry' in e:
        c=[(p['lon'],p['lat']) for p in e['geometry']]
        if len(c)>3 and c[0]==c[-1]: polys=[Polygon(c)]
    elif e['type']=='relation':
        ls=[LineString([(p['lon'],p['lat']) for p in m['geometry']]) for m in e.get('members',[]) if m.get('role')=='outer' and 'geometry' in m]
        if ls: polys=list(polygonize(unary_union(ls)))
    for p in polys:
        p=p.buffer(0)
        if p.is_empty: continue
        isw=t.get('natural')=='water'
        if not isw and proj(p).area<3000: continue
        if isw and proj(p).area<2000: continue
        p=p.intersection(LAND)
        if p.is_empty: continue
        (water if isw else parks).append(p)
out['parks']=poly_d(unary_union(parks),0.3)
out['water']=poly_d(unary_union(water),0.3)
# boundary street labels: from spec legs
exec(open('spec.py').read().split('EXTRA_RINGS')[0].replace('from geo','#'), globals()) if False else None
json.dump(out,open('mapdata.json','w'),separators=(',',':'))
import os; print('size',os.path.getsize('mapdata.json')/1e6,'MB')
