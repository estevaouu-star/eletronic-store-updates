from pathlib import Path
import json

root = Path("app")


def read(path: str) -> str:
    return (root / path).read_text(encoding="utf-8")


def write(path: str, content: str) -> None:
    (root / path).write_text(content, encoding="utf-8")


def replace_once(content: str, old: str, new: str, label: str) -> str:
    if old not in content:
        raise SystemExit(f"Trecho não encontrado: {label}")
    return content.replace(old, new, 1)


pkg = json.loads(read("package.json"))
pkg["version"] = "10.10.30"
write("package.json", json.dumps(pkg, indent=2, ensure_ascii=False))

html = read("public/index.html")
html = replace_once(
    html,
    'id="versionInfo" class="version-info">v10.10.29',
    'id="versionInfo" class="version-info">v10.10.30',
    "versão no cabeçalho",
)
write("public/index.html", html)

server = read("src/server.ts")
server = replace_once(
    server,
    '  criadoEm:string; atualizadoEm:string;\n};\n\ntype DiagnosticoSeguranca',
    '  criadoEm:string; atualizadoEm:string;\n  prontoEm?:string; garantiaAte?:string;\n};\n\ntype DiagnosticoSeguranca',
    "datas persistidas da garantia na OS",
)
server = replace_once(
    server,
    'const now = () => new Date().toISOString();',
    '''const now = () => new Date().toISOString();
function garantiaAte101030(inicio:string){
  const start=new Date(inicio);if(Number.isNaN(start.getTime()))return inicio;
  const day=start.getDate(),end=new Date(start);end.setDate(1);end.setMonth(end.getMonth()+3);
  const lastDay=new Date(end.getFullYear(),end.getMonth()+1,0).getDate();end.setDate(Math.min(day,lastDay));return end.toISOString();
}
function garantirDatasOS101030(o:any,usarHistorico=false){
  let changed=false;
  if(!o.prontoEm&&usarHistorico&&(o.status==="Pronto"||o.status==="Entregue")){o.prontoEm=(o.status==="Pronto"?o.atualizadoEm:o.criadoEm)||o.criadoEm||o.atualizadoEm||now();changed=true}
  if(o.prontoEm&&!o.garantiaAte){o.garantiaAte=garantiaAte101030(o.prontoEm);changed=true}
  return changed;
}''',
    "cálculo imutável de três meses",
)
server = replace_once(
    server,
    '''    for (const list of [db.vendedores,db.produtos,db.clientes,db.servicos,db.ordensServico,db.diagnosticosSeguranca,db.vendas,db.movimentos,db.caixas] as any[]) {
      for (const item of list) item.lojaId ??= 1;
    }
    for(const v of db.vendas){''',
    '''    for (const list of [db.vendedores,db.produtos,db.clientes,db.servicos,db.ordensServico,db.diagnosticosSeguranca,db.vendas,db.movimentos,db.caixas] as any[]) {
      for (const item of list) item.lojaId ??= 1;
    }
    for(const o of db.ordensServico)garantirDatasOS101030(o,true);
    for(const v of db.vendas){''',
    "migração das ordens prontas antigas",
)
server = replace_once(
    server,
    '''app.get("/api/ordens-servico",auth,(_req,res)=>{
  const lojaId=lojaIdReq(_req);res.json(db.ordensServico.filter(o=>o.lojaId===lojaId).reverse());
});''',
    '''app.get("/api/ordens-servico",auth,(_req,res)=>{
  const lojaId=lojaIdReq(_req),lista=db.ordensServico.filter(o=>o.lojaId===lojaId).reverse();let changed=false;
  for(const o of lista)changed=garantirDatasOS101030(o,true)||changed;
  if(changed)salvar();res.json(lista);
});''',
    "migração após sincronização da nuvem",
)
server = replace_once(
    server,
    '  if(req.body.status!==undefined&&allowed.includes(String(req.body.status)))o.status=req.body.status;',
    '''  garantirDatasOS101030(o,true);
  if(req.body.status!==undefined&&allowed.includes(String(req.body.status))){
    const novoStatus=String(req.body.status) as OrdemServico["status"];o.status=novoStatus;
    if((novoStatus==="Pronto"||novoStatus==="Entregue")&&!o.prontoEm){o.prontoEm=now();o.garantiaAte=garantiaAte101030(o.prontoEm)}
    else garantirDatasOS101030(o,false);
  }''',
    "início da garantia ao marcar pronto",
)
write("src/server.ts", server)

