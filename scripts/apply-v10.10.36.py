from pathlib import Path
import json,re

root=Path('app')
def read(p): return (root/p).read_text(encoding='utf-8')
def write(p,s): (root/p).write_text(s,encoding='utf-8')
def replace1(s,a,b,label):
    if a not in s: raise RuntimeError(f'Trecho nao encontrado: {label}')
    return s.replace(a,b,1)

# versão
pkg=json.loads(read('package.json'));pkg['version']='10.10.36';write('package.json',json.dumps(pkg,indent=2,ensure_ascii=False))
html=read('public/index.html');html=replace1(html,'id="versionInfo" class="version-info">v10.10.35','id="versionInfo" class="version-info">v10.10.36','versao');write('public/index.html',html)
js=read('public/app.js');js=replace1(js,'const atual="10.10.35"','const atual="10.10.36"','atualizador')
server=read('src/server.ts')

# -------- servidor: novos status, migração, garantia e bloqueio --------
# amplia o tipo final da OS sem depender da ordem exata dos patches anteriores
server=server.replace('status:"Recebido"|"Em análise"|"Aguardando peça"|"Em reparo"|"Pronto"|"Entregue"|"Cancelada";',
'''status:"Acabou de chegar"|"Esperando técnico consertar"|"Pago"|"Finalizado"|"Cancelada"|"Recebido"|"Em análise"|"Aguardando peça"|"Em reparo"|"Pronto"|"Entregue";''',1)
if 'finalizadoEm?:string;' not in server:
    server=server.replace('prontoEm?:string; garantiaAte?:string;','prontoEm?:string; garantiaAte?:string; finalizadoEm?:string;',1)

# status padrão em novas OS
server=server.replace('status:"Recebido"','status:"Acabou de chegar"',1)

# migração segura dos status antigos ao carregar a base
anchor='''    for(const o of db.ordensServico)garantirDatasOS101030(o,true);'''
if anchor in server and 'migrarStatusOS101036' not in server:
    helper='''    const migrarStatusOS101036=(o:any)=>{\n      const mapa:any={"Recebido":"Acabou de chegar","Em análise":"Esperando técnico consertar","Aguardando peça":"Esperando técnico consertar","Em reparo":"Esperando técnico consertar","Pronto":"Esperando técnico consertar","Entregue":"Pago"};\n      if(mapa[o.status])o.status=mapa[o.status];\n    };\n    for(const o of db.ordensServico){garantirDatasOS101030(o,true);migrarStatusOS101036(o)};'''
    server=server.replace(anchor,helper,1)

# allowed da edição
server=re.sub(r'const allowed=\[[^\]]+\];',
'''const allowed=["Acabou de chegar","Esperando técnico consertar","Pago","Finalizado","Cancelada"];''',server,count=1)

# bloqueio forte no PUT de OS finalizada
put_anchor='''app.put("/api/ordens-servico/:id",auth,(req,res)=>{'''
if put_anchor in server and 'OS_FINALIZADA_101036' not in server:
    pos=server.find(put_anchor)+len(put_anchor)
    # injeta depois da localização de o; fazemos pela primeira linha que encontra a ordem dentro do handler
    tail=server[pos:]
    m=re.search(r'(\n\s*const o=db\.ordensServico\.find\([^\n]+\);\s*\n\s*if\(!o\)return res\.status\(404\)[^\n]+;)',tail)
    if not m: raise RuntimeError('Localizacao da OS no PUT nao encontrada')
    block=m.group(1)+'''\n  // OS_FINALIZADA_101036: uma OS finalizada vira registro histórico, sem edição.\n  if(o.status==="Finalizado")return res.status(409).json({erro:"Esta ordem de serviço foi finalizada e está bloqueada para alterações."});'''
    tail=tail[:m.start()]+block+tail[m.end():]
    server=server[:pos]+tail

# Ao marcar Finalizado exige Pago; ao finalizar grava data. Garantia não depende de pagamento.
needle='''  if(req.body.status!==undefined&&allowed.includes(String(req.body.status))){
    const novoStatus=String(req.body.status) as OrdemServico["status"];o.status=novoStatus;
    if((novoStatus==="Pronto"||novoStatus==="Entregue")&&!o.prontoEm){o.prontoEm=now();o.garantiaAte=garantiaAte101030(o.prontoEm)}
    else garantirDatasOS101030(o,false);
  }'''
