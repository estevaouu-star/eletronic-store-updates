from pathlib import Path
import json

root=Path('app')
def read(p): return (root/p).read_text(encoding='utf-8')
def write(p,s): (root/p).write_text(s,encoding='utf-8')
def must_replace(s,a,b,label):
    if a not in s: raise RuntimeError(f'Trecho não encontrado: {label}')
    return s.replace(a,b,1)

pkg=json.loads(read('package.json'))
pkg['version']='10.3.0'
write('package.json',json.dumps(pkg,indent=2,ensure_ascii=False))

# 1) Corrige perda de foco na digitação do pagamento: atualizar apenas os totais,
# sem reconstruir os campos a cada tecla.
js=read('public/app.js')
old='''  const calc=pagamentoAplicado(),total=totalAtualVenda();
  $("#paymentModalTotal").textContent=money(total);$("#paymentModalRemaining").textContent=money(calc.restante||0);$("#paymentModalChange").textContent=money(calc.troco||0);$("#paymentModalChangeRow").hidden=!(calc.troco>0);
  const btn=$("#confirmPayment");if(btn)btn.disabled=Boolean(calc.erro)||calc.restante>0.009||calc.pagamentos.length===0;
  const msg=$("#paymentModalMessage");if(msg)msg.textContent=calc.erro||(calc.restante>0.009?`Falta ${money(calc.restante)} para completar o pagamento.`:(calc.troco>0?`Troco: ${money(calc.troco)}`:"Pagamento completo."));
}'''
new='''  updatePaymentSummary();
}
function updatePaymentSummary(){
  const calc=pagamentoAplicado(),total=totalAtualVenda();
  if($("#paymentModalTotal"))$("#paymentModalTotal").textContent=money(total);
  if($("#paymentModalRemaining"))$("#paymentModalRemaining").textContent=money(calc.restante||0);
  if($("#paymentModalChange"))$("#paymentModalChange").textContent=money(calc.troco||0);
  if($("#paymentModalChangeRow"))$("#paymentModalChangeRow").hidden=!(calc.troco>0);
  const btn=$("#confirmPayment");if(btn)btn.disabled=Boolean(calc.erro)||calc.restante>0.009||calc.pagamentos.length===0;
  const msg=$("#paymentModalMessage");if(msg)msg.textContent=calc.erro||(calc.restante>0.009?`Falta ${money(calc.restante)} para completar o pagamento.`:(calc.troco>0?`Troco: ${money(calc.troco)}`:"Pagamento completo."));
}'''
js=must_replace(js,old,new,'resumo do pagamento')
js=must_replace(js,
'document.addEventListener("input",e=>{if(e.target?.classList?.contains("pay-modal-value")){const i=Number(e.target.dataset.i);if(paymentLines[i])paymentLines[i].valor=Math.max(0,Number(e.target.value)||0);renderPaymentModal()}});',
'document.addEventListener("input",e=>{if(e.target?.classList?.contains("pay-modal-value")){const i=Number(e.target.dataset.i);if(paymentLines[i])paymentLines[i].valor=Math.max(0,Number(e.target.value)||0);updatePaymentSummary()}});',
'input do pagamento')
js=must_replace(js,
'document.addEventListener("change",e=>{if(e.target?.classList?.contains("pay-modal-method")){const i=Number(e.target.dataset.i);if(paymentLines[i])paymentLines[i].forma=e.target.value;renderPaymentModal()}});',
'document.addEventListener("change",e=>{if(e.target?.classList?.contains("pay-modal-method")){const i=Number(e.target.dataset.i);if(paymentLines[i])paymentLines[i].forma=e.target.value;updatePaymentSummary()}});',
'forma de pagamento')