js = read("public/app.js")
js = replace_once(js, 'const atual="10.10.29"', 'const atual="10.10.30"', "versão do atualizador")
js = replace_once(
    js,
    '''<div><span>Atualizada</span><b>${new Date(o.atualizadoEm).toLocaleString('pt-BR')}</b></div>''',
    '''<div><span>${o.prontoEm?'Pronto em':'Atualizada'}</span><b>${new Date(o.prontoEm||o.atualizadoEm).toLocaleString('pt-BR')}</b></div>''',
    "data de conclusão no cartão da OS",
)
js += r'''

// 10.10.30 - via da loja e garantia iniciada uma única vez quando a OS fica pronta.
function osGarantia101030(o){return o?.prontoEm&&o?.garantiaAte?{inicio:o.prontoEm,fim:o.garantiaAte}:null}
function osPodeGarantia101030(o){return ['Pronto','Entregue'].includes(o?.status)&&Boolean(osGarantia101030(o))}
function osReceipt101030(row,kind){
 const o=osAtual101025(row);if(!o)return '';
 const garantia=kind==='garantia',loja=kind==='loja',warranty=garantia?osGarantia101030(o):null;
 if(garantia&&!warranty)return '';
 const title=garantia?'VIA DE GARANTIA':loja?'VIA DA LOJA':'VIA DO CLIENTE';
 const nota=garantia?'Garantia de 3 meses contada a partir do momento em que o serviço foi marcado como pronto. A retirada ou o pagamento posterior não alteram estas datas.':loja?'Arquive esta via na loja e confira o número da OS e o aparelho com a via do cliente no momento da retirada.':'Guarde esta via e apresente-a para conferir e retirar o aparelho.';
 const assinatura=garantia?'Assinatura do funcionário':loja?'Conferência da loja / cliente':'Assinatura do cliente';
 const observacaoLoja=loja&&o.observacoes?`<div class="receipt-text"><b>Observações internas</b><br>${esc(o.observacoes)}</div>`:'';
 return `<div class="receipt receipt-structured-101025">${logoComprovante101025()}<h2>${esc(config.nomeLoja||aparencia.nomeSistema||'Eletromix')}</h2>${config.cnpj?`<p>CNPJ: ${esc(config.cnpj)}</p>`:''}${config.endereco?`<p>${esc(config.endereco)}</p>`:''}<div class="receipt-kicker">ORDEM DE SERVIÇO · ${title}</div><div class="receipt-doc-number">OS #${o.id}</div><p>Emitida em ${dataHoraRecibo101025(new Date())}</p><div class="receipt-section"><div class="receipt-section-title">CLIENTE</div>${linhaRecibo101025('Nome',o.clienteNome)}${linhaRecibo101025('Telefone',o.telefone||'Não informado')}</div><div class="receipt-section"><div class="receipt-section-title">APARELHO</div>${linhaRecibo101025('Tipo',o.aparelho)}${linhaRecibo101025('Marca',o.marca||'Não informada')}${linhaRecibo101025('Modelo',o.modelo||'Não informado')}</div><div class="receipt-section"><div class="receipt-section-title">SERVIÇO</div>${linhaRecibo101025('Serviço',o.servicoNome||'Diagnóstico')}${linhaRecibo101025('Status',o.status)}${linhaRecibo101025('Valor',money(o.valor))}<div class="receipt-text"><b>Relato do cliente</b><br>${esc(o.problemaRelatado||'Não informado')}</div>${observacaoLoja}</div>${garantia?`<div class="receipt-emphasis"><div class="receipt-section-title">GARANTIA DO SERVIÇO</div>${linhaRecibo101025('Serviço pronto em',dataHoraRecibo101025(warranty.inicio))}${linhaRecibo101025('Garantia válida até',dataHoraRecibo101025(warranty.fim))}</div>`:''}<p class="receipt-note">${nota}</p><div class="receipt-signature">${assinatura}</div></div>`;
}

syncOSPrint101020=function(){
 const section=document.querySelector('#ordensServico');if(!section)return;
 section.querySelectorAll('.os-print-actions-101015,.os-via-unica-101017').forEach(x=>x.remove());
 section.querySelectorAll('.os-print-actions-101020').forEach(box=>{if(!box.closest('.os-card-101023[data-os-id]'))box.remove()});
 osRows101015().forEach(row=>{let box=row.querySelector(':scope > .os-print-actions-101020');row.querySelectorAll('.os-print-actions-101020').forEach((x,i)=>{if(i>0)x.remove()});if(box)return;const o=osAtual101025(row);box=document.createElement('div');box.className='os-print-actions-101020';box.innerHTML='<button type="button" class="secondary os-via-cliente-101030">Via do cliente</button><button type="button" class="secondary os-via-loja-101030">Via da loja</button>'+(osPodeGarantia101030(o)?'<button type="button" class="primary os-via-garantia-101030">Via de garantia</button>':'');row.appendChild(box)});
};
async function imprimirOS101030(row,kind,button){
 const ordem=osAtual101025(row);if(!ordem)return toast('Selecione uma ordem de serviço para imprimir.');
 if(kind==='garantia'&&!osPodeGarantia101030(ordem))return toast('Marque a ordem como Pronto antes de imprimir a garantia.');
 if(osPrintInFlight101020)return toast('A impressão da OS já foi enviada. Aguarde um instante.');if(!window.desktopPrinter)return toast('Módulo de impressão do Windows não está disponível.');
 const original=button?.textContent||'',html=osReceipt101030(row,kind);if(!html)return toast('Não foi possível montar esta via.');osPrintInFlight101020=true;if(button){button.disabled=true;button.textContent='Imprimindo...'}
 try{loadPrinterSettings();const result=await window.desktopPrinter.print({html,deviceName:printerSettings.deviceName,paperWidth:printerSettings.paperWidth,itemCount:1});if(!result?.success)throw new Error(result?.failureReason||'A impressora não respondeu.');if(result.deviceName){printerSettings.deviceName=result.deviceName;savePrinterSettings()}const nomes={cliente:'Via do cliente',loja:'Via da loja',garantia:'Via de garantia'};toast(`${nomes[kind]} enviada para a impressora.`)}catch(e){console.error('[OS térmica 101030]',e);toast(`Falha ao imprimir: ${String(e?.message||e)}`)}finally{osPrintInFlight101020=false;if(button){button.disabled=false;button.textContent=original}}
}
document.addEventListener('click',event=>{const button=event.target.closest?.('.os-via-cliente-101030,.os-via-loja-101030,.os-via-garantia-101030');if(!button)return;event.preventDefault();event.stopImmediatePropagation();const kind=button.classList.contains('os-via-garantia-101030')?'garantia':button.classList.contains('os-via-loja-101030')?'loja':'cliente';imprimirOS101030(button.closest('.os-card-101023[data-os-id]'),kind,button)},true);

editOS=function(id){
 const o=ordensServico.find(x=>Number(x.id)===Number(id));if(!o)return toast('Ordem não encontrada.');
 const warranty=osGarantia101030(o),alreadyReady=['Pronto','Entregue'].includes(o.status);
 const warrantyInfo=warranty?`<div class="os-warranty-info-101030"><b>Garantia iniciada em ${dataHoraRecibo101025(warranty.inicio)}</b><span>Válida até ${dataHoraRecibo101025(warranty.fim)}. Esta data não muda no pagamento nem na retirada.</span></div>`:'';
 const readyAction=alreadyReady?'':`<button type="button" class="os-ready-101030" id="markOSReady101030">${warranty?'Marcar como pronto (mantém a garantia)':'Marcar como pronto e iniciar garantia'}</button>`;
 openModal(`Ordem de serviço #${id}`,`<div class="os-edit-summary-101023"><b>${esc(o.clienteNome)}</b><span>${esc(o.aparelho)} ${esc(o.marca||'')} ${esc(o.modelo||'')}</span><p>${esc(o.problemaRelatado||'Sem problema descrito.')}</p></div>${warrantyInfo}<form id="editOSForm101023" class="os-form-101023"><div class="form-grid"><div><label>Status</label><select name="status">${['Recebido','Em análise','Aguardando peça','Em reparo','Pronto','Entregue','Cancelada'].map(s=>`<option ${o.status===s?'selected':''}>${s}</option>`).join('')}</select></div><div><label>Serviço</label><select name="servicoId">${osServiceOptions101023(o.servicoId)}</select></div><div><label>Valor</label><input name="valor" type="number" min="0" step="0.01" value="${Number(o.valor)||0}"></div><div><label>Observações</label><input name="observacoes" value="${esc(o.observacoes||'')}"></div></div><div class="os-main-actions-101030">${readyAction}<button type="submit" class="primary os-submit-101023">Salvar alterações</button></div><div class="os-danger-actions-101023"><button type="button" class="secondary" id="cancelOS101023">Cancelar ordem</button><button type="button" class="danger" id="deleteOS101023">Excluir definitivamente</button></div></form>`);
 const form=document.querySelector('#editOSForm101023');form.onsubmit=async event=>{event.preventDefault();const button=form.querySelector('button[type="submit"]');button.disabled=true;try{const response=await api(`/api/ordens-servico/${id}`,{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify(Object.fromEntries(new FormData(form)))}),data=await response.json().catch(()=>({}));if(!response.ok)throw new Error(data.erro||'Não foi possível atualizar.');closeModal();await loadOS();toast(data.prontoEm?`Ordem atualizada. Garantia até ${dataHoraRecibo101025(data.garantiaAte)}.`:'Ordem atualizada.')}catch(e){toast(e?.message||'Erro ao atualizar ordem.');button.disabled=false}};
 const mark=document.querySelector('#markOSReady101030');if(mark)mark.onclick=async()=>{const aviso=warranty?'A garantia já iniciada será mantida sem alterar as datas.':'A data e a hora de agora iniciarão os 3 meses de garantia.';if(!confirm(`Marcar a ordem #${id} como pronta? ${aviso}`))return;mark.disabled=true;mark.textContent='Marcando como pronto...';try{const response=await api(`/api/ordens-servico/${id}`,{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify({status:'Pronto'})}),data=await response.json().catch(()=>({}));if(!response.ok)throw new Error(data.erro||'Não foi possível marcar como pronto.');closeModal();await loadOS();toast(`OS #${id} pronta. Garantia até ${dataHoraRecibo101025(data.garantiaAte)}.`)}catch(e){toast(e?.message||'Erro ao marcar como pronto.');mark.disabled=false;mark.textContent=warranty?'Marcar como pronto (mantém a garantia)':'Marcar como pronto e iniciar garantia'}};
 document.querySelector('#cancelOS101023').onclick=async()=>{if(!confirm(`Cancelar a ordem #${id}? Ela continuará no histórico.`))return;const response=await api(`/api/ordens-servico/${id}`,{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify({status:'Cancelada'})}),data=await response.json().catch(()=>({}));if(!response.ok)return toast(data.erro||'Não foi possível cancelar.');closeModal();await loadOS();toast(`Ordem #${id} cancelada.`)};
 document.querySelector('#deleteOS101023').onclick=async()=>{if(!confirm(`Excluir definitivamente a ordem #${id}? Esta ação não pode ser desfeita.`))return;const response=await api(`/api/ordens-servico/${id}`,{method:'DELETE'}),data=await response.json().catch(()=>({}));if(!response.ok)return toast(data.erro||'Não foi possível excluir.');closeModal();await loadOS();toast(`Ordem #${id} excluída.`)};
};
setTimeout(syncOSPrint101020,0);
'''
write("public/app.js", js)

