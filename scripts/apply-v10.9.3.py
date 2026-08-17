from pathlib import Path
import json,re
root=Path('app')
def read(p): return (root/p).read_text(encoding='utf-8')
def write(p,s): (root/p).write_text(s,encoding='utf-8')

def sub_once(pattern,repl,text,label,flags=0):
    out,n=re.subn(pattern,repl,text,count=1,flags=flags)
    if n!=1: raise RuntimeError('Nao foi possivel aplicar: '+label)
    return out

pkg=json.loads(read('package.json'));pkg['version']='10.9.3';write('package.json',json.dumps(pkg,indent=2,ensure_ascii=False))
html=read('public/index.html')
html=html.replace('id="versionInfo" class="version-info">v10.9.2','id="versionInfo" class="version-info">v10.9.3',1)
html=html.replace('<table><thead><tr><th>Código</th><th>Cód. barras</th><th>Produto</th><th>Marca</th><th>Venda</th><th>Estoque</th><th>Status</th><th></th></tr></thead><tbody id="tableProdutos"></tbody></table></div>', '<div class="products-table-scroll"><table><thead><tr><th>Código</th><th>Cód. barras</th><th>Produto</th><th>Marca</th><th>Venda</th><th>Estoque</th><th>Status</th><th></th></tr></thead><tbody id="tableProdutos"></tbody></table></div><div id="produtosPager" class="products-real-pager"></div></div>',1)
write('public/index.html',html)

js=read('public/app.js')
js=js.replace('const atual="10.9.2"','const atual="10.9.3"',1)
# Desliga as tentativas anteriores de reconstruir o Caixa por cima do DOM.
js=js.replace('function setupCaixa(){\n   const s=caixa();', 'function setupCaixa(){\n   return;\n   const s=caixa();',1)
js=js.replace('function buildPdvLayout(){\n  const s=document.querySelector', 'function buildPdvLayout(){\n  return;\n  const s=document.querySelector',1)

# Caixa: categorias e favoritos renderizados diretamente a partir do array de produtos.
new_busca=r'''let pdvCategoriaAtiva="Todos";
function pdvFavoritosSet(){try{return new Set(JSON.parse(localStorage.getItem("eletromix_pdv_favoritos")||"[]").map(Number))}catch{return new Set()}}
function setPdvCategoria(nome){pdvCategoriaAtiva=nome;renderBuscaProdutos()}
function togglePdvFavorito(id,event){event?.stopPropagation?.();const f=pdvFavoritosSet();f.has(Number(id))?f.delete(Number(id)):f.add(Number(id));localStorage.setItem("eletromix_pdv_favoritos",JSON.stringify([...f]));renderBuscaProdutos()}
function ensurePdvCatalog(){
  const lista=$("#listaProdutos");if(!lista)return null;
  let box=$("#pdvSmartCatalog");if(box)return box;
  box=document.createElement("div");box.id="pdvSmartCatalog";box.className="pdv-smart-catalog";
  box.innerHTML='<div class="pdv-smart-title">CATEGORIAS</div><div id="pdvCategorias" class="pdv-smart-categories"></div><div class="pdv-smart-title pdv-smart-products-head"><span>PRODUTOS</span><span class="muted">Clique para adicionar</span></div>';
  lista.parentElement.insertBefore(box,lista);box.appendChild(lista);lista.classList.add("pdv-smart-product-grid");
  const servTitle=$("#listaServicos")?.previousElementSibling;if(servTitle)servTitle.classList.add("pdv-service-title");
  return box;
}
function renderBuscaProdutos(){
  const q=normalizarBusca($("#buscaTexto")?.value);ensurePdvCatalog();
  const ativos=produtos.filter(p=>p.ativo);
  const favoritos=pdvFavoritosSet();
  const categorias=["Todos","★ Favoritos",...new Set(ativos.map(p=>(p.categoria||"Geral").trim()||"Geral"))];
  if(!categorias.includes(pdvCategoriaAtiva))pdvCategoriaAtiva="Todos";
  const cats=$("#pdvCategorias");if(cats)cats.innerHTML=categorias.map(c=>`<button type="button" class="pdv-smart-cat ${c===pdvCategoriaAtiva?"active":""}" onclick='setPdvCategoria(${JSON.stringify(c)})'>${esc(c)}</button>`).join("");
  const a=ativos.filter(p=>{
    if(pdvCategoriaAtiva==="★ Favoritos"&&!favoritos.has(Number(p.id)))return false;
    if(pdvCategoriaAtiva!=="Todos"&&pdvCategoriaAtiva!=="★ Favoritos"&&(p.categoria||"Geral")!==pdvCategoriaAtiva)return false;
    if(!q)return true;
    return [p.nome,p.marca,p.categoria,p.codigo,p.codigoBarras].map(normalizarBusca).some(v=>v.includes(q));
  }).slice(0,15);
  $("#listaProdutos").innerHTML=a.map(p=>`<div class="pdv-smart-product" onclick="add(${p.id})"><button type="button" class="pdv-smart-fav" onclick="togglePdvFavorito(${p.id},event)" title="Favoritar">${favoritos.has(Number(p.id))?"★":"☆"}</button><b>${esc(p.nome)}</b><small>${esc(p.categoria||"Geral")} · Estoque ${p.estoque}</small><strong>${money(p.precoVenda)}</strong></div>`).join("")||'<p class="muted">Nenhum produto encontrado.</p>';
  const ss=servicos.filter(s=>s.ativo&&(!q||[s.nome,s.categoria,s.descricao].map(normalizarBusca).some(v=>v.includes(q)))).slice(0,8);
  $("#listaServicos").innerHTML=ss.map(s=>`<div class="product"><div><b>${esc(s.nome)}</b><small>${esc(s.categoria)} · ${money(s.preco)}</small></div><button onclick="addServico(${s.id})">Adicionar</button></div>`).join("")||'<p class="muted">Nenhum serviço encontrado.</p>';
}'''
js=sub_once(r'function renderBuscaProdutos\(\)\{.*?\n\}\nfunction add\(id\)\{',new_busca+'\nfunction add(id){',js,'renderBuscaProdutos real',re.S)

