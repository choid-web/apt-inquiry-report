# 작업 3. 후보 단지 목록 v2 — 직방 매물 0~9건, 점수 = 단지 조회 유저·관심 백분위 평균(문의 제외)
import json,collections,sys,os,re,bisect,csv
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from common import *
HERE=os.path.dirname(os.path.abspath(__file__));OUT=os.path.join(HERE,'../../data/v2')
RAW={'lst1101':'1793793594631',
 'view_zb':['1793671188264','1793671212280','1793671222480','1793671245111'],
 'view_hg':['1793671271840','1793671354075','1793671409267','1793671504205','1793671536524'],
 'inq_post':('1793632662548','1793632667621'),
 'attr':['1793698669848','1793698679630','1793698755798','1793698766252','1793797700567','1793797846116','1793797857945'],   # danji_id, total_households, completion_date (≥100세대) + 미만
 'loc':['1793698778567','1793698854635','1793698858119','1793797700567','1793797846116','1793797857945'],
 'name':['1793699062180','1793699073344','1793699077906']+json.loads(os.environ.get('NAME_EXTRA','[]')),
 'occ':os.environ.get('OCC_KEY','1793672184712'),'rent':'1793671603360',
 'naver':['1793798443424','1793798459869','1793798473120','1793798486794'],
 'naver_total':['1793798331390','1793798339963','1793798416710','1793798427556']}
l01={sid(r['zbhg_ods_item.area_danji_id']):float(r['zb_daily_operating_item.open_item_cnt'] or 0) for r in L(RAW['lst1101']) if r['zbhg_ods_item.area_danji_id'] is not None}
V=collections.Counter();W=collections.Counter()
for f in RAW['view_zb']:
    for r in L(f): i=sid(r['zb_apart_view_wish_call.area_danji_id']);V[i]+=float(r['zb_apart_view_wish_call.view_user_cnt'] or 0);W[i]+=float(r['zb_apart_view_wish_call.wish_cnt'] or 0)
for f in RAW['view_hg']:
    for r in L(f): i=sid(r['hg_ods_apt.zb_area_danji_id']);V[i]+=float(r['hg_apart_view_wish_call.view_user_cnt'] or 0);W[i]+=float(r['hg_apart_view_wish_call.wish_cnt'] or 0)
I=collections.Counter()
for r in L(RAW['inq_post'][0]): I[sid(r['zb_apart_view_wish_call.area_danji_id'])]+=float(r['zb_apart_view_wish_call.inquiry_cnt'] or 0)
for r in L(RAW['inq_post'][1]): I[sid(r['hg_ods_apt.zb_area_danji_id'])]+=float(r['hg_apart_view_wish_call.inquiry_cnt'] or 0)
A={}
for f in RAW['attr']:
    for r in L(f): A[sid(r['zb_ods_area_danji.danji_id'])]={'hh':float(r['zb_ods_area_danji.total_households'] or 0),'cd':r['zb_ods_area_danji.completion_date']}
for f in RAW['loc']:
    for r in L(f):
        i=sid(r['zb_ods_area_danji.danji_id'])
        if i in A: A[i]['l1'],A[i]['l2']=r.get('zb_ods_area_danji.local1'),r.get('zb_ods_area_danji.local2')
NM={};PRO={}
for f in RAW['name']:
    for r in L(f): i=sid(r['zb_ods_area_danji.danji_id']);NM[i]=r['zb_ods_area_danji.danji_name'];PRO[i]=r['zb_ods_area_danji.is_pro_entry']
OCC={sid(r['zb_ods_area_danji.danji_id']):r['zb_ods_area_danji.occupancy_status'] for r in L(RAW['occ'])}
RENT={sid(r['zb_ods_area_danji.danji_id']) for r in L(RAW['rent'])}
# N사: 단지 × has_pro_product × has_other_product → 고유 매물·중개사 수
NV=collections.defaultdict(lambda:{'nv_lst':0,'nv_pro':0,'nv_lb':0,'nv_none':0})
k='zb_naver_mapped_items.'
for f in RAW['naver']:
    for r in L(f):
        d=sid(r[k+'area_danji_id']);n=r[k+'realtor_cnt'] or 0;x=NV[d];x['nv_lst']+=r[k+'unique_article_cnt'] or 0
        if r[k+'has_pro_product']=='Y': x['nv_pro']+=n
        elif r[k+'has_other_product']=='Y': x['nv_lb']+=n
        else: x['nv_none']+=n
# 추가 조회 5곳(11/4, 조회값 옮겨 적음): 모두 PRO·LIGHT·BASIC 미이용 중개사만
for d,a,n in [('37461',76,7),('20103',29,9),('6073',25,11),('1904',16,8),('18385',10,3)]:
    NV[d]={'nv_lst':a,'nv_pro':0,'nv_lb':0,'nv_none':n}
HAVE_NV=bool(RAW['naver'])
NVT={}
for f in RAW['naver_total']:
    for r in L(f): NVT[sid(r[k+'area_danji_id'])]=r[k+'unique_article_cnt'] or 0
def ym(cd):
    m=re.match(r'(\d{4})년(\d{2})월',cd or '');return int(m[1])*12+int(m[2])-1 if m else None
NOW=2026*12+10;W0,W1=NOW,2027*12+4
def eligible(i,a,min_hh):
    if a['hh']<min_hh or i in RENT or NM.get(i,'').find('테스트')>=0: return None
    t=ym(a['cd']);o=OCC.get(i)
    if o in('분양','입주예정') or (t is not None and t>NOW):
        if t is None or not(W0<=t<=W1): return None
        if o=='입주예정' or (t is not None and t>NOW and o!='분양'):
            if NVT.get(i,0)<=0: return None
            return '입주예정'
        return '분양'
    return ''
