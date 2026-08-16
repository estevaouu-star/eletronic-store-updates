const fs=require("fs"), path=require("path");
const root=process.argv[2]||"app";
const read=p=>fs.readFileSync(path.join(root,p),"utf8");
const write=(p,s)=>fs.writeFileSync(path.join(root,p),s,"utf8");
function mustReplace(s,a,b,label){if(!s.includes(a))throw new Error("Trecho não encontrado: "+label);return s.replace(a,b)}

let pkg=JSON.parse(read("package.json"));
pkg.version="10.1.0";
pkg.build=pkg.build||{};
pkg.build.publish=[{provider:"github",owner:"estevaouu-star",repo:"eletronic-store-updates",releaseType:"release"}];
write("package.json",JSON.stringify(pkg,null,2));

let server=read("src/server.ts");
server=mustReplace(server,
`  subtotal:number; acrescimo:number; desconto:number; total:number; formaPagamento:string;
  itens:ItemVenda[];`,
`  subtotal:number; acrescimo:number; desconto:number; total:number; formaPagamento:string;
  pagamentos?:{forma:string;valor:number}[];
  itens:ItemVenda[];`,"tipo Venda");
server=mustReplace(server,
`const {itens,servicos:servicosVenda=[],desconto=0,acrescimo=0,formaPagamento,clienteId=null,vendedorId=null,compradorDocumento="",compradorTelefone="",compradorEmail=""}=req.body;`,
`const {itens,servicos:servicosVenda=[],desconto=0,acrescimo=0,formaPagamento,pagamentos=[],clienteId=null,vendedorId=null,compradorDocumento="",compradorTelefone="",compradorEmail=""}=req.body;`,"payload venda");
server=mustReplace(server,
`if((!Array.isArray(itens)||!itens.length)&&(!Array.isArray(servicosVenda)||!servicosVenda.length)||!formaPagamento)return res.status(400).json({erro:"Venda inválida."});`,
`if((!Array.isArray(itens)||!itens.length)&&(!Array.isArray(servicosVenda)||!servicosVenda.length))return res.status(400).json({erro:"Venda inválida."});`,"validacao venda");
server=mustReplace(server,
`    const cliente=db.clientes.find(c=>c.lojaId===lojaId&&c.id===Number(clienteId));
    const v:Venda={lojaId,vendedorId:vendedor.id,vendedorNome:vendedor.nome,id:db.seq.venda++,clienteId:cliente?.id||null,clienteNome:cliente?.nome||"Consumidor final",compradorDocumento:String(compradorDocumento||""),compradorTelefone:String(compradorTelefone||""),compradorEmail:String(compradorEmail||""),usuarioId:u.id,usuarioNome:u.nome,subtotal,acrescimo:adicional,desconto:d,total:subtotal+adicional-d,formaPagamento:String(formaPagamento),itens:itensVenda,status:"concluida",criadoEm:now()};`,
`    const cliente=db.clientes.find(c=>c.lojaId===lojaId&&c.id===Number(clienteId));
    const totalVenda=subtotal+adicional-d;
    const formasPermitidas=new Set(["PIX","Dinheiro","Débito","Crédito"]);
    let pagamentosVenda:{forma:string;valor:number}[]=[];
    if(Array.isArray(pagamentos)&&pagamentos.length){
      pagamentosVenda=pagamentos.map((p:any)=>({forma:String(p.forma||""),valor:Math.round((Number(p.valor)||0)*100)/100})).filter((p:any)=>p.forma&&p.valor>0);
      if(!pagamentosVenda.length||pagamentosVenda.some(p=>!formasPermitidas.has(p.forma)))throw new Error("Forma de pagamento inválida.");
      const soma=Math.round(pagamentosVenda.reduce((a,p)=>a+p.valor,0)*100)/100;
      if(Math.abs(soma-Math.round(totalVenda*100)/100)>0.009)throw new Error(\`Os pagamentos precisam somar exatamente \${totalVenda.toLocaleString("pt-BR",{style:"currency",currency:"BRL"})}.\`);
    }else{
      const forma=String(formaPagamento||"");
      if(!formasPermitidas.has(forma))throw new Error("Selecione uma forma de pagamento.");
      pagamentosVenda=[{forma,valor:Math.round(totalVenda*100)/100}];
    }
    const formaResumo=pagamentosVenda.length>1?"Misto":pagamentosVenda[0].forma;
    const v:Venda={lojaId,vendedorId:vendedor.id,vendedorNome:vendedor.nome,id:db.seq.venda++,clienteId:cliente?.id||null,clienteNome:cliente?.nome||"Consumidor final",compradorDocumento:String(compradorDocumento||""),compradorTelefone:String(compradorTelefone||""),compradorEmail:String(compradorEmail||""),usuarioId:u.id,usuarioNome:u.nome,subtotal,acrescimo:adicional,desconto:d,total:totalVenda,formaPagamento:formaResumo,pagamentos:pagamentosVenda,itens:itensVenda,status:"concluida",criadoEm:now()};`,"criacao venda");
