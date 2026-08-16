from pathlib import Path
import json,re
root=Path('app')
def read(p): return (root/p).read_text(encoding='utf-8')
def write(p,s): (root/p).write_text(s,encoding='utf-8')
def must(s,a,b,label):
    if a not in s: raise RuntimeError(f'Trecho nao encontrado: {label}')
    return s.replace(a,b,1)

pkg=json.loads(read('package.json'));pkg['version']='10.7.3';write('package.json',json.dumps(pkg,indent=2,ensure_ascii=False))

html=read('public/index.html')
html=html.replace('id="versionInfo" class="version-info">v10.7.2','id="versionInfo" class="version-info">v10.7.3')
old='''      <h3 class="pdv-products-title">Produtos</h3><div id="listaProdutos" class="product-list"></div>
      <h3 style="margin-top:18px">Serviços</h3><div id="listaServicos" class="product-list"></div>'''
new='''      <div class="pdv-catalog-columns">
        <div class="pdv-catalog-pane"><div class="pdv-catalog-head"><h3 class="pdv-products-title">Produtos</h3></div><div id="listaProdutos" class="product-list"></div></div>
        <div class="pdv-catalog-pane"><div class="pdv-catalog-head"><h3>Serviços</h3></div><div id="listaServicos" class="product-list"></div></div>
      </div>'''
html=must(html,old,new,'listas Produtos/Servicos do Caixa')
write('public/index.html',html)

js=read('public/app.js')
js=js.replace('const atual="10.7.2"','const atual="10.7.3"')
# Corrige clique real: a lista usa add(id), nao addCart(id).
js=js.replace("const b=e.target?.closest?.('[onclick*=\"addCart(\"]'); if(!b)return;\n  const m=String(b.getAttribute('onclick')||'').match(/addCart\\((\\d+)\\)/); if(!m)return;",
"const b=e.target?.closest?.('[onclick*=\"add(\"]'); if(!b)return;\n  const m=String(b.getAttribute('onclick')||'').match(/add\\((\\d+)\\)/); if(!m)return;")
# O Enter do codigo tambem deve abrir o ajuste, em vez de apenas avisar.
js=js.replace('''    toast(`${produto.nome}: produto sem estoque.`);
    input.select();
    return;''','''    abrirAjusteEstoquePdv(produto.id);
    input.select();
    return;''')
# A funcao add tambem abre o ajuste como garantia.
js=js.replace('''function add(id){
  const p=produtos.find(x=>x.id===id);if(!p||!p.ativo||p.estoque<=0)return toast("Produto sem estoque.");''','''function add(id){
  const p=produtos.find(x=>x.id===id);if(!p||!p.ativo)return;if(p.estoque<=0){abrirAjusteEstoquePdv(id);return;}''')
write('public/app.js',js)

server=read('src/server.ts')
server=must(server,'app.post("/api/produtos/:id/estoque",auth,admin,(req,res)=>{','app.post("/api/produtos/:id/estoque",auth,(req,res)=>{','liberar ajuste estoque para qualquer usuario')
write('src/server.ts',server)

css=read('public/style.css')
css += r'''
/* 10.7.3 - layout definitivo do catalogo do Caixa */
.caixa-compact-section .pdv-catalog-columns{display:grid!important;grid-template-columns:minmax(0,1fr) minmax(0,1fr)!important;gap:12px!important;margin-top:12px!important}.pdv-catalog-pane{min-width:0;border:1px solid var(--border);border-radius:13px;background:color-mix(in srgb,var(--card-bg) 98%,var(--page-bg) 2%);padding:10px}.pdv-catalog-head{display:flex;align-items:center;justify-content:space-between;margin-bottom:6px}.pdv-catalog-head h3{margin:0!important}.pdv-catalog-pane .product-list{max-height:420px!important;overflow:auto!important}.pdv-catalog-pane .product{padding:8px!important}.zero-stock-modal{display:grid;gap:4px}.zero-stock-modal .muted{margin-top:-3px}@media(max-width:900px){.caixa-compact-section .pdv-catalog-columns{grid-template-columns:1fr!important}}
'''
write('public/style.css',css)
print('Patch 10.7.3 aplicado: Produtos e Servicos lado a lado e ajuste de estoque funcionando no clique e no codigo.')
