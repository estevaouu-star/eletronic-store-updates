from pathlib import Path
import json

root = Path("app")


def read(path: str) -> str:
    return (root / path).read_text(encoding="utf-8")


def write(path: str, content: str) -> None:
    (root / path).write_text(content, encoding="utf-8")


pkg = json.loads(read("package.json"))
pkg["version"] = "10.10.25"
write("package.json", json.dumps(pkg, indent=2, ensure_ascii=False))

html = read("public/index.html").replace(
    'id="versionInfo" class="version-info">v10.10.24',
    'id="versionInfo" class="version-info">v10.10.25',
    1,
)
write("public/index.html", html)

server = read("src/server.ts")
old_consulta = '''app.get("/api/vendas/consulta",auth,(req,res)=>{
  const lojaId=lojaIdReq(req),modo=String(req.query.modo||"dia")==="mes"?"mes":"dia";'''
new_consulta = '''app.get("/api/vendas/consulta",auth,(req,res)=>{
  res.setHeader("Cache-Control","no-store, no-cache, must-revalidate");
  const lojaId=lojaIdReq(req),modo=String(req.query.modo||"dia")==="mes"?"mes":"dia";'''
if old_consulta not in server:
    raise SystemExit("Consulta de vendas 10.10.24 não encontrada.")
server = server.replace(old_consulta, new_consulta, 1)
write("src/server.ts", server)

main = read("electron/main.cjs")
old_print_css = '''    .receipt-total{display:flex;justify-content:space-between;font-size:${width===58?14:16}px;font-weight:700;border-top:1px dashed #000;margin-top:5px;padding-top:5px}
  </style>'''
new_print_css = '''    .receipt-total{display:flex;justify-content:space-between;font-size:${width===58?14:16}px;font-weight:700;border-top:1px dashed #000;margin-top:5px;padding-top:5px}
    .receipt-kicker{text-align:center;font-size:8px;font-weight:700;letter-spacing:.12em;margin:3px 0}.receipt-doc-number{text-align:center;font-size:13px;font-weight:900;margin:2px 0 5px}.receipt-section{margin-top:6px;padding-top:5px;border-top:1px dashed #555}.receipt-section-title{font-size:8px;font-weight:900;letter-spacing:.1em;margin-bottom:3px}.receipt-row{display:flex;justify-content:space-between;gap:7px;padding:1px 0;font-size:${width===58?9:10}px}.receipt-row span:first-child{color:#333;flex:0 0 auto}.receipt-row b{text-align:right;overflow-wrap:anywhere}.receipt-text{font-size:${width===58?9:10}px;line-height:1.3;white-space:normal;overflow-wrap:anywhere}.receipt-emphasis{margin-top:6px;padding:6px;border:1px solid #000}.receipt-emphasis .receipt-row{font-size:${width===58?11:12}px}.receipt-signature{margin:18px auto 0;width:78%;padding-top:4px;border-top:1px solid #000;text-align:center;font-size:8px}.receipt-note{margin-top:6px!important;font-size:8px!important;line-height:1.25}.receipt-items td:first-child{overflow-wrap:anywhere}.receipt-payment{padding:2px 0;border-bottom:1px dotted #999}.receipt-payment:last-child{border-bottom:0}
  </style>'''
if old_print_css not in main:
    raise SystemExit("CSS térmico esperado não encontrado.")
main = main.replace(old_print_css, new_print_css, 1)
write("electron/main.cjs", main)

js = read("public/app.js").replace(
    'const atual="10.10.24"', 'const atual="10.10.25"', 1
)
old_cloud_poll = 'setInterval(()=>{if(token&&me)loadCloudStatus()},5000);'
new_cloud_poll = 'setInterval(()=>{if(token&&me&&!document.hidden)loadCloudStatus()},15000);'
if old_cloud_poll not in js:
    raise SystemExit("Monitor de nuvem esperado não encontrado.")
