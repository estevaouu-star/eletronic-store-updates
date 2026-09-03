from pathlib import Path
import json,re

root=Path("app")
def read(path): return (root/path).read_text(encoding="utf-8")
def write(path,value): (root/path).write_text(value,encoding="utf-8")

pkg=json.loads(read("package.json"));pkg["version"]="10.11.25";write("package.json",json.dumps(pkg,indent=2,ensure_ascii=False))
html=read("public/index.html");html,n=re.subn(r'(id="versionInfo" class="version-info">v)[0-9.]+',r'\g<1>10.11.25',html,count=1)
if n!=1: raise SystemExit("versão HTML não encontrada")
write("public/index.html",html)
js=read("public/app.js");js,n=re.subn(r'const atual="[0-9.]+"(?=,status=)','const atual="10.11.25"',js,count=1)
if n!=1: raise SystemExit("versão atualizador não encontrada")
write("public/app.js",js)

main=read("electron/main.cjs")
print_start=main.index('ipcMain.handle("printer:print"')
print_end=main.index("app.whenReady()",print_start)
print_before=main[print_start:print_end]
if '"printer:list"' in main or "'printer:list'" in main:
    raise SystemExit("printer:list já existe; interrompido para não duplicar")
list_handler=r'''ipcMain.handle("printer:list", async () => {
  if (!mainWindow || mainWindow.isDestroyed()) return [];
  try {
    const printers = await Promise.race([
      mainWindow.webContents.getPrintersAsync(),
      new Promise((_, reject) => setTimeout(() => reject(new Error("Tempo esgotado ao consultar impressoras.")), 6000))
    ]);
    return (Array.isArray(printers) ? printers : [])
      .filter(printer => !isVirtualPrinter101113(printer))
      .map(printer => ({
        name: String(printer.name || ""),
        displayName: String(printer.displayName || printer.name || ""),
        description: String(printer.description || ""),
        status: Number(printer.status || 0),
        isDefault: Boolean(printer.isDefault)
      }));
  } catch (error) {
    console.error("[printer:list]", error);
    return [];
  }
});

'''
main=main[:print_start]+list_handler+main[print_start:]
new_print_start=main.index('ipcMain.handle("printer:print"')
new_print_end=main.index("app.whenReady()",new_print_start)
if main[new_print_start:new_print_end] != print_before:
    raise SystemExit("ERRO: fluxo funcional de impressão foi alterado")
write("electron/main.cjs",main)
print("10.11.25: restaura exclusivamente a listagem de impressoras, com timeout, preservando impressão e layout.")
