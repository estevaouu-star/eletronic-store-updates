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
html = replace_once(html, 'id="versionInfo" class="version-info">v10.10.26', 'id="versionInfo" class="version-info">v10.10.27', "versão no cabeçalho")
write("public/index.html", html)

server = read("src/server.ts")
server = replace_once(
    server,
    "  ativo:boolean; criadoEm:string; atualizadoEm:string;\n",
    "  imagemUrl?:string; ativo:boolean; criadoEm:string; atualizadoEm:string;\n",
    "campo de foto no produto",
)
server = replace_once(
    server,
    "      (p as any).ativo ??= true;\n      (p as any).atualizadoEm ??= p.criadoEm || now();",
    "      (p as any).ativo ??= true;\n      (p as any).imagemUrl ??= \"\";\n      (p as any).atualizadoEm ??= p.criadoEm || now();",
    "migração das fotos",
)
server = replace_once(
    server,
    '''app.post("/api/produtos",auth,admin,(req,res)=>{
  const {codigo,codigoBarras="",nome,categoria,marca,precoCusto,precoVenda,estoque=0,estoqueMinimo=1}=req.body;''',
    '''app.post("/api/produtos/imagem",auth,admin,async(req,res)=>{
  try{
    const dataUrl=String(req.body.dataUrl||"");
    if(!/^data:image\\/(jpeg|png|webp);base64,/i.test(dataUrl)||dataUrl.length>850_000)return res.status(400).json({erro:"A imagem é inválida ou ficou grande demais."});
    const c=cloudCfg();
    if(!c?.enabled||!c.syncId||!c.secret)return res.status(503).json({erro:"Ative a sincronização online para salvar fotos de produtos."});
    const mobileUrl=String(process.env.ELETROMIX_MOBILE_URL||"https://eletromix-mobile.estevaouu.chatgpt.site").replace(/\\/$/,"");
    const response=await fetch(`${mobileUrl}/api/mobile`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({action:"product-image-sync",syncId:c.syncId,syncSecret:c.secret,dataUrl})});
    const result=await response.json() as any;
    if(!response.ok||!result?.imageUrl)return res.status(response.status||502).json({erro:result?.error||"Não foi possível enviar a foto."});
    res.json({imagemUrl:String(result.imageUrl)});
  }catch(e:any){res.status(502).json({erro:String(e?.message||"Não foi possível enviar a foto.")});}
});

app.post("/api/produtos",auth,admin,(req,res)=>{
  const {codigo,codigoBarras="",nome,categoria,marca,precoCusto,precoVenda,estoque=0,estoqueMinimo=1,imagemUrl=""}=req.body;''',
    "rota de envio da foto",
)
server = replace_once(
    server,
    "estoqueMinimo:Math.max(0,Number(estoqueMinimo)||0),ativo:true,criadoEm:now(),atualizadoEm:now()",
    "estoqueMinimo:Math.max(0,Number(estoqueMinimo)||0),imagemUrl:String(imagemUrl||\"\"),ativo:true,criadoEm:now(),atualizadoEm:now()",
    "foto ao cadastrar produto",
)
server = replace_once(
    server,
    "p.precoCusto=Number(req.body.precoCusto??p.precoCusto);p.precoVenda=Number(req.body.precoVenda??p.precoVenda);p.estoqueMinimo=Math.max(0,Number(req.body.estoqueMinimo??p.estoqueMinimo));",
    "p.precoCusto=Number(req.body.precoCusto??p.precoCusto);p.precoVenda=Number(req.body.precoVenda??p.precoVenda);p.estoqueMinimo=Math.max(0,Number(req.body.estoqueMinimo??p.estoqueMinimo));p.imagemUrl=String(req.body.imagemUrl??p.imagemUrl??\"\");",
    "foto ao editar produto",
)
write("src/server.ts", server)

