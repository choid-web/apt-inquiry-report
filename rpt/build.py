# 리포트 빌드: python3 build.py  → apt-inquiry-report.html, preview.html
import subprocess,base64,os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
t=open('template.html').read(); dd=open('data.json').read().replace('</','<\\/')
page=t.replace('__DATA__',dd)
open('chars.txt','w').write(''.join(sorted(c for c in set(page)|set('0123456789+−-.,%~·→/()[]÷ABCDEFGHYN') if ord(c)>=32)))
subprocess.run(['pyftsubset','../font/PretendardVariable.woff2','--text-file=chars.txt','--flavor=woff2','--layout-features=*','--output-file=pret-sub.woff2'],check=True)
out=page.replace('__FONT__',base64.b64encode(open('pret-sub.woff2','rb').read()).decode())
open('apt-inquiry-report.html','w').write(out); open('preview.html','w').write('<!doctype html>'+out)
print('built',len(out))
