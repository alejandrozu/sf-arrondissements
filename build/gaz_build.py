exec(open('gaz.py').read())
import collections
Xs=X
# ---------- custom: SoMa partition
soma=A['soma']
i80=[(-122.3835,37.7905)]+along('I-80 WESTBOUND',(-122.3895,37.7870),(-122.40682,37.77343))+[(-122.4109,37.7694)]
lines=[S('02ND ST',Xs('02ND ST','MARKET ST'),Xs('02ND ST','TOWNSEND ST')),
       S('04TH ST',Xs('04TH ST','I-80 WESTBOUND'),Xs('04TH ST','TOWNSEND ST')),
       S('05TH ST',Xs('05TH ST','MARKET ST'),Xs('05TH ST','I-80 WESTBOUND')),
       S('07TH ST',Xs('07TH ST','MARKET ST'),Xs('07TH ST','I-80 WESTBOUND')),
       S('11TH ST',Xs('11TH ST','MARKET ST'),Xs('11TH ST','DIVISION ST')),
       S('HOWARD ST',Xs('HOWARD ST','07TH ST'),Xs('HOWARD ST','11TH ST')),
       S('BRANNAN ST',Xs('BRANNAN ST','02ND ST'),Xs('BRANNAN ST','04TH ST')), i80]
seeds={'East Cut':[Xs('FREMONT ST','HOWARD ST'),Xs('BEALE ST','FOLSOM ST')],
 'South Beach':[(-122.3905,37.7825),(-122.3915,37.7815)],
 'Yerba Buena':[Xs('03RD ST','HOWARD ST'),Xs('04TH ST','MISSION ST')],
 'China Basin':[mid(Xs('03RD ST','TOWNSEND ST'),Xs('03RD ST','BRANNAN ST')),mid(Xs('02ND ST','BRANNAN ST'),Xs('03RD ST','BRYANT ST'))],
 'Central SoMa':[mid(Xs('05TH ST','HOWARD ST'),Xs('06TH ST','FOLSOM ST')),Xs('06TH ST','MISSION ST'),mid(Xs('06TH ST','HOWARD ST'),Xs('07TH ST','FOLSOM ST'))],
 'Inner SoMa':[mid(Xs('08TH ST','MARKET ST'),Xs('08TH ST','HOWARD ST')),mid(Xs('09TH ST','MARKET ST'),Xs('09TH ST','HOWARD ST'))],
 'Leather District':[Xs('09TH ST','FOLSOM ST')],
 'SoMa Triangle':[mid(Xs('12TH ST','FOLSOM ST'),Xs('11TH ST','HOWARD ST'))],
 'South SoMa':[Xs('06TH ST','BRANNAN ST'),Xs('05TH ST','BRANNAN ST'),Xs('07TH ST','TOWNSEND ST'),Xs('08TH ST','BRANNAN ST')]}
SOMA=subdivide(soma,lines,seeds)
# ---------- Oracle Park (8th, between Townsend and Mission Creek)
creek=Polygon(json.load(open('creek.json'))).buffer(0)
xs=[creek.bounds[0]+i*(creek.bounds[2]-creek.bounds[0])/30 for i in range(31)]
cl=[]
for x in xs:
    v=creek.intersection(LineString([(x,37.76),(x,37.79)]))
    if not v.is_empty: cl.append((x,(v.bounds[1]+v.bounds[3])/2))
