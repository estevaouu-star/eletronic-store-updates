from pathlib import Path
import json

root = Path("app")


def read(path: str) -> str:
    return (root / path).read_text(encoding="utf-8")


def write(path: str, content: str) -> None:
    (root / path).write_text(content, encoding="utf-8")


pkg = json.loads(read("package.json"))
pkg["version"] = "10.10.24"
write("package.json", json.dumps(pkg, indent=2, ensure_ascii=False))

html = read("public/index.html").replace(
    'id="versionInfo" class="version-info">v10.10.23',
    'id="versionInfo" class="version-info">v10.10.24',
    1,
)
old_sales = '''<section id="vendas" class="section">
  <div class="title"><div><h2>Vendas</h2><p>Histórico, comprovantes e cancelamentos.</p></div></div>
  <div class="card"><input id="filtroVendas" placeholder="Buscar por número, cliente ou vendedor...">
  <table><thead><tr><th>Nº</th><th>Data</th><th>Cliente</th><th>Vendedor</th><th>Pagamento</th><th>Total</th><th>Status</th><th>Fiscal</th><th></th></tr></thead><tbody id="tableVendas"></tbody></table></div>
</section>'''
new_sales = '''<section id="vendas" class="section vendas-section-101024">
  <div class="title"><div><h2>Vendas</h2><p>Consulte um dia por vez ou veja o resumo organizado do mês.</p></div></div>
  <div class="card vendas-filter-card-101024">
    <div class="vendas-mode-101024"><button type="button" class="active" data-vendas-mode="day">Por dia</button><button type="button" data-vendas-mode="month">Por mês</button></div>
    <div class="vendas-filters-101024">
      <div id="vendasDiaBox101024"><label>Dia</label><input id="vendasData101024" type="date"></div>
      <div id="vendasMesBox101024" hidden><label>Mês</label><input id="vendasMesInput101024" type="month"></div>
      <div class="vendas-search-101024"><label>Buscar neste dia</label><input id="filtroVendas" placeholder="Número, cliente ou vendedor..."></div>
      <button type="button" class="secondary" id="vendasHoje101024">Hoje</button>
    </div>
  </div>
  <div id="vendasResumo101024" class="vendas-stats-101024"></div>
  <div id="vendasMes101024" class="vendas-days-101024" hidden></div>
  <div id="vendasDia101024" class="card vendas-table-card-101024">
    <div class="vendas-day-head-101024"><div><span>Movimento do dia</span><b id="vendasPeriodoTitulo101024">Hoje</b></div><small id="vendasQuantidade101024">0 vendas</small></div>
    <div class="vendas-table-scroll-101024"><table><thead><tr><th>Nº</th><th>Horário</th><th>Cliente</th><th>Vendedor</th><th>Pagamento</th><th>Total</th><th>Status</th><th>Fiscal</th><th></th></tr></thead><tbody id="tableVendas"></tbody></table></div>
  </div>
</section>'''
if old_sales not in html:
    raise SystemExit("Seção de Vendas 10.10.23 não encontrada.")
html = html.replace(old_sales, new_sales, 1)
write("public/index.html", html)

server = read("src/server.ts")
old_sales_get = '''app.get("/api/vendas",auth,(_req,res)=>{const lojaId=lojaIdReq(_req);res.json(db.vendas.filter(v=>v.lojaId===lojaId).reverse());});'''
new_sales_get = '''app.get("/api/vendas/consulta",auth,(req,res)=>{
  const lojaId=lojaIdReq(req),modo=String(req.query.modo||"dia")==="mes"?"mes":"dia";
  const chave=(valor:string)=>new Date(valor).toLocaleDateString("sv-SE");
  const hoje=chave(now()),loja=db.vendas.filter(v=>v.lojaId===lojaId);
  if(modo==="mes"){
    const mes=/^\\d{4}-\\d{2}$/.test(String(req.query.mes||""))?String(req.query.mes):hoje.slice(0,7);
    const mapa=new Map<string,{data:string;vendas:number;concluidas:number;canceladas:number;total:number}>();
    for(const v of loja){const data=chave(v.criadoEm);if(!data.startsWith(mes))continue;const item=mapa.get(data)||{data,vendas:0,concluidas:0,canceladas:0,total:0};item.vendas++;if(v.status==="concluida"){item.concluidas++;item.total+=v.total}else item.canceladas++;mapa.set(data,item)}
    const dias=[...mapa.values()].sort((a,b)=>b.data.localeCompare(a.data));
    return res.json({modo:"mes",mes,dias,resumo:{vendas:dias.reduce((s,d)=>s+d.vendas,0),concluidas:dias.reduce((s,d)=>s+d.concluidas,0),canceladas:dias.reduce((s,d)=>s+d.canceladas,0),total:dias.reduce((s,d)=>s+d.total,0)}});
  }
  const data=/^\\d{4}-\\d{2}-\\d{2}$/.test(String(req.query.data||""))?String(req.query.data):hoje;
  const vendas=loja.filter(v=>chave(v.criadoEm)===data).sort((a,b)=>new Date(b.criadoEm).getTime()-new Date(a.criadoEm).getTime());
  res.json({modo:"dia",data,vendas,resumo:{vendas:vendas.length,concluidas:vendas.filter(v=>v.status==="concluida").length,canceladas:vendas.filter(v=>v.status==="cancelada").length,total:vendas.filter(v=>v.status==="concluida").reduce((s,v)=>s+v.total,0)}});
});

app.get("/api/vendas",auth,(_req,res)=>{const lojaId=lojaIdReq(_req);res.json(db.vendas.filter(v=>v.lojaId===lojaId).reverse());});'''
if old_sales_get not in server:
    raise SystemExit("Endpoint de vendas esperado não encontrado.")
