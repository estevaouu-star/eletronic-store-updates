from pathlib import Path
import json

root=Path('app')
def read(p): return (root/p).read_text(encoding='utf-8')
def write(p,s): (root/p).write_text(s,encoding='utf-8')
def must(s,a,b,label):
    if a not in s: raise RuntimeError(f'Trecho não encontrado: {label}')
    return s.replace(a,b,1)

pkg=json.loads(read('package.json'));pkg['version']='10.5.0';write('package.json',json.dumps(pkg,indent=2,ensure_ascii=False))

# Backend: guardar e validar quantidade de parcelas do crédito.
s=read('src/server.ts')
s=must(s,
'pagamentos?:{forma:string;valor:number;recebido?:number}[]; troco?:number;',
'pagamentos?:{forma:string;valor:number;recebido?:number;parcelas?:number}[]; troco?:number;',
'tipo parcelas na venda')
s=must(s,
'let pagamentosVenda:{forma:string;valor:number;recebido?:number}[]=[];',
'let pagamentosVenda:{forma:string;valor:number;recebido?:number;parcelas?:number}[]=[];',
'tipo parcelas pagamentosVenda')
s=must(s,
'pagamentosVenda=pagamentos.map((p:any)=>({forma:String(p.forma||""),valor:Math.round((Number(p.valor)||0)*100)/100,recebido:p.recebido==null?undefined:Math.round((Number(p.recebido)||0)*100)/100})).filter((p:any)=>p.forma&&p.valor>0);',
'pagamentosVenda=pagamentos.map((p:any)=>({forma:String(p.forma||""),valor:Math.round((Number(p.valor)||0)*100)/100,recebido:p.recebido==null?undefined:Math.round((Number(p.recebido)||0)*100)/100,parcelas:String(p.forma||"")==="Crédito"?Math.max(1,Math.min(12,Math.trunc(Number(p.parcelas)||1))):undefined})).filter((p:any)=>p.forma&&p.valor>0);',
'normalizar parcelas')
needle='''      for(const p of pagamentosVenda){
        if(p.recebido!=null){
          if(p.forma!=="Dinheiro")throw new Error("Valor recebido só pode ser informado para pagamento em dinheiro.");
          if(p.recebido+0.009<p.valor)throw new Error("O valor recebido em dinheiro não pode ser menor que o valor aplicado.");
        }
      }'''
rep='''      for(const p of pagamentosVenda){
        if(p.recebido!=null){
          if(p.forma!=="Dinheiro")throw new Error("Valor recebido só pode ser informado para pagamento em dinheiro.");
          if(p.recebido+0.009<p.valor)throw new Error("O valor recebido em dinheiro não pode ser menor que o valor aplicado.");
        }
        if(p.forma==="Crédito"){
          const n=Math.trunc(Number(p.parcelas)||1);
          if(n<1||n>12)throw new Error("O crédito deve ser parcelado entre 1x e 12x.");
          p.parcelas=n;
        }else p.parcelas=undefined;
      }'''
s=must(s,needle,rep,'validacao parcelas')
write('src/server.ts',s)

