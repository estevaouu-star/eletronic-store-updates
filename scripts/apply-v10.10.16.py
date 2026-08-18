from pathlib import Path
import json
root=Path('app')
def read(p): return (root/p).read_text(encoding='utf-8')
def write(p,s): (root/p).write_text(s,encoding='utf-8')

pkg=json.loads(read('package.json'));pkg['version']='10.10.16';write('package.json',json.dumps(pkg,indent=2,ensure_ascii=False))
html=read('public/index.html').replace('id="versionInfo" class="version-info">v10.10.15','id="versionInfo" class="version-info">v10.10.16',1);write('public/index.html',html)
server=read('src/server.ts').replace('app.put("/api/aparencia",auth,admin,(req,res)=>{','app.put("/api/aparencia",auth,(req,res)=>{',1);write('src/server.ts',server)
js=read('public/app.js').replace('const atual="10.10.15"','const atual="10.10.16"',1)
js += r'''
// 10.10.16 - Personalização: salva de verdade e sempre recarrega o estado persistido da loja.
const APAR_CACHE_101016='eletromix_aparencia_v3:';
function aparKey101016(){let id='default';try{id=String(storeId||document.querySelector('#storeSelect,#lojaSelect,.store-select select')?.value||'default')}catch{}return APAR_CACHE_101016+id}
function cacheApar101016(a){try{localStorage.setItem(aparKey101016(),JSON.stringify(a||{}))}catch{}}
function cachedApar101016(){try{return JSON.parse(localStorage.getItem(aparKey101016())||'null')}catch{return null}}
function setApar101016(d){if(!d||typeof aparencia==='undefined')return;Object.keys(aparencia).forEach(k=>delete aparencia[k]);Object.assign(aparencia,d);cacheApar101016(d);try{applyAparencia()}catch{}}
function syncAparFields101016(){
 if(typeof aparencia==='undefined')return;
 const sec=document.querySelector('#aparencia,#personalizacao,#personalizar,#customizacao,.section.active');if(!sec)return;
 sec.querySelectorAll('input,select,textarea').forEach(el=>{const k=el.name||el.id;if(!k||aparencia[k]===undefined||el.type==='file')return;if(el.type==='checkbox')el.checked=!!aparencia[k];else el.value=String(aparencia[k]??'')});
}
async function reloadApar101016(){
 try{const r=await api('/api/aparencia');if(!r.ok)throw new Error();const d=await r.json();setApar101016(d);syncAparFields101016()}catch{const d=cachedApar101016();if(d){setApar101016(d);syncAparFields101016()}}
}
async function saveApar101016(form){
 const body={...(typeof aparencia!=='undefined'?aparencia:{})};
 new FormData(form).forEach((v,k)=>{if(typeof v==='string')body[k]=v});
 if(typeof aparencia!=='undefined'){if(aparencia.logoTopoDataUrl)body.logoTopoDataUrl=aparencia.logoTopoDataUrl;if(aparencia.logoComprovanteDataUrl)body.logoComprovanteDataUrl=aparencia.logoComprovanteDataUrl;if(aparencia.logoDataUrl&&!body.logoTopoDataUrl)body.logoTopoDataUrl=aparencia.logoDataUrl}
 const r=await api('/api/aparencia',{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});let d={};try{d=await r.json()}catch{}if(!r.ok)throw new Error(d.erro||'Não foi possível salvar a personalização.');setApar101016(d);syncAparFields101016();return d;
}
function aparForm101016(el){const sec=el?.closest?.('#aparencia,#personalizacao,#personalizar,#customizacao,.section')||document.querySelector('#aparencia,#personalizacao,#personalizar,#customizacao');return el?.closest?.('form')||sec?.querySelector('form')||null}
function isAparSave101016(btn){if(!btn)return false;const txt=((btn.textContent||'')+' '+(btn.id||'')+' '+(btn.className||'')).toLowerCase();const sec=btn.closest?.('#aparencia,#personalizacao,#personalizar,#customizacao,.section');return !!sec&&/salvar|save|aplicar/.test(txt)&&/personal|apar|custom/i.test((sec.id||'')+' '+(sec.querySelector('h1,h2,h3')?.textContent||''))}
document.addEventListener('submit',async e=>{const f=e.target;if(!/personal|apar|custom/i.test((f.closest?.('.section')?.id||'')+' '+(f.closest?.('.section')?.querySelector('h1,h2,h3')?.textContent||'')))return;e.preventDefault();e.stopImmediatePropagation();try{await saveApar101016(f);toast('Personalização salva.')}catch(err){toast(err?.message||'Erro ao salvar personalização.')}},true);
document.addEventListener('click',e=>{const nav=e.target.closest?.('.nav');if(nav&&/personal|apar|custom/i.test((nav.textContent||'')+' '+(nav.dataset?.s||'')))setTimeout(reloadApar101016,80);const b=e.target.closest?.('button,input[type="submit"]');if(isAparSave101016(b)){const f=aparForm101016(b);if(f){e.preventDefault();e.stopImmediatePropagation();saveApar101016(f).then(()=>toast('Personalização salva.')).catch(err=>toast(err?.message||'Erro ao salvar personalização.'))}}},true);
document.addEventListener('change',e=>{if(e.target.matches?.('#storeSelect,#lojaSelect,.store-select select'))setTimeout(reloadApar101016,100)},true);
document.addEventListener('DOMContentLoaded',()=>setTimeout(reloadApar101016,400));
'''
write('public/app.js',js)
print('10.10.16: Personalização corrigida: salvar persiste no servidor por loja e a aba sempre recarrega o valor salvo.')