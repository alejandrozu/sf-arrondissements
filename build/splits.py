import json
from shapely.geometry import shape
from geo import proj
A={k:shape(v) for k,v in json.load(open('arr.json')).items()}
NUM={'northbeach':1,'downtown':2,'soma':3,'marina':4,'westernaddition':5,'castro':6,'mission':7,'missionbay':8,'hills':9,'presidio':10,'richmond':11,'sunset':12,'parkside':13,'lakemerced':14,'excelsior':15,'bayview':16,'ggp':'GGP'}
def report(name,feats,key):
    print('=====',name)
    for f in feats:
        n=f['properties'].get(key); 
        if not f.get('geometry'): continue
        g=shape(f['geometry']).buffer(0); tot=proj(g).area
        if tot<1: continue
        parts=sorted(((proj(A[k].intersection(g)).area,k) for k in A if A[k].intersects(g)),reverse=True)
        parts=[(a,k) for a,k in parts if a/tot>0.03 and a>15000]
        if len(parts)>1:
            print(f"{n:38s}", ' | '.join(f"{NUM[k]}: {a/tot*100:.0f}% ({a/2.59e6:.2f} sq mi)" for a,k in parts))
for fn,key,nm in [('find_nbhd.geojson','name','SF Find'),('ds_realtor.geojson','nbrhood','Realtor'),('analysis_nbhd.geojson','nhood','Analysis'),('ds_c28a-f6gs.geojson','community_benefit_district','CBD'),('ds_5xmc-5bjj.geojson','district_name','Cultural')]:
    report(nm,json.load(open(fn))['features'],key)
