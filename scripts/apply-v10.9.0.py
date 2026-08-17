from pathlib import Path
import json

root=Path('app')
def read(p): return (root/p).read_text(encoding='utf-8')
def write(p,s): (root/p).write_text(s,encoding='utf-8')

pkg=json.loads(read('package.json')); pkg['version']='10.9.0'; write('package.json',json.dumps(pkg,indent=2,ensure_ascii=False))

html=read('public/index.html')
html=html.replace('id="versionInfo" class="version-info">v10.8.5','id="versionInfo" class="version-info">v10.9.0',1)
write('public/index.html',html)

js=read('public/app.js')
js=js.replace('const atual="10.8.5"','const atual="10.9.0"',1)
js += r'''
// Eletromix 10.9.0 - Caixa em fluxo de PDV rápido inspirado na referência Smart POS.
function eletromixCaixaSection(){return document.querySelector('#caixa')||document.querySelector('.section.active')}
function eletromixFindButton(section,re){return [...section.querySelectorAll('button')].find(b=>re.test((b.textContent||'').trim()))}
function eletromixBarcodeInput(section){return [...section.querySelectorAll('input')].find(i=>/código|codigo|barras|leia/i.test((i.placeholder||'')+' '+(i.closest('label,div')?.textContent||'')))}
function setupSmartPdv(){
 const s=document.querySelector('#caixa'); if(!s||s.dataset.smartPdv==='1')return; s.dataset.smartPdv='1'; s.classList.add('smart-pdv');
 const title=s.querySelector('.title');
 const bar=document.createElement('div'); bar.className='smart-pdv-commandbar';
 bar.innerHTML='<div class="smart-pdv-brand"><span class="smart-pdv-dot"></span><div><b>Venda rápida</b><small>Leitor pronto para receber produtos</small></div></div><div class="smart-pdv-shortcuts"><button type="button" data-smart="focus"><kbd>F2</kbd> Código</button><button type="button" data-smart="client"><kbd>F4</kbd> Cliente</button><button type="button" class="smart-charge" data-smart="charge"><kbd>F10</kbd> COBRAR</button></div>';
 if(title)title.insertAdjacentElement('afterend',bar); else s.prepend(bar);
 bar.querySelector('[data-smart="focus"]').onclick=()=>{const i=eletromixBarcodeInput(s);if(i){i.focus();i.select()}};
 bar.querySelector('[data-smart="client"]').onclick=()=>{const b=eletromixFindButton(s,/\+\s*cliente|cliente/i);if(b)b.click()};
 bar.querySelector('[data-smart="charge"]').onclick=()=>{const b=eletromixFindButton(s,/ir para pagamento|finalizar venda|cobrar/i);if(b)b.click();else toast('Adicione itens para cobrar.')};
 setTimeout(()=>{const i=eletromixBarcodeInput(s);if(i)i.focus()},120);
}
document.addEventListener('keydown',e=>{
 const s=document.querySelector('#caixa'); if(!s||!s.classList.contains('active'))return;
 if(e.key==='F2'){e.preventDefault();const i=eletromixBarcodeInput(s);if(i){i.focus();i.select()}}
 if(e.key==='F4'){e.preventDefault();const b=eletromixFindButton(s,/\+\s*cliente|cliente/i);if(b)b.click()}
 if(e.key==='F10'){e.preventDefault();const b=eletromixFindButton(s,/ir para pagamento|finalizar venda|cobrar/i);if(b)b.click()}
});
document.addEventListener('click',e=>{if(e.target?.closest?.('.nav[data-s="caixa"]'))setTimeout(setupSmartPdv,40)});
document.addEventListener('DOMContentLoaded',setupSmartPdv);
setTimeout(setupSmartPdv,250);
'''
write('public/app.js',js)