replacement='''  if(req.body.status!==undefined&&allowed.includes(String(req.body.status))){
    const novoStatus=String(req.body.status) as OrdemServico["status"];
    if(novoStatus==="Finalizado"&&o.status!=="Pago")return res.status(400).json({erro:"Marque a ordem como Pago antes de finalizar."});
    o.status=novoStatus;
    if(novoStatus==="Finalizado")o.finalizadoEm=now();
    garantirDatasOS101030(o,false);
  }
  if(req.body.iniciarGarantia===true&&!o.prontoEm){o.prontoEm=now();o.garantiaAte=garantiaAte101030(o.prontoEm)}'''
if needle in server:
    server=server.replace(needle,replacement,1)
else:
    raise RuntimeError('Bloco de status/garantia 10.10.30 nao encontrado')

write('src/server.ts',server)

# -------- cliente: valor indefinido, novos status, garantia separada, preview e lock --------
# helper de valor
js += r'''

// 10.10.36 - fluxo simplificado de OS, diagnóstico sem preço e histórico final bloqueado.
const OS_STATUS_101036=['Acabou de chegar','Esperando técnico consertar','Pago','Finalizado'];
function osValor101036(o){return Number(o?.valor)>0?money(Number(o.valor)):'A definir após diagnóstico'}
function osValorCurto101036(o){return Number(o?.valor)>0?money(Number(o.valor)):'Valor indefinido'}
function osFinalizada101036(o){return o?.status==='Finalizado'}
function osGarantiaAtiva101036(o){return Boolean(o?.prontoEm&&o?.garantiaAte)}
function osStatusClass101036(status){return String(status||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().replace(/[^a-z0-9]+/g,'-')}

// Serviço opcional: sem serviço escolhido = diagnóstico/observação, sem exibir R$ 0,00.
osServiceOptions101023=function(selected=''){
 const options=servicos.filter(s=>s.ativo).map(s=>`<option value="${s.id}" ${String(selected)===String(s.id)?'selected':''}>${esc(s.nome)} · ${money(s.preco)}</option>`).join('');
 return `<option value="" ${selected===''||selected==null?'selected':''}>Ainda não definido — em diagnóstico</option>${options}`;
};

renderOS=function(){
 const search=(document.querySelector('#filtroOS')?.value||'').trim().toLowerCase();
 const filter=document.querySelector('#filtroStatusOS101023')?.value||osStatusFilter101023||'todos';osStatusFilter101023=filter;
 const all=Array.isArray(ordensServico)?ordensServico:[];
 const counts={chegar:all.filter(o=>o.status==='Acabou de chegar').length,tecnico:all.filter(o=>o.status==='Esperando técnico consertar').length,pago:all.filter(o=>o.status==='Pago').length,finalizado:all.filter(o=>o.status==='Finalizado').length};
 const stats=document.querySelector('#osStats101023');if(stats)stats.innerHTML=`<button type="button" data-os-status-filter="Acabou de chegar"><span>Acabou de chegar</span><b>${counts.chegar}</b><small>aguardando andamento</small></button><button type="button" data-os-status-filter="Esperando técnico consertar"><span>Esperando técnico</span><b>${counts.tecnico}</b><small>em diagnóstico ou reparo</small></button><button type="button" data-os-status-filter="Pago"><span>Pago</span><b>${counts.pago}</b><small>aguardando finalização</small></button><button type="button" data-os-status-filter="Finalizado"><span>Finalizadas</span><b>${counts.finalizado}</b><small>histórico bloqueado</small></button>`;
 const select=document.querySelector('#filtroStatusOS101023');if(select){const wanted=['todos',...OS_STATUS_101036];const current=select.value;select.innerHTML='<option value="todos">Todos os status</option>'+OS_STATUS_101036.map(s=>`<option>${s}</option>`).join('');select.value=wanted.includes(current)?current:'todos'}
 const list=all.filter(o=>{const matchesStatus=filter==='todos'||o.status===filter;const hay=[o.id,o.clienteNome,o.telefone,o.aparelho,o.marca,o.modelo,o.servicoNome,o.status].join(' ').toLowerCase();return matchesStatus&&(!search||hay.includes(search))});
 const host=document.querySelector('#osList101023');if(!host)return;
 host.innerHTML=list.map(o=>`<article class="os-card os-card-101023 ${osFinalizada101036(o)?'os-locked-101036':''}" data-os-id="${o.id}"><div class="os-card-accent-101023 status-${osStatusClass101036(o.status)}"></div><div class="os-card-head-101023"><div><span class="os-number-101023">OS #${o.id}</span><h3>${esc(o.clienteNome)}</h3><small>${esc(o.telefone||'Telefone não informado')}</small></div><span class="os-status-101023 status-${osStatusClass101036(o.status)}">${esc(o.status)}</span></div><div class="os-device-101023"><div><span>Aparelho</span><b>${esc(o.aparelho)}${o.marca?` · ${esc(o.marca)}`:''}${o.modelo?` · ${esc(o.modelo)}`:''}</b></div><div><span>Serviço</span><b>${o.servicoId?esc(o.servicoNome||'Serviço definido'):'Em diagnóstico / serviço ainda não definido'}</b></div></div><div class="os-problem-101023"><span>Relato</span><p>${esc(o.problemaRelatado||'Nenhum problema detalhado.')}</p></div><footer><div><span>Valor</span><strong>${osValorCurto101036(o)}</strong></div><div><span>${o.prontoEm?'Garantia iniciada':'Atualizada'}</span><b>${new Date(o.prontoEm||o.atualizadoEm).toLocaleString('pt-BR')}</b></div><button type="button" class="secondary os-edit-101023" data-edit-os="${o.id}">${osFinalizada101036(o)?'Ver ordem / vias':'Abrir / atualizar'}</button></footer></article>`).join('')||'<div class="os-empty-101023"><b>Nenhuma ordem encontrada</b><span>Crie uma nova ordem ou altere os filtros.</span></div>';
 setTimeout(syncOSPrint101020,0);
};

novaOS=async function(){
 try{await loadServicos()}catch(e){console.error('[OS serviços 101036]',e);return toast('Não foi possível carregar os serviços.')}
 const clients=clientes.filter(c=>c.ativo).map(c=>`<option value="${esc(c.nome)}"></option>`).join('');
 openModal('Nova ordem de serviço',`<form id="osForm101023" class="os-form-101023"><section><h4>Cliente e aparelho</h4><div class="form-grid"><div><label>Cliente *</label><input name="clienteNome" list="osClientes101023" autocomplete="off" required><datalist id="osClientes101023">${clients}</datalist></div><div><label>Telefone</label><input name="telefone" inputmode="tel" placeholder="(00) 00000-0000"></div><div><label>Aparelho *</label><input name="aparelho" placeholder="Ex.: Celular, notebook" required></div><div><label>Marca</label><input name="marca"></div><div><label>Modelo</label><input name="modelo"></div><div><label>Serviço</label><select name="servicoId" id="osServico101023">${osServiceOptions101023('')}</select><small id="osServicoHelp101023" class="os-field-help-101023">Pode ficar sem serviço enquanto estiver em diagnóstico.</small></div></div></section><section><h4>Atendimento</h4><label>Problema relatado</label><textarea name="problemaRelatado" rows="3" placeholder="Descreva o que o cliente informou..."></textarea><div class="form-grid"><div><label>Valor (opcional)</label><input name="valor" type="number" min="0" step="0.01" placeholder="A definir após diagnóstico"><small class="os-field-help-101023">Se ficar vazio ou zero, as vias mostrarão “A definir após diagnóstico”.</small></div><div><label>Observações internas</label><input name="observacoes"></div></div></section><button type="submit" class="primary os-submit-101023">Criar ordem de serviço</button></form>`);
 const form=document.querySelector('#osForm101023'),select=document.querySelector('#osServico101023'),help=document.querySelector('#osServicoHelp101023');
 select?.addEventListener('change',()=>{const service=servicos.find(s=>String(s.id)===select.value);if(help)help.textContent=service?`${service.nome} · preço cadastrado ${money(service.preco)}`:'Sem serviço definido: permanece em diagnóstico e o valor fica a definir.'});
 form.onsubmit=async event=>{event.preventDefault();const button=form.querySelector('button[type="submit"]');button.disabled=true;button.textContent='Criando ordem...';try{const raw=Object.fromEntries(new FormData(form));if(!String(raw.valor||'').trim())delete raw.valor;const response=await api('/api/ordens-servico',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(raw)}),data=await response.json().catch(()=>({}));if(!response.ok)throw new Error(data.erro||'Não foi possível criar a ordem.');closeModal();await loadOS();toast(`Ordem #${data.id} criada.`)}catch(e){toast(e?.message||'Erro ao criar ordem.');button.disabled=false;button.textContent='Criar ordem de serviço'}};
};

function osViaHtml101036(o,kind){
 const fake=document.createElement('article');fake.dataset.osId=String(o.id);document.body.appendChild(fake);let html='';try{html=osReceipt101030(fake,kind)}finally{fake.remove()}if(!html)return '';
 html=html.replace(/<div class="receipt-row"><span>Valor<\/span><b>[^<]*<\/b><\/div>/,`<div class="receipt-row"><span>Valor</span><b>${osValor101036(o)}</b></div>`);
 html=html.replace(/<div class="receipt-line"><span>Valor<\/span><b>[^<]*<\/b><\/div>/,`<div class="receipt-line"><span>Valor</span><b>${osValor101036(o)}</b></div>`);
 return html;
}
function visualizarVia101036(o,kind){const names={cliente:'Via do cliente',loja:'Via da loja',garantia:'Via de garantia'};if(kind==='garantia'&&!osGarantiaAtiva101036(o))return toast('A garantia ainda não foi iniciada pelo técnico.');const html=osViaHtml101036(o,kind);if(!html)return toast('Não foi possível montar esta via.');openModal(names[kind],`<div class="os-preview-101036">${html}</div><div class="modal-actions"><button class="secondary" type="button" onclick="closeModal()">Fechar</button></div>`)}

editOS=function(id){
 const o=ordensServico.find(x=>Number(x.id)===Number(id));if(!o)return toast('Ordem não encontrada.');
 const locked=osFinalizada101036(o),warranty=osGarantia101030(o);
 const warrantyInfo=warranty?`<div class="os-warranty-info-101030"><b>Garantia iniciada em ${dataHoraRecibo101025(warranty.inicio)}</b><span>Válida até ${dataHoraRecibo101025(warranty.fim)}.</span></div>`:`<div class="os-warranty-info-101036"><b>Garantia ainda não iniciada</b><span>Inicie quando o técnico concluir o reparo.</span></div>`;
 if(locked){
  openModal(`Ordem finalizada #${id}`,`<div class="os-locked-banner-101036"><b>🔒 Ordem finalizada</b><span>Este registro está bloqueado. Você ainda pode consultar as vias e a garantia.</span></div><div class="os-edit-summary-101023"><b>${esc(o.clienteNome)}</b><span>${esc(o.aparelho)} ${esc(o.marca||'')} ${esc(o.modelo||'')}</span><p>${esc(o.problemaRelatado||'Sem problema descrito.')}</p></div>${warrantyInfo}<div class="os-readonly-grid-101036"><div><span>Serviço</span><b>${o.servicoId?esc(o.servicoNome||'Serviço definido'):'Não definido / diagnóstico'}</b></div><div><span>Valor</span><b>${osValor101036(o)}</b></div><div><span>Status</span><b>${esc(o.status)}</b></div><div><span>Finalizada</span><b>${o.finalizadoEm?new Date(o.finalizadoEm).toLocaleString('pt-BR'):'Data não registrada'}</b></div></div><div class="os-preview-actions-101036"><button class="secondary" id="verViaCliente101036">Ver via do cliente</button><button class="secondary" id="verViaLoja101036">Ver via da loja</button><button class="primary" id="verViaGarantia101036" ${warranty?'':'disabled'}>${warranty?'Ver / acionar garantia':'Garantia não iniciada'}</button></div>`);
  document.querySelector('#verViaCliente101036')?.addEventListener('click',()=>visualizarVia101036(o,'cliente'));document.querySelector('#verViaLoja101036')?.addEventListener('click',()=>visualizarVia101036(o,'loja'));document.querySelector('#verViaGarantia101036')?.addEventListener('click',()=>visualizarVia101036(o,'garantia'));return;
 }
 openModal(`Ordem de serviço #${id}`,`<div class="os-edit-summary-101023"><b>${esc(o.clienteNome)}</b><span>${esc(o.aparelho)} ${esc(o.marca||'')} ${esc(o.modelo||'')}</span><p>${esc(o.problemaRelatado||'Sem problema descrito.')}</p></div>${warrantyInfo}<form id="editOSForm101023" class="os-form-101023"><div class="form-grid"><div><label>Status</label><select name="status">${OS_STATUS_101036.map(s=>`<option ${o.status===s?'selected':''}>${s}</option>`).join('')}</select></div><div><label>Serviço</label><select name="servicoId">${osServiceOptions101023(o.servicoId)}</select></div><div><label>Valor</label><input name="valor" type="number" min="0" step="0.01" value="${Number(o.valor)>0?Number(o.valor):''}" placeholder="A definir após diagnóstico"><small class="os-field-help-101023">Vazio ou zero será mostrado como “A definir após diagnóstico”.</small></div><div><label>Observações</label><input name="observacoes" value="${esc(o.observacoes||'')}"></div></div><div class="os-main-actions-101030">${!warranty?'<button type="button" class="os-ready-101030" id="markOSReady101036">Técnico concluiu — iniciar garantia</button>':''}<button type="submit" class="primary os-submit-101023">Salvar alterações</button></div><div class="os-preview-actions-101036"><button type="button" class="secondary" id="verViaCliente101036">Ver via do cliente</button><button type="button" class="secondary" id="verViaLoja101036">Ver via da loja</button>${warranty?'<button type="button" class="secondary" id="verViaGarantia101036">Ver via de garantia</button>':''}</div></form>`);
 const form=document.querySelector('#editOSForm101023');form.onsubmit=async event=>{event.preventDefault();const raw=Object.fromEntries(new FormData(form));if(!String(raw.valor||'').trim())raw.valor=0;if(raw.status==='Finalizado'&&o.status!=='Pago')return toast('Primeiro marque a ordem como Pago, salve e depois finalize.');const button=form.querySelector('button[type="submit"]');button.disabled=true;try{const response=await api(`/api/ordens-servico/${id}`,{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify(raw)}),data=await response.json().catch(()=>({}));if(!response.ok)throw new Error(data.erro||'Não foi possível atualizar.');closeModal();await loadOS();toast(data.status==='Finalizado'?'Ordem finalizada e bloqueada.':'Ordem atualizada.')}catch(e){toast(e?.message||'Erro ao atualizar ordem.');button.disabled=false}};
 document.querySelector('#markOSReady101036')?.addEventListener('click',async()=>{if(!confirm('O técnico concluiu o reparo? A garantia de 3 meses começará agora e a data não será alterada depois.'))return;const b=document.querySelector('#markOSReady101036');b.disabled=true;b.textContent='Iniciando garantia...';try{const r=await api(`/api/ordens-servico/${id}`,{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify({iniciarGarantia:true})}),d=await r.json().catch(()=>({}));if(!r.ok)throw new Error(d.erro||'Não foi possível iniciar a garantia.');closeModal();await loadOS();toast(`Garantia iniciada. Válida até ${dataHoraRecibo101025(d.garantiaAte)}.`)}catch(e){toast(e?.message||'Erro ao iniciar garantia.');b.disabled=false;b.textContent='Técnico concluiu — iniciar garantia'}});
 document.querySelector('#verViaCliente101036')?.addEventListener('click',()=>visualizarVia101036(o,'cliente'));document.querySelector('#verViaLoja101036')?.addEventListener('click',()=>visualizarVia101036(o,'loja'));document.querySelector('#verViaGarantia101036')?.addEventListener('click',()=>visualizarVia101036(o,'garantia'));
};

// Corrige o valor também na impressão térmica das vias.
const osReceiptBase101036=osReceipt101030;
osReceipt101030=function(row,kind){const o=osAtual101025(row);let html=osReceiptBase101036(row,kind);if(!o||!html)return html;const formatted=osValor101036(o);html=html.replace(/(<span>Valor<\/span>\s*<b>)[^<]*(<\/b>)/,`$1${formatted}$2`);return html};
'''

