from pathlib import Path
import json,re
root=Path('app')
def read(p): return (root/p).read_text(encoding='utf-8')
def write(p,s): (root/p).write_text(s,encoding='utf-8')
def sub1(pattern,repl,text,label,flags=0):
    out,n=re.subn(pattern,repl,text,count=1,flags=flags)
    if n!=1: raise RuntimeError('Falha ao aplicar '+label)
    return out

pkg=json.loads(read('package.json'));pkg['version']='10.9.5';write('package.json',json.dumps(pkg,indent=2,ensure_ascii=False))

html=read('public/index.html')
html=html.replace('id="versionInfo" class="version-info">v10.9.4','id="versionInfo" class="version-info">v10.9.5',1)

# Botão Faltando informação na aba Produtos. Procura a toolbar dentro da própria seção,
# sem depender da string exata produzida por patches anteriores.
sec=re.search(r'(<section id="produtos" class="section">)(.*?)(</section>)',html,re.S)
if not sec: raise RuntimeError('Seção Produtos não encontrada')
body=sec.group(2)
if 'id="filtroInfoProdutoBtn"' not in body:
    pat=r'(<div class="toolbar(?: produtos-toolbar)?">\s*<input id="filtroProdutos"[^>]*>\s*<select id="filtroStatusProduto"[^>]*>.*?</select>)(\s*</div>)'
    body2,n=re.subn(pat,r'\1<button id="filtroInfoProdutoBtn" type="button" class="secondary small">Faltando informação</button>\2',body,count=1,flags=re.S)
    if n!=1: raise RuntimeError('Toolbar de Produtos não encontrada')
    body=body2.replace('<div class="toolbar">','<div class="toolbar produtos-toolbar">',1)
    html=html[:sec.start(2)]+body+html[sec.end(2):]

# No novo Caixa, pagamento sai da tela principal. COBRAR fica imediatamente abaixo do total.
old_bottom='''      <div class="pdv1094-bottom">
        <div class="pdv1094-totals totals">
          <div><span>Subtotal</span><b id="sub">R$ 0,00</b></div>
          <div class="discount-row"><span>Desconto</span><div class="discount-control"><select id="discountType"><option value="value">R$</option><option value="percent">%</option></select><input id="desc" type="number" min="0" step=".01" value="0"><small id="discountPreview"></small></div></div>
          <div><span>Acréscimo</span><input id="surcharge" type="number" min="0" step=".01" value="0"></div>
          <div class="big pdv1094-total"><span>TOTAL</span><b id="total">R$ 0,00</b></div>
        </div>
        <div class="payment-box pdv1094-payment">
          <div class="payment-head"><label>Pagamento</label><label class="payment-split-toggle"><input id="splitPayment" type="checkbox"> Dividir</label></div>
          <div id="singlePaymentBox"><select id="pay"><option>PIX</option><option>Dinheiro</option><option>Débito</option><option>Crédito</option></select></div>
          <div id="splitPaymentBox" class="split-payment-box" hidden><div id="splitPaymentRows"></div><div class="split-payment-summary"><span>Distribuído</span><b id="splitPaymentDistributed">R$ 0,00</b><span>Restante</span><b id="splitPaymentRemaining">R$ 0,00</b></div><button id="addPaymentMethod" class="secondary small" type="button">+ Outra forma</button></div>
          <button id="finish" class="primary pdv1094-charge">COBRAR</button>
        </div>
      </div>'''
new_bottom='''      <div class="pdv1095-checkout">
        <div class="pdv1094-totals totals">
          <div><span>Subtotal</span><b id="sub">R$ 0,00</b></div>
          <div class="discount-row"><span>Desconto</span><div class="discount-control"><select id="discountType"><option value="value">R$</option><option value="percent">%</option></select><input id="desc" type="number" min="0" step=".01" value="0"><small id="discountPreview"></small></div></div>
          <div><span>Acréscimo</span><input id="surcharge" type="number" min="0" step=".01" value="0"></div>
          <div class="big pdv1094-total"><span>TOTAL</span><b id="total">R$ 0,00</b></div>
          <button id="openCheckout" type="button" class="primary pdv1095-charge">COBRAR</button>
        </div>
      </div>

      <div id="checkoutFloat" class="pdv1095-overlay hidden" aria-hidden="true">
        <div class="pdv1095-float-card" role="dialog" aria-modal="true" aria-labelledby="checkoutFloatTitle">
          <div class="pdv1095-float-head"><div><small>Finalizar venda</small><h3 id="checkoutFloatTitle">Pagamento</h3></div><button id="closeCheckout" type="button" aria-label="Fechar">×</button></div>
          <div class="pdv1095-float-total"><span>Total a receber</span><b id="checkoutFloatTotal">R$ 0,00</b></div>
          <div class="payment-box pdv1095-payment-box">
            <div class="payment-head"><label>Forma de pagamento</label><label class="payment-split-toggle"><input id="splitPayment" type="checkbox"> Dividir pagamento</label></div>
            <div id="singlePaymentBox"><select id="pay"><option>PIX</option><option>Dinheiro</option><option>Débito</option><option>Crédito</option></select></div>
            <div id="splitPaymentBox" class="split-payment-box" hidden><div id="splitPaymentRows"></div><div class="split-payment-summary"><span>Distribuído</span><b id="splitPaymentDistributed">R$ 0,00</b><span>Restante</span><b id="splitPaymentRemaining">R$ 0,00</b></div><button id="addPaymentMethod" class="secondary small" type="button">+ Outra forma</button></div>
          </div>
          <div class="pdv1095-float-actions"><button id="cancelCheckout" type="button" class="secondary">Voltar</button><button id="finish" type="button" class="primary">Finalizar venda</button></div>
        </div>
      </div>'''
