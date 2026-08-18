from pathlib import Path
import json
root=Path('app')
def read(p): return (root/p).read_text(encoding='utf-8')
def write(p,s): (root/p).write_text(s,encoding='utf-8')

pkg=json.loads(read('package.json'));pkg['version']='10.10.13';write('package.json',json.dumps(pkg,indent=2,ensure_ascii=False))
html=read('public/index.html').replace('id="versionInfo" class="version-info">v10.10.12','id="versionInfo" class="version-info">v10.10.13',1);write('public/index.html',html)
js=read('public/app.js').replace('const atual="10.10.12"','const atual="10.10.13"',1)
js += r'''
// 10.10.13 - garante que o perfil 1024x768 use a mesma estrutura do Caixa normal em duas colunas.
function corrigirCaixa1024_101013(){
 if(document.body.dataset.monitorProfile!=='1024x768')return;
 const shell=document.querySelector('#caixa .pdv1094-shell');
 const sale=document.querySelector('#caixa .pdv1094-sale');
 const catalog=document.querySelector('#caixa .pdv1094-catalog');
 if(shell){shell.style.removeProperty('display');shell.classList.add('pdv1024-shell-101013')}
 if(sale)sale.classList.add('pdv1024-sale-101013');
 if(catalog)catalog.classList.add('pdv1024-catalog-101013');
 const cats=document.querySelector('#pdvCategorias');if(cats)cats.classList.add('pdv1024-cats-101013');
 const products=document.querySelector('#pdvProdutosPanel');if(products)products.classList.add('pdv1024-products-101013');
 const services=document.querySelector('#pdvServicosPanel');if(services)services.classList.add('pdv1024-products-101013');
}
document.addEventListener('DOMContentLoaded',()=>setTimeout(corrigirCaixa1024_101013,80));
document.addEventListener('click',e=>{if(e.target.closest?.('.nav[data-s="caixa"]'))setTimeout(corrigirCaixa1024_101013,50)},true);
window.addEventListener('resize',()=>setTimeout(corrigirCaixa1024_101013,50));
setTimeout(corrigirCaixa1024_101013,300);setTimeout(corrigirCaixa1024_101013,1000);
'''
write('public/app.js',js)

