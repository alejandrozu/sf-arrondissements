import json, itertools
d=json.load(open('mapdata.json'))
N={a['id']:set(a['neigh']) for a in d['arr']}
H={'red':0,'orange':30,'yellow':60,'chartreuse':90,'green':120,'jade':150,'cyan':180,'azure':210,'blue':240,'purple':270,'magenta':300,'pink':330,'brown':30,'viridian':150,'aubergine':270,'black':None}
def clash(a,b):
    if H[a] is None or H[b] is None: return False
    dd=abs(H[a]-H[b])%360; dd=min(dd,360-dd); return dd<=30
C={
'northbeach':{'green':3,'chartreuse':2,'red':1},
'downtown':{'red':3,'yellow':1},
'soma':{'black':3,'aubergine':1},
'marina':{'blue':3,'azure':2},
'westernaddition':{'purple':3,'aubergine':2,'magenta':1},
'castro':{'pink':3,'magenta':1},
'mission':{'brown':3,'yellow':2,'orange':2,'magenta':1},
'missionbay':{'azure':2,'orange':2,'brown':2,'cyan':1,'blue':1},
'hills':{'viridian':3,'green':2},
'presidio':{'orange':3,'viridian':1,'red':1},
'richmond':{'cyan':2,'jade':2,'azure':1,'yellow':1},
'sunset':{'yellow':3,'magenta':2,'orange':2,'brown':1},
'parkside':{'green':3,'chartreuse':2,'jade':2},
'lakemerced':{'azure':3,'cyan':3,'jade':2,'viridian':1},
'excelsior':{'aubergine':3,'purple':1,'chartreuse':1,'jade':1},
'bayview':{'red':2,'yellow':2,'jade':1,'cyan':1,'magenta':1},
}
ids=sorted(C,key=lambda k:len(C[k]))
best=[]
def rec(i,asg,used,score):
    if i==len(ids):
        best.append((score,dict(asg))); return
    k=ids[i]
    for col,s in C[k].items():
        if col in used: continue
        if any(n in asg and clash(col,asg[n]) for n in N[k]): continue
        asg[k]=col; used.add(col); rec(i+1,asg,used,score+s); del asg[k]; used.discard(col)
rec(0,{},set(),0)
best.sort(key=lambda x:-x[0]); print(len(best))
for s,a in best[:6]: print(s,a)
