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
pkg["version"] = "10.10.26"
write("package.json", json.dumps(pkg, indent=2, ensure_ascii=False))

html = read("public/index.html")
html = replace_once(
    html,
    'id="versionInfo" class="version-info">v10.10.25',
    'id="versionInfo" class="version-info">v10.10.26',
    "versão no cabeçalho",
)
html = replace_once(
    html,
    '    <button id="cashBadge" class="cash-status-button warn" type="button" title="Clique para gerenciar o caixa"><span class="cash-status-dot"></span><span class="cash-status-text">Caixa fechado</span><span class="cash-status-arrow" data-icon="chevron-down"></span></button>\n',
    "",
    "indicador de caixa no cabeçalho",
)
html = replace_once(
    html,
    '<div class="full printer-actions"><button type="button" class="secondary" id="refreshPrintersBtn">Atualizar impressoras</button><button type="button" class="secondary" id="testPrinterBtn">Imprimir teste</button></div>',
    '<div class="full printer-actions"><button type="button" class="secondary" id="refreshPrintersBtn">Atualizar impressoras</button><button type="button" class="secondary" id="testPrinterBtn">Imprimir teste</button></div><div class="full printer-save-row"><button type="button" class="primary" id="savePrinterBtn">Salvar impressora para esta loja</button></div>',
    "botão para salvar impressora",
)
html = replace_once(
    html,
    '<div><span class="settings-eyebrow">ACESSO</span><h3>Usuários e login</h3><p>Somente administradores podem criar ou alterar logins, inclusive o próprio. Defina também quais lojas cada usuário pode acessar.</p></div>',
    '<div><span class="settings-eyebrow">ACESSO</span><h3>Usuários e login</h3><p>Cada administrador altera somente a própria conta. Ao criar um administrador, escolha exatamente quais lojas ele poderá acessar.</p></div>',
    "explicação de acesso",
)
html = html.replace('>Editar meu acesso</button>', '>Editar minha conta</button>', 1)
write("public/index.html", html)