write("src/server.ts",server);

let html=read("public/index.html");
html=mustReplace(html,
`      <label>Forma de pagamento</label>
      <select id="pay"><option>PIX</option><option>Dinheiro</option><option>Débito</option><option>Crédito</option></select>`,
`      <div class="payment-box">
        <div class="payment-head">
          <label>Forma de pagamento</label>
          <label class="payment-split-toggle"><input id="splitPayment" type="checkbox"> Dividir pagamento</label>
        </div>
        <div id="singlePaymentBox">
          <select id="pay"><option>PIX</option><option>Dinheiro</option><option>Débito</option><option>Crédito</option></select>
        </div>
        <div id="splitPaymentBox" class="split-payment-box" hidden>
          <div id="splitPaymentRows"></div>
          <div class="split-payment-summary"><span>Distribuído</span><b id="splitPaymentDistributed">R$ 0,00</b><span>Restante</span><b id="splitPaymentRemaining">R$ 0,00</b></div>
          <button id="addPaymentMethod" class="secondary small" type="button">+ Outra forma</button>
        </div>
      </div>`,"UI pagamento");
write("public/index.html",html);

let app=read("public/app.js");
const marker=`async function finish(){`;
if(!app.includes(marker))throw new Error("finish nao encontrada");
const helpers=`
let splitPaymentLines=[{forma:"PIX",valor:0},{forma:"Dinheiro",valor:0}];
function totalAtualVenda(){
  const subProdutos=cart.reduce((sum,i)=>{const p=produtos.find(x=>x.id===i.produtoId);return sum+(p.precoVenda+(Number(i.acrescimoUnitario)||0))*i.quantidade},0);
  const subServicos=cartServicos.reduce((sum,i)=>{const s=servicos.find(x=>x.id===i.servicoId);return sum+(s.preco+(Number(i.acrescimoUnitario)||0))*i.quantidade},0);
  const acrescimo=Number($("#surcharge")?.value)||0;
  return Math.max(0,subProdutos+subServicos+acrescimo-calcularDesconto(subProdutos+subServicos+acrescimo).valor);
}
function renderSplitPayments(){
  const box=$("#splitPaymentRows");if(!box)return;
  const total=totalAtualVenda();
  box.innerHTML=splitPaymentLines.map((p,i)=>\`<div class="split-payment-row"><select class="split-pay-method" data-i="\${i}"><option \${p.forma==="PIX"?"selected":""}>PIX</option><option \${p.forma==="Dinheiro"?"selected":""}>Dinheiro</option><option \${p.forma==="Débito"?"selected":""}>Débito</option><option \${p.forma==="Crédito"?"selected":""}>Crédito</option></select><input class="split-pay-value" data-i="\${i}" type="number" min="0" step=".01" value="\${Number(p.valor||0).toFixed(2)}">\${splitPaymentLines.length>2?\`<button class="icon-danger split-pay-remove" data-i="\${i}" type="button">×</button>\`:""}</div>\`).join("");
  const dist=Math.round(splitPaymentLines.reduce((a,p)=>a+(Number(p.valor)||0),0)*100)/100;
  const rem=Math.round((total-dist)*100)/100;
  if($("#splitPaymentDistributed"))$("#splitPaymentDistributed").textContent=money(dist);
  if($("#splitPaymentRemaining")){$("#splitPaymentRemaining").textContent=money(rem);$("#splitPaymentRemaining").classList.toggle("payment-ok",Math.abs(rem)<0.01);$("#splitPaymentRemaining").classList.toggle("payment-bad",Math.abs(rem)>=0.01)}
}
function toggleSplitPayment(){const on=Boolean($("#splitPayment")?.checked);if($("#singlePaymentBox"))$("#singlePaymentBox").hidden=on;if($("#splitPaymentBox"))$("#splitPaymentBox").hidden=!on;if(on){const total=totalAtualVenda();if(!splitPaymentLines.some(p=>Number(p.valor)>0))splitPaymentLines=[{forma:"PIX",valor:0},{forma:"Dinheiro",valor:total}];renderSplitPayments()}}
function pagamentosDaVenda(){if(!$("#splitPayment")?.checked)return null;return splitPaymentLines.map(p=>({forma:p.forma,valor:Math.round((Number(p.valor)||0)*100)/100})).filter(p=>p.valor>0)}
function resetPagamentos(){if($("#splitPayment"))$("#splitPayment").checked=false;splitPaymentLines=[{forma:"PIX",valor:0},{forma:"Dinheiro",valor:0}];toggleSplitPayment()}
`;
app=app.replace(marker,helpers+marker);
app=mustReplace(app,
`async function finish(){if(!caixaAtual)return toast("Abra o caixa antes de vender.");if(!cart.length&&!cartServicos.length)return toast("Adicione produtos ou serviços ao carrinho.");`,
`async function finish(){if(!caixaAtual)return toast("Abra o caixa antes de vender.");if(!cart.length&&!cartServicos.length)return toast("Adicione produtos ou serviços ao carrinho.");const pagamentos=pagamentosDaVenda();if($("#splitPayment")?.checked){const soma=Math.round((pagamentos||[]).reduce((a,p)=>a+p.valor,0)*100)/100,totalEsperado=Math.round(totalAtualVenda()*100)/100;if((pagamentos||[]).length<2)return toast("Informe pelo menos duas formas de pagamento.");if(Math.abs(soma-totalEsperado)>0.009)return toast(\`Falta distribuir \${money(totalEsperado-soma)} no pagamento.\`);}`,"finish inicio");
app=mustReplace(app,`formaPagamento:$("#pay").value,clienteId:`,`formaPagamento:$("#pay").value,pagamentos,clienteId:`,"payload frontend");
app=mustReplace(app,`if($("#surcharge"))$("#surcharge").value=0;$("#compradorDocumento")`,`if($("#surcharge"))$("#surcharge").value=0;resetPagamentos();$("#compradorDocumento")`,"reset pagamento");
app=mustReplace(app,'<br>Pagamento: ${esc(v.formaPagamento)}</p>','<br>Pagamento: ${esc(v.formaPagamento)}${Array.isArray(v.pagamentos)&&v.pagamentos.length>1?`<br>${v.pagamentos.map(p=>`${esc(p.forma)}: ${money(p.valor)}`).join("<br>")}`:""}</p>',"comprovante");
app += `
document.addEventListener("change",e=>{if(e.target?.id==="splitPayment"){toggleSplitPayment();return}if(e.target?.classList?.contains("split-pay-method")){const i=Number(e.target.dataset.i);if(splitPaymentLines[i]){splitPaymentLines[i].forma=e.target.value;renderSplitPayments()}return}});
document.addEventListener("input",e=>{if(e.target?.classList?.contains("split-pay-value")){const i=Number(e.target.dataset.i);if(!splitPaymentLines[i])return;splitPaymentLines[i].valor=Math.max(0,Number(e.target.value)||0);if(splitPaymentLines.length===2){const outro=i===0?1:0,total=totalAtualVenda();splitPaymentLines[outro].valor=Math.max(0,Math.round((total-splitPaymentLines[i].valor)*100)/100)}renderSplitPayments()}});
document.addEventListener("click",e=>{if(e.target?.closest?.("#addPaymentMethod")){e.preventDefault();if(splitPaymentLines.length>=4)return toast("Máximo de 4 formas por venda.");splitPaymentLines.push({forma:"PIX",valor:0});renderSplitPayments();return}const rem=e.target?.closest?.(".split-pay-remove");if(rem){e.preventDefault();const i=Number(rem.dataset.i);if(splitPaymentLines.length>2){splitPaymentLines.splice(i,1);renderSplitPayments()}return}});
`;
write("public/app.js",app);

