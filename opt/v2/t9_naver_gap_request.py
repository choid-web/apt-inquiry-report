# N사 수집·매핑 누락 요청 단지 목록 (11/5). 후보 2,000곳 중 11/1 N사 매핑 매물 0건 169곳.
# 수집 이력: zb_naver_mapped_items 2025-01~2026-10 월별, area_danji_id 기준 (tool-results 1793852730949)
import os,sys,json,csv,collections
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
from common import L,sid
k='zb_naver_mapped_items.'
H=collections.defaultdict(dict)
for r in L('1793852730949'):
    n=int(r[k+'unique_article_cnt'] or 0)
    if n>0: H[sid(r[k+'area_danji_id'])][r[k+'base_date.month'][:7]]=n
R=json.load(open(os.path.join(HERE,'../../data/v2/candidates_2000.json')))['rows']
rows=[]
for r in R:
    if not r['mapping_check']: continue
    h=H.get(str(r['danji_id']),{})
    lm=max(h) if h else ''
    if r['mapping_check']=='N사 이력 없음': t='C. N사 이력 없음(매핑 누락 여부 확인 필요)'
    elif lm: t='A. 수집 중단(예전엔 수집·매핑됨)'
    else: t='B. 2025년 이후 매핑 기록 없음(수집 안 됨 또는 매핑 누락)'
    rows.append({'요청 구분':t,'후보 순위':r['rank'],'직방 단지 ID':r['danji_id'],'단지명':r['name'],'시도':r['local1'],'시군구':r['local2'] or '',
      '세대수':r['households'],'준공(입주)':r['completion'],'직방 매물 구간':r['bucket'],'최근 3주 단지 조회 유저':r['danji_view_users'],
      'N사 매물 이력 12개월(활동 데이터)':r['naver_hist_12m'],'N사 매물 이력 3개월(활동 데이터)':r['naver_hist_3m'],
      '마지막 수집·매핑 월':lm,'마지막 월 N사 매물 수':h.get(lm,'') if lm else '','N사 단지번호(확인분)':'','비고':''})
# 사용자가 N사 URL로 확인한 단지(11/5)
for x in rows:
    if x['단지명']=='올림픽선수기자촌': x['N사 단지번호(확인분)']='634'; x['비고']='11/5 확인: 2025-11까지 수집·매핑, 이후 수집 없음'
    if x['단지명']=='목동신시가지7단지': x['N사 단지번호(확인분)']='659'; x['비고']='11/5 확인: 2024년 이후 수집 기록 없음'
    if x['단지명']=='진산마을삼성래미안5차': x['N사 단지번호(확인분)']='8213'; x['비고']='11/5 확인: N사 8213은 2026-07까지 수집됐으나 직방 단지 매핑 없음(매핑 누락)'
rows.sort(key=lambda x:(x['요청 구분'],x['후보 순위']))
out=os.path.join(HERE,'../../data/v2/naver_gap_request.csv')
with open(out,'w',newline='',encoding='utf-8-sig') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
print(collections.Counter(x['요청 구분'] for x in rows)); print(len(rows))