css=read('public/style.css')
css += r'''
/* 10.9.0 - Caixa / PDV rápido */
#caixa.smart-pdv{--pdv-line:color-mix(in srgb,var(--border) 72%,transparent);max-width:1500px;margin:0 auto}
#caixa.smart-pdv>.title{display:flex;align-items:end;justify-content:space-between;margin-bottom:10px}
#caixa.smart-pdv>.title h2{font-size:28px;letter-spacing:-.04em;margin-bottom:1px}
.smart-pdv-commandbar{display:flex;align-items:center;justify-content:space-between;gap:16px;padding:11px 13px;margin:0 0 12px;border:1px solid var(--pdv-line);border-radius:14px;background:var(--card-bg);box-shadow:0 8px 22px rgba(0,0,0,.055)}
.smart-pdv-brand{display:flex;align-items:center;gap:10px}.smart-pdv-brand>div{display:grid}.smart-pdv-brand b{font-size:14px}.smart-pdv-brand small{font-size:11px;color:var(--muted);margin-top:1px}.smart-pdv-dot{width:9px;height:9px;border-radius:50%;background:var(--primary);box-shadow:0 0 0 5px color-mix(in srgb,var(--primary) 12%,transparent)}
.smart-pdv-shortcuts{display:flex;gap:7px;align-items:center}.smart-pdv-shortcuts button{height:38px;padding:0 12px;border:1px solid var(--pdv-line);border-radius:9px;background:color-mix(in srgb,var(--card-bg) 92%,var(--page-bg));color:var(--text);font-weight:750;cursor:pointer}.smart-pdv-shortcuts button:hover{border-color:var(--primary);transform:translateY(-1px)}.smart-pdv-shortcuts kbd{font:800 10px/1 system-ui;padding:4px 5px;border-radius:5px;background:color-mix(in srgb,var(--text) 8%,transparent);margin-right:5px}.smart-pdv-shortcuts .smart-charge{background:var(--primary);border-color:var(--primary);color:#fff;min-width:126px;box-shadow:0 7px 18px color-mix(in srgb,var(--primary) 25%,transparent)}.smart-pdv-shortcuts .smart-charge kbd{background:rgba(255,255,255,.18)}
#caixa.smart-pdv .card{border-radius:13px;box-shadow:none;border:1px solid var(--pdv-line)}
#caixa.smart-pdv input,#caixa.smart-pdv select{min-height:38px}
#caixa.smart-pdv .pdv-catalog-columns{gap:9px!important;margin-top:9px!important}
#caixa.smart-pdv .pdv-catalog-pane{padding:8px!important;border-radius:11px!important}
#caixa.smart-pdv .pdv-catalog-pane .product-list{max-height:500px!important}
#caixa.smart-pdv .product{border-radius:8px!important;margin-bottom:5px!important;transition:border-color .12s ease,background .12s ease}
#caixa.smart-pdv .product:hover{border-color:color-mix(in srgb,var(--primary) 55%,var(--border));background:color-mix(in srgb,var(--primary) 3%,var(--card-bg))}
#caixa.smart-pdv .product button{min-height:32px;border-radius:7px}
#caixa.smart-pdv h3{letter-spacing:-.02em}
#caixa.smart-pdv [id*="cart" i],#caixa.smart-pdv [class*="cart" i]{scrollbar-width:thin}
#caixa.smart-pdv .primary{box-shadow:0 6px 16px color-mix(in srgb,var(--primary) 20%,transparent)}
@media(min-width:1050px){#caixa.smart-pdv{padding-bottom:18px}#caixa.smart-pdv .pdv-catalog-pane .product-list{max-height:54vh!important}}
@media(max-width:760px){.smart-pdv-commandbar{align-items:stretch;flex-direction:column}.smart-pdv-shortcuts{display:grid;grid-template-columns:1fr 1fr 1.3fr}.smart-pdv-shortcuts button{padding:0 7px}.smart-pdv-brand small{display:none}}
'''
write('public/style.css',css)
print('Patch 10.9.0 aplicado: Caixa redesenhado para fluxo rápido de PDV, atalhos F2/F4/F10 e visual inspirado no Smart POS.')