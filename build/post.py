import json,collections
d=json.load(open('mapdata.json'))
B={
'northbeach':['Broadway','Van Ness Ave','The Bay'],
'downtown':['Market St','Van Ness Ave','Broadway','The Bay','Steuart St','Don Chee Way'],
'soma':['Market St','Steuart St','Don Chee Way','The Bay','Townsend St','Division St','13th St','South Van Ness Ave'],
'marina':['Van Ness Ave','Geary Blvd','Presidio Ave','Lyon St','Presidio boundary','The Bay'],
'westernaddition':['Van Ness Ave','Geary Blvd','Masonic Ave','Fulton St','Stanyan St','Clarendon Ave','Twin Peaks Blvd','Clayton St','Market St','Castro St','Duboce Ave'],
'castro':['Duboce Ave','Market St','Dolores St','Cesar Chavez St','Guerrero St','San Jose Ave','Bosworth St','Elk St','Diamond Heights Blvd','Portola Dr','Castro St'],
'mission':['Market St','South Van Ness Ave','13th St','Division St','Potrero Ave','Cesar Chavez St','US-101','I-280','San Jose Ave','Guerrero St','Dolores St'],
'missionbay':['Division St','Townsend St','The Bay','Islais Creek','Cesar Chavez St','Potrero Ave'],
'hills':['Clayton St','Twin Peaks Blvd','Clarendon Ave','Stanyan St','Frederick St','Arguello Blvd','Irving St','3rd Ave','Parnassus Ave','Kirkham St','6th Ave','7th Ave','Laguna Honda Blvd','Dewey Blvd','Claremont Blvd','Portola Dr','Monterey Blvd','Bosworth St','Elk St','Diamond Heights Blvd','Market St'],
'presidio':['Presidio boundary','Pacific Ave','West Pacific Ave','Golden Gate','Pacific Ocean','The Bay'],
'richmond':['Fulton St','Masonic Ave','Presidio Ave','Lyon St','Pacific Ave','Presidio boundary','Pacific Ocean'],
'sunset':['Lincoln Way','Arguello Blvd','Irving St','3rd Ave','Parnassus Ave','Kirkham St','6th Ave','7th Ave','Laguna Honda Blvd','Dewey Blvd','Taraval St','14th Ave','Rivera St','15th Ave','Ortega St','Pacific Ocean'],
'parkside':['Ortega St','15th Ave','Rivera St','14th Ave','Taraval St','Claremont Blvd','Portola Dr','Sloat Blvd','Pacific Ocean'],
'lakemerced':['Sloat Blvd','Junipero Serra Blvd','Monterey Blvd','I-280','County line','Pacific Ocean'],
'excelsior':['I-280','US-101','County line'],
'bayview':['Cesar Chavez St','Islais Creek','US-101','County line','The Bay'],
}
C={'northbeach':1,'downtown':0,'soma':2,'marina':3,'westernaddition':4,'castro':5,'mission':1,'missionbay':4}
nei={a['id']:set(a['neigh'])-{'ggp'} for a in d['arr']}
cnt=collections.Counter(C.values())
for a in sorted(d['arr'],key=lambda a:a['n']):
    a['neigh']=sorted(nei[a['id']]); a['bounds']=B[a['id']]
    if a['id'] not in C:
        used={C[j] for j in nei[a['id']] if j in C}
        C[a['id']]=min((c for c in range(6) if c not in used),key=lambda c:(cnt[c],c)); cnt[C[a['id']]]+=1
    a['c']=C[a['id']]
    if a['id']=='castro' and 'Glen Park (village)' not in a['nb']: a['nb']=sorted(a['nb']+['Glen Park (village)'])
    if a['id']=='hills': a['nb']=sorted(set(['Glen Canyon' if x=='Glen Park' else x for x in a['nb']]+['Twin Peaks','Forest Hill Extension']))
    print(a['n'],a['name'],a['mi2'],a.get('pop'),a['c'])
json.dump(d,open('mapdata.json','w'),separators=(',',':'))
