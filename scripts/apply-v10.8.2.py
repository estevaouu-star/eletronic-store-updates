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
pkg['version']='10.8.2'
write('package.json',json.dumps(pkg,indent=2,ensure_ascii=False))

# -----------------------------------------------------------------------------
# Login visual + usuário no topo + gestão de usuários em Configurações
# -----------------------------------------------------------------------------
html=read('public/index.html')
html=html.replace('id="versionInfo" class="version-info">v10.8.1','id="versionInfo" class="version-info">v10.8.2',1)

login_markup='''<div id="loginScreen" class="login-screen">
  <div class="login-card eletromix-login-card">
    <div class="login-brand-wrap"><img src="eletromix-app-icon.png" alt="Eletromix" class="login-logo"></div>
    <h1>Eletromix</h1>
    <p>Entre com seu usuário para acessar o sistema.</p>
    <form id="loginForm" onsubmit="login(event)">
      <label for="login">Usuário</label>
      <input id="login" name="login" autocomplete="username" required autofocus placeholder="Digite seu usuário">
      <label for="senha">Senha</label>
      <input id="senha" name="senha" type="password" autocomplete="current-password" required placeholder="Digite sua senha">
      <button class="primary login-submit" type="submit">Entrar</button>
      <div id="loginError" role="alert"></div>
    </form>
  </div>
</div>
'''
html=must(html,'<div id="app">',login_markup+'<div id="app" class="hidden">','tela de login')

store_label='<label class="operator-label"><span class="header-label-icon" data-icon="store"></span><span>Loja</span><select id="storeSelect"></select></label>'
user_controls='''<div class="operator-user" id="operatorUser"><span class="operator-user-dot"></span><span id="userName">Usuário</span><button id="logoutBtn" type="button" title="Sair do sistema">Sair</button></div>
    '''
html=must(html,store_label,user_controls+store_label,'usuario no cabecalho')

config_start=html.find('<section id="config" class="section">')
if config_start<0: raise RuntimeError('Secao Configuracoes nao encontrada')
config_end=html.find('</section>',config_start)
if config_end<0: raise RuntimeError('Fim da secao Configuracoes nao encontrado')
users_block='''
  <div class="settings-block admin-only access-settings-block">
    <div class="settings-block-head">
      <div><span class="settings-eyebrow">ACESSO</span><h3>Usuários e login</h3><p>Crie acessos individuais para saber quem está usando o caixa.</p></div>
      <button id="novoUsuarioBtn" class="primary small" type="button">Novo usuário</button>
    </div>
    <div class="table-scroll"><table><thead><tr><th>Nome</th><th>Login</th><th>Cargo</th><th>Status</th><th></th></tr></thead><tbody id="tableUsuarios"></tbody></table></div>
  </div>
'''
html=html[:config_end]+users_block+html[config_end:]
write('public/index.html',html)

css=read('public/style.css')
css += r'''
/* 10.8.2 - login e identificação do operador */
.login-screen{position:fixed;inset:0;z-index:9999;display:grid;place-items:center;padding:24px;background:radial-gradient(circle at 50% 0,#461111 0,#171010 38%,#08090b 100%)}
.eletromix-login-card{width:min(430px,94vw);padding:34px;border:1px solid rgba(255,45,45,.24)!important;border-radius:24px!important;box-shadow:0 28px 90px #000b!important;text-align:left!important}
.login-brand-wrap{display:flex;justify-content:center;margin-bottom:10px}.login-logo{width:82px;height:82px;object-fit:contain;border-radius:20px;background:#080808}
.eletromix-login-card h1{text-align:center;font-size:28px;margin:8px 0 6px}.eletromix-login-card>p{text-align:center;margin:0 0 24px!important}.eletromix-login-card input{height:48px}.login-submit{width:100%;height:48px;margin-top:5px;font-size:15px}.operator-user{display:flex;align-items:center;gap:8px;padding:5px 6px 5px 10px;border:1px solid rgba(255,255,255,.1);border-radius:12px;background:rgba(255,255,255,.04)}.operator-user-dot{width:7px;height:7px;border-radius:999px;background:#38c172}.operator-user #userName{font-weight:700;color:inherit!important;white-space:nowrap}.operator-user #logoutBtn{padding:7px 9px!important;border-radius:8px!important;background:rgba(255,255,255,.08)!important}.access-settings-block{margin-top:18px}.access-settings-block .settings-block-head{align-items:center}
@media(max-width:1000px){.operator-user #userName{display:none}.operator-user{padding-left:6px}}
'''
write('public/style.css',css)

