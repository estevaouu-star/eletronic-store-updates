from pathlib import Path
import json,re
root=Path('app')
def read(p): return (root/p).read_text(encoding='utf-8')
def write(p,s): (root/p).write_text(s,encoding='utf-8')
def sub1(pattern,repl,text,label,flags=0):
    out,n=re.subn(pattern,repl,text,count=1,flags=flags)
    if n!=1: raise RuntimeError('Falha: '+label)
    return out

pkg=json.loads(read('package.json'));pkg['version']='10.9.4';write('package.json',json.dumps(pkg,indent=2,ensure_ascii=False))

html=read('public/index.html')
html=html.replace('id="versionInfo" class="version-info">v10.9.3','id="versionInfo" class="version-info">v10.9.4',1)
# Remove a opção manual Abrir/Fechar Caixa do menu.
html=re.sub(r'\s*<button class="nav" data-s="caixaGestao">.*?</button>','',html,count=1,flags=re.S)

# Caixa reconstruído do zero, preservando IDs usados pelo fluxo existente.
novo_caixa=r'''<section id="caixa" class="section active caixa-1094">
  <div class="pdv1094-topline">
    <div><h2>Caixa / PDV</h2><p>Venda direta, rápida e organizada.</p></div>
    <div class="pdv1094-assignment">
      <div class="pdv1094-field"><label>Vendedor</label><div class="select-lock-row"><select id="vendedorVenda"><option value="">Selecione o vendedor...</option></select><button class="lock-toggle" id="lockVendedorBtn" type="button" title="Travar vendedor"><span data-icon="unlock"></span></button></div><span id="vendedorLockStatus" class="lock-status">Livre</span></div>
      <div class="pdv1094-field"><div class="pdv1094-client-head"><label>Cliente</label><button class="link-button" id="newClientShortcut" type="button">+ Cliente</button></div><div class="select-lock-row"><select id="clienteVenda"><option value="">Consumidor final</option></select><button class="lock-toggle" id="lockClienteBtn" type="button" title="Travar cliente"><span data-icon="unlock"></span></button></div><span id="clienteLockStatus" class="lock-status">Livre</span></div>
    </div>
  </div>

  <div class="pdv1094-shell">
    <section class="pdv1094-sale">
      <div class="pdv1094-codebar">
        <div class="pdv1094-code"><label for="buscaCodigo">Código / código de barras</label><input id="buscaCodigo" autocomplete="off" placeholder="Digite ou leia e pressione Enter"></div>
        <div class="pdv1094-search"><label for="buscaTexto">Pesquisar</label><input id="buscaTexto" autocomplete="off" placeholder="Nome, marca, código, categoria..."></div>
      </div>

      <div class="pdv1094-cart-card">
        <div class="pdv1094-section-head"><h3>Itens da venda</h3><span class="muted">Carrinho</span></div>
        <div id="cart" class="cart pdv1094-cart"></div>
      </div>

      <details class="buyer-details pdv1094-buyer"><summary>Dados opcionais do comprovante</summary><div class="form-grid compact"><div><label>CPF/CNPJ</label><input id="compradorDocumento" placeholder="Opcional"></div><div><label>Telefone</label><input id="compradorTelefone" placeholder="Opcional"></div><div class="full"><label>E-mail</label><input id="compradorEmail" type="email" placeholder="Opcional"></div></div></details>

      <div class="pdv1094-bottom">
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
      </div>
    </section>

    <section class="pdv1094-catalog">
      <div class="pdv1094-section-head"><h3>Categorias</h3><button type="button" class="pdv1094-search-focus" onclick="document.querySelector('#buscaTexto')?.focus()">⌕ Pesquisar</button></div>
      <div id="pdvCategorias" class="pdv1094-categories"></div>
      <div class="pdv1094-catalog-tabs"><button id="pdvTabProdutos" type="button" class="active" onclick="setPdvTipo('produtos')">Produtos</button><button id="pdvTabServicos" type="button" onclick="setPdvTipo('servicos')">Serviços</button></div>
      <div id="pdvProdutosPanel" class="pdv1094-panel"><div id="listaProdutos" class="pdv1094-product-grid"></div></div>
      <div id="pdvServicosPanel" class="pdv1094-panel hidden"><div id="listaServicos" class="pdv1094-service-grid"></div></div>
    </section>
  </div>
</section>'''
html=sub1(r'<section id="caixa" class="section active.*?</section>\s*\n\s*<section id="produtos"',novo_caixa+'\n\n<section id="produtos"',html,'substituir Caixa completo',re.S)
write('public/index.html',html)

