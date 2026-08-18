from pathlib import Path
import json,re
root=Path('app')
def read(p): return (root/p).read_text(encoding='utf-8')
def write(p,s): (root/p).write_text(s,encoding='utf-8')

pkg=json.loads(read('package.json'));pkg['version']='10.10.16';write('package.json',json.dumps(pkg,indent=2,ensure_ascii=False))
html=read('public/index.html').replace('id="versionInfo" class="version-info">v10.10.15','id="versionInfo" class="version-info">v10.10.16',1);write('public/index.html',html)

# Personalização deve obedecer à regra geral: vendedor pode tudo dentro da própria loja.
server=read('src/server.ts')
server,n=re.subn(r'app\.put\("/api/aparencia",auth,admin,\(req,res\)=>\{','app.put("/api/aparencia",auth,(req,res)=>{',server,count=1)
if n!=1: raise RuntimeError('Rota de aparência protegida por admin não encontrada')
write('src/server.ts',server)

js=read('public/app.js').replace('const atual="10.10.15"','const atual="10.10.16"',1)
js += r'''
// 10.10.16 - Personalização: salva de verdade no backend da loja e confirma lendo novamente.
function aparForm101016(el){return el?.closest?.('form')||el?.closest?.('#aparencia,#personalizacao,#personalizar,#customizacao,.section')?.querySelector('form')||null}
function aparSection101016(el){return el?.closest?.('#aparencia,#personalizacao,#personalizar,#customizacao,.section')||null}
function isApar101016(sec){return !!sec&&/personal|apar|custom/i.test((sec.id||'')+' '+(sec.querySelector('h1,h2,h3')?.textContent||''))}
function fillApar101016(){
 const sec=document.querySelector('#aparencia,#personalizacao,#personalizar,#customizacao,.section.active');if(!sec||!isApar101016(sec)||typeof aparencia==='undefined')return;
 sec.querySelectorAll('input,select,textarea').forEach(el=>{const k=el.name||el.id;if(!k||!(k in aparencia)||el.type==='file')return;if(el.type==='checkbox')el.checked=!!aparencia[k];else el.value=String(aparencia[k]??'')});
}
async function aparJson101016(url,opts){
 const r=await api(url,opts);const d=await r.json().catch(()=>({}));if(!r.ok)throw new Error(d.erro||`Erro ${r.status}`);return d;
}
async function reloadApar101016(){
 try{const d=await aparJson101016('/api/aparencia');aparencia={...aparencia,...d};applyAparencia();fillApar101016();return d}catch(e){console.error('[aparencia reload]',e);throw e}
}
async function saveApar101016(form){
 const body={...aparencia};
 new FormData(form).forEach((v,k)=>{if(typeof v==='string')body[k]=v});
 form.querySelectorAll('input[id],select[id],textarea[id]').forEach(el=>{if(el.type!=='file'&&el.id&&el.id in aparencia)body[el.id]=el.type==='checkbox'?el.checked:el.value});
 // As imagens são carregadas para aparencia antes do clique em salvar.
 if(aparencia.logoTopoDataUrl!==undefined)body.logoTopoDataUrl=aparencia.logoTopoDataUrl;
 if(aparencia.logoComprovanteDataUrl!==undefined)body.logoComprovanteDataUrl=aparencia.logoComprovanteDataUrl;
 const salvo=await aparJson101016('/api/aparencia',{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
 aparencia={...aparencia,...salvo};applyAparencia();
 // Confirma o valor persistido no servidor. O botão só mostra sucesso depois dessa leitura.
 const confirmado=await aparJson101016('/api/aparencia');aparencia={...aparencia,...confirmado};applyAparencia();fillApar101016();
 return confirmado;
}
document.addEventListener('click',e=>{
 const nav=e.target.closest?.('.nav');if(nav&&/personal|apar|custom/i.test((nav.textContent||'')+' '+(nav.dataset?.s||'')))setTimeout(()=>reloadApar101016().catch(()=>{}),80);
 const b=e.target.closest?.('button,input[type="submit"]');if(!b)return;const sec=aparSection101016(b);const txt=((b.textContent||'')+' '+(b.value||'')+' '+(b.id||'')+' '+(b.className||'')).toLowerCase();
 if(isApar101016(sec)&&/salvar|save|aplicar/.test(txt)){const f=aparForm101016(b);if(!f)return;e.preventDefault();e.stopImmediatePropagation();saveApar101016(f).then(()=>toast('Personalização salva.')).catch(err=>{console.error(err);toast(err?.message||'Erro ao salvar personalização.')})}
},true);
document.addEventListener('submit',e=>{const f=e.target,sec=aparSection101016(f);if(!isApar101016(sec))return;e.preventDefault();e.stopImmediatePropagation();saveApar101016(f).then(()=>toast('Personalização salva.')).catch(err=>{console.error(err);toast(err?.message||'Erro ao salvar personalização.')})},true);
'''
write('public/app.js',js)
print('10.10.16: personalização salva via PUT com JSON correto, liberada por loja e confirmada por GET após salvar.')