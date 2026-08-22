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

# BACKEND: ADM só é necessário em /api/usuarios. Todo o restante exige apenas usuário logado.
server=read('src/server.ts')
pat=re.compile(r'app\.(get|post|put|delete|patch)\("([^"]+)",auth,admin,')
def unlock(m):
    method,path=m.group(1),m.group(2)
    if path.startswith('/api/usuarios'):
        return m.group(0)
    return f'app.{method}("{path}",auth,'
server,n=pat.subn(unlock,server)
write('src/server.ts',server)

# FRONTEND: remove verificações de cargo que bloqueiem funções comuns.
# Gestão de usuário/login/senha/acesso continua intacta e exclusiva de ADM.
js=read('public/app.js')
js=js.replace('const atual="10.11.0"','const atual="10.11.1"',1)
protected=('usuario','usuário','usuarios','usuários','login','senha','acesso','novousuario','editusuario','loadusuarios','editmeuacesso')
unlocked=0
new_lines=[]
for line in js.splitlines():
    low=line.lower()
    if 'admin' in low and 'cargo' in low and not any(k in low for k in protected):
        before=line
        line=re.sub(r'me\?\.cargo\s*===?\s*["\']admin["\']','true',line)
        line=re.sub(r'me\?\.cargo\s*!==?\s*["\']admin["\']','false',line)
        line=re.sub(r'me\.cargo\s*===?\s*["\']admin["\']','true',line)
        line=re.sub(r'me\.cargo\s*!==?\s*["\']admin["\']','false',line)
        if line!=before: unlocked+=1
    new_lines.append(line)
js='\n'.join(new_lines)+'\n'

js += r'''

// 10.11.01 - ADM exclusivo apenas para gestão de login/usuários.
function liberarAcoesGerais101101(){
 const areaUsuarios=(el)=>Boolean(el?.closest?.('#usuariosTable,#usuariosBody,.access-head-actions,[data-user-management],.user-management,.access-management'));
 document.querySelectorAll('[data-admin-only],.admin-only,[data-role="admin"],.only-admin').forEach(el=>{
   if(areaUsuarios(el))return;
   const txt=(el.textContent||el.getAttribute('title')||el.getAttribute('aria-label')||'').toLowerCase();
   if(/login|usu[aá]rio|acesso|senha/.test(txt))return;
   el.hidden=false;el.removeAttribute('hidden');el.removeAttribute('aria-hidden');
   el.classList.remove('admin-only','only-admin');
   if('disabled' in el)el.disabled=false;
   el.removeAttribute('disabled');el.removeAttribute('aria-disabled');
   el.style.removeProperty('display');el.style.removeProperty('visibility');el.style.removeProperty('pointer-events');el.style.removeProperty('opacity');
 });
 document.querySelectorAll('button:disabled,a[aria-disabled="true"],input:disabled,select:disabled').forEach(el=>{
   if(areaUsuarios(el))return;
   const txt=(el.textContent||el.getAttribute('title')||el.getAttribute('aria-label')||'').toLowerCase();
   if(/login|usu[aá]rio|acesso|senha/.test(txt))return;
   el.disabled=false;el.removeAttribute('disabled');el.removeAttribute('aria-disabled');
 });
}
const permissoesObserver101101=new MutationObserver(()=>liberarAcoesGerais101101());
document.addEventListener('DOMContentLoaded',()=>setTimeout(liberarAcoesGerais101101,100));
setTimeout(()=>{liberarAcoesGerais101101();permissoesObserver101101.observe(document.documentElement,{childList:true,subtree:true,attributes:true,attributeFilter:['hidden','disabled','class','style']})},500);
'''
write('public/app.js',js)
print(f'10.11.01: {n} rotas comuns liberadas e {unlocked} verificacoes visuais removidas; /api/usuarios permanece ADM.')
