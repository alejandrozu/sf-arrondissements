import json, math
from shapely.geometry import shape
from shapely.ops import polylabel, transform
d=json.load(open('mapdata.json')); G=json.load(open('gaz.json'))
# Alcatraz Island as its own neighborhood of the 10th
if not any(o['name']=='Alcatraz Island' for o in G['nb']):
    from shapely.geometry import mapping as _mp
    from geo import proj as _pj
    _A=shape(json.load(open('arr.json'))['presidio'])
    _alc=[p for p in _A.geoms if p.centroid.y>37.825 and p.centroid.x<-122.41][0]
    G['nb'].append({'arr':'presidio','n':10,'name':'Alcatraz Island','origs':['Alcatraz Island'],'sqmi':round(_pj(_alc).area/2589988.11,3),'g':_mp(_alc)})
# v3: Golden Gate Heights, Forest Hill and West Portal join the 9th; the 12th and 13th merge; 14-16 renumbered 13-15
V3_MOVE={'Golden Gate Heights','Forest Hill','West Portal'}
V3_ARR={'parkside':'sunset','ggp':'richmond'}
V3_NUM={'presidio':10,'richmond':11,'sunset':12,'lakemerced':13,'excelsior':14,'bayview':15,'hills':9}
_old2id={}
for o in G['nb']:
    _old2id[(int(o['n']),o['name'])]=o['arr']
    if o['name'] in V3_MOVE: o['arr']='hills'
    o['arr']=V3_ARR.get(o['arr'],o['arr'])
    if o['arr'] in V3_NUM: o['n']=V3_NUM[o['arr']]
for o in G['nb']:
    if o['name']=='Oceanview' and o['arr']=='lakemerced': o['name']='Inner Oceanview'
_new={o['name']:(o['arr'],int(o['n'])) for o in G['nb']}
_spl=[]
for r in G['splits']:
    groups={}
    for sd in r['sides']:
        for nm in sd['names']:
            if nm not in _new: continue
            ar,nn=_new[nm]; groups.setdefault(nn,[]).append(nm)
    if len(groups)<2: continue
    _spl.append({'orig':r['orig'],'sides':[{'n':nn,'names':nms,'pct':0,'sqmi':0} for nn,nms in sorted(groups.items())]})
G['splits']=_spl
# Parnassus Piedmont: the new neighborhood of the 9th east of 7th Avenue, between Golden Gate Park and Lawton
import os as _os
if _os.path.exists('v3_e7.json') and not any(o['name']=='Parnassus Piedmont' for o in G['nb']):
    from shapely.geometry import mapping as _mp3
    from shapely.ops import unary_union as _uu3
    _E7=shape(json.load(open('v3_e7.json'))); _H=shape(json.load(open('arr.json'))['hills'])
    _taken=_uu3([shape(o['g']).buffer(0) for o in G['nb'] if o['arr']=='hills' and o['name']!='Inner Sunset'])
    _sg=_H.intersection(_E7).difference(_taken).buffer(-4e-5,join_style=2).buffer(4e-5,join_style=2).intersection(_H)   # drop thin slivers along 7th Ave
    _sg=_uu3([q for q in getattr(_sg,'geoms',[_sg]) if q.geom_type=='Polygon' and q.area>2e-7])
    G['nb'].append({'arr':'hills','n':9,'name':'Parnassus Piedmont','origs':['Parnassus Piedmont'],'sqmi':0,'g':_mp3(_sg)})
# clip the 9th's and 12th's neighborhoods to the new borders (16th Avenue); leftover strips join the neighbor sharing the longest edge
from shapely.geometry import mapping as _mp2
from shapely.ops import unary_union as _uu
from geo import proj as _pj2
_AR3={k:shape(v) for k,v in json.load(open('arr.json')).items()}
for _k in ('hills','sunset'):
    _its=[o for o in G['nb'] if o['arr']==_k]
    _gs={id(o):shape(o['g']).buffer(0).intersection(_AR3[_k]) for o in _its}
    _left=_AR3[_k].difference(_uu(list(_gs.values())))
    for _p in getattr(_left,'geoms',[_left]):
        if _p.geom_type!='Polygon' or _p.area<1e-9: continue
        _best=max(_its,key=lambda o:_p.buffer(2e-5).intersection(_gs[id(o)]).area)
        _gs[id(_best)]=_uu([_gs[id(_best)],_p])
    for o in _its:
        _g=_gs[id(o)].buffer(1e-7).buffer(-1e-7)
        _g=_uu([q for q in getattr(_g,'geoms',[_g]) if q.geom_type=='Polygon' and q.area>2e-8])
        o['g']=_mp2(_g); o['sqmi']=round(_pj2(_g).area/2589988.11,3)
LON0,LAT0=-122.5155,37.8335; K=math.cos(math.radians(37.765)); SC=1000/((-122.355-LON0)*K)
def P(lon,lat): return ((lon-LON0)*K*SC,(LAT0-lat)*SC)
def tp(g): return transform(lambda x,y,z=None:P(x,y),g)
def ring_d(coords):
    out=[]
    for x,y in coords:
        s=f'{x:.1f},{y:.1f}'
        if not out or out[-1]!=s: out.append(s)
    return 'M'+'L'.join(out)+'Z'
