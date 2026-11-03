import json,glob,collections,statistics as st,re,math
TD='/root/.claude/projects/-home-claude/2cc0b143-8bcb-52c0-8b96-02b78da6f48e/tool-results/'
NM={};PRO={}
for f in ['1793699062180','1793699073344','1793699077906']:
    t=open(glob.glob(TD+'*'+f+'.txt')[0]).read()
    for r in json.loads(t[t.index('{'):])['data']:
        i=str(r['zb_ods_area_danji.danji_id']).split('.')[0];NM[i]=r['zb_ods_area_danji.danji_name'];PRO[i]=r['zb_ods_area_danji.is_pro_entry']
M=json.load(open('m2b.json'));U=M['U']
H=set(str(r['id']) for r in json.load(open('../top518.json')))
def grp(v):
    r=v['reg'];return '서울' if r.startswith('서울') else '경기' if r.startswith('경기') else r
def yr(cd):
    m=re.match(r'(\d{4})년(\d{2})월',cd or '');return f"{m[1]}.{m[2]}" if m else '-'
bad=lambda i:'테스트' in (NM.get(i) or '')
c=[(i,v) for i,v in U.items() if v['cov']<0.5 and v['view']>=100 and not bad(i)]
c.sort(key=lambda x:-x[1]['gap'])
B=c[:500]
O3=[r for r in json.load(open('o3_rows.json')) if not bad(r['id'])][:500]
O3ids=set(r['id'] for r in O3);Bids=set(i for i,v in B)
def note(v):
    return '입주 전' if v['age']=='new' else ''
b2=[[k+1,v['l1'],v['l2'] or '',int(i),NM.get(i,''),int(v['hh']),yr(v['cd']),PRO.get(i,''),int(v['lst']),round(v['need']),round(v['gap']),int(v['view']),note(v)] for k,(i,v) in enumerate(B)]
o3=[]
for k,r in enumerate(O3):
    v=U[r['id']];o3.append([k+1,v['l1'],v['l2'] or '',int(r['id']),NM.get(r['id'],''),int(v['hh']),PRO.get(r['id'],''),int(v['lst']),int(v['view']),int(r['top3']),int(r['top1']),r['noff'],r['pro']])
def summ(items):
    g=collections.Counter(grp(U[i]) for i in items);return g
S={'b2':{'n':len(B),'reg':summ(Bids),'ovH':len(Bids&H),'ovO':len(Bids&O3ids),'lst0':sum(1 for i,v in B if v['lst']==0),'lst12':sum(1 for i,v in B if 1<=v['lst']<=2),'lst3':sum(1 for i,v in B if v['lst']>=3),'medhh':st.median(v['hh'] for i,v in B),'medneed':st.median(v['need'] for i,v in B),'medlst':st.median(v['lst'] for i,v in B),'pro':sum(PRO.get(i)=='Y' for i in Bids),'r2':M['r2'],'coef':M['coef'],'ref':M['ref'],'cand':len(c)},
   'o3':{'n':len(O3),'reg':summ(O3ids),'ovH':len(O3ids&H),'ovB':len(O3ids&Bids),'medtop3':st.median(r['top3'] for r in O3),'medtop1':st.median(r['top1'] for r in O3),'mednoff':st.median(r['noff'] for r in O3),'pro':sum(PRO.get(i)=='Y' for i in O3ids),'univ':len(json.load(open('o3_rows.json'))),'withpro':sum(1 for r in O3 if r['pro']>0),'sumtop3':sum(r['top3'] for r in O3),'medview':st.median(U[r['id']]['view'] for r in O3)}}
for k in S: S[k]['reg']=dict(S[k]['reg'])
print(json.dumps(S,ensure_ascii=False,indent=0)[:3000])
print(b2[:8]);print(o3[:8])
json.dump({'b2':b2,'o3':o3,'S':S},open('opt_out.json','w'),ensure_ascii=False)
