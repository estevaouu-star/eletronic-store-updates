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
pkg['version']='10.8.4'
write('package.json',json.dumps(pkg,indent=2,ensure_ascii=False))

# -----------------------------------------------------------------------------
# HTML: deixa explícito que somente ADM gerencia acessos e mostra lojas na tabela.
# -----------------------------------------------------------------------------
html=read('public/index.html')
html=html.replace('id="versionInfo" class="version-info">v10.8.3','id="versionInfo" class="version-info">v10.8.4',1)
html=html.replace('Crie acessos individuais para saber quem está usando o caixa.','Somente administradores podem criar ou alterar logins, inclusive o próprio. Defina também quais lojas cada usuário pode acessar.',1)
html=html.replace('<th>Nome</th><th>Login</th><th>Cargo</th><th>Status</th><th></th>','<th>Nome</th><th>Login</th><th>Cargo</th><th>Lojas permitidas</th><th>Status</th><th></th>',1)
write('public/index.html',html)

css=read('public/style.css')
css += r'''
/* 10.8.4 - permissões de usuário por loja */
.user-store-access{grid-column:1/-1;border:1px solid var(--border);border-radius:14px;padding:12px 14px;background:color-mix(in srgb,var(--card-bg) 94%,var(--accent) 6%)}
.user-store-access>label:first-child{display:block;margin-bottom:8px;font-weight:800}.user-store-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}.user-store-option{display:flex;align-items:center;gap:8px;padding:9px 10px;border:1px solid var(--border);border-radius:10px;background:var(--card-bg)}.user-store-option input{width:auto!important;margin:0}.user-store-help{display:block;margin-top:8px;color:var(--text-muted)}.user-store-badges{display:flex;flex-wrap:wrap;gap:5px}.user-store-badge{display:inline-flex;padding:4px 7px;border:1px solid var(--border);border-radius:999px;font-size:11px;font-weight:700;background:var(--card-bg)}
@media(max-width:720px){.user-store-grid{grid-template-columns:1fr}}
'''
write('public/style.css',css)

# -----------------------------------------------------------------------------
# Backend: lojas permitidas por usuário e gestão de login somente por ADM.
# ADM sempre tem acesso a todas as lojas ativas. Vendedor pode ter uma ou várias.
# -----------------------------------------------------------------------------
server=read('src/server.ts')
server=must(server,
'''type Usuario = {
  id:number; nome:string; login:string; senhaHash:string;
  cargo:Cargo; ativo:boolean; criadoEm:string;
};''',
'''type Usuario = {
  id:number; nome:string; login:string; senhaHash:string;
  cargo:Cargo; ativo:boolean; criadoEm:string; lojaIds?:number[];
};''','tipo Usuario com lojas')

# Migração: instalações existentes continuam funcionando; vendedores atuais recebem as lojas ativas atuais.
old_migration='''if(!Array.isArray(db.usuarios))db.usuarios=[];
if(db.usuarios.length===0){
  db.usuarios.push({id:db.seq.usuario++,nome:"Administrador",login:"admin",senhaHash:senhaHash("admin123"),cargo:"admin",ativo:true,criadoEm:now()});
  salvar();
}

const sessoes = new Map<string,{usuarioId:number;expira:number}>();'''
new_migration='''if(!Array.isArray(db.usuarios))db.usuarios=[];
if(db.usuarios.length===0){
  db.usuarios.push({id:db.seq.usuario++,nome:"Administrador",login:"admin",senhaHash:senhaHash("admin123"),cargo:"admin",ativo:true,criadoEm:now(),lojaIds:db.lojas.filter(l=>l.ativo).map(l=>l.id)});
  salvar();
}
let usuariosMigrados=false;
const lojasAtivasIds=()=>db.lojas.filter(l=>l.ativo).map(l=>l.id);
for(const u of db.usuarios){
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
}

const sessoes = new Map<string,{usuarioId:number;expira:number}>();'''
server=must(server,old_migration,new_migration,'migracao de permissoes por loja')

# lojaIdReq jamais entrega uma loja não autorizada ao usuário autenticado.
old_loja='''function lojaIdReq(req:express.Request):number {
  const requested=Number(req.headers["x-store-id"]||1);
  const loja=db.lojas.find(l=>l.id===requested&&l.ativo) || db.lojas.find(l=>l.ativo);
  return loja?.id || 1;
}'''
new_loja='''function lojaIdReq(req:express.Request):number {
  const requested=Number(req.headers["x-store-id"]||1);
  const u=(req as any).usuario as Usuario|undefined;
  const permitidas=u?lojasPermitidasUsuario(u):db.lojas.filter(l=>l.ativo);
  const loja=permitidas.find(l=>l.id===requested) || permitidas[0];
  return loja?.id || 0;
}'''
server=must(server,old_loja,new_loja,'lojaIdReq autorizado')