# -----------------------------------------------------------------------------
# Frontend: login real, sessão persistida, logout, papel único por clique
# -----------------------------------------------------------------------------
js=read('public/app.js')
js=must(js,'let token="acesso-local",me={id:1,nome:"Acesso local",login:"local",cargo:"admin"},','let token=localStorage.getItem("es_token")||"",me=null,','estado inicial de login')

old_ui='''function showLogin(){showApp()}
function showApp(){const app=$("#app");if(app)app.classList.remove("hidden");document.querySelectorAll(".admin-only").forEach(x=>x.style.display="block")}'''
new_ui='''function showLogin(){
  const loginScreen=$("#loginScreen"),app=$("#app");
  if(loginScreen)loginScreen.classList.remove("hidden");
  if(app)app.classList.add("hidden");
  setTimeout(()=>$("#login")?.focus(),30);
}
function showApp(){
  const loginScreen=$("#loginScreen"),app=$("#app");
  if(loginScreen)loginScreen.classList.add("hidden");
  if(app)app.classList.remove("hidden");
  const isAdmin=me?.cargo==="admin";
  document.querySelectorAll(".admin-only").forEach(x=>x.style.display=isAdmin?"":"none");
  if($("#userName"))$("#userName").textContent=me?.nome||me?.login||"Usuário";
}'''
js=must(js,old_ui,new_ui,'showLogin/showApp')

old_start='''async function start(){
  try{showApp()}catch{}
  try{
    const r=await api("/api/me");
    if(r.ok){me=await r.json();caixaAtual=me.caixa;}
  }catch(e){console.error("Falha em /api/me",e)}
  try{await boot()}catch(e){console.error("Falha no carregamento inicial",e)}
}
async function login(e){e.preventDefault();const r=await fetch("/api/login",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({login:$("#login").value,senha:$("#senha").value})});const d=await r.json();if(!r.ok){$("#loginError").textContent=d.erro;return}token=d.token;me=d.usuario;localStorage.setItem("es_token",token);$("#loginError").textContent="";showApp();await boot()}
function logout(){location.reload()}'''
new_start='''async function start(){
  if(!token){showLogin();return;}
  try{
    const r=await api("/api/me");
    if(!r.ok)throw new Error("Sessão inválida");
    me=await r.json();caixaAtual=me.caixa;showApp();await boot();
  }catch(e){console.error("Sessão não pôde ser restaurada",e);logout(false)}
}
async function login(e){
  e?.preventDefault?.();
  const btn=$("#loginForm button[type=submit]");if(btn){btn.disabled=true;btn.textContent="Entrando..."}
  try{
    const r=await fetch("/api/login",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({login:$("#login").value,senha:$("#senha").value})});
    const d=await r.json();
    if(!r.ok){if($("#loginError"))$("#loginError").textContent=d.erro||"Não foi possível entrar.";return}
    token=d.token;me=d.usuario;localStorage.setItem("es_token",token);if($("#loginError"))$("#loginError").textContent="";showApp();await boot();
  }finally{if(btn){btn.disabled=false;btn.textContent="Entrar"}}
}
function logout(callApi=true){
  const oldToken=token;token="";me=null;caixaAtual=null;localStorage.removeItem("es_token");
  if(callApi&&oldToken)fetch("/api/logout",{method:"POST",headers:{Authorization:"Bearer "+oldToken}}).catch(()=>{});
  showLogin();
}'''
js=must(js,old_start,new_start,'start/login/logout')

# Botão do comprovante recebe ID para ser bloqueado enquanto imprime.
js=js.replace('<button class="primary" onclick="printReceipt()">Imprimir</button>','<button class="primary" id="receiptPrintBtn" onclick="printReceipt()">Imprimir</button>',1)

