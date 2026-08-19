from pathlib import Path
import json

root = Path("app")


def read(path: str) -> str:
    return (root / path).read_text(encoding="utf-8")


def write(path: str, content: str) -> None:
    (root / path).write_text(content, encoding="utf-8")


def replace_once(content: str, old: str, new: str, label: str) -> str:
    if old not in content:
        raise SystemExit(f"Trecho não encontrado: {label}")
    return content.replace(old, new, 1)


pkg = json.loads(read("package.json"))
pkg["version"] = "10.10.27"
write("package.json", json.dumps(pkg, indent=2, ensure_ascii=False))

html = read("public/index.html")
html = replace_once(
    html,
    'id="versionInfo" class="version-info">v10.10.26',
    'id="versionInfo" class="version-info">v10.10.27',
    "versão no cabeçalho",
)
html = replace_once(
    html,
    '<thead><tr><th>Código</th><th>Cód. barras</th><th>Produto</th>',
    '<thead><tr><th class="product-image-column-101027">Imagem</th><th>Código</th><th>Cód. barras</th><th>Produto</th>',
    "coluna de imagem dos produtos",
)
write("public/index.html", html)

server = read("src/server.ts")
server = replace_once(
    server,
    '  id:number; codigo:string; codigoBarras:string; nome:string; categoria:string; marca:string;\n',
    '  id:number; codigo:string; codigoBarras:string; nome:string; categoria:string; marca:string; imagemUrl?:string;\n',
    "tipo Produto com imagem",
)
server = replace_once(
    server,
    'for (const p of db.produtos) (p as any).codigoBarras ??= "";',
    'for (const p of db.produtos) {(p as any).codigoBarras ??= "";try{(p as any).imagemUrl=normalizarImagemProduto((p as any).imagemUrl)}catch{(p as any).imagemUrl=""}}',
    "migração da imagem do produto",
)
server = replace_once(
    server,
    '// Produtos\napp.get("/api/produtos",auth,(_req,res)=>{',
    '''// Produtos
function normalizarImagemProduto(raw:any):string{
  const value=String(raw||"").trim();
  if(!value)return "";
  if(value.length>2048)throw new Error("O endereço da imagem é muito grande.");
  let parsed:URL;try{parsed=new URL(value)}catch{throw new Error("Endereço de imagem inválido.")}
  if(parsed.protocol!=="https:")throw new Error("A imagem do produto precisa usar um endereço HTTPS.");
  return parsed.toString();
}
app.get("/api/produtos",auth,(_req,res)=>{''',
    "validação de imagem do produto",
)
server = replace_once(
    server,
    'const {codigo,codigoBarras="",nome,categoria,marca,precoCusto,precoVenda,estoque=0,estoqueMinimo=1}=req.body;',
    'const {codigo,codigoBarras="",nome,categoria,marca,imagemUrl="",precoCusto,precoVenda,estoque=0,estoqueMinimo=1}=req.body;',
    "imagem no cadastro do produto",
)
server = replace_once(
    server,
    'if(!codigo||!nome||!categoria||!marca||precoVenda===undefined)return res.status(400).json({erro:"Preencha os campos obrigatórios."});',
    'if(!codigo||!nome||!categoria||!marca||precoVenda===undefined)return res.status(400).json({erro:"Preencha os campos obrigatórios."});let imagemNormalizada="";try{imagemNormalizada=normalizarImagemProduto(imagemUrl)}catch(e:any){return res.status(400).json({erro:String(e?.message||e)})}',
    "validar imagem no cadastro",
)
server = replace_once(
    server,
    'categoria:String(categoria),marca:String(marca),precoCusto:',
    'categoria:String(categoria),marca:String(marca),imagemUrl:imagemNormalizada,precoCusto:',
    "salvar imagem no cadastro",
)
server = replace_once(
    server,
    'p.codigo=novoCodigo;p.codigoBarras=novoCodigoBarras;p.nome=String(req.body.nome??p.nome);p.categoria=String(req.body.categoria??p.categoria);p.marca=String(req.body.marca??p.marca);',
    'p.codigo=novoCodigo;p.codigoBarras=novoCodigoBarras;p.nome=String(req.body.nome??p.nome);p.categoria=String(req.body.categoria??p.categoria);p.marca=String(req.body.marca??p.marca);if(req.body.imagemUrl!==undefined){try{p.imagemUrl=normalizarImagemProduto(req.body.imagemUrl)}catch(e:any){return res.status(400).json({erro:String(e?.message||e)})}}',
    "atualizar imagem do produto",
)
write("src/server.ts", server)