js=read('public/app.js')
js=js.replace('const atual="10.9.3"','const atual="10.9.4"',1)
# 25 produtos por página na tela Produtos.
js=js.replace('const produtosPorPagina=3;','const produtosPorPagina=25;',1)
js=js.replace('${a.length} produtos · 3 por página','${a.length} produtos · 25 por página',1)

# Catálogo do novo Caixa: sem remontar DOM antigo.
new_catalog=r'''let pdvCategoriaAtiva="Todos";
let pdvTipoAtivo="produtos";
function pdvFavoritosSet(){try{return new Set(JSON.parse(localStorage.getItem("eletromix_pdv_favoritos")||"[]").map(Number))}catch{return new Set()}}
function setPdvCategoria(nome){pdvCategoriaAtiva=nome;pdvTipoAtivo="produtos";renderBuscaProdutos()}
function setPdvTipo(tipo){pdvTipoAtivo=tipo==="servicos"?"servicos":"produtos";renderBuscaProdutos()}
function togglePdvFavorito(id,event){event?.stopPropagation?.();const f=pdvFavoritosSet();f.has(Number(id))?f.delete(Number(id)):f.add(Number(id));localStorage.setItem("eletromix_pdv_favoritos",JSON.stringify([...f]));renderBuscaProdutos()}
function renderBuscaProdutos(){
  const q=normalizarBusca($("#buscaTexto")?.value),ativos=produtos.filter(p=>p.ativo),favoritos=pdvFavoritosSet();
  const categorias=["Todos","★ Favoritos",...new Set(ativos.map(p=>(p.categoria||"Geral").trim()||"Geral"))];
  if(!categorias.includes(pdvCategoriaAtiva))pdvCategoriaAtiva="Todos";
  const cats=$("#pdvCategorias");if(cats)cats.innerHTML=categorias.map(c=>`<button type="button" class="pdv1094-cat ${c===pdvCategoriaAtiva?"active":""}" onclick='setPdvCategoria(${JSON.stringify(c)})'>${esc(c)}</button>`).join("");
  const produtosFiltrados=ativos.filter(p=>{
    if(pdvCategoriaAtiva==="★ Favoritos"&&!favoritos.has(Number(p.id)))return false;
    if(pdvCategoriaAtiva!=="Todos"&&pdvCategoriaAtiva!=="★ Favoritos"&&(p.categoria||"Geral")!==pdvCategoriaAtiva)return false;
    if(!q)return true;return [p.nome,p.marca,p.categoria,p.codigo,p.codigoBarras].map(normalizarBusca).some(v=>v.includes(q));
  }).slice(0,30);
  const lp=$("#listaProdutos");if(lp)lp.innerHTML=produtosFiltrados.map(p=>`<article class="pdv1094-product" onclick="add(${p.id})"><button type="button" class="pdv1094-fav" onclick="togglePdvFavorito(${p.id},event)">${favoritos.has(Number(p.id))?"★":"☆"}</button><div class="pdv1094-product-icon">▣</div><b>${esc(p.nome)}</b><small>${esc(p.categoria||"Geral")} · Est. ${p.estoque}</small><strong>${money(p.precoVenda)}</strong></article>`).join("")||'<p class="muted">Nenhum produto encontrado.</p>';
  const ss=servicos.filter(s=>s.ativo&&(!q||[s.nome,s.categoria,s.descricao].map(normalizarBusca).some(v=>v.includes(q)))).slice(0,30);
  const ls=$("#listaServicos");if(ls)ls.innerHTML=ss.map(s=>`<article class="pdv1094-product pdv1094-service" onclick="addServico(${s.id})"><div class="pdv1094-product-icon">⌁</div><b>${esc(s.nome)}</b><small>${esc(s.categoria||"Serviço")}</small><strong>${money(s.preco)}</strong></article>`).join("")||'<p class="muted">Nenhum serviço encontrado.</p>';
  $("#pdvProdutosPanel")?.classList.toggle("hidden",pdvTipoAtivo!=="produtos");$("#pdvServicosPanel")?.classList.toggle("hidden",pdvTipoAtivo!=="servicos");$("#pdvTabProdutos")?.classList.toggle("active",pdvTipoAtivo==="produtos");$("#pdvTabServicos")?.classList.toggle("active",pdvTipoAtivo==="servicos");
}'''
js=sub1(r'let pdvCategoriaAtiva="Todos";.*?\nfunction add\(id\)\{',new_catalog+'\nfunction add(id){',js,'novo catálogo PDV',re.S)

