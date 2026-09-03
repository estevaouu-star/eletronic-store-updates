from pathlib import Path
import json,re

root=Path("app")
def read(path): return (root/path).read_text(encoding="utf-8")
def write(path,value): (root/path).write_text(value,encoding="utf-8")

pkg=json.loads(read("package.json"))
if pkg.get("version")!="10.11.20": raise SystemExit(f"base incorreta: esperado 10.11.20, encontrado {pkg.get('version')}")
pkg["version"]="10.11.29"
write("package.json",json.dumps(pkg,indent=2,ensure_ascii=False))

html=read("public/index.html")
html,n=re.subn(r'(id="versionInfo" class="version-info">v)10\.11\.20',r'\g<1>10.11.29',html,count=1)
if n!=1: raise SystemExit("versão HTML 10.11.20 não encontrada")
write("public/index.html",html)

js=read("public/app.js")
js,n=re.subn(r'const atual="10\.11\.20"(?=,status=)','const atual="10.11.29"',js,count=1)
if n!=1: raise SystemExit("versão do atualizador 10.11.20 não encontrada")
write("public/app.js",js)

print("10.11.29: cópia funcional exata da 10.11.20; somente o número da versão foi alterado.")
