from pathlib import Path
import json
root=Path('app')
def read(p): return (root/p).read_text(encoding='utf-8')
def write(p,s): (root/p).write_text(s,encoding='utf-8')
def replace1(s,a,b,label):
    if a not in s: raise RuntimeError(f'Trecho nao encontrado: {label}')
    return s.replace(a,b,1)

pkg=json.loads(read('package.json'));pkg['version']='10.10.43';write('package.json',json.dumps(pkg,indent=2,ensure_ascii=False))
html=read('public/index.html');html=replace1(html,'id="versionInfo" class="version-info">v10.10.42','id="versionInfo" class="version-info">v10.10.43','versao');write('public/index.html',html)
js=read('public/app.js');js=replace1(js,'const atual="10.10.42"','const atual="10.10.43"','atualizador')
server=read('src/server.ts')

# Endpoint final e simples de exclusão, independente de status.
if '/api/ordens-servico/:id/excluir-final' not in server:
    server += '''\napp.delete("/api/ordens-servico/:id/excluir-final",auth,(req,res)=>{\n  const id=Number(req.params.id),lojaId=lojaIdReq(req);\n  const index=db.ordensServico.findIndex(x=>x.lojaId===lojaId&&x.id===id);\n  if(index<0)return res.status(404).json({erro:"Ordem de serviço não encontrada."});\n  db.ordensServico.splice(index,1);salvar();\n  return res.json({ok:true,id});\n});\n'''

js += r'''

// 10.10.43 - fluxo isolado e direto para excluir OS e imprimir garantia.
async function excluirOS101043(id){
 const o=(ordensServico||[]).find(x=>Number(x.id)===Number(id));
 if(!o)return toast('Ordem de serviço não encontrada.');
 const msg=o.status==='Finalizado'
  ? `A OS #${o.id} está finalizada. Excluir definitivamente mesmo assim?`
  : `Excluir definitivamente a OS #${o.id}?`;
 if(!window.confirm(msg))return;
 try{
  const r=await api(`/api/ordens-servico/${o.id}/excluir-final`,{method:'DELETE'});
  const data=await r.json().catch(()=>({}));
  if(!r.ok||data.ok!==true)throw new Error(data.erro||'Falha ao excluir.');
  await loadOS();
  toast(`OS #${o.id} excluída.`);
 }catch(e){console.error('[OS delete 101043]',e);toast(e?.message||'Erro ao excluir OS.')}
}

async function imprimirGarantia101043(id,button){
 const o=(ordensServico||[]).find(x=>Number(x.id)===Number(id));
 if(!o)return toast('Ordem não encontrada.');
 if(!o.prontoEm||!o.garantiaAte)return toast('A garantia ainda não foi acionada.');
 const html=osViaHtml101036(o,'garantia');
 if(!html)return toast('Não foi possível montar a via de garantia.');
 const original=button?.textContent||'Imprimir garantia';
 try{
   if(button){button.disabled=true;button.textContent='Imprimindo...'}
   if(window.desktopPrinter?.print){
     loadPrinterSettings?.();
     const result=await window.desktopPrinter.print({html,deviceName:printerSettings?.deviceName,paperWidth:printerSettings?.paperWidth,itemCount:1});
     if(!result?.success)throw new Error(result?.failureReason||'A impressora não respondeu.');
     toast('Via de garantia enviada para a impressora.');
     return;
   }
   if(typeof imprimirHtmlOS101038==='function'){
     imprimirHtmlOS101038(`Garantia OS #${o.id}`,html);return;
   }
   const w=window.open('','_blank');if(!w)throw new Error('Permita a abertura da janela de impressão.');
   w.document.write(`<html><head><meta charset="utf-8"><title>Garantia OS #${o.id}</title></head><body>${html}<script>window.onload=()=>window.print()<\/script></body></html>`);w.document.close();
 }catch(e){console.error('[garantia print 101043]',e);toast(`Falha ao imprimir garantia: ${e?.message||e}`)}
 finally{if(button){button.disabled=false;button.textContent=original}}
}

function instalarAcoesOS101043(){
 document.querySelectorAll('.os-card-101023[data-os-id]').forEach(card=>{
  const id=Number(card.dataset.osId);const o=(ordensServico||[]).find(x=>Number(x.id)===id);if(!o)return;
  card.querySelectorAll('.os-delete-101039,.os-card-delete-101042,.os-card-warranty-101042').forEach(x=>x.remove());
  const footer=card.querySelector('footer');if(!footer)return;
  const printBox=card.querySelector('.os-print-actions-101020')||footer;
  if(o.prontoEm&&o.garantiaAte){
    const b=document.createElement('button');b.type='button';b.className='primary os-print-warranty-101043';b.textContent='Imprimir garantia';b.onclick=(ev)=>{ev.preventDefault();ev.stopPropagation();imprimirGarantia101043(id,b)};printBox.appendChild(b);
  }
  const del=document.createElement('button');del.type='button';del.className='danger os-delete-final-101043';del.textContent='Excluir OS';del.onclick=(ev)=>{ev.preventDefault();ev.stopPropagation();excluirOS101043(id)};footer.appendChild(del);
 });
}

const renderOSBase101043=renderOS;
renderOS=function(){renderOSBase101043();setTimeout(instalarAcoesOS101043,0)};
setTimeout(instalarAcoesOS101043,0);
'''
write('public/app.js',js);write('src/server.ts',server)
print('10.10.43: exclusão de qualquer OS e impressão de garantia refeitas com fluxo isolado.')
