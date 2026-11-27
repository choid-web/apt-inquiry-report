# 후속 점검 빌드: python3 build.py → followup.html
import subprocess,base64,os,sys
os.chdir(os.path.dirname(os.path.abspath(__file__)))
page=open(sys.argv[1] if len(sys.argv)>1 else 'template.html').read().replace('__CSS__',open('_css.html').read())
open('chars.txt','w').write(''.join(sorted(c for c in set(page)|set('0123456789+−-.,%~·→/()') if ord(c)>=32)))
subprocess.run(['pyftsubset','../../font/PretendardVariable.woff2','--text-file=chars.txt','--flavor=woff2','--layout-features=*','--output-file=pret-sub.woff2'],check=True)
out=page.replace('__FONT__',base64.b64encode(open('pret-sub.woff2','rb').read()).decode())
OUT=sys.argv[2] if len(sys.argv)>2 else 'followup.html'
open(OUT,'w').write(out); open(OUT.replace('.html','_preview.html') if len(sys.argv)>2 else 'preview.html','w').write('<!doctype html>'+out)
print('built',len(out))
