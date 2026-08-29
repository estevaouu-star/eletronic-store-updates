from pathlib import Path
import json,re

root=Path('app')
def read(p): return (root/p).read_text(encoding='utf-8')
def write(p,s): (root/p).write_text(s,encoding='utf-8')

pkg=json.loads(read('package.json'));pkg['version']='10.11.11';write('package.json',json.dumps(pkg,indent=2,ensure_ascii=False))
html=read('public/index.html');html,n=re.subn(r'(id="versionInfo" class="version-info">v)[0-9.]+',r'\g<1>10.11.11',html,count=1)
if n!=1: raise SystemExit('versao html nao encontrada')
write('public/index.html',html)

js=read('public/app.js');js,n=re.subn(r'const atual="[0-9.]+"(?=,status=)','const atual="10.11.11"',js,count=1)
if n!=1: raise SystemExit('versao atualizador nao encontrada')
js=js.replace('toast(r?.success?"Teste impresso com sucesso.":`Falha no teste: ${r?.failureReason||"erro"}`);','toast(r?.success?"Teste enviado diretamente para a ELGIN i8.":`Falha no teste: ${r?.failureReason||"erro"}`);',1)
write('public/app.js',js)

main=read('electron/main.cjs')
old='''    const printers = await mainWindow.webContents.getPrintersAsync();
    return printers.map(p => ({'''
new='''    const printers = (await mainWindow.webContents.getPrintersAsync()).filter(p=>!isVirtualPrinter101111(p));
    return printers.map(p => ({'''
if old not in main: raise SystemExit('listagem de impressoras nao encontrada')
main=main.replace(old,new,1)

anchor='''ipcMain.handle("printer:list", async () => {'''
helper='''function isVirtualPrinter101111(printer){
  const label=`${printer?.name||""} ${printer?.displayName||""} ${printer?.description||""}`;
  return /onenote|one note|notas|bloco de notas|notepad|pdf|xps|fax|microsoft print|send to/i.test(label);
}

'''
if anchor not in main: raise SystemExit('handler printer:list nao encontrado')
main=main.replace(anchor,helper+anchor,1)

old2='''  try { available = mainWindow ? await mainWindow.webContents.getPrintersAsync() : []; } catch {}
  if(deviceName && !available.some(p=>p.name===deviceName))deviceName="";'''
new2='''  try { available = mainWindow ? (await mainWindow.webContents.getPrintersAsync()).filter(p=>!isVirtualPrinter101111(p)) : []; } catch {}
  if(deviceName && (!available.some(p=>p.name===deviceName)||isVirtualPrinter101111({name:deviceName})))deviceName="";'''
if old2 not in main: raise SystemExit('selecao de impressora nao encontrada')
main=main.replace(old2,new2,1)

old3='if(process.platform==="win32" && !elginI8 && !/pdf|xps|onenote|fax/i.test(deviceName)){' 
new3='if(process.platform==="win32" && !/pdf|xps|onenote|fax|notas|notepad/i.test(deviceName)){' 
if old3 not in main: raise SystemExit('exclusao RAW da ELGIN i8 nao encontrada')
main=main.replace(old3,new3,1)
write('electron/main.cjs',main)
print('10.11.11: ELGIN i8 usa ESC/POS RAW; Notas, OneNote, PDF e outras impressoras virtuais ficam bloqueadas.')