server = server.replace(old_sales_get, new_sales_get, 1)
write("src/server.ts", server)

js = read("public/app.js").replace(
    'const atual="10.10.23"', 'const atual="10.10.24"', 1
)
js += r'''

// 10.10.24 - pagamento com troco real, conclusão integrada ao tema e vendas por período.
function trocoPagamento101024(){return Math.round(pagamentos1096.reduce((s,p)=>s+Math.max(0,Number(p.recebido||0)-Number(p.valor||0)),0)*100)/100}

renderPagamentos1096=function(){
 const host=document.querySelector('#pagamentos1096');if(!host)return;
 if(!pagamentos1096.length){host.innerHTML='<div class="pay101024-empty"><b>Nenhum pagamento lançado</b><span>Informe o valor recebido e escolha a forma.</span></div>';return}
 host.innerHTML=pagamentos1096.map((p,i)=>`<div class="pay101024-row"><div class="pay101024-method-icon">${p.tipo==='Dinheiro'?'R$':p.tipo==='PIX'?'PX':p.tipo==='Débito'?'DB':'CR'}</div><div><b>${esc(p.tipo)}${p.tipo==='Crédito'&&p.parcelas?` · ${p.parcelas}x`:''}</b><small>${p.tipo==='Dinheiro'&&Number(p.recebido)>Number(p.valor)?`Aplicado ${money(p.valor)} · recebido ${money(p.recebido)} · troco ${money(Number(p.recebido)-Number(p.valor))}`:money(p.valor)}</small></div><button type="button" data-rm-pay="${i}" title="Remover pagamento">×</button></div>`).join('');
};

atualizarPagamento1096=function(){
 const total=totalVenda1096(),pago=pago1096(),rest=Math.max(0,Math.round((total-pago)*100)/100),troco=trocoPagamento101024();
 const totalEl=document.querySelector('#pay1096Total'),restEl=document.querySelector('#pay1096Restante'),changeEl=document.querySelector('#pay101024Troco'),input=document.querySelector('#pay1096Valor');
 if(totalEl)totalEl.textContent=money(total);if(restEl)restEl.textContent=money(rest);if(changeEl)changeEl.textContent=money(troco);
 if(input&&!input.value&&rest>0)input.value=rest.toFixed(2).replace('.',',');
 document.querySelector('#pay101024ChangeCard')?.classList.toggle('active',troco>0);
 renderPagamentos1096();const finish=document.querySelector('#finish1096');if(finish)finish.disabled=!(total>0&&rest<0.01&&pagamentos1096.length);
 const msg=document.querySelector('#pay101024Message');if(msg)msg.textContent=rest>0?`Ainda falta ${money(rest)}.`:(troco>0?`Pagamento completo. Entregue ${money(troco)} de troco.`:'Pagamento completo.');
};

montarPagamento1096=function(){
 removerUiAntiga1096();
 const caixa=document.querySelector('#caixa'),totalRow=document.querySelector('.pdv1094-total');if(!caixa||!totalRow)return;
 let cobrar=document.querySelector('#openCheckout1096');if(!cobrar){cobrar=document.createElement('button');cobrar.id='openCheckout1096';cobrar.type='button';cobrar.className='primary pay1096-open';cobrar.textContent='COBRAR';totalRow.parentElement.appendChild(cobrar)}
 if(document.querySelector('#checkout1096'))return;
 const overlay=document.createElement('div');overlay.id='checkout1096';overlay.className='pay1096-overlay pay101024-overlay hidden';overlay.innerHTML=`<div class="pay101024-card" role="dialog" aria-modal="true" aria-labelledby="pay101024Title">
  <header class="pay101024-head"><div><span>FINALIZAR VENDA</span><h3 id="pay101024Title">Pagamento</h3></div><button id="cancel1096" type="button" aria-label="Fechar">×</button></header>
  <div class="pay101024-balance"><div class="total"><span>Total da venda</span><b id="pay1096Total">R$ 0,00</b></div><div><span>Falta pagar</span><b id="pay1096Restante">R$ 0,00</b></div><div id="pay101024ChangeCard"><span>Troco</span><b id="pay101024Troco">R$ 0,00</b></div></div>
  <div class="pay101024-entry"><label for="pay1096Valor">Valor recebido</label><div><span>R$</span><input id="pay1096Valor" inputmode="decimal" autocomplete="off" placeholder="0,00"></div><small>No dinheiro, pode informar um valor maior; o troco será calculado automaticamente.</small></div>
  <div class="pay101024-method-title"><b>Forma de pagamento</b><span>Escolha para lançar o valor acima</span></div>
  <div class="pay1096-methods pay101024-methods"><button type="button" data-pay1096="Dinheiro"><span>R$</span>DINHEIRO</button><button type="button" data-pay1096="PIX"><span>PX</span>PIX</button><button type="button" data-pay1096="Débito"><span>DB</span>DÉBITO</button><button type="button" data-pay1096="Crédito"><span>CR</span>CRÉDITO</button></div>
  <div class="pay101024-installments"><label for="pay101024Parcelas">Parcelas do crédito</label><select id="pay101024Parcelas">${Array.from({length:12},(_,i)=>`<option value="${i+1}">${i+1}x</option>`).join('')}</select></div>
  <div class="pay101024-launched"><div><b>Pagamentos lançados</b><small id="pay101024Message"></small></div><div id="pagamentos1096"></div></div>
  <footer class="pay101024-actions"><button type="button" class="secondary" onclick="fecharPagamento1096()">Voltar</button><button id="finish1096" type="button" class="primary">Finalizar venda</button></footer>
 </div>`;document.body.appendChild(overlay);atualizarPagamento1096();
};

abrirPagamento1096=function(){
 if(!document.querySelector('#vendedorVenda')?.value)return toast('Selecione o vendedor antes de cobrar.');
 if(!cart.length&&!cartServicos.length)return toast('Adicione pelo menos um item antes de cobrar.');
 document.querySelector('#checkout1096')?.remove();pagamentos1096=[];montarPagamento1096();document.querySelector('#checkout1096')?.classList.remove('hidden');document.body.classList.add('pay1096-lock');atualizarPagamento1096();setTimeout(()=>document.querySelector('#pay1096Valor')?.select(),30);
};
fecharPagamento1096=function(){document.querySelector('#checkout1096')?.classList.add('hidden');document.body.classList.remove('pay1096-lock');pagamentos1096=[]};

addPagamento1096=function(tipo){
 const total=totalVenda1096(),rest=Math.max(0,Math.round((total-pago1096())*100)/100);let recebido=lerValor1096();if(!(recebido>0))recebido=rest;if(!(recebido>0))return;
 if(tipo!=='Dinheiro'&&recebido>rest+0.009)return toast('Somente dinheiro pode ser maior que o valor restante.');
 const valor=tipo==='Dinheiro'?Math.min(rest,recebido):recebido;if(!(valor>0))return;
 const item={tipo,valor:Math.round(valor*100)/100};if(tipo==='Dinheiro')item.recebido=Math.round(recebido*100)/100;if(tipo==='Crédito')item.parcelas=Math.max(1,Math.min(12,Number(document.querySelector('#pay101024Parcelas')?.value)||1));
 pagamentos1096.push(item);const input=document.querySelector('#pay1096Valor');if(input)input.value='';atualizarPagamento1096();
};

function mostrarVendaFinalizada101024(v){
 showReceipt(v);const receiptNode=document.querySelector('#receiptPrint'),cash=Array.isArray(v.pagamentos)?v.pagamentos.find(p=>p.forma==='Dinheiro'&&Number(p.recebido)>Number(p.valor)):null;if(receiptNode&&Number(v.troco)>0&&!receiptNode.textContent.includes('Troco:')){const info=document.createElement('p');info.innerHTML=`Recebido em dinheiro: ${money(cash?.recebido||0)}<br>Troco: ${money(v.troco)}`;receiptNode.querySelector('.receipt-total')?.before(info)}const receipt=receiptNode?.outerHTML||'';
 openModal('',`<div class="sale-success-101024"><div class="sale-success-mark-101024">✓</div><span>VENDA FINALIZADA</span><h2>Venda #${v.id}</h2><div class="sale-success-change-101024"><small>Troco para o cliente</small><b>${money(v.troco||0)}</b></div><p>Pagamento registrado com sucesso.</p><div class="sale-success-actions-101024"><button class="secondary" id="receiptPrintBtn" type="button" onclick="printReceipt()">Imprimir comprovante <kbd>F9</kbd></button><button class="primary" id="nextSale101024" type="button">Próxima venda <kbd>F10</kbd></button></div></div><div class="receipt-hidden-101024">${receipt}</div>`);
 const title=document.querySelector('#modalTitle');if(title)title.textContent='';document.querySelector('#nextSale101024').onclick=()=>{closeModal();document.querySelector('#buscaCodigo')?.focus()};
}

finalizar1096=async function(){
 const total=totalVenda1096(),rest=Math.max(0,Math.round((total-pago1096())*100)/100);if(rest>0.009)return toast(`Ainda falta ${money(rest)}.`);if(!pagamentos1096.length)return toast('Informe o pagamento.');
 const button=document.querySelector('#finish1096');if(button){button.disabled=true;button.textContent='Finalizando...'}
 const pagamentos=pagamentos1096.map(p=>({forma:p.tipo,valor:p.valor,...(p.recebido!=null?{recebido:p.recebido}:{}),...(p.parcelas?{parcelas:p.parcelas}:{})}));
 const subProdutos=cart.reduce((sum,i)=>{const p=produtos.find(x=>x.id===i.produtoId);return sum+(p.precoVenda+(Number(i.acrescimoUnitario)||0))*i.quantidade},0),subServicos=cartServicos.reduce((sum,i)=>{const s=servicos.find(x=>x.id===i.servicoId);return sum+(s.preco+(Number(i.acrescimoUnitario)||0))*i.quantidade},0),acrescimo=Number(document.querySelector('#surcharge')?.value)||0,descontoCalc=calcularDesconto(subProdutos+subServicos+acrescimo);
 try{
  const response=await api('/api/vendas',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({itens:cart,servicos:cartServicos,desconto:descontoCalc.valor,acrescimo,formaPagamento:pagamentos.length>1?'Misto':pagamentos[0].forma,pagamentos,troco:trocoPagamento101024(),clienteId:document.querySelector('#clienteVenda')?.value||null,vendedorId:document.querySelector('#vendedorVenda')?.value||null,compradorDocumento:document.querySelector('#compradorDocumento')?.value||'',compradorTelefone:document.querySelector('#compradorTelefone')?.value||'',compradorEmail:document.querySelector('#compradorEmail')?.value||''})}),data=await response.json().catch(()=>({}));
  if(!response.ok)throw new Error(data.erro||'Não foi possível finalizar a venda.');
  fecharPagamento1096();cart=[];cartServicos=[];document.querySelector('#desc').value=0;if(document.querySelector('#discountType'))document.querySelector('#discountType').value='value';if(document.querySelector('#surcharge'))document.querySelector('#surcharge').value=0;['#compradorDocumento','#compradorTelefone','#compradorEmail'].forEach(s=>{const e=document.querySelector(s);if(e)e.value=''});limparSelecoesPdvAposVenda();await Promise.all([loadProdutos(),loadDashboard()]);renderCart();mostrarVendaFinalizada101024(data);if(printerSettings.autoPrint)setTimeout(()=>directPrintReceipt(),150);
 }catch(e){console.error('[venda 101024]',e);toast(e?.message||'Erro ao finalizar venda.');if(button){button.disabled=false;button.textContent='Finalizar venda'}}
};

document.querySelector('#checkout1096')?.remove();setTimeout(montarPagamento1096,0);
window.addEventListener('keydown',event=>{if(document.querySelector('.sale-success-101024')){if(event.key==='F9'){event.preventDefault();printReceipt()}if(event.key==='F10'){event.preventDefault();document.querySelector('#nextSale101024')?.click()}}},true);

let vendasMode101024='day',vendasConsulta101024={resumo:{vendas:0,concluidas:0,canceladas:0,total:0}};
function dataLocal101024(date=new Date()){const y=date.getFullYear(),m=String(date.getMonth()+1).padStart(2,'0'),d=String(date.getDate()).padStart(2,'0');return `${y}-${m}-${d}`}
function formatarData101024(value,complete=false){const date=new Date(`${value}T12:00:00`);return date.toLocaleDateString('pt-BR',complete?{weekday:'long',day:'2-digit',month:'long',year:'numeric'}:{weekday:'short',day:'2-digit',month:'2-digit'})}
function resumoVendas101024(resumo={}){const host=document.querySelector('#vendasResumo101024');if(host)host.innerHTML=`<div><span>Vendas</span><b>${Number(resumo.vendas)||0}</b></div><div><span>Concluídas</span><b>${Number(resumo.concluidas)||0}</b></div><div><span>Canceladas</span><b>${Number(resumo.canceladas)||0}</b></div><div><span>Faturamento</span><b>${money(resumo.total||0)}</b></div>`}
function linhaVenda101024(v){return `<tr><td><b>#${v.id}</b></td><td>${new Date(v.criadoEm).toLocaleTimeString('pt-BR',{hour:'2-digit',minute:'2-digit'})}</td><td>${esc(v.clienteNome)}</td><td>${esc(v.vendedorNome||v.usuarioNome)}</td><td>${esc(v.formaPagamento)}${v.troco?`<small class="sale-change-101024">Troco ${money(v.troco)}</small>`:''}</td><td><b>${money(v.total)}</b></td><td><span class="sale-status-101024 ${v.status}">${v.status==='concluida'?'Finalizada':'Cancelada'}</span></td><td>${v.fiscal?`<span class="fiscal-badge">${v.fiscal.tipo==='rascunho-nfe'?'NF-e':'NFC-e'} rascunho</span>`:'-'}</td><td><div class="row-actions"><button class="edit" onclick="viewVenda(${v.id})">Ver</button>${me.cargo==='admin'&&v.status==='concluida'?`<button class="edit" onclick="fiscalVenda(${v.id})">Fiscal</button><button class="delete" onclick="cancelVenda(${v.id})">Cancelar</button>`:''}${me.cargo==='admin'&&v.status==='cancelada'?`<button class="delete" onclick="deleteVenda(${v.id})">Excluir</button>`:''}</div></td></tr>`}

renderVendas=function(){
 if(vendasMode101024!=='day')return;const query=(document.querySelector('#filtroVendas')?.value||'').trim().toLowerCase(),list=(Array.isArray(vendas)?vendas:[]).filter(v=>!query||[v.id,v.clienteNome,v.vendedorNome,v.usuarioNome,v.formaPagamento].join(' ').toLowerCase().includes(query));
 const body=document.querySelector('#tableVendas');if(body)body.innerHTML=list.map(linhaVenda101024).join('')||'<tr><td colspan="9"><div class="vendas-empty-101024"><b>Nenhuma venda neste dia</b><span>Escolha outra data ou faça uma nova venda no Caixa.</span></div></td></tr>';
 const qtd=document.querySelector('#vendasQuantidade101024');if(qtd)qtd.textContent=`${list.length} ${list.length===1?'venda':'vendas'}`;
};
function renderVendasMes101024(){const host=document.querySelector('#vendasMes101024'),dias=vendasConsulta101024.dias||[];if(!host)return;host.innerHTML=dias.map(d=>`<button type="button" class="vendas-day-card-101024" data-vendas-day="${d.data}"><div><span>${formatarData101024(d.data)}</span><b>${d.vendas} ${d.vendas===1?'venda':'vendas'}</b></div><div><span>Faturamento</span><strong>${money(d.total)}</strong></div><small>${d.canceladas?`${d.canceladas} cancelada${d.canceladas===1?'':'s'}`:'Sem cancelamentos'} · abrir dia →</small></button>`).join('')||'<div class="vendas-month-empty-101024"><b>Nenhuma venda neste mês</b><span>Selecione outro mês para consultar.</span></div>'}
loadVendas=async function(){
 const today=dataLocal101024(),dateInput=document.querySelector('#vendasData101024'),monthInput=document.querySelector('#vendasMesInput101024');if(dateInput&&!dateInput.value)dateInput.value=today;if(monthInput&&!monthInput.value)monthInput.value=today.slice(0,7);
 const query=vendasMode101024==='month'?`modo=mes&mes=${encodeURIComponent(monthInput?.value||today.slice(0,7))}`:`modo=dia&data=${encodeURIComponent(dateInput?.value||today)}`,response=await api(`/api/vendas/consulta?${query}`),data=await response.json();if(!response.ok)throw new Error(data.erro||'Não foi possível consultar as vendas.');vendasConsulta101024=data;resumoVendas101024(data.resumo);
 const monthHost=document.querySelector('#vendasMes101024'),dayHost=document.querySelector('#vendasDia101024'),search=document.querySelector('.vendas-search-101024'),dayBox=document.querySelector('#vendasDiaBox101024'),monthBox=document.querySelector('#vendasMesBox101024');
 if(vendasMode101024==='month'){vendas=[];monthHost.hidden=false;dayHost.hidden=true;search.hidden=true;dayBox.hidden=true;monthBox.hidden=false;renderVendasMes101024()}else{vendas=data.vendas||[];monthHost.hidden=true;dayHost.hidden=false;search.hidden=false;dayBox.hidden=false;monthBox.hidden=true;const title=document.querySelector('#vendasPeriodoTitulo101024');if(title)title.textContent=formatarData101024(data.data,true);renderVendas()}
 document.querySelectorAll('[data-vendas-mode]').forEach(b=>b.classList.toggle('active',b.dataset.vendasMode===vendasMode101024));
};
document.addEventListener('click',event=>{const mode=event.target.closest?.('[data-vendas-mode]');if(mode){vendasMode101024=mode.dataset.vendasMode;loadVendas();return}const day=event.target.closest?.('[data-vendas-day]');if(day){vendasMode101024='day';document.querySelector('#vendasData101024').value=day.dataset.vendasDay;loadVendas();return}if(event.target.closest?.('#vendasHoje101024')){vendasMode101024='day';document.querySelector('#vendasData101024').value=dataLocal101024();loadVendas()}},true);
document.addEventListener('change',event=>{if(event.target?.id==='vendasData101024'||event.target?.id==='vendasMesInput101024')loadVendas()},true);
'''
write("public/app.js", js)

