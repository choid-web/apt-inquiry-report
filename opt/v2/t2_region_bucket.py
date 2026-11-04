# 작업 2. 사업부 지역 × 9/28 매물 구간별 신규 LIGHT 유입과 문의 변화
import json,collections,sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from common import *
RAW={'lst0928':'1793793590536','lst1101':'1793793594631','subs0928':'1793793613751','subs1101':'1793793618800',
     'agent1101':['1793793644837','1793793845854','1793793854436','1793793863409','1793793940836','1793793949355','1793793958283','1793793969328'],
     'inq_pre':('1793793986260','1793793991288'),'inq_post':('1793632662548','1793632667621'),
     'loc':['1793698778567','1793698854635','1793698858119']+json.loads(os.environ.get('LOC_EXTRA','[]'))}
def lst(k): return {sid(r['zbhg_ods_item.area_danji_id']):float(r['zb_daily_operating_item.open_item_cnt'] or 0) for r in L(k) if r['zbhg_ods_item.area_danji_id'] is not None}
def inq(fz,fh):
    I=collections.Counter()
    for r in L(fz): I[sid(r['zb_apart_view_wish_call.area_danji_id'])]+=float(r['zb_apart_view_wish_call.inquiry_cnt'] or 0)
    for r in L(fh): I[sid(r['hg_ods_apt.zb_area_danji_id'])]+=float(r['hg_apart_view_wish_call.inquiry_cnt'] or 0)
    I.pop(None,None);return I
l28=lst(RAW['lst0928']);l01=lst(RAW['lst1101'])
k='zbhg_daily_apart_subscription.'
s28={r[k+'user_no'] for r in L(RAW['subs0928'])}
nl={r[k+'user_no'] for r in L(RAW['subs1101']) if r[k+'apart_subs']=='light'}-s28
NL=collections.Counter()
nlset={sid(x) for x in nl}
for f in RAW['agent1101']:
    for r in L(f):
        d=sid(r['zbhg_ods_item.area_danji_id']);u=sid(r['zbhg_ods_item.user_no'])
        if d and u in nlset: NL[d]+=float(r['zb_daily_operating_item.open_item_cnt'] or 0)
pre=inq(*RAW['inq_pre']);post=inq(*RAW['inq_post'])
loc={}
for f in RAW['loc']:
    for r in L(f): loc[sid(r['zb_ods_area_danji.danji_id'])]=(r.get('zb_ods_area_danji.local1'),r.get('zb_ods_area_danji.local2'))
ids=set(l28)|set(l01)
rows=collections.defaultdict(lambda:collections.Counter())
for d in ids:
    a,b=l28.get(d,0),l01.get(d,0)
    if a==0 and b==0: continue
    r=reg(*loc.get(d,(None,None)));bk=bucket(a);c=rows[(r,bk)]
    c['danji']+=1;c['lst_0928']+=a;c['lst_1101']+=b;n=NL.get(d,0);c['newlight_lst']+=n
    side='in' if n>0 else 'out';c['newlight_danji']+=(n>0);c['other_danji']+=(n==0)
    c[f'inq_{side}_pre']+=pre.get(d,0);c[f'inq_{side}_post']+=post.get(d,0)
regtot=collections.Counter()
for (r,bk),c in rows.items(): regtot[r]+=c['newlight_lst']
out=[]
for r in REGIONS+['미확인']:
    for bk in BUCKETS:
        if (r,bk) not in rows: continue
        c=rows[(r,bk)]
        def chg(a,b): return round(b/a-1,4) if a else None
        out.append({'region':r,'bucket':bk,'danji':c['danji'],'lst_0928':int(c['lst_0928']),'lst_1101':int(c['lst_1101']),
            'lst_change':chg(c['lst_0928'],c['lst_1101']),'newlight_lst':int(c['newlight_lst']),
            'newlight_share_in_region':round(c['newlight_lst']/regtot[r],4) if regtot[r] else None,
            'newlight_danji':c['newlight_danji'],'no_newlight_danji':c['other_danji'],
            'inq_in_pre':int(c['inq_in_pre']),'inq_in_post':int(c['inq_in_post']),'inq_in_change':chg(c['inq_in_pre'],c['inq_in_post']),
            'inq_out_pre':int(c['inq_out_pre']),'inq_out_post':int(c['inq_out_post']),'inq_out_change':chg(c['inq_out_pre'],c['inq_out_post'])})
tot=collections.Counter()
for o in out:
    for kk in ['danji','lst_0928','lst_1101','newlight_lst','newlight_danji','no_newlight_danji','inq_in_pre','inq_in_post','inq_out_pre','inq_out_post']: tot[kk]+=o[kk]
meta={'definition':{
 'listing':'직방 광고매물(ods 등록, 제휴 매물 제외), 아파트, 노출(open). zb_daily_operating_item.open_item_cnt × zbhg_ods_item.area_danji_id. 9/28·11/1 스냅샷.',
 'bucket':'9/28 단지 매물 수 구간. 0 구간은 9/28 매물 0건이면서 11/1에 매물이 생긴 단지만.',
 'new_light':'9/28에 아파트 상품(PRO·LIGHT·BASIC)을 이용하지 않다가 11/1에 LIGHT를 이용 중인 중개사(zbhg_daily_apart_subscription, apart_subs=light). %d명. 코호트 리포트(AOMC 반영원장 4,677곳)와 기준이 달라 값이 조금 다름.'%len(nlset),
 'newlight_lst':'신규 LIGHT 중개사가 11/1 그 단지에 노출 중인 매물 수(대표 중개사 기준, zbhg_ods_item.user_no).',
 'inquiry':'직방+호갱노노 단지별 문의 수(zb/hg_apart_view_wish_call, action_group=문의) 합. 전 3주 8/31~9/20, 최근 3주 10/12~11/1.',
 'in_out':'in = 신규 LIGHT 매물이 1건 이상 들어간 단지, out = 안 들어간 단지.',
 'region':'사업부 9개 시장지역(opt/m2b.py reg()와 동일). 단지 소재지가 확인되지 않은 단지는 미확인.'},
 'totals':dict(tot),'new_light_agents':len(nlset)}
json.dump({'meta':meta,'rows':out},open(os.path.join(os.path.dirname(__file__),'../../data/v2/region_bucket.json'),'w'),ensure_ascii=False,indent=1)
print(json.dumps(meta['totals'],ensure_ascii=False))
for o in out:
    if o['region'] in('경기B','경기C','서울A','미확인'): print(o['region'],o['bucket'],o['danji'],o['lst_0928'],o['lst_1101'],o['newlight_lst'],o['newlight_share_in_region'],o['inq_in_change'],o['inq_out_change'])
