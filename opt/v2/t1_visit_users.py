# 작업 1. 방문 유저 — 2026-11-04 de-cube 조회값을 옮겨 적고 집계.
# zb: zb_dau_conversion.dau (service_type=아파트, 앱+웹, base_date granularity=week)
# hg: hg_dau_conversion.dau (service_type=호갱노노, 앱+웹, base_date granularity=week)
# 같은 값으로 view_user(그 주 방문 유저 중 조회 유저)도 함께 받음.
import json
WEEKS=['2026-08-03','2026-08-10','2026-08-17','2026-08-24','2026-08-31','2026-09-07','2026-09-14','2026-09-21','2026-09-28','2026-10-05','2026-10-12','2026-10-19','2026-10-26']
ZB=[362466,360388,366133,379922,367524,347833,322208,327184,350010,346606,349403,340212,334574]
ZBV=[306479,303963,309497,321577,310634,293345,270923,275184,295466,292242,294334,285920,280288]
HG=[1369890,1373825,1373438,1369515,1376528,1370094,1351054,1311068,1361617,1342295,1349871,1339179,1323303]
HGV=[1206400,1218972,1222789,1215885,1218093,1217628,1193831,1129002,1152540,1149040,1147516,1138364,1120349]
PRE=['2026-08-31','2026-09-07','2026-09-14']; POST=['2026-10-12','2026-10-19','2026-10-26']
HOL={'2026-09-21':'추석 연휴 주'}
def blk(v,vv):
    d=dict(zip(WEEKS,v)); dv=dict(zip(WEEKS,vv))
    pre=sum(d[w] for w in PRE)/3; post=sum(d[w] for w in POST)/3
    return {'pre':round(pre),'post':round(post),'change':round(post/pre-1,4),
            'weekly':[{'week_start':w,'visit_users':d[w],'view_users':dv[w],**({'note':HOL[w]} if w in HOL else {})} for w in WEEKS]}
zb=blk(ZB,ZBV); hg=blk(HG,HGV)
tot=blk([a+b for a,b in zip(ZB,HG)],[a+b for a,b in zip(ZBV,HGV)])
out={'definition':'주 평균 방문 유저 = 달력 주(월~일) 동안 한 번 이상 방문한 고유 로그인 유저 수(앱+웹)를 주마다 구해 3주 평균. 전 3주 = 8/31~9/20 시작 주(8/31·9/7·9/14), 최근 3주 = 10/12·10/19·10/26 시작 주. 직방은 아파트 서비스 방문 유저(직방 앱 안 아파트 화면 방문), 호갱노노는 서비스 전체 방문 유저. 합계는 두 앱 단순 합(두 앱을 모두 쓴 유저는 중복).',
     'cube':{'zb':'zb_dau_conversion.dau (service_type=아파트, platform 필터 없음=앱+웹, base_date granularity=week → 주 내 count_distinct user_no)','hg':'hg_dau_conversion.dau (service_type=호갱노노, platform 필터 없음=앱+웹, granularity=week)'},
     'unique_basis':'주(월~일) 단위 고유. 일 단위 DAU 합이 아님. zb는 같은 값이 zb_wau_mau_conversion 일요일 7일 롤링 WAU와 일치함을 확인(8/9 362,466).',
     'view_users_note':'view_users = 같은 주 방문 유저 중 조회 유저(직방=아파트 조회, 호갱노노=전체 조회). 리포트의 단지 조회 유저(단지별 합)와 다른 값.',
     'platforms':{'zb':zb,'hg':hg,'total':tot}}
json.dump(out,open('data/v2/visit_users.json','w'),ensure_ascii=False,indent=1)
for k in ['zb','hg','total']: print(k,out['platforms'][k]['pre'],out['platforms'][k]['post'],out['platforms'][k]['change'])
