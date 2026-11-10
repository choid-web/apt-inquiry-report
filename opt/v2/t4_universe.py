# 작업 4. '의미 있는 단지' 모집단
import json,collections,sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from common import *
HERE=os.path.dirname(os.path.abspath(__file__))
CLS=['1793798042827','1793798052683','1793798062294','1793798140247','1793798150165','1793798162111','1793798174044']
ATTR=['1793698669848','1793698679630','1793698755798','1793698766252','1793797700567','1793797846116','1793797857945']
LOCF=['1793698778567','1793698854635','1793698858119','1793797700567','1793797846116','1793797857945']
C={};H={};LOC={}
for f in CLS:
    for r in L(f): C[sid(r['zb_ods_area_danji.danji_id'])]=(int(r['zb_ods_area_danji.enabled2']),r['zb_ods_area_danji.category2'])
for f in ATTR:
    for r in L(f): H[sid(r['zb_ods_area_danji.danji_id'])]=float(r['zb_ods_area_danji.total_households'] or 0)
for f in LOCF:
    for r in L(f): LOC[sid(r['zb_ods_area_danji.danji_id'])]=(r.get('zb_ods_area_danji.local1'),r.get('zb_ods_area_danji.local2'))
RENT={sid(r['zb_ods_area_danji.danji_id']) for r in L('1793671603360')}
OCC={sid(r['zb_ods_area_danji.danji_id']):r['zb_ods_area_danji.occupancy_status'] for r in L('1793672184712')}
KEEP={'아파트','주상복합','주상복합2','재건축','분양전환(전체)'}
steps=['비노출 단지(enabled2≠4)','아파트 외 유형(연립·빌라·뉴스테이·광고단지·삭제대상 등)','임대 단지','100세대 미만(세대수 미상 포함)','분양 단계(입주 전 분양·청약)']
ex=collections.Counter();keep=[];step_region=collections.defaultdict(collections.Counter)
for i,(en,c2) in C.items():
    r=reg(*LOC.get(i,(None,None)))
    if en!=4: ex[steps[0]]+=1;continue
    if c2 not in KEEP: ex[steps[1]]+=1;continue
    if i in RENT: ex[steps[2]]+=1;continue
    if H.get(i,0)<100: ex[steps[3]]+=1;continue
    if OCC.get(i)=='분양': ex[steps[4]]+=1;continue
    keep.append(i)
exposed=[i for i,(en,c2) in C.items() if en==4]
byr=collections.Counter(reg(*LOC.get(i,(None,None))) for i in keep)
byr_exp=collections.Counter(reg(*LOC.get(i,(None,None))) for i in exposed)
cand=json.load(open(os.path.join(HERE,'../../data/v2/candidates_v2.json')))
cids={str(r['danji_id']) for r in cand['combined']};c02={str(r['danji_id']) for r in cand['top_0_2']};c39={str(r['danji_id']) for r in cand['top_3_9']}
ks=set(keep)
out={'definition':'단지 등급(S1/S2 등) 필드는 zb_ods_area_danji에 없음(확인한 분류 필드: enabled2 노출 여부, category·category2 단지 분류, is_rental, occupancy_status, is_pro_target). 대안 기준 = 아파트 서비스 단지 중 ① 노출(enabled2=4) ② 단지세부분류가 아파트·주상복합·주상복합2·재건축·분양전환 ③ 임대 아님 ④ 100세대 이상 ⑤ 분양 단계(입주 전) 아님. 위 순서대로 제외. 입주예정 단지는 포함.',
 'total':len(C),'exposed_total':len(exposed),'excluded_by':dict((s,ex[s]) for s in steps),'meaningful':len(keep),
 'by_region':{r:byr.get(r,0) for r in REGIONS+['미확인'] if byr.get(r,0)},
 'by_region_exposed_all':{r:byr_exp.get(r,0) for r in REGIONS+['미확인'] if byr_exp.get(r,0)},
 'is_pro_target_note':'프로 판매 대상(is_pro_target=1)은 노출 아파트 31,274곳 중 약 3.0만 곳으로 노출 단지와 거의 겹쳐 모집단 축소 기준으로는 쓰지 않음.',
 'candidates_share':{'combined_1000':{'in_meaningful':len(cids&ks),'share_of_meaningful':round(len(cids)/len(keep),4)},
                     'top_0_2_500':round(len(c02)/len(keep),4),'top_3_9_500':round(len(c39)/len(keep),4)}}
json.dump(out,open(os.path.join(HERE,'../../data/v2/universe.json'),'w'),ensure_ascii=False,indent=1)
print(json.dumps({k:out[k] for k in ['total','exposed_total','excluded_by','meaningful','by_region','candidates_share']},ensure_ascii=False))
