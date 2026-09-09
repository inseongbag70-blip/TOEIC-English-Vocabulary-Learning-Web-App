"""같은 형식의 TOEIC 단어 PDF에서 단어 데이터를 다시 추출하는 보조 스크립트."""
import json, re, sys, os
try:
    import pypdf
except ImportError:
    print('pypdf가 필요합니다. pip install pypdf')
    raise
pdf = sys.argv[1] if len(sys.argv)>1 else '토익-단어장-PDF-for-PC-A4size-All(2).pdf'
out = sys.argv[2] if len(sys.argv)>2 else 'data/words.json'
r=pypdf.PdfReader(pdf)
text='\n'.join((p.extract_text() or '') for p in r.pages)
pat=re.compile(r'^\s*(\d+)\s+([A-Za-z][A-Za-z-]*)\s+\1\s+(.*)$',re.M)
d={}
for n,w,m in pat.findall(text):
    d[int(n)]={'number':int(n),'word':w,'meaning':re.sub(r'\s+',' ',m).strip()}
# PDF의 683번 accommodation은 텍스트 추출에서 줄바꿈으로 분리되는 경우가 있어 보정
if 683 not in d:
    d[683]={'number':683,'word':'accommodations','meaning':'(명) 숙박 시설'}
words=[d[k] for k in sorted(d)]
os.makedirs(os.path.dirname(out) or '.',exist_ok=True)
json.dump(words,open(out,'w',encoding='utf-8'),ensure_ascii=False,indent=2)
print(f'{len(words)}개 단어 저장: {out}')