if 'id="checkoutFloat"' not in html:
    if old_bottom not in html: raise RuntimeError('Bloco de pagamento 10.9.4 não encontrado')
    html=html.replace(old_bottom,new_bottom,1)
write('public/index.html',html)

js=read('public/app.js')
js=js.replace('const atual="10.9.4"','const atual="10.9.5"',1)

if 'let produtosSomenteIncompletos=false;' not in js:
    insert='''\nlet produtosSomenteIncompletos=false;\nfunction produtoTemInformacaoFaltando(p){return !String(p.codigo||'').trim()||!String(p.nome||'').trim()||!String(p.categoria||'').trim()||!String(p.marca||'').trim()||!String(p.codigoBarras||'').trim()||!(Number(p.precoVenda)>0)}\nfunction toggleFiltroInfoProdutos(){produtosSomenteIncompletos=!produtosSomenteIncompletos;produtosPagina=1;const b=document.querySelector('#filtroInfoProdutoBtn');if(b)b.classList.toggle('active',produtosSomenteIncompletos);renderProdutos()}\n'''
    idx=js.find('let produtosPagina=1;')
    if idx<0: raise RuntimeError('Paginação de Produtos não encontrada')
    js=js[:idx]+insert+js[idx:]

old='const a=produtos.filter(p=>(p.nome.toLowerCase().includes(q)||p.codigo.toLowerCase().includes(q)||p.marca.toLowerCase().includes(q))&&(!st||(st==="ativo"?p.ativo:!p.ativo)));'
new='const a=produtos.filter(p=>(p.nome.toLowerCase().includes(q)||p.codigo.toLowerCase().includes(q)||p.marca.toLowerCase().includes(q))&&(!st||(st==="ativo"?p.ativo:!p.ativo))&&(!produtosSomenteIncompletos||produtoTemInformacaoFaltando(p)));'
if old in js: js=js.replace(old,new,1)

old_add='function add(id){\n  const p=produtos.find(x=>x.id===id);'
new_add='function add(id){\n  if(!$("#vendedorVenda")?.value)return toast("Selecione o vendedor antes de iniciar a venda.");\n  const p=produtos.find(x=>x.id===id);'
if old_add in js: js=js.replace(old_add,new_add,1)
old_serv='function addServico(id){\n  const s=servicos.find(x=>x.id===id);'
new_serv='function addServico(id){\n  if(!$("#vendedorVenda")?.value)return toast("Selecione o vendedor antes de iniciar a venda.");\n  const s=servicos.find(x=>x.id===id);'
if old_serv in js: js=js.replace(old_serv,new_serv,1)
if 'function adicionarProdutoPorCodigo(){\n  if(!$("#vendedorVenda")?.value)' not in js:
    js=js.replace('function adicionarProdutoPorCodigo(){','function adicionarProdutoPorCodigo(){\n  if(!$("#vendedorVenda")?.value)return toast("Selecione o vendedor antes de iniciar a venda.");',1)
js=js.replace('async function finish(){if(!cart.length&&!cartServicos.length)','async function finish(){if(!$("#vendedorVenda")?.value)return toast("Selecione o vendedor antes de finalizar a venda.");if(!cart.length&&!cartServicos.length)',1)

