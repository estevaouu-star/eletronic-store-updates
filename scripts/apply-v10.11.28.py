from pathlib import Path
import json,re

root=Path("app")
def read(path): return (root/path).read_text(encoding="utf-8")
def write(path,value): (root/path).write_text(value,encoding="utf-8")

pkg=json.loads(read("package.json"));pkg["version"]="10.11.28";write("package.json",json.dumps(pkg,indent=2,ensure_ascii=False))
html=read("public/index.html");html,n=re.subn(r'(id="versionInfo" class="version-info">v)[0-9.]+',r'\g<1>10.11.28',html,count=1)
if n!=1: raise SystemExit("versão HTML não encontrada")
write("public/index.html",html)
js=read("public/app.js");js,n=re.subn(r'const atual="[0-9.]+"(?=,status=)','const atual="10.11.28"',js,count=1)
if n!=1: raise SystemExit("versão atualizador não encontrada")
write("public/app.js",js)

main=read("electron/main.cjs")
anchor="async function getPhysicalPrinters101126(){"
if anchor not in main: raise SystemExit("âncora da detecção não encontrada")
predicate=r'''function isVirtualPrinter101128(printer){
  const text=`${printer?.name||""} ${printer?.displayName||""} ${printer?.description||""}`.toLowerCase();
  return /microsoft print to pdf|print to pdf|onenote|one note|notas|xps|document writer|fax/.test(text);
}

'''
main=main.replace(anchor,predicate+anchor,1)
main=main.replace("isVirtualPrinter101113(","isVirtualPrinter101128(")
if "isVirtualPrinter101113(" in main: raise SystemExit("referência indefinida permaneceu")
write("electron/main.cjs",main)
print("10.11.28: elimina ReferenceError e valida impressoras com função autocontida.")