def poly_d(g,tol=0.3):
    g=tp(g).simplify(tol); dd=''
    for p in getattr(g,'geoms',[g]):
        if p.geom_type!='Polygon' or p.is_empty: continue
        dd+=ring_d(p.exterior.coords)
        for r in p.interiors: dd+=ring_d(r.coords)
    return dd
GLOBAL={'Western Addition':'Fillmore','Panhandle':'NoPa','Downtown / Union Square':'Union Square','Lincoln Park / Ft. Miley':'Lincoln Park & Lands End','Presidio National Park':'Presidio','Candlestick Point SRA':'Candlestick Point','Laurel Heights / Jordan Park':'Laurel Heights','Fishermans Wharf':"Fisherman's Wharf",'Mt. Davidson Manor':'Mount Davidson Manor'}
# split lookup: piece name -> (orig, other sides)
splits=[]
spl_for={}
for r in G['splits']:
    sides=[{'n':s['n'],'names':s['names'],'pct':s['pct'],'sqmi':s['sqmi']} for s in r['sides']]
    splits.append({'orig':GLOBAL.get(r['orig'],r['orig']),'sides':sides})
    for s in sides:
        others=[f"{o['names'][0]} ({o['n']}{'er' if o['n']==1 else 'e'})" for o in sides if o is not s]
        key=(s['n'],s['names'][0]); spl_for.setdefault(key,[]).append(f"Part of {GLOBAL.get(r['orig'],r['orig'])}; other side: "+', '.join(others))
nb=[]
for o in G['nb']:
    if o['n']==0: continue
    g=shape(o['g'])
    big=max(getattr(g,'geoms',[g]),key=lambda p:p.area)
    c=polylabel(tp(big),tolerance=0.3)
    nb.append({'name':o['name'],'d':poly_d(g),'x':round(c.x,1),'y':round(c.y,1),'arr':o['arr'],'sqmi':o['sqmi'],'aka':[a for a in o['origs'] if a!=o['name']]})
d['nb']=nb
for a in d['arr']:
    items=sorted([o for o in G['nb'] if o['arr']==a['id']],key=lambda o:-o['sqmi'])
    a['nb']=[o['name'] for o in items]
    a['nbsplit']={o['name']:spl_for[(a['n'],o['name'])][0] for o in items if (a['n'],o['name']) in spl_for}
d['splits']=splits
FL=json.load(open('floats.json'))
d['float']=[]
for f in FL:
    x,y=P(f['lon'],f['lat']); d['float'].append({'name':f['name'],'x':round(x,1),'y':round(y,1),'arr':f['arr']})
for a in d['arr']:
    a['micro']=sorted(f['name'] for f in FL if f['arr']==a['id'])
    if a['id']=='northbeach': a['blurb']='Little Italy, North Beach, Telegraph Hill, Russian Hill, Lombard Crest Russian Hill and Fisherman\u2019s Wharf, everything north of Broadway and east of Van Ness.'
    if a['id']=='marina': a['blurb']='Marina Fine Arts, Spanish Marina and East Marina; Cow Hollow and Union Street; Cannon Hill and Lafayette Pacific Heights, Lower Pacific Heights, Japantown and Fort Mason.'
    if a['id']=='westernaddition': a['blurb']='Hayes Valley, Alamo Square, the Fillmore, Lower Haight, NoPa, Anza Vista, Haight-Ashbury, Cole Valley, Ashbury Heights, Buena Vista and Corona Heights.'
    if a['id']=='castro': a['blurb']='Duboce Triangle south of Duboce Avenue, the Castro, Eureka Valley, Dolores Heights, Mission Dolores, Downtown Noe Valley, Duncan Hill and Horner\u2019s Hill (greater Noe Valley), Gold Mine Hill, Fairmount and Glen Park.'
    if a['id']=='mission': a['blurb']='The Valencia Corridor, South Van Ness, the Food Processing District, Central Mission, Calle 24, Liberty Hill, the Mission Triangle, La Lengua, Bernal Heights, the Bernal Triangle, Peralta Heights, Holly Park and St. Mary\u2019s Park.'
    if a['id']=='missionbay': a['blurb']='Oracle Park, Mission Creek, Mission Bay, Showplace Square, Potrero Valley, Potrero Hill, Potrero Terrace, Dogpatch, Potrero Point and the Central Waterfront down to Islais Creek.'
    if a['id']=='bayview': a['blurb']='Everything east of US-101 south of Islais Creek: Inner Bayview, Bayview Hills, Bayview Valley, Bayview Heights, Hunters Point, India Basin, Amador Point, Islais Creek, Silver Terrace, the Produce Market, Bret Harte and Candlestick Point.'
    if a['id']=='richmond': a['blurb']='The Inner and Outer Richmond, Laurel Heights, Presidio Heights, Lone Mountain, Seacliff, Lake Street, Lincoln Park, Lands End and Sutro Heights, and Golden Gate Park from the Panhandle to Ocean Beach.'
    if a['id']=='lakemerced': a['blurb']=a['blurb'].replace(' Oceanview,',' Inner Oceanview,').replace('Inner Inner','Inner')
    if a['id']=='hills': a['blurb']='Twin Peaks, Midtown Terrace, Clarendon Heights, Parnassus Heights with Mount Sutro and UCSF, Parnassus Piedmont east of 7th Avenue, Golden Gate Heights, Forest Hill and the Forest Hill Extension, Forest Knolls, West Portal, the west side of Diamond Heights, Glen Canyon, Miraloma Park, Sherwood Forest, St. Francis Wood, Monterey Heights, Westwood Highlands and Sunnyside north of Monterey Boulevard.'
    if a['id']=='sunset': a['blurb']='The whole Sunset and Parkside, from Golden Gate Park down to Sloat Boulevard and from the ocean to the hills: the Inner, Central and Outer Sunset, Inner and Outer Parkside, Parkside and Pine Lake Park.'
    if a['id']=='downtown': a['blurb']='North of Market: Union Square, the Financial District, the Embarcadero, Chinatown, Nob Hill, Lower Polk, the Tenderloin and Civic Center.'