# Não bloquear venda por abertura manual: backend cria turno automaticamente.
js=js.replace('async function finish(){if(!caixaAtual)return toast("Abra o caixa antes de vender.");','async function finish(){',1)
write('public/app.js',js)

server=read('src/server.ts')
# Garante um caixa interno automático por usuário/loja para preservar relatórios, sem tela de abrir/fechar.
anchor='''function caixaAbertoDoUsuario(usuarioId:number,lojaId:number) {
  return db.caixas.find(c => c.lojaId===lojaId && c.usuarioId === usuarioId && c.status === "aberto");
}'''
if anchor not in server: raise RuntimeError('funcao caixaAbertoDoUsuario não encontrada')
auto=anchor+'''\nfunction garantirCaixaAutomatico(u:Usuario,lojaId:number){\n  const atual=caixaAbertoDoUsuario(u.id,lojaId);if(atual)return atual;\n  const c:Caixa={lojaId,id:db.seq.caixa++,usuarioId:u.id,usuarioNome:u.nome,abertoEm:now(),saldoInicial:0,status:"aberto"};\n  db.caixas.push(c);salvar();return c;\n}'''
server=server.replace(anchor,auto,1)
server=server.replace('app.get("/api/caixa/status",auth,(req,res)=>res.json(caixaAbertoDoUsuario((req as any).usuario.id,lojaIdReq(req))||null));','app.get("/api/caixa/status",auth,(req,res)=>{const u=(req as any).usuario as Usuario;res.json(garantirCaixaAutomatico(u,lojaIdReq(req)));});',1)
server=server.replace('const lojaId=lojaIdReq(req);if(!caixaAbertoDoUsuario(u.id,lojaId))return res.status(400).json({erro:"Abra o caixa antes de registrar vendas."});','const lojaId=lojaIdReq(req);garantirCaixaAutomatico(u,lojaId);',1)
write('src/server.ts',server)

