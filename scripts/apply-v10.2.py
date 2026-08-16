from pathlib import Path
import re, json

root=Path("app")
def read(p): return (root/p).read_text(encoding="utf-8")
def write(p,s): (root/p).write_text(s,encoding="utf-8")
def must_replace(s,a,b,label):
    if a not in s: raise RuntimeError(f"Trecho não encontrado: {label}")
    return s.replace(a,b,1)

pkg=json.loads(read("package.json"))
pkg["version"]="10.2.0"
pkg.setdefault("build",{})["publish"]=[{"provider":"github","owner":"estevaouu-star","repo":"eletronic-store-updates","releaseType":"release"}]
write("package.json",json.dumps(pkg,indent=2,ensure_ascii=False))

h=read("public/index.html")
pat=r'<div class="payment-box">.*?</div>\s*<button id="finish" class="primary">Finalizar venda</button>'
repl='''<div class="payment-launch">
        <div><label>Pagamento</label><small>Escolha os valores e formas na próxima etapa.</small></div>
        <button id="finish" class="primary">Ir para pagamento</button>
      </div>'''
h,n=re.subn(pat,repl,h,count=1,flags=re.S)
if n!=1: raise RuntimeError("Bloco de pagamento do Caixa não encontrado")
write("public/index.html",h)

s=read("src/server.ts")
s=must_replace(s,'pagamentos?:{forma:string;valor:number}[];','pagamentos?:{forma:string;valor:number;recebido?:number}[]; troco?:number;',"tipo Venda")
s=must_replace(s,'formaPagamento,pagamentos=[],clienteId=','formaPagamento,pagamentos=[],troco=0,clienteId=',"payload venda")
s=must_replace(s,
'pagamentosVenda=pagamentos.map((p:any)=>({forma:String(p.forma||""),valor:Math.round((Number(p.valor)||0)*100)/100})).filter((p:any)=>p.forma&&p.valor>0);',
'pagamentosVenda=pagamentos.map((p:any)=>({forma:String(p.forma||""),valor:Math.round((Number(p.valor)||0)*100)/100,recebido:p.recebido==null?undefined:Math.round((Number(p.recebido)||0)*100)/100})).filter((p:any)=>p.forma&&p.valor>0);',
"normalização pagamentos")
needle='''      const soma=Math.round(pagamentosVenda.reduce((a,p)=>a+p.valor,0)*100)/100;
      if(Math.abs(soma-Math.round(totalVenda*100)/100)>0.009)throw new Error(`Os pagamentos precisam somar exatamente ${totalVenda.toLocaleString("pt-BR",{style:"currency",currency:"BRL"})}.`);'''
rep='''      const soma=Math.round(pagamentosVenda.reduce((a,p)=>a+p.valor,0)*100)/100;
      if(Math.abs(soma-Math.round(totalVenda*100)/100)>0.009)throw new Error(`Os pagamentos precisam somar exatamente ${totalVenda.toLocaleString("pt-BR",{style:"currency",currency:"BRL"})}.`);
      for(const p of pagamentosVenda){
        if(p.recebido!=null){
          if(p.forma!=="Dinheiro")throw new Error("Valor recebido só pode ser informado para pagamento em dinheiro.");
          if(p.recebido+0.009<p.valor)throw new Error("O valor recebido em dinheiro não pode ser menor que o valor aplicado.");
        }
      }'''
s=must_replace(s,needle,rep,"validação pagamentos")
needle='''    const formaResumo=pagamentosVenda.length>1?"Misto":pagamentosVenda[0].forma;
    const v:Venda={lojaId,vendedorId:vendedor.id,vendedorNome:vendedor.nome,id:db.seq.venda++,clienteId:cliente?.id||null,clienteNome:cliente?.nome||"Consumidor final",compradorDocumento:String(compradorDocumento||""),compradorTelefone:String(compradorTelefone||""),compradorEmail:String(compradorEmail||""),usuarioId:u.id,usuarioNome:u.nome,subtotal,acrescimo:adicional,desconto:d,total:totalVenda,formaPagamento:formaResumo,pagamentos:pagamentosVenda,itens:itensVenda,status:"concluida",criadoEm:now()};'''
