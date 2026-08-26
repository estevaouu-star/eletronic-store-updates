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
write("public/app.js", js)

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
write("src/server.ts", server)

print("10.11.03: sincronização GZIP de ponta a ponta, banco compactado e alterações agrupadas.")
