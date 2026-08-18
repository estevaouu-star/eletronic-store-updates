from pathlib import Path
import json

root = Path("app")


def read(path: str) -> str:
    return (root / path).read_text(encoding="utf-8")


def write(path: str, content: str) -> None:
    (root / path).write_text(content, encoding="utf-8")


pkg = json.loads(read("package.json"))
pkg["version"] = "10.10.23"
write("package.json", json.dumps(pkg, indent=2, ensure_ascii=False))

html = read("public/index.html").replace(
    'id="versionInfo" class="version-info">v10.10.22',
    'id="versionInfo" class="version-info">v10.10.23',
    1,
)
old_section = '''<section id="ordensServico" class="section">
  <div class="title"><div><h2>Ordens de Serviço</h2><p>Controle aparelhos recebidos para assistência técnica.</p></div><button class="primary small" id="novaOSBtn">Nova ordem</button></div>
  <div class="card"><input id="filtroOS" placeholder="Buscar cliente, aparelho, modelo ou serviço...">
  <table><thead><tr><th>Nº</th><th>Cliente</th><th>Aparelho</th><th>Serviço</th><th>Valor</th><th>Status</th><th>Atualizado</th><th></th></tr></thead><tbody id="tableOS"></tbody></table></div>
</section>'''
new_section = '''<section id="ordensServico" class="section os-section-101023">
  <div class="title os-title-101023"><div><h2>Ordens de Serviço</h2><p>Acompanhe cada aparelho do recebimento até a entrega.</p></div><button class="primary small os-new-101023" id="novaOSBtn" type="button">+ Nova ordem</button></div>
  <div id="osStats101023" class="os-stats-101023"></div>
  <div class="card os-workspace-101023">
    <div class="os-toolbar-101023"><div class="os-search-101023"><span>⌕</span><input id="filtroOS" placeholder="Buscar cliente, aparelho, modelo ou serviço..."></div><select id="filtroStatusOS101023" aria-label="Filtrar por status"><option value="todos">Todos os status</option><option>Recebido</option><option>Em análise</option><option>Aguardando peça</option><option>Em reparo</option><option>Pronto</option><option>Entregue</option><option>Cancelada</option></select></div>
    <div id="osList101023" class="os-list-101023"></div>
  </div>
</section>'''
if old_section not in html:
    raise SystemExit("Seção antiga de Ordens de Serviço não encontrada.")
html = html.replace(old_section, new_section, 1)
write("public/index.html", html)

server = read("src/server.ts")
server = server.replace(
    'status:"Recebido"|"Em análise"|"Aguardando peça"|"Em reparo"|"Pronto"|"Entregue";',
    'status:"Recebido"|"Em análise"|"Aguardando peça"|"Em reparo"|"Pronto"|"Entregue"|"Cancelada";',
    1,
)
old_post_service = '''  const lojaId=lojaIdReq(req);const servico=db.servicos.find(s=>s.lojaId===lojaId&&s.id===Number(req.body.servicoId));
  const o:OrdemServico={'''
new_post_service = '''  const lojaId=lojaIdReq(req);
  const servicoInformado=String(req.body.servicoId??"").trim();
  const servico=servicoInformado?db.servicos.find(s=>s.lojaId===lojaId&&s.ativo&&s.id===Number(servicoInformado)):undefined;
  if(servicoInformado&&!servico)return res.status(400).json({erro:"O serviço selecionado não existe ou está inativo."});
  const o:OrdemServico={'''
if old_post_service not in server:
    raise SystemExit("Criação de OS esperada não encontrada.")
server = server.replace(old_post_service, new_post_service, 1)
server = server.replace(
    'const allowed=["Recebido","Em análise","Aguardando peça","Em reparo","Pronto","Entregue"];',
    'const allowed=["Recebido","Em análise","Aguardando peça","Em reparo","Pronto","Entregue","Cancelada"];',
    1,
)