js = js.replace(old_cloud_poll, new_cloud_poll, 1)
js += r'''

// 10.10.25 - histórico sem cartões antigos, impressão somente em OS real e comprovantes organizados.
const loadVendasBase101025=loadVendas;
loadVendas=async function(){
 await loadVendasBase101025();
 const month=document.querySelector('#vendasMes101024'),day=document.querySelector('#vendasDia101024');
 if(vendasMode101024==='day'&&month){month.hidden=true;month.replaceChildren()}
 if(vendasMode101024==='month'&&day)day.hidden=true;
};

function logoComprovante101025(){const src=aparencia.logoComprovanteDataUrl||aparencia.logoDataUrl;return src?`<div class="receipt-logo"><img src="${src}" alt="Logo"></div>`:''}
function linhaRecibo101025(label,value){return value?`<div class="receipt-row"><span>${esc(label)}</span><b>${esc(value)}</b></div>`:''}
function dataHoraRecibo101025(value){return new Date(value).toLocaleString('pt-BR',{dateStyle:'short',timeStyle:'short'})}

showReceipt=function(v){
 const pagamentos=Array.isArray(v.pagamentos)&&v.pagamentos.length?v.pagamentos:[{forma:v.formaPagamento,valor:v.total}],troco=Number(v.troco)||0;
 const paymentHtml=pagamentos.map(p=>`<div class="receipt-payment">${linhaRecibo101025(p.forma+(p.forma==='Crédito'&&p.parcelas?` · ${p.parcelas}x`:''),money(p.valor))}${p.forma==='Dinheiro'&&p.recebido!=null?linhaRecibo101025('Recebido',money(p.recebido)):''}</div>`).join('');
 const items=(Array.isArray(v.itens)?v.itens:[]).map(i=>`<tr><td><b>${esc(i.nomeProduto)}</b><br><small>${money(i.precoUnitario)}${i.acrescimoUnitario?` + ${money(i.acrescimoUnitario)} acréscimo`:''}</small></td><td>${i.quantidade}</td><td>${money(i.subtotal)}</td></tr>`).join('');
 const receipt=`<div class="receipt receipt-structured-101025" id="receiptPrint">${logoComprovante101025()}<h2>${esc(config.nomeLoja||aparencia.nomeSistema||'Eletromix')}</h2>${config.cnpj?`<p>CNPJ: ${esc(config.cnpj)}</p>`:''}${config.endereco?`<p>${esc(config.endereco)}</p>`:''}<div class="receipt-kicker">COMPROVANTE DE VENDA</div><div class="receipt-doc-number">VENDA #${v.id}</div><p>${dataHoraRecibo101025(v.criadoEm)}</p><div class="receipt-section"><div class="receipt-section-title">ATENDIMENTO</div>${linhaRecibo101025('Cliente',v.clienteNome||'Consumidor final')}${linhaRecibo101025('Vendedor',v.vendedorNome||v.usuarioNome)}${linhaRecibo101025('CPF/CNPJ',v.compradorDocumento)}${linhaRecibo101025('Telefone',v.compradorTelefone)}${linhaRecibo101025('E-mail',v.compradorEmail)}${linhaRecibo101025('Endereço',v.compradorEndereco)}</div><div class="receipt-section"><div class="receipt-section-title">ITENS</div><table class="receipt-items"><thead><tr><th>Descrição</th><th>Qtd.</th><th>Total</th></tr></thead><tbody>${items}</tbody></table></div><div class="receipt-section"><div class="receipt-section-title">RESUMO</div>${linhaRecibo101025('Subtotal',money(v.subtotal))}${Number(v.acrescimo)?linhaRecibo101025('Acréscimo',money(v.acrescimo)):''}${Number(v.desconto)?linhaRecibo101025('Desconto','− '+money(v.desconto)):''}</div><div class="receipt-section"><div class="receipt-section-title">PAGAMENTO</div>${paymentHtml}${troco?`<div class="receipt-emphasis">${linhaRecibo101025('TROCO',money(troco))}</div>`:''}</div><div class="receipt-total"><span>TOTAL</span><span>${money(v.total)}</span></div>${config.rodapeComprovante?`<p class="receipt-note">${esc(config.rodapeComprovante)}</p>`:''}<p class="receipt-note">Obrigado pela preferência.</p></div>`;
 openModal(`Comprovante da venda #${v.id}`,`${receipt}<div class="modal-actions"><button class="secondary" onclick="closeModal()">Fechar</button><button class="primary" id="receiptPrintBtn" onclick="printReceipt()">Imprimir</button></div>`);
};

function osAtual101025(row){const id=Number(row?.dataset?.osId||row?.getAttribute?.('data-os-id'));return ordensServico.find(o=>Number(o.id)===id)||null}
function osReceipt101025(row,kind){
 const o=osAtual101025(row);if(!o)return '';
 const garantia=kind==='garantia',warranty=garantia?garantirGarantia101017(row):null,title=garantia?'VIA DE GARANTIA':'VIA DO CLIENTE';
 return `<div class="receipt receipt-structured-101025">${logoComprovante101025()}<h2>${esc(config.nomeLoja||aparencia.nomeSistema||'Eletromix')}</h2>${config.cnpj?`<p>CNPJ: ${esc(config.cnpj)}</p>`:''}${config.endereco?`<p>${esc(config.endereco)}</p>`:''}<div class="receipt-kicker">ORDEM DE SERVIÇO · ${title}</div><div class="receipt-doc-number">OS #${o.id}</div><p>Emitida em ${dataHoraRecibo101025(new Date())}</p><div class="receipt-section"><div class="receipt-section-title">CLIENTE</div>${linhaRecibo101025('Nome',o.clienteNome)}${linhaRecibo101025('Telefone',o.telefone||'Não informado')}</div><div class="receipt-section"><div class="receipt-section-title">APARELHO</div>${linhaRecibo101025('Tipo',o.aparelho)}${linhaRecibo101025('Marca',o.marca||'Não informada')}${linhaRecibo101025('Modelo',o.modelo||'Não informado')}</div><div class="receipt-section"><div class="receipt-section-title">SERVIÇO</div>${linhaRecibo101025('Serviço',o.servicoNome||'Diagnóstico')}${linhaRecibo101025('Status',o.status)}${linhaRecibo101025('Valor',money(o.valor))}<div class="receipt-text"><b>Relato do cliente</b><br>${esc(o.problemaRelatado||'Não informado')}</div></div>${garantia?`<div class="receipt-emphasis"><div class="receipt-section-title">GARANTIA DO SERVIÇO</div>${linhaRecibo101025('Início',fmtDate101015(new Date(warranty.inicio)))}${linhaRecibo101025('Válida até',fmtDate101015(new Date(warranty.fim)))}</div><p class="receipt-note">Garantia de 3 meses referente ao serviço executado nesta Ordem de Serviço. Apresente esta via quando precisar do atendimento de garantia.</p>`:`<p class="receipt-note">Guarde esta via para acompanhar o atendimento e retirar o aparelho.</p>`}<div class="receipt-signature">Assinatura do cliente</div></div>`;
}

osRows101015=function(){return [...document.querySelectorAll('#osList101023 .os-card-101023[data-os-id]')]};
syncOSPrint101020=function(){
 const section=document.querySelector('#ordensServico');if(!section)return;
 section.querySelectorAll('.os-print-actions-101015,.os-via-unica-101017').forEach(x=>x.remove());
 section.querySelectorAll('.os-print-actions-101020').forEach(box=>{if(!box.closest('.os-card-101023[data-os-id]'))box.remove()});
 osRows101015().forEach(row=>{let box=row.querySelector(':scope > .os-print-actions-101020');row.querySelectorAll('.os-print-actions-101020').forEach((x,i)=>{if(i>0)x.remove()});if(box)return;box=document.createElement('div');box.className='os-print-actions-101020';box.innerHTML='<button type="button" class="secondary os-via-cliente-101020">Imprimir via do cliente</button><button type="button" class="primary os-via-garantia-101020">Imprimir via de garantia</button>';row.appendChild(box)});
};
imprimirOSDireto101020=async function(row,kind,button){
 const ordem=osAtual101025(row);if(!ordem)return toast('Selecione uma ordem de serviço para imprimir.');
 if(osPrintInFlight101020)return toast('A impressão da OS já foi enviada. Aguarde um instante.');if(!window.desktopPrinter)return toast('Módulo de impressão do Windows não está disponível.');
 const original=button?.textContent||'',html=osReceipt101025(row,kind);osPrintInFlight101020=true;if(button){button.disabled=true;button.textContent='Imprimindo...'}
 try{loadPrinterSettings();const result=await window.desktopPrinter.print({html,deviceName:printerSettings.deviceName,paperWidth:printerSettings.paperWidth,itemCount:1});if(!result?.success)throw new Error(result?.failureReason||'A impressora não respondeu.');if(result.deviceName){printerSettings.deviceName=result.deviceName;savePrinterSettings()}toast(kind==='garantia'?'Via de garantia enviada para a impressora.':'Via do cliente enviada para a impressora.')}catch(e){console.error('[OS térmica 101025]',e);toast(`Falha ao imprimir: ${String(e?.message||e)}`)}finally{osPrintInFlight101020=false;if(button){button.disabled=false;button.textContent=original}}
};
setTimeout(syncOSPrint101020,0);

// Desempenho 10.10.25 - remove observadores legados redundantes e abre o Caixa primeiro.
try{[obs1096,vrObs1097,obs10100,obs10101,obs10102,obs10103,obs10104].forEach(observer=>observer?.disconnect?.())}catch(e){console.warn('[performance101025 observers]',e)}
const hardwareFraco101025=(Number(navigator.hardwareConcurrency)||4)<=4||(Number(navigator.deviceMemory)||4)<=4;
document.documentElement.classList.toggle('performance-lite-101025',hardwareFraco101025);

let bootPromise101025=null;
function tarefaOciosa101025(fn){
 if(typeof requestIdleCallback==='function')requestIdleCallback(fn,{timeout:1400});else setTimeout(fn,350);
}
boot=async function(){
 if(bootPromise101025)return bootPromise101025;
 bootPromise101025=(async()=>{
  renderEsIcons();
  await Promise.all([loadAparencia(),loadConfig(),loadProdutos(),loadServicos(),loadClientes(),loadVendedores(),loadCaixa(),loadLojas()]);
  renderCart();applyPdvLocks();
  tarefaOciosa101025(()=>{if(!me)return;Promise.allSettled([loadDashboard(),...(me.cargo==='admin'?[loadUsuarios()]:[])]).catch(()=>{});renderEsIcons()});
  return true;
 })();
 try{return await bootPromise101025}finally{bootPromise101025=null}
};
window.loadAll=boot;

// Várias tentativas antigas de restauração podem acordar juntas no início. Uma só faz o trabalho.
const restoreAuthBase101025=restoreAuth101010;
let restoreAuthPromise101025=null;
restoreAuth101010=async function(){
 if(me&&token)return true;
 if(restoreAuthPromise101025)return restoreAuthPromise101025;
 restoreAuthPromise101025=Promise.resolve(restoreAuthBase101025()).finally(()=>{restoreAuthPromise101025=null});
 return restoreAuthPromise101025;
};
'''
write("public/app.js", js)

