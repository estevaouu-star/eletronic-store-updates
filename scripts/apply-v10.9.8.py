from pathlib import Path
import json
root=Path('app')
def read(p): return (root/p).read_text(encoding='utf-8')
def write(p,s): (root/p).write_text(s,encoding='utf-8')
pkg=json.loads(read('package.json'));pkg['version']='10.9.8';write('package.json',json.dumps(pkg,indent=2,ensure_ascii=False))
html=read('public/index.html').replace('id="versionInfo" class="version-info">v10.9.7','id="versionInfo" class="version-info">v10.9.8',1);write('public/index.html',html)
js=read('public/app.js').replace('const atual="10.9.7"','const atual="10.9.8"',1)
# 10.9.7 procurava qualquer elemento que CONTIVESSE o texto Venda Rapida. Isso podia escolher
# o container principal do app e substituir seu innerHTML inteiro durante o boot/login.
old="function vr1097FindPanel(){return [...document.querySelectorAll('section,dialog,.modal,.card,.panel,[role=\"dialog\"]')].find(n=>/venda r[aá]pida/i.test(n.textContent||''))||null}"
new="function vr1097FindPanel(){const nodes=[...document.querySelectorAll('dialog,.modal,[role=\"dialog\"],section,.panel,.card')];const matches=nodes.filter(n=>/venda r[aá]pida/i.test(n.textContent||'')&&!n.matches('#app,#loginScreen,body,html')&&!n.querySelector('#loginForm'));if(!matches.length)return null;return matches.sort((a,b)=>(a.textContent||'').length-(b.textContent||'').length)[0]}"
if old not in js: raise RuntimeError('vr1097FindPanel nao encontrado')
js=js.replace(old,new,1)
# Nunca reconstrua nada enquanto login estiver visivel ou app oculto.
old2="function rebuildVendaRapida1097(){\n const p=vr1097FindPanel();if(!p||p.dataset.vr1097==='1')return;p.dataset.vr1097='1';p.classList.add('vr1097-root');"
new2="function rebuildVendaRapida1097(){\n const app=document.querySelector('#app'),login=document.querySelector('#loginScreen');if(!app||app.classList.contains('hidden')||(login&&!login.classList.contains('hidden')))return;const p=vr1097FindPanel();if(!p||p.dataset.vr1097==='1'||p.contains(document.querySelector('#loginForm')))return;p.dataset.vr1097='1';p.classList.add('vr1097-root');"
if old2 not in js: raise RuntimeError('rebuildVendaRapida1097 nao encontrado')
js=js.replace(old2,new2,1)
write('public/app.js',js)
print('10.9.8: corrige Cannot set properties of null apos login; Venda Rapida nao pode mais substituir o container do app.')