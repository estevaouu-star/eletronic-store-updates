from pathlib import Path
import json
root=Path('app')
def read(p): return (root/p).read_text(encoding='utf-8')
def write(p,s): (root/p).write_text(s,encoding='utf-8')
pkg=json.loads(read('package.json'));pkg['version']='10.10.9';write('package.json',json.dumps(pkg,indent=2,ensure_ascii=False))
html=read('public/index.html').replace('id="versionInfo" class="version-info">v10.10.8','id="versionInfo" class="version-info">v10.10.9',1);write('public/index.html',html)
js=read('public/app.js').replace('const atual="10.10.8"','const atual="10.10.9"',1)
js += r'''
// 10.10.9 - sessão persistente estável entre versões do patch e reinícios.
// A chave 10.10.7 anterior ficava presa à versão e a restauração era disparada tarde demais.
const sessaoPersistente10109='eletromix_session';
function gravarSessao10109(){
 if(!token||!me)return;
 try{localStorage.setItem(sessaoPersistente10109,JSON.stringify({token,me,storeId:storeId||null,savedAt:Date.now()}))}catch(e){console.error('[session109 save]',e)}
}
function apagarSessao10109(){try{localStorage.removeItem(sessaoPersistente10109);localStorage.removeItem('es_session_10107')}catch{}}
function migrarSessao10109(){
 try{
  if(localStorage.getItem(sessaoPersistente10109))return;
  const antiga=JSON.parse(localStorage.getItem('es_session_10107')||'null');
  if(antiga?.token&&antiga?.me)localStorage.setItem(sessaoPersistente10109,JSON.stringify({token:antiga.token,me:antiga.me,storeId:antiga.storeId||null,savedAt:Date.now()}));
 }catch{}
}
const showAppBase10109=showApp;showApp=function(){showAppBase10109();gravarSessao10109()};
// Clique explícito em Sair é a única ação normal que apaga a lembrança local.
document.addEventListener('click',e=>{const b=e.target.closest?.('#logoutBtn,[data-action="logout"],.logout-btn');if(b)apagarSessao10109()},true);
async function restaurarSessao10109(){
 if(me&&token){gravarSessao10109();return true}
 migrarSessao10109();let s=null;try{s=JSON.parse(localStorage.getItem(sessaoPersistente10109)||'null')}catch{apagarSessao10109();return false}
 if(!s?.token||!s?.me)return false;
 token=s.token;me=s.me;if(s.storeId)storeId=s.storeId;
 try{
   // endpoint autenticado: confirma que o backend restaurou o token persistido.
   await api('/api/lojas');
   showApp();await loadStores();await loadAll();return true;
 }catch(e){
   console.warn('[session109 restore]',e);token='';me=null;apagarSessao10109();return false;
 }
}
// Executa cedo e novamente depois do bootstrap legado, que pode limpar as variáveis em memória.
migrarSessao10109();
document.addEventListener('DOMContentLoaded',()=>restaurarSessao10109());
setTimeout(restaurarSessao10109,50);setTimeout(restaurarSessao10109,350);setTimeout(restaurarSessao10109,1200);
'''
write('public/app.js',js)
print('10.10.9: sessão usa chave estável, migra token anterior, salva após login e restaura após o bootstrap.')