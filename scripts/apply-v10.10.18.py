from pathlib import Path
import json
root=Path('app')
def read(p): return (root/p).read_text(encoding='utf-8')
def write(p,s): (root/p).write_text(s,encoding='utf-8')

pkg=json.loads(read('package.json'));pkg['version']='10.10.18';write('package.json',json.dumps(pkg,indent=2,ensure_ascii=False))
html=read('public/index.html').replace('id="versionInfo" class="version-info">v10.10.17','id="versionInfo" class="version-info">v10.10.18',1);write('public/index.html',html)

# Personalização: vendedor também salva a aparência da própria loja.
server=read('src/server.ts')
old='app.put("/api/aparencia",auth,admin,(req,res)=>{'
if old in server: server=server.replace(old,'app.put("/api/aparencia",auth,(req,res)=>{',1)
write('src/server.ts',server)

js=read('public/app.js').replace('const atual="10.10.17"','const atual="10.10.18"',1)
js += r'''
// 10.10.18 - confirma a Personalização realmente salva no servidor da loja.
async function confirmarPersonalizacao101018(){
 try{const r=await api('/api/aparencia');if(!r.ok){const d=await r.json().catch(()=>({}));throw new Error(d.erro||'Falha ao recarregar personalização.')}const salva=await r.json();aparencia={...aparencia,...salva};if(typeof applyAparencia==='function')applyAparencia();return true}catch(e){console.error('[personalizacao 101018]',e);try{toast(e.message||'Falha ao confirmar personalização.')}catch{}return false}
}
function secPersonalizacao101018(){const nav=[...document.querySelectorAll('.nav')].find(n=>/personaliza/i.test(n.textContent||''));const id=nav?.dataset?.s;return (id&&document.getElementById(id))||document.querySelector('#personalizacao,#aparencia,#customizacao')}
document.addEventListener('click',e=>{const sec=secPersonalizacao101018(),btn=e.target.closest?.('button,input[type="submit"]');if(!sec||!btn||!sec.contains(btn))return;const t=((btn.textContent||'')+' '+(btn.value||'')+' '+(btn.id||'')).toLowerCase();if(!/salvar|aplicar/.test(t))return;setTimeout(async()=>{if(await confirmarPersonalizacao101018())try{toast('Personalização salva na loja.')}catch{}},350)},true);

// 10.10.18 - desfaz a unificação errada da 10.10.17.
// Via cliente e Via garantia ficam SEPARADAS e usam desktopPrinter, o mesmo motor do comprovante.
try{
 unificarBotoesOS101017=function(){
   document.querySelectorAll('.os-via-unica-101017,.os-print-actions-101015').forEach(x=>x.remove());
   if(typeof injectOSPrint101016==='function')injectOSPrint101016();
 };
}catch{}
function corrigirOS101018(){
 document.querySelectorAll('.os-via-unica-101017,.os-print-actions-101015').forEach(x=>x.remove());
 if(typeof injectOSPrint101016==='function')injectOSPrint101016();
}
document.addEventListener('click',e=>{if(e.target.closest?.('.nav[data-s="ordens"],.nav[data-s="ordensServico"],.nav[data-s="ordens-servico"]'))setTimeout(corrigirOS101018,120)},true);
new MutationObserver(()=>{const sec=typeof osSec101015==='function'?osSec101015():null;if(sec?.classList.contains('active'))setTimeout(corrigirOS101018,0)}).observe(document.documentElement,{childList:true,subtree:true});
document.addEventListener('DOMContentLoaded',()=>setTimeout(corrigirOS101018,500));setTimeout(corrigirOS101018,1200);
'''
write('public/app.js',js)
css=read('public/style.css')+r'''
/* 10.10.18 */
.os-via-unica-101017{display:none!important}
'''
write('public/style.css',css)
print('10.10.18: Personalização persiste por loja; Via cliente e Via garantia ficam separadas e imprimem pelo mesmo motor térmico do comprovante.')