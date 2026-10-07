import json
from shapely.geometry import shape, Point, LineString
from shapely.ops import unary_union, split
from shapely.strtree import STRtree
from geo import proj, along
A={k:shape(v) for k,v in json.load(open('arr.json')).items()}
AN={f['properties']['nhood']:shape(f['geometry']).buffer(0) for f in json.load(open('analysis_nbhd.geojson'))['features']}
sq=lambda g: proj(g).area/2.58999e6
km=lambda g: proj(g).area/1e6
# ---- 16 option = current
O16=dict(A)
# ---- 18 option
O18=dict(A)
js=along('JUNIPERO SERRA BLVD',(-122.4716,37.7347),(-122.4721,37.7081))
cut=LineString([(js[0][0],js[0][1]+0.003)]+js+[(js[-1][0],js[-1][1]-0.004)])
parts=list(split(A['lakemerced'],cut).geoms)
west=unary_union([p for p in parts if p.representative_point().x< -122.4725 or p.centroid.x< -122.4735])
east=A['lakemerced'].difference(west)
O18.pop('lakemerced'); O18['lakemerced18']=west; O18['ingleside18']=east
E=A['excelsior']; eastpoly=unary_union([AN['Portola'],AN['McLaren Park'],AN['Visitacion Valley']])
pe=E.intersection(eastpoly); pw=E.difference(eastpoly)
pws=sorted(getattr(pw,'geoms',[pw]),key=lambda p:-p.area)
pw=pws[0]; pe=unary_union([pe]+pws[1:]).buffer(0.000005).buffer(-0.000005)
O18.pop('excelsior'); O18['excelsior18']=pw; O18['portola18']=pe
# ---- population
B=json.load(open('blocks.json'))['features']
pts=[(Point(float(b['attributes']['INTPTLON']),float(b['attributes']['INTPTLAT'])),b['attributes']['POP100'],b['attributes']['HU100']) for b in B]
def pop(O):
    out={k:0 for k in O}; miss=0
    for p,n,h in pts:
        for k,g in O.items():
            if g.contains(p): out[k]+=n; break
        else: miss+=n
    return out,miss
P16,m16=pop(O16); P18,m18=pop(O18)
print('unassigned pop 16:',m16,' 18:',m18)
# ---- open land in lake merced area
nm=json.load(open('nm_Lake_Merced__San_Francisco.json'))[0]['geojson']; LAKE=shape(nm).buffer(0)
ZOO=shape(json.load(open('nm_San_Francisco_Zoo.json'))[0]['geojson']).buffer(0)
G=json.load(open('osm_green.json'))
from shapely.geometry import Polygon
def way(id_):
    for e in G['elements']:
        if e['type']=='way' and e['id']==id_: return Polygon([(p['lon'],p['lat']) for p in e['geometry']]).buffer(0)
items=[('Lake Merced (water)',LAKE),('TPC Harding Park & Fleming (golf)',way(16753068)),('San Francisco Golf Club',way(16753994)),('Olympic Club, SF part (golf)',way(1417078425)),
       ('Fort Funston',way(404851503)),('San Francisco Zoo',ZOO),('Lake Merced Park (shore & trails)',way(404847043)),('Ocean Beach south (sand)',way(305490053))]
def openland(g):
    acc=None; rows=[]
    for n,p in items:
        piece=p.intersection(g)
        if acc is not None: piece=piece.difference(acc)
        rows.append((n,sq(piece))); acc=piece if acc is None else unary_union([acc,piece])
    return rows,sq(acc)
res={'O16':{k:(sq(g),P16[k]) for k,g in O16.items()},'O18':{k:(sq(g),P18[k]) for k,g in O18.items()}}
r16,t16=openland(O16['lakemerced']); r18,t18=openland(O18['lakemerced18'])
res['open16']=(r16,t16); res['open18']=(r18,t18)
json.dump(res,open('analysis.json','w'),indent=1)
for k,(a,p) in sorted(res['O16'].items(),key=lambda x:-x[1][1]): print('16',k,round(a,2),p)
for k,(a,p) in sorted(res['O18'].items(),key=lambda x:-x[1][1]): print('18',k,round(a,2),p)
print('open 14 (16-opt):',[(n,round(a,3)) for n,a in r16],round(t16,2))
print('open LM (18-opt):',[(n,round(a,3)) for n,a in r18],round(t18,2))
json.dump({k:v.__geo_interface__ for k,v in O18.items()},open('arr18.json','w'))