rep='''    const formaResumo=pagamentosVenda.length>1?"Misto":pagamentosVenda[0].forma;
    const trocoCalculado=Math.round(pagamentosVenda.reduce((acc,p)=>acc+(p.forma==="Dinheiro"&&p.recebido!=null?Math.max(0,p.recebido-p.valor):0),0)*100)/100;
    const v:Venda={lojaId,vendedorId:vendedor.id,vendedorNome:vendedor.nome,id:db.seq.venda++,clienteId:cliente?.id||null,clienteNome:cliente?.nome||"Consumidor final",compradorDocumento:String(compradorDocumento||""),compradorTelefone:String(compradorTelefone||""),compradorEmail:String(compradorEmail||""),usuarioId:u.id,usuarioNome:u.nome,subtotal,acrescimo:adicional,desconto:d,total:totalVenda,formaPagamento:formaResumo,pagamentos:pagamentosVenda,troco:trocoCalculado,itens:itensVenda,status:"concluida",criadoEm:now()};'''
s=must_replace(s,needle,rep,"gravação venda")
write("src/server.ts",s)

js=read("public/app.js")
start=js.find('let splitPaymentLines=')
end=js.find('function showReceipt',start)
if start<0 or end<0: raise RuntimeError("Lógica de pagamento 10.1 não encontrada")
new_block=r'''
let paymentLines=[];

function totalAtualVenda(){
  const subProdutos=cart.reduce((sum,i)=>{const p=produtos.find(x=>x.id===i.produtoId);return sum+(p.precoVenda+(Number(i.acrescimoUnitario)||0))*i.quantidade},0);
  const subServicos=cartServicos.reduce((sum,i)=>{const s=servicos.find(x=>x.id===i.servicoId);return sum+(s.preco+(Number(i.acrescimoUnitario)||0))*i.quantidade},0);
  const acrescimo=Number($("#surcharge")?.value)||0;
  return Math.max(0,subProdutos+subServicos+acrescimo-calcularDesconto(subProdutos+subServicos+acrescimo).valor);
}
function pagamentoAplicado(){
  const total=totalAtualVenda();let restante=total,troco=0;const pagamentos=[];
  for(const linha of paymentLines){
    const informado=Math.max(0,Number(linha.valor)||0);if(informado<=0)continue;
    if(linha.forma==="Dinheiro"){
      const aplicado=Math.min(restante,informado);
      if(aplicado>0)pagamentos.push({forma:"Dinheiro",valor:Math.round(aplicado*100)/100,recebido:Math.round(informado*100)/100});
      restante=Math.max(0,restante-aplicado);troco+=Math.max(0,informado-aplicado);
    }else{
      const aplicado=Math.min(restante,informado);
      if(aplicado>0)pagamentos.push({forma:linha.forma,valor:Math.round(aplicado*100)/100});
      restante=Math.max(0,restante-aplicado);
      if(informado>aplicado)return {erro:"Somente dinheiro pode ultrapassar o valor restante.",pagamentos:[],restante,troco:0};
    }
  }
  return {pagamentos,restante:Math.round(restante*100)/100,troco:Math.round(troco*100)/100};
}
function renderPaymentModal(){
  const host=$("#paymentRows");if(!host)return;
  host.innerHTML=paymentLines.map((p,i)=>`<div class="pay-modal-row">
    <select class="pay-modal-method" data-i="${i}"><option ${p.forma==="PIX"?"selected":""}>PIX</option><option ${p.forma==="Dinheiro"?"selected":""}>Dinheiro</option><option ${p.forma==="Débito"?"selected":""}>Débito</option><option ${p.forma==="Crédito"?"selected":""}>Crédito</option></select>
    <div class="pay-value-wrap"><span>R$</span><input class="pay-modal-value" data-i="${i}" type="number" min="0" step=".01" value="${Number(p.valor||0)||""}" placeholder="0,00"></div>
    ${paymentLines.length>1?`<button class="pay-remove" data-i="${i}" type="button" title="Remover">×</button>`:""}
  </div>`).join("");
  const calc=pagamentoAplicado(),total=totalAtualVenda();
  $("#paymentModalTotal").textContent=money(total);$("#paymentModalRemaining").textContent=money(calc.restante||0);$("#paymentModalChange").textContent=money(calc.troco||0);$("#paymentModalChangeRow").hidden=!(calc.troco>0);
  const btn=$("#confirmPayment");if(btn)btn.disabled=Boolean(calc.erro)||calc.restante>0.009||calc.pagamentos.length===0;
  const msg=$("#paymentModalMessage");if(msg)msg.textContent=calc.erro||(calc.restante>0.009?`Falta ${money(calc.restante)} para completar o pagamento.`:(calc.troco>0?`Troco: ${money(calc.troco)}`:"Pagamento completo."));
}
function openPaymentModal(){
  if(!caixaAtual)return toast("Abra o caixa antes de vender.");if(!cart.length&&!cartServicos.length)return toast("Adicione produtos ou serviços ao carrinho.");
  paymentLines=[{forma:"PIX",valor:totalAtualVenda()}];
  openModal("Finalizar pagamento",`<div class="payment-modal">
    <div class="payment-total-highlight"><span>Total da venda</span><strong id="paymentModalTotal">${money(totalAtualVenda())}</strong></div>
    <p class="muted">Informe quanto será pago em cada forma. Adicione outras formas até completar o total.</p>
    <div id="paymentRows"></div>
    <button id="addPaymentRow" class="secondary" type="button">+ Adicionar outra forma de pagamento</button>
    <div class="payment-status"><div><span>Falta pagar</span><b id="paymentModalRemaining">R$ 0,00</b></div><div id="paymentModalChangeRow" hidden><span>Troco</span><b id="paymentModalChange">R$ 0,00</b></div></div>
    <div id="paymentModalMessage" class="payment-message"></div>
    <div class="modal-actions"><button class="secondary" type="button" onclick="closeModal()">Cancelar</button><button id="confirmPayment" class="primary" type="button">Confirmar pagamento</button></div>
  </div>`);renderPaymentModal();
}
async function submitSaleWithPayments(){
  const calc=pagamentoAplicado();if(calc.erro)return toast(calc.erro);if(calc.restante>0.009)return toast(`Ainda faltam ${money(calc.restante)}.`);if(!calc.pagamentos.length)return toast("Informe uma forma de pagamento.");
  const subProdutos=cart.reduce((sum,i)=>{const p=produtos.find(x=>x.id===i.produtoId);return sum+(p.precoVenda+(Number(i.acrescimoUnitario)||0))*i.quantidade},0);
  const subServicos=cartServicos.reduce((sum,i)=>{const s=servicos.find(x=>x.id===i.servicoId);return sum+(s.preco+(Number(i.acrescimoUnitario)||0))*i.quantidade},0);
  const acrescimo=Number($("#surcharge")?.value)||0;const descontoCalc=calcularDesconto(subProdutos+subServicos+acrescimo);
  const r=await api("/api/vendas",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({itens:cart,servicos:cartServicos,desconto:descontoCalc.valor,descontoPercentual:$("#discountType")?.value==="percent"?descontoCalc.percentual:null,acrescimo,formaPagamento:calc.pagamentos.length>1?"Misto":calc.pagamentos[0].forma,pagamentos:calc.pagamentos,troco:calc.troco,clienteId:$("#clienteVenda").value||null,vendedorId:$("#vendedorVenda")?.value||null,compradorDocumento:$("#compradorDocumento").value,compradorTelefone:$("#compradorTelefone").value,compradorEmail:$("#compradorEmail").value})});
  const d=await r.json();if(!r.ok)return toast(d.erro);
  closeModal();cart=[];cartServicos=[];$("#desc").value=0;if($("#discountType"))$("#discountType").value="value";if($("#surcharge"))$("#surcharge").value=0;$("#compradorDocumento").value="";$("#compradorTelefone").value="";$("#compradorEmail").value="";limparSelecoesPdvAposVenda();await Promise.all([loadProdutos(),loadDashboard()]);renderCart();showReceipt(d);if(printerSettings.autoPrint)setTimeout(()=>directPrintReceipt(),120);toast(calc.troco>0?`Venda #${d.id} finalizada! Troco: ${money(calc.troco)}`:`Venda #${d.id} finalizada!`);
}
async function finish(){openPaymentModal()}
'''
js=js[:start]+new_block+js[end:]
js=must_replace(js,
'${v.pagamentos.map(p=>`${esc(p.forma)}: ${money(p.valor)}`).join("<br>")}',
'${v.pagamentos.map(p=>`${esc(p.forma)}: ${money(p.valor)}${p.forma==="Dinheiro"&&p.recebido!=null&&p.recebido>p.valor?` (recebido ${money(p.recebido)})`:""}`).join("<br>")}${v.troco?`<br>Troco: ${money(v.troco)}`:""}',
"comprovante")
js=re.sub(r'\ndocument\.addEventListener\("change",e=>\{\s*if\(e\.target\?\.id==="splitPayment"\).*?document\.addEventListener\("click",e=>\{.*?\}\);\s*','\n',js,count=1,flags=re.S)
js=js.replace('''renderSplitPayments();return;
  }
  const rem=e.target?.closest?.(".split-pay-remove");
  if(rem){e.preventDefault();const i=Number(rem.dataset.i);if(splitPaymentLines.length>2){splitPaymentLines.splice(i,1);renderSplitPayments()}return}
});
''','')
js += r'''
document.addEventListener("input",e=>{if(e.target?.classList?.contains("pay-modal-value")){const i=Number(e.target.dataset.i);if(paymentLines[i])paymentLines[i].valor=Math.max(0,Number(e.target.value)||0);renderPaymentModal()}});
document.addEventListener("change",e=>{if(e.target?.classList?.contains("pay-modal-method")){const i=Number(e.target.dataset.i);if(paymentLines[i])paymentLines[i].forma=e.target.value;renderPaymentModal()}});
document.addEventListener("click",e=>{
  if(e.target?.closest?.("#addPaymentRow")){e.preventDefault();paymentLines.push({forma:"Dinheiro",valor:0});renderPaymentModal();return}
  const rem=e.target?.closest?.(".pay-remove");if(rem){e.preventDefault();const i=Number(rem.dataset.i);if(paymentLines.length>1){paymentLines.splice(i,1);renderPaymentModal()}return}
  if(e.target?.closest?.("#confirmPayment")){e.preventDefault();submitSaleWithPayments();return}
});
'''
write("public/app.js",js)