# Produtos: paginação de verdade em 3 linhas renderizadas.
new_prod=r'''let produtosPagina=1;
const produtosPorPagina=3;
function mudarPaginaProdutos(p){produtosPagina=Math.max(1,Number(p)||1);renderProdutos();document.querySelector("#produtos")?.scrollIntoView({block:"start"})}
function renderProdutosReset(){produtosPagina=1;renderProdutos()}
function renderProdutos(){
  const q=$("#filtroProdutos").value.toLowerCase(),st=$("#filtroStatusProduto").value;
  const a=produtos.filter(p=>(p.nome.toLowerCase().includes(q)||p.codigo.toLowerCase().includes(q)||p.marca.toLowerCase().includes(q))&&(!st||(st==="ativo"?p.ativo:!p.ativo)));
  const paginas=Math.max(1,Math.ceil(a.length/produtosPorPagina));if(produtosPagina>paginas)produtosPagina=paginas;
  const inicio=(produtosPagina-1)*produtosPorPagina,visiveis=a.slice(inicio,inicio+produtosPorPagina);
  $("#tableProdutos").innerHTML=visiveis.map(p=>`<tr><td>${esc(p.codigo)}</td><td>${esc(p.codigoBarras||"-")}</td><td>${esc(p.nome)}</td><td>${esc(p.marca)}</td><td>${money(p.precoVenda)}</td><td>${p.estoque<=p.estoqueMinimo?"⚠️ ":""}${p.estoque}</td><td class="${p.ativo?"status-ok":"status-off"}">${p.ativo?"Ativo":"Inativo"}</td><td><div class="row-actions"><button class="edit" onclick="editProduto(${p.id})">Editar</button><button class="edit" onclick="stockProduto(${p.id})">Estoque</button></div></td></tr>`).join("")||'<tr><td colspan="8" class="muted">Nenhum produto encontrado.</td></tr>';
  const pager=$("#produtosPager");if(pager){const ini=Math.max(1,produtosPagina-2),fim=Math.min(paginas,ini+4);let b=`<button ${produtosPagina===1?"disabled":""} onclick="mudarPaginaProdutos(${produtosPagina-1})">‹ Anterior</button>`;for(let i=ini;i<=fim;i++)b+=`<button class="${i===produtosPagina?"active":""}" onclick="mudarPaginaProdutos(${i})">${i}</button>`;b+=`<button ${produtosPagina===paginas?"disabled":""} onclick="mudarPaginaProdutos(${produtosPagina+1})">Próxima ›</button><span>${a.length} produtos · 3 por página</span>`;pager.innerHTML=b}
}'''
js=sub_once(r'function renderProdutos\(\)\{.*?\}\nfunction produtoForm',new_prod+'\nfunction produtoForm',js,'renderProdutos paginado',re.S)
js=js.replace('["filtroProdutos","input",debounce(renderProdutos,100)]','["filtroProdutos","input",debounce(renderProdutosReset,100)]',1)
js=js.replace('["filtroStatusProduto","change",renderProdutos]','["filtroStatusProduto","change",renderProdutosReset]',1)
write('public/app.js',js)

