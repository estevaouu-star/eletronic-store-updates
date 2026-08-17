from pathlib import Path
import json
root=Path('app')
def read(p): return (root/p).read_text(encoding='utf-8')
def write(p,s): (root/p).write_text(s,encoding='utf-8')

pkg=json.loads(read('package.json'));pkg['version']='10.9.6';write('package.json',json.dumps(pkg,indent=2,ensure_ascii=False))
html=read('public/index.html').replace('id="versionInfo" class="version-info">v10.9.5','id="versionInfo" class="version-info">v10.9.6',1)
write('public/index.html',html)

js=read('public/app.js').replace('const atual="10.9.5"','const atual="10.9.6"',1)

# Desativa a UI 10.9.5 problemática sem depender do HTML final.
js += r'''
// 10.9.6 - pagamento redesenhado, remove Faltando informação e corrige Venda Rápida
let pagamentos1096=[];
function totalVenda1096(){
 const txt=document.querySelector('#total')?.textContent||'0';
 return Number(txt.replace(/[^0-9,.-]/g,'').replace(/\./g,'').replace(',','.'))||0;
}
function pago1096(){return pagamentos1096.reduce((s,p)=>s+Number(p.valor||0),0)}
function money1096(v){return Number(v||0).toLocaleString('pt-BR',{style:'currency',currency:'BRL'})}
function removerUiAntiga1096(){
 document.querySelector('#filtroInfoProdutoBtn')?.remove();
 const old=document.querySelector('#checkoutFloat');if(old)old.remove();
 const oldBtn=document.querySelector('#openCheckout');if(oldBtn)oldBtn.remove();
}
function renderPagamentos1096(){
 const host=document.querySelector('#pagamentos1096');if(!host)return;
 if(!pagamentos1096.length){host.innerHTML='<div class="pay1096-empty">Nenhum pagamento lançado.</div>';return}
 host.innerHTML=pagamentos1096.map((p,i)=>`<div class="pay1096-row"><div><b>${esc(p.tipo)}</b><small>${money1096(p.valor)}</small></div><button type="button" data-rm-pay="${i}" title="Remover">×</button></div>`).join('');
}
function atualizarPagamento1096(){
 const total=totalVenda1096(),pago=pago1096(),rest=Math.max(0,total-pago);
 const a=document.querySelector('#pay1096Total'),b=document.querySelector('#pay1096Restante'),c=document.querySelector('#pay1096Valor');
 if(a)a.textContent=money1096(total);if(b)b.textContent=money1096(rest);if(c&&!c.value)c.value=rest.toFixed(2).replace('.',',');
 renderPagamentos1096();
 const fin=document.querySelector('#finish1096');if(fin)fin.disabled=!(total>0&&Math.abs(rest)<0.01);
}
function montarPagamento1096(){
 removerUiAntiga1096();
 const caixa=document.querySelector('#caixa'),totalRow=document.querySelector('.pdv1094-total');if(!caixa||!totalRow||document.querySelector('#openCheckout1096'))return;
 const cobrar=document.createElement('button');cobrar.id='openCheckout1096';cobrar.type='button';cobrar.className='primary pay1096-open';cobrar.textContent='COBRAR';totalRow.parentElement.appendChild(cobrar);
 const ov=document.createElement('div');ov.id='checkout1096';ov.className='pay1096-overlay hidden';ov.innerHTML=`<div class="pay1096-card" role="dialog" aria-modal="true">
   <div class="pay1096-title">PAGAMENTO</div>
   <div class="pay1096-summary"><div><span>TOTAL</span><b id="pay1096Total">R$ 0,00</b></div><div><span>RESTANTE</span><b id="pay1096Restante">R$ 0,00</b></div></div>
   <label class="pay1096-value-label">Valor deste pagamento</label><input id="pay1096Valor" class="pay1096-value" inputmode="decimal" autocomplete="off" placeholder="0,00">
   <div class="pay1096-help">Selecione uma forma de pagamento</div>
   <div class="pay1096-methods">
     <button type="button" data-pay1096="Dinheiro">DINHEIRO</button><button type="button" data-pay1096="PIX">PIX</button>
     <button type="button" data-pay1096="Débito">DÉBITO</button><button type="button" data-pay1096="Crédito">CRÉDITO</button>
     <button type="button" data-pay1096="Crédito parcelado">CRÉDITO PARCELADO</button><button type="button" data-pay1096="Outros">OUTROS</button>
   </div>
   <div id="pay1096OutroBox" class="pay1096-other hidden"><label>Qual é a outra forma?</label><input id="pay1096Outro" placeholder="Digite a forma de pagamento"><button id="addOutro1096" type="button">ADICIONAR</button></div>
   <div class="pay1096-paid-title">Pagamentos lançados</div><div id="pagamentos1096" class="pay1096-paid"></div>
   <div class="pay1096-actions"><button id="cancel1096" type="button" class="pay1096-cancel">CANCELAR</button><button id="finish1096" type="button" class="pay1096-finish">FINALIZAR</button></div>
 </div>`;
 document.body.appendChild(ov);atualizarPagamento1096();
}
function abrirPagamento1096(){
 if(!document.querySelector('#vendedorVenda')?.value)return toast('Selecione o vendedor antes de cobrar.');
 if(!cart.length&&!cartServicos.length)return toast('Adicione pelo menos um item antes de cobrar.');
 montarPagamento1096();pagamentos1096=[];document.querySelector('#checkout1096')?.classList.remove('hidden');document.body.classList.add('pay1096-lock');atualizarPagamento1096();setTimeout(()=>document.querySelector('#pay1096Valor')?.select(),30)
}
function fecharPagamento1096(){document.querySelector('#checkout1096')?.classList.add('hidden');document.body.classList.remove('pay1096-lock')}
function lerValor1096(){const el=document.querySelector('#pay1096Valor');return Number(String(el?.value||'').replace(/\./g,'').replace(',','.'))||0}
function addPagamento1096(tipo){
 let valor=lerValor1096(),rest=Math.max(0,totalVenda1096()-pago1096());if(!(valor>0))valor=rest;if(valor>rest+0.01)return toast('O valor informado é maior que o restante.');if(!(valor>0))return;
 pagamentos1096.push({tipo,valor});const inp=document.querySelector('#pay1096Valor');if(inp)inp.value='';atualizarPagamento1096();
}
async function finalizar1096(){
 const rest=Math.max(0,totalVenda1096()-pago1096());if(rest>0.01)return toast('Ainda existe valor restante.');
 const original=document.querySelector('#pay');if(original){original.value=pagamentos1096.length===1?pagamentos1096[0].tipo:'Múltiplos'}
 // Integra com o fluxo existente. Se houver split, preenche a estrutura interna de forma compatível.
 try{if(typeof splitPayments!=='undefined'){splitPayments=pagamentos1096.map(p=>({tipo:p.tipo,valor:p.valor}))}}catch{}
 fecharPagamento1096();await finish();
}
function corrigirVendaRapida1096(){
 // Corrige qualquer painel/modal existente identificado pelo texto Venda Rápida.
 const nodes=[...document.querySelectorAll('section,dialog,.modal,.card,.panel,[role="dialog"]')];
 for(const n of nodes){
   const txt=(n.textContent||'').toLowerCase();if(!txt.includes('venda rápida')&&!txt.includes('venda rapida'))continue;if(n.dataset.seller1096==='1')continue;n.dataset.seller1096='1';
   const select=document.createElement('select');select.className='quick1096-seller';select.innerHTML='<option value="">Selecione o vendedor...</option>';
   const principal=document.querySelector('#vendedorVenda');if(principal)select.innerHTML=principal.innerHTML;
   const box=document.createElement('div');box.className='quick1096-sellerbox';box.innerHTML='<label>Vendedor</label>';box.appendChild(select);
   const first=n.querySelector('input,select,button');first?.parentElement?.insertBefore(box,first)||n.prepend(box);
   n.addEventListener('click',e=>{const b=e.target.closest('button');if(!b)return;const t=(b.textContent||'').toLowerCase();if(/finalizar|vender|confirmar|cobrar/.test(t)&&!select.value){e.preventDefault();e.stopImmediatePropagation();toast('Selecione o vendedor na Venda Rápida.')}},true);
 }
}
const obs1096=new MutationObserver(()=>{montarPagamento1096();corrigirVendaRapida1096();removerUiAntiga1096()});
document.addEventListener('DOMContentLoaded',()=>setTimeout(()=>{montarPagamento1096();corrigirVendaRapida1096()},500));setTimeout(()=>{montarPagamento1096();corrigirVendaRapida1096()},900);obs1096.observe(document.documentElement,{childList:true,subtree:true});
document.addEventListener('click',e=>{
 if(e.target.closest?.('#openCheckout1096')){e.preventDefault();abrirPagamento1096();return}
 if(e.target.closest?.('#cancel1096')){e.preventDefault();fecharPagamento1096();return}
 const m=e.target.closest?.('[data-pay1096]');if(m){e.preventDefault();const tipo=m.dataset.pay1096;if(tipo==='Outros'){document.querySelector('#pay1096OutroBox')?.classList.remove('hidden');document.querySelector('#pay1096Outro')?.focus()}else addPagamento1096(tipo);return}
 if(e.target.closest?.('#addOutro1096')){e.preventDefault();const nome=document.querySelector('#pay1096Outro')?.value?.trim();if(!nome)return toast('Digite a forma de pagamento.');addPagamento1096(nome);document.querySelector('#pay1096OutroBox')?.classList.add('hidden');return}
 const rm=e.target.closest?.('[data-rm-pay]');if(rm){pagamentos1096.splice(Number(rm.dataset.rmPay),1);atualizarPagamento1096();return}
 if(e.target.closest?.('#finish1096')){e.preventDefault();finalizar1096();return}
});
'''
write('public/app.js',js)