def build(min_hh):
    U=[]
    for i,a in A.items():
        n=l01.get(i,0)
        if n>9: continue
        e=eligible(i,a,min_hh)
        if e is None: continue
        U.append(dict(id=i,lst=int(n),bk=bucket(n) if n>0 else '0',view=V.get(i,0),wish=W.get(i,0),inq=I.get(i,0),note=e,**a))
    cv=sorted(u['view'] for u in U);cw=sorted(u['wish'] for u in U)
    for u in U:
        u['score']=round((bisect.bisect_right(cv,u['view'])/len(cv)+bisect.bisect_right(cw,u['wish'])/len(cw))/2,4)
    return U
U=build(100);U100=build(0)
def top(U,grp,n=500):
    s=[u for u in U if (u['bk'] in('0','1~2'))==(grp=='0~2')];s.sort(key=lambda u:(-u['score'],-u['view']));return s[:n]
T02=top(U,'0~2');T39=top(U,'3~9')
old=set(str(r['id']) for r in json.load(open(os.path.join(HERE,'../../data/top518.json'))))
def row(u,rank):
    i=u['id'];nv=NV.get(i) if i in NV else ({'nv_lst':0,'nv_pro':0,'nv_lb':0,'nv_none':0} if NVT.get(i,0)==0 else None)
    return {'rank':rank,'region':reg(u.get('l1'),u.get('l2')),'local1':u.get('l1'),'local2':u.get('l2'),'danji_id':int(i),'name':NM.get(i,''),
            'households':int(u['hh']),'completion':u['cd'],'bucket':u['bk'],'zb_listings_1101':u['lst'],'danji_view_users':int(u['view']),
            'wish':int(u['wish']),'inquiry_ref':int(u['inq']),'score':u['score'],'pro_entry':PRO.get(i,''),
            'naver_listings':int(NVT.get(i,0)),'naver_agents_pro':nv['nv_pro'] if nv else None,'naver_agents_light_basic':nv['nv_lb'] if nv else None,'naver_agents_none':nv['nv_none'] if nv else None,
            'note':u['note'],'in_old_518':i in old,'region_assoc_mark':''}
L02=[row(u,k+1) for k,u in enumerate(T02)];L39=[row(u,k+1) for k,u in enumerate(T39)]
comb=sorted(T02+T39,key=lambda u:(-u['score'],-u['view']));LC=[row(u,k+1) for k,u in enumerate(comb)]
# 100세대 미만 허용 비교
def topids(U,grp): return {u['id'] for u in top(U,grp)}
small_in={g:sum(1 for i in topids(U100,g) if A[i]['hh']<100) for g in('0~2','3~9')}
cmp={'universe_size':{'0~2':sum(u['bk'] in('0','1~2') for u in U),'3~9':sum(u['bk']=='3~9' for u in U)},
     'overlap_old_518':{'0~2':sum(r['in_old_518'] for r in L02),'3~9':sum(r['in_old_518'] for r in L39),'combined':sum(r['in_old_518'] for r in LC)},
     'under100_enter_top500_if_allowed':small_in,
     'universe_size_if_under100_allowed':{'0~2':sum(u['bk'] in('0','1~2') for u in U100),'3~9':sum(u['bk']=='3~9' for u in U100)},
     'region_counts':{g:dict(collections.Counter(r['region'] for r in Lx)) for g,Lx in (('0~2',L02),('3~9',L39))},
     'naver_composition_included':HAVE_NV}
meta={'definition':{
 'universe':'11/1 직방 광고매물(ods 등록, 제휴 제외, 노출) 0~9건 아파트 단지. 제외: 임대, 100세대 미만, 입주 6개월 초과(2027-05 이후) 분양·입주예정, 테스트 단지. 입주 6개월 이내 입주예정은 N사 매물이 있을 때만 포함(비고 입주예정).',
 'score':'최근 3주(10/12~11/1) 단지 조회 유저(직방+호갱노노 합, 앱 간 중복 미제거)와 관심(관심 단지 등록) 각각의 백분위(모집단 대비, 같은 값은 상위 순위로) 평균. 문의는 점수에 넣지 않고 참고 열(inquiry_ref)로만.',
 'lists':'top_0_2 = 매물 0~2건 상위 500, top_3_9 = 매물 3~9건 상위 500, combined = 둘을 합쳐 점수순(1,000곳). 백분위는 0~9건 전체 모집단 기준이라 두 목록 점수를 바로 비교할 수 있음.',
 'naver':'zb_naver_mapped_items 11/1. N사 매물 = 고유 매물 수, 중개사 수 = 그 단지에 매물을 올린 고유 중개사 수를 직방 아파트 상품 이용 상태별로 나눔(PRO 이용 / LIGHT·BASIC 이용 / 직방 상품 미이용).',
 'region_assoc_mark':'지역회 O/X/△ 표시용 빈칸(내부 작업용, 리포트에 쓰지 않음).'},
 'compare':cmp}
json.dump({'meta':meta,'top_0_2':L02,'top_3_9':L39,'combined':LC},open(os.path.join(OUT,'candidates_v2.json'),'w'),ensure_ascii=False,indent=1)
cols=['list']+list(LC[0].keys())
with open(os.path.join(OUT,'candidates_v2.csv'),'w',newline='',encoding='utf-8-sig') as fh:
    w=csv.writer(fh);w.writerow(cols)
    for nm,Lx in (('0~2',L02),('3~9',L39)):
        for r in Lx: w.writerow([nm]+[r[c] for c in cols[1:]])
print(json.dumps(cmp,ensure_ascii=False))