app = read("public/app.js")
app = replace_once(app, 'const atual="10.10.26"', 'const atual="10.10.27"', "versão do atualizador")
app = replace_once(
    app,
    '''<div class="pdv1094-product-icon">▣</div><b>${esc(p.nome)}</b>''',
    '''${p.imagemUrl?`<img class="pdv1094-product-photo" src="${esc(p.imagemUrl)}" alt="" loading="lazy">`:`<div class="pdv1094-product-icon">▣</div>`}<b>${esc(p.nome)}</b>''',
    "foto no caixa",
)
app = replace_once(
    app,
    '''<td>${esc(p.nome)}</td><td>${esc(p.marca)}</td>''',
    '''<td><div class="product-name-photo">${p.imagemUrl?`<img src="${esc(p.imagemUrl)}" alt="" loading="lazy">`:`<span>▦</span>`}<b>${esc(p.nome)}</b></div></td><td>${esc(p.marca)}</td>''',
    "foto na tabela de produtos",
)
old_form = '''function produtoForm(p={}){return `<form id="modalProductForm" class="form-grid"><div><label>Código interno</label><input name="codigo" value="${esc(p.codigo||"")}" required></div><div><label>Código de barras</label><input name="codigoBarras" value="${esc(p.codigoBarras||"")}" placeholder="EAN/UPC ou código interno"></div><div><label>Nome</label><input name="nome" value="${esc(p.nome||"")}" required></div><div><label>Categoria</label><input name="categoria" value="${esc(p.categoria||"")}" required></div><div><label>Marca</label><input name="marca" value="${esc(p.marca||"")}" required></div><div><label>Preço de custo</label><input name="precoCusto" type="number" step=".01" value="${p.precoCusto??0}"></div><div><label>Preço de venda</label><input name="precoVenda" type="number" step=".01" value="${p.precoVenda??0}" required></div><div><label>Estoque mínimo</label><input name="estoqueMinimo" type="number" value="${p.estoqueMinimo??1}"></div>${p.id?`<div><label>Status</label><select name="ativo"><option value="true" ${p.ativo?"selected":""}>Ativo</option><option value="false" ${!p.ativo?"selected":""}>Inativo</option></select></div>`:`<div><label>Estoque inicial</label><input name="estoque" type="number" value="0"></div>`}<button class="primary full">${p.id?"Salvar alterações":"Cadastrar produto"}</button></form>`}'''
new_form = '''let produtoImagemPendente101027=null;
function produtoForm(p={}){return `<form id="modalProductForm" class="form-grid"><div class="full product-photo-file"><div id="produtoImagemPreview" class="product-photo-desktop">${p.imagemUrl?`<img src="${esc(p.imagemUrl)}" alt="Foto do produto">`:`<span>▦<small>Sem foto</small></span>`}</div><div><b>Foto do produto</b><p>Escolha uma imagem salva no computador. Ela será reduzida automaticamente.</p><label class="secondary product-file-button">Selecionar arquivo<input id="produtoImagemArquivo" name="imagemArquivo" type="file" accept="image/*"></label>${p.imagemUrl?'<button id="removerImagemProduto" class="product-photo-remove" type="button">Remover foto</button>':""}</div></div><div><label>Código interno</label><input name="codigo" value="${esc(p.codigo||"")}" required></div><div><label>Código de barras</label><input name="codigoBarras" value="${esc(p.codigoBarras||"")}" placeholder="EAN/UPC ou código interno"></div><div><label>Nome</label><input name="nome" value="${esc(p.nome||"")}" required></div><div><label>Categoria</label><input name="categoria" value="${esc(p.categoria||"")}" required></div><div><label>Marca</label><input name="marca" value="${esc(p.marca||"")}" required></div><div><label>Preço de custo</label><input name="precoCusto" type="number" step=".01" value="${p.precoCusto??0}"></div><div><label>Preço de venda</label><input name="precoVenda" type="number" step=".01" value="${p.precoVenda??0}" required></div><div><label>Estoque mínimo</label><input name="estoqueMinimo" type="number" value="${p.estoqueMinimo??1}"></div>${p.id?`<div><label>Status</label><select name="ativo"><option value="true" ${p.ativo?"selected":""}>Ativo</option><option value="false" ${!p.ativo?"selected":""}>Inativo</option></select></div>`:`<div><label>Estoque inicial</label><input name="estoque" type="number" value="0"></div>`}<button class="primary full">${p.id?"Salvar alterações":"Cadastrar produto"}</button></form>`}
function blobDataUrl101027(blob){return new Promise((resolve,reject)=>{const r=new FileReader();r.onload=()=>resolve(String(r.result||""));r.onerror=reject;r.readAsDataURL(blob)})}
async function compactarImagemProduto101027(file){
  if(!file?.type?.startsWith("image/"))throw new Error("Escolha um arquivo de imagem.");
  if(file.size>12*1024*1024)throw new Error("A imagem original deve ter no máximo 12 MB.");
  const url=URL.createObjectURL(file);
  try{
    const image=await new Promise((resolve,reject)=>{const el=new Image();el.onload=()=>resolve(el);el.onerror=()=>reject(new Error("Não foi possível abrir a imagem."));el.src=url});
    for(const opt of [{side:900,quality:.78},{side:720,quality:.7},{side:560,quality:.62}]){
      const scale=Math.min(1,opt.side/Math.max(image.naturalWidth,image.naturalHeight)),canvas=document.createElement("canvas");canvas.width=Math.max(1,Math.round(image.naturalWidth*scale));canvas.height=Math.max(1,Math.round(image.naturalHeight*scale));const ctx=canvas.getContext("2d");if(!ctx)throw new Error("Não foi possível preparar a imagem.");ctx.drawImage(image,0,0,canvas.width,canvas.height);const blob=await new Promise(resolve=>canvas.toBlob(resolve,"image/jpeg",opt.quality));if(blob&&blob.size<=550000)return await blobDataUrl101027(blob);
    }
    throw new Error("A imagem ficou grande demais. Tente outra.");
  }finally{URL.revokeObjectURL(url)}
}
function renderProdutoImagemPreview101027(value){const host=$("#produtoImagemPreview");if(!host)return;host.innerHTML=value?`<img src="${esc(value)}" alt="Foto do produto">`:'<span>▦<small>Sem foto</small></span>'}
function bindProdutoImagem101027(){
  const input=$("#produtoImagemArquivo");if(input)input.onchange=async()=>{const file=input.files?.[0];if(!file)return;try{toast("Preparando imagem...");produtoImagemPendente101027=await compactarImagemProduto101027(file);renderProdutoImagemPreview101027(produtoImagemPendente101027);toast("Imagem pronta para salvar.")}catch(e){toast(e?.message||"Não foi possível preparar a imagem.")}finally{input.value=""}};
  const remove=$("#removerImagemProduto");if(remove)remove.onclick=()=>{produtoImagemPendente101027="";renderProdutoImagemPreview101027("");remove.remove()};
}'''
app = replace_once(app, old_form, new_form, "editor de foto do produto")
app = replace_once(
    app,
    '''function newProduto(){openModal("Novo produto",produtoForm());$("#modalProductForm").onsubmit=e=>saveProduto(e)}
function editProduto(id){const p=produtos.find(x=>x.id===id);openModal("Editar produto",produtoForm(p));$("#modalProductForm").onsubmit=e=>saveProduto(e,id)}''',
    '''function newProduto(){produtoImagemPendente101027=null;openModal("Novo produto",produtoForm());bindProdutoImagem101027();$("#modalProductForm").onsubmit=e=>saveProduto(e)}
function editProduto(id){const p=produtos.find(x=>x.id===id);produtoImagemPendente101027=null;openModal("Editar produto",produtoForm(p));bindProdutoImagem101027();$("#modalProductForm").onsubmit=e=>saveProduto(e,id)}''',
    "inicialização do editor de foto",
)
app = replace_once(
    app,
    '''    const raw=Object.fromEntries(new FormData(e.target));
    if(id)raw.ativo=raw.ativo==="true";''',
    '''    const raw=Object.fromEntries(new FormData(e.target));
    delete raw.imagemArquivo;
    if(id)raw.ativo=raw.ativo==="true";
    const atual=id?produtos.find(x=>x.id===id):null;
    let imagemUrl=produtoImagemPendente101027===null?(atual?.imagemUrl||""):produtoImagemPendente101027;
    if(String(imagemUrl).startsWith("data:image/")){
      toast("Enviando foto...");
      const upload=await api("/api/produtos/imagem",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({dataUrl:imagemUrl})}),resultado=await upload.json();
      if(!upload.ok)return toast(resultado.erro||"Não foi possível enviar a foto.");
      imagemUrl=resultado.imagemUrl;
    }
    raw.imagemUrl=imagemUrl;''',
    "envio da foto antes de salvar",
)
write("public/app.js", app)