old_put = '''  if(req.body.status!==undefined&&allowed.includes(String(req.body.status)))o.status=req.body.status;
  if(req.body.valor!==undefined)o.valor=Math.max(0,Number(req.body.valor)||0);
  if(req.body.observacoes!==undefined)o.observacoes=String(req.body.observacoes);'''
new_put = '''  if(req.body.status!==undefined&&allowed.includes(String(req.body.status)))o.status=req.body.status;
  if(req.body.servicoId!==undefined){
    const informado=String(req.body.servicoId??"").trim();
    const servico=informado?db.servicos.find(s=>s.lojaId===o.lojaId&&s.ativo&&s.id===Number(informado)):undefined;
    if(informado&&!servico)return res.status(400).json({erro:"O serviço selecionado não existe ou está inativo."});
    o.servicoId=servico?.id||null;o.servicoNome=servico?.nome||"Diagnóstico";
    if(req.body.valor===undefined&&servico)o.valor=servico.preco;
  }
  if(req.body.valor!==undefined)o.valor=Math.max(0,Number(req.body.valor)||0);
  if(req.body.observacoes!==undefined)o.observacoes=String(req.body.observacoes);'''
if old_put not in server:
    raise SystemExit("Atualização de OS esperada não encontrada.")
server = server.replace(old_put, new_put, 1)
delete_anchor = '''  o.atualizadoEm=now();salvar();res.json(o);
});



// Diagnóstico de segurança para celulares'''
delete_replacement = '''  o.atualizadoEm=now();salvar();res.json(o);
});

app.delete("/api/ordens-servico/:id",auth,(req,res)=>{
  const index=db.ordensServico.findIndex(x=>x.lojaId===lojaIdReq(req)&&x.id===Number(req.params.id));
  if(index<0)return res.status(404).json({erro:"Ordem de serviço não encontrada."});
  const [removida]=db.ordensServico.splice(index,1);salvar();res.json({ok:true,id:removida.id});
});



// Diagnóstico de segurança para celulares'''
if delete_anchor not in server:
    raise SystemExit("Ponto de exclusão de OS não encontrado.")
server = server.replace(delete_anchor, delete_replacement, 1)
write("src/server.ts", server)