css = read("public/style.css") + r'''

/* 10.10.25 - estado correto de Vendas e comprovantes organizados */
#vendasMes101024[hidden],#vendasDia101024[hidden],#vendasDiaBox101024[hidden],#vendasMesBox101024[hidden],.vendas-search-101024[hidden]{display:none!important}
.receipt-structured-101025 .receipt-kicker{text-align:center;margin:7px 0 2px;font-size:10px;font-weight:900;letter-spacing:.1em;color:var(--text-muted)}.receipt-structured-101025 .receipt-doc-number{text-align:center;font-size:17px;font-weight:900;margin-bottom:6px}.receipt-structured-101025 .receipt-section{margin-top:9px;padding-top:7px;border-top:1px dashed var(--border)}.receipt-structured-101025 .receipt-section-title{margin-bottom:5px;font-size:9px;font-weight:900;letter-spacing:.1em;color:var(--text-muted)}.receipt-structured-101025 .receipt-row{display:flex;justify-content:space-between;gap:12px;padding:2px 0;font-size:11px}.receipt-structured-101025 .receipt-row span:first-child{color:var(--text-muted)}.receipt-structured-101025 .receipt-row b{text-align:right;overflow-wrap:anywhere}.receipt-structured-101025 .receipt-text{margin-top:6px;font-size:11px;line-height:1.4;overflow-wrap:anywhere}.receipt-structured-101025 .receipt-payment{padding:3px 0;border-bottom:1px dotted var(--border)}.receipt-structured-101025 .receipt-emphasis{margin-top:7px;padding:8px;border:1px solid var(--text-main);border-radius:5px}.receipt-structured-101025 .receipt-signature{width:78%;margin:26px auto 0;padding-top:5px;border-top:1px solid var(--text-main);text-align:center;font-size:9px}.receipt-structured-101025 .receipt-note{font-size:9px;line-height:1.35}.receipt-structured-101025 .receipt-items td:first-child{overflow-wrap:anywhere}
.performance-lite-101025 *{scroll-behavior:auto!important}.performance-lite-101025 .section{animation:none!important}.performance-lite-101025 header,.performance-lite-101025 .modal,.performance-lite-101025 .pay101024-overlay{backdrop-filter:none!important}.performance-lite-101025 .card,.performance-lite-101025 .settings-block,.performance-lite-101025 .modal-card,.performance-lite-101025 .pay101024-card,.performance-lite-101025 .primary,.performance-lite-101025 .product,.performance-lite-101025 aside,.performance-lite-101025 header{box-shadow:none!important}.performance-lite-101025 .card,.performance-lite-101025 .nav,.performance-lite-101025 button,.performance-lite-101025 input,.performance-lite-101025 select,.performance-lite-101025 textarea,.performance-lite-101025 .product{transition:none!important}
'''
write("public/style.css", css)

print("10.10.25: histórico limpo, botões de OS corretos e comprovantes organizados.")
