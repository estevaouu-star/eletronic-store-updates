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
raw_first = r'''    // MODO PRINCIPAL: rasteriza somente o comprovante e envia bytes ESC/POS diretamente à fila RAW.
    // Isso ignora por completo o tamanho de página/formulário do driver do Windows, que era a origem
    // do avanço enorme de papel em algumas impressoras térmicas.
    if(process.platform==="win32" && !isVirtualPrinter101113({name:deviceName})){
      try{
        const rect=await printWindow.webContents.executeJavaScript(`(()=>{
          const el=document.querySelector('.receipt');if(!el)return null;
          const st=document.createElement('style');st.textContent='html,body{margin:0!important;padding:0!important;min-height:0!important;height:auto!important;overflow:hidden!important}.receipt{position:relative!important;top:0!important;margin:0!important;transform:none!important}';document.head.appendChild(st);
          const r=el.getBoundingClientRect();return {x:Math.max(0,Math.floor(r.x)),y:Math.max(0,Math.floor(r.y)),width:Math.max(1,Math.ceil(r.width)),height:Math.max(1,Math.ceil(r.height))};
        })()`);
        if(!rect)throw new Error("Área do comprovante não encontrada.");
        const image=await printWindow.webContents.capturePage(rect);
        const raw=receiptImageToEscPos(image,width);
        await sendRawPrinterWindows(deviceName,raw);
        return {success:true,failureReason:"",deviceName,paperWidth:width,mode:"escpos"};
      }catch(err){
        rawFailure=String(err?.message||err);
        console.error("[printer] Modo térmico direto falhou; usando fallback do Windows:",rawFailure);
      }
    }

    // Fallback para impressoras que não aceitam ESC/POS RAW.
'''
driver_first = r'''    // 10.11.14: o driver instalado no próprio computador volta a ser o caminho principal.
    // O modo RAW pode aceitar o trabalho sem que a ELGIN i8 mova o papel; por isso ele fica só como reserva.
'''
if raw_first not in main: raise SystemExit("bloco RAW principal não encontrado")
main = main.replace(raw_first, driver_first, 1)

old_driver = r'''    const result=await new Promise(resolve=>{
      printWindow.webContents.print({silent:true,printBackground:true,deviceName,margins:{marginType:"none"},pageSize:{width:Math.round(width*1000),height:Math.round(heightMm*1000)}},(success,failureReason)=>resolve({success,failureReason:failureReason||"",deviceName,paperWidth:width,paperLength:heightMm,mode:"windows",rawFailure}));
    });
    return result;'''
new_driver = r'''    const elginI8=/elgin.*i8|i8.*elgin/i.test(available.find(p=>p.name===deviceName)?.displayName||deviceName);
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
    return {...result,rawFailure};'''
if old_driver not in main: raise SystemExit("bloco do driver não encontrado")
main = main.replace(old_driver, new_driver, 1)
write("electron/main.cjs", main)
print("10.11.14: driver local da ELGIN i8 como principal; RAW somente após falha real do driver.")
