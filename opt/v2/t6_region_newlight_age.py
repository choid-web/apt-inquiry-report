# 작업 6. 지역별 신규 LIGHT 매물의 단지 성격(준공 연차)
import json,collections,sys,os,re
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from common import *
HERE=os.path.dirname(os.path.abspath(__file__))
RAW={'lst0928':'1793793590536','subs0928':'1793793613751','subs1101':'1793793618800',
 'agent1101':['1793793644837','1793793845854','1793793854436','1793793863409','1793793940836','1793793949355','1793793958283','1793793969328'],
 'attr':['1793698669848','1793698679630','1793698755798','1793698766252']+json.loads(os.environ.get('ATTR_EXTRA','[]')),
 'loc':['1793698778567','1793698854635','1793698858119']+json.loads(os.environ.get('LOC_EXTRA','[]')),
 'name':['1793699062180','1793699073344','1793699077906']+json.loads(os.environ.get('NAME_EXTRA','[]')),
 'occ':'1793672184712'}
k='zbhg_daily_apart_subscription.'
s28={sid(r[k+'user_no']) for r in L(RAW['subs0928'])}
nl={sid(r[k+'user_no']) for r in L(RAW['subs1101']) if r[k+'apart_subs']=='light'}-s28
NL=collections.Counter()
for f in RAW['agent1101']:
    for r in L(f):
        d=sid(r['zbhg_ods_item.area_danji_id'])
        if d and sid(r['zbhg_ods_item.user_no']) in nl: NL[d]+=float(r['zb_daily_operating_item.open_item_cnt'] or 0)
l28={sid(r['zbhg_ods_item.area_danji_id']):float(r['zb_daily_operating_item.open_item_cnt'] or 0) for r in L(RAW['lst0928']) if r['zbhg_ods_item.area_danji_id'] is not None}
A={}
for f in RAW['attr']:
    for r in L(f): A[sid(r['zb_ods_area_danji.danji_id'])]={'hh':float(r['zb_ods_area_danji.total_households'] or 0),'cd':r['zb_ods_area_danji.completion_date']}
LOC={}
for f in RAW['loc']:
    for r in L(f): LOC[sid(r['zb_ods_area_danji.danji_id'])]=(r.get('zb_ods_area_danji.local1'),r.get('zb_ods_area_danji.local2'))
NM={}
for f in RAW['name']:
    for r in L(f): NM[sid(r['zb_ods_area_danji.danji_id'])]=r['zb_ods_area_danji.danji_name']
OCC={sid(r['zb_ods_area_danji.danji_id']):r['zb_ods_area_danji.occupancy_status'] for r in L(RAW['occ'])}
NOW=2026*12+10
AGES=['입주예정·분양','입주 2년 이내','3~5년','6~10년','11년 이상','준공 시점 미상']
def age(d):
    a=A.get(d);o=OCC.get(d)
    m=re.match(r'(\d{4})년(\d{2})월',(a or {}).get('cd') or '')
    if o in('분양','입주예정'): return AGES[0]
    if not m: return AGES[5]
    t=int(m[1])*12+int(m[2])-1
    if t>NOW: return AGES[0]
    y=(NOW-t)/12
    return AGES[1] if y<2 else AGES[2] if y<6 else AGES[3] if y<11 else AGES[4]
MSPLIT={'부산광역시':'부산','대구광역시':'대구','대전광역시':'대전','울산광역시':'울산','세종특별자치시':'세종','전남광주통합특별시':'광주(옛 광주 5개 구)'}
def region(d):
    l1,l2=LOC.get(d,(None,None));r=reg(l1,l2)
    return r,(MSPLIT.get(l1) if r=='5대광역시+세종' else None)
agg=collections.defaultdict(lambda:{'new':collections.Counter(),'old':collections.Counter()})
for d,n in NL.items():
    r,s=region(d);a=age(d);agg[r]['new'][a]+=n
    if s: agg['5대광역시+세종·'+s]['new'][a]+=n
for d,n in l28.items():
    r,s=region(d);a=age(d);agg[r]['old'][a]+=n
    if s: agg['5대광역시+세종·'+s]['old'][a]+=n
order=REGIONS+['5대광역시+세종·'+v for v in MSPLIT.values()]+['미확인']
rows=[]
for r in order:
    if r not in agg: continue
    x=agg[r];tn=sum(x['new'].values());to=sum(x['old'].values())
    rows.append({'region':r,'newlight_lst':int(tn),'newlight_by_age':{a:int(x['new'][a]) for a in AGES},
      'newlight_share_by_age':{a:round(x['new'][a]/tn,4) if tn else None for a in AGES},
      'existing_0928_lst':int(to),'existing_share_by_age':{a:round(x['old'][a]/to,4) if to else None for a in AGES}})
SG=collections.Counter()
for d,n in NL.items():
    l1,l2=LOC.get(d,(None,None));SG[(l1,l2)]+=n
tot=sum(NL.values())
top_sgg=[{'local1':a,'local2':b,'region':reg(a,b),'newlight_lst':int(n),'share':round(n/tot,4)} for (a,b),n in SG.most_common(10)]
top_danji=[]
for d,n in sorted(NL.items(),key=lambda x:-x[1])[:20]:
    l1,l2=LOC.get(d,(None,None));a=A.get(d,{})
    top_danji.append({'danji_id':int(d),'name':NM.get(d,''),'region':reg(l1,l2),'local1':l1,'local2':l2,'completion':a.get('cd'),'households':int(a['hh']) if a else None,'age_group':age(d),'newlight_lst':int(n),'lst_0928':int(l28.get(d,0))})
meta={'definition':{
 'new_light':'9/28 아파트 상품 미이용 → 11/1 LIGHT 이용 중개사(%d명)의 11/1 노출 매물(직방 광고매물, 제휴 제외).'%len(nl),
 'existing':'9/28 직방 광고매물(제휴 제외) 전체 — 같은 지역 비교용 분포.',
 'age':'단지 준공 시점(zb_ods_area_danji.completion_date) 기준 연차(2026-11 기준). 입주예정·분양 = occupancy_status 분양·입주예정 또는 준공 시점이 미래.',
 'region':'사업부 9개 시장지역. 5대광역시+세종은 시도별로 한 번 더 나눔(광주는 옛 광주 5개 구).',
 'note':'영업 채널(소속)별 분석은 하지 않음(내부 사정, 리포트 제외 원칙).'},
 'total_newlight_lst':int(tot)}
json.dump({'meta':meta,'rows':rows,'top_sgg':top_sgg,'top_danji':top_danji},open(os.path.join(HERE,'../../data/v2/region_newlight_age.json'),'w'),ensure_ascii=False,indent=1)
for r in rows: print(r['region'],r['newlight_lst'],{a[:4]:v for a,v in r['newlight_share_by_age'].items()},'| old',{a[:4]:v for a,v in r['existing_share_by_age'].items()})
