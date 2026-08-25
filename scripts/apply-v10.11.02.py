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
pkg["version"] = "10.11.2"
write("package.json", json.dumps(pkg, indent=2, ensure_ascii=False))

html, html_changes = re.subn(
    r'(id="versionInfo" class="version-info">v)[0-9.]+',
    r'\g<1>10.11.02',
    read("public/index.html"),
    count=1,
)
if html_changes != 1:
    raise SystemExit("Trecho não encontrado: versão no cabeçalho")
write("public/index.html", html)

js, js_changes = re.subn(r'const atual="[0-9.]+"(?=,status=)', 'const atual="10.11.2"', read("public/app.js"), count=1)
if js_changes != 1:
    raise SystemExit("Trecho não encontrado: versão do atualizador")
write("public/app.js", js)

server = read("src/server.ts")
start = server.find('const cloudFile=path.join(dataDir,"cloud.json");')
end = server.find("\n\nfunction lojaIdReq", start)
if start < 0 or end < 0:
    raise SystemExit("Trecho não encontrado: sincronização em nuvem")

cloud = r'''const cloudFile=path.join(dataDir,"cloud.json");
const cloudStateFile101102=path.join(dataDir,"cloud-state.json");
const CLOUD_URL_101102="https://eletromix-mobile.estevaouu.chatgpt.site";
type CloudCfg={enabled:boolean;url:string;publishableKey:string;syncId:string;secret:string;pollSeconds:number};
function cloudCfg():CloudCfg|null{
  let cfg:CloudCfg;
  try{cfg=JSON.parse(fs.readFileSync(cloudFile,"utf8"))}
  catch{try{cfg=JSON.parse(fs.readFileSync(path.join(__dirname,"../data/cloud.json"),"utf8"))}catch{return null}}
  if(!cfg||typeof cfg!=="object")return null;
  const antiga=/supabase\.co/i.test(String(cfg.url||""));
  if(antiga||!cfg.url){cfg.url=CLOUD_URL_101102;cfg.publishableKey="";cfg.pollSeconds=0;try{fs.writeFileSync(cloudFile,JSON.stringify(cfg,null,2))}catch{}}
  return cfg;
}
function carregarCloudState101102(){try{const s=JSON.parse(fs.readFileSync(cloudStateFile101102,"utf8"));return {version:Math.max(0,Number(s.version)||0),updatedAt:String(s.updatedAt||"")}}catch{return {version:0,updatedAt:""}}}
function salvarCloudState101102(){try{fs.writeFileSync(cloudStateFile101102,JSON.stringify({version:cloudVersion,updatedAt:cloudUpdatedAt},null,2))}catch{}}
const cloudInicial101102=carregarCloudState101102();
let cloudVersion=cloudInicial101102.version,cloudState:"online"|"offline"|"syncing"|"local"="local",cloudMessage="Atualização manual",cloudUpdatedAt=cloudInicial101102.updatedAt;
let cloudPushTimer:NodeJS.Timeout|null=null,cloudBusy=false,cloudDirty=false;
async function cloudRpc(name:string,body:any){
  const c=cloudCfg(); if(!c?.enabled)throw new Error("Nuvem desativada");
  const r=await fetch(`${String(c.url).replace(/\/$/,"")}/rest/v1/rpc/${name}`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)});
  const text=await r.text(); if(!r.ok)throw new Error(text||`HTTP ${r.status}`); return text?JSON.parse(text):null;
}
async function cloudRemoteVersion101102(){
  const c=cloudCfg();if(!c?.enabled)return {version:0,updated_at:""};
  const rows=await cloudRpc("electronic_store_version",{p_sync_id:c.syncId,p_secret:c.secret});
  const row=Array.isArray(rows)?rows[0]:rows;return {version:Number(row?.version)||0,updated_at:String(row?.updated_at||"")};
}
async function cloudPull(apply=true){
  const c=cloudCfg();if(!c?.enabled){cloudState="local";cloudMessage="Modo local";return false}
  cloudState="syncing";cloudMessage="Verificando alterações...";
  try{
    const meta=await cloudRemoteVersion101102();
    if(apply&&meta.version>cloudVersion){
      cloudMessage="Baixando alteração nova...";
      const rows=await cloudRpc("electronic_store_pull",{p_sync_id:c.syncId,p_secret:c.secret});
      const row=Array.isArray(rows)?rows[0]:rows;
      if(row?.payload&&Object.keys(row.payload).length){db=row.payload as Banco;fs.writeFileSync(dataFile,JSON.stringify(db,null,2));cloudDirty=false;cloudVersion=Number(row.version)||meta.version;cloudUpdatedAt=row.updated_at||meta.updated_at||"";}
    }else{cloudVersion=meta.version||cloudVersion;cloudUpdatedAt=meta.updated_at||cloudUpdatedAt;}
    salvarCloudState101102();cloudState="online";cloudMessage="Atualizado manualmente";return true;
  }catch(e:any){cloudState="offline";cloudMessage="Sem conexão com a nuvem";console.error("Cloud pull:",e?.message||e);return false}
}
async function cloudPush(){
  const c=cloudCfg();if(!c?.enabled||cloudBusy)return;cloudBusy=true;cloudState="syncing";cloudMessage="Enviando alterações...";
  try{
    if(!cloudVersion){try{const meta=await cloudRemoteVersion101102();cloudVersion=meta.version;cloudUpdatedAt=meta.updated_at;}catch{cloudVersion=0}}
    const rows=await cloudRpc("electronic_store_push",{p_sync_id:c.syncId,p_secret:c.secret,p_payload:db,p_expected_version:cloudVersion});
    const row=Array.isArray(rows)?rows[0]:rows;
    if(!row?.ok){await cloudPull(true);cloudState="online";cloudMessage="Havia uma alteração mais nova; revise e salve novamente";return;}
    cloudVersion=Number(row.version)||cloudVersion;cloudUpdatedAt=row.updated_at||"";cloudDirty=false;salvarCloudState101102();cloudState="online";cloudMessage="Alterações salvas na nuvem";
  }catch(e:any){cloudState="offline";cloudMessage=String(e?.message||"Falha na sincronização").slice(0,100);console.error("Cloud push:",e?.message||e)}finally{cloudBusy=false}
}
function agendarCloudPush(){if(cloudPushTimer)clearTimeout(cloudPushTimer);cloudPushTimer=setTimeout(()=>cloudPush(),350)}
const salvar = () => {fs.writeFileSync(dataFile, JSON.stringify(db, null, 2));cloudDirty=true;agendarCloudPush()};
async function iniciarCloud(){
  const c=cloudCfg();if(!c?.enabled)return;
  const ok=await cloudPull(true);
  if(!ok&&fs.existsSync(dataFile))await cloudPush();
}
'''
server = server[:start] + cloud + server[end:]
server = replace_once(
    server,
    'app.post("/api/cloud/sync",auth,async(_req,res)=>{const ok=await cloudPull(true);if(ok)await cloudPush();res.json({ok:cloudState==="online",state:cloudState,message:cloudMessage,version:cloudVersion})});',
    'app.post("/api/cloud/sync",auth,async(_req,res)=>{if(cloudDirty)await cloudPush();else await cloudPull(true);res.json({ok:cloudState==="online",state:cloudState,message:cloudMessage,version:cloudVersion,updatedAt:cloudUpdatedAt})});',
    "sincronização manual",
)
write("src/server.ts", server)

print("10.11.02: banco migrado para D1, consulta leve por versão e sincronização periódica removida.")