# Login e /me informam ao frontend as lojas efetivamente permitidas.
old_login='''  const token=crypto.randomBytes(24).toString("hex");
  sessoes.set(token,{usuarioId:u.id,expira:Date.now()+8*60*60*1000});
  res.json({token,usuario:{id:u.id,nome:u.nome,login:u.login,cargo:u.cargo}});'''
new_login='''  const lojaIds=idsLojasPermitidas(u);
  if(u.cargo!=="admin" && lojaIds.length===0)return res.status(403).json({erro:"Este usuário não possui nenhuma loja liberada. Peça ao administrador para liberar o acesso."});
  const token=crypto.randomBytes(24).toString("hex");
  sessoes.set(token,{usuarioId:u.id,expira:Date.now()+8*60*60*1000});
  res.json({token,usuario:{id:u.id,nome:u.nome,login:u.login,cargo:u.cargo,lojaIds}});'''
server=must(server,old_login,new_login,'login com lojaIds')
server=must(server,
'''  res.json({id:u.id,nome:u.nome,login:u.login,cargo:u.cargo,caixa:caixaAbertoDoUsuario(u.id,lojaIdReq(req))||null});''',
'''  const lojaIds=idsLojasPermitidas(u);
  res.json({id:u.id,nome:u.nome,login:u.login,cargo:u.cargo,lojaIds,caixa:caixaAbertoDoUsuario(u.id,lojaIdReq(req))||null});''','me com lojaIds')

# Lista de lojas: vendedor vê apenas as liberadas; ADM vê todas.
server=must(server,
'app.get("/api/lojas",auth,(_req,res)=>res.json(db.lojas));',
'''app.get("/api/lojas",auth,(req,res)=>{
  const u=(req as any).usuario as Usuario;
  if(u.cargo==="admin")return res.json(db.lojas);
  const ids=new Set(idsLojasPermitidas(u));
  res.json(db.lojas.filter(l=>ids.has(l.id)));
});''','GET lojas filtrado')

# Visão geral também respeita as lojas do login.
server=must(server,
'''app.get("/api/lojas/resumo-geral",auth,(_req,res)=>{
  const hoje=new Date().toLocaleDateString("sv-SE");
  const resumo=db.lojas.filter(l=>l.ativo).map(l=>{''',
'''app.get("/api/lojas/resumo-geral",auth,(req,res)=>{
  const hoje=new Date().toLocaleDateString("sv-SE");
  const u=(req as any).usuario as Usuario;
  const permitidas=new Set(idsLojasPermitidas(u));
  const resumo=db.lojas.filter(l=>l.ativo&&permitidas.has(l.id)).map(l=>{''','resumo geral filtrado')

# Relatório consolidado nunca mostra unidades fora da permissão do login.
server=must(server,
'''app.get("/api/relatorios/consolidado",auth,(req,res)=>{
  const {inicio,fim,de,ate}=parsePeriodo(req);
  const lojas=db.lojas.filter(l=>l.ativo).map(loja=>({loja,...relatorioDaLoja(loja.id,inicio,fim)}));''',
'''app.get("/api/relatorios/consolidado",auth,(req,res)=>{
  const {inicio,fim,de,ate}=parsePeriodo(req);
  const u=(req as any).usuario as Usuario;
  const permitidas=new Set(idsLojasPermitidas(u));
  const lojas=db.lojas.filter(l=>l.ativo&&permitidas.has(l.id)).map(loja=>({loja,...relatorioDaLoja(loja.id,inicio,fim)}));''','relatorio consolidado filtrado')