tw=along('TOWNSEND ST',Xs('TOWNSEND ST','THE EMBARCADERO'),Xs('TOWNSEND ST','DIVISION ST'))
op=Polygon([(-122.3850,37.7835)]+tw+[(-122.4044,37.7697)]+cl+[(-122.3850,37.7790)]).buffer(0)
CUSTOM=[]  # (name, geom, arrkey or None)
CUSTOM.append(('Rincon Hill',FIND['Rincon Hill'],'soma'))
for n,g in SOMA.items(): CUSTOM.append((n,g,'soma'))
CUSTOM.append(('Corbett Heights',FIND['Upper Market'],'hills'))
CUSTOM.append(('Jackson Square',loop(S('BROADWAY',Xs('COLUMBUS AVE','BROADWAY'),Xs('SANSOME ST','BROADWAY')),S('SANSOME ST',Xs('SANSOME ST','BROADWAY'),Xs('SANSOME ST','WASHINGTON ST')),S('WASHINGTON ST',Xs('SANSOME ST','WASHINGTON ST'),Xs('COLUMBUS AVE','WASHINGTON ST')),S('COLUMBUS AVE',Xs('COLUMBUS AVE','WASHINGTON ST'),Xs('COLUMBUS AVE','BROADWAY'))),'downtown'))
gj=Xs('SAN JOSE AVE','GUERRERO ST')
CUSTOM.append(('La Lengua',loop(S('CESAR CHAVEZ ST',Xs('CESAR CHAVEZ ST','GUERRERO ST'),Xs('MISSION ST','CESAR CHAVEZ ST')),S('MISSION ST',Xs('MISSION ST','CESAR CHAVEZ ST'),Xs('30TH ST','MISSION ST')),S('30TH ST',Xs('30TH ST','MISSION ST'),Xs('30TH ST','SAN JOSE AVE')),S('SAN JOSE AVE',Xs('30TH ST','SAN JOSE AVE'),gj),S('GUERRERO ST',gj,Xs('CESAR CHAVEZ ST','GUERRERO ST'))),'mission'))
# west of Larkin -> Lower Polk ; east of Drumm -> Embarcadero ; Little Italy ; Russian Hill split
lk=along('LARKIN ST',(-122.416291702,37.777493844),(-122.422196208,37.806436365))
westL=Polygon(lk+[(-122.45,37.81),(-122.45,37.77)]).buffer(0)
CUSTOM.append(('Lower Polk',unary_union([FIND['Tenderloin'],FIND['Lower Nob Hill']]).intersection(westL),'downtown'))
dr=along('DRUMM ST',(-122.396302004,37.79325635),(-122.397137098,37.797243627))
eastD=Polygon([(-122.3962,37.7925)]+dr+[(-122.3975,37.7990),(-122.38,37.80),(-122.38,37.79)]).buffer(0)
CUSTOM.append(('Embarcadero',unary_union([FIND['Financial District'],FIND['Northern Waterfront']]).intersection(eastD).difference(FIND['Northern Waterfront'].difference(FIND['Financial District'])),'downtown'))
fb=along('GREENWICH ST',(-122.447158297, 37.797515005),(-122.401582552, 37.803287187))
southF=Polygon(fb+[(-122.39,37.8025),(-122.39,37.79),(-122.45,37.79)]).buffer(0)
CUSTOM.append(('Little Italy',FIND['North Beach'].intersection(southF),'northbeach'))
un=along('UNION ST',Xs('UNION ST','VAN NESS AVE'),Xs('UNION ST','COLUMBUS AVE'))
southU=Polygon([(-122.45,un[0][1])]+un+[(-122.39,un[-1][1]),(-122.39,37.79),(-122.45,37.79)]).buffer(0)
def line_ext(nm):
    pts=[c for s_ in json.load(open('streets.json')) if s_['streetname']==nm for c in s_['line']['coordinates']]
    return min(pts,key=lambda p:p[1]),max(pts,key=lambda p:p[1])
def side_poly(nm,p=None,q=None,side='west',far=0.08):
    if p is None: p,q=line_ext(nm)
    c=along(nm,p,q); c=[(c[0][0],c[0][1]-0.03)]+c+[(c[-1][0],c[-1][1]+0.03)]
    dx=-far if side=='west' else far
    return Polygon(c+[(c[-1][0]+dx,c[-1][1]),(c[0][0]+dx,c[0][1])]).buffer(0)
def ns_poly(nm,side='south',far=0.08,lo=-123,hi=-122):
    pts=sorted(c for s_ in json.load(open('streets.json')) if s_['streetname']==nm for c in s_['line']['coordinates'] if lo<=c[0]<=hi)
    import collections as _c
    b=_c.defaultdict(list)
    for x,y in pts: b[round(x,3)].append(y)
    c=[(x,sum(v)/len(v)) for x,v in sorted(b.items())]
    c=[(c[0][0]-0.03,c[0][1])]+c+[(c[-1][0]+0.03,c[-1][1])]
    dy=-far if side=='south' else far
    return Polygon(c+[(c[-1][0],c[-1][1]+dy),(c[0][0],c[0][1]+dy)]).buffer(0)
