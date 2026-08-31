from pathlib import Path
import json, re

root = Path("app")
def read(path): return (root / path).read_text(encoding="utf-8")
def write(path, value): (root / path).write_text(value, encoding="utf-8")

pkg = json.loads(read("package.json"))
pkg["version"] = "10.11.14"
write("package.json", json.dumps(pkg, indent=2, ensure_ascii=False))

html = read("public/index.html")
html, count = re.subn(r'(id="versionInfo" class="version-info">v)[0-9.]+', r'\g<1>10.11.14', html, count=1)
if count != 1: raise SystemExit("versão do HTML não encontrada")
write("public/index.html", html)

js = read("public/app.js")
js, count = re.subn(r'const atual="[0-9.]+"(?=,status=)', 'const atual="10.11.14"', js, count=1)
if count != 1: raise SystemExit("versão do atualizador não encontrada")
js = js.replace(
    'if(status)status.textContent=`Trabalho enviado para ${r.deviceName||printerSettings.deviceName}${r.mode==="escpos"?" · térmico direto":""}.`;',
    'if(status)status.textContent=`Trabalho entregue ao driver de ${r.deviceName||printerSettings.deviceName}${r.mode==="escpos-fallback"?" · modo térmico de reserva":""}.`;',
    1,
)
write("public/app.js", js)

main = read("electron/main.cjs")
new_handler = r'''ipcMain.handle("printer:print", async (_event, payload = {}) => {
  const width = Number(payload.paperWidth) === 58 ? 58 : 80;
  let deviceName = String(payload.deviceName || "").trim();
  let available = [];
  try { available = mainWindow ? (await mainWindow.webContents.getPrintersAsync()).filter(p=>!isVirtualPrinter101113(p)) : []; } catch {}
  if(deviceName && (!available.some(p=>p.name===deviceName)||isVirtualPrinter101113({name:deviceName})))deviceName="";
  if(!deviceName){
    const preferred=available.find(p=>/elgin.*i8|i8.*elgin/i.test(`${p.name} ${p.displayName||""} ${p.description||""}`))||available.find(p=>/epson|bematech|elgin|daruma|control.?id|thermal|t[eé]rmica|receipt|pos|tm-|mp-|80|58/i.test(`${p.name} ${p.displayName||""} ${p.description||""}`))||available.find(p=>p.isDefault)||available[0];
    if(preferred)deviceName=preferred.name;
  }
  if(!deviceName)return {success:false,failureReason:"Nenhuma impressora física instalada foi encontrada neste computador."};
  if(thermalPrintBusy)return {success:false,failureReason:"Uma impressão já está em andamento.",deviceName,busy:true};
  thermalPrintBusy=true;
  const printWindow=getThermalRenderWindow();
  let rawFailure="";
  try{
    const html=receiptPrintHtml(String(payload.html||""),width);
    await printWindow.loadURL(`data:text/html;charset=utf-8,${encodeURIComponent(html)}`);
    await printWindow.webContents.executeJavaScript(`Promise.all(Array.from(document.images||[]).map(img=>img.complete?Promise.resolve():new Promise(r=>{img.onload=r;img.onerror=r}))).then(()=>true)`);
    await new Promise(resolve=>setTimeout(resolve,50));
    const receiptPx=await printWindow.webContents.executeJavaScript(`(()=>{const el=document.querySelector('.receipt');if(!el)return 0;return Math.max(el.getBoundingClientRect().height,el.scrollHeight||0)})()`);
    const measuredMm=Number(receiptPx||0)*25.4/96;
    const heightMm=Math.min(1000,Math.max(28,Math.ceil(measuredMm+3)));
    const selected=available.find(p=>p.name===deviceName);
    const elginI8=/elgin.*i8|i8.*elgin/i.test(`${selected?.name||deviceName} ${selected?.displayName||""} ${selected?.description||""}`);
    const printOptions=elginI8
      ? {silent:true,printBackground:true,deviceName,margins:{marginType:"none"}}
      : {silent:true,printBackground:true,deviceName,margins:{marginType:"none"},pageSize:{width:Math.round(width*1000),height:Math.round(heightMm*1000)}};
    const result=await new Promise(resolve=>{
      let settled=false;
      const finish=value=>{if(settled)return;settled=true;clearTimeout(timer);resolve(value)};
      const timer=setTimeout(()=>finish({success:false,failureReason:"O driver da impressora não respondeu em 15 segundos.",deviceName,paperWidth:width,mode:"windows-timeout"}),15000);
      try{printWindow.webContents.print(printOptions,(success,failureReason)=>finish({success,failureReason:failureReason||"",deviceName,paperWidth:width,paperLength:heightMm,mode:elginI8?"windows-elgin-i8":"windows"}))}
      catch(err){finish({success:false,failureReason:String(err?.message||err),deviceName,paperWidth:width,mode:"windows-error"})}
    });
    if(result.success)return result;

    // Reserva: só tenta ESC/POS quando o driver declarou falha ou expirou.
    if(process.platform==="win32" && !isVirtualPrinter101113({name:deviceName})){
      try{
        const rect=await printWindow.webContents.executeJavaScript(`(()=>{const el=document.querySelector('.receipt');if(!el)return null;const r=el.getBoundingClientRect();return {x:Math.max(0,Math.floor(r.x)),y:Math.max(0,Math.floor(r.y)),width:Math.max(1,Math.ceil(r.width)),height:Math.max(1,Math.ceil(r.height))}})()`);
        if(!rect)throw new Error("Área do comprovante não encontrada.");
        const image=await printWindow.webContents.capturePage(rect);
        await sendRawPrinterWindows(deviceName,receiptImageToEscPos(image,width));
        return {success:true,failureReason:"",deviceName,paperWidth:width,mode:"escpos-fallback",driverFailure:result.failureReason};
      }catch(err){rawFailure=String(err?.message||err)}
    }
    return {...result,rawFailure};
  }catch(err){
    console.error("[printer] Erro ao imprimir:",err);
    return {success:false,failureReason:String(err?.message||err),deviceName,rawFailure};
  }finally{thermalPrintBusy=false}
});'''

pattern=r'ipcMain\.handle\("printer:print", async \(_event, payload = \{\}\) => \{.*?\n\}\);(?=\n\napp\.whenReady\(\))'
main,count=re.subn(pattern,lambda _m:new_handler,main,count=1,flags=re.S)
if count!=1: raise SystemExit("handler de impressão não encontrado")
write("electron/main.cjs", main)
print("10.11.14: driver local da ELGIN i8 como principal; RAW somente após falha real do driver.")
