# opt/v2 공통: 큐브 원본 결과(JSON) 로더와 사업부 9개 시장지역 구분.
# 원본 쿼리 결과는 커밋하지 않음. RAW_DIR 환경변수(기본: 세션 tool-results)에서 파일 이름 일부로 찾음.
import json,glob,os,collections
RAW_DIR=os.environ.get('RAW_DIR','/root/.claude/projects/-home-claude/2cc0b143-8bcb-52c0-8b96-02b78da6f48e/tool-results/')
def L(key):
    f=glob.glob(os.path.join(RAW_DIR,'*'+key+'*'))[0]; t=open(f).read()
    return json.loads(t[t.index('{'):])['data']
sid=lambda x: str(x).split('.')[0] if x is not None else None
# opt/m2b.py reg()와 동일
SA={'강남구','서초구','용산구','송파구'};SB={'성동구','마포구','광진구','양천구','영등포구','동작구','종로구','강동구','중구'}
GA={'과천시','성남시 분당구'}
GB={'성남시 수정구','하남시','용인시 수지구','광명시','성남시 중원구','수원시 영통구','안양시 동안구','의왕시','구리시','안양시 만안구','용인시 기흥구','수원시 팔달구','고양시 덕양구','고양시 일산동구','부천시 원미구','수원시 장안구','부천시 소사구','남양주시','군포시'}
MET={'부산광역시','대구광역시','대전광역시','울산광역시','세종특별자치시'}
REGIONS=['서울A','서울B','서울C','경기A','경기B','경기C','인천','5대광역시+세종','기타']
def reg(l1,l2):
    l2=l2 or ''
    if not l1: return '미확인'
    if l1=='서울특별시': return '서울A' if l2 in SA else '서울B' if l2 in SB else '서울C'
    if l1=='경기도':
        if l2 in GA: return '경기A'
        if l2 in GB or l2.startswith('화성시'): return '경기B'
        return '경기C'
    if l1=='인천광역시': return '인천'
    if l1 in MET: return '5대광역시+세종'
    if l1=='전남광주통합특별시' and l2 in ('동구','서구','남구','북구','광산구'): return '5대광역시+세종'
    return '기타'
def bucket(n):
    return '0' if n==0 else '1~2' if n<=2 else '3~9' if n<=9 else '10~29' if n<=29 else '30+'
BUCKETS=['0','1~2','3~9','10~29','30+']