let css=read("public/style.css");
css += `
.payment-box{margin-top:10px;padding:10px;border:1px solid var(--border);border-radius:11px;background:var(--surface-soft,var(--card-bg))}
.payment-head{display:flex;align-items:center;justify-content:space-between;gap:10px;margin-bottom:6px}
.payment-split-toggle{display:flex!important;align-items:center;gap:6px;margin:0!important;font-size:11px!important;font-weight:700}
.payment-split-toggle input{width:auto!important;min-height:0!important;margin:0}
.split-payment-box{display:grid;gap:8px}
.split-payment-row{display:grid;grid-template-columns:minmax(110px,1fr) minmax(100px,.7fr) 30px;gap:7px;align-items:center;margin-bottom:6px}
.split-payment-row select,.split-payment-row input{margin:0!important;min-width:0}
.icon-danger{border:0;background:#fee2e2;color:#a51616;border-radius:8px;height:34px;font-size:20px;cursor:pointer}
.split-payment-summary{display:grid;grid-template-columns:auto 1fr auto 1fr;gap:7px;align-items:center;padding:7px 9px;background:var(--card-bg);border-radius:8px;font-size:11px}
.split-payment-summary b{text-align:right}.payment-ok{color:#17833b}.payment-bad{color:#b33a3a}
@media(max-width:600px){.split-payment-row{grid-template-columns:1fr 1fr 30px}.payment-head{align-items:flex-start;flex-direction:column}.split-payment-summary{grid-template-columns:auto 1fr}}
`;
write("public/style.css",css);
console.log("Atualização 10.1.0 aplicada");