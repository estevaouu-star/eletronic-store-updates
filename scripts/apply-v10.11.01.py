from pathlib import Path
import json,re
root=Path('app')
def read(p): return (root/p).read_text(encoding='utf-8')
def write(p,s): (root/p).write_text(s,encoding='utf-8')
def rep(s,a,b):
    if a not in s: raise RuntimeError(f'nao encontrado: {a}')
    return s.replace(a,b,1)

pkg=json.loads(read('package.json'));pkg['version']='10.11.1';write('package.json',json.dumps(pkg,indent=2,ensure_ascii=False))
html=read('public/index.html')
html=html.replace('id="versionInfo" class="version-info">v10.11.00','id="versionInfo" class="version-info">v10.11.01',1)
write('public/index.html',html)

server=read('src/server.ts')
# Política 10.11.01: qualquer usuário autenticado pode usar todas as rotas,
# exceto gestão de usuários/login, que permanece auth+admin.
pat=re.compile(r'app\.(get|post|put|delete)\("([^"]+)",auth,admin,')
def unlock(m):
    method,path=m.group(1),m.group(2)
    if path.startswith('/api/usuarios'):
        return m.group(0)
    return f'app.{method}("{path}",auth,'
server,n=pat.subn(unlock,server)
write('src/server.ts',server)

js=read('public/app.js')
js=js.replace('const atual="10.11.0"','const atual="10.11.1"',1)
js += r'''

// 10.11.01 - ADM exclusivo apenas para gestão de login/usuários.
// Demais ações devem ficar disponíveis para qualquer usuário autenticado.
function liberarAcoesGerais101101(){
 const areaUsuarios=(el)=>Boolean(el?.closest?.('#usuariosTable,#usuariosBody,.access-head-actions,[data-user-management],.user-management,.access-management'));
 document.querySelectorAll('[data-admin-only],.admin-only,[data-role="admin"]').forEach(el=>{
   if(areaUsuarios(el))return;
   el.hidden=false;
   el.removeAttribute('hidden');
   el.removeAttribute('aria-hidden');
   el.classList.remove('admin-only');
   if('disabled' in el)el.disabled=false;
   el.style.removeProperty('display');
   el.style.removeProperty('visibility');
   el.style.removeProperty('pointer-events');
   el.style.removeProperty('opacity');
 });
 // Botões comuns que versões antigas possam ter desabilitado por cargo.
 document.querySelectorAll('button:disabled,a[aria-disabled="true"],input:disabled,select:disabled').forEach(el=>{
   if(areaUsuarios(el))return;
   const txt=(el.textContent||el.getAttribute('title')||el.getAttribute('aria-label')||'').toLowerCase();
   if(/login|usu[aá]rio|acesso|senha/.test(txt))return;
   el.disabled=false;el.removeAttribute('aria-disabled');
 });
}
const permissoesObserver101101=new MutationObserver(()=>liberarAcoesGerais101101());
document.addEventListener('DOMContentLoaded',()=>setTimeout(liberarAcoesGerais101101,100));
setTimeout(()=>{liberarAcoesGerais101101();permissoesObserver101101.observe(document.documentElement,{childList:true,subtree:true,attributes:true,attributeFilter:['hidden','disabled','class','style']})},500);
'''
write('public/app.js',js)
print(f'10.11.01: {n} rotas ADM revisadas; usuarios permanecem exclusivos de ADM.')