# Substitui rotas de usuário: apenas ADM; login, senha, cargo, status e lojas editáveis.
old_users='''// Usuários
app.get("/api/usuarios",auth,admin,(_req,res)=>res.json(db.usuarios.map(({senhaHash,...u})=>u)));
app.post("/api/usuarios",auth,admin,(req,res)=>{
  const {nome,login,senha,cargo="vendedor"}=req.body;
  if(!nome||!login||!senha)return res.status(400).json({erro:"Nome, login e senha são obrigatórios."});
  if(db.usuarios.some(u=>u.login===String(login).trim()))return res.status(409).json({erro:"Esse login já existe."});
  const u:Usuario={id:db.seq.usuario++,nome:String(nome),login:String(login).trim(),senhaHash:senhaHash(String(senha)),cargo:cargo==="admin"?"admin":"vendedor",ativo:true,criadoEm:now()};
  db.usuarios.push(u);salvar();const {senhaHash:_,...safe}=u;res.status(201).json(safe);
});
app.put("/api/usuarios/:id",auth,admin,(req,res)=>{
  const u=db.usuarios.find(x=>x.id===Number(req.params.id));if(!u)return res.status(404).json({erro:"Usuário não encontrado."});
  if(req.body.nome!==undefined)u.nome=String(req.body.nome);
  if(req.body.cargo!==undefined)u.cargo=req.body.cargo==="admin"?"admin":"vendedor";
  if(req.body.ativo!==undefined)u.ativo=Boolean(req.body.ativo);
  if(req.body.senha)u.senhaHash=senhaHash(String(req.body.senha));
  salvar();const {senhaHash:_,...safe}=u;res.json(safe);
});'''
new_users='''// Usuários - somente administradores gerenciam acessos, inclusive o próprio login.
app.get("/api/usuarios",auth,admin,(_req,res)=>res.json(db.usuarios.map(({senhaHash,...u})=>({...u,lojaIds:idsLojasPermitidas(u)}))));
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
server=must(server,old_users,new_users,'rotas de usuarios com lojas')
write('src/server.ts',server)

# -----------------------------------------------------------------------------
# Frontend: seletor só mostra lojas permitidas e gestão de usuários tem checkboxes.
# -----------------------------------------------------------------------------
js=read('public/app.js')

# Alinha a loja escolhida assim que /me responde, antes do boot paralelo.
helper='''function ajustarLojaAoUsuario(){
  const permitidas=Array.isArray(me?.lojaIds)?me.lojaIds.map(Number):[];
  if(permitidas.length && !permitidas.includes(Number(lojaId))){
    lojaId=permitidas[0];localStorage.setItem("es_store_id",String(lojaId));
  }
}
'''
anchor='function openModal(title,html){'
if helper not in js:
    js=must(js,anchor,helper+anchor,'helper de loja do usuario')
js=js.replace('me=await r.json();caixaAtual=me.caixa;showApp();await boot();','me=await r.json();caixaAtual=me.caixa;ajustarLojaAoUsuario();showApp();await boot();',1)
js=js.replace('me=await meResp.json();caixaAtual=me.caixa||null;\n    showApp();','me=await meResp.json();caixaAtual=me.caixa||null;ajustarLojaAoUsuario();\n    showApp();',1)

# Segurança visual extra: se a API retornar somente lojas permitidas, o seletor segue essa lista.
old_users_js='''async function loadUsuarios(){const a=await(await api("/api/usuarios")).json();$("#tableUsuarios").innerHTML=a.map(u=>`<tr><td>${esc(u.nome)}</td><td>${esc(u.login)}</td><td>${esc(u.cargo)}</td><td class="${u.ativo?"status-ok":"status-off"}">${u.ativo?"Ativo":"Inativo"}</td><td><div class="row-actions"><button class="edit" onclick="editUsuario(${u.id})">Editar</button></div></td></tr>`).join("")}
function newUsuario(){openModal("Novo usuário",`<form id="userForm" class="form-grid"><div><label>Nome</label><input name="nome" required></div><div><label>Login</label><input name="login" required></div><div><label>Senha</label><input name="senha" type="password" required></div><div><label>Cargo</label><select name="cargo"><option value="vendedor">Vendedor</option><option value="admin">Administrador</option></select></div><button class="primary full">Criar usuário</button></form>`);$("#userForm").onsubmit=async e=>{e.preventDefault();const r=await api("/api/usuarios",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(Object.fromEntries(new FormData(e.target)))}),d=await r.json();if(!r.ok)return toast(d.erro);closeModal();await loadUsuarios();toast("Usuário criado.")}}
async function editUsuario(id){const a=await(await api("/api/usuarios")).json(),u=a.find(x=>x.id===id);openModal("Editar usuário",`<form id="editUserForm" class="form-grid"><div><label>Nome</label><input name="nome" value="${esc(u.nome)}"></div><div><label>Cargo</label><select name="cargo"><option value="vendedor" ${u.cargo==="vendedor"?"selected":""}>Vendedor</option><option value="admin" ${u.cargo==="admin"?"selected":""}>Administrador</option></select></div><div><label>Status</label><select name="ativo"><option value="true" ${u.ativo?"selected":""}>Ativo</option><option value="false" ${!u.ativo?"selected":""}>Inativo</option></select></div><div><label>Nova senha (opcional)</label><input name="senha" type="password"></div><button class="primary full">Salvar</button></form>`);$("#editUserForm").onsubmit=async e=>{e.preventDefault();const raw=Object.fromEntries(new FormData(e.target));raw.ativo=raw.ativo==="true";const r=await api(`/api/usuarios/${id}`,{method:"PUT",headers:{"Content-Type":"application/json"},body:JSON.stringify(raw)}),d=await r.json();if(!r.ok)return toast(d.erro);closeModal();await loadUsuarios();toast("Usuário atualizado.")}}'''
new_users_js=r'''function nomeLojaPorId(id){return lojas.find(l=>Number(l.id)===Number(id))?.nome||`Loja ${id}`}
function userStoreAccessMarkup(selected=[],cargo="vendedor"){
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
js=must(js,old_users_js,new_users_js,'gestao de usuarios por lojas')

js=js.replace('const atual="10.8.3"','const atual="10.8.4"',1)
write('public/app.js',js)

print('Patch 10.8.4 aplicado: somente ADM gerencia logins e vendedores podem ter uma ou várias lojas permitidas.')