css=read('public/style.css')+r'''
/* 10.9.3 - hotfix visual e desempenho */
@media(min-width:761px){.layout{display:flex!important;align-items:stretch}.layout>aside{flex:0 0 170px!important;width:170px!important;min-width:170px!important;max-width:170px!important;display:block!important;overflow-y:auto!important;overflow-x:hidden!important}.layout>main{flex:1 1 auto!important;width:auto!important;min-width:0!important;max-width:none!important;margin:14px auto!important;overflow-x:hidden!important}}
#caixa{max-width:none!important;width:100%!important}#caixa .pdv-grid{display:grid!important;grid-template-columns:minmax(390px,43%) minmax(0,57%)!important;gap:10px!important;align-items:start!important}#caixa .pdv-grid>.card:first-child{grid-column:2;grid-row:1}#caixa .pdv-grid>.card:nth-child(2){grid-column:1;grid-row:1}#caixa .pdv-grid>.card{min-width:0!important;padding:14px!important}#caixa .pdv-search-grid{grid-template-columns:1fr!important;gap:6px!important}.pdv-smart-title{background:color-mix(in srgb,var(--accent) 24%,#101820);color:#fff;border-radius:6px;padding:7px 9px;font-size:11px;font-weight:900;letter-spacing:.06em;margin:5px 0 7px}.pdv-smart-products-head{display:flex;justify-content:space-between;align-items:center}.pdv-smart-categories{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:6px;margin-bottom:8px}.pdv-smart-cat{min-height:54px;border:1px solid var(--border);border-radius:7px;background:var(--card-bg);color:var(--text-main);font-weight:800;cursor:pointer;padding:6px}.pdv-smart-cat.active{background:var(--accent)!important;color:#fff!important;border-color:var(--accent)!important}.pdv-smart-product-grid{display:grid!important;grid-template-columns:repeat(3,minmax(0,1fr))!important;gap:7px!important;max-height:430px!important;overflow:auto!important}.pdv-smart-product{position:relative;min-height:105px;border:1px solid var(--border);border-radius:8px;padding:28px 9px 9px;background:var(--card-bg);cursor:pointer;display:flex;flex-direction:column;justify-content:flex-end;gap:4px}.pdv-smart-product:hover{border-color:var(--accent)}.pdv-smart-product b{font-size:12px}.pdv-smart-product small{font-size:10px;color:var(--text-muted)}.pdv-smart-product strong{font-size:13px;color:var(--accent)}.pdv-smart-fav{position:absolute;top:5px;right:5px;border:0;background:transparent;color:var(--accent);font-size:18px;cursor:pointer}.pdv-service-title{margin-top:10px!important}.products-table-scroll{overflow-x:auto}.products-real-pager{display:flex;align-items:center;justify-content:center;gap:6px;padding:14px 4px 2px;flex-wrap:wrap}.products-real-pager button{height:34px;min-width:36px;border:1px solid var(--border);border-radius:7px;background:var(--card-bg);color:var(--text-main);cursor:pointer}.products-real-pager button.active{background:var(--accent);color:#fff;border-color:var(--accent)}.products-real-pager button:disabled{opacity:.4;cursor:default}.products-real-pager span{font-size:12px;color:var(--text-muted);margin-left:6px}@media(max-width:1100px){#caixa .pdv-grid{grid-template-columns:1fr!important}#caixa .pdv-grid>.card:first-child,#caixa .pdv-grid>.card:nth-child(2){grid-column:1;grid-row:auto}.pdv-smart-product-grid{grid-template-columns:repeat(3,1fr)!important}.pdv-smart-categories{grid-template-columns:repeat(3,1fr)}}
'''
write('public/style.css',css)
print('10.9.3 aplicada: sidebar restaurada, Caixa em layout PDV real e Produtos paginados 3 por pagina.')