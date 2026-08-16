from pathlib import Path
import json,re
root=Path('app')
def read(p): return (root/p).read_text(encoding='utf-8')
def write(p,s): (root/p).write_text(s,encoding='utf-8')

pkg=json.loads(read('package.json')); pkg['version']='10.7.2'; write('package.json',json.dumps(pkg,indent=2,ensure_ascii=False))

html=read('public/index.html')
# Atualiza versão mostrada no cabeçalho.
html=html.replace('id="versionInfo" class="version-info">v10.7.1','id="versionInfo" class="version-info">v10.7.2')
# Agrupa as listas existentes de produtos e serviços em duas colunas, preservando IDs e lógica atuais.
prod_pat=r'(<div class="card[^>]*>\s*<h3[^>]*>Produtos.*?<div id="listaProdutos".*?</div>\s*</div>)'
serv_pat=r'(<div class="card[^>]*>\s*<h3[^>]*>Serviços.*?<div id="listaServicos".*?</div>\s*</div>)'
pm=re.search(prod_pat,html,re.S|re.I); sm=re.search(serv_pat,html,re.S|re.I)
if pm and sm and pm.start()<sm.start():
    pblock=pm.group(1); sblock=sm.group(1)
    between=html[pm.end():sm.start()]
    if not between.strip(): html=html[:pm.start()]+'<div class="pdv-catalog-columns">'+pblock+sblock+'</div>'+html[sm.end():]
# Se a estrutura tiver ambos dentro do mesmo card, CSS abaixo organiza pelos containers/IDs sem mover a lógica.
write('public/index.html',html)

js=read('public/app.js')
js=js.replace('const atual="10.7.1"','const atual="10.7.2"')
# Intercepta tentativa de adicionar produto zerado. Qualquer usuário logado pode ajustar, conforme solicitado.
js += r'''
// Eletromix 10.7.2 - estoque zerado no PDV: qualquer usuário pode ajustar.
function abrirAjusteEstoquePdv(produtoId){
  const p=produtos.find(x=>Number(x.id)===Number(produtoId)); if(!p)return toast("Produto não encontrado.");
  openModal("Produto sem estoque",`<div class="zero-stock-modal"><p><b>${esc(p.nome)}</b> está com estoque zerado.</p><p class="muted">Informe a quantidade que deve ficar disponível para continuar a venda.</p><form id="zeroStockForm"><label>Quantidade para adicionar</label><input name="quantidade" type="number" min="1" step="1" value="1" required autofocus><label>Motivo</label><input name="motivo" value="Ajuste rápido pelo Caixa" required><button class="primary full" type="submit">Atualizar estoque</button></form></div>`);
  const f=document.querySelector('#zeroStockForm'); if(f)f.onsubmit=async e=>{e.preventDefault();const q=Math.max(1,Math.trunc(Number(e.target.quantidade.value)||0));const motivo=String(e.target.motivo.value||'Ajuste rápido pelo Caixa');const r=await api(`/api/produtos/${p.id}/estoque`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({tipo:'entrada',quantidade:q,motivo})});const d=await r.json();if(!r.ok)return toast(d.erro||'Não foi possível atualizar o estoque.');closeModal();await loadProdutos();toast(`Estoque de ${p.nome} atualizado.`);};
}
document.addEventListener('click',e=>{
  const b=e.target?.closest?.('[onclick*="addCart("]'); if(!b)return;
  const m=String(b.getAttribute('onclick')||'').match(/addCart\((\d+)\)/); if(!m)return;
  const p=produtos.find(x=>Number(x.id)===Number(m[1])); if(!p||Number(p.estoque)>0)return;
  e.preventDefault();e.stopImmediatePropagation();abrirAjusteEstoquePdv(p.id);
},true);
'''
write('public/app.js',js)

css=read('public/style.css')
css += r'''
/* 10.7.2 - Produtos e Serviços lado a lado no Caixa */
.pdv-catalog-columns{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:14px;align-items:start}.pdv-catalog-columns>.card{min-width:0;margin-bottom:0!important}.pdv-catalog-columns #listaProdutos,.pdv-catalog-columns #listaServicos{max-height:430px;overflow:auto}.zero-stock-modal p:first-child{font-size:16px;margin-top:0}.zero-stock-modal .full{width:100%}
/* Compatibilidade com a estrutura atual do PDV quando as duas listas estiverem no mesmo bloco */
.caixa-compact-section .pdv-products-services,.caixa-compact-section .catalogs-row{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:14px}
@media(max-width:900px){.pdv-catalog-columns,.caixa-compact-section .pdv-products-services,.caixa-compact-section .catalogs-row{grid-template-columns:1fr}}
'''
write('public/style.css',css)
print('Patch 10.7.2 aplicado: Produtos e Serviços lado a lado; ajuste rápido de estoque liberado para qualquer usuário.')