server = read("src/server.ts")
server = replace_once(
    server,
    '  cargo:Cargo; ativo:boolean; criadoEm:string; lojaIds?:number[];\n',
    '  cargo:Cargo; ativo:boolean; criadoEm:string; lojaIds?:number[]; acessoTodasLojas?:boolean;\n',
    "tipo Usuario",
)
server = replace_once(
    server,
    'usuarios: [{id:1,nome:"Administrador",login:"admin",senhaHash:senhaHash("admin123"),cargo:"admin",ativo:true,criadoEm:now()}],',
    'usuarios: [{id:1,nome:"Administrador",login:"admin",senhaHash:senhaHash("admin123"),cargo:"admin",ativo:true,criadoEm:now(),acessoTodasLojas:true}],',
    "administrador inicial",
)
server = replace_once(
    server,
    'db.usuarios.push({id:db.seq.usuario++,nome:"Administrador",login:"admin",senhaHash:senhaHash("admin123"),cargo:"admin",ativo:true,criadoEm:now(),lojaIds:db.lojas.filter(l=>l.ativo).map(l=>l.id)});',
    'db.usuarios.push({id:db.seq.usuario++,nome:"Administrador",login:"admin",senhaHash:senhaHash("admin123"),cargo:"admin",ativo:true,criadoEm:now(),lojaIds:db.lojas.filter(l=>l.ativo).map(l=>l.id),acessoTodasLojas:true});',
    "administrador recuperado",
)
old_access = '''for(const u of db.usuarios){
  if(!Array.isArray(u.lojaIds)){
    u.lojaIds=lojasAtivasIds();
    usuariosMigrados=true;
  }
}
if(usuariosMigrados)salvar();

function lojasPermitidasUsuario(u:Usuario):Loja[]{
  const ativas=db.lojas.filter(l=>l.ativo);
  if(u.cargo==="admin")return ativas;
  const ids=new Set((u.lojaIds||[]).map(Number));
  return ativas.filter(l=>ids.has(l.id));
}
function idsLojasPermitidas(u:Usuario):number[]{return lojasPermitidasUsuario(u).map(l=>l.id)}
function normalizarLojaIdsUsuario(cargo:Cargo,raw:any):number[]{
  if(cargo==="admin")return lojasAtivasIds();
  const validas=new Set(lojasAtivasIds());
  const entrada=Array.isArray(raw)?raw:[raw];
  return [...new Set(entrada.map(Number).filter((id:number)=>Number.isInteger(id)&&validas.has(id)))];
}'''
new_access = '''for(const u of db.usuarios){
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
}
if(usuariosMigrados)salvar();

function lojasPermitidasUsuario(u:Usuario):Loja[]{
  const ativas=db.lojas.filter(l=>l.ativo);
  if(u.cargo==="admin"&&u.acessoTodasLojas===true)return ativas;
  const ids=new Set((u.lojaIds||[]).map(Number));
  return ativas.filter(l=>ids.has(l.id));
}
function idsLojasPermitidas(u:Usuario):number[]{return lojasPermitidasUsuario(u).map(l=>l.id)}
function normalizarLojaIdsUsuario(_cargo:Cargo,raw:any):number[]{
  const validas=new Set(lojasAtivasIds());
  const entrada=Array.isArray(raw)?raw:[raw];
  return [...new Set(entrada.map(Number).filter((id:number)=>Number.isInteger(id)&&validas.has(id)))];
}
function adminGlobal(req:express.Request,res:express.Response,next:express.NextFunction){
  const u=(req as any).usuario as Usuario|undefined;
  if(!u||u.cargo!=="admin"||u.acessoTodasLojas!==true)return res.status(403).json({erro:"Apenas um administrador com acesso a todas as lojas pode realizar esta ação."});
  next();
}
function escopoPermitidoAoOperador(operador:Usuario,ids:number[]):boolean{
  if(operador.cargo==="admin"&&operador.acessoTodasLojas===true)return true;
  const permitidas=new Set(idsLojasPermitidas(operador));
  return ids.every(id=>permitidas.has(Number(id)));
}'''
server = replace_once(server, old_access, new_access, "controle de lojas por administrador")
server = replace_once(
    server,
    'if(u.cargo!=="admin" && lojaIds.length===0)return res.status(403).json({erro:"Este usuário não possui nenhuma loja liberada. Peça ao administrador para liberar o acesso."});',
    'if(lojaIds.length===0)return res.status(403).json({erro:"Este usuário não possui nenhuma loja liberada. Peça ao administrador para liberar o acesso."});',
    "login sem lojas",
)
server = replace_once(
    server,
    '''app.get("/api/lojas",auth,(req,res)=>{
  const u=(req as any).usuario as Usuario;
  if(u.cargo==="admin")return res.json(db.lojas);
  const ids=new Set(idsLojasPermitidas(u));
  res.json(db.lojas.filter(l=>ids.has(l.id)));
});
app.post("/api/lojas",auth,admin,(req,res)=>{''',
    '''app.get("/api/lojas",auth,(req,res)=>{
  const u=(req as any).usuario as Usuario;
  const ids=new Set(idsLojasPermitidas(u));
  res.json(db.lojas.filter(l=>ids.has(l.id)));
});
app.post("/api/lojas",auth,adminGlobal,(req,res)=>{''',
    "listagem e criação de lojas",
)
server = replace_once(
    server,
    '''app.put("/api/lojas/:id",auth,admin,(req,res)=>{
  const l=db.lojas.find(x=>x.id===Number(req.params.id));
  if(!l)return res.status(404).json({erro:"Loja não encontrada."});''',
    '''app.put("/api/lojas/:id",auth,admin,(req,res)=>{
  const operador=(req as any).usuario as Usuario;
  const l=db.lojas.find(x=>x.id===Number(req.params.id));
  if(!l)return res.status(404).json({erro:"Loja não encontrada."});
  if(!idsLojasPermitidas(operador).includes(l.id))return res.status(403).json({erro:"Você não possui acesso a esta loja."});''',
    "edição de loja restrita",
)
server = server.replace('app.get("/api/email-config",auth,admin,(_req,res)=>{', 'app.get("/api/email-config",auth,adminGlobal,(_req,res)=>{', 1)
server = server.replace('app.put("/api/email-config",auth,admin,(req,res)=>{', 'app.put("/api/email-config",auth,adminGlobal,(req,res)=>{', 1)
old_report = '''function lojasDoRelatorio(lojaIdRaw:any){
  const valor=String(lojaIdRaw??"todas").trim();
  if(valor==="todas"||valor==="")return db.lojas.filter(l=>l.ativo);

  const id=Number(valor);
  const loja=db.lojas.find(l=>l.id===id&&l.ativo);
  if(!loja)throw new Error("Loja selecionada não foi encontrada.");
  return [loja];
}

function relatorioConsolidadoTexto(inicio:Date,fim:Date,periodoTitulo:string,lojaIdRaw:any){
  const lojasSelecionadas=lojasDoRelatorio(lojaIdRaw);'''
new_report = '''function lojasDoRelatorio(lojaIdRaw:any,usuario:Usuario){
  const permitidas=lojasPermitidasUsuario(usuario);
  const valor=String(lojaIdRaw??"todas").trim();
  if(valor==="todas"||valor==="")return permitidas;

  const id=Number(valor);
  const loja=permitidas.find(l=>l.id===id&&l.ativo);
  if(!loja)throw new Error("Você não possui acesso à loja selecionada.");
  return [loja];
}

function relatorioConsolidadoTexto(inicio:Date,fim:Date,periodoTitulo:string,lojaIdRaw:any,usuario:Usuario){
  const lojasSelecionadas=lojasDoRelatorio(lojaIdRaw,usuario);'''
