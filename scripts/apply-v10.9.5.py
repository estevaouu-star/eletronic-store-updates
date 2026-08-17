from pathlib import Path
import json
root=Path('app')
def read(p): return (root/p).read_text(encoding='utf-8')
def write(p,s): (root/p).write_text(s,encoding='utf-8')

pkg=json.loads(read('package.json'));pkg['version']='10.9.5';write('package.json',json.dumps(pkg,indent=2,ensure_ascii=False))
html=read('public/index.html').replace('id="versionInfo" class="version-info">v10.9.4','id="versionInfo" class="version-info">v10.9.5',1)
write('public/index.html',html)

js=read('public/app.js').replace('const atual="10.9.4"','const atual="10.9.5"',1)

# Filtro Faltando informação sem tocar na estrutura HTML da toolbar.
if 'let produtosSomenteIncompletos=false;' not in js:
    marker='let produtosPagina=1;'
    if marker not in js: raise RuntimeError('Paginacao de Produtos nao encontrada')
    insert='''let produtosSomenteIncompletos=false;\nfunction produtoTemInformacaoFaltando(p){return !String(p.codigo||'').trim()||!String(p.nome||'').trim()||!String(p.categoria||'').trim()||!String(p.marca||'').trim()||!String(p.codigoBarras||'').trim()||!(Number(p.precoVenda)>0)}\nfunction toggleFiltroInfoProdutos(){produtosSomenteIncompletos=!produtosSomenteIncompletos;produtosPagina=1;const b=document.querySelector('#filtroInfoProdutoBtn');if(b)b.classList.toggle('active',produtosSomenteIncompletos);renderProdutos()}\n'''
    js=js.replace(marker,insert+marker,1)

old='const a=produtos.filter(p=>(p.nome.toLowerCase().includes(q)||p.codigo.toLowerCase().includes(q)||p.marca.toLowerCase().includes(q))&&(!st||(st==="ativo"?p.ativo:!p.ativo)));'
new='const a=produtos.filter(p=>(p.nome.toLowerCase().includes(q)||p.codigo.toLowerCase().includes(q)||p.marca.toLowerCase().includes(q))&&(!st||(st==="ativo"?p.ativo:!p.ativo))&&(!produtosSomenteIncompletos||produtoTemInformacaoFaltando(p)));'
if old not in js and 'produtosSomenteIncompletos||produtoTemInformacaoFaltando' not in js: raise RuntimeError('renderProdutos nao encontrado')
js=js.replace(old,new,1)

# Vendedor obrigatório antes de iniciar a venda.
if 'Selecione o vendedor antes de iniciar a venda.' not in js:
    js=js.replace('function add(id){\n  const p=produtos.find(x=>x.id===id);','function add(id){\n  if(!$("#vendedorVenda")?.value)return toast("Selecione o vendedor antes de iniciar a venda.");\n  const p=produtos.find(x=>x.id===id);',1)
    js=js.replace('function addServico(id){\n  const s=servicos.find(x=>x.id===id);','function addServico(id){\n  if(!$("#vendedorVenda")?.value)return toast("Selecione o vendedor antes de iniciar a venda.");\n  const s=servicos.find(x=>x.id===id);',1)
    js=js.replace('function adicionarProdutoPorCodigo(){','function adicionarProdutoPorCodigo(){\n  if(!$("#vendedorVenda")?.value)return toast("Selecione o vendedor antes de iniciar a venda.");',1)
if 'Selecione o vendedor antes de finalizar a venda.' not in js:
    js=js.replace('async function finish(){if(!cart.length&&!cartServicos.length)','async function finish(){if(!$("#vendedorVenda")?.value)return toast("Selecione o vendedor antes de finalizar a venda.");if(!cart.length&&!cartServicos.length)',1)