# Corrige impressão duplicada também na interface: um clique = uma requisição enquanto a anterior não termina.
print_start=js.find('async function directPrintReceipt(){')
print_end=js.find('\nasync function testPrinter(){',print_start)
if print_start<0 or print_end<0: raise RuntimeError('directPrintReceipt nao encontrado')
new_print=r'''let receiptPrintInFlight=false;
async function directPrintReceipt(){
  if(receiptPrintInFlight){toast("A impressão já foi enviada. Aguarde um instante.");return}
  if(!window.desktopPrinter)return toast("Módulo de impressão do Windows não está disponível.");
  const btn=$("#receiptPrintBtn");
  receiptPrintInFlight=true;if(btn){btn.disabled=true;btn.textContent="Imprimindo..."}
  try{
    if(!printerSettings.deviceName){await refreshPrinters();if(!printerSettings.deviceName)return toast("Selecione uma impressora em Configurações.")}
    const payload=receiptPrintPayload();if(!payload)return toast("Comprovante não encontrado.");
    const status=$("#printerStatus");if(status)status.textContent="Enviando para a impressora...";
    const r=await window.desktopPrinter.print(payload);
    if(r?.success){
      if(r.deviceName && r.deviceName!==printerSettings.deviceName){printerSettings.deviceName=r.deviceName;savePrinterSettings();}
      if(status)status.textContent=`Impresso em ${r.deviceName||printerSettings.deviceName}${r.mode==="escpos"?" · térmico direto · corte automático":""}.`;
      toast("Comprovante enviado uma vez para a impressora.");
    }else{
      const motivo=r?.failureReason||"erro desconhecido";
      if(status)status.textContent=`Falha: ${motivo}`;
      toast(r?.busy?"A impressora ainda está processando o comprovante anterior.":`Falha ao imprimir: ${motivo}`);
    }
  }catch(err){
    console.error("Falha na impressão",err);
    const motivo=String(err?.message||err||"erro desconhecido");
    if($("#printerStatus"))$("#printerStatus").textContent=`Falha: ${motivo}`;
    toast(`Falha ao imprimir: ${motivo}`);
  }finally{
    receiptPrintInFlight=false;if(btn){btn.disabled=false;btn.textContent="Imprimir"}
  }
}'''
js=js[:print_start]+new_print+js[print_end:]

# Carrega usuários ao abrir Configurações e liga os controles de sessão.
js += r'''
document.addEventListener("DOMContentLoaded",()=>{
  $("#logoutBtn")?.addEventListener("click",()=>logout(true));
  $("#novoUsuarioBtn")?.addEventListener("click",newUsuario);
});
document.addEventListener("click",e=>{
  if(e.target?.closest?.('.nav[data-s="config"]') && me?.cargo==="admin")setTimeout(()=>loadUsuarios().catch(()=>{}),80);
});
'''
js=js.replace('const atual="10.8.1"','const atual="10.8.2"',1)
write('public/app.js',js)

# -----------------------------------------------------------------------------
# Backend: autenticação de verdade em todas as rotas protegidas.
# -----------------------------------------------------------------------------
server=read('src/server.ts')
old_auth='''function auth(req:express.Request,res:express.Response,next:express.NextFunction) {
  const u=db.usuarios.find(x=>x.cargo==="admin"&&x.ativo) || db.usuarios.find(x=>x.ativo);
  if(!u)return res.status(500).json({erro:"Nenhum usuário ativo configurado."});
  (req as any).usuario=u;
  next();
}'''
new_auth='''function auth(req:express.Request,res:express.Response,next:express.NextFunction) {
  const header=String(req.headers.authorization||"");
  const token=header.toLowerCase().startsWith("bearer ")?header.slice(7).trim():"";
  const sessao=token?sessoes.get(token):undefined;
  if(!sessao)return res.status(401).json({erro:"Faça login para continuar."});
  if(sessao.expira<=Date.now()){
    sessoes.delete(token);
    return res.status(401).json({erro:"Sua sessão expirou. Entre novamente."});
  }
  const u=db.usuarios.find(x=>x.id===sessao.usuarioId&&x.ativo);
  if(!u){sessoes.delete(token);return res.status(401).json({erro:"Usuário inválido ou desativado."});}
  (req as any).token=token;
  (req as any).usuario=u;
  next();
}'''
server=must(server,old_auth,new_auth,'middleware de autenticacao')
write('src/server.ts',server)

# -----------------------------------------------------------------------------
# Electron: corrige ACK do worker (causa real das reimpressões) + trava concorrência.
# -----------------------------------------------------------------------------
main=read('electron/main.cjs')
main=must(main,'const parts=line.slice(14).split("|");','const parts=line.slice("__ELETROMIX__".length).split("|");','parser de resposta do spooler')

handler='ipcMain.handle("printer:print", async (_event, payload = {}) => {'
main=must(main,handler,'let thermalPrintBusy=false;\n'+handler,'trava global de impressao')
needle='''  const printWindow=getThermalRenderWindow();
  let rawFailure="";
  try{'''
replacement='''  if(thermalPrintBusy)return {success:false,failureReason:"Uma impressão já está em andamento.",deviceName,busy:true};
  thermalPrintBusy=true;
  const printWindow=getThermalRenderWindow();
  let rawFailure="";
  try{'''
main=must(main,needle,replacement,'inicio da trava de impressao')
old_final='''  }finally{
    // Mantém a janela invisível pronta para a próxima impressão.
  }
});'''
new_final='''  }finally{
    thermalPrintBusy=false;
    // Mantém a janela invisível pronta para a próxima impressão.
  }
});'''
main=must(main,old_final,new_final,'fim da trava de impressao')
write('electron/main.cjs',main)

print('Patch 10.8.2 aplicado: impressão duplicada corrigida, login real ativado e usuários acessíveis nas Configurações.')
