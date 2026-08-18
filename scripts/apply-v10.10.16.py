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
// 10.10.16 - Personalização: usa o mesmo helper api() do aplicativo e persiste por loja.
function aparForm101016(el){return el?.closest?.('form')||el?.closest?.('#aparencia,#personalizacao,#personalizar,#customizacao,.section')?.querySelector('form')||null}
function aparSection101016(el){return el?.closest?.('#aparencia,#personalizacao,#personalizar,#customizacao,.section')||null}
function isApar101016(sec){return !!sec&&/personal|apar|custom/i.test((sec.id||'')+' '+(sec.querySelector('h1,h2,h3')?.textContent||''))}
function fillApar101016(){
 const sec=document.querySelector('#aparencia,#personalizacao,#personalizar,#customizacao,.section.active');if(!sec||!isApar101016(sec)||typeof aparencia==='undefined')return;
 sec.querySelectorAll('input,select,textarea').forEach(el=>{const k=el.name||el.id;if(!k||!(k in aparencia)||el.type==='file')return;if(el.type==='checkbox')el.checked=!!aparencia[k];else el.value=String(aparencia[k]??'')});
}
async function reloadApar101016(){try{const d=await api('/api/aparencia');if(d&&typeof d==='object'){aparencia={...aparencia,...d};applyAparencia();fillApar101016()}}catch(e){console.error('[aparencia reload]',e)}}
async function saveApar101016(form){
 const body={...aparencia};new FormData(form).forEach((v,k)=>{if(typeof v==='string')body[k]=v});
 // Campos sem name também entram pelo id.
 form.querySelectorAll('input[id],select[id],textarea[id]').forEach(el=>{if(el.type!=='file'&&el.id)body[el.id]=el.type==='checkbox'?el.checked:el.value});
 if(aparencia.logoTopoDataUrl)body.logoTopoDataUrl=aparencia.logoTopoDataUrl;if(aparencia.logoComprovanteDataUrl)body.logoComprovanteDataUrl=aparencia.logoComprovanteDataUrl;
 const d=await api('/api/aparencia',{method:'PUT',body:JSON.stringify(body)});aparencia={...aparencia,...d};applyAparencia();fillApar101016();return d;
}
document.addEventListener('click',e=>{
 const nav=e.target.closest?.('.nav');if(nav&&/personal|apar|custom/i.test((nav.textContent||'')+' '+(nav.dataset?.s||'')))setTimeout(reloadApar101016,80);
 const b=e.target.closest?.('button,input[type="submit"]');if(!b)return;const sec=aparSection101016(b);const txt=((b.textContent||'')+' '+(b.id||'')+' '+(b.className||'')).toLowerCase();
 if(isApar101016(sec)&&/salvar|save|aplicar/.test(txt)){const f=aparForm101016(b);if(!f)return;e.preventDefault();e.stopImmediatePropagation();saveApar101016(f).then(()=>toast('Personalização salva.')).catch(err=>{console.error(err);toast(err?.message||'Erro ao salvar personalização.')})}
},true);
document.addEventListener('submit',e=>{const f=e.target,sec=aparSection101016(f);if(!isApar101016(sec))return;e.preventDefault();e.stopImmediatePropagation();saveApar101016(f).then(()=>toast('Personalização salva.')).catch(err=>toast(err?.message||'Erro ao salvar personalização.'))},true);
'''
write('public/app.js',js)
print('10.10.16: personalizacao salva via PUT real e recarrega do servidor por loja.')