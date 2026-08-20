from pathlib import Path
import json
root=Path('app')
def read(p): return (root/p).read_text(encoding='utf-8')
def write(p,s): (root/p).write_text(s,encoding='utf-8')
def replace1(s,a,b,label):
    if a not in s: raise RuntimeError(f'Trecho nao encontrado: {label}')
    return s.replace(a,b,1)
pkg=json.loads(read('package.json'));pkg['version']='10.10.37';write('package.json',json.dumps(pkg,indent=2,ensure_ascii=False))
html=read('public/index.html');html=replace1(html,'id="versionInfo" class="version-info">v10.10.36','id="versionInfo" class="version-info">v10.10.37','versao');write('public/index.html',html)
js=read('public/app.js');js=replace1(js,'const atual="10.10.36"','const atual="10.10.37"','atualizador');write('public/app.js',js)
print('10.10.37: build de consolidação para publicação em Releases, preservando todas as correções da 10.10.36.')