def side2(nm,side='east',lo=-90,hi=90,far=0.08,ext=0.03):
    pts=[c for s_ in json.load(open('streets.json')) if s_['streetname']==nm for c in s_['line']['coordinates'] if lo<=c[1]<=hi]
    import collections as _c
    b=_c.defaultdict(list)
    for x,y in pts: b[round(y,3)].append(x)
    c=[(sum(v)/len(v),y) for y,v in sorted(b.items())]
    # extend along end directions
    def e(a,bb):
        import math as _m
        dx,dy=bb[0]-a[0],bb[1]-a[1]; n=_m.hypot(dx,dy) or 1; return (bb[0]+dx/n*ext,bb[1]+dy/n*ext)
    c=[e(c[1],c[0])]+c+[e(c[-2],c[-1])]
    dx=far if side=='east' else -far
    return Polygon(c+[(c[-1][0]+dx,c[-1][1]),(c[0][0]+dx,c[0][1])]).buffer(0)
eastLv=side_poly('LEAVENWORTH ST',side='east')
RH=FIND['Russian Hill']
CUSTOM.append(('Russian Hill',RH.intersection(unary_union([southU,eastLv])),'northbeach'))
CUSTOM.append(('Lombard Crest Russian Hill',RH.difference(unary_union([southU,eastLv])),'northbeach'))
westFill=side_poly('FILLMORE ST',side='west')
westScott=side_poly('SCOTT ST',side='west')
CUSTOM.append(('Marina Fine Arts',FIND['Marina'].intersection(westFill).intersection(westScott),'marina'))
CUSTOM.append(('Spanish Marina',FIND['Marina'].intersection(westFill).difference(westScott),'marina'))
CUSTOM.append(('East Marina',FIND['Marina'].difference(westFill),'marina'))
CUSTOM.append(('Cannon Hill Pacific Heights',FIND['Pacific Heights'].intersection(westFill),'marina'))
CUSTOM.append(('Lafayette Pacific Heights',FIND['Pacific Heights'].difference(westFill),'marina'))
westDiv=side_poly('DIVISADERO ST',(-122.4372,37.7700),(-122.4425,37.8000),side='west')
tk=along('TURK BLVD',(-122.46,37.778),(-122.437,37.781)); southTurk=Polygon(tk+[(-122.43,37.7795),(-122.43,37.76),(-122.46,37.76)]).buffer(0)
fw=FIND['Western Addition'].intersection(westDiv)
northOak=ns_poly('OAK ST',side='north',lo=-122.455,hi=-122.436)
CUSTOM.append(('NoPa',A['westernaddition'].intersection(westDiv).intersection(northOak).difference(FIND['Anza Vista']),'westernaddition'))
southClip=ns_poly('CLIPPER ST',side='south',lo=-122.445,hi=-122.424)
eastChurch=side_poly('CHURCH ST',side='east')
south24w=ns_poly('24TH ST',side='south',lo=-122.435,hi=-122.420)
CUSTOM.append(("Horner's Hill",unary_union([FIND['Noe Valley'].intersection(southClip),FIND['Dolores Heights'].intersection(south24w)]).intersection(eastChurch),'castro'))
CUSTOM.append(('Duncan Hill',FIND['Noe Valley'].intersection(southClip).difference(eastChurch),'castro'))
CUSTOM.append(('Downtown Noe Valley',FIND['Noe Valley'].difference(southClip),'castro'))
# ---- 8th: Oracle Park / Mission Creek / Potrero
west3=side_poly('03RD ST',Xs('03RD ST','24TH ST'),(-122.3935,37.7810),side='west')
ln=along('MISSION BAY DR',(-122.398627777,37.769491055),(-122.3962,37.77036))+along('LONG BRIDGE ST',(-122.39423,37.77037),(-122.39143,37.77347))
ln=[(-122.4060,37.7660)]+ln+[(-122.3914,37.7800)]
nwMB=Polygon(ln+[(-122.42,37.7800),(-122.42,37.7660)]).buffer(0)
OPfull=op.difference(FIND['Showplace Square'])
CUSTOM.append(('Oracle Park',op.difference(FIND['Showplace Square']).difference(west3),'missionbay'))
CUSTOM.append(('Mission Creek',unary_union([OPfull.intersection(west3),FIND['Mission Bay'].intersection(nwMB)]),'missionbay'))
north24=ns_poly('24TH ST',side='north',lo=-122.405,hi=-122.380)
north20=ns_poly('20TH ST',side='north',lo=-122.426,hi=-122.405)
south23=ns_poly('23RD ST',side='south',lo=-122.424,hi=-122.405)
westMis=side_poly('MISSION ST',Xs('23RD ST','MISSION ST'),(-122.4195,37.7700),side='west')
eastFol=side_poly('FOLSOM ST',Xs('20TH ST','FOLSOM ST'),(-122.4150,37.7700),side='east')
M=FIND['Mission']
CUSTOM.append(('Calle 24',M.intersection(south23),'mission'))
CUSTOM.append(('Food Processing District',M.intersection(north20).intersection(eastFol),'mission'))
CUSTOM.append(('Valencia Corridor',M.intersection(north20).intersection(westMis),'mission'))
CUSTOM.append(('South Van Ness',M.intersection(north20).difference(eastFol).difference(westMis),'mission'))
CUSTOM.append(('Central Mission',M.difference(north20).difference(south23),'mission'))
southCort=ns_poly('CORTLAND AVE',side='south',lo=-122.423,hi=-122.406)
CUSTOM.append(('Bernal Triangle',FIND['Bernal Heights'].intersection(southCort),'mission'))
CUSTOM.append(('Amador Point',FIND['Central Waterfront'].intersection(side2('ILLINOIS ST','east')),'bayview'))
southPalou=ns_poly('PALOU AVE',side='south')
eastMen=side2('MENDELL ST','east')
BV=FIND['Bayview']
CUSTOM.append(('Inner Bayview',BV.intersection(southPalou),'bayview'))
CUSTOM.append(('Bayview Hills',BV.difference(southPalou).intersection(eastMen),'bayview'))
CUSTOM.append(('Bayview Valley',BV.difference(southPalou).difference(eastMen),'bayview'))
CUSTOM.append(('Potrero Point',FIND['Central Waterfront'].difference(west3).intersection(north24),'missionbay'))
tl=[(-122.4200,37.7544)]+along('23RD ST',Xs('23RD ST','POTRERO AVE'),Xs('23RD ST','MISSOURI ST'))+[Xs('MISSOURI ST','SIERRA ST'),Xs('SIERRA ST','TEXAS ST')]+along('22ND ST',Xs('22ND ST','TEXAS ST'),Xs('22ND ST','PENNSYLVANIA AVE'))+[(-122.3800,37.7570)]
southT=Polygon(tl+[(-122.3800,37.70),(-122.4200,37.70)]).buffer(0)
CUSTOM.append(('Potrero Terrace',FIND['Potrero Hill'].intersection(southT),'missionbay'))
northMar=ns_poly('MARIPOSA ST',side='north',lo=-122.408,hi=-122.388); north19=ns_poly('19TH ST',side='north',lo=-122.406,hi=-122.389)
connX=Xs('CONNECTICUT ST','18TH ST'); dhX=Xs('DE HARO ST','19TH ST')
band=box(dhX[0],37.755,connX[0],37.770)
CUSTOM.append(('Potrero Valley',FIND['Potrero Hill'].intersection(unary_union([northMar,north19.intersection(band)])),'missionbay'))
LAKE=shape(json.load(open('nm_Lake_Merced__San_Francisco.json'))[0]['geojson']).buffer(0)
CUSTOM.append(('Fort Funston',osmway(404851503),'lakemerced'))
CUSTOM.append(('Lake Merced',unary_union([LAKE,osmway(404847043),osmway(16753068)]),'lakemerced'))
FINDPRI=['Sutro Heights','Presidio Terrace','Lincoln Park / Ft. Miley','Seacliff','Lake Street','Laurel Heights / Jordan Park','Lone Mountain','Presidio Heights']
REALSEL={'richmond':['Central Richmond','Inner Richmond','Outer Richmond'],
 'sunset':['Inner Sunset','Central Sunset','Outer Sunset','Golden Gate Heights','Forest Hill','Inner Parkside','Parkside','Outer Parkside','Pine Lake Park','West Portal'],
 'parkside':['Inner Sunset','Central Sunset','Outer Sunset','Golden Gate Heights','Forest Hill','Inner Parkside','Parkside','Outer Parkside','Pine Lake Park','West Portal'],
 'hills':['Twin Peaks','Forest Hills Extension'],'lakemerced':['Lakeside','Ingleside Heights'],'bayview':['Bayview Heights']}
