import json,glob,collections
TD='/root/.claude/projects/-home-claude/2cc0b143-8bcb-52c0-8b96-02b78da6f48e/tool-results/'
def L(f):
    t=open(glob.glob(TD+'*'+f+'.txt')[0]).read();return json.loads(t[t.index('{'):])['data']
def sid(x): return str(x).split('.')[0] if x is not None else None
D={}
for f in ['1793698669848','1793698679630','1793698755798','1793698766252']:
    for r in L(f):
        i=sid(r['zb_ods_area_danji.danji_id']);D[i]={'hh':float(r['zb_ods_area_danji.total_households'] or 0),'cd':r['zb_ods_area_danji.completion_date']}
loc={}
for f in ['1793698778567','1793698854635','1793698858119']:
    for r in L(f):
        loc[sid(r['zb_ods_area_danji.danji_id'])]=(r['zb_ods_area_danji.local1'],r.get('zb_ods_area_danji.local2'))
for i in D: D[i]['l1'],D[i]['l2']=loc.get(i,(None,None))
print('danji',len(D),'noloc',sum(1 for v in D.values() if not v['l1']))
# listings
lst={sid(r['zbhg_ods_apart_item.area_danji_id']):float(r['zb_daily_operating_item.open_item_cnt'] or 0) for r in L('1793632658428')}
# views
V=collections.Counter();W=collections.Counter()
for f in ['1793671188264','1793671212280','1793671222480','1793671245111']:
    for r in L(f):
        i=sid(r['zb_apart_view_wish_call.area_danji_id']);V[i]+=float(r['zb_apart_view_wish_call.view_user_cnt'] or 0);W[i]+=float(r['zb_apart_view_wish_call.wish_cnt'] or 0)
for f in ['1793671271840','1793671354075','1793671409267','1793671504205','1793671536524']:
    for r in L(f):
        i=sid(r['hg_ods_apt.zb_area_danji_id']);V[i]+=float(r['hg_apart_view_wish_call.view_user_cnt'] or 0);W[i]+=float(r['hg_apart_view_wish_call.wish_cnt'] or 0)
I=collections.Counter()
for r in L('1793632662548'): I[sid(r['zb_apart_view_wish_call.area_danji_id'])]+=float(r['zb_apart_view_wish_call.inquiry_cnt'] or 0)
for r in L('1793632667621'): I[sid(r['hg_ods_apt.zb_area_danji_id'])]+=float(r['hg_apart_view_wish_call.inquiry_cnt'] or 0)
rent=set(map(str,json.load(open('../rent.json'))['rent']))
aux=json.load(open('../aux.json'));occ=aux['occ']
for i,v in D.items():
    v['lst']=lst.get(i,0);v['view']=V.get(i,0);v['wish']=W.get(i,0);v['inq']=I.get(i,0)
    v['rent']=i in rent;o=occ.get(i);v['occ']=o[0] if o else None
json.dump(D,open('base.json','w'),ensure_ascii=False)
import statistics as st
print('rent',sum(v['rent'] for v in D.values()),'occ',collections.Counter(v['occ'] for v in D.values()))
print('view>0',sum(v['view']>0 for v in D.values()),'lst>0',sum(v['lst']>0 for v in D.values()))
print(list(D.items())[:2])
