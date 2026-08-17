from pathlib import Path
import json

root=Path('app')
def read(p): return (root/p).read_text(encoding='utf-8')
def write(p,s): (root/p).write_text(s,encoding='utf-8')
def must(s,a,b,label):
    if a not in s: raise RuntimeError(f'Trecho nao encontrado: {label}')
    return s.replace(a,b,1)

pkg=json.loads(read('package.json'))
pkg['version']='10.8.1'
write('package.json',json.dumps(pkg,indent=2,ensure_ascii=False))

html=read('public/index.html')
html=html.replace('id="versionInfo" class="version-info">v10.8.0','id="versionInfo" class="version-info">v10.8.1')
write('public/index.html',html)

js=read('public/app.js')
js=js.replace('const atual="10.8.0"','const atual="10.8.1"')
write('public/app.js',js)

main=read('electron/main.cjs')
# A 10.8.0 colocou os escapes PowerShell `r e `n dentro de um template literal JavaScript.
# O caractere ` encerrou o template literal e impediu o Electron de iniciar.
# Usa [char]13/[char]10, que produz o mesmo resultado no PowerShell sem nenhum backtick no JS.
old='''    $msg=([string]$_.Exception.Message).Replace("`r",' ').Replace("`n",' ')'''
new='''    $msg=([string]$_.Exception.Message).Replace([char]13,' ').Replace([char]10,' ')'''
main=must(main,old,new,'escape PowerShell que quebrava o main.cjs')
write('electron/main.cjs',main)

print('Patch 10.8.1 aplicado: corrigido SyntaxError da 10.8.0 sem remover corte, clareamento da logo ou otimizações de impressão.')