# 2) Produtos com informação faltando.
# Critérios: código/nome vazios, marca ausente ou placeholder, categoria ausente/placeholder,
# preço de venda inválido e custo não informado. Código de barras é tratado como opcional.
old_render='''function renderProdutos(){const q=$("#filtroProdutos").value.toLowerCase(),st=$("#filtroStatusProduto").value;const a=produtos.filter(p=>(p.nome.toLowerCase().includes(q)||p.codigo.toLowerCase().includes(q)||p.marca.toLowerCase().includes(q))&&(!st||(st==="ativo"?p.ativo:!p.ativo)));$("#tableProdutos").innerHTML=a.map(p=>`<tr><td>${esc(p.codigo)}</td><td>${esc(p.codigoBarras||"-")}</td><td>${esc(p.nome)}</td><td>${esc(p.marca)}</td><td>${money(p.precoVenda)}</td><td>${p.estoque<=p.estoqueMinimo?"⚠️ ":""}${p.estoque}</td><td class="${p.ativo?"status-ok":"status-off"}">${p.ativo?"Ativo":"Inativo"}</td><td><div class="row-actions">${`<button class="edit" onclick="editProduto(${p.id})">Editar</button><button class="edit" onclick="stockProduto(${p.id})">Estoque</button>`}</div></td></tr>`).join("")}'''
new_render='''let filtroProdutosIncompletos=false;
function informacoesFaltantesProduto(p){
  const faltas=[];
  const marca=String(p.marca||"").trim().toLowerCase(),categoria=String(p.categoria||"").trim().toLowerCase();
  if(!String(p.codigo||"").trim())faltas.push("código interno");
  if(!String(p.nome||"").trim())faltas.push("nome");
  if(!marca||["não informada","nao informada","sem marca"].includes(marca))faltas.push("marca");
  if(!categoria||["importados","não informada","nao informada"].includes(categoria))faltas.push("categoria");
  if(!(Number(p.precoVenda)>0))faltas.push("preço de venda");
  if(!(Number(p.precoCusto)>0))faltas.push("preço de custo");
  return faltas;
}
function renderProdutos(){
  const q=$("#filtroProdutos").value.toLowerCase(),st=$("#filtroStatusProduto").value;
  const incompletos=produtos.filter(p=>informacoesFaltantesProduto(p).length);
  const btn=$("#produtosIncompletosBtn");if(btn){btn.textContent=`Faltando informação (${incompletos.length})`;btn.classList.toggle("active",filtroProdutosIncompletos)}
  const a=produtos.filter(p=>(p.nome.toLowerCase().includes(q)||p.codigo.toLowerCase().includes(q)||String(p.marca||"").toLowerCase().includes(q))&&(!st||(st==="ativo"?p.ativo:!p.ativo))&&(!filtroProdutosIncompletos||informacoesFaltantesProduto(p).length));
  $("#tableProdutos").innerHTML=a.map(p=>{const faltas=informacoesFaltantesProduto(p);return `<tr><td>${esc(p.codigo)}</td><td>${esc(p.codigoBarras||"-")}</td><td>${esc(p.nome)}${filtroProdutosIncompletos&&faltas.length?`<div class="missing-info">Falta: ${faltas.map(esc).join(", ")}</div>`:""}</td><td>${esc(p.marca)}</td><td>${money(p.precoVenda)}</td><td>${p.estoque<=p.estoqueMinimo?"⚠️ ":""}${p.estoque}</td><td class="${p.ativo?"status-ok":"status-off"}">${p.ativo?"Ativo":"Inativo"}</td><td><div class="row-actions"><button class="edit" onclick="editProduto(${p.id})">${filtroProdutosIncompletos?"Corrigir":"Editar"}</button><button class="edit" onclick="stockProduto(${p.id})">Estoque</button></div></td></tr>`}).join("")||`<tr><td colspan="8" class="muted">${filtroProdutosIncompletos?"Nenhum produto com informação faltando.":"Nenhum produto encontrado."}</td></tr>`;
}'''
js=must_replace(js,old_render,new_render,'lista de produtos')
js += '''\ndocument.addEventListener("click",e=>{if(e.target?.closest?.("#produtosIncompletosBtn")){e.preventDefault();filtroProdutosIncompletos=!filtroProdutosIncompletos;renderProdutos();return}});\n'''
write('public/app.js',js)

h=read('public/index.html')
h=must_replace(h,
'<div class="card"><div class="toolbar"><input id="filtroProdutos" placeholder="Buscar produto..."><select id="filtroStatusProduto"><option value="">Todos</option><option value="ativo">Ativos</option><option value="inativo">Inativos</option></select></div>',
'<div class="card"><div class="toolbar"><input id="filtroProdutos" placeholder="Buscar produto..."><select id="filtroStatusProduto"><option value="">Todos</option><option value="ativo">Ativos</option><option value="inativo">Inativos</option></select><button id="produtosIncompletosBtn" class="secondary small" type="button">Faltando informação (0)</button></div>',
'toolbar produtos')
write('public/index.html',h)

css=read('public/style.css')
css += '''\n#produtosIncompletosBtn.active{background:#fff3cd;border-color:#d6a600;color:#765500;font-weight:800}\n.missing-info{margin-top:4px;font-size:11px;color:#9a5b00;background:#fff6db;border-radius:6px;padding:3px 6px;display:inline-block}\n'''
write('public/style.css',css)
print('Patch 10.3.0 aplicado.')