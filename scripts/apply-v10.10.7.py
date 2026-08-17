from pathlib import Path
import json,re
root=Path('app')
def read(p): return (root/p).read_text(encoding='utf-8')
def write(p,s): (root/p).write_text(s,encoding='utf-8')
pkg=json.loads(read('package.json'));pkg['version']='10.10.7';write('package.json',json.dumps(pkg,indent=2,ensure_ascii=False))
html=read('public/index.html').replace('id="versionInfo" class="version-info">v10.10.6','id="versionInfo" class="version-info">v10.10.7',1);write('public/index.html',html)
js=read('public/app.js').replace('const atual="10.10.6"','const atual="10.10.7"',1)
js += r'''
// 10.10.7 - categorias rolaveis, remove somente contador quebrado e persiste sessao de verdade.
function fixCategorias10107(){
 const caixa=document.querySelector('#caixa');if(!caixa)return;
 const title=[...caixa.querySelectorAll('h1,h2,h3,h4,h5,h6,strong,b,div,span')].find(e=>(e.textContent||'').trim()==='Categorias');
 if(!title)return;
 let box=title.parentElement;
 // sobe ate um container que contenha os botoes de categoria, sem pegar o catalogo inteiro
 for(let i=0;i<3&&box?.parentElement;i++){if(box.querySelectorAll('button').length>=4)break;box=box.parentElement}
 if(box){box.classList.add('categorias-scroll-10107');}
}
function removeContadorQuebrado10107(){
 const sec=document.querySelector('#produtos');if(!sec)return;
 // Mantem #filtroInfoProdutoBtn funcional. Remove apenas OUTRO controle/texto "Faltando informacao (N)".
 [...sec.querySelectorAll('button,a,span,label,div')].forEach(el=>{
   if(el.id==='filtroInfoProdutoBtn'||el.closest?.('#filtroInfoProdutoBtn'))return;
   const t=(el.textContent||'').replace(/\s+/g,' ').trim();
   if(/^Faltando informa(?:ç|c)(?:ão|ao)\s*\(\s*\d+\s*\)$/i.test(t)){
     const nested=el.querySelectorAll?.('button,a')?.length||0;
     if(!nested)el.remove();
   }
 });
}
// Sessao persistente: salva token+usuario, nao senha. Reabre direto enquanto a versao for a mesma.
const sessao10107='es_session_10107';
function saveSession10107(){if(!me||!token)return;try{localStorage.setItem(sessao10107,JSON.stringify({version:atual,token,me,storeId:storeId||null}))}catch(e){console.error('[session save]',e)}}
function clearSession10107(){localStorage.removeItem(sessao10107)}
const showAppBase10107=showApp;showApp=function(){showAppBase10107();saveSession10107();setTimeout(fixCategorias10107,30)};
// Sobrescreve o logout final para apagar sessao somente quando o usuario realmente clicar em Sair.
const logoutBase10107=logout;logout=function(callApi=true){if(callApi)clearSession10107();return logoutBase10107(callApi)};
async function restoreSession10107(){
 if(me)return true;let s=null;try{s=JSON.parse(localStorage.getItem(sessao10107)||'null')}catch{clearSession10107();return false}
 if(!s||s.version!==atual||!s.token||!s.me){clearSession10107();return false}
 token=s.token;me=s.me;if(s.storeId)storeId=s.storeId;
 try{
   // valida o token no servidor antes de liberar o app
   await api('/api/lojas');
   showApp();await loadStores();await loadAll();return true;
 }catch(e){console.warn('[session restore]',e);token='';me=null;clearSession10107();return false}
}
document.addEventListener('DOMContentLoaded',()=>setTimeout(restoreSession10107,60));setTimeout(restoreSession10107,180);setTimeout(restoreSession10107,650);
document.addEventListener('click',e=>{if(e.target.closest?.('.nav[data-s="produtos"]'))setTimeout(removeContadorQuebrado10107,40);if(e.target.closest?.('.nav[data-s="caixa"]'))setTimeout(fixCategorias10107,40)},true);
new MutationObserver(()=>{removeContadorQuebrado10107();fixCategorias10107()}).observe(document.documentElement,{childList:true,subtree:true});
setTimeout(removeContadorQuebrado10107,500);setTimeout(fixCategorias10107,500);
'''
write('public/app.js',js)
css=read('public/style.css')+r'''
/* 10.10.7 - scroll SOMENTE dentro das categorias */
#caixa .categorias-scroll-10107{max-height:176px!important;overflow-y:auto!important;overflow-x:hidden!important;overscroll-behavior:contain!important;scrollbar-width:thin!important;padding-right:4px!important}
#caixa .categorias-scroll-10107::-webkit-scrollbar{width:7px}#caixa .categorias-scroll-10107::-webkit-scrollbar-thumb{background:#ffffff2b;border-radius:8px}
'''
write('public/style.css',css)
print('10.10.7: categorias com scroll interno; contador Faltando informacao (N) removido sem tocar no filtro funcional; sessao persistida por token ate atualizar ou clicar Sair.')