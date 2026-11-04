# 작업 5. N사 매핑 누락 점검
# ACT = zb_danji_realtor_activity (snapshot 2026-11-01) 조회값: 단지 -> (n_cnt_sum N사 매물 이력 12개월, activity_agent_cnt)
import json,collections,sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from common import *
HERE=os.path.dirname(os.path.abspath(__file__))
ACT={34:(429,13),240:(89,19),287:(509,20),359:(829,28),360:(3114,31),362:(1578,19),364:(322,27),365:(2162,10),421:(554,26),484:(586,24),549:(262,29),555:(509,34),581:(180,15),694:(6778,14),697:(178,24),699:(186,15),722:(348,22),733:(1539,43),821:(141,23),826:(63,11),829:(198,20),888:(56,16),982:(56,13),983:(165,15),1017:(722,32),1018:(126,20),1028:(465,43),1044:(142,25),1073:(1673,17),1077:(3966,23),1083:(3456,24),1092:(57,16),1182:(0,0),1201:(0,0),1204:(0,1),1213:(0,2),1239:(278,16),1315:(244,28),1375:(3,2),1392:(1307,31),1498:(6168,38),1626:(548,12),2322:(138,25),2406:(229,20),2426:(783,29),2452:(322,20),2479:(174,19),2497:(0,3),2498:(645,14),2918:(427,23),2954:(622,32),3988:(569,26),5474:(0,1),5497:(336,29),10799:(301,46),26535:(857,28),33075:(3776,44),33076:(1411,33),78928:(4562,58),87818:(0,0),88747:(0,0),90807:(0,0),92487:(216,11),94973:(0,0),95096:(0,0)}
# 대단지(500세대 이상 + 최근 3주 단지 조회 유저 1,000명 이상) 중 11/1 N사 매핑 매물 0건 단지 수와, 그중 활동도 원천에 N사 매물 이력이 있는 단지 수(danji_cnt 조회값, 3묶음 합 172+14+0)
BIG_GAP_WITH_HISTORY=186
NVT={}
for f in ['1793798331390','1793798339963','1793798416710','1793798427556']:
    for r in L(f): NVT[sid(r['zb_naver_mapped_items.area_danji_id'])]=r['zb_naver_mapped_items.unique_article_cnt'] or 0
NM={};
for f in ['1793699062180','1793699073344','1793699077906']:
    for r in L(f): NM[sid(r['zb_ods_area_danji.danji_id'])]=r['zb_ods_area_danji.danji_name']
A={};LOC={}
for f in ['1793698669848','1793698679630','1793698755798','1793698766252']:
    for r in L(f): A[sid(r['zb_ods_area_danji.danji_id'])]=float(r['zb_ods_area_danji.total_households'] or 0)
for f in ['1793698778567','1793698854635','1793698858119']:
    for r in L(f): LOC[sid(r['zb_ods_area_danji.danji_id'])]=(r.get('zb_ods_area_danji.local1'),r.get('zb_ods_area_danji.local2'))
T=json.load(open(os.path.join(HERE,'../../data/top518.json')));HN=json.load(open(os.path.join(HERE,'../../data/h_naver.json')))
checked=[]
for r in T:
    i=str(r['id'])
    if HN[i]['all']!=0: continue
    n,a=ACT[int(i)]
    mapped_now=NVT.get(i,0)>0
    if n>0: note='N사 매물 이력 있음(12개월 %d건, 활동 중개사 %d명)인데 11/1 매핑 매물 0건 → 단지 매핑 누락 추정'%(n,a)
    else: note='N사 매물 이력도 없음 → 실제 N사 매물이 없거나(신축·소규모 등) 매핑 자체가 없음. 이 자료로 구분 불가'
    checked.append({'id':int(i),'name':NM.get(i,r.get('name','')),'region':reg(*LOC.get(i,(r.get('l1'),r.get('l2')))),'hh':int(A.get(i,r.get('hh') or 0)),'view':int(r['view']),
                    'mapped':mapped_now,'naver_history_12m':n,'activity_agents':a,'mapping_gap_suspected':n>0 and not mapped_now,'note':note})
big=[i for i,h in A.items() if h>=500]
need=json.load(open(os.environ.get('NV_NEED','/tmp/claude-0/-home-claude/2cc0b143-8bcb-52c0-8b96-02b78da6f48e/scratchpad/v2/nv_need.json')))['big']
gap=[i for i in need if NVT.get(i,0)<=0]
out={'definition':{
 'checked':'우선 단지 518곳(data/top518.json) 중 기존 N사 집계(data/h_naver.json)에서 N사 매물 0건이던 65곳. mapped = 11/1 zb_naver_mapped_items에 매물이 1건 이상 매핑되는지. naver_history_12m = zb_danji_realtor_activity(11/1)의 N사 매물 이력 합(최근 12개월, 활동 중개사 기준).',
 'mapping_source':'N사 단지 ID(hscp_no) ↔ 직방 단지 ID 매핑 표는 공개 큐브에서 직접 조회할 수 없음. 대신 같은 단지에 대해 활동도 원천(직방 단지 ID 기준)에는 N사 매물 이력이 있는데 매핑 매물 큐브에는 0건이면 매핑 누락으로 추정.',
 'gap_count_large_danji':'세대수 500 이상 + 최근 3주(10/12~11/1) 단지 조회 유저(직방+호갱노노) 1,000명 이상 단지 중 11/1 N사 매핑 매물 0건인 단지 수.'},
 'checked':checked,
 'summary_65':{'total':len(checked),'gap_suspected':sum(c['mapping_gap_suspected'] for c in checked),'no_history':sum(c['naver_history_12m']==0 for c in checked)},
 'gap_count_large_danji':len(gap),'large_danji_total':len(need),'gap_large_with_naver_history':BIG_GAP_WITH_HISTORY,
 'gap_large_without_history':len(gap)-BIG_GAP_WITH_HISTORY}
json.dump(out,open(os.path.join(HERE,'../../data/v2/naver_mapping_gap.json'),'w'),ensure_ascii=False,indent=1)
print(out['summary_65'],out['gap_count_large_danji'],out['large_danji_total'])
print([ (c['name'],c['naver_history_12m']) for c in checked if '한강' in c['name']])