server = replace_once(server, old_report, new_report, "escopo dos relatórios")
server = replace_once(
    server,
    '''    const tipo=String(req.body.tipo||"dia");
    const periodo=periodoRelatorio(tipo,req.body.mes);
    const lojasSelecionadas=lojasDoRelatorio(req.body.lojaId);''',
    '''    const usuario=(req as any).usuario as Usuario;
    const tipo=String(req.body.tipo||"dia");
    const periodo=periodoRelatorio(tipo,req.body.mes);
    const lojasSelecionadas=lojasDoRelatorio(req.body.lojaId,usuario);''',
    "relatório por e-mail permitido",
)
server = replace_once(
    server,
    'body:relatorioConsolidadoTexto(periodo.inicio,periodo.fim,periodo.titulo,req.body.lojaId)',
    'body:relatorioConsolidadoTexto(periodo.inicio,periodo.fim,periodo.titulo,req.body.lojaId,usuario)',
    "corpo do relatório permitido",
)
server = replace_once(
    server,
    '''    db.emailConfig.emailConsolidado=destino;
    salvar();''',
    '''    if(usuario.acessoTodasLojas===true){
      db.emailConfig.emailConsolidado=destino;
      salvar();
    }''',
    "configuração global de e-mail protegida",
)

old_users = '''// Usuários - somente administradores gerenciam acessos, inclusive o próprio login.
app.get("/api/usuarios",auth,admin,(_req,res)=>res.json(db.usuarios.map(u=>{
  const {senhaHash,...safe}=u;
  return {...safe,lojaIds:idsLojasPermitidas(u)};
})));
app.post("/api/usuarios",auth,admin,(req,res)=>{
  const {nome,login,senha,cargo="vendedor",lojaIds=[]}=req.body;
  if(!nome||!login||!senha)return res.status(400).json({erro:"Nome, login e senha são obrigatórios."});
  const loginLimpo=String(login).trim();
  if(db.usuarios.some(u=>u.login.toLowerCase()===loginLimpo.toLowerCase()))return res.status(409).json({erro:"Esse login já existe."});
  const cargoFinal:Cargo=cargo==="admin"?"admin":"vendedor";
  const lojasFinais=normalizarLojaIdsUsuario(cargoFinal,lojaIds);
  if(cargoFinal!=="admin"&&lojasFinais.length===0)return res.status(400).json({erro:"Selecione pelo menos uma loja para este usuário."});
  const u:Usuario={id:db.seq.usuario++,nome:String(nome).trim(),login:loginLimpo,senhaHash:senhaHash(String(senha)),cargo:cargoFinal,ativo:true,criadoEm:now(),lojaIds:lojasFinais};
  db.usuarios.push(u);salvar();const {senhaHash:_,...safe}=u;res.status(201).json({...safe,lojaIds:idsLojasPermitidas(u)});
});
app.put("/api/usuarios/:id",auth,admin,(req,res)=>{
  const operador=(req as any).usuario as Usuario;
  const u=db.usuarios.find(x=>x.id===Number(req.params.id));if(!u)return res.status(404).json({erro:"Usuário não encontrado."});
  const cargoFinal:Cargo=req.body.cargo!==undefined?(req.body.cargo==="admin"?"admin":"vendedor"):u.cargo;
  const ativoFinal=req.body.ativo!==undefined?Boolean(req.body.ativo):u.ativo;
  if(u.cargo==="admin" && (cargoFinal!=="admin" || !ativoFinal)){
    const outrosAdmins=db.usuarios.filter(x=>x.id!==u.id&&x.cargo==="admin"&&x.ativo);
    if(outrosAdmins.length===0)return res.status(400).json({erro:"Não é possível remover ou desativar o último administrador."});
  }
  if(req.body.login!==undefined){
    const novoLogin=String(req.body.login).trim();
    if(!novoLogin)return res.status(400).json({erro:"O login não pode ficar vazio."});
    if(db.usuarios.some(x=>x.id!==u.id&&x.login.toLowerCase()===novoLogin.toLowerCase()))return res.status(409).json({erro:"Esse login já existe."});
    u.login=novoLogin;
  }
  if(req.body.nome!==undefined)u.nome=String(req.body.nome).trim();
  u.cargo=cargoFinal;
  u.ativo=ativoFinal;
  const lojasFinais=normalizarLojaIdsUsuario(cargoFinal,req.body.lojaIds!==undefined?req.body.lojaIds:u.lojaIds||[]);
  if(cargoFinal!=="admin"&&lojasFinais.length===0)return res.status(400).json({erro:"Selecione pelo menos uma loja para este usuário."});
  u.lojaIds=lojasFinais;
  if(req.body.senha)u.senhaHash=senhaHash(String(req.body.senha));
  salvar();
  const {senhaHash:_,...safe}=u;
  res.json({...safe,lojaIds:idsLojasPermitidas(u),editadoPeloUsuarioId:operador.id});
});'''
new_users = '''// Usuários - administradores são isolados entre si e cada conta respeita seu escopo de lojas.
function usuarioSeguro101026(u:Usuario){
  const {senhaHash,...safe}=u;
  return {...safe,lojaIds:idsLojasPermitidas(u),acessoTodasLojas:u.cargo==="admin"&&u.acessoTodasLojas===true};
}
app.get("/api/usuarios",auth,admin,(req,res)=>{
  const operador=(req as any).usuario as Usuario;
  const permitidas=new Set(idsLojasPermitidas(operador));
  const visiveis=operador.acessoTodasLojas===true?db.usuarios:db.usuarios.filter(u=>u.id===operador.id||(u.cargo!=="admin"&&(u.lojaIds||[]).some(id=>permitidas.has(Number(id)))));
  res.json(visiveis.map(usuarioSeguro101026));
});
app.post("/api/usuarios",auth,admin,(req,res)=>{
  const operador=(req as any).usuario as Usuario;
  const {nome,login,senha,cargo="vendedor",lojaIds=[]}=req.body;
  if(!nome||!login||!senha)return res.status(400).json({erro:"Nome, login e senha são obrigatórios."});
  const loginLimpo=String(login).trim();
  if(db.usuarios.some(u=>u.login.toLowerCase()===loginLimpo.toLowerCase()))return res.status(409).json({erro:"Esse login já existe."});
  const cargoFinal:Cargo=cargo==="admin"?"admin":"vendedor";
  const acessoTodasLojas=cargoFinal==="admin"&&Boolean(req.body.acessoTodasLojas);
  if(acessoTodasLojas&&operador.acessoTodasLojas!==true)return res.status(403).json({erro:"Seu acesso não permite criar um administrador global."});
  const lojasFinais=acessoTodasLojas?lojasAtivasIds():normalizarLojaIdsUsuario(cargoFinal,lojaIds);
  if(lojasFinais.length===0)return res.status(400).json({erro:"Selecione pelo menos uma loja para este usuário."});
  if(!escopoPermitidoAoOperador(operador,lojasFinais))return res.status(403).json({erro:"Você só pode liberar lojas às quais possui acesso."});
  const u:Usuario={id:db.seq.usuario++,nome:String(nome).trim(),login:loginLimpo,senhaHash:senhaHash(String(senha)),cargo:cargoFinal,ativo:true,criadoEm:now(),lojaIds:lojasFinais,acessoTodasLojas};
  db.usuarios.push(u);salvar();res.status(201).json(usuarioSeguro101026(u));
});
app.put("/api/usuarios/:id",auth,admin,(req,res)=>{
  const operador=(req as any).usuario as Usuario;
  const u=db.usuarios.find(x=>x.id===Number(req.params.id));if(!u)return res.status(404).json({erro:"Usuário não encontrado."});
  if(u.cargo==="admin"&&u.id!==operador.id)return res.status(403).json({erro:"Um administrador não pode alterar a conta de outro administrador."});

  if(u.cargo!=="admin"&&!escopoPermitidoAoOperador(operador,(u.lojaIds||[]).map(Number)))return res.status(403).json({erro:"Este usuário pertence a uma loja fora do seu acesso."});
  const editandoProprioAdmin=u.cargo==="admin"&&u.id===operador.id;
  const cargoFinal:Cargo=editandoProprioAdmin?"admin":(req.body.cargo!==undefined?(req.body.cargo==="admin"?"admin":"vendedor"):u.cargo);
  const ativoFinal=editandoProprioAdmin?u.ativo:(req.body.ativo!==undefined?Boolean(req.body.ativo):u.ativo);
  const acessoTodasLojas=editandoProprioAdmin?Boolean(u.acessoTodasLojas):(cargoFinal==="admin"&&Boolean(req.body.acessoTodasLojas));
  if(acessoTodasLojas&&operador.acessoTodasLojas!==true)return res.status(403).json({erro:"Seu acesso não permite liberar todas as lojas."});

  if(req.body.login!==undefined){
    const novoLogin=String(req.body.login).trim();
    if(!novoLogin)return res.status(400).json({erro:"O login não pode ficar vazio."});
    if(db.usuarios.some(x=>x.id!==u.id&&x.login.toLowerCase()===novoLogin.toLowerCase()))return res.status(409).json({erro:"Esse login já existe."});
    u.login=novoLogin;
  }
  if(req.body.nome!==undefined)u.nome=String(req.body.nome).trim();
  let lojasFinais=editandoProprioAdmin?(u.lojaIds||[]):(acessoTodasLojas?lojasAtivasIds():normalizarLojaIdsUsuario(cargoFinal,req.body.lojaIds!==undefined?req.body.lojaIds:u.lojaIds||[]));
  if(lojasFinais.length===0)return res.status(400).json({erro:"Selecione pelo menos uma loja para este usuário."});
  if(!escopoPermitidoAoOperador(operador,lojasFinais))return res.status(403).json({erro:"Você só pode liberar lojas às quais possui acesso."});
  u.cargo=cargoFinal;u.ativo=ativoFinal;u.lojaIds=lojasFinais;u.acessoTodasLojas=acessoTodasLojas;
  if(req.body.senha)u.senhaHash=senhaHash(String(req.body.senha));
  salvar();res.json({...usuarioSeguro101026(u),editadoPeloUsuarioId:operador.id});
});'''
server = replace_once(server, old_users, new_users, "proteção de administradores")
server = server.replace('app.get("/api/backup",auth,admin,(_req,res)=>{', 'app.get("/api/backup",auth,adminGlobal,(_req,res)=>{', 1)
write("src/server.ts", server)