css = read("public/style.css") + r'''

/* 10.10.24 - pagamento e consulta de vendas adaptados à personalização */
.pay101024-overlay{background:color-mix(in srgb,var(--topbar) 72%,transparent)!important;backdrop-filter:blur(7px)}.pay101024-card{width:min(660px,96vw);max-height:94vh;overflow:auto;border:1px solid color-mix(in srgb,var(--border) 78%,var(--accent));border-radius:20px;background:var(--card-bg);color:var(--text-main);box-shadow:0 32px 100px #0007}.pay101024-head{display:flex;justify-content:space-between;align-items:center;padding:18px 20px 14px;border-bottom:1px solid var(--border);background:linear-gradient(135deg,color-mix(in srgb,var(--accent) 12%,var(--card-bg)),var(--card-bg))}.pay101024-head span{font-size:10px;font-weight:900;letter-spacing:.12em;color:var(--accent)}.pay101024-head h3{margin:3px 0 0;font-size:24px}.pay101024-head button{border:0;background:transparent;color:var(--text-main);font-size:28px;cursor:pointer}.pay101024-balance{display:grid;grid-template-columns:1.3fr 1fr 1fr;gap:8px;padding:14px 20px}.pay101024-balance>div{padding:12px;border:1px solid var(--border);border-radius:12px;background:color-mix(in srgb,var(--page-bg) 58%,var(--card-bg));display:grid;gap:3px}.pay101024-balance span{font-size:10px;text-transform:uppercase;font-weight:800;color:var(--text-muted)}.pay101024-balance b{font-size:17px}.pay101024-balance .total{background:color-mix(in srgb,var(--accent) 11%,var(--card-bg));border-color:color-mix(in srgb,var(--accent) 30%,var(--border))}.pay101024-balance .total b{font-size:23px;color:var(--accent)}#pay101024ChangeCard.active{background:color-mix(in srgb,#19a45b 12%,var(--card-bg));border-color:color-mix(in srgb,#19a45b 38%,var(--border))}#pay101024ChangeCard.active b{color:#128049}.pay101024-entry{padding:0 20px 12px}.pay101024-entry label{margin:0 0 6px}.pay101024-entry>div{display:flex;align-items:center;border:1px solid color-mix(in srgb,var(--accent) 38%,var(--border));border-radius:12px;background:var(--card-bg);overflow:hidden}.pay101024-entry>div:focus-within{box-shadow:0 0 0 3px color-mix(in srgb,var(--accent) 12%,transparent);border-color:var(--accent)}.pay101024-entry>div span{padding-left:14px;font-weight:900;color:var(--accent)}.pay101024-entry input{margin:0!important;border:0!important;box-shadow:none!important;font-size:25px;font-weight:850;background:transparent!important;color:var(--text-main)}.pay101024-entry small{display:block;margin-top:6px;color:var(--text-muted);font-size:10px}.pay101024-method-title{display:flex;justify-content:space-between;gap:8px;align-items:center;padding:0 20px 8px}.pay101024-method-title span{font-size:10px;color:var(--text-muted)}.pay101024-methods{display:grid!important;grid-template-columns:repeat(4,1fr)!important;gap:8px!important;padding:0 20px}.pay101024-methods button{min-height:64px!important;border:1px solid var(--border)!important;border-radius:12px!important;background:color-mix(in srgb,var(--page-bg) 62%,var(--card-bg))!important;color:var(--text-main)!important;display:flex!important;flex-direction:column!important;align-items:center!important;justify-content:center!important;gap:5px!important;font-size:10px!important;font-weight:850!important}.pay101024-methods button:hover{border-color:var(--accent)!important;background:color-mix(in srgb,var(--accent) 9%,var(--card-bg))!important}.pay101024-methods button span{display:grid;place-items:center;width:28px;height:25px;border-radius:7px;background:color-mix(in srgb,var(--accent) 14%,var(--card-bg));color:var(--accent);font-size:10px}.pay101024-installments{display:flex;align-items:center;gap:10px;padding:10px 20px 4px}.pay101024-installments label{white-space:nowrap;font-size:11px}.pay101024-installments select{margin:0!important;min-height:36px;padding:7px!important}.pay101024-launched{margin:10px 20px;padding:12px;border:1px solid var(--border);border-radius:13px;background:color-mix(in srgb,var(--page-bg) 50%,var(--card-bg))}.pay101024-launched>div:first-child{display:flex;justify-content:space-between;gap:10px;margin-bottom:8px}.pay101024-launched small{font-size:10px;color:var(--text-muted)}.pay101024-empty{display:grid;gap:2px;text-align:center;padding:12px;color:var(--text-muted)}.pay101024-empty b{color:var(--text-main);font-size:11px}.pay101024-row{display:grid;grid-template-columns:32px 1fr 30px;align-items:center;gap:9px;padding:8px 0;border-top:1px solid var(--border)}.pay101024-row:first-child{border-top:0}.pay101024-method-icon{display:grid;place-items:center;width:30px;height:30px;border-radius:8px;background:color-mix(in srgb,var(--accent) 12%,var(--card-bg));color:var(--accent);font-size:9px;font-weight:900}.pay101024-row b,.pay101024-row small{display:block}.pay101024-row b{font-size:11px}.pay101024-row small{font-size:10px;color:var(--text-muted);margin-top:2px}.pay101024-row>button{border:0;background:transparent;color:var(--danger);font-size:20px;cursor:pointer}.pay101024-actions{display:flex;gap:10px;padding:4px 20px 20px}.pay101024-actions button{flex:1;min-height:45px}.pay101024-actions .primary:disabled{opacity:.45;cursor:not-allowed}.sale-success-101024{text-align:center;padding:8px 8px 2px}.sale-success-mark-101024{width:64px;height:64px;margin:0 auto 10px;border-radius:50%;display:grid;place-items:center;background:color-mix(in srgb,#18a45b 15%,var(--card-bg));border:1px solid color-mix(in srgb,#18a45b 38%,var(--border));color:#149052;font-size:34px;font-weight:900}.sale-success-101024>span{font-size:10px;font-weight:900;letter-spacing:.13em;color:var(--accent)}.sale-success-101024 h2{margin:4px 0 14px}.sale-success-change-101024{margin:auto;max-width:420px;padding:18px;border-radius:15px;border:1px solid color-mix(in srgb,var(--accent) 30%,var(--border));background:linear-gradient(135deg,color-mix(in srgb,var(--accent) 11%,var(--card-bg)),color-mix(in srgb,var(--page-bg) 55%,var(--card-bg)))}.sale-success-change-101024 small,.sale-success-change-101024 b{display:block}.sale-success-change-101024 small{color:var(--text-muted);font-weight:800}.sale-success-change-101024 b{margin-top:5px;font-size:37px;color:var(--accent)}.sale-success-101024 p{color:var(--text-muted);font-size:12px}.sale-success-actions-101024{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:16px}.sale-success-actions-101024 button{min-height:48px}.sale-success-actions-101024 kbd{margin-left:5px;padding:2px 5px;border-radius:5px;background:#ffffff22;border:1px solid currentColor;font-size:9px}.receipt-hidden-101024{position:fixed;left:-100000px;top:0;width:420px;pointer-events:none}
.vendas-section-101024{max-width:1320px}.vendas-filter-card-101024{padding:13px!important}.vendas-mode-101024{display:flex;gap:5px;margin-bottom:11px;padding:4px;border:1px solid var(--border);border-radius:11px;background:color-mix(in srgb,var(--page-bg) 62%,var(--card-bg));width:max-content}.vendas-mode-101024 button{min-width:105px;padding:8px 13px;border:0;border-radius:8px;background:transparent;color:var(--text-muted);font-weight:800;cursor:pointer}.vendas-mode-101024 button.active{background:var(--accent);color:#fff}.vendas-filters-101024{display:grid;grid-template-columns:190px minmax(240px,1fr) auto;gap:10px;align-items:end}.vendas-filters-101024>div[hidden]{display:none}.vendas-filters-101024 label{margin:0 0 4px;font-size:10px;text-transform:uppercase;color:var(--text-muted)}.vendas-filters-101024 input{margin:0!important;min-height:42px}.vendas-filters-101024>button{height:42px}.vendas-stats-101024{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:12px}.vendas-stats-101024>div{padding:13px 15px;border:1px solid var(--border);border-radius:13px;background:var(--card-bg);box-shadow:0 4px 14px #00000008}.vendas-stats-101024 span,.vendas-day-head-101024 span{display:block;font-size:9px;text-transform:uppercase;letter-spacing:.07em;font-weight:850;color:var(--text-muted)}.vendas-stats-101024 b{display:block;margin-top:5px;font-size:20px}.vendas-table-card-101024{padding:14px!important}.vendas-day-head-101024{display:flex;align-items:end;justify-content:space-between;gap:10px;margin-bottom:10px}.vendas-day-head-101024 b{display:block;margin-top:3px;text-transform:capitalize}.vendas-day-head-101024 small{color:var(--text-muted)}.vendas-table-scroll-101024{overflow:auto;max-height:calc(100vh - 360px);min-height:220px}.vendas-table-scroll-101024 th{position:sticky;top:0;z-index:1}.sale-change-101024{display:block;color:var(--text-muted);font-size:9px;margin-top:3px}.sale-status-101024{display:inline-flex;padding:5px 7px;border-radius:999px;font-size:9px;font-weight:900}.sale-status-101024.concluida{background:#e2f6ea;color:#137944}.sale-status-101024.cancelada{background:#fde8e8;color:#a52c2c}.vendas-empty-101024{display:grid;gap:4px;place-items:center;min-height:180px;color:var(--text-muted)}.vendas-empty-101024 b{color:var(--text-main)}.vendas-days-101024{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px}.vendas-day-card-101024{display:grid;grid-template-columns:1fr auto;gap:11px;padding:15px;border:1px solid var(--border);border-radius:14px;background:var(--card-bg);color:var(--text-main);text-align:left;cursor:pointer}.vendas-day-card-101024:hover{border-color:var(--accent);transform:translateY(-1px);box-shadow:0 7px 20px #0000000c}.vendas-day-card-101024 span,.vendas-day-card-101024 small{display:block;color:var(--text-muted);font-size:10px}.vendas-day-card-101024 b{display:block;margin-top:4px;font-size:16px}.vendas-day-card-101024 strong{display:block;margin-top:4px;color:var(--accent);font-size:16px}.vendas-day-card-101024 small{grid-column:1/-1;padding-top:8px;border-top:1px solid var(--border)}.vendas-month-empty-101024{grid-column:1/-1;display:grid;place-items:center;gap:4px;min-height:220px;border:1px dashed var(--border);border-radius:14px;color:var(--text-muted)}.vendas-month-empty-101024 b{color:var(--text-main)}
@media(max-width:900px){.pay101024-methods{grid-template-columns:repeat(2,1fr)!important}.vendas-days-101024{grid-template-columns:repeat(2,1fr)}.vendas-stats-101024{grid-template-columns:repeat(2,1fr)}}
@media(max-width:620px){.pay101024-balance{grid-template-columns:1fr 1fr}.pay101024-balance .total{grid-column:1/-1}.pay101024-method-title,.pay101024-launched>div:first-child{align-items:flex-start;flex-direction:column}.sale-success-actions-101024,.vendas-filters-101024,.vendas-days-101024{grid-template-columns:1fr}.vendas-mode-101024{width:100%}.vendas-mode-101024 button{flex:1}.vendas-table-scroll-101024{max-height:none}}
'''
write("public/style.css", css)

print("10.10.24: troco em dinheiro, pagamento personalizado e vendas leves por dia/mês.")