RENAME={('Civic Center',5):'Performing Arts District',('Duboce Triangle',5):'Lower Haight',('South Beach',8):'Oracle Park',
 ('Mission Dolores',7):'Valencia Corridor',('Upper Market',9):'Corbett Heights',('Dolores Heights',7):'Liberty Hill',
 ('Central Waterfront',16):'Islais Creek',('Diamond Heights',6):'Gold Mine Hill',('Northern Waterfront',2):'Golden Gateway',
 ('Sunnyside',9):'North Sunnyside',('Sunnyside',14):'South Sunnyside',('Glen Park',9):'Glen Canyon',
 ('Aquatic Park / Ft. Mason',1):'Aquatic Park',('Aquatic Park / Ft. Mason',4):'Fort Mason',('Cathedral Hill',4):'North Cathedral Hill',
 ('Polk Gulch',1):'Upper Polk',('North Beach',2):'Jackson Square',('Eureka Valley',5):'Corona Heights',('Japantown',5):'Fillmore',('South of Market',7):'Mission Triangle'}
GLOBAL={'Western Addition':'Fillmore','Panhandle':'NoPa','Downtown / Union Square':'Union Square','Lincoln Park / Ft. Miley':'Lincoln Park & Lands End',
 'Forest Hills Extension':'Forest Hill Extension','Presidio National Park':'Presidio','Candlestick Point SRA':'Candlestick Point','Aquatic Park / Ft. Mason':'Fort Mason',
 'Laurel Heights / Jordan Park':'Laurel Heights','Fishermans Wharf':"Fisherman's Wharf",'St. Marys Park':"St. Mary's Park",'Mt. Davidson Manor':'Mount Davidson Manor','Lakeshore':'Lakeshore & SF State'}