css = read("public/style.css")
photos_css = '''
/* Fotos de produtos 10.10.27 */
.pdv1094-product-photo{width:100%;height:46px;min-height:0;object-fit:contain;object-position:center;margin-bottom:auto;border-radius:6px;background:color-mix(in srgb,var(--page-bg) 72%,var(--card-bg));pointer-events:none}
.product-name-photo{display:flex;align-items:center;gap:8px;min-width:150px}.product-name-photo img,.product-name-photo>span{width:36px;height:36px;flex:0 0 36px;border-radius:8px;background:color-mix(in srgb,var(--page-bg) 72%,var(--card-bg));object-fit:contain}.product-name-photo>span{display:grid;place-items:center;color:var(--accent)}.product-name-photo b{font-size:13px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.product-photo-file{display:grid!important;grid-template-columns:116px 1fr;gap:14px;align-items:center;padding:12px;border:1px solid var(--border);border-radius:12px;background:color-mix(in srgb,var(--page-bg) 65%,var(--card-bg))}.product-photo-desktop{display:grid;place-items:center;width:116px;height:116px;overflow:hidden;border:1px dashed var(--border);border-radius:11px;background:var(--card-bg)}.product-photo-desktop img{width:100%;height:100%;object-fit:contain}.product-photo-desktop>span{display:grid;justify-items:center;gap:5px;color:var(--accent);font-size:28px}.product-photo-desktop small{font-size:10px;color:var(--text-muted)}.product-photo-file p{margin:5px 0 9px;color:var(--text-muted);font-size:11px}.product-file-button{display:inline-flex!important;align-items:center;width:auto;padding:9px 12px!important;margin:0 7px 0 0!important;cursor:pointer}.product-file-button input{display:none}.product-photo-remove{border:0;background:transparent;color:var(--danger);font-size:11px;font-weight:800;cursor:pointer}
body[data-monitor-profile="1024x768"] #caixa .pdv1094-product-photo{height:32px!important;margin-bottom:2px!important}body[data-monitor-profile="1024x768"] #caixa .pdv1094-product{overflow:hidden!important}.performance-lite-101025 .pdv1094-product-photo{box-shadow:none!important}
@media(max-width:620px){.product-photo-file{grid-template-columns:88px 1fr}.product-photo-desktop{width:88px;height:88px}}

'''
css = replace_once(css, "/* 10.10.26 - impressora por loja e proteção visual de administradores */", photos_css + "/* 10.10.26 - impressora por loja e proteção visual de administradores */", "estilos das fotos")
write("public/style.css", css)

print("10.10.27: fotos de produtos no PDV e cadastro por arquivo, com layout seguro para monitor antigo.")