css = read("public/style.css") + r'''

/* 10.10.30 - conclusão da OS e garantia fixa */
.os-main-actions-101030{display:grid;grid-template-columns:1fr 1fr;gap:9px}.os-main-actions-101030:has(>button:only-child){grid-template-columns:1fr}
.os-ready-101030{min-height:44px;border:1px solid color-mix(in srgb,#159455 65%,var(--border));border-radius:9px;background:color-mix(in srgb,#159455 13%,var(--card-bg));color:#117443;font-weight:900;cursor:pointer}
.os-ready-101030:hover{background:color-mix(in srgb,#159455 20%,var(--card-bg))}.os-ready-101030:disabled{opacity:.6;cursor:wait}
.os-warranty-info-101030{display:grid;gap:4px;margin-bottom:12px;padding:12px 14px;border:1px solid color-mix(in srgb,#159455 45%,var(--border));border-radius:11px;background:color-mix(in srgb,#159455 9%,var(--card-bg))}
.os-warranty-info-101030 b{color:#117443}.os-warranty-info-101030 span{font-size:11px;color:var(--text-muted);line-height:1.4}
@media(max-width:620px){.os-main-actions-101030{grid-template-columns:1fr}}
'''
write("public/style.css", css)

print("10.10.30: via da loja e garantia fixa iniciada ao marcar a OS como pronta.")
