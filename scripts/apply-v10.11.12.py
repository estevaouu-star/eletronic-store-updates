from pathlib import Path
import json,re
root=Path('app')
def read(p): return (root/p).read_text(encoding='utf-8')
def write(p,s): (root/p).write_text(s,encoding='utf-8')

pkg=json.loads(read('package.json'));pkg['version']='10.11.12';write('package.json',json.dumps(pkg,indent=2,ensure_ascii=False))
html=read('public/index.html');html,n=re.subn(r'(id="versionInfo" class="version-info">v)[0-9.]+',r'\g<1>10.11.12',html,count=1)
if n!=1: raise SystemExit('versao html nao encontrada')
write('public/index.html',html)

js=read('public/app.js');js,n=re.subn(r'const atual="[0-9.]+"(?=,status=)','const atual="10.11.12"',js,count=1)
if n!=1: raise SystemExit('versao atualizador nao encontrada')

# Corrige a causa real do relogin: a 10.10.11 passou a FUNCAO ORIGINAL diretamente
# para tres setTimeout. Esses callbacks guardaram a referencia antiga antes da 10.11.10
# substituir autoLogin101011, entao ignoravam o bloqueio e relogavam logo apos Sair.
old='setTimeout(autoLogin101011,180);setTimeout(autoLogin101011,700);setTimeout(autoLogin101011,1600);'
new='setTimeout(()=>autoLogin101011(),180);setTimeout(()=>autoLogin101011(),700);setTimeout(()=>autoLogin101011(),1600);'
if old not in js: raise SystemExit('timers diretos do auto-login nao encontrados')
js=js.replace(old,new,1)

# Defesa dentro da funcao ORIGINAL: mesmo uma referencia antiga ja capturada para imediatamente
# se o usuario tiver clicado em Sair.
needle='async function autoLogin101011(){\n if(autoLogin101011Running||me||!window.eletromixRemember101011)return false;'
replacement='async function autoLogin101011(){\n try{if(localStorage.getItem("eletromix_manual_logout_101110")==="1")return false}catch{}\n if(autoLogin101011Running||me||!window.eletromixRemember101011)return false;'
if needle not in js: raise SystemExit('funcao autoLogin101011 original nao encontrada')
js=js.replace(needle,replacement,1)

# Submit sintetico nao pode reativar auto-login. Somente o envio real feito pelo usuario.
old_submit="document.addEventListener('submit',e=>{\n    if(e.target?.matches?.('#loginForm'))liberarLogout101110();\n  },true);"
new_submit="document.addEventListener('submit',e=>{\n    if(e.target?.matches?.('#loginForm') && e.isTrusted)liberarLogout101110();\n  },true);"
if old_submit not in js: raise SystemExit('liberacao do logout 10.11.10 nao encontrada')
js=js.replace(old_submit,new_submit,1)

write('public/app.js',js)
print('10.11.12: corrige a referencia antiga capturada pelos timers de auto-login e impede relogin apos Sair.')
