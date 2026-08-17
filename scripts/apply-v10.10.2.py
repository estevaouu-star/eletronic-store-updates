from pathlib import Path
import json
root=Path('app')
def read(p): return (root/p).read_text(encoding='utf-8')
def write(p,s): (root/p).write_text(s,encoding='utf-8')

pkg=json.loads(read('package.json'));pkg['version']='10.10.2';write('package.json',json.dumps(pkg,indent=2,ensure_ascii=False))
html=read('public/index.html').replace('id="versionInfo" class="version-info">v10.10.1','id="versionInfo" class="version-info">v10.10.2',1);write('public/index.html',html)

js=read('public/app.js').replace('const atual="10.10.1"','const atual="10.10.2"',1)
js += r'''
// 10.10.2 - remove TODO comportamento residual da antiga Venda Rapida e torna F1/F2 confiaveis.
function corrigirVendaRapida1096(){document.querySelectorAll('.quick1096-sellerbox,.quick1096-seller').forEach(n=>n.remove())}
function limparVendaRapidaResidual10102(){
 document.querySelectorAll('.quick1096-sellerbox,.quick1096-seller,.smart-pdv-commandbar,.vr1097-root,.vr1097-shell,#vr1097Picker').forEach(n=>n.remove());
 document.querySelector('#caixa')?.classList.remove('smart-pdv');
}
function picker10102(kind){
 const seller=kind==='seller',src=document.querySelector(seller?'#vendedorVenda':'#clienteVenda');if(!src)return toast(seller?'Vendedores não carregados.':'Clientes não carregados.');
 document.querySelector('#picker10102')?.remove();
 const opts=[...src.options];const ov=document.createElement('div');ov.id='picker10102';ov.className='picker10102-overlay';
 ov.innerHTML=`<div class="picker10102-card"><div class="picker10102-head"><b>${seller?'VENDEDOR — F1':'CLIENTE — F2'}</b><button type="button" data-close10102>×</button></div><input data-filter10102 autocomplete="off" placeholder="Pesquisar..."><div class="picker10102-list"></div></div>`;
 document.body.appendChild(ov);const list=ov.querySelector('.picker10102-list'),filter=ov.querySelector('[data-filter10102]');
 function render(q=''){const m=opts.filter(o=>(o.textContent||'').toLowerCase().includes(q.toLowerCase()));list.innerHTML=m.map((o,i)=>`<button type="button" data-opt10102="${opts.indexOf(o)}" class="${o.value===src.value?'active':''}">${esc(o.textContent||'')}</button>`).join('')||'<span class="muted">Nenhum resultado.</span>'}
 render();filter.focus();filter.addEventListener('input',()=>render(filter.value));ov.addEventListener('click',e=>{if(e.target===ov||e.target.closest('[data-close10102]')){ov.remove();return}const b=e.target.closest('[data-opt10102]');if(!b)return;const o=opts[Number(b.dataset.opt10102)];if(!o)return;src.value=o.value;src.dispatchEvent(new Event('change',{bubbles:true}));ov.remove()})
}
// Captura primeiro para impedir os atalhos antigos F2/F4 da 10.9.0/10.10.0.
document.addEventListener('keydown',e=>{
 if(e.repeat)return;const caixa=document.querySelector('#caixa');if(!caixa||!caixa.classList.contains('active'))return;
 if(e.key==='F1'){e.preventDefault();e.stopImmediatePropagation();picker10102('seller');return}
 if(e.key==='F2'){e.preventDefault();e.stopImmediatePropagation();picker10102('client');return}
 if(e.key==='F10'){e.preventDefault();e.stopImmediatePropagation();const vend=document.querySelector('#vendedorVenda');if(!vend?.value)return toast('Selecione o vendedor com F1 antes de cobrar.');const btn=document.querySelector('#openCheckout1096')||document.querySelector('.pdv1094-charge')||document.querySelector('#finish');if(btn)btn.click();return}
},true);
// Se clicar nos selos F1/F2, abre o mesmo seletor confiavel.
document.addEventListener('click',e=>{if(e.target.closest?.('.shortcut10100-f1')){e.preventDefault();picker10102('seller')}if(e.target.closest?.('.shortcut10100-f2')){e.preventDefault();picker10102('client')}});
const obs10102=new MutationObserver(limparVendaRapidaResidual10102);obs10102.observe(document.documentElement,{childList:true,subtree:true});
document.addEventListener('DOMContentLoaded',()=>setTimeout(limparVendaRapidaResidual10102,50));setTimeout(limparVendaRapidaResidual10102,600);
'''
write('public/app.js',js)

css=read('public/style.css')+r'''
/* 10.10.2 - seletor F1/F2 independente do select nativo */
.quick1096-sellerbox,.quick1096-seller,.smart-pdv-commandbar,.vr1097-root,.vr1097-shell{display:none!important}.picker10102-overlay{position:fixed;inset:0;z-index:20000;background:rgba(0,0,0,.68);display:grid;place-items:center;padding:14px}.picker10102-card{width:min(430px,94vw);max-height:min(560px,90vh);display:flex;flex-direction:column;gap:7px;padding:12px;background:var(--card-bg);border:1px solid var(--border);border-radius:12px;box-shadow:0 25px 80px rgba(0,0,0,.45)}.picker10102-head{height:32px;display:flex;align-items:center;justify-content:space-between}.picker10102-head button{border:0;background:transparent;color:var(--text);font-size:22px}.picker10102-card input{height:38px!important;min-height:38px!important;margin:0!important}.picker10102-list{min-height:80px;overflow-y:auto;display:grid;gap:4px}.picker10102-list button{min-height:38px;padding:7px 10px;text-align:left;border:1px solid var(--border);border-radius:7px;background:var(--input-bg);color:var(--text);font-weight:700}.picker10102-list button.active{border-color:var(--accent);box-shadow:inset 3px 0 0 var(--accent)}
'''
write('public/style.css',css)
print('10.10.2: remove bloqueio residual da Venda Rapida; F1 vendedor, F2 cliente e F10 cobrar corrigidos.')