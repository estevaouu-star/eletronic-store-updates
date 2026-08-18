from pathlib import Path
import json
root=Path('app')
def read(p): return (root/p).read_text(encoding='utf-8')
def write(p,s): (root/p).write_text(s,encoding='utf-8')

pkg=json.loads(read('package.json'));pkg['version']='10.10.18';write('package.json',json.dumps(pkg,indent=2,ensure_ascii=False))
html=read('public/index.html').replace('id="versionInfo" class="version-info">v10.10.17','id="versionInfo" class="version-info">v10.10.18',1);write('public/index.html',html)

# Causa real do "salva e volta": a rota de aparência continuava bloqueada para vendedor.
# Vendedor pode fazer tudo dentro da loja permitida, então ele também pode salvar a personalização dessa loja.
server=read('src/server.ts')
old='app.put("/api/aparencia",auth,admin,(req,res)=>{'
if old not in server: raise RuntimeError('Rota PUT /api/aparencia com bloqueio admin não encontrada')
server=server.replace(old,'app.put("/api/aparencia",auth,(req,res)=>{',1)
write('src/server.ts',server)

js=read('public/app.js').replace('const atual="10.10.17"','const atual="10.10.18"',1)
js += r'''
// 10.10.18 - depois de salvar Personalização, confirma o que ficou persistido no servidor.
async function confirmarPersonalizacao101018(){
 try{
   const r=await api('/api/aparencia');
   if(!r.ok){const d=await r.json().catch(()=>({}));throw new Error(d.erro||'Falha ao recarregar personalização.');}
   const salva=await r.json();aparencia={...aparencia,...salva};
   if(typeof applyAparencia==='function')applyAparencia();
   return true;
 }catch(e){console.error('[personalizacao 101018]',e);try{toast(e.message||'Falha ao confirmar personalização.')}catch{}return false}
}
function secPersonalizacao101018(){
 const nav=[...document.querySelectorAll('.nav')].find(n=>/personaliza/i.test(n.textContent||''));
 const id=nav?.dataset?.s;return (id&&document.getElementById(id))||document.querySelector('#personalizacao,#aparencia,#customizacao');
}
document.addEventListener('click',e=>{
 const sec=secPersonalizacao101018(),btn=e.target.closest?.('button,input[type="submit"]');if(!sec||!btn||!sec.contains(btn))return;
 const t=((btn.textContent||'')+' '+(btn.value||'')+' '+(btn.id||'')).toLowerCase();if(!/salvar|aplicar/.test(t))return;
 setTimeout(async()=>{if(await confirmarPersonalizacao101018())try{toast('Personalização salva na loja.')}catch{}},350);
},true);
'''
write('public/app.js',js)
print('10.10.18: vendedor pode salvar aparência da própria loja e o app confirma a persistência no servidor.')