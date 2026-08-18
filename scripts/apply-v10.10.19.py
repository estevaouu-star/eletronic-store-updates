from pathlib import Path
import json

root = Path("app")


def read(path: str) -> str:
    return (root / path).read_text(encoding="utf-8")


def write(path: str, content: str) -> None:
    (root / path).write_text(content, encoding="utf-8")


pkg = json.loads(read("package.json"))
pkg["version"] = "10.10.19"
write("package.json", json.dumps(pkg, indent=2, ensure_ascii=False))

html = read("public/index.html").replace(
    'id="versionInfo" class="version-info">v10.10.18',
    'id="versionInfo" class="version-info">v10.10.19',
    1,
)
write("public/index.html", html)

server = read("src/server.ts")
old_login = '''app.post("/api/login",(req,res)=>{
  const login=String(req.body.login||"").trim();
  const senha=String(req.body.senha||"");
  const u=db.usuarios.find(x=>x.login===login&&x.ativo);
  if(!u||u.senhaHash!==senhaHash(senha))return res.status(401).json({erro:"Login ou senha incorretos."});'''
new_login = '''app.post("/api/login",(req,res)=>{
  const login=String(req.body.login||"").trim();
  const senha=String(req.body.senha||"");
  const loginNormalizado=login.toLocaleLowerCase("pt-BR");
  const u=db.usuarios.find(x=>x.ativo&&String(x.login||"").trim().toLocaleLowerCase("pt-BR")===loginNormalizado);
  if(!u||u.senhaHash!==senhaHash(senha))return res.status(401).json({erro:"Login ou senha incorretos."});'''
if old_login not in server:
    raise SystemExit("Trecho de login esperado não foi encontrado.")
server = server.replace(old_login, new_login, 1)
write("src/server.ts", server)

js = read("public/app.js").replace(
    'const atual="10.10.18"', 'const atual="10.10.19"', 1
)
js += r'''

// 10.10.19 - correção consolidada de login, abas e Produtos.
// Compatibilidade com as rotinas antigas de sessão: o nome real desta base é lojaId.
try{
 Object.defineProperty(window,'storeId',{configurable:true,get:()=>lojaId,set:value=>{const id=Number(value);if(id>0){lojaId=id;localStorage.setItem('es_store_id',String(id))}}});
 window.loadStores=loadLojas;
 window.loadAll=boot;
}catch(e){console.error('[compatibilidade 101019]',e)}

// Sempre usa a aba clicada como fonte da verdade. Isso elimina a disputa entre
// os patches antigos que alternavam class, hidden e display separadamente.
function activateSection101019(sectionId){
 const section=document.getElementById(String(sectionId||''));
 if(!section||!section.classList.contains('section'))return false;
 document.querySelectorAll('.nav[data-s]').forEach(nav=>nav.classList.toggle('active',nav.dataset.s===section.id));
 document.querySelectorAll('.section').forEach(item=>{
   const active=item===section;
   item.classList.toggle('active',active);
   item.hidden=!active;
   item.setAttribute('aria-hidden',active?'false':'true');
   item.style.setProperty('display',active?(item.id==='caixa'?'flex':'block'):'none','important');
 });
 document.body.classList.toggle('caixa-mode-10103',section.id==='caixa');
 document.body.classList.toggle('caixa-ativo-101014',section.id==='caixa');
 return true;
}
document.addEventListener('click',event=>{
 const nav=event.target.closest?.('.nav[data-s]');
 if(!nav)return;
 const id=nav.dataset.s;
 queueMicrotask(()=>activateSection101019(id));
 setTimeout(()=>activateSection101019(id),0);
 setTimeout(()=>activateSection101019(id),120);
},true);
document.addEventListener('DOMContentLoaded',()=>{
 const id=document.querySelector('.nav.active[data-s]')?.dataset.s||'caixa';
 activateSection101019(id);
});
const showAppBase101019=showApp;
showApp=function(){showAppBase101019();setTimeout(()=>activateSection101019(document.querySelector('.nav.active[data-s]')?.dataset.s||'caixa'),0)};

// Unifica o critério do Dashboard e da lista de Produtos.
produtoTemInformacaoFaltando=function(produto){
 return !!produto?.ativo&&informacoesFaltantesProduto(produto).length>0;
};
try{produtoIncompleto10106=produtoTemInformacaoFaltando}catch{}

function syncProdutos101019(){
 document.querySelector('#produtosIncompletosBtn')?.remove();
 const section=document.querySelector('#produtos');
 if(!section)return;
 let button=document.querySelector('#filtroInfoProdutoBtn');
 if(!button){
   const toolbar=section.querySelector('.toolbar');
   if(!toolbar)return;
   button=document.createElement('button');
   button.id='filtroInfoProdutoBtn';
   button.type='button';
   button.className='secondary small';
   toolbar.appendChild(button);
 }
 button.textContent='Faltando informações';
 button.hidden=false;
 button.disabled=false;
 button.style.removeProperty('display');
 button.classList.toggle('active',!!produtosSomenteIncompletos);
 button.setAttribute('aria-pressed',produtosSomenteIncompletos?'true':'false');
}
const renderProdutosBase101019=renderProdutos;
renderProdutos=function(){renderProdutosBase101019();syncProdutos101019()};
document.addEventListener('click',event=>{
 const pending=event.target.closest?.('[data-pending="incompletos"]');
 if(!pending)return;
 produtosSomenteIncompletos=true;
 filtroProdutosIncompletos=true;
 produtosPagina=1;
 const nav=document.querySelector('.nav[data-s="produtos"]');
 nav?.click();
 setTimeout(()=>{activateSection101019('produtos');syncProdutos101019();renderProdutos()},100);
},true);
document.addEventListener('click',event=>{
 if(event.target.closest?.('.nav[data-s="produtos"]'))setTimeout(syncProdutos101019,30);
},true);
document.addEventListener('DOMContentLoaded',()=>setTimeout(syncProdutos101019,80));
setTimeout(syncProdutos101019,300);
'''
write("public/app.js", js)

css = read("public/style.css") + r'''

/* 10.10.19 - uma única seção visível e filtro de pendências consistente. */
.section[hidden]{display:none!important}
#filtroInfoProdutoBtn.active{background:var(--accent);color:#fff;border-color:var(--accent)}
'''
write("public/style.css", css)

print("10.10.19: login sem diferença de maiúsculas, navegação consolidada e filtro de Produtos alinhado ao Dashboard.")
