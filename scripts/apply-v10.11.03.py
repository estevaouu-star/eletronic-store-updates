from pathlib import Path
import json
import re

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
pkg["version"] = "10.11.3"
write("package.json", json.dumps(pkg, indent=2, ensure_ascii=False))

html, changed = re.subn(r'(id="versionInfo" class="version-info">v)[0-9.]+', r'\g<1>10.11.03', read("public/index.html"), count=1)
if changed != 1:
    raise SystemExit("Trecho não encontrado: versão no cabeçalho")
write("public/index.html", html)

js, changed = re.subn(r'const atual="[0-9.]+"(?=,status=)', 'const atual="10.11.3"', read("public/app.js"), count=1)
if changed != 1:
    raise SystemExit("Trecho não encontrado: versão do atualizador")

server = read("src/server.ts")
server = replace_once(server, 'import crypto from "crypto";', 'import crypto from "crypto";\nimport { gzipSync, gunzipSync } from "zlib";', "importação GZIP")
server = replace_once(
    server,
    'const rows=await cloudRpc("electronic_store_pull",{p_sync_id:c.syncId,p_secret:c.secret});\n      const row=Array.isArray(rows)?rows[0]:rows;\n      if(row?.payload&&Object.keys(row.payload).length){db=row.payload as Banco;fs.writeFileSync(dataFile,JSON.stringify(db,null,2));cloudDirty=false;cloudVersion=Number(row.version)||meta.version;cloudUpdatedAt=row.updated_at||meta.updated_at||"";}',
    'const rows=await cloudRpc("electronic_store_pull",{p_sync_id:c.syncId,p_secret:c.secret,p_accept_gzip:true});\n      const row=Array.isArray(rows)?rows[0]:rows;\n      const payload=row?.payload_gzip?JSON.parse(gunzipSync(Buffer.from(row.payload_gzip,"base64")).toString("utf8")):row?.payload;\n      if(payload&&Object.keys(payload).length){db=payload as Banco;fs.writeFileSync(dataFile,JSON.stringify(db,null,2));cloudDirty=false;cloudVersion=Number(row.version)||meta.version;cloudUpdatedAt=row.updated_at||meta.updated_at||"";}',
    "download GZIP",
)
server = replace_once(
    server,
    'const rows=await cloudRpc("electronic_store_push",{p_sync_id:c.syncId,p_secret:c.secret,p_payload:db,p_expected_version:cloudVersion});',
    'const payloadGzip=gzipSync(Buffer.from(JSON.stringify(db)),{level:9}).toString("base64");\n    const rows=await cloudRpc("electronic_store_push",{p_sync_id:c.syncId,p_secret:c.secret,p_payload_gzip:payloadGzip,p_encoding:"gzip-base64",p_expected_version:cloudVersion});',
    "upload GZIP",
)
server = replace_once(
    server,
    'function agendarCloudPush(){if(cloudPushTimer)clearTimeout(cloudPushTimer);cloudPushTimer=setTimeout(()=>cloudPush(),350)}',
    'function agendarCloudPush(){if(cloudPushTimer)clearTimeout(cloudPushTimer);cloudPushTimer=setTimeout(()=>cloudPush(),1200)}',
    "agrupamento de alterações",
)

anchor='app.post("/api/login",'
idx=server.find(anchor)
if idx<0:
    raise SystemExit("Trecho não encontrado: rota /api/login")
route=r'''
// 10.11.03 - primeiro acesso local em computador novo, sem depender da nuvem.
app.post("/api/primeiro-acesso-local",(req,res)=>{
  const remote=String(req.socket.remoteAddress||"");
  const local=remote==="127.0.0.1"||remote==="::1"||remote.endsWith(":127.0.0.1");
  if(!local)return res.status(403).json({erro:"Configuração inicial permitida apenas neste computador."});
  const {login,senha}=req.body||{};
  const loginLimpo=String(login||"").trim();
  const senhaLimpa=String(senha||"");
  if(!loginLimpo||senhaLimpa.length<4)return res.status(400).json({erro:"Informe usuário e senha com pelo menos 4 caracteres."});
  const ativos=db.usuarios.filter(u=>u.ativo);
  const padrao=ativos.length===1&&ativos[0].cargo==="admin"&&String(ativos[0].login).toLowerCase()==="admin"&&String(ativos[0].nome).toLowerCase().includes("administrador");
  if(!padrao)return res.status(409).json({erro:"Este computador já possui acesso configurado."});
  const u=ativos[0];
  u.login=loginLimpo;u.nome=loginLimpo;u.senhaHash=senhaHash(senhaLimpa);salvar();
  const token=crypto.randomBytes(24).toString("hex");
  sessoes.set(token,{usuarioId:u.id,expira:Date.now()+8*60*60*1000});
  res.json({token,usuario:{id:u.id,nome:u.nome,login:u.login,cargo:u.cargo,lojaIds:idsLojasPermitidas(u)},primeiroAcesso:true});
});

'''
server=server[:idx]+route+server[idx:]
write("src/server.ts", server)

js += r'''

// 10.11.03 - em instalação nova, o primeiro login pode ser configurado localmente.
async function primeiroAcessoLocal101103(login,senha){
  const r=await fetch('/api/primeiro-acesso-local',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({login,senha})});
  let d={};try{d=await r.json()}catch{}
  return r.ok?d:null;
}
document.addEventListener('DOMContentLoaded',()=>{
 const form=document.querySelector('#loginForm');if(!form||form.dataset.login101103)return;
 form.dataset.login101103='1';
 form.addEventListener('submit',async e=>{
   e.preventDefault();e.stopImmediatePropagation();
   const login=(document.querySelector('#login')?.value||'').trim(),senha=document.querySelector('#senha')?.value||'',err=document.querySelector('#loginError'),btn=form.querySelector('button[type=submit]');
   if(btn){btn.disabled=true;btn.textContent='Entrando...'}
   try{
     const r=await fetch('/api/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({login,senha})});
     let d={};try{d=await r.json()}catch{}
     if(r.ok){token=d.token;me=d.usuario;localStorage.setItem('es_token',token);if(err)err.textContent='';showApp();await boot();return}
     const local=await primeiroAcessoLocal101103(login,senha);
     if(local){token=local.token;me=local.usuario;localStorage.setItem('es_token',token);if(err)err.textContent='';showApp();await boot();toast('Acesso deste computador configurado.');return}
     if(err)err.textContent=d.erro||'Usuário ou senha inválidos.';
   }catch(ex){console.error('Falha no login',ex);if(err)err.textContent='Não foi possível conectar ao sistema local.'}
   finally{if(btn){btn.disabled=false;btn.textContent='Entrar'}}
 },true);
});
'''
write("public/app.js", js)

print("10.11.03: GZIP mantido e primeiro login local em computador novo corrigido.")
