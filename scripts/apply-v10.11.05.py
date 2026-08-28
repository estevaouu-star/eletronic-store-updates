from pathlib import Path
import json,re
root=Path('app')
def read(p): return (root/p).read_text(encoding='utf-8')
def write(p,s): (root/p).write_text(s,encoding='utf-8')
pkg=json.loads(read('package.json'));pkg['version']='10.11.5';write('package.json',json.dumps(pkg,indent=2,ensure_ascii=False))
html=read('public/index.html');html,n=re.subn(r'(id="versionInfo" class="version-info">v)[0-9.]+',r'\g<1>10.11.05',html,count=1)
if n!=1: raise SystemExit('versao cabecalho nao encontrada')
write('public/index.html',html)
js=read('public/app.js');js,n=re.subn(r'const atual="[0-9.]+"(?=,status=)','const atual="10.11.5"',js,count=1)
if n!=1: raise SystemExit('versao atualizador nao encontrada')
write('public/app.js',js)
main=read('electron/main.cjs')
old='''    // MODO PRINCIPAL: rasteriza somente o comprovante e envia bytes ESC/POS diretamente à fila RAW.
    // Isso ignora por completo o tamanho de página/formulário do driver do Windows, que era a origem
    // do avanço enorme de papel em algumas impressoras térmicas.
    if(process.platform==="win32" && !/pdf|xps|onenote|fax/i.test(deviceName)){'''
new='''    // ELGIN i8: alguns drivers aceitam o job RAW sem erro, mas nao imprimem o raster ESC/POS.
    // Na i8, usa primeiro o driver do Windows. Outras termicas continuam no RAW rapido.
    const printerMeta=available.find(p=>p.name===deviceName);
    const printerLabel=`${deviceName} ${printerMeta?.displayName||""} ${printerMeta?.description||""}`;
    const elginI8=/elgin.*\\bi[- ]?8\\b|\\bi[- ]?8\\b.*elgin/i.test(printerLabel);
    if(process.platform==="win32" && !elginI8 && !/pdf|xps|onenote|fax/i.test(deviceName)){'''
if old not in main: raise SystemExit('bloco RAW nao encontrado')
main=main.replace(old,new,1)
old2='''    const result=await new Promise(resolve=>{
      printWindow.webContents.print({silent:true,printBackground:true,deviceName,margins:{marginType:"none"},pageSize:{width:Math.round(width*1000),height:Math.round(heightMm*1000)}},(success,failureReason)=>resolve({success,failureReason:failureReason||"",deviceName,paperWidth:width,paperLength:heightMm,mode:"windows",rawFailure}));
    });
    return result;'''
new2='''    const result=await new Promise(resolve=>{
      printWindow.webContents.print({silent:true,printBackground:true,deviceName,margins:{marginType:"none"},pageSize:{width:Math.round(width*1000),height:Math.round(heightMm*1000)}},(success,failureReason)=>resolve({success,failureReason:failureReason||"",deviceName,paperWidth:width,paperLength:heightMm,mode:elginI8?"windows-elgin-i8":"windows",rawFailure}));
    });
    if(elginI8 && !result.success){
      const retry=await new Promise(resolve=>{
        printWindow.webContents.print({silent:true,printBackground:true,deviceName,margins:{marginType:"none"}},(success,failureReason)=>resolve({success,failureReason:failureReason||"",deviceName,paperWidth:width,mode:"windows-elgin-i8-driver",rawFailure:String(result.failureReason||rawFailure||"")}));
      });
      return retry;
    }
    return result;'''
if old2 not in main: raise SystemExit('fallback Windows nao encontrado')
main=main.replace(old2,new2,1)
write('electron/main.cjs',main)
print('10.11.05: ELGIN i8 usa driver Windows primeiro e tenta preferencias nativas se necessario.')