js = read("public/app.js").replace(
    'const atual="10.10.22"', 'const atual="10.10.23"', 1
)
js += r'''

// 10.10.23 - Ordens de Serviço estáveis e redesenhadas.
// Interrompe o ciclo dos patches 10.10.15/17/18, que adicionavam e removiam
// os mesmos botões continuamente e bloqueavam formulário e select.
try{injectOSPrint101015=function(){};unificarBotoesOS101017=function(){};corrigirOS101018=function(){}}catch(e){console.error('[OS legado 101023]',e)}

let osStatusFilter101023='todos';
function osStatusClass101023(status){
 return String(status||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().replace(/[^a-z0-9]+/g,'-');
}
function osServiceOptions101023(selected=''){
 const options=servicos.filter(s=>s.ativo).map(s=>`<option value="${s.id}" ${String(selected)===String(s.id)?'selected':''}>${esc(s.nome)} · ${money(s.preco)}</option>`).join('');
 return `<option value="" ${selected===''||selected==null?'selected':''}>Diagnóstico inicial</option>${options}`;
}
renderOS=function(){
 const search=(document.querySelector('#filtroOS')?.value||'').trim().toLowerCase();
 const filter=document.querySelector('#filtroStatusOS101023')?.value||osStatusFilter101023||'todos';osStatusFilter101023=filter;
 const all=Array.isArray(ordensServico)?ordensServico:[];
 const counts={abertas:all.filter(o=>!['Entregue','Cancelada'].includes(o.status)).length,andamento:all.filter(o=>['Em análise','Aguardando peça','Em reparo'].includes(o.status)).length,prontas:all.filter(o=>o.status==='Pronto').length,entregues:all.filter(o=>o.status==='Entregue').length};
 const stats=document.querySelector('#osStats101023');if(stats)stats.innerHTML=`<button type="button" data-os-status-filter="todos"><span>Ordens abertas</span><b>${counts.abertas}</b><small>acompanhamento geral</small></button><button type="button" data-os-status-filter="Em reparo"><span>Em andamento</span><b>${counts.andamento}</b><small>análise, peça ou reparo</small></button><button type="button" data-os-status-filter="Pronto"><span>Prontas</span><b>${counts.prontas}</b><small>aguardando retirada</small></button><button type="button" data-os-status-filter="Entregue"><span>Entregues</span><b>${counts.entregues}</b><small>atendimentos concluídos</small></button>`;
 const list=all.filter(o=>{
  const matchesStatus=filter==='todos'||o.status===filter||(filter==='Em reparo'&&['Em análise','Aguardando peça','Em reparo'].includes(o.status));
  const hay=[o.id,o.clienteNome,o.telefone,o.aparelho,o.marca,o.modelo,o.servicoNome,o.status].join(' ').toLowerCase();
  return matchesStatus&&(!search||hay.includes(search));
 });
 const host=document.querySelector('#osList101023');if(!host)return;
 host.innerHTML=list.map(o=>`<article class="os-card os-card-101023" data-os-id="${o.id}"><div class="os-card-accent-101023 status-${osStatusClass101023(o.status)}"></div><div class="os-card-head-101023"><div><span class="os-number-101023">OS #${o.id}</span><h3>${esc(o.clienteNome)}</h3><small>${esc(o.telefone||'Telefone não informado')}</small></div><span class="os-status-101023 status-${osStatusClass101023(o.status)}">${esc(o.status)}</span></div><div class="os-device-101023"><div><span>Aparelho</span><b>${esc(o.aparelho)}${o.marca?` · ${esc(o.marca)}`:''}${o.modelo?` · ${esc(o.modelo)}`:''}</b></div><div><span>Serviço</span><b>${esc(o.servicoNome||'Diagnóstico')}</b></div></div><div class="os-problem-101023"><span>Relato</span><p>${esc(o.problemaRelatado||'Nenhum problema detalhado.')}</p></div><footer><div><span>Valor</span><strong>${money(o.valor)}</strong></div><div><span>Atualizada</span><b>${new Date(o.atualizadoEm).toLocaleString('pt-BR')}</b></div><button type="button" class="secondary os-edit-101023" data-edit-os="${o.id}">Abrir / atualizar</button></footer></article>`).join('')||'<div class="os-empty-101023"><b>Nenhuma ordem encontrada</b><span>Crie uma nova ordem ou altere os filtros.</span></div>';
 setTimeout(syncOSPrint101020,0);
};

novaOS=async function(){
 try{await loadServicos()}catch(e){console.error('[OS serviços 101023]',e);return toast('Não foi possível carregar os serviços.')}
 const clients=clientes.filter(c=>c.ativo).map(c=>`<option value="${esc(c.nome)}"></option>`).join('');
 openModal('Nova ordem de serviço',`<form id="osForm101023" class="os-form-101023"><section><h4>Cliente e aparelho</h4><div class="form-grid"><div><label>Cliente *</label><input name="clienteNome" list="osClientes101023" autocomplete="off" required><datalist id="osClientes101023">${clients}</datalist></div><div><label>Telefone</label><input name="telefone" inputmode="tel" placeholder="(00) 00000-0000"></div><div><label>Aparelho *</label><input name="aparelho" placeholder="Ex.: Celular, notebook" required></div><div><label>Marca</label><input name="marca"></div><div><label>Modelo</label><input name="modelo"></div><div><label>Serviço</label><select name="servicoId" id="osServico101023">${osServiceOptions101023('')}</select><small id="osServicoHelp101023" class="os-field-help-101023">Diagnóstico inicial, sem serviço definido.</small></div></div></section><section><h4>Atendimento</h4><label>Problema relatado</label><textarea name="problemaRelatado" rows="3" placeholder="Descreva o que o cliente informou..."></textarea><div class="form-grid"><div><label>Valor combinado (opcional)</label><input name="valor" type="number" min="0" step="0.01" placeholder="Usar preço do serviço"></div><div><label>Observações internas</label><input name="observacoes"></div></div></section><button type="submit" class="primary os-submit-101023">Criar ordem de serviço</button></form>`);
 const form=document.querySelector('#osForm101023'),select=document.querySelector('#osServico101023'),help=document.querySelector('#osServicoHelp101023');
 select?.addEventListener('change',()=>{const service=servicos.find(s=>String(s.id)===select.value);if(help)help.textContent=service?`${service.nome} · preço cadastrado ${money(service.preco)}`:'Diagnóstico inicial, sem serviço definido.'});
 form.onsubmit=async event=>{
  event.preventDefault();const button=form.querySelector('button[type="submit"]');button.disabled=true;button.textContent='Criando ordem...';
  try{
   const raw=Object.fromEntries(new FormData(form));if(!String(raw.valor||'').trim())delete raw.valor;
   const response=await api('/api/ordens-servico',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(raw)}),data=await response.json().catch(()=>({}));
   if(!response.ok)throw new Error(data.erro||'Não foi possível criar a ordem.');
   closeModal();await loadOS();toast(`Ordem #${data.id} criada.`);
  }catch(e){console.error('[criar OS 101023]',e);toast(e?.message||'Erro ao criar ordem.');button.disabled=false;button.textContent='Criar ordem de serviço'}
 };
};

editOS=function(id){
 const o=ordensServico.find(x=>Number(x.id)===Number(id));if(!o)return toast('Ordem não encontrada.');
 openModal(`Ordem de serviço #${id}`,`<div class="os-edit-summary-101023"><b>${esc(o.clienteNome)}</b><span>${esc(o.aparelho)} ${esc(o.marca||'')} ${esc(o.modelo||'')}</span><p>${esc(o.problemaRelatado||'Sem problema descrito.')}</p></div><form id="editOSForm101023" class="os-form-101023"><div class="form-grid"><div><label>Status</label><select name="status">${['Recebido','Em análise','Aguardando peça','Em reparo','Pronto','Entregue','Cancelada'].map(s=>`<option ${o.status===s?'selected':''}>${s}</option>`).join('')}</select></div><div><label>Serviço</label><select name="servicoId">${osServiceOptions101023(o.servicoId)}</select></div><div><label>Valor</label><input name="valor" type="number" min="0" step="0.01" value="${Number(o.valor)||0}"></div><div><label>Observações</label><input name="observacoes" value="${esc(o.observacoes||'')}"></div></div><button type="submit" class="primary os-submit-101023">Salvar alterações</button><div class="os-danger-actions-101023"><button type="button" class="secondary" id="cancelOS101023">Cancelar ordem</button><button type="button" class="danger" id="deleteOS101023">Excluir definitivamente</button></div></form>`);
 const form=document.querySelector('#editOSForm101023');form.onsubmit=async event=>{event.preventDefault();const button=form.querySelector('button');button.disabled=true;try{const response=await api(`/api/ordens-servico/${id}`,{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify(Object.fromEntries(new FormData(form)))}),data=await response.json().catch(()=>({}));if(!response.ok)throw new Error(data.erro||'Não foi possível atualizar.');closeModal();await loadOS();toast('Ordem atualizada.')}catch(e){toast(e?.message||'Erro ao atualizar ordem.');button.disabled=false}};
 document.querySelector('#cancelOS101023').onclick=async()=>{if(!confirm(`Cancelar a ordem #${id}? Ela continuará no histórico.`))return;const response=await api(`/api/ordens-servico/${id}`,{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify({status:'Cancelada'})}),data=await response.json().catch(()=>({}));if(!response.ok)return toast(data.erro||'Não foi possível cancelar.');closeModal();await loadOS();toast(`Ordem #${id} cancelada.`)};
 document.querySelector('#deleteOS101023').onclick=async()=>{if(!confirm(`Excluir definitivamente a ordem #${id}? Esta ação não pode ser desfeita.`))return;const response=await api(`/api/ordens-servico/${id}`,{method:'DELETE'}),data=await response.json().catch(()=>({}));if(!response.ok)return toast(data.erro||'Não foi possível excluir.');closeModal();await loadOS();toast(`Ordem #${id} excluída.`)};
};

document.addEventListener('change',event=>{if(event.target?.id==='filtroStatusOS101023'){osStatusFilter101023=event.target.value;renderOS()}},true);
document.addEventListener('click',event=>{const stat=event.target.closest?.('[data-os-status-filter]');if(stat){const select=document.querySelector('#filtroStatusOS101023');if(select)select.value=stat.dataset.osStatusFilter;osStatusFilter101023=stat.dataset.osStatusFilter;renderOS();return}const edit=event.target.closest?.('[data-edit-os]');if(edit){event.preventDefault();editOS(Number(edit.dataset.editOs))}},true);
'''
write("public/app.js", js)

