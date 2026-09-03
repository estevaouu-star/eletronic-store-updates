from pathlib import Path
import json,re

root=Path("app")
def read(path): return (root/path).read_text(encoding="utf-8")
def write(path,value): (root/path).write_text(value,encoding="utf-8")

pkg=json.loads(read("package.json"));pkg["version"]="10.11.27";write("package.json",json.dumps(pkg,indent=2,ensure_ascii=False))
html=read("public/index.html");html,n=re.subn(r'(id="versionInfo" class="version-info">v)[0-9.]+',r'\g<1>10.11.27',html,count=1)
if n!=1: raise SystemExit("versão HTML não encontrada")
write("public/index.html",html)
js=read("public/app.js");js,n=re.subn(r'const atual="[0-9.]+"(?=,status=)','const atual="10.11.27"',js,count=1)
if n!=1: raise SystemExit("versão atualizador não encontrada")

start=js.index("async function refreshPrinters(){")
end=js.index("function receiptPrintPayload()",start)
new_refresh=r'''async function refreshPrinters(){
  loadPrinterSettings();
  const select=$("#printerSelect"),status=$("#printerStatus");
  if(!select)return;
  select.innerHTML='<option value="">Carregando impressoras...</option>';
  if(!window.desktopPrinter){
    select.innerHTML='<option value="">Disponível somente no aplicativo Windows</option>';
    if(status)status.textContent="Abra o Eletromix instalado para impressão direta.";
    return;
  }
  const saved=String(printerSettings.deviceName||"").trim();
  const known=saved||"ELGIN i8 (copy 1)";
  try{
    const printers=await Promise.race([
      window.desktopPrinter.list(),
      new Promise((_,reject)=>setTimeout(()=>reject(new Error("A consulta do Windows demorou demais.")),12000))
    ]);
    if(!Array.isArray(printers)||!printers.length){
      printerSettings.deviceName=known;
      select.innerHTML=`<option value="${esc(known)}">${esc(known)} — configuração recuperada</option>`;
      select.value=known;
      if(status)status.textContent=`Impressora recuperada: ${known}.`;
      return;
    }
    const defaultPrinter=printers.find(p=>p.isDefault);
    if(!saved||!printers.some(p=>p.name===saved))printerSettings.deviceName=defaultPrinter?.name||printers.find(p=>/elgin.*i8|i8.*elgin/i.test(p.name||""))?.name||printers[0].name;
    select.innerHTML=printers.map(p=>`<option value="${esc(p.name)}">${esc(p.displayName||p.name)}${p.isDefault?" — padrão":""}</option>`).join("");
    select.value=printerSettings.deviceName;
    if(status)status.textContent=`Pronta: ${printers.find(p=>p.name===select.value)?.displayName||select.value}`;
  }catch(err){
    console.error(err);
    printerSettings.deviceName=known;
    select.innerHTML=`<option value="${esc(known)}">${esc(known)} — configuração recuperada</option>`;
    select.value=known;
    if(status)status.textContent=`Impressora recuperada após falha da listagem: ${known}.`;
  }
}

'''
js=js[:start]+new_refresh+js[end:]
write("public/app.js",js)

main=read("electron/main.cjs")
old='if(deviceName && (!available.some(p=>p.name===deviceName)||isVirtualPrinter101113({name:deviceName})))deviceName="";'
new='if(deviceName && isVirtualPrinter101113({name:deviceName}))deviceName="";\n  if(deviceName && available.length && !available.some(p=>p.name===deviceName))deviceName="";'
if old not in main: raise SystemExit("validação antiga do destino não encontrada")
main=main.replace(old,new,1)
old2='''  if(!deviceName){
    const preferred=available.find(p=>/elgin.*i8|i8.*elgin/i.test(`${p.name} ${p.displayName||""} ${p.description||""}`))||available.find(p=>/epson|bematech|elgin|daruma|control.?id|thermal|t[eé]rmica|receipt|pos|tm-|mp-|80|58/i.test(`${p.name} ${p.displayName||""} ${p.description||""}`))||available.find(p=>p.isDefault)||available[0];
    if(preferred)deviceName=preferred.name;
  }
'''
if old2 not in main: raise SystemExit("seleção automática não encontrada")
new2=old2.replace('    if(preferred)deviceName=preferred.name;','    if(preferred)deviceName=preferred.name;\n    else if(process.platform==="win32")deviceName="ELGIN i8 (copy 1)";')
main=main.replace(old2,new2,1)
write("electron/main.cjs",main)
print("10.11.27: encerra carregamento em 12s, recupera ELGIN salva e não descarta destino quando listagem falha.")
