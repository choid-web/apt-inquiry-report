import json,re,math,collections,statistics as st
import numpy as np
D=json.load(open('base.json'))
SA={'강남구','서초구','용산구','송파구'};SB={'성동구','마포구','광진구','양천구','영등포구','동작구','종로구','강동구','중구'}
GA={'과천시','성남시 분당구'}
GB={'성남시 수정구','하남시','용인시 수지구','광명시','성남시 중원구','수원시 영통구','안양시 동안구','의왕시','구리시','안양시 만안구','용인시 기흥구','수원시 팔달구','고양시 덕양구','고양시 일산동구','부천시 원미구','수원시 장안구','부천시 소사구','남양주시','군포시'}
MET={'부산광역시','대구광역시','대전광역시','울산광역시','세종특별자치시'}
def reg(v):
    l1,l2=v['l1'],v['l2'] or ''
    if l1=='서울특별시': return '서울A' if l2 in SA else '서울B' if l2 in SB else '서울C'
    if l1=='경기도':
        if l2 in GA: return '경기A'
        if l2 in GB or l2.startswith('화성시'): return '경기B'
        return '경기C'
    if l1=='인천광역시': return '인천'
    if l1 in MET: return '5대광역시+세종'
    if l1=='전남광주통합특별시' and l2 in ('동구','서구','남구','북구','광산구'): return '5대광역시+세종'
    return '기타'
def ym(cd):
    m=re.match(r'(\d{4})년(\d{2})월',cd or '');return int(m[1])*12+int(m[2])-1 if m else None
NOW=2026*12+10  # 2026-11
W0,W1=2026*12+10,2027*12+4
def age_b(v):
    t=ym(v['cd'])
    if t is None: return 'unk'
    if t>NOW: return 'new'  # 입주 전
    a=(NOW-t)/12
    return '0-2' if a<3 else '3-5' if a<6 else '6-10' if a<11 else '11-20' if a<21 else '21-30' if a<31 else '30+'
U={}
for i,v in D.items():
    if v['rent']: continue
    t=ym(v['cd'])
    if v['occ'] in('분양','입주예정') or (t is not None and t>NOW):
        if t is None or not (W0<=t<=W1): continue
    v['reg']=reg(v);v['age']=age_b(v);U[i]=v
print('universe',len(U))
REGS=sorted(set(v['reg'] for v in U.values()));AGES=['0-2','3-5','6-10','11-20','21-30','30+','new','unk']
def X(v):
    x=[1.0,math.log(v['hh'])]
    x+=[1.0 if v['reg']==r else 0.0 for r in REGS[1:]]
    x+=[1.0 if v['age']==a else 0.0 for a in AGES[1:]]
    return x
fit=[v for v in U.values() if v['view']>0]
A=np.array([X(v) for v in fit]);y=np.array([math.log(v['view']) for v in fit])
b,*_=np.linalg.lstsq(A,y,rcond=None);pred=A@b
r2=1-((y-pred)**2).sum()/((y-y.mean())**2).sum()
print('R2',round(r2,3),'n',len(fit))
names=['const','log세대수']+['reg_'+r for r in REGS[1:]]+['age_'+a for a in AGES[1:]]
for n,c in zip(names,b): print(n,round(c,3))
resid=y-pred;smear=np.mean(np.exp(resid))
for v in U.values(): v['ev']=math.exp(np.array(X(v))@b)*smear
# reference ratio by region: listings per 1000 expected viewers among covered danjis
ref={}
for r in REGS:
    s=[v['lst']/v['ev']*1000 for v in U.values() if v['reg']==r and v['lst']>=3]
    ref[r]=st.median(s);print('ref',r,len(s),round(ref[r],2))
for v in U.values():
    v['need']=v['ev']*ref[v['reg']]/1000;v['gap']=v['need']-v['lst'];v['cov']=v['lst']/v['need'] if v['need']>0 else 9
json.dump({'U':U,'ref':ref,'r2':r2,'coef':dict(zip(names,b.tolist()))},open('m2b.json','w'),ensure_ascii=False)
cand=[(i,v) for i,v in U.items() if v['cov']<0.5]
cand.sort(key=lambda x:-x[1]['gap'])
print('cand',len(cand))
for i,v in cand[:25]: print(i,v['reg'],v['l2'],int(v['hh']),v['age'],v['lst'],round(v['need'],1),int(v['ev']),int(v['view']))
top=cand[:500]
print('lst dist',collections.Counter(min(int(v['lst']),10) for i,v in top))
print('reg',collections.Counter(v['reg'] for i,v in top))
H=set(str(r['id']) for r in json.load(open('../top518.json')))
print('overlap with H',sum(1 for i,v in top if i in H))