css = read("public/style.css") + r'''

/* 10.10.23 - Ordens de Serviço */
.os-section-101023{max-width:1280px}.os-title-101023{align-items:flex-end}.os-new-101023{min-height:42px;padding-inline:18px!important}.os-stats-101023{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;margin-bottom:12px}.os-stats-101023 button{display:flex;flex-direction:column;align-items:flex-start;min-height:104px;padding:14px;border:1px solid var(--border);border-radius:14px;background:var(--card-bg);color:var(--text-main);cursor:pointer;text-align:left;box-shadow:0 4px 16px #00000009}.os-stats-101023 button:hover{border-color:var(--accent);transform:translateY(-1px)}.os-stats-101023 span{font-size:11px;font-weight:800;text-transform:uppercase;letter-spacing:.05em;color:var(--text-muted)}.os-stats-101023 b{font-size:27px;margin:7px 0 2px}.os-stats-101023 small{font-size:10px;color:var(--text-muted)}.os-workspace-101023{padding:14px!important}.os-toolbar-101023{display:grid;grid-template-columns:minmax(0,1fr) 220px;gap:10px;margin-bottom:12px}.os-toolbar-101023 input,.os-toolbar-101023 select{margin:0!important;min-height:42px}.os-search-101023{position:relative}.os-search-101023>span{position:absolute;left:13px;top:9px;z-index:1;font-size:20px;color:var(--text-muted)}.os-search-101023 input{padding-left:40px!important}.os-list-101023{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:11px}.os-card-101023{position:relative;overflow:hidden;padding:15px;border:1px solid var(--border);border-radius:14px;background:color-mix(in srgb,var(--card-bg) 97%,var(--page-bg));box-shadow:0 4px 15px #00000009}.os-card-accent-101023{position:absolute;inset:0 auto 0 0;width:4px;background:#87929c}.os-card-accent-101023.status-em-analise,.os-card-accent-101023.status-aguardando-peca{background:#d28b17}.os-card-accent-101023.status-em-reparo{background:#2674d9}.os-card-accent-101023.status-pronto{background:#16a05d}.os-card-accent-101023.status-entregue{background:#75808a}.os-card-head-101023{display:flex;justify-content:space-between;gap:12px;align-items:flex-start}.os-number-101023{font-size:10px;font-weight:900;color:var(--accent);letter-spacing:.06em}.os-card-head-101023 h3{margin:3px 0 2px;font-size:17px}.os-card-head-101023 small{font-size:10px;color:var(--text-muted)}.os-status-101023{padding:6px 8px;border-radius:999px;background:color-mix(in srgb,#87929c 13%,var(--card-bg));color:#59636c;font-size:10px;font-weight:900;white-space:nowrap}.os-status-101023.status-em-analise,.os-status-101023.status-aguardando-peca{background:#fff2d9;color:#9a650c}.os-status-101023.status-em-reparo{background:#e5f0ff;color:#1d62bb}.os-status-101023.status-pronto{background:#e0f7ea;color:#117844}.os-status-101023.status-entregue{background:#edf0f2;color:#58616a}.os-device-101023{display:grid;grid-template-columns:1fr 1fr;gap:9px;margin:13px 0 9px}.os-device-101023>div,.os-problem-101023{padding:9px 10px;border-radius:9px;background:color-mix(in srgb,var(--page-bg) 72%,var(--card-bg));border:1px solid color-mix(in srgb,var(--border) 75%,transparent)}.os-device-101023 span,.os-problem-101023>span,.os-card-101023 footer span{display:block;font-size:9px;font-weight:800;text-transform:uppercase;letter-spacing:.04em;color:var(--text-muted);margin-bottom:3px}.os-device-101023 b{font-size:11px}.os-problem-101023 p{margin:0;font-size:11px;line-height:1.35;min-height:30px}.os-card-101023 footer{display:grid;grid-template-columns:90px 1fr auto;gap:9px;align-items:end;margin-top:10px;padding-top:10px;border-top:1px solid var(--border)}.os-card-101023 footer strong{font-size:15px;color:var(--accent)}.os-card-101023 footer b{font-size:10px}.os-edit-101023{min-height:32px!important;padding:7px 10px!important;font-size:10px!important}.os-empty-101023{grid-column:1/-1;display:grid;place-items:center;gap:5px;min-height:180px;border:1px dashed var(--border);border-radius:12px;color:var(--text-muted)}.os-empty-101023 b{color:var(--text-main)}.os-form-101023{display:grid;gap:13px}.os-form-101023 section{padding:12px;border:1px solid var(--border);border-radius:12px;background:color-mix(in srgb,var(--page-bg) 55%,var(--card-bg))}.os-form-101023 h4{margin:0 0 8px;font-size:14px}.os-form-101023 textarea{width:100%;resize:vertical;min-height:78px;padding:10px;border:1px solid var(--border);border-radius:8px;background:var(--card-bg);color:var(--text-main);font:inherit}.os-form-101023 textarea:focus{outline:none;border-color:var(--accent);box-shadow:0 0 0 3px var(--accent-soft)}.os-field-help-101023{display:block;margin:-7px 0 8px;color:var(--text-muted);font-size:10px}.os-submit-101023{width:100%;min-height:44px}.os-submit-101023:disabled{opacity:.65;cursor:wait}.os-edit-summary-101023{padding:12px;margin-bottom:12px;border-left:4px solid var(--accent);background:var(--surface-soft);border-radius:8px}.os-edit-summary-101023 b,.os-edit-summary-101023 span{display:block}.os-edit-summary-101023 span{margin-top:3px;color:var(--text-muted);font-size:12px}.os-edit-summary-101023 p{margin:8px 0 0;font-size:12px}.os-card-101023>.os-print-actions-101020{padding-top:8px;border-top:1px dashed var(--border)}
@media(max-width:1050px){.os-list-101023{grid-template-columns:1fr}.os-stats-101023{grid-template-columns:repeat(2,1fr)}}
@media(max-width:650px){.os-stats-101023{grid-template-columns:1fr 1fr}.os-toolbar-101023,.os-device-101023{grid-template-columns:1fr}.os-card-101023 footer{grid-template-columns:1fr 1fr}.os-edit-101023{grid-column:1/-1}.os-title-101023{align-items:flex-start}.os-new-101023{width:100%}}
.os-card-accent-101023.status-cancelada{background:#ba3b3b}.os-status-101023.status-cancelada{background:#fde9e9;color:#9c2929}.os-danger-actions-101023{display:flex;justify-content:flex-end;gap:8px;padding-top:4px}.os-danger-actions-101023 button{min-height:36px;padding:8px 12px}.os-danger-actions-101023 .danger{border:1px solid #c93f3f;background:#c93f3f;color:#fff;border-radius:8px;font-weight:800;cursor:pointer}.os-danger-actions-101023 .danger:hover{background:#a92f2f;border-color:#a92f2f}
@media(max-width:650px){.os-danger-actions-101023{flex-direction:column}.os-danger-actions-101023 button{width:100%}}
'''
write("public/style.css", css)

print("10.10.23: OS redesenhada, criação corrigida e seleção de serviços estabilizada.")
