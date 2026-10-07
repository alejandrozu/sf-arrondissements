import json, math
from shapely.geometry import shape, Polygon, LineString, Point, mapping, box
from shapely.ops import unary_union, polygonize
from geo import proj, along, X
A={k:shape(v) for k,v in json.load(open('arr.json')).items()}
NUM={'northbeach':1,'downtown':2,'soma':3,'marina':4,'westernaddition':5,'castro':6,'mission':7,'missionbay':8,'hills':9,'presidio':10,'richmond':11,'sunset':12,'parkside':13,'lakemerced':14,'excelsior':15,'bayview':16,'ggp':0}
KEY={v:k for k,v in NUM.items()}
sqmi=lambda g: proj(g).area/2.58999e6
FIND={f['properties']['name']:shape(f['geometry']).buffer(0) for f in json.load(open('find_nbhd.geojson'))['features']}
REAL={f['properties']['nbrhood']:shape(f['geometry']).buffer(0) for f in json.load(open('ds_realtor.geojson'))['features']}
CBD={f['properties']['community_benefit_district']:shape(f['geometry']).buffer(0) for f in json.load(open('ds_c28a-f6gs.geojson'))['features']}
CD={f['properties']['district_name']:shape(f['geometry']).buffer(0) for f in json.load(open('ds_5xmc-5bjj.geojson'))['features']}
G=json.load(open('osm_green.json'))
def osmway(i,src=G):
    for e in src['elements']:
        if e['type']=='way' and e['id']==i: return Polygon([(p['lon'],p['lat']) for p in e['geometry']]).buffer(0)
OSMP=json.load(open('osm_places.json'))
def osmplace(name):
    for e in OSMP['elements']:
        if e['type']=='way' and e.get('tags',{}).get('name')==name: return Polygon([(p['lon'],p['lat']) for p in e['geometry']]).buffer(0)
def S(n,p,q): return along(n,p,q)
def loop(*legs):
    c=[]
    for l in legs: c+= [tuple(x) for x in l]
    return Polygon(c).buffer(0)
def ext(c,m=0.0015):
    def e(a,b):
        dx,dy=b[0]-a[0],b[1]-a[1]; n=math.hypot(dx,dy) or 1; return (b[0]+dx/n*m,b[1]+dy/n*m)
    return [e(c[1],c[0])]+list(c)+[e(c[-2],c[-1])]
def subdivide(parent,lines,seeds):
    ls=[LineString(ext(c)) for c in lines]+[LineString(p.exterior.coords) for p in getattr(parent,'geoms',[parent])]
    faces=[f.intersection(parent) for f in polygonize(unary_union(ls))]
    faces=[p for f in faces for p in getattr(f,'geoms',[f]) if p.geom_type=='Polygon' and p.area>1e-10]
    lab=[None]*len(faces)
    for i,f in enumerate(faces):
        for n,pts in seeds.items():
            if any(f.contains(Point(p)) for p in pts): lab[i]=n
    # unlabeled -> neighbour with longest border
    for _ in range(5):
        for i,f in enumerate(faces):
            if lab[i] is None:
                best=None
                for j,g in enumerate(faces):
                    if lab[j] is None: continue
                    l=f.buffer(1e-6).intersection(g.boundary).length
                    if l>0 and (best is None or l>best[0]): best=(l,lab[j])
                if best: lab[i]=best[1]
    out={}
    for f,l in zip(faces,lab):
        if l: out.setdefault(l,[]).append(f)
    return {k:unary_union(v) for k,v in out.items()}
def mid(a,b): return ((a[0]+b[0])/2,(a[1]+b[1])/2)
