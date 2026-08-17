from pathlib import Path
import json,re
root=Path('app')
def read(p): return (root/p).read_text(encoding='utf-8')
def write(p,s): (root/p).write_text(s,encoding='utf-8')

pkg=json.loads(read('package.json'));pkg['version']='10.10.0';write('package.json',json.dumps(pkg,indent=2,ensure_ascii=False))
html=read('public/index.html').replace('id="versionInfo" class="version-info">v10.9.9','id="versionInfo" class="version-info">v10.10.0',1)
write('public/index.html',html)

js=read('public/app.js').replace('const atual="10.9.9"','const atual="10.10.0"',1)
# Neutraliza completamente a Venda Rapida das versões anteriores.
js += r'''
// 10.10.0 - Venda Rápida removida; atalhos passam a agir no Caixa normal.
function removerVendaRapida10100(){
 document.querySelectorAll('.vr1097-root,.vr1097-shell,#vr1097Picker').forEach(n=>n.remove());
 // Remove botões/cards dedicados à Venda Rápida sem tocar no Caixa principal.
 [...document.querySelectorAll('button,a,.card,.panel,dialog,[role="dialog"]')].forEach(n=>{
   const t=(n.textContent||'').trim();
   if(/^venda r[aá]pida$/i.test(t)||(/venda r[aá]pida/i.test(t)&&!n.closest('#caixa')&&!n.querySelector('#loginForm'))) {
     if(!n.closest('#caixa')&&!n.closest('#loginScreen')) n.remove();
   }
 });
}
function marcarAtalhosCaixa10100(){
 const vend=document.querySelector('#vendedorVenda'),cli=document.querySelector('#clienteVenda'),btn=document.querySelector('#openCheckout1096')||document.querySelector('#finish');
 if(vend){const box=vend.closest('.pdv1094-field')||vend.parentElement;if(box&&!box.querySelector('.shortcut10100-f1')){const k=document.createElement('span');k.className='shortcut10100 shortcut10100-f1';k.textContent='F1';box.appendChild(k)}}
 if(cli){const box=cli.closest('.pdv1094-field')||cli.parentElement;if(box&&!box.querySelector('.shortcut10100-f2')){const k=document.createElement('span');k.className='shortcut10100 shortcut10100-f2';k.textContent='F2';box.appendChild(k)}}
 if(btn&&!btn.querySelector('.shortcut10100-f10')){const k=document.createElement('span');k.className='shortcut10100 shortcut10100-f10';k.textContent='F10';btn.appendChild(k)}
}
function abrirSelect10100(sel){
 if(!sel)return;
 sel.focus();
 try{sel.showPicker?.()}catch{}
 sel.dispatchEvent(new MouseEvent('mousedown',{bubbles:true}));
}
document.addEventListener('keydown',e=>{
 if(e.repeat)return;
 const caixa=document.querySelector('#caixa');if(!caixa||!caixa.classList.contains('active'))return;
 if(e.key==='F1'){e.preventDefault();abrirSelect10100(document.querySelector('#vendedorVenda'));return}
 if(e.key==='F2'){e.preventDefault();abrirSelect10100(document.querySelector('#clienteVenda'));return}
 if(e.key==='F10'){e.preventDefault();const btn=document.querySelector('#openCheckout1096')||document.querySelector('#finish');btn?.click();return}
},true);
const obs10100=new MutationObserver(()=>{removerVendaRapida10100();marcarAtalhosCaixa10100()});
document.addEventListener('DOMContentLoaded',()=>setTimeout(()=>{removerVendaRapida10100();marcarAtalhosCaixa10100()},300));
setTimeout(()=>{removerVendaRapida10100();marcarAtalhosCaixa10100()},900);
obs10100.observe(document.documentElement,{childList:true,subtree:true});
'''
write('public/app.js',js)

css=read('public/style.css')+r'''
/* 10.10.0 - Caixa fixo em uma tela; scroll só no catálogo de produtos */
html,body{overflow:hidden!important}#app{height:100vh;overflow:hidden!important}.layout{height:calc(100vh - 68px)!important;min-height:0!important;overflow:hidden!important}main{height:100%;min-height:0!important;overflow:hidden!important;margin:0 auto!important;padding-top:12px!important;padding-bottom:12px!important}.section{height:100%;min-height:0!important;overflow:hidden!important}#caixa.caixa-1094{height:100%!important;min-height:0!important;display:flex!important;flex-direction:column!important;overflow:hidden!important}.pdv1094-topline{flex:0 0 auto!important;margin-bottom:8px!important}.pdv1094-shell{flex:1 1 auto!important;min-height:0!important;height:auto!important;overflow:hidden!important}.pdv1094-sale,.pdv1094-catalog{min-height:0!important;height:100%!important;overflow:hidden!important}.pdv1094-sale{display:flex!important;flex-direction:column!important}.pdv1094-cart-card{flex:1 1 auto!important;min-height:0!important;overflow:hidden!important}.pdv1094-cart{height:100%!important;max-height:none!important;overflow-y:auto!important}.pdv1094-catalog{display:flex!important;flex-direction:column!important}.pdv1094-categories{flex:0 0 auto!important;max-height:82px!important;overflow-x:auto!important;overflow-y:hidden!important}.pdv1094-catalog-tabs{flex:0 0 auto!important}.pdv1094-panel{flex:1 1 auto!important;min-height:0!important;overflow:hidden!important}.pdv1094-product-grid,.pdv1094-service-grid{height:100%!important;min-height:0!important;overflow-y:auto!important;overflow-x:hidden!important}.pdv1094-buyer{flex:0 0 auto!important}.pdv1094-bottom{flex:0 0 auto!important;margin-top:6px!important}.shortcut10100{display:inline-flex;align-items:center;justify-content:center;min-width:26px;height:20px;padding:0 6px;border-radius:6px;background:color-mix(in srgb,var(--accent) 18%,var(--card-bg));border:1px solid color-mix(in srgb,var(--accent) 38%,var(--border));font-size:10px;font-weight:900;line-height:1}.pdv1094-field{position:relative}.pdv1094-field>.shortcut10100{position:absolute;top:0;right:4px}.pdv1094-charge,.pay1096-open{display:flex!important;align-items:center!important;justify-content:center!important;gap:8px!important}.pdv1094-charge .shortcut10100,.pay1096-open .shortcut10100{background:#ffffff20;border-color:#ffffff35;color:#fff}@media(max-height:720px){main{padding-top:7px!important;padding-bottom:7px!important}.pdv1094-topline h2{font-size:22px!important}.pdv1094-topline p{display:none}.pdv1094-assignment{gap:6px!important}.pdv1094-codebar input{min-height:34px!important}.pdv1094-bottom{gap:6px!important}.pdv1094-categories{max-height:64px!important}}
'''
write('public/style.css',css)
print('10.10.0: Venda Rápida removida, F1 vendedor, F2 cliente, F10 cobrar e Caixa sem scroll da página.')