css=read('public/style.css')+r'''
/* 10.9.4 - Caixa totalmente reconstruído */
.caixa-1094{width:100%;max-width:none!important}.pdv1094-topline{display:flex;align-items:end;justify-content:space-between;gap:18px;margin-bottom:12px}.pdv1094-topline h2{margin:0;font-size:26px;letter-spacing:-.03em}.pdv1094-topline p{margin:3px 0 0;color:var(--text-muted)}.pdv1094-assignment{display:grid;grid-template-columns:minmax(230px,1fr) minmax(260px,1fr);gap:9px;min-width:min(620px,55vw)}.pdv1094-field{position:relative}.pdv1094-field label{margin:0 0 4px;font-size:11px}.pdv1094-field select{margin:0;min-height:38px}.pdv1094-field .lock-status{position:absolute;right:44px;top:0;font-size:9px}.pdv1094-client-head{display:flex;justify-content:space-between;align-items:center}.pdv1094-client-head .link-button{font-size:11px}.pdv1094-shell{display:grid;grid-template-columns:minmax(430px,43%) minmax(520px,57%);gap:10px;min-height:calc(100vh - 155px)}.pdv1094-sale,.pdv1094-catalog{border:1px solid var(--border);background:var(--card-bg);border-radius:12px;padding:11px;min-width:0;box-shadow:0 5px 16px rgba(0,0,0,.04)}.pdv1094-sale{display:flex;flex-direction:column;gap:9px}.pdv1094-codebar{display:grid;grid-template-columns:.75fr 1.25fr;gap:7px}.pdv1094-codebar label{font-size:10px;margin:0 0 3px}.pdv1094-codebar input{margin:0;min-height:39px}.pdv1094-cart-card{flex:1;min-height:220px;border:1px solid var(--border);border-radius:9px;padding:9px}.pdv1094-section-head{display:flex;align-items:center;justify-content:space-between;gap:10px}.pdv1094-section-head h3{margin:0;font-size:14px}.pdv1094-cart{max-height:34vh!important;min-height:180px!important}.pdv1094-buyer{margin:0!important}.pdv1094-bottom{display:grid;grid-template-columns:1fr .9fr;gap:9px}.pdv1094-totals,.pdv1094-payment{border:1px solid var(--border);border-radius:9px;padding:9px;margin:0!important}.pdv1094-total{border-top:1px solid var(--border);padding-top:8px!important;margin-top:8px!important}.pdv1094-total b{font-size:22px}.pdv1094-payment select{margin:4px 0 7px}.pdv1094-charge{width:100%;min-height:54px;font-size:18px;font-weight:900;letter-spacing:.02em}.pdv1094-catalog{display:flex;flex-direction:column;gap:8px}.pdv1094-search-focus{border:1px solid var(--border);background:var(--card-bg);color:var(--text-main);border-radius:7px;padding:6px 10px;cursor:pointer}.pdv1094-categories{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:6px}.pdv1094-cat{min-height:52px;border:1px solid var(--border);background:color-mix(in srgb,var(--card-bg) 90%,var(--page-bg));color:var(--text-main);border-radius:7px;font-weight:800;font-size:11px;cursor:pointer;padding:6px}.pdv1094-cat.active{background:var(--accent)!important;color:#fff!important;border-color:var(--accent)!important}.pdv1094-catalog-tabs{display:grid;grid-template-columns:1fr 1fr;gap:6px}.pdv1094-catalog-tabs button{height:36px;border:1px solid var(--border);background:var(--card-bg);color:var(--text-main);border-radius:7px;font-weight:800;cursor:pointer}.pdv1094-catalog-tabs button.active{background:color-mix(in srgb,var(--accent) 14%,var(--card-bg));border-color:var(--accent);color:var(--accent)}.pdv1094-panel{flex:1;min-height:0}.pdv1094-product-grid,.pdv1094-service-grid{display:grid;grid-template-columns:repeat(4,minmax(110px,1fr));gap:7px;max-height:58vh;overflow:auto;padding-right:2px}.pdv1094-product{position:relative;min-height:116px;border:1px solid var(--border);background:var(--card-bg);border-radius:8px;padding:25px 8px 9px;display:flex;flex-direction:column;justify-content:flex-end;gap:4px;cursor:pointer}.pdv1094-product:hover{border-color:var(--accent);box-shadow:0 5px 14px rgba(0,0,0,.06)}.pdv1094-product-icon{font-size:21px;opacity:.55;margin-bottom:auto}.pdv1094-product b{font-size:11.5px;line-height:1.2}.pdv1094-product small{font-size:9.5px;color:var(--text-muted)}.pdv1094-product strong{font-size:13px;color:var(--accent)}.pdv1094-fav{position:absolute;right:5px;top:4px;border:0;background:transparent;color:var(--accent);font-size:18px;cursor:pointer}.products-real-pager span{font-size:12px}@media(max-width:1180px){.pdv1094-shell{grid-template-columns:1fr}.pdv1094-assignment{min-width:0}.pdv1094-product-grid,.pdv1094-service-grid{grid-template-columns:repeat(4,1fr);max-height:420px}}@media(max-width:820px){.pdv1094-topline{align-items:stretch;flex-direction:column}.pdv1094-assignment,.pdv1094-codebar,.pdv1094-bottom{grid-template-columns:1fr}.pdv1094-product-grid,.pdv1094-service-grid{grid-template-columns:repeat(2,1fr)}.pdv1094-categories{grid-template-columns:repeat(3,1fr)}}
'''
write('public/style.css',css)
print('10.9.4: Caixa reconstruído, caixa automático e Produtos com 25 por página.')