css=read('public/style.css')
css += r'''
/* 10.10.36 - OS: diagnóstico, lock e visualização de vias */
.os-locked-101036{opacity:.92}.os-locked-101036 .os-card-accent-101023{filter:saturate(.7)}
.os-locked-banner-101036{display:grid;gap:4px;padding:12px 14px;border:1px solid var(--border);border-radius:12px;margin-bottom:12px;background:color-mix(in srgb,var(--card-bg) 86%,var(--page-bg))}.os-locked-banner-101036 b{font-size:14px}.os-locked-banner-101036 span{font-size:12px;color:var(--muted)}
.os-readonly-grid-101036{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;margin:12px 0}.os-readonly-grid-101036>div{display:grid;gap:3px;padding:10px;border:1px solid var(--border);border-radius:10px}.os-readonly-grid-101036 span{font-size:10px;text-transform:uppercase;letter-spacing:.07em;color:var(--muted)}
.os-preview-actions-101036{display:flex;gap:8px;flex-wrap:wrap;margin-top:12px}.os-preview-101036{max-height:70vh;overflow:auto;padding:12px;background:#fff;color:#111;border-radius:10px}.os-preview-101036 .receipt{margin:auto}.os-warranty-info-101036{display:grid;gap:3px;padding:10px 12px;border:1px dashed var(--border);border-radius:10px;margin:10px 0}.os-warranty-info-101036 span{font-size:11px;color:var(--muted)}
@media(max-width:700px){.os-readonly-grid-101036{grid-template-columns:1fr}.os-preview-actions-101036>*{flex:1 1 100%}}
'''
write('public/app.js',js);write('public/style.css',css)
print('10.10.36: OS com valor a definir, status simplificados, garantia separada, finalização bloqueada e preview das três vias.')