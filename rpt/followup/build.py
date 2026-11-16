# 후속 점검 빌드: python3 build.py → followup.html
import subprocess,base64,os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
page=open('template.html').read().replace('__CSS__',open('_css.html').read())
open('chars.txt','w').write(''.join(sorted(c for c in set(page)|set('0123456789+−-.,%~·→/()') if ord(c)>=32)))
subprocess.run(['pyftsubset','../../font/PretendardVariable.woff2','--text-file=chars.txt','--flavor=woff2','--layout-features=*','--output-file=pret-sub.woff2'],check=True)
out=page.replace('__FONT__',base64.b64encode(open('pret-sub.woff2','rb').read()).decode())
open('followup.html','w').write(out); open('preview.html','w').write('<!doctype html>'+out)
print('built',len(out))
