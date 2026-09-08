from pathlib import Path
import json,re

root=Path("app")
def read(p): return (root/p).read_text(encoding="utf-8")
def write(p,s): (root/p).write_text(s,encoding="utf-8")
def must(s,a,b,label):
    if a not in s: raise SystemExit("trecho ausente: "+label)
    return s.replace(a,b,1)

pkg=json.loads(read("package.json"))
if pkg.get("version")!="10.11.29": raise SystemExit("base precisa ser 10.11.29")
pkg["version"]="10.11.30"
write("package.json",json.dumps(pkg,indent=2,ensure_ascii=False))

html=read("public/index.html")
html,n=re.subn(r'(id="versionInfo" class="version-info">v)10\.11\.29',r'\g<1>10.11.30',html,count=1)
if n!=1: raise SystemExit("versao HTML ausente")
write("public/index.html",html)

server=read("src/server.ts")
old='''for(const u of db.usuarios){
  if(!Array.isArray(u.lojaIds)){
    u.lojaIds=lojasAtivasIds();
    usuariosMigrados=true;
  }
  // Administradores criados nas versões anteriores tinham acesso global.
  if(u.cargo==="admin" && typeof u.acessoTodasLojas!=="boolean"){
    u.acessoTodasLojas=true;
    usuariosMigrados=true;
  }
  if(u.cargo!=="admin" && u.acessoTodasLojas){u.acessoTodasLojas=false;usuariosMigrados=true;}
}'''
new='''for(const u of db.usuarios){
  if(u.cargo==="admin"){
    const todas=lojasAtivasIds();
    if(u.acessoTodasLojas!==true||JSON.stringify(u.lojaIds||[])!==JSON.stringify(todas)){u.acessoTodasLojas=true;u.lojaIds=todas;usuariosMigrados=true;}
  }else{
    const validas=(Array.isArray(u.lojaIds)?u.lojaIds:[]).map(Number).filter(id=>lojasAtivasIds().includes(id));
    const unica=validas[0]||lojasAtivasIds()[0];
    const novas=unica?[unica]:[];
    if(u.acessoTodasLojas||JSON.stringify(u.lojaIds||[])!==JSON.stringify(novas)){u.acessoTodasLojas=false;u.lojaIds=novas;usuariosMigrados=true;}
  }
}'''
server=must(server,old,new,"migracao de papeis")
server=must(server,
'''function lojasPermitidasUsuario(u:Usuario):Loja[]{
  const ativas=db.lojas.filter(l=>l.ativo);
  if(u.cargo==="admin"&&u.acessoTodasLojas===true)return ativas;
  const ids=new Set((u.lojaIds||[]).map(Number));
  return ativas.filter(l=>ids.has(l.id));
}''',
'''function lojasPermitidasUsuario(u:Usuario):Loja[]{
  const ativas=db.lojas.filter(l=>l.ativo);
  if(u.cargo==="admin")return ativas;
  const unica=Number((u.lojaIds||[])[0]);
  return ativas.filter(l=>l.id===unica).slice(0,1);
}''',"lojas permitidas")
server=must(server,
'''function normalizarLojaIdsUsuario(_cargo:Cargo,raw:any):number[]{
  const validas=new Set(lojasAtivasIds());
  const entrada=Array.isArray(raw)?raw:[raw];
  return [...new Set(entrada.map(Number).filter((id:number)=>Number.isInteger(id)&&validas.has(id)))];
}''',
'''function normalizarLojaIdsUsuario(cargo:Cargo,raw:any):number[]{
  if(cargo==="admin")return lojasAtivasIds();
  const validas=new Set(lojasAtivasIds());
  const entrada=Array.isArray(raw)?raw:[raw];
  const primeira=entrada.map(Number).find((id:number)=>Number.isInteger(id)&&validas.has(id));
  return primeira?[primeira]:[];
}''',"normalizacao unica")
server=server.replace('const acessoTodasLojas=cargoFinal==="admin"&&Boolean(req.body.acessoTodasLojas);','const acessoTodasLojas=cargoFinal==="admin";',1)
server=server.replace('const acessoTodasLojas=editandoProprioAdmin?Boolean(u.acessoTodasLojas):(cargoFinal==="admin"&&Boolean(req.body.acessoTodasLojas));','const acessoTodasLojas=cargoFinal==="admin";',1)
write("src/server.ts",server)

js=read("public/app.js")
js=must(js,'const atual="10.11.29"','const atual="10.11.30"',"versao JS")
js += r'''

// 10.11.30 - papéis simples: administrador troca de loja; vendedor fica em uma única loja.
function aplicarPapelSimples101130(){
 const admin=me?.cargo==='admin',sel=document.querySelector('#storeSelect');
 if(sel){sel.disabled=!admin;sel.title=admin?'Escolha a loja':'Este vendedor está vinculado a esta loja';}
 document.documentElement.classList.toggle('seller-fixed-store-101130',!admin);
}
const loadLojasBase101130=loadLojas;
loadLojas=async function(){const r=await loadLojasBase101130();aplicarPapelSimples101130();return r};
document.addEventListener('DOMContentLoaded',()=>setTimeout(aplicarPapelSimples101130,100));

// Inicialização econômica para máquinas antigas: Caixa primeiro; painéis secundários no tempo ocioso.
const bootBase101130=boot;
let bootUnico101130=null;
boot=async function(){
 if(bootUnico101130)return bootUnico101130;
 document.documentElement.classList.add('booting-lite-101130');
 bootUnico101130=Promise.resolve(bootBase101130()).finally(()=>{document.documentElement.classList.remove('booting-lite-101130');bootUnico101130=null;aplicarPapelSimples101130()});
 return bootUnico101130;
};
window.loadAll=boot;
'''
write("public/app.js",js)

css=read("public/style.css")+r'''

/* 10.11.30 - layout leve para PCs antigos e telas compactas */
.booting-lite-101130{cursor:progress}.booting-lite-101130 .section:not(.active){display:none!important}
.performance-lite-101025 *, .performance-lite-101025 *::before, .performance-lite-101025 *::after{animation:none!important;transition:none!important;filter:none!important}
.performance-lite-101025 body,.performance-lite-101025 header,.performance-lite-101025 aside,.performance-lite-101025 .modal{background-image:none!important}
.performance-lite-101025 img{content-visibility:auto}.performance-lite-101025 .smart-products-grid{contain:layout paint}
.seller-fixed-store-101130 #storeSelect{opacity:.86;cursor:not-allowed}
@media(max-width:1366px){main{padding:0 14px 24px!important;margin:14px auto!important}.card{padding:13px!important}.page-head{gap:8px;margin-bottom:10px!important}.pdv1092-layout{grid-template-columns:minmax(350px,42%) minmax(460px,58%)!important;gap:8px!important}.smart-products-grid{grid-template-columns:repeat(3,minmax(100px,1fr))!important}.product{padding:9px!important}aside{width:210px!important}.app-shell{grid-template-columns:210px minmax(0,1fr)!important}}
@media(max-width:1100px){.pdv1092-layout{grid-template-columns:1fr!important}.smart-products-grid{grid-template-columns:repeat(3,minmax(100px,1fr))!important}}
'''
write("public/style.css",css)
print("10.11.30: papeis simplificados, vendedor em uma loja e modo leve reforcado.")
