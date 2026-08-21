from pathlib import Path
import json
root=Path('app')
def read(p): return (root/p).read_text(encoding='utf-8')
def write(p,s): (root/p).write_text(s,encoding='utf-8')
def replace1(s,a,b,label):
    if a not in s: raise RuntimeError(f'Trecho nao encontrado: {label}')
    return s.replace(a,b,1)

pkg=json.loads(read('package.json'));pkg['version']='10.10.42';write('package.json',json.dumps(pkg,indent=2,ensure_ascii=False))
html=read('public/index.html');html=replace1(html,'id="versionInfo" class="version-info">v10.10.41','id="versionInfo" class="version-info">v10.10.42','versao');write('public/index.html',html)
js=read('public/app.js');js=replace1(js,'const atual="10.10.41"','const atual="10.10.42"','atualizador')
server=read('src/server.ts')

anchor='''app.delete("/api/ordens-servico/:id",auth,(req,res)=>{\n  const index=db.ordensServico.findIndex(x=>x.lojaId===lojaIdReq(req)&&x.id===Number(req.params.id));\n  if(index<0)return res.status(404).json({erro:"Ordem de serviço não encontrada."});\n  const [removida]=db.ordensServico.splice(index,1);salvar();res.json({ok:true,id:removida.id});\n});'''
if anchor not in server: raise RuntimeError('Endpoint DELETE de OS nao encontrado')
extra=anchor+'''\n\napp.delete("/api/ordens-servico/:id/excluir",auth,(req,res)=>{\n  const id=Number(req.params.id),lojaId=lojaIdReq(req);\n  const index=db.ordensServico.findIndex(x=>x.lojaId===lojaId&&x.id===id);\n  if(index<0)return res.status(404).json({erro:"Ordem de serviço não encontrada."});\n  const [removida]=db.ordensServico.splice(index,1);\n  salvar();\n  return res.json({ok:true,id:removida.id});\n});'''
server=server.replace(anchor,extra,1)

js += r'''

// 10.10.42 - garantia fora do Abrir/Atualizar + exclusão independente e impressão direta.
async function excluirOS101042(id){
 const o=(ordensServico||[]).find(x=>Number(x.id)===Number(id));
 if(!o)return toast('Ordem de serviço não encontrada.');
 const aviso=o.status==='Finalizado'
   ? `ATENÇÃO: a OS #${o.id} está FINALIZADA. Ela será removida definitivamente do histórico. Deseja excluir?`
   : `Excluir definitivamente a OS #${o.id} de ${o.clienteNome}?`;
 if(!confirm(aviso))return;
 try{
   const r=await api(`/api/ordens-servico/${o.id}/excluir`,{method:'DELETE'});
   const data=await r.json().catch(()=>({}));
   if(!r.ok||data.ok!==true)throw new Error(data.erro||'Não foi possível excluir a ordem.');
   ordensServico=(ordensServico||[]).filter(x=>Number(x.id)!==Number(o.id));
   renderOS();
   toast(`OS #${o.id} excluída definitivamente.`);
 }catch(e){console.error('[excluir OS 101042]',e);toast(e?.message||'Erro ao excluir a ordem de serviço.')}
}

async function imprimirGarantia101042(o,button){
 if(!o)return toast('Ordem não encontrada.');
 if(!osGarantiaAtiva101041(o))return toast('Acione a garantia antes de imprimir.');
 const html=osViaHtml101036(o,'garantia');
 if(!html)return toast('Não foi possível montar a via de garantia.');
 const original=button?.textContent||'Imprimir garantia';
 if(button){button.disabled=true;button.textContent='Imprimindo...'}
 try{
   if(window.desktopPrinter){
     loadPrinterSettings();
     const result=await window.desktopPrinter.print({html,deviceName:printerSettings.deviceName,paperWidth:printerSettings.paperWidth,itemCount:1});
     if(!result?.success)throw new Error(result?.failureReason||'A impressora não respondeu.');
     if(result.deviceName){printerSettings.deviceName=result.deviceName;savePrinterSettings()}
     toast('Via de garantia enviada para a impressora.');
     return;
   }
   if(typeof imprimirHtmlOS101038==='function'){
     imprimirHtmlOS101038(`Garantia OS #${o.id}`,html);
     return;
   }
   visualizarVia101036(o,'garantia');
 }catch(e){console.error('[garantia 101042]',e);toast(`Falha ao imprimir garantia: ${String(e?.message||e)}`)}
 finally{if(button){button.disabled=false;button.textContent=original}}
}

const renderOSBase101042=renderOS;
renderOS=function(){
 renderOSBase101042();
 document.querySelectorAll('.os-card-101023[data-os-id]').forEach(card=>{
   const o=(ordensServico||[]).find(x=>Number(x.id)===Number(card.dataset.osId));if(!o)return;
   const footer=card.querySelector('footer');if(!footer)return;
   card.querySelectorAll('.os-card-warranty-101042,.os-card-delete-101042').forEach(x=>x.remove());
   const actions=card.querySelector('.os-print-actions-101020')||footer;
   if(osGarantiaAtiva101041(o)){
     const warranty=document.createElement('button');warranty.type='button';warranty.className='primary os-card-warranty-101042';warranty.dataset.warrantyOs101042=String(o.id);warranty.textContent='Imprimir garantia';actions.appendChild(warranty);
   }
   const del=document.createElement('button');del.type='button';del.className='danger os-card-delete-101042';del.dataset.deleteOs101042=String(o.id);del.textContent='Excluir OS';footer.appendChild(del);
   card.querySelectorAll('.os-delete-101039').forEach(b=>b.style.display='none');
 });
};

const editOSBase101042=editOS;
editOS=function(id){
 editOSBase101042(id);
 setTimeout(()=>{
   const o=(ordensServico||[]).find(x=>Number(x.id)===Number(id));if(!o)return;
   const form=document.querySelector('#editOSForm101023');if(!form)return;
   const area=form.querySelector('.os-warranty-actions-101041');
   if(area&&osGarantiaAtiva101041(o))area.innerHTML=`<span><b>Garantia acionada</b><br>${dataHoraRecibo101025(o.prontoEm)} até ${dataHoraRecibo101025(o.garantiaAte)}.<br>A impressão fica disponível no cartão da OS.</span>`;
   const oldDel=form.querySelector('#deleteOS101041');if(oldDel)oldDel.style.display='none';
   let del=form.querySelector('#deleteOS101042');if(!del){del=document.createElement('button');del.type='button';del.id='deleteOS101042';del.className='danger';del.textContent='Excluir definitivamente';form.appendChild(del)}
   del.onclick=()=>excluirOS101042(Number(o.id));
 },0);
};

document.addEventListener('click',e=>{
 const warranty=e.target?.closest?.('[data-warranty-os-101042]');
 if(warranty){e.preventDefault();e.stopImmediatePropagation();const o=(ordensServico||[]).find(x=>Number(x.id)===Number(warranty.dataset.warrantyOs101042));if(o)imprimirGarantia101042(o,warranty);return}
 const del=e.target?.closest?.('[data-delete-os-101042]');
 if(del){e.preventDefault();e.stopImmediatePropagation();excluirOS101042(Number(del.dataset.deleteOs101042));return}
},true);
'''
write('public/app.js',js);write('src/server.ts',server)
print('10.10.42: imprimir garantia no cartão com impressão direta e exclusão de OS por endpoint dedicado.')
