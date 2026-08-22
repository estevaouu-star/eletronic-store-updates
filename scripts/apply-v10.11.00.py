from pathlib import Path
import json
root=Path('app')
def read(p): return (root/p).read_text(encoding='utf-8')
def write(p,s): (root/p).write_text(s,encoding='utf-8')
def rep(s,a,b):
 if a not in s: raise RuntimeError(f'nao encontrado: {a}')
 return s.replace(a,b,1)
pkg=json.loads(read('package.json'));pkg['version']='10.11.0';write('package.json',json.dumps(pkg,indent=2,ensure_ascii=False))
html=read('public/index.html');html=rep(html,'id="versionInfo" class="version-info">v10.10.52','id="versionInfo" class="version-info">v10.11.00');write('public/index.html',html)
js=read('public/app.js');js=rep(js,'const atual="10.10.52"','const atual="10.11.0"')
# Mantém integralmente a correção 10.10.52 já aplicada: modelo/serviço/ciência/assinatura priorizados e garantia intacta.
write('public/app.js',js)
print('10.11.00 pronta para release com layout compacto aprovado como alvo.')