MINMI=0.02
OUT=[]   # dicts
for k,arr in A.items():
    n=NUM[k]; rem=arr; pieces=[]
    layers=[(nm,g,'custom') for nm,g,ak in CUSTOM if ak==k]
    if k=='richmond': layers+=[(nm,FIND[nm],'find') for nm in FINDPRI]
    layers+=[(nm,REAL[nm],'realtor') for nm in REALSEL.get(k,[])]
    layers+=[(nm,g,'find') for nm,g in FIND.items()]
    for nm,g,src in layers:
        p=g.intersection(rem)
        p=unary_union([q for q in getattr(p,'geoms',[p]) if q.geom_type=='Polygon'])
        if p.is_empty or sqmi(p)<0.0005: continue
        pieces.append({'orig':nm,'src':src,'g':p}); rem=rem.difference(p)
    # name
    for pc in pieces:
        nm=pc['orig']
        pc['name']=RENAME.get((nm,n)) or GLOBAL.get(nm) or nm
    # merge minor pieces (not custom) into neighbour
    def full(nm,src):
        return FIND.get(nm) if src=='find' else REAL.get(nm) if src=='realtor' else None
    changed=True
    while changed:
        changed=False
        for pc in pieces:
            if pc.get('dead') or pc['src']=='custom': continue
            fg=full(pc['orig'],pc['src']); share=sqmi(pc['g'])/max(sqmi(fg.intersection(unary_union(list(A.values())))),1e-9)
            if (pc['orig'],n) in RENAME: continue
            if (sqmi(pc['g'])<0.03 and share<0.5) or (share<0.15 and sqmi(pc['g'])<0.08) or sqmi(pc['g'])<0.006:
                best=None
                for q in pieces:
                    if q is pc or q.get('dead'): continue
                    l=pc['g'].buffer(2e-5).intersection(q['g']).area
                    if l>0 and (best is None or l>best[0]): best=(l,q)
                if best:
                    best[1]['g']=unary_union([best[1]['g'],pc['g']]); pc['dead']=True; changed=True
    # explode into parts; small parts + leftover reassigned to neighbouring main part
    live=[pc for pc in pieces if not pc.get('dead')]
    parts=[]
    for pc in live:
        ps=sorted([p for p in getattr(pc['g'],'geoms',[pc['g']]) if p.geom_type=='Polygon'],key=lambda p:-p.area)
        for i,p in enumerate(ps): parts.append({'pc':pc,'g':p,'main':i==0 or sqmi(p)>0.01})
    if not rem.is_empty:
        for p in getattr(rem,'geoms',[rem]):
            if p.geom_type=='Polygon' and p.area>0: parts.append({'pc':None,'g':p,'main':False})
    mains=[q for q in parts if q['main']]
    for q in parts:
        if q['main']: continue
        best=None
        for m in mains:
            l=q['g'].buffer(3e-5).intersection(m['g']).area
            if l>0 and (best is None or l>best[0]): best=(l,m)
        if best: best[1]['g']=unary_union([best[1]['g'],q['g']])
    for pc in live: pc['g']=unary_union([m['g'] for m in mains if m['pc'] is pc]).buffer(0)
    pieces=[pc for pc in live if not pc['g'].is_empty]
    # merge same names
    byname=collections.OrderedDict()
    for pc in pieces:
        if pc.get('dead'): continue
        byname.setdefault(pc['name'],[]).append(pc)
    for nm,pcs in byname.items():
        gg=unary_union([p['g'] for p in pcs]).buffer(0)
        gg=unary_union([p for p in getattr(gg,'geoms',[gg]) if p.geom_type=='Polygon' and sqmi(p)>=0.001]) or gg
        OUT.append({'arr':k,'n':n,'name':nm,'origs':sorted(set(p['orig'] for p in pcs)),'g':gg})