json.dump(d,open('mapdata.json','w'),separators=(',',':'))
print(len(nb),'neighborhoods,',len(splits),'splits')
# ---------- site v2 extras
from shapely.geometry import Point
from shapely.ops import unary_union
from shapely.strtree import STRtree
from geo import proj
SHORT={'northbeach':'Northport','downtown':'NoMa','soma':'SoMa','marina':'Pacific','westernaddition':'Ashbury','castro':'The Valleys','mission':'The Mission','missionbay':'Potrero','hills':'The Hills','presidio':'Federal','richmond':'The Richmond','sunset':'The Sunset','lakemerced':'Oceanview','excelsior':'Southside','bayview':'Bayview'}
LONGV3={'sunset':'Sunset & Parkside'}
def ringof(n): return 'r1' if n<=3 else 'r2' if n<=9 else 'r3'
RLAB={'r1':'Ring 1','r2':'Ring 2','rh':'Ring –','r3':'Ring 3'}
for a in d['arr']:
    a.setdefault('long',a['name'])
    if a['id'] in LONGV3: a['long']=LONGV3[a['id']]
    a['name']=SHORT[a['id']]; a['ring']=ringof(a['n']); a['ringlab']=RLAB[a['ring']]
BLK=[(Point(float(b['attributes']['INTPTLON']),float(b['attributes']['INTPTLAT'])),b['attributes']['POP100']) for b in json.load(open('blocks.json'))['features']]
bt=STRtree([p for p,_ in BLK])
def pop(g):
    idx=bt.query(g,predicate='contains'); return int(sum(BLK[i][1] for i in idx))
geoms={}
for o in G['nb']:
    if o['n']==0: continue
    geoms[o['name']+'|'+o['arr']]=shape(o['g'])
FLs=json.load(open('floats.json'))
keys=list(geoms)
for item in d['nb']:
    key=item['name']+'|'+item['arr']; g=geoms[key]
    km2=proj(g).area/1e6
    item['pop']=pop(g); item['acres']=round(km2*247.105); item['ha']=round(km2*100)
    item['fl']=[f['name'] for f in FLs if g.contains(Point(f['lon'],f['lat']))]
    gb=g.buffer(3e-5)
    item['nbr']=sorted({k.split('|')[0]+'|'+k.split('|')[1] for k in keys if k!=key and gb.intersects(geoms[k]) and gb.intersection(geoms[k]).area>2e-9})
    arr=next(x for x in d['arr'] if x['id']==item['arr'])
    item['split']=arr.get('nbsplit',{}).get(item['name'])
# rings
AR={k:shape(v) for k,v in json.load(open('arr.json')).items()}
rings=[]
for rid,lab,nm in [('r1','Ring 1','The center'),('r2','Ring 2','The inner ring'),('r3','Ring 3','The outer ring')]:
    mem=[a for a in d['arr'] if a['ring']==rid]
    g=unary_union([AR[a['id']].buffer(3e-5,join_style=2) for a in mem]).buffer(-3e-5,join_style=2)
    big=max(getattr(g,'geoms',[g]),key=lambda p:p.area); c=polylabel(tp(big),tolerance=0.5)
    rings.append({'id':rid,'label':lab,'name':nm,'members':[a['id'] for a in mem],'d':poly_d(g,0.25),'lx':round(c.x,1),'ly':round(c.y,1),
      'sqmi':round(sum(a['mi2'] for a in mem),2),'km2':round(sum(a['km2'] for a in mem),1),'pop':sum(a['pop'] for a in mem)})
d['rings']=rings
d.pop('splits',None)
json.dump(d,open('mapdata.json','w'),separators=(',',':'))
print('rings',[(r['label'],r['sqmi'],r['pop']) for r in rings])
