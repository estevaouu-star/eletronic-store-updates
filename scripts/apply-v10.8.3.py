from pathlib import Path
import json

root=Path('app')
def read(p): return (root/p).read_text(encoding='utf-8')
def write(p,s): (root/p).write_text(s,encoding='utf-8')
def must(s,a,b,label):
    if a not in s: raise RuntimeError(f'Trecho nao encontrado: {label}')
    return s.replace(a,b,1)

# Versão
pkg=json.loads(read('package.json'))
pkg['version']='10.8.3'
write('package.json',json.dumps(pkg,indent=2,ensure_ascii=False))

# HTML: formulário passa a usar listener normal (Enter funciona sem depender de inline handler)
html=read('public/index.html')
html=html.replace('id="versionInfo" class="version-info">v10.8.2','id="versionInfo" class="version-info">v10.8.3',1)
html=must(html,'<form id="loginForm" onsubmit="login(event)">','<form id="loginForm">','formulario de login')
write('public/index.html',html)

js=read('public/app.js')

# Corrige a corrida que derrubava o login: chamadas antigas sem token não podem apagar um token novo.
old_api='async function api(url,opt={}){opt.headers={...(opt.headers||{}),...(token?{Authorization:"Bearer "+token}:{}),"X-Store-Id":String(lojaId)};const r=await fetch(url,opt);if(r.status===401){logout(false);throw new Error("Sessão expirada.")}return r}'
new_api='''async function api(url,opt={}){
  const requestToken=token;
  opt.headers={...(opt.headers||{}),...(requestToken?{Authorization:"Bearer "+requestToken}:{}),"X-Store-Id":String(lojaId)};
  const r=await fetch(url,opt);
  // Só encerra a sessão se ESTE pedido saiu com o mesmo token que ainda está ativo.
  // Assim uma requisição iniciada antes do login não consegue apagar a sessão recém-criada.
  if(r.status===401 && requestToken && requestToken===token){logout(false);throw new Error("Sessão expirada.")}
  return r;
}'''
js=must(js,old_api,new_api,'api 401')

# Não rouba mais o foco do campo de senha.
old_show='''function showLogin(){
  const loginScreen=$("#loginScreen"),app=$("#app");
  if(loginScreen)loginScreen.classList.remove("hidden");
  if(app)app.classList.add("hidden");
  setTimeout(()=>$("#login")?.focus(),30);
}'''
new_show='''function showLogin(){
  const loginScreen=$("#loginScreen"),app=$("#app");
  if(loginScreen)loginScreen.classList.remove("hidden");
  if(app)app.classList.add("hidden");
  // Não força foco aqui: o usuário pode estar digitando a senha.
}'''
js=must(js,old_show,new_show,'showLogin sem roubar foco')

# Login robusto: Enter, clique, erro visível e verificação da sessão antes de abrir o sistema.
start=js.find('async function login(e){')
end=js.find('\nfunction logout(',start)
if start<0 or end<0: raise RuntimeError('funcao login nao encontrada')
new_login=r'''let loginInFlight=false;
async function login(e){
  e?.preventDefault?.();
  if(loginInFlight)return;
  const loginEl=$("#login"),senhaEl=$("#senha"),errEl=$("#loginError"),btn=$("#loginForm button[type=submit]");
  const loginValue=String(loginEl?.value||"").trim(),senhaValue=String(senhaEl?.value||"");
  if(!loginValue||!senhaValue){if(errEl)errEl.textContent="Informe usuário e senha.";return}
  loginInFlight=true;if(btn){btn.disabled=true;btn.textContent="Entrando..."}if(errEl)errEl.textContent="";
  try{
    const r=await fetch("/api/login",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({login:loginValue,senha:senhaValue})});
    let d={};try{d=await r.json()}catch{}
    if(!r.ok){if(errEl)errEl.textContent=d.erro||"Usuário ou senha incorretos.";senhaEl?.focus();return}
    const newToken=String(d.token||"");
    if(!newToken)throw new Error("O servidor não retornou uma sessão válida.");
    token=newToken;me=d.usuario||null;localStorage.setItem("es_token",token);
    const meResp=await api("/api/me");
    if(!meResp.ok)throw new Error("Não foi possível confirmar a sessão.");
    me=await meResp.json();caixaAtual=me.caixa||null;
    showApp();
    await boot();
    loadCloudStatus().catch(()=>{});
  }catch(err){
    console.error("Falha no login",err);
    if(errEl)errEl.textContent=String(err?.message||"Não foi possível entrar no Eletromix.");
    if(token){token="";me=null;localStorage.removeItem("es_token")}
    showLogin();
  }finally{
    loginInFlight=false;if(btn){btn.disabled=false;btn.textContent="Entrar"}
  }
}'''
js=js[:start]+new_login+js[end:]