js = read("public/app.js")
js = replace_once(js, 'const atual="10.10.25"', 'const atual="10.10.26"', "versão do atualizador")
old_printer = '''function loadPrinterSettings(){
  try{printerSettings={...printerSettings,...JSON.parse(localStorage.getItem("es_printer")||"{}")}}catch{}
  const width=$("#printerWidth"),auto=$("#printerAuto");
  if(width)width.value=String(printerSettings.paperWidth||80);
  if(auto)auto.value=String(Boolean(printerSettings.autoPrint));
}
function savePrinterSettings(){
  const select=$("#printerSelect"),width=$("#printerWidth"),auto=$("#printerAuto");
  if(select)printerSettings.deviceName=select.value||"";
  if(width)printerSettings.paperWidth=Number(width.value)===58?58:80;
  if(auto)printerSettings.autoPrint=auto.value==="true";
  localStorage.setItem("es_printer",JSON.stringify(printerSettings));
}'''
new_printer = '''function printerStorageKey101026(){return `es_printer_store_${Number(lojaId)||1}`}
function readPrinterForm101026(){
  const select=$("#printerSelect"),width=$("#printerWidth"),auto=$("#printerAuto");
  if(select)printerSettings.deviceName=select.value||"";
  if(width)printerSettings.paperWidth=Number(width.value)===58?58:80;
  if(auto)printerSettings.autoPrint=auto.value==="true";
}
function loadPrinterSettings(){
  printerSettings={deviceName:"",paperWidth:80,autoPrint:false};
  const key=printerStorageKey101026();let raw=localStorage.getItem(key);
  // Migra uma única vez a configuração antiga para a loja atualmente selecionada.
  if(!raw){const legacy=localStorage.getItem("es_printer");if(legacy){raw=legacy;localStorage.setItem(key,legacy);localStorage.removeItem("es_printer")}}
  try{printerSettings={...printerSettings,...JSON.parse(raw||"{}")}}catch{}
  const width=$("#printerWidth"),auto=$("#printerAuto");
  if(width)width.value=String(printerSettings.paperWidth||80);
  if(auto)auto.value=String(Boolean(printerSettings.autoPrint));
}
function savePrinterSettings(showFeedback=false){
  readPrinterForm101026();
  localStorage.setItem(printerStorageKey101026(),JSON.stringify(printerSettings));
  if(showFeedback){
    const nome=nomeLojaPorId(lojaId),status=$("#printerStatus");
    if(status)status.textContent=`Configuração salva neste computador para ${nome}.`;
    toast(`Impressora salva para ${nome}.`);
  }
}'''
js = replace_once(js, old_printer, new_printer, "preferência de impressora por loja")
js = replace_once(js, '    savePrinterSettings();\n    if(status)status.textContent=`Pronta:', '    if(status)status.textContent=`Pronta:', "não salvar ao atualizar lista")
js = replace_once(js, '  savePrinterSettings();\n  if(!printerSettings.deviceName)', '  readPrinterForm101026();\n  if(!printerSettings.deviceName)', "teste sem salvar implicitamente")
old_cash = 'function renderCaixa(){const badge=$("#cashBadge"),box=$("#cashStatusBox");if(caixaAtual){badge.textContent="Caixa aberto";badge.className="badge ok";$("#openCashBox").classList.add("hidden");$("#closeCashBox").classList.remove("hidden");box.innerHTML=`<p><b>Caixa #${caixaAtual.id}</b></p><p>Aberto em: ${new Date(caixaAtual.abertoEm).toLocaleString("pt-BR")}</p><p>Saldo inicial: ${money(caixaAtual.saldoInicial)}</p>`}else{badge.textContent="Caixa fechado";badge.className="badge warn";$("#openCashBox").classList.remove("hidden");$("#closeCashBox").classList.add("hidden");box.innerHTML=\'<div class="warning-box">Nenhum caixa aberto. Abra um caixa para registrar vendas.</div>\'}}'
new_cash = '''function renderCaixa(){
  const box=$("#cashStatusBox"),open=$("#openCashBox"),close=$("#closeCashBox");
  if(caixaAtual){if(open)open.classList.add("hidden");if(close)close.classList.remove("hidden");if(box)box.innerHTML=`<p><b>Caixa #${caixaAtual.id}</b></p><p>Aberto em: ${new Date(caixaAtual.abertoEm).toLocaleString("pt-BR")}</p><p>Saldo inicial: ${money(caixaAtual.saldoInicial)}</p>`}
  else{if(open)open.classList.remove("hidden");if(close)close.classList.add("hidden");if(box)box.innerHTML='<div class="warning-box">Nenhum caixa aberto. Abra um caixa para registrar vendas.</div>'}
}'''
js = replace_once(js, old_cash, new_cash, "cabeçalho sem status de caixa")

