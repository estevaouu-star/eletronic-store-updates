from pathlib import Path
import json,re

root=Path("app")
def read(path): return (root/path).read_text(encoding="utf-8")
def write(path,value): (root/path).write_text(value,encoding="utf-8")

pkg=json.loads(read("package.json"));pkg["version"]="10.11.22";write("package.json",json.dumps(pkg,indent=2,ensure_ascii=False))
html=read("public/index.html");html,n=re.subn(r'(id="versionInfo" class="version-info">v)[0-9.]+',r'\g<1>10.11.22',html,count=1)
if n!=1: raise SystemExit("versão HTML não encontrada")
write("public/index.html",html)
js=read("public/app.js");js,n=re.subn(r'const atual="[0-9.]+"(?=,status=)','const atual="10.11.22"',js,count=1)
if n!=1: raise SystemExit("versão atualizador não encontrada")
write("public/app.js",js)

main=read("electron/main.cjs")
pattern=r'''    if\(elginI8\)\{
      // A i8 tem área realmente imprimível menor que os 80 mm da bobina\.
.*?      await new Promise\(resolve=>setTimeout\(resolve,80\)\);
    \}

'''
replacement=r'''    if(elginI8){
      // Aplica somente CSS pela API do Electron. Nenhum script roda dentro do comprovante.
      await printWindow.webContents.insertCSS(String.raw`
        @page{margin:0!important}
        html,body{margin:0!important;padding:0!important;width:100%!important;background:#fff!important;color:#000!important}
        .receipt{position:relative!important;left:auto!important;right:auto!important;top:0!important;width:64mm!important;max-width:64mm!important;min-width:0!important;margin:0 auto!important;padding:2mm 1.5mm 3mm!important;box-sizing:border-box!important;transform:none!important;overflow:hidden!important;font-family:Arial,sans-serif!important;font-size:13px!important;line-height:1.34!important;color:#000!important}
        .receipt *{box-sizing:border-box!important;max-width:100%!important;color:#000!important}
        .receipt img{display:block!important;max-width:40mm!important;max-height:13mm!important;width:auto!important;height:auto!important;object-fit:contain!important;margin:0 auto 2mm!important}
        .receipt table{width:100%!important;max-width:100%!important;border-collapse:collapse!important;table-layout:fixed!important}
        .receipt th,.receipt td{min-width:0!important;padding:2px 1px!important;overflow-wrap:anywhere!important;vertical-align:top!important}
        .receipt th:last-child,.receipt td:last-child{text-align:right!important}
        .receipt h1,.receipt h2,.receipt h3{text-align:center!important;margin:3px 0!important;line-height:1.2!important}
        .receipt p{margin:2px 0!important}
      `);
      await new Promise(resolve=>setTimeout(resolve,50));
    }

'''
main,n=re.subn(pattern,lambda _m:replacement,main,count=1,flags=re.S)
if n!=1: raise SystemExit("script visual 10.11.21 não encontrado")
main=main.replace('mode:elginI8?"windows-elgin-i8-aligned":"windows"','mode:elginI8?"windows-elgin-i8-css-safe":"windows"',1)
write("electron/main.cjs",main)
print("10.11.22: alinhamento via insertCSS; remove executeJavaScript que bloqueava a impressão.")