# Monta COBRAR abaixo do total e pagamento flutuante em runtime, usando os elementos reais da 10.9.4.
if '// 10.9.5 runtime checkout' not in js:
    js += r'''
// 10.9.5 runtime checkout
function montarCheckout1095(){
  const caixa=document.querySelector('#caixa');if(!caixa||document.querySelector('#openCheckout'))return;
  const totalRow=document.querySelector('.pdv1094-total');
  const payment=document.querySelector('.pdv1094-payment');
  const finish=document.querySelector('#finish');
  if(!totalRow||!payment||!finish)return;
  const cobrar=document.createElement('button');cobrar.id='openCheckout';cobrar.type='button';cobrar.className='primary pdv1095-charge';cobrar.textContent='COBRAR';totalRow.parentElement.appendChild(cobrar);
  const overlay=document.createElement('div');overlay.id='checkoutFloat';overlay.className='pdv1095-overlay hidden';overlay.setAttribute('aria-hidden','true');
  overlay.innerHTML='<div class="pdv1095-float-card" role="dialog" aria-modal="true"><div class="pdv1095-float-head"><div><small>Finalizar venda</small><h3>Pagamento</h3></div><button id="closeCheckout" type="button">×</button></div><div class="pdv1095-float-total"><span>Total a receber</span><b id="checkoutFloatTotal">R$ 0,00</b></div><div id="checkoutPaymentHost"></div><div class="pdv1095-float-actions"><button id="cancelCheckout" type="button" class="secondary">Voltar</button></div></div>';
  document.body.appendChild(overlay);
  document.querySelector('#checkoutPaymentHost').appendChild(payment);
  payment.classList.add('pdv1095-payment-box');finish.textContent='Finalizar venda';finish.classList.add('pdv1095-finish');
  const toolbar=document.querySelector('#produtos .toolbar');if(toolbar&&!document.querySelector('#filtroInfoProdutoBtn')){const b=document.createElement('button');b.id='filtroInfoProdutoBtn';b.type='button';b.className='secondary small';b.textContent='Faltando informação';toolbar.appendChild(b);toolbar.classList.add('produtos-toolbar')}
  atualizarBloqueioPdv();
}
function atualizarBloqueioPdv(){const ok=!!document.querySelector('#vendedorVenda')?.value;const s=document.querySelector('#caixa');if(!s)return;s.classList.toggle('pdv1095-seller-missing',!ok);['#buscaCodigo','#buscaTexto'].forEach(sel=>{const e=document.querySelector(sel);if(e)e.disabled=!ok})}
function abrirCheckoutFlutuante(){if(!document.querySelector('#vendedorVenda')?.value)return toast('Selecione o vendedor antes de cobrar.');if(!cart.length&&!cartServicos.length)return toast('Adicione pelo menos um item antes de cobrar.');const o=document.querySelector('#checkoutFloat');if(!o)return;const t=document.querySelector('#checkoutFloatTotal'),total=document.querySelector('#total');if(t&&total)t.textContent=total.textContent;o.classList.remove('hidden');o.setAttribute('aria-hidden','false');document.body.classList.add('pdv1095-modal-open');setTimeout(()=>document.querySelector('#pay')?.focus(),20)}
function fecharCheckoutFlutuante(){const o=document.querySelector('#checkoutFloat');if(!o)return;o.classList.add('hidden');o.setAttribute('aria-hidden','true');document.body.classList.remove('pdv1095-modal-open')}
document.addEventListener('click',e=>{if(e.target.closest?.('#openCheckout')){e.preventDefault();abrirCheckoutFlutuante();return}if(e.target.closest?.('#closeCheckout,#cancelCheckout')){e.preventDefault();fecharCheckoutFlutuante();return}if(e.target.id==='checkoutFloat'){fecharCheckoutFlutuante();return}if(e.target.closest?.('#filtroInfoProdutoBtn')){e.preventDefault();toggleFiltroInfoProdutos();return}});
document.addEventListener('change',e=>{if(e.target?.id==='vendedorVenda')atualizarBloqueioPdv()});
document.addEventListener('keydown',e=>{if(e.key==='Escape')fecharCheckoutFlutuante()});
document.addEventListener('DOMContentLoaded',()=>setTimeout(montarCheckout1095,500));setTimeout(montarCheckout1095,900);
'''
write('public/app.js',js)

css=read('public/style.css')
if '/* 10.9.5 runtime */' not in css:
    css += r'''
/* 10.9.5 runtime */
.pdv1095-charge{width:100%;min-height:54px;margin-top:12px;font-size:17px;font-weight:900}.pdv1095-overlay{position:fixed;inset:0;z-index:9999;background:rgba(0,0,0,.62);backdrop-filter:blur(4px);display:grid;place-items:center;padding:20px}.pdv1095-float-card{width:min(520px,94vw);max-height:90vh;overflow:auto;background:var(--card-bg);color:var(--text-main);border:1px solid var(--border);border-radius:18px;padding:18px;box-shadow:0 30px 90px rgba(0,0,0,.38)}.pdv1095-float-head{display:flex;align-items:center;justify-content:space-between}.pdv1095-float-head h3{margin:3px 0 0;font-size:25px}.pdv1095-float-head>button{border:0;background:transparent;color:var(--text-main);font-size:30px;cursor:pointer}.pdv1095-float-total{margin:16px 0;padding:16px;border-radius:12px;background:color-mix(in srgb,var(--accent) 10%,var(--card-bg));display:flex;align-items:center;justify-content:space-between}.pdv1095-float-total b{font-size:27px;color:var(--accent)}.pdv1095-payment-box{border:0!important;padding:0!important}.pdv1095-payment-box .pdv1094-charge{width:100%;min-height:48px;margin-top:12px}.pdv1095-float-actions{margin-top:8px}.pdv1095-modal-open{overflow:hidden}.pdv1095-seller-missing .pdv1094-catalog{position:relative}.pdv1095-seller-missing .pdv1094-catalog:after{content:'Selecione um vendedor para começar a venda';position:absolute;inset:0;z-index:5;display:grid;place-items:center;text-align:center;padding:30px;background:color-mix(in srgb,var(--card-bg) 88%,transparent);backdrop-filter:blur(2px);font-weight:900;font-size:16px;border-radius:12px}.pdv1095-seller-missing #openCheckout{opacity:.5;pointer-events:none}.produtos-toolbar{align-items:center}.produtos-toolbar #filtroInfoProdutoBtn{white-space:nowrap;margin-bottom:12px}.produtos-toolbar #filtroInfoProdutoBtn.active{background:var(--accent)!important;color:#fff!important}.hidden.pdv1095-overlay{display:none!important}
'''
write('public/style.css',css)
print('10.9.5 aplicada sem dependencia da toolbar HTML.')