css=read("public/style.css")
css += r'''
.payment-launch{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-top:10px;padding-top:10px;border-top:1px solid var(--border)}
.payment-launch label{display:block;font-weight:800}.payment-launch small{display:block;color:var(--text-muted);margin-top:2px}
.payment-modal{display:grid;gap:12px}.payment-total-highlight{display:flex;align-items:center;justify-content:space-between;padding:14px;border-radius:12px;background:var(--surface-soft,var(--card-bg));border:1px solid var(--border)}.payment-total-highlight strong{font-size:22px}
.pay-modal-row{display:grid;grid-template-columns:minmax(130px,.8fr) minmax(130px,1fr) 34px;gap:8px;align-items:center;margin-bottom:8px}
.pay-modal-row select,.pay-modal-row input{margin:0!important}.pay-value-wrap{display:flex;align-items:center;border:1px solid var(--border);border-radius:9px;overflow:hidden;background:var(--card-bg)}.pay-value-wrap span{padding:0 8px;color:var(--text-muted);font-weight:700}.pay-value-wrap input{border:0!important;box-shadow:none!important}
.pay-remove{height:36px;border:0;border-radius:9px;background:#fee2e2;color:#a51616;font-size:20px;cursor:pointer}
.payment-status{display:grid;grid-template-columns:1fr 1fr;gap:8px}.payment-status>div{display:flex;justify-content:space-between;gap:12px;padding:10px 12px;border-radius:10px;background:var(--surface-soft,var(--card-bg));border:1px solid var(--border)}.payment-status b{font-size:15px}.payment-message{min-height:18px;font-weight:700;color:var(--text-muted)}
#confirmPayment:disabled{opacity:.45;cursor:not-allowed}
@media(max-width:600px){.pay-modal-row{grid-template-columns:1fr 1fr 34px}.payment-status{grid-template-columns:1fr}.payment-launch{align-items:stretch;flex-direction:column}}
'''
write("public/style.css",css)
print("Patch 10.2.0 aplicado.")