js = read("public/app.js")
js = js.replace('const atual="10.10.26"', 'const atual="10.10.27"', 1)
thumb_helpers = '''function imagemProdutoSegura101027(produto){
  const raw=String(produto?.imagemUrl||"").trim();if(!raw)return "";
  try{const url=new URL(raw);return url.protocol==="https:"?esc(url.href):""}catch{return ""}
}
function miniaturaProduto101027(produto,tipo="lista"){
  const url=imagemProdutoSegura101027(produto),size=tipo==="caixa"?46:40;
  return `<span class="product-thumb-101027 product-thumb-${tipo}-101027"><span class="product-thumb-fallback-101027" aria-hidden="true">▣</span>${url?`<img src="${url}" alt="${esc(produto?.nome||"Produto")}" width="${size}" height="${size}" loading="lazy" decoding="async" fetchpriority="low" onload="this.parentElement.classList.add('loaded')" onerror="this.hidden=true;this.parentElement.classList.add('failed')">`:""}</span>`;
}
'''
js = replace_once(
    js,
    'function renderBuscaProdutos(){',
    thumb_helpers + 'function renderBuscaProdutos(){',
    "helpers de miniatura",
)
js = replace_once(
    js,
    '<div class="pdv1094-product-icon">▣</div><b>${esc(p.nome)}</b>',
    '${miniaturaProduto101027(p,"caixa")}<b>${esc(p.nome)}</b>',
    "imagem no catálogo do caixa",
)
old_product_row = '''$("#tableProdutos").innerHTML=visiveis.map(p=>`<tr><td>${esc(p.codigo)}</td><td>${esc(p.codigoBarras||"-")}</td><td>${esc(p.nome)}</td><td>${esc(p.marca)}</td><td>${money(p.precoVenda)}</td><td>${p.estoque<=p.estoqueMinimo?"⚠️ ":""}${p.estoque}</td><td class="${p.ativo?"status-ok":"status-off"}">${p.ativo?"Ativo":"Inativo"}</td><td><div class="row-actions"><button class="edit" onclick="editProduto(${p.id})">Editar</button><button class="edit" onclick="stockProduto(${p.id})">Estoque</button></div></td></tr>`).join("")||'<tr><td colspan="8" class="muted">Nenhum produto encontrado.</td></tr>';'''
new_product_row = '''$("#tableProdutos").innerHTML=visiveis.map(p=>`<tr><td class="product-image-cell-101027">${miniaturaProduto101027(p,"lista")}</td><td>${esc(p.codigo)}</td><td>${esc(p.codigoBarras||"-")}</td><td>${esc(p.nome)}</td><td>${esc(p.marca)}</td><td>${money(p.precoVenda)}</td><td>${p.estoque<=p.estoqueMinimo?"⚠️ ":""}${p.estoque}</td><td class="${p.ativo?"status-ok":"status-off"}">${p.ativo?"Ativo":"Inativo"}</td><td><div class="row-actions"><button class="edit" onclick="editProduto(${p.id})">Editar</button><button class="edit" onclick="stockProduto(${p.id})">Estoque</button></div></td></tr>`).join("")||'<tr><td colspan="9" class="muted">Nenhum produto encontrado.</td></tr>';'''
js = replace_once(js, old_product_row, new_product_row, "imagem na lista de produtos")
js = replace_once(
    js,
    '''async function loadCloudStatus(){
  if(!token||!me)return;
  try{const r=await api("/api/cloud/status"),d=await r.json(),b=$("#cloudBadge"),t=$("#cloudText");if(!b||!t)return;t.textContent=d.state==="online"?"Online":d.state==="syncing"?"Sincronizando":d.state==="offline"?"Offline":"Local";b.className=`cloud-badge ${d.state||"local"}`;b.title=d.message||"Status da nuvem"}catch{}
}''',
    '''let cloudVersionProdutos101027=null,cloudRefreshProdutos101027=false;
async function loadCloudStatus(){
  if(!token||!me)return;
  try{const r=await api("/api/cloud/status"),d=await r.json(),b=$("#cloudBadge"),t=$("#cloudText");if(!b||!t)return;t.textContent=d.state==="online"?"Online":d.state==="syncing"?"Sincronizando":d.state==="offline"?"Offline":"Local";b.className=`cloud-badge ${d.state||"local"}`;b.title=d.message||"Status da nuvem";
    const version=Number(d.version)||0;if(cloudVersionProdutos101027===null)cloudVersionProdutos101027=version;else if(version>cloudVersionProdutos101027&&!cloudRefreshProdutos101027){cloudVersionProdutos101027=version;cloudRefreshProdutos101027=true;loadProdutos().finally(()=>{cloudRefreshProdutos101027=false})}
  }catch{}
}''',
    "atualização leve após sincronização mobile",
)
write("public/app.js", js)

css = read("public/style.css") + r'''

/* 10.10.27 - miniaturas de produtos sincronizadas com o app mobile */
.product-image-column-101027{width:54px}.product-image-cell-101027{width:54px;padding-block:5px!important}.product-thumb-101027{position:relative;display:grid;place-items:center;flex:0 0 auto;overflow:hidden;border:1px solid var(--border);border-radius:8px;background:color-mix(in srgb,var(--page-bg) 72%,var(--card-bg));color:var(--text-muted)}.product-thumb-lista-101027{width:40px;height:40px}.product-thumb-caixa-101027{width:46px;height:46px;margin:0 0 auto}.product-thumb-101027 img{position:absolute;inset:0;z-index:2;width:100%;height:100%;display:block;object-fit:contain;background:var(--card-bg)}.product-thumb-fallback-101027{font-size:16px;line-height:1;opacity:.52}.product-thumb-101027.loaded .product-thumb-fallback-101027{visibility:hidden}.product-thumb-101027.failed img{display:none!important}.pdv1094-product>.product-thumb-caixa-101027{margin-bottom:auto}.performance-lite-101025 .product-thumb-101027{border-radius:5px}.performance-lite-101025 .product-thumb-101027 img{image-rendering:auto}
body[data-monitor-profile="1024x768"] #caixa .product-thumb-caixa-101027{width:36px;height:36px;border-radius:6px}
'''
write("public/style.css", css)

print("10.10.27: imagens do app mobile exibidas no Caixa e em Produtos com carregamento leve.")