# ---------- split report (source polygons vs arrondissements)
report=[]
for src,coll in [('find',FIND),('realtor',{k:REAL[k] for v in REALSEL.values() for k in v})]:
    for og,fg in coll.items():
        sides=[]
        for k,arr in A.items():
            part=fg.intersection(arr)
            if part.is_empty: continue
            m=sqmi(part)
            names=collections.Counter()
            for o in OUT:
                if o['arr']==k:
                    ov=sqmi(o['g'].intersection(part))
                    if ov>0.004: names[o['name']]+=ov
            sides.append((NUM[k],m,[nm for nm,_ in names.most_common(3)]))
        tot=sum(x[1] for x in sides) or 1
        big=[x for x in sides if x[1]>=0.02 and x[1]/tot>=0.12]
        if len(big)>1 and not any(r['orig']==og for r in report):
            report.append({'orig':og,'src':src,'sides':[{'n':a,'sqmi':round(m,2),'pct':round(m/tot*100),'names':nm} for a,m,nm in sorted(big,key=lambda x:-x[1])]})
json.dump({'nb':[{'arr':o['arr'],'n':o['n'],'name':o['name'],'origs':o['origs'],'sqmi':round(sqmi(o['g']),3),'g':mapping(o['g'])} for o in OUT],'splits':report},open('gaz.json','w'))
for n in sorted(set(o['n'] for o in OUT)):
    print(n, ', '.join(f"{o['name']}({sqmi(o['g']):.2f})" for o in OUT if o['n']==n))
print('---- splits')
for r in report: print(r['orig'],' | '.join(f"{s['n']}:{s['pct']}% {s['sqmi']} {s['names']}" for s in r['sides']))
# ---------- floating micro-neighborhood labels (no boundaries)
FLOAT=[
 ('Little Saigon',mid(Xs('LARKIN ST','EDDY ST'),Xs('LARKIN ST','ELLIS ST'))),
 ('Theater District',Xs('MASON ST','GEARY ST')),
 ('Uptown Tenderloin',Xs('JONES ST','ELLIS ST')),
 ('Transgender District',Xs('TURK ST','TAYLOR ST')),
 ('French Quarter',Xs('KEARNY ST','BUSH ST')),
 ('Manilatown',Xs('KEARNY ST','JACKSON ST')),
 ('Barbary Coast',Xs('PACIFIC AVE','MONTGOMERY ST')),
 ('Mid-Market',mid(Xs('JONES ST','MARKET ST'),Xs('LEAVENWORTH ST','GOLDEN GATE AVE'))),
 ('Tendernob',Xs('LEAVENWORTH ST','BUSH ST')),
 ('SoMa Pilipinas',Xs('06TH ST','MINNA ST')),
 ('Transbay',Xs('01ST ST','MISSION ST')),
 ('Mint Plaza',Xs('05TH ST','MISSION ST')),
 ('South Park',mid(Xs('02ND ST','BRANNAN ST'),Xs('03RD ST','BRYANT ST'))),
 ('Upper Fillmore',Xs('FILLMORE ST','CLAY ST')),
 ('Billionaires\' Row',Xs('BROADWAY','BAKER ST')),
 ('Jazz District',Xs('FILLMORE ST','EDDY ST')),
 ('Upper Haight',mid(Xs('HAIGHT ST','STANYAN ST'),Xs('HAIGHT ST','MASONIC AVE'))),
 ('Greater Noe Valley',mid(Xs('CHURCH ST','30TH ST'),Xs('CHURCH ST','CLIPPER ST'))),
 ('Greater Mission',Xs('20TH ST','SOUTH VAN NESS AVE')),
 ('American Indian Cultural District',Xs('VALENCIA ST','16TH ST')),
 ('Washington Square',mid(Xs('POWELL ST','UNION ST'),Xs('FILBERT ST','STOCKTON ST'))),
]
FL=[]
for nm,p in FLOAT:
    k=next((k for k,g in A.items() if g.contains(Point(p))),None)
    FL.append({'name':nm,'lon':p[0],'lat':p[1],'arr':k}); print('float',nm,k)
json.dump(FL,open('floats.json','w'))