css=read('public/style.css')+r'''
/* 10.9.6 pagamento estilo PDV */
#filtroInfoProdutoBtn{display:none!important}.pay1096-open{width:100%;min-height:54px;margin-top:12px;font-size:17px;font-weight:950}.pay1096-overlay{position:fixed;inset:0;z-index:12000;background:rgba(0,0,0,.72);display:grid;place-items:center;padding:16px}.pay1096-overlay.hidden{display:none!important}.pay1096-card{width:min(520px,96vw);max-height:94vh;overflow:auto;background:#f7f7f7;color:#26313d;border-radius:14px;padding:20px 26px;box-shadow:0 30px 100px rgba(0,0,0,.5)}.pay1096-title{background:#082f63;color:#fff;text-align:center;font-weight:900;padding:11px;border-radius:5px;margin-bottom:17px}.pay1096-summary{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-bottom:17px}.pay1096-summary>div{display:flex;align-items:baseline;gap:7px}.pay1096-summary span{font-size:12px;font-weight:800;color:#6d7278}.pay1096-summary b{font-size:26px;font-weight:500}.pay1096-value-label{display:block;font-size:12px;font-weight:800;margin-bottom:5px}.pay1096-value{width:100%;height:44px;text-align:center;font-size:24px;background:#fff;color:#1f2a35;border:1px solid #abb3bc;border-radius:5px}.pay1096-help{text-align:center;font-size:12px;font-weight:700;color:#70757b;margin:16px 0 9px}.pay1096-methods{display:grid;grid-template-columns:1fr 1fr;gap:8px 12px}.pay1096-methods button,.pay1096-other button{min-height:40px;border:0;border-radius:4px;background:#11567f;color:#fff;font-weight:900;cursor:pointer}.pay1096-other{margin-top:10px;padding:10px;border:1px solid #ccd2d8;border-radius:7px;background:#fff}.pay1096-other.hidden{display:none}.pay1096-other label{display:block;font-size:12px;font-weight:800;margin-bottom:5px}.pay1096-other input{width:100%;margin-bottom:8px}.pay1096-paid-title{margin-top:18px;font-size:12px;font-weight:900;color:#70757b}.pay1096-paid{margin-top:7px;display:grid;gap:7px}.pay1096-empty{padding:12px;border:1px dashed #c3c8cd;border-radius:7px;text-align:center;color:#80868b}.pay1096-row{display:flex;justify-content:space-between;align-items:center;padding:9px 10px;background:#fff;border:1px solid #d9dde1;border-radius:6px}.pay1096-row>div{display:flex;gap:10px;align-items:center}.pay1096-row small{font-weight:800}.pay1096-row button{border:0;background:transparent;color:#d82828;font-size:22px;font-weight:900;cursor:pointer}.pay1096-actions{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:18px}.pay1096-actions button{min-height:42px;border:0;border-radius:5px;color:#fff;font-weight:900}.pay1096-cancel{background:#ff2b2b}.pay1096-finish{background:#0b9b18}.pay1096-finish:disabled{opacity:.45}.pay1096-lock{overflow:hidden}.quick1096-sellerbox{margin:8px 0 12px;padding:10px;border:1px solid var(--border);border-radius:8px;background:var(--card-bg)}.quick1096-sellerbox label{display:block;font-size:11px;font-weight:800;margin-bottom:5px}.quick1096-seller{width:100%}
'''
write('public/style.css',css)
print('10.9.6: pagamento redesenhado, Faltando informação removido e vendedor obrigatório na Venda Rápida.')