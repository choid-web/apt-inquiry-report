import json,glob,collections,statistics as st
TD='/root/.claude/projects/-home-claude/2cc0b143-8bcb-52c0-8b96-02b78da6f48e/tool-results/'
k='zb_naver_mapped_items.'
O=collections.defaultdict(list);P=collections.Counter()
ids=set(json.load(open('o3_ids.json')));seen=set()
for f in ['1793698960558','1793698972735','1793698984835','1793698996978','1793699009169','1793699021345']:
    t=open(glob.glob(TD+'*'+f+'.txt')[0]).read();d=json.loads(t[t.index('{'):])['data']
    for r in d:
        i=str(r[k+'area_danji_id']).split('.')[0];seen.add(i);a=r[k+'unique_article_cnt'] or 0
        if r[k+'has_pro_product']=='Y': P[i]+=1
        else: O[i].append(a)
M=json.load(open('m2b.json'));U=M['U']
rows=[]
for i in ids:
    o=sorted(O.get(i,[]),reverse=True)
    rows.append(dict(id=i,top1=o[0] if o else 0,top3=sum(o[:3]),noff=len(o),nlst=sum(o),pro=P.get(i,0),view=U[i]['view'],lst=U[i]['lst']))
rows.sort(key=lambda r:(-r['top3'],-r['view']))
print('universe',len(rows),'with naver',sum(r['noff']>0 for r in rows),'seen',len(seen&ids))
top=rows[:500]
print('top500 top3 min',top[-1]['top3'],'median top3',st.median(r['top3'] for r in top),'median top1',st.median(r['top1'] for r in top))
H=set(str(r['id']) for r in json.load(open('../top518.json')))
print('overlap H',sum(r['id'] in H for r in top))
json.dump(rows,open('o3_rows.json','w'))
print(top[:5])
