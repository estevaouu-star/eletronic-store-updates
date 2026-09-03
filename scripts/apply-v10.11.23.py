from pathlib import Path
import json,re

root=Path("app")
def read(path): return (root/path).read_text(encoding="utf-8")
def write(path,value): (root/path).write_text(value,encoding="utf-8")

pkg=json.loads(read("package.json"));pkg["version"]="10.11.23";write("package.json",json.dumps(pkg,indent=2,ensure_ascii=False))
html=read("public/index.html");html,n=re.subn(r'(id="versionInfo" class="version-info">v)[0-9.]+',r'\g<1>10.11.23',html,count=1)
if n!=1: raise SystemExit("versão HTML não encontrada")
write("public/index.html",html)
js=read("public/app.js");js,n=re.subn(r'const atual="[0-9.]+"(?=,status=)','const atual="10.11.23"',js,count=1)
if n!=1: raise SystemExit("versão atualizador não encontrada")
write("public/app.js",js)

main=read("electron/main.cjs")
pattern=r'''    if\(elginI8\)\{
      // Aplica somente CSS pela API do Electron\. Nenhum script roda dentro do comprovante\.
.*?      await new Promise\(resolve=>setTimeout\(resolve,50\)\);
    \}

'''
main,n=re.subn(pattern,"",main,count=1,flags=re.S)
if n!=1: raise SystemExit("bloco visual 10.11.22 não encontrado")
main=main.replace('mode:elginI8?"windows-elgin-i8-css-safe":"windows"','mode:elginI8?"windows-elgin-i8-driver-native-restored":"windows"',1)
write("electron/main.cjs",main)
print("10.11.23: remove integralmente os ajustes 10.11.21/22 e restaura o fluxo funcional da 10.11.20.")
