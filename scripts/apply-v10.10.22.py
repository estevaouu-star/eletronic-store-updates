from pathlib import Path
import json

root = Path("app")


def read(path: str) -> str:
    return (root / path).read_text(encoding="utf-8")


def write(path: str, content: str) -> None:
    (root / path).write_text(content, encoding="utf-8")


pkg = json.loads(read("package.json"))
pkg["version"] = "10.10.22"
write("package.json", json.dumps(pkg, indent=2, ensure_ascii=False))

html = read("public/index.html").replace(
    'id="versionInfo" class="version-info">v10.10.21',
    'id="versionInfo" class="version-info">v10.10.22',
    1,
).replace(
    'id="logoutBtn" type="button" title="Sair do sistema"',
    'id="exitAppBtn" type="button" title="Fechar o aplicativo"',
    1,
)
write("public/index.html", html)

server = read("src/server.ts")
old_auth = '''function auth(req:express.Request,res:express.Response,next:express.NextFunction) {
  const header=String(req.headers.authorization||"");
  const token=header.toLowerCase().startsWith("bearer ")?header.slice(7).trim():"";
  const sessao=token?sessoes.get(token):undefined;'''
new_auth = '''function tokenCookie101022(req:express.Request):string {
  const raw=String(req.headers.cookie||"");
  const item=raw.split(";").map(x=>x.trim()).find(x=>x.startsWith("eletromix_session="));
  if(!item)return "";
  try{return decodeURIComponent(item.slice("eletromix_session=".length)).trim()}catch{return ""}
}
function auth(req:express.Request,res:express.Response,next:express.NextFunction) {
  const header=String(req.headers.authorization||"");
  const bearer=header.toLowerCase().startsWith("bearer ")?header.slice(7).trim():"";
  const token=bearer||tokenCookie101022(req);
  const sessao=token?sessoes.get(token):undefined;'''
if old_auth not in server:
    raise SystemExit("Middleware de autenticação não encontrado.")
server = server.replace(old_auth, new_auth, 1)

old_login_response = '''  salvarSessaoPersistente108(token,u.id);
  res.json({token,usuario:{id:u.id,nome:u.nome,login:u.login,cargo:u.cargo,lojaIds}});'''
new_login_response = '''  salvarSessaoPersistente108(token,u.id);
  // Cookie persistente do próprio Electron/Chromium. Não depende de localStorage,
  // senha lembrada, versão instalada nem ordem dos scripts da interface.
  res.cookie("eletromix_session",token,{httpOnly:true,sameSite:"strict",maxAge:3650*24*60*60*1000,path:"/"});
  res.json({token,usuario:{id:u.id,nome:u.nome,login:u.login,cargo:u.cargo,lojaIds}});'''
if old_login_response not in server:
    raise SystemExit("Resposta de login não encontrada.")
server = server.replace(old_login_response, new_login_response, 1)

old_logout = '''app.post("/api/logout",auth,(req,res)=>{
  sessoes.delete((req as any).token);
  res.json({ok:true});
});'''
new_logout = '''app.post("/api/logout",auth,(req,res)=>{
  sessoes.delete((req as any).token);
  res.clearCookie("eletromix_session",{path:"/"});
  res.json({ok:true});
});'''
if old_logout not in server:
    raise SystemExit("Logout não encontrado.")
server = server.replace(old_logout, new_logout, 1)

old_me = '''app.get("/api/me",auth,(req,res)=>{
  const u=(req as any).usuario as Usuario;
  const lojaIds=idsLojasPermitidas(u);
  res.json({id:u.id,nome:u.nome,login:u.login,cargo:u.cargo,lojaIds,caixa:caixaAbertoDoUsuario(u.id,lojaIdReq(req))||null});
});'''
new_me = '''app.get("/api/me",auth,(req,res)=>{
  const u=(req as any).usuario as Usuario;
  const lojaIds=idsLojasPermitidas(u);
  // Migra automaticamente qualquer token antigo válido para o cookie persistente.
  res.cookie("eletromix_session",String((req as any).token||""),{httpOnly:true,sameSite:"strict",maxAge:3650*24*60*60*1000,path:"/"});
  res.json({id:u.id,nome:u.nome,login:u.login,cargo:u.cargo,lojaIds,caixa:caixaAbertoDoUsuario(u.id,lojaIdReq(req))||null});
});'''
if old_me not in server:
    raise SystemExit("Endpoint /api/me não encontrado.")
server = server.replace(old_me, new_me, 1)
write("src/server.ts", server)

js = read("public/app.js").replace(
    'const atual="10.10.21"', 'const atual="10.10.22"', 1
)
old_start = '''async function start(){
  if(!token){showLogin();return;}
  try{
    const r=await api("/api/me");
    if(!r.ok)throw new Error("Sessão inválida");
    me=await r.json();caixaAtual=me.caixa;ajustarLojaAoUsuario();showApp();await boot();
  }catch(e){console.error("Sessão não pôde ser restaurada",e);logout(false)}
}'''
new_start = '''async function start(){
  try{
    // Mesmo sem token no localStorage, /api/me reconhece o cookie persistente
    // salvo pelo processo do aplicativo.
    const r=await api("/api/me");
    if(!r.ok){showLogin();return false}
    me=await r.json();caixaAtual=me.caixa;ajustarLojaAoUsuario();showApp();await boot();return true;
  }catch(e){console.error("Sessão não pôde ser restaurada",e);showLogin();return false}
}'''
if old_start not in js:
    raise SystemExit("Inicialização base não encontrada.")
js = js.replace(old_start, new_start, 1)

old_exit_listener = '$("#logoutBtn")?.addEventListener("click",()=>logout(true));'
new_exit_listener = '''$("#exitAppBtn")?.addEventListener("click",async()=>{
    try{gravarSessao10109();await saveAuth101010()}catch{}
    if(window.eletromixApp101021?.quit)await window.eletromixApp101021.quit();else window.close();
  });'''
if old_exit_listener not in js:
    raise SystemExit("Listener de saída não encontrado.")
js = js.replace(old_exit_listener, new_exit_listener, 1)
write("public/app.js", js)

print("10.10.22: autenticação persistente por cookie do aplicativo e Sair sem logout legado.")