if '// 10.9.5 - cobrança flutuante e vendedor obrigatório' not in js:
    js += r'''
// 10.9.5 - cobrança flutuante e vendedor obrigatório
function atualizarBloqueioPdv(){
  const ok=!!document.querySelector('#vendedorVenda')?.value;
  const s=document.querySelector('#caixa');if(!s)return;s.classList.toggle('pdv1095-seller-missing',!ok);
  ['#buscaCodigo','#buscaTexto'].forEach(sel=>{const e=document.querySelector(sel);if(e)e.disabled=!ok});
  s.querySelectorAll('.pdv1094-product,.pdv1094-cat,.pdv1094-catalog-tabs button').forEach(e=>{e.setAttribute('aria-disabled',String(!ok));});
}
function abrirCheckoutFlutuante(){
  if(!document.querySelector('#vendedorVenda')?.value)return toast('Selecione o vendedor antes de cobrar.');
  if(!cart.length&&!cartServicos.length)return toast('Adicione pelo menos um item antes de cobrar.');
  const o=document.querySelector('#checkoutFloat');if(!o)return;
  const t=document.querySelector('#checkoutFloatTotal'),total=document.querySelector('#total');if(t&&total)t.textContent=total.textContent;
  o.classList.remove('hidden');o.setAttribute('aria-hidden','false');document.body.classList.add('pdv1095-modal-open');
  setTimeout(()=>document.querySelector('#pay')?.focus(),30);
}
function fecharCheckoutFlutuante(){const o=document.querySelector('#checkoutFloat');if(!o)return;o.classList.add('hidden');o.setAttribute('aria-hidden','true');document.body.classList.remove('pdv1095-modal-open')}
document.addEventListener('click',e=>{
  if(e.target.closest?.('#openCheckout')){e.preventDefault();abrirCheckoutFlutuante();return}
  if(e.target.closest?.('#closeCheckout,#cancelCheckout')){e.preventDefault();fecharCheckoutFlutuante();return}
  if(e.target.id==='checkoutFloat'){fecharCheckoutFlutuante();return}
  if(e.target.closest?.('#filtroInfoProdutoBtn')){e.preventDefault();toggleFiltroInfoProdutos();return}
});
document.addEventListener('change',e=>{if(e.target?.id==='vendedorVenda')atualizarBloqueioPdv()});
document.addEventListener('keydown',e=>{if(e.key==='Escape'&&!document.querySelector('#checkoutFloat')?.classList.contains('hidden'))fecharCheckoutFlutuante()});
document.addEventListener('DOMContentLoaded',()=>setTimeout(atualizarBloqueioPdv,500));setTimeout(atualizarBloqueioPdv,900);
'''
write('public/app.js',js)

css=read('public/style.css')
if '/* 10.9.5 - fluxo de venda guiado */' not in css:
    css += r'''
/* 10.9.5 - fluxo de venda guiado */
.pdv1095-checkout{margin-top:auto}.pdv1095-charge{width:100%;min-height:54px;margin-top:12px;font-size:17px;font-weight:950;letter-spacing:.02em}.pdv1095-overlay{position:fixed;inset:0;z-index:9999;background:rgba(0,0,0,.62);backdrop-filter:blur(4px);display:grid;place-items:center;padding:20px}.pdv1095-float-card{width:min(520px,94vw);max-height:90vh;overflow:auto;background:var(--card-bg);color:var(--text-main);border:1px solid var(--border);border-radius:18px;padding:18px;box-shadow:0 30px 90px rgba(0,0,0,.38)}.pdv1095-float-head{display:flex;align-items:center;justify-content:space-between}.pdv1095-float-head small{color:var(--text-muted);font-weight:800;text-transform:uppercase;letter-spacing:.08em}.pdv1095-float-head h3{margin:3px 0 0;font-size:25px}.pdv1095-float-head>button{border:0;background:transparent;color:var(--text-main);font-size:30px;cursor:pointer}.pdv1095-float-total{margin:16px 0;padding:16px;border-radius:12px;background:color-mix(in srgb,var(--accent) 10%,var(--card-bg));display:flex;align-items:center;justify-content:space-between}.pdv1095-float-total b{font-size:27px;color:var(--accent)}.pdv1095-payment-box{border:0!important;padding:0!important}.pdv1095-float-actions{display:grid;grid-template-columns:.7fr 1.3fr;gap:8px;margin-top:16px}.pdv1095-float-actions button{min-height:48px}.pdv1095-modal-open{overflow:hidden}.pdv1095-seller-missing .pdv1094-catalog{position:relative}.pdv1095-seller-missing .pdv1094-catalog:after{content:'Selecione um vendedor para começar a venda';position:absolute;inset:0;z-index:5;display:grid;place-items:center;text-align:center;padding:30px;background:color-mix(in srgb,var(--card-bg) 88%,transparent);backdrop-filter:blur(2px);font-weight:900;font-size:16px;color:var(--text-main);border-radius:12px}.pdv1095-seller-missing #openCheckout{opacity:.5;pointer-events:none}.produtos-toolbar{align-items:center}.produtos-toolbar #filtroInfoProdutoBtn{white-space:nowrap;margin-bottom:12px}.produtos-toolbar #filtroInfoProdutoBtn.active{background:var(--accent)!important;color:#fff!important}.hidden.pdv1095-overlay{display:none!important}
'''
write('public/style.css',css)
print('10.9.5: patch robusto aplicado.')