# Frontend: cada linha de Crédito ganha seletor de 1x a 12x.
js=read('public/app.js')
js=must(js,
'''  host.innerHTML=paymentLines.map((p,i)=>`<div class="pay-modal-row">
    <select class="pay-modal-method" data-i="${i}"><option ${p.forma==="PIX"?"selected":""}>PIX</option><option ${p.forma==="Dinheiro"?"selected":""}>Dinheiro</option><option ${p.forma==="Débito"?"selected":""}>Débito</option><option ${p.forma==="Crédito"?"selected":""}>Crédito</option></select>
    <div class="pay-value-wrap"><span>R$</span><input class="pay-modal-value" data-i="${i}" type="number" min="0" step=".01" value="${Number(p.valor||0)||""}" placeholder="0,00"></div>
    ${paymentLines.length>1?`<button class="pay-remove" data-i="${i}" type="button" title="Remover">×</button>`:""}
  </div>`).join("");''',
'''  host.innerHTML=paymentLines.map((p,i)=>`<div class="pay-modal-row ${p.forma==="Crédito"?"has-installments":""}">
    <select class="pay-modal-method" data-i="${i}"><option ${p.forma==="PIX"?"selected":""}>PIX</option><option ${p.forma==="Dinheiro"?"selected":""}>Dinheiro</option><option ${p.forma==="Débito"?"selected":""}>Débito</option><option ${p.forma==="Crédito"?"selected":""}>Crédito</option></select>
    <div class="pay-value-wrap"><span>R$</span><input class="pay-modal-value" data-i="${i}" type="number" min="0" step=".01" value="${Number(p.valor||0)||""}" placeholder="0,00"></div>
    ${p.forma==="Crédito"?`<select class="pay-modal-installments" data-i="${i}" title="Parcelas">${Array.from({length:12},(_,n)=>`<option value="${n+1}" ${(Number(p.parcelas)||1)===n+1?"selected":""}>${n+1}x</option>`).join("")}</select>`:""}
    ${paymentLines.length>1?`<button class="pay-remove" data-i="${i}" type="button" title="Remover">×</button>`:""}
  </div>`).join("");''',
'linha de pagamento parcelado')
js=must(js,
'if(aplicado>0)pagamentos.push({forma:linha.forma,valor:Math.round(aplicado*100)/100});',
'if(aplicado>0)pagamentos.push({forma:linha.forma,valor:Math.round(aplicado*100)/100,...(linha.forma==="Crédito"?{parcelas:Math.max(1,Math.min(12,Math.trunc(Number(linha.parcelas)||1)))}:{})});',
'parcelas no payload frontend')
js=must(js,
'paymentLines=[{forma:"PIX",valor:totalAtualVenda()}];',
'paymentLines=[{forma:"PIX",valor:totalAtualVenda(),parcelas:1}];',
'parcelas padrao')
js=must(js,
'document.addEventListener("change",e=>{if(e.target?.classList?.contains("pay-modal-method")){const i=Number(e.target.dataset.i);if(paymentLines[i])paymentLines[i].forma=e.target.value;updatePaymentSummary()}});',
'document.addEventListener("change",e=>{if(e.target?.classList?.contains("pay-modal-method")){const i=Number(e.target.dataset.i);if(paymentLines[i]){paymentLines[i].forma=e.target.value;if(e.target.value==="Crédito"&&!paymentLines[i].parcelas)paymentLines[i].parcelas=1}renderPaymentModal();return}if(e.target?.classList?.contains("pay-modal-installments")){const i=Number(e.target.dataset.i);if(paymentLines[i])paymentLines[i].parcelas=Math.max(1,Math.min(12,Number(e.target.value)||1));updatePaymentSummary();return}});',
'eventos parcelas')
js=must(js,
'paymentLines.push({forma:"Dinheiro",valor:0});',
'paymentLines.push({forma:"Dinheiro",valor:0,parcelas:1});',
'linha adicional parcelas')
# Exibir parcelas no comprovante.
js=must(js,
'${v.pagamentos.map(p=>`${esc(p.forma)}: ${money(p.valor)}${p.forma==="Dinheiro"&&p.recebido!=null&&p.recebido>p.valor?` (recebido ${money(p.recebido)})`:""}`).join("<br>")}${v.troco?`<br>Troco: ${money(v.troco)}`:""}',
'${v.pagamentos.map(p=>`${esc(p.forma)}${p.forma==="Crédito"&&p.parcelas?` ${p.parcelas}x`:""}: ${money(p.valor)}${p.forma==="Dinheiro"&&p.recebido!=null&&p.recebido>p.valor?` (recebido ${money(p.recebido)})`:""}`).join("<br>")}${v.troco?`<br>Troco: ${money(v.troco)}`:""}',
'parcelas comprovante')
write('public/app.js',js)

css=read('public/style.css')
css += '''\n.pay-modal-row.has-installments{grid-template-columns:minmax(115px,1fr) minmax(120px,1fr) 76px 34px}\n.pay-modal-installments{min-width:70px;margin:0!important}\n@media(max-width:620px){.pay-modal-row.has-installments{grid-template-columns:1fr 1fr}.pay-modal-row.has-installments .pay-remove{grid-column:2;justify-self:end}}\n'''
write('public/style.css',css)
print('Patch 10.5.0 aplicado: crédito parcelado de 1x a 12x.')
