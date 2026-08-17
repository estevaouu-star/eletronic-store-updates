from pathlib import Path
import json,re
root=Path('app')
def read(p): return (root/p).read_text(encoding='utf-8')
def write(p,s): (root/p).write_text(s,encoding='utf-8')

pkg=json.loads(read('package.json'));pkg['version']='10.10.6';write('package.json',json.dumps(pkg,indent=2,ensure_ascii=False))
html=read('public/index.html').replace('id="versionInfo" class="version-info">v10.10.5','id="versionInfo" class="version-info">v10.10.6',1);write('public/index.html',html)

js=read('public/app.js').replace('const atual="10.10.5"','const atual="10.10.6"',1)
js += r'''
// 10.10.6 - permissao do vendedor por loja, login persistente real e filtro Faltando informacoes funcional.

// Vendedor usa o sistema completo. A restricao de lojas continua vindo do backend (/api/lojas + x-store-id autorizado).
// Nao escondemos telas operacionais por cargo; o vendedor simplesmente nao recebe lojas fora da permissao dele.
const showAppBase10106=showApp;
showApp=function(){
  showAppBase10106();
  document.querySelectorAll('.admin-only').forEach(el=>{el.style.removeProperty('display');el.removeAttribute('hidden')});
  // O seletor de loja continua limitado ao que /api/lojas devolve para o usuario.
  const sel=document.querySelector('#storeSelect');
  if(sel&&me?.cargo!=='admin'&&sel.options.length===1){sel.disabled=true;sel.title='Este acesso está limitado a esta loja.'}else if(sel){sel.disabled=false;sel.removeAttribute('title')}
};

// Corrige o que a 10.10.5 fez ao trocar o filtro funcional pelo filtro de status.
function produtoIncompleto10106(p){
  return !String(p?.codigo||'').trim()||!String(p?.nome||'').trim()||!String(p?.categoria||'').trim()||!String(p?.marca||'').trim()||!String(p?.codigoBarras||'').trim()||!(Number(p?.precoVenda)>0);
}
function fixProdutos10106(){
  const sec=document.querySelector('#produtos');if(!sec)return;
  // tira o filtro que entrou no lugar errado
  const status=document.querySelector('#filtroStatusProduto');if(status)status.style.display='none';
  // neutraliza a rotina 10.9.6 que apagava o botao correto em cada mutation
  try{removerUiAntiga1096=function(){const old=document.querySelector('#checkoutFloat');if(old)old.remove();const oldBtn=document.querySelector('#openCheckout');if(oldBtn)oldBtn.remove()}}catch{}
  let b=document.querySelector('#filtroInfoProdutoBtn');
  if(!b){
    const toolbar=sec.querySelector('.toolbar')||sec.querySelector('.filters')||sec.querySelector('form')||sec.querySelector('.card')||sec.firstElementChild;
    if(!toolbar)return;
    b=document.createElement('button');b.id='filtroInfoProdutoBtn';b.type='button';b.className='secondary small';b.textContent='Faltando informações';toolbar.appendChild(b);
  }
  b.style.removeProperty('display');b.disabled=false;b.classList.toggle('active',!!produtosSomenteIncompletos);
}
// A logica de filtro ja existe desde 10.9.5; esta versao garante o botao certo e liga o clique diretamente.
document.addEventListener('click',e=>{const b=e.target.closest?.('#filtroInfoProdutoBtn');if(!b)return;e.preventDefault();e.stopImmediatePropagation();produtosSomenteIncompletos=!produtosSomenteIncompletos;try{produtosPagina=1}catch{};b.classList.toggle('active',produtosSomenteIncompletos);renderProdutos()},true);
try{fixProdutos10105=fixProdutos10106}catch{}
document.addEventListener('click',e=>{if(e.target.closest?.('.nav[data-s="produtos"]'))setTimeout(fixProdutos10106,40)},true);setTimeout(fixProdutos10106,300);setTimeout(fixProdutos10106,900);

// Login persistente: a 10.10.5 redefinia start depois que start() podia ja ter sido chamado.
// Aqui o auto-login roda por conta propria sempre que a tela de login aparecer.
let autoLogin10106Running=false;
async function autoLogin10106(){
  if(autoLogin10106Running||me)return;
  if(localStorage.getItem('es_remember_version')!==atual)return;
  const u=localStorage.getItem('es_remember_login'),p=localStorage.getItem('es_remember_pass');if(!u||!p)return;
  const screen=document.querySelector('#loginScreen');if(screen?.classList.contains('hidden'))return;
  autoLogin10106Running=true;
  try{
    const lu=document.querySelector('#login'),lp=document.querySelector('#senha');if(lu)lu.value=u;if(lp)lp.value=p;
    await login({preventDefault(){}});
  }catch(err){console.error('[auto-login10106]',err)}finally{autoLogin10106Running=false}
}
document.addEventListener('DOMContentLoaded',()=>setTimeout(autoLogin10106,180));
setTimeout(autoLogin10106,450);setTimeout(autoLogin10106,1200);
new MutationObserver(()=>{if(!me)setTimeout(autoLogin10106,40)}).observe(document.documentElement,{subtree:true,attributes:true,attributeFilter:['class']});

// Atualizador: usa diretamente a bridge Electron; nao depende da aba atual.
forceUpdate10105=async function(){
 const btns=[document.querySelector('#updateButton'),document.querySelector('#loginUpdateButton')].filter(Boolean);
 btns.forEach(b=>{b.disabled=true;b.dataset.prev10106=b.textContent;b.textContent='Verificando atualização...'});
 try{
   if(window.electronAPI?.checkForUpdates){
     const r=await window.electronAPI.checkForUpdates();
     // algumas versoes da bridge retornam estado, outras apenas disparam os eventos do updater
     if(r?.downloaded&&window.electronAPI?.installUpdate)await window.electronAPI.installUpdate();
     else if(r?.available&&window.electronAPI?.downloadUpdate)await window.electronAPI.downloadUpdate();
     return;
   }
   if(window.desktopUpdater?.check){await window.desktopUpdater.check();return}
   window.open('https://github.com/estevaouu-star/eletronic-store-updates/releases/latest','_blank');
 }catch(err){console.error('[update10106]',err);window.open('https://github.com/estevaouu-star/eletronic-store-updates/releases/latest','_blank')}
 finally{setTimeout(()=>btns.forEach(b=>{b.disabled=false;b.textContent=b.dataset.prev10106||'Atualizar'}),1800)}
};
'''
write('public/app.js',js)

css=read('public/style.css')+r'''
/* 10.10.6 */
#filtroStatusProduto{display:none!important}#filtroInfoProdutoBtn{display:inline-flex!important;align-items:center!important;white-space:nowrap}#filtroInfoProdutoBtn.active{background:var(--accent)!important;color:#fff!important;border-color:var(--accent)!important}
'''
write('public/style.css',css)
print('10.10.6: vendedor com acesso operacional completo dentro das lojas permitidas; login persistente corrigido; Faltando informacoes restaurado e filtro de status removido; atualizador reforcado.')