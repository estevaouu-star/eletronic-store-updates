from pathlib import Path
import json, re

root = Path("app")
def read(path): return (root / path).read_text(encoding="utf-8")
def write(path, value): (root / path).write_text(value, encoding="utf-8")

pkg = json.loads(read("package.json"))
pkg["version"] = "10.11.15"
write("package.json", json.dumps(pkg, indent=2, ensure_ascii=False))

html = read("public/index.html")
html, count = re.subn(r'(id="versionInfo" class="version-info">v)[0-9.]+', r'\g<1>10.11.15', html, count=1)
if count != 1: raise SystemExit("versão do HTML não encontrada")
write("public/index.html", html)

js = read("public/app.js")
js, count = re.subn(r'const atual="[0-9.]+"(?=,status=)', 'const atual="10.11.15"', js, count=1)
if count != 1: raise SystemExit("versão do atualizador não encontrada")
js = js.replace(
    'if(status)status.textContent=`Trabalho entregue ao driver de ${r.deviceName||printerSettings.deviceName}${r.mode==="escpos-fallback"?" · modo térmico de reserva":""}.`; ',
    'if(status)status.textContent=`Comprovante enviado em 80 mm para ${r.deviceName||printerSettings.deviceName}.`; ',
    1,
)
write("public/app.js", js)

main = read("electron/main.cjs")
old = '''    const printOptions=elginI8
      ? {silent:true,printBackground:true,deviceName,margins:{marginType:"none"}}
      : {silent:true,printBackground:true,deviceName,margins:{marginType:"none"},pageSize:{width:Math.round(width*1000),height:Math.round(heightMm*1000)}};'''
new = '''    // A ELGIN i8 também precisa receber uma página térmica explícita. Sem isso o spooler
    // aceita o trabalho usando o tamanho padrão do driver, mas a impressora não avança o papel.
    const printOptions={
      silent:true,
      printBackground:true,
      deviceName,
      margins:{marginType:"none"},
      pageSize:{width:Math.round(width*1000),height:Math.round(heightMm*1000)},
      landscape:false,
      scaleFactor:100,
      pagesPerSheet:1,
      collate:false,
      copies:1
    };'''
if old not in main: raise SystemExit("opções da ELGIN i8 da 10.11.14 não encontradas")
main = main.replace(old, new, 1)
main = main.replace('mode:elginI8?"windows-elgin-i8":"windows"', 'mode:elginI8?"windows-elgin-i8-80mm":"windows"', 1)
write("electron/main.cjs", main)
print("10.11.15: ELGIN i8 recebe papel térmico explícito de 80 mm e altura medida do comprovante.")