old_users_ui = '''function userStoreAccessMarkup(selected=[],cargo="vendedor"){
  const ids=new Set((selected||[]).map(Number));
  const ativas=lojas.filter(l=>l.ativo);
  return `<div class="user-store-access"><label>Lojas que este login pode acessar</label><div class="user-store-grid">${ativas.map(l=>`<label class="user-store-option"><input type="checkbox" name="lojaIds" value="${l.id}" ${ids.has(Number(l.id))?"checked":""}><span>${esc(l.nome)}</span></label>`).join("")}</div><small class="user-store-help">Vendedor: marque uma ou várias lojas. Administrador: acesso automático a todas as lojas.</small></div>`;
}
function syncUserStoreFields(form){
  const admin=form?.cargo?.value==="admin";
  form?.querySelectorAll('input[name="lojaIds"]').forEach(x=>{x.disabled=admin;if(admin)x.checked=true});
}
function userPayload(form){
  const raw=Object.fromEntries(new FormData(form));
  raw.lojaIds=[...form.querySelectorAll('input[name="lojaIds"]:checked')].map(x=>Number(x.value));
  if(raw.ativo!==undefined)raw.ativo=raw.ativo==="true";
  return raw;
}
async function loadUsuarios(){
  if(me?.cargo!=="admin")return;
  const r=await api("/api/usuarios"),a=await r.json();if(!r.ok)return toast(a.erro||"Não foi possível carregar os usuários.");
  $("#tableUsuarios").innerHTML=a.map(u=>{
    const nomes=u.cargo==="admin"?["Todas as lojas"]:(u.lojaIds||[]).map(nomeLojaPorId);
    return `<tr><td>${esc(u.nome)}</td><td>${esc(u.login)}</td><td>${u.cargo==="admin"?"Administrador":"Vendedor"}</td><td><div class="user-store-badges">${nomes.map(n=>`<span class="user-store-badge">${esc(n)}</span>`).join("")||"<span class='muted'>Nenhuma</span>"}</div></td><td class="${u.ativo?"status-ok":"status-off"}">${u.ativo?"Ativo":"Inativo"}</td><td><div class="row-actions"><button class="edit" onclick="editUsuario(${u.id})">Editar</button></div></td></tr>`;
  }).join("");
}
function editMeuAcesso(){if(me?.cargo!=="admin")return;if(me?.id)return editUsuario(Number(me.id));}
function newUsuario(){
  if(me?.cargo!=="admin")return toast("Somente o administrador pode criar logins.");
  openModal("Novo usuário",`<form id="userForm" class="form-grid"><div><label>Nome</label><input name="nome" required></div><div><label>Login</label><input name="login" required autocomplete="off"></div><div><label>Senha</label><input name="senha" type="password" required autocomplete="new-password"></div><div><label>Cargo</label><select name="cargo"><option value="vendedor">Vendedor</option><option value="admin">Administrador</option></select></div>${userStoreAccessMarkup([],"vendedor")}<button class="primary full">Criar usuário</button></form>`);
  const f=$("#userForm");f.cargo.onchange=()=>syncUserStoreFields(f);syncUserStoreFields(f);
  f.onsubmit=async e=>{e.preventDefault();const raw=userPayload(e.target);if(raw.cargo!=="admin"&&!raw.lojaIds.length)return toast("Selecione pelo menos uma loja.");const r=await api("/api/usuarios",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(raw)}),d=await r.json();if(!r.ok)return toast(d.erro);closeModal();await loadUsuarios();toast("Usuário criado.")};
}
async function editUsuario(id){
  if(me?.cargo!=="admin")return toast("Somente o administrador pode alterar logins.");
  const r=await api("/api/usuarios"),a=await r.json();if(!r.ok)return toast(a.erro||"Não foi possível carregar o usuário.");const u=a.find(x=>x.id===id);if(!u)return toast("Usuário não encontrado.");
  openModal("Editar usuário",`<form id="editUserForm" class="form-grid"><div><label>Nome</label><input name="nome" value="${esc(u.nome)}" required></div><div><label>Login</label><input name="login" value="${esc(u.login)}" required autocomplete="off"></div><div><label>Cargo</label><select name="cargo"><option value="vendedor" ${u.cargo==="vendedor"?"selected":""}>Vendedor</option><option value="admin" ${u.cargo==="admin"?"selected":""}>Administrador</option></select></div><div><label>Status</label><select name="ativo"><option value="true" ${u.ativo?"selected":""}>Ativo</option><option value="false" ${!u.ativo?"selected":""}>Inativo</option></select></div><div class="full"><label>Nova senha (deixe em branco para manter)</label><input name="senha" type="password" autocomplete="new-password"></div>${userStoreAccessMarkup(u.lojaIds||[],u.cargo)}<button class="primary full">Salvar alterações</button></form>`);
  const f=$("#editUserForm");f.cargo.onchange=()=>syncUserStoreFields(f);syncUserStoreFields(f);
  f.onsubmit=async e=>{e.preventDefault();const raw=userPayload(e.target);if(raw.cargo!=="admin"&&!raw.lojaIds.length)return toast("Selecione pelo menos uma loja.");const rr=await api(`/api/usuarios/${id}`,{method:"PUT",headers:{"Content-Type":"application/json"},body:JSON.stringify(raw)}),d=await rr.json();if(!rr.ok)return toast(d.erro);if(id===me?.id){me={...me,...d};ajustarLojaAoUsuario();if($("#userName"))$("#userName").textContent=me.nome||me.login}closeModal();await loadUsuarios();await loadLojas();toast("Usuário atualizado.")};
}'''
new_users_ui = '''function userStoreAccessMarkup(selected=[],cargo="vendedor",allStores=false){
  const ids=new Set((selected||[]).map(Number)),ativas=lojas.filter(l=>l.ativo),isAdmin=cargo==="admin";
  return `<div class="user-store-access"><label>Lojas que este login pode acessar</label><label class="check-line user-all-stores ${isAdmin?"":"hidden"}"><input type="checkbox" name="acessoTodasLojas" ${allStores?"checked":""}> Todas as lojas, inclusive lojas criadas no futuro</label><div class="user-store-grid">${ativas.map(l=>`<label class="user-store-option"><input type="checkbox" name="lojaIds" value="${l.id}" ${ids.has(Number(l.id))?"checked":""}><span>${esc(l.nome)}</span></label>`).join("")}</div><small class="user-store-help">Marque somente as lojas em que esta pessoa poderá trabalhar.</small></div>`;
}
function syncUserStoreFields(form){
  const admin=form?.cargo?.value==="admin",allWrap=form?.querySelector('.user-all-stores'),all=form?.querySelector('input[name="acessoTodasLojas"]');
  if(allWrap)allWrap.classList.toggle("hidden",!admin);if(!admin&&all)all.checked=false;
  form?.querySelectorAll('input[name="lojaIds"]').forEach(x=>{x.disabled=Boolean(admin&&all?.checked)});
}
function userPayload(form){
  const raw=Object.fromEntries(new FormData(form));
  raw.lojaIds=[...form.querySelectorAll('input[name="lojaIds"]:checked')].map(x=>Number(x.value));
  raw.acessoTodasLojas=Boolean(form.querySelector('input[name="acessoTodasLojas"]:checked'));
  if(raw.ativo!==undefined)raw.ativo=raw.ativo==="true";
  return raw;
}
async function loadUsuarios(){
  if(me?.cargo!=="admin")return;
  const r=await api("/api/usuarios"),a=await r.json();if(!r.ok)return toast(a.erro||"Não foi possível carregar os usuários.");
  $("#tableUsuarios").innerHTML=a.map(u=>{
    const nomes=u.acessoTodasLojas?["Todas as lojas"]:(u.lojaIds||[]).map(nomeLojaPorId),podeEditar=u.cargo!=="admin"||Number(u.id)===Number(me?.id);
    const acao=podeEditar?`<button class="edit" onclick="editUsuario(${u.id})">Editar</button>`:'<span class="admin-protected-101026">Conta protegida</span>';
    return `<tr><td>${esc(u.nome)}</td><td>${esc(u.login)}</td><td>${u.cargo==="admin"?"Administrador":"Vendedor"}</td><td><div class="user-store-badges">${nomes.map(n=>`<span class="user-store-badge">${esc(n)}</span>`).join("")||"<span class='muted'>Nenhuma</span>"}</div></td><td class="${u.ativo?"status-ok":"status-off"}">${u.ativo?"Ativo":"Inativo"}</td><td><div class="row-actions">${acao}</div></td></tr>`;
  }).join("");
}
function editMeuAcesso(){if(me?.cargo!=="admin")return;if(me?.id)return editUsuario(Number(me.id));}
function newUsuario(){
  if(me?.cargo!=="admin")return toast("Somente o administrador pode criar logins.");
  openModal("Novo usuário",`<form id="userForm" class="form-grid"><div><label>Nome</label><input name="nome" required></div><div><label>Login</label><input name="login" required autocomplete="off"></div><div><label>Senha</label><input name="senha" type="password" required autocomplete="new-password"></div><div><label>Cargo</label><select name="cargo"><option value="vendedor">Vendedor</option><option value="admin">Administrador</option></select></div>${userStoreAccessMarkup([],"vendedor",false)}<button class="primary full">Criar usuário</button></form>`);
  const f=$("#userForm");f.cargo.onchange=()=>syncUserStoreFields(f);f.querySelector('input[name="acessoTodasLojas"]')?.addEventListener("change",()=>syncUserStoreFields(f));syncUserStoreFields(f);
  f.onsubmit=async e=>{e.preventDefault();const raw=userPayload(e.target);if(!raw.acessoTodasLojas&&!raw.lojaIds.length)return toast("Selecione pelo menos uma loja.");const r=await api("/api/usuarios",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(raw)}),d=await r.json();if(!r.ok)return toast(d.erro);closeModal();await loadUsuarios();toast(raw.cargo==="admin"?"Administrador criado com as lojas selecionadas.":"Usuário criado.")};
}
async function editUsuario(id){
  if(me?.cargo!=="admin")return toast("Somente o administrador pode alterar logins.");
  const r=await api("/api/usuarios"),a=await r.json();if(!r.ok)return toast(a.erro||"Não foi possível carregar o usuário.");const u=a.find(x=>x.id===id);if(!u)return toast("Usuário não encontrado.");
  if(u.cargo==="admin"&&Number(u.id)!==Number(me?.id))return toast("Cada administrador só pode alterar a própria conta.");
  const ownAdmin=u.cargo==="admin"&&Number(u.id)===Number(me?.id);
  const scope=ownAdmin?`<div class="full admin-scope-readonly-101026"><b>Lojas permitidas</b><div class="user-store-badges">${(u.acessoTodasLojas?["Todas as lojas"]:(u.lojaIds||[]).map(nomeLojaPorId)).map(n=>`<span class="user-store-badge">${esc(n)}</span>`).join("")}</div><small>O próprio administrador não pode aumentar suas permissões.</small></div>`:userStoreAccessMarkup(u.lojaIds||[],u.cargo,Boolean(u.acessoTodasLojas));
  const controls=ownAdmin?'':`<div><label>Cargo</label><select name="cargo"><option value="vendedor" ${u.cargo==="vendedor"?"selected":""}>Vendedor</option><option value="admin" ${u.cargo==="admin"?"selected":""}>Administrador</option></select></div><div><label>Status</label><select name="ativo"><option value="true" ${u.ativo?"selected":""}>Ativo</option><option value="false" ${!u.ativo?"selected":""}>Inativo</option></select></div>`;
  openModal(ownAdmin?"Editar minha conta":"Editar usuário",`<form id="editUserForm" class="form-grid"><div><label>Nome</label><input name="nome" value="${esc(u.nome)}" required></div><div><label>Login</label><input name="login" value="${esc(u.login)}" required autocomplete="off"></div>${controls}<div class="full"><label>Nova senha (deixe em branco para manter)</label><input name="senha" type="password" autocomplete="new-password"></div>${scope}<button class="primary full">Salvar alterações</button></form>`);
  const f=$("#editUserForm");if(!ownAdmin){f.cargo.onchange=()=>syncUserStoreFields(f);f.querySelector('input[name="acessoTodasLojas"]')?.addEventListener("change",()=>syncUserStoreFields(f));syncUserStoreFields(f)}
  f.onsubmit=async e=>{e.preventDefault();const raw=ownAdmin?Object.fromEntries(new FormData(e.target)):userPayload(e.target);if(!ownAdmin&&!raw.acessoTodasLojas&&!raw.lojaIds.length)return toast("Selecione pelo menos uma loja.");const rr=await api(`/api/usuarios/${id}`,{method:"PUT",headers:{"Content-Type":"application/json"},body:JSON.stringify(raw)}),d=await rr.json();if(!rr.ok)return toast(d.erro);if(id===me?.id){me={...me,...d};ajustarLojaAoUsuario();if($("#userName"))$("#userName").textContent=me.nome||me.login}closeModal();await loadUsuarios();await loadLojas();toast("Usuário atualizado.")};
}'''
js = replace_once(js, old_users_ui, new_users_ui, "interface de usuários")
js = replace_once(
    js,
    '<div class="receipt-signature">Assinatura do cliente</div></div>`;',
    '<div class="receipt-signature">${garantia?\'Assinatura do funcionário\':\'Assinatura do cliente\'}</div></div>`;',
    "assinatura do funcionário na via de garantia",
)
js = replace_once(
    js,
    '    if(target.closest?.("#testPrinterBtn")){e.preventDefault();testPrinter();return}',
    '    if(target.closest?.("#testPrinterBtn")){e.preventDefault();testPrinter();return}\n    if(target.closest?.("#savePrinterBtn")){e.preventDefault();savePrinterSettings(true);return}',
    "evento salvar impressora",
)
js = replace_once(
    js,
    '  for(const id of ["printerSelect","printerWidth","printerAuto"]){const el=$("#"+id);if(el)el.addEventListener("change",savePrinterSettings)}',
    '  for(const id of ["printerSelect","printerWidth","printerAuto"]){const el=$("#"+id);if(el)el.addEventListener("change",()=>{readPrinterForm101026();const status=$("#printerStatus");if(status)status.textContent=`Alterações não salvas para ${nomeLojaPorId(lojaId)}.`})}',
    "impressora só salva no botão",
)
js = replace_once(
    js,
    ''' bootPromise101025=(async()=>{
  renderEsIcons();''',
    ''' bootPromise101025=(async()=>{
  renderEsIcons();loadPrinterSettings();''',
    "recarregar impressora ao trocar de loja",
)
write("public/app.js", js)

css = read("public/style.css") + r'''

/* 10.10.26 - impressora por loja e proteção visual de administradores */
.printer-save-row{display:flex}.printer-save-row button{width:100%;min-height:42px}.admin-protected-101026{display:inline-flex;align-items:center;padding:5px 8px;border-radius:999px;background:color-mix(in srgb,var(--border) 55%,transparent);color:var(--text-muted);font-size:11px;font-weight:800}.admin-scope-readonly-101026{padding:12px;border:1px solid var(--border);border-radius:10px;background:color-mix(in srgb,var(--card-bg) 94%,var(--page-bg) 6%)}.admin-scope-readonly-101026>b,.admin-scope-readonly-101026>small{display:block}.admin-scope-readonly-101026 .user-store-badges{margin:8px 0}.user-all-stores{margin:7px 0 10px;padding:10px;border:1px solid var(--border);border-radius:9px;background:color-mix(in srgb,var(--accent) 7%,var(--card-bg))}
'''
write("public/style.css", css)

print("10.10.26: impressora por loja, administradores isolados e cabeçalho simplificado.")
