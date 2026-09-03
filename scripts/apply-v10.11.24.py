from pathlib import Path
import json,re

root=Path("app")
def read(path): return (root/path).read_text(encoding="utf-8")
def write(path,value): (root/path).write_text(value,encoding="utf-8")

pkg=json.loads(read("package.json"));pkg["version"]="10.11.24";write("package.json",json.dumps(pkg,indent=2,ensure_ascii=False))
html=read("public/index.html");html,n=re.subn(r'(id="versionInfo" class="version-info">v)[0-9.]+',r'\g<1>10.11.24',html,count=1)
if n!=1: raise SystemExit("versão HTML não encontrada")
write("public/index.html",html)
js=read("public/app.js");js,n=re.subn(r'const atual="[0-9.]+"(?=,status=)','const atual="10.11.24"',js,count=1)
if n!=1: raise SystemExit("versão atualizador não encontrada")
write("public/app.js",js)

main=read("electron/main.cjs")
handler_start=main.index('ipcMain.handle("printer:print"')
handler_end=main.index("app.whenReady()",handler_start)
handler_before=main[handler_start:handler_end]

start=main.index("function receiptPrintHtml")
end=main.index("function receiptImageToEscPos",start)
new_func=r'''function receiptPrintHtml(bodyHtml, paperWidth) {
  const width = paperWidth === 58 ? 58 : 80;
  // Margem conservadora para o driver ELGIN i8: evita corte no lado direito.
  const inner = width === 58 ? 44 : 60;
  let content = String(bodyHtml || "");
  // Alguns modelos antigos incluem a despedida duas vezes.
  let thanksSeen = false;
  content = content.replace(/Obrigado pela prefer(?:ê|e)ncia!?/gi, (text) => {
    if (thanksSeen) return "";
    thanksSeen = true;
    return text;
  });
  return `<!doctype html><html><head><meta charset="utf-8"><style>
    @page{margin:0!important}
    *{box-sizing:border-box}
    html,body{margin:0!important;padding:0!important;background:#fff;color:#000;width:${width}mm;overflow:hidden}
    body{font-family:Arial,Helvetica,sans-serif;font-size:${width===58?11:12}px;line-height:1.3}
    .receipt{width:${inner}mm!important;max-width:${inner}mm!important;margin:0 auto!important;padding:3mm 0!important;overflow:hidden}
    .receipt h2{font-size:${width===58?16:18}px;margin:0 0 4px;text-align:center;line-height:1.15}
    .receipt p{text-align:center;margin:3px 0;overflow-wrap:anywhere}
    .receipt-logo{display:none!important}
    table{width:100%!important;max-width:100%!important;table-layout:fixed;border-collapse:collapse;margin:5px 0}
    th,td{font-size:${width===58?10:11}px;padding:4px 1px;border-bottom:1px dashed #777;text-align:left;vertical-align:top;overflow-wrap:anywhere}
    th:first-child,td:first-child{width:auto}
    th:nth-child(2),td:nth-child(2){width:${width===58?8:9}mm;text-align:center;white-space:nowrap}
    th:last-child,td:last-child{width:${width===58?15:18}mm;text-align:right;white-space:nowrap}
    .receipt-total{display:flex;justify-content:space-between;align-items:baseline;gap:5px;font-size:${width===58?15:17}px;font-weight:700;border-top:1px dashed #000;margin-top:6px;padding-top:6px}
    .receipt-total>*:last-child{white-space:nowrap}
    .receipt-kicker{text-align:center;font-size:9px;font-weight:700;letter-spacing:.08em;margin:4px 0}
    .receipt-doc-number{text-align:center;font-size:${width===58?14:16}px;font-weight:900;margin:3px 0 6px}
    .receipt-section{margin-top:7px;padding-top:6px;border-top:1px dashed #555}
    .receipt-section-title{font-size:9px;font-weight:900;letter-spacing:.08em;margin-bottom:4px}
    .receipt-row{display:flex;align-items:flex-start;gap:4px;padding:2px 0;font-size:${width===58?10:11}px;min-width:0}
    .receipt-row span:first-child{flex:0 0 ${width===58?15:19}mm;color:#333}
    .receipt-row b{flex:1;min-width:0;text-align:right;overflow-wrap:anywhere}
    .receipt-text{font-size:${width===58?10:11}px;line-height:1.35;white-space:normal;overflow-wrap:anywhere}
    .receipt-emphasis{margin-top:7px;padding:6px 4px;border:1px solid #000}
    .receipt-emphasis .receipt-row{font-size:${width===58?12:13}px}
    .receipt-signature{margin:18px auto 0;width:78%;padding-top:4px;border-top:1px solid #000;text-align:center;font-size:9px}
    .receipt-note{margin-top:7px!important;font-size:9px!important;line-height:1.3}
    .receipt-items td:first-child{overflow-wrap:anywhere}
    .receipt-payment{padding:3px 0;border-bottom:1px dotted #999}
    .receipt-payment:last-child{border-bottom:0}
  </style></head><body>${content}</body></html>`;
}

'''
main=main[:start]+new_func+main[end:]
handler_after=main[main.index('ipcMain.handle("printer:print"'):main.index("app.whenReady()",main.index('ipcMain.handle("printer:print"'))]
if handler_after!=handler_before: raise SystemExit("ERRO: fluxo funcional de impressão foi alterado")
write("electron/main.cjs",main)
print("10.11.24: corrige somente o layout do comprovante e preserva integralmente o envio funcional da 10.11.20.")
