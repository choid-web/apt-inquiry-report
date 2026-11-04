# 후보 단지 2,000곳 (11/5 사용자 지시): t3와 같은 모집단·점수(단지 조회 유저 백분위 + 관심 백분위) ÷ 2.
# 제외: 성남시 분당구·수원시 영통구·화성시 동탄구·파주시, 분양 단지. 구간 구분 없이 점수 상위 2,000곳.
import os,json,csv,collections,statistics as st
HERE=os.path.dirname(os.path.abspath(__file__))
src=open(os.path.join(HERE,'t3_candidates.py')).read(); src=src[:src.index("L02=")]
g={'__file__':os.path.join(HERE,'t3_candidates.py'),'__name__':'t3'}; exec(src,g)
U,row=g['U'],g['row']
# 11/5 추가 조회: 기존에 N사 중개사 구성이 없던 1,129곳(zb_naver_mapped_items 11/1, 230개씩 5회)
NEW_NV=['1793808044431','1793808062305','1793808075077','1793808088690','1793808100807']
k='zb_naver_mapped_items.'
for f in NEW_NV:
    for r in g['L'](f):
        d=g['sid'](r[k+'area_danji_id']);n=r[k+'realtor_cnt'] or 0;x=g['NV'][d]
        x['nv_lst']+=r[k+'unique_article_cnt'] or 0
        if r[k+'has_pro_product']=='Y': x['nv_pro']+=n
        elif r[k+'has_other_product']=='Y': x['nv_lb']+=n
        else: x['nv_none']+=n
EXR={('경기도','성남시 분당구'),('경기도','수원시 영통구'),('경기도','화성시 동탄구'),('경기도','파주시')}
ex=collections.Counter(u.get('l2') for u in U if (u.get('l1'),u.get('l2')) in EXR)
ex_bunyang=sum(u['note']=='분양' for u in U)
P=[u for u in U if (u.get('l1'),u.get('l2')) not in EXR and u['note']!='분양']
top=sorted(P,key=lambda u:(-u['score'],-u['view']))[:2000]
L=[row(u,k+1) for k,u in enumerate(top)]
C795={str(r[5]) for r in json.load(open(os.path.join(HERE,'../../rpt/data.json')))['cand']}
for r,u in zip(L,top): r['in_795']=u['id'] in C795
G=lambda r:'0~2' if r['bucket'] in('0','1~2') else '3~9'
summ={'universe_after_exclusion':len(P),'excluded_region_danji':dict(ex),'excluded_bunyang':ex_bunyang,
 'n':len(L),'by_bucket':dict(collections.Counter(G(r) for r in L)),'zero_listing':sum(r['bucket']=='0' for r in L),
 'overlap_795':sum(r['in_795'] for r in L),'score_min':min(r['score'] for r in L),
 'view_min':min(r['danji_view_users'] for r in L),'view_median':st.median(r['danji_view_users'] for r in L),
 'wish_median':st.median(r['wish'] for r in L),'hh_median':st.median(r['households'] for r in L),
 'naver_listing_danji':sum(r['naver_listings']>0 for r in L),
 'naver_agent_mix_known':sum(r['naver_agents_pro'] is not None for r in L),
 'by_region':dict(collections.Counter(r['region'] for r in L).most_common())}
meta={'definition':{'universe':'t3_candidates.py와 같음(11/1 직방 광고매물 0~9건, 임대·100세대 미만·입주 6개월 초과 분양/입주예정 제외) + 분양 단지 제외 + 성남 분당구·수원 영통구·화성 동탄구·파주시 제외.',
 'score':'(최근 3주 단지 조회 유저 백분위 + 관심 등록 백분위) ÷ 2. 백분위는 0~9건 전체 모집단 기준(t3와 같음). 동점이면 조회 유저 많은 순.',
 'select':'구간(0~2·3~9) 구분 없이 점수 상위 2,000곳.',
 'naver_agents':'N사 매물을 올린 중개사 수를 직방 아파트 상품 이용 상태(PRO / LIGHT·BASIC / 미이용)로 나눔. 기존 v2 1,000곳 조회분 + 11/5 추가 조회 1,129곳.'},'summary':summ}
OUT=os.path.join(HERE,'../../data/v2')
json.dump({'meta':meta,'rows':L},open(os.path.join(OUT,'candidates_2000.json'),'w'),ensure_ascii=False,indent=1)
H={'rank':'순위','region':'사업부 지역','local1':'시도','local2':'시군구','danji_id':'단지 ID','name':'단지명','households':'세대수','completion':'준공(입주)','bucket':'매물 구간','zb_listings_1101':'11/1 직방 매물','danji_view_users':'단지 조회 유저','wish':'관심','inquiry_ref':'문의(참고)','score':'점수','pro_entry':'PRO 입점','naver_listings':'N사 매물','naver_agents_pro':'N사 중개사 PRO 이용','naver_agents_light_basic':'N사 중개사 LIGHT·BASIC','naver_agents_none':'N사 중개사 미이용','note':'비고','in_old_518':'이전 518 포함','in_795':'현재 795 포함','region_assoc_mark':'지역회 표시(내부용)'}
with open(os.path.join(OUT,'candidates_2000.csv'),'w',newline='',encoding='utf-8-sig') as fh:
    w=csv.writer(fh); w.writerow([H[k] for k in H])
    for r in L: w.writerow(['' if r[k] is None else r[k] for k in H])
print(json.dumps(summ,ensure_ascii=False,indent=1))