# A nuvem não chama API protegida enquanto a tela de login está aberta.
old_cloud='''async function loadCloudStatus(){
  try{const r=await api("/api/cloud/status"),d=await r.json(),b=$("#cloudBadge"),t=$("#cloudText");if(!b||!t)return;t.textContent=d.state==="online"?"Online":d.state==="syncing"?"Sincronizando":d.state==="offline"?"Offline":"Local";b.className=`cloud-badge ${d.state||"local"}`;b.title=d.message||"Status da nuvem"}catch{}
}
async function syncCloudNow(){const b=$("#cloudBadge");if(b)b.className="cloud-badge syncing";try{const r=await api("/api/cloud/sync",{method:"POST"}),d=await r.json();toast(d.ok?"Dados sincronizados.":d.message||"Falha na sincronização");await loadCloudStatus();if(d.ok)await boot()}catch{toast("Não foi possível sincronizar agora.")}}
setInterval(loadCloudStatus,5000);
document.addEventListener("DOMContentLoaded",()=>{loadCloudStatus();$("#cloudBadge")?.addEventListener("click",syncCloudNow)});'''
new_cloud='''async function loadCloudStatus(){
  if(!token||!me)return;
  try{const r=await api("/api/cloud/status"),d=await r.json(),b=$("#cloudBadge"),t=$("#cloudText");if(!b||!t)return;t.textContent=d.state==="online"?"Online":d.state==="syncing"?"Sincronizando":d.state==="offline"?"Offline":"Local";b.className=`cloud-badge ${d.state||"local"}`;b.title=d.message||"Status da nuvem"}catch{}
}
async function syncCloudNow(){if(!token||!me)return;const b=$("#cloudBadge");if(b)b.className="cloud-badge syncing";try{const r=await api("/api/cloud/sync",{method:"POST"}),d=await r.json();toast(d.ok?"Dados sincronizados.":d.message||"Falha na sincronização");await loadCloudStatus();if(d.ok)await boot()}catch{toast("Não foi possível sincronizar agora.")}}
setInterval(()=>{if(token&&me)loadCloudStatus()},5000);
document.addEventListener("DOMContentLoaded",()=>{$("#cloudBadge")?.addEventListener("click",syncCloudNow)});'''
js=must(js,old_cloud,new_cloud,'status da nuvem antes do login')

# Garante submit por Enter/clique através de event listener único.
listener='''document.addEventListener("DOMContentLoaded",()=>{
  $("#loginForm")?.addEventListener("submit",login);
  $("#logoutBtn")?.addEventListener("click",()=>logout(true));
  $("#novoUsuarioBtn")?.addEventListener("click",newUsuario);
});'''
old_listener='''document.addEventListener("DOMContentLoaded",()=>{
  $("#logoutBtn")?.addEventListener("click",()=>logout(true));
  $("#novoUsuarioBtn")?.addEventListener("click",newUsuario);
});'''
js=must(js,old_listener,listener,'listener do formulario')
js=js.replace('const atual="10.8.2"','const atual="10.8.3"',1)
write('public/app.js',js)

# Backend: migração de segurança para instalações antigas que, por qualquer motivo, estejam sem usuário.
server=read('src/server.ts')
anchor='''const sessoes = new Map<string,{usuarioId:number;expira:number}>();'''
insert='''if(!Array.isArray(db.usuarios))db.usuarios=[];
if(db.usuarios.length===0){
  db.usuarios.push({id:db.seq.usuario++,nome:"Administrador",login:"admin",senhaHash:senhaHash("admin123"),cargo:"admin",ativo:true,criadoEm:now()});
  salvar();
}

const sessoes = new Map<string,{usuarioId:number;expira:number}>();'''
server=must(server,anchor,insert,'migracao usuario admin')
write('src/server.ts',server)

print('Patch 10.8.3 aplicado: login sem roubo de foco, sem corrida de 401 e Enter funcionando.')