css=read('public/style.css')+r'''
/* 10.10.13 - Caixa 1024x768 realmente utilizável: duas colunas e scroll só nas áreas internas. */
body[data-monitor-profile="1024x768"]{overflow:hidden!important}
body[data-monitor-profile="1024x768"] header{height:50px!important;min-height:50px!important}
body[data-monitor-profile="1024x768"] .layout{height:calc(100vh - 50px)!important;min-height:0!important;overflow:hidden!important}
body[data-monitor-profile="1024x768"] main{height:100%!important;min-height:0!important;overflow:hidden!important;padding:8px!important}
body[data-monitor-profile="1024x768"] #caixa{height:100%!important;min-height:0!important;overflow:hidden!important;display:flex!important;flex-direction:column!important;gap:6px!important}
body[data-monitor-profile="1024x768"] #caixa .pdv1094-topline{flex:0 0 auto!important;margin-bottom:4px!important;gap:8px!important;align-items:end!important}
body[data-monitor-profile="1024x768"] #caixa .pdv1094-topline h2{font-size:20px!important}
body[data-monitor-profile="1024x768"] #caixa .pdv1094-topline p{font-size:11px!important;margin-top:1px!important}
body[data-monitor-profile="1024x768"] #caixa .pdv1094-assignment{min-width:0!important;width:54%!important;grid-template-columns:1fr 1fr!important;gap:6px!important}
body[data-monitor-profile="1024x768"] #caixa .pdv1094-field select{min-height:32px!important;height:32px!important;padding:4px 7px!important;font-size:11px!important}
body[data-monitor-profile="1024x768"] #caixa .lock-toggle{min-width:32px!important;width:32px!important;height:32px!important;min-height:32px!important;padding:0!important}
body[data-monitor-profile="1024x768"] #caixa .pdv1094-shell.pdv1024-shell-101013{display:grid!important;grid-template-columns:minmax(330px,43%) minmax(0,57%)!important;grid-template-rows:minmax(0,1fr)!important;gap:7px!important;flex:1 1 auto!important;min-height:0!important;height:auto!important;overflow:hidden!important}
body[data-monitor-profile="1024x768"] #caixa .pdv1094-sale.pdv1024-sale-101013,body[data-monitor-profile="1024x768"] #caixa .pdv1094-catalog.pdv1024-catalog-101013{height:100%!important;min-height:0!important;overflow:hidden!important;padding:8px!important;border-radius:10px!important}
body[data-monitor-profile="1024x768"] #caixa .pdv1094-sale.pdv1024-sale-101013{display:flex!important;flex-direction:column!important;gap:6px!important}
body[data-monitor-profile="1024x768"] #caixa .pdv1094-codebar{grid-template-columns:42% 58%!important;gap:5px!important}
body[data-monitor-profile="1024x768"] #caixa .pdv1094-codebar input{min-height:32px!important;height:32px!important;font-size:11px!important;padding:5px 7px!important}
body[data-monitor-profile="1024x768"] #caixa .pdv1094-cart-card{flex:1 1 auto!important;min-height:0!important;padding:7px!important;overflow:hidden!important}
body[data-monitor-profile="1024x768"] #caixa .pdv1094-cart{min-height:0!important;max-height:none!important;height:100%!important;overflow-y:auto!important;overscroll-behavior:contain!important}
body[data-monitor-profile="1024x768"] #caixa .pdv1094-buyer{flex:0 0 auto!important}
body[data-monitor-profile="1024x768"] #caixa .pdv1094-bottom{flex:0 0 auto!important;gap:5px!important;margin-top:0!important}
body[data-monitor-profile="1024x768"] #caixa .pdv1094-totals{padding:6px!important;gap:3px!important;font-size:11px!important}
body[data-monitor-profile="1024x768"] #caixa .pdv1094-totals input,body[data-monitor-profile="1024x768"] #caixa .pdv1094-totals select{min-height:29px!important;height:29px!important;padding:3px 6px!important}
body[data-monitor-profile="1024x768"] #caixa .pdv1094-total{font-size:15px!important}
body[data-monitor-profile="1024x768"] #caixa .pdv1094-charge{min-height:38px!important;height:38px!important;font-size:13px!important}
body[data-monitor-profile="1024x768"] #caixa .pdv1094-catalog.pdv1024-catalog-101013{display:flex!important;flex-direction:column!important;gap:5px!important}
body[data-monitor-profile="1024x768"] #caixa #pdvCategorias.pdv1024-cats-101013{flex:0 0 116px!important;height:116px!important;max-height:116px!important;display:grid!important;grid-template-columns:repeat(5,minmax(0,1fr))!important;grid-auto-rows:34px!important;gap:4px!important;overflow-y:auto!important;overflow-x:hidden!important;padding-right:3px!important;align-content:start!important;overscroll-behavior:contain!important}
body[data-monitor-profile="1024x768"] #caixa #pdvCategorias .pdv1094-cat{min-height:34px!important;height:34px!important;padding:3px 5px!important;font-size:10px!important;line-height:1.05!important}
body[data-monitor-profile="1024x768"] #caixa .pdv1094-catalog-tabs{flex:0 0 34px!important;height:34px!important;margin:0!important}
body[data-monitor-profile="1024x768"] #caixa .pdv1094-catalog-tabs button{min-height:34px!important;height:34px!important;padding:4px!important;font-size:11px!important}
body[data-monitor-profile="1024x768"] #caixa .pdv1094-panel.pdv1024-products-101013{flex:1 1 auto!important;min-height:0!important;height:auto!important;overflow-y:auto!important;overflow-x:hidden!important;overscroll-behavior:contain!important}
body[data-monitor-profile="1024x768"] #caixa .pdv1094-product-grid,body[data-monitor-profile="1024x768"] #caixa .pdv1094-service-grid{display:grid!important;grid-template-columns:repeat(4,minmax(0,1fr))!important;gap:5px!important;align-content:start!important}
body[data-monitor-profile="1024x768"] #caixa .pdv1094-product{min-height:82px!important;padding:6px!important;font-size:10px!important}
body[data-monitor-profile="1024x768"] #caixa .pdv1094-product b{font-size:10px!important;line-height:1.05!important}body[data-monitor-profile="1024x768"] #caixa .pdv1094-product small{font-size:9px!important}body[data-monitor-profile="1024x768"] #caixa .pdv1094-product strong{font-size:11px!important}
'''
write('public/style.css',css)
print('10.10.13: perfil 1024x768 mantém o Caixa em duas colunas e torna carrinho, categorias e produtos roláveis internamente.')