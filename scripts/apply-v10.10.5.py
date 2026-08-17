from pathlib import Path
import json,re
root=Path('app')
def read(p): return (root/p).read_text(encoding='utf-8')
def write(p,s): (root/p).write_text(s,encoding='utf-8')
pkg=json.loads(read('package.json'));pkg['version']='10.10.5';write('package.json',json.dumps(pkg,indent=2,ensure_ascii=False))
html=read('public/index.html').replace('id="versionInfo" class="version-info">v10.10.4','id="versionInfo" class="version-info">v10.10.5',1);write('public/index.html',html)
js=read('public/app.js').replace('const atual="10.10.4"','const atual="10.10.5"',1)
js += r'''
// 10.10.5 - consolidacao: abas, produtos, atualizador e login lembrado por versao.
function fixSections10105(){
 const secs=[...document.querySelectorAll('.section')];
 let active=secs.find(s=>s.classList.contains('active'));
 if(!active){const nav=document.querySelector('.nav.active[data-s]');active=nav?document.querySelector('#'+nav.dataset.s):null;if(active)active.classList.add('active')}
 secs.forEach(s=>{const on=s===active;s.hidden=!on;s.setAttribute('aria-hidden',on?'false':'true');s.style.setProperty('display',on?(s.id==='caixa'?'flex':'block'):'none','important')});
 document.body.classList.toggle('caixa-mode-10103',active?.id==='caixa');
}
document.addEventListener('click',e=>{const nav=e.target.closest?.('.nav[data-s]');if(nav){setTimeout(fixSections10105,0);setTimeout(fixSections10105,80)}},true);
new MutationObserver(fixSections10105).observe(document.documentElement,{subtree:true,attributes:true,attributeFilter:['class']});
setTimeout(fixSections10105,100);setTimeout(fixSections10105,700);

// Produtos: remove definitivamente o botao quebrado "Faltando informacao" e preserva/restaura o filtro de status que funcionava.
function fixProdutos10105(){
 document.querySelector('#filtroInfoProdutoBtn')?.remove();
 const sec=document.querySelector('#produtos');if(!sec)return;
 let st=document.querySelector('#filtroStatusProduto');
 if(!st){
   const toolbar=sec.querySelector('.toolbar')||sec.querySelector('.filters')||sec.querySelector('form')||sec.firstElementChild;
   if(toolbar){st=document.createElement('select');st.id='filtroStatusProduto';st.innerHTML='<option value="">Todos os status</option><option value="ativo">Ativos</option><option value="inativo">Inativos</option>';toolbar.appendChild(st);st.addEventListener('change',()=>{try{produtosPagina=1}catch{};typeof renderProdutosReset==='function'?renderProdutosReset():renderProdutos()})}
 }
 if(st){st.style.removeProperty('display');st.disabled=false}
}
document.addEventListener('click',e=>{if(e.target.closest?.('.nav[data-s="produtos"]'))setTimeout(fixProdutos10105,30)},true);setTimeout(fixProdutos10105,500);

// Atualizador independente das abas. Se o bridge automatico nao existir, abre a release mais recente como fallback.
async function forceUpdate10105(){
 const btns=[document.querySelector('#updateButton'),document.querySelector('#loginUpdateButton')].filter(Boolean);btns.forEach(b=>{b.disabled=true;b.dataset.prev=b.textContent;b.textContent='Verificando atualização...'});
 try{
   if(window.electronAPI?.checkForUpdates){await window.electronAPI.checkForUpdates();return}
   if(window.desktopUpdater?.check){await window.desktopUpdater.check();return}
   window.open('https://github.com/estevaouu-star/eletronic-store-updates/releases/latest','_blank');
 }catch(err){console.error('[update10105]',err);window.open('https://github.com/estevaouu-star/eletronic-store-updates/releases/latest','_blank')}
 finally{setTimeout(()=>btns.forEach(b=>{b.disabled=false;if(b.dataset.prev)b.textContent=b.dataset.prev}),2500)}
}
document.addEventListener('click',e=>{if(e.target.closest?.('#updateButton,#loginUpdateButton')){e.preventDefault();e.stopImmediatePropagation();forceUpdate10105()}},true);

// Lembra a conta neste computador enquanto a versao nao mudar. A atualizacao força novo login.
const rememberVersion10105='es_remember_version',rememberLogin10105='es_remember_login',rememberPass10105='es_remember_pass';
function clearRemember10105(){localStorage.removeItem(rememberLogin10105);localStorage.removeItem(rememberPass10105);localStorage.setItem(rememberVersion10105,atual)}
if(localStorage.getItem(rememberVersion10105)&&localStorage.getItem(rememberVersion10105)!==atual){localStorage.removeItem('es_token');clearRemember10105()}
const loginBase10105=login;
login=async function(e){
 const user=document.querySelector('#login')?.value||'',pass=document.querySelector('#senha')?.value||'';
 await loginBase10105(e);
 if(me&&token){localStorage.setItem(rememberVersion10105,atual);localStorage.setItem(rememberLogin10105,user);localStorage.setItem(rememberPass10105,pass)}
};
const startBase10105=start;
start=async function(){
 try{await startBase10105()}catch(err){console.error(err)}
 if(me||localStorage.getItem(rememberVersion10105)!==atual)return;
 const u=localStorage.getItem(rememberLogin10105),p=localStorage.getItem(rememberPass10105);if(!u||!p)return;
 const lu=document.querySelector('#login'),lp=document.querySelector('#senha');if(lu)lu.value=u;if(lp)lp.value=p;
 try{await login({preventDefault(){}})}catch(err){console.error('[auto-login10105]',err)}
};
// Sair manualmente continua sendo sair de verdade.
const logoutBase10105=logout;
logout=function(callApi=true){if(callApi)clearRemember10105();return logoutBase10105(callApi)};
'''
write('public/app.js',js)
css=read('public/style.css')+r'''
/* 10.10.5 regras finais */
.section[aria-hidden="true"],.section[hidden]{display:none!important}.section[aria-hidden="false"]{visibility:visible!important;opacity:1!important}#filtroInfoProdutoBtn{display:none!important}#filtroStatusProduto{display:inline-block!important;visibility:visible!important;opacity:1!important}
'''
write('public/style.css',css)
print('10.10.5: abas consolidadas, Faltando informacao removido, filtro status restaurado, atualizador com fallback e login lembrado ate a proxima versao.')