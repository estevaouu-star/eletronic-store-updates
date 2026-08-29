from pathlib import Path
import json,re

root=Path('app')
def read(p): return (root/p).read_text(encoding='utf-8')
def write(p,s): (root/p).write_text(s,encoding='utf-8')

pkg=json.loads(read('package.json'));pkg['version']='10.11.9';write('package.json',json.dumps(pkg,indent=2,ensure_ascii=False))
html=read('public/index.html');html,n=re.subn(r'(id="versionInfo" class="version-info">v)[0-9.]+',r'\g<1>10.11.09',html,count=1)
if n!=1: raise SystemExit('versao html nao encontrada')
write('public/index.html',html)
js=read('public/app.js');js,n=re.subn(r'const atual="[0-9.]+"(?=,status=)','const atual="10.11.9"',js,count=1)
if n!=1: raise SystemExit('versao atualizador nao encontrada')
write('public/app.js',js)

main=read('electron/main.cjs')
start=main.find('async function sendElginI8DirectWindows(bytes){')
end=main.find('\nasync function sendRawPrinterWindows(deviceName,bytes){',start)
if start<0 or end<0: raise SystemExit('ponte COM da ELGIN i8 nao encontrada')
main=main[:start]+main[end+1:]

direct=r'''    // Primeiro tenta comunicacao direta pela Virtual COM da i8, caminho comum em PDVs.
    if(process.platform==="win32" && elginI8){
      try{
        const rect=await printWindow.webContents.executeJavaScript(`(()=>{const el=document.querySelector('.receipt');if(!el)return null;const r=el.getBoundingClientRect();return {x:Math.max(0,Math.floor(r.x)),y:Math.max(0,Math.floor(r.y)),width:Math.max(1,Math.ceil(r.width)),height:Math.max(1,Math.ceil(r.height))}})()`);
        if(rect){const image=await printWindow.webContents.capturePage(rect);const raw=receiptImageToEscPos(image,width);const direct=await sendElginI8DirectWindows(raw);return {success:true,failureReason:"",deviceName,paperWidth:width,mode:"elgin-i8-com",port:direct.port};}
      }catch(err){rawFailure=String(err?.message||err);console.error("[printer] ELGIN i8 direta falhou; tentando driver Windows:",rawFailure)}
    }
'''
if direct not in main: raise SystemExit('chamada COM da ELGIN i8 nao encontrada')
main=main.replace(direct,'',1)

old=r'''    const result=await new Promise(resolve=>{
      printWindow.webContents.print({silent:true,printBackground:true,deviceName,margins:{marginType:"none"},pageSize:{width:Math.round(width*1000),height:Math.round(heightMm*1000)}},(success,failureReason)=>resolve({success,failureReason:failureReason||"",deviceName,paperWidth:width,paperLength:heightMm,mode:elginI8?"windows-elgin-i8":"windows",rawFailure}));
    });
    if(elginI8 && !result.success){
      const retry=await new Promise(resolve=>{
        printWindow.webContents.print({silent:true,printBackground:true,deviceName,margins:{marginType:"none"}},(success,failureReason)=>resolve({success,failureReason:failureReason||"",deviceName,paperWidth:width,mode:"windows-elgin-i8-driver",rawFailure:String(result.failureReason||rawFailure||"")}));
      });
      return retry;
    }
    return result;'''
new=r'''    // ELGIN i8: uma unica chamada ao driver instalado no Windows. Nao procura portas COM,
    // nao cria PowerShell por clique e nao repete o trabalho silenciosamente.
    const printOptions=elginI8
      ? {silent:true,printBackground:true,deviceName,margins:{marginType:"none"}}
      : {silent:true,printBackground:true,deviceName,margins:{marginType:"none"},pageSize:{width:Math.round(width*1000),height:Math.round(heightMm*1000)}};
    const result=await new Promise(resolve=>{
      let settled=false;
      const finish=value=>{if(settled)return;settled=true;clearTimeout(timer);resolve(value)};
      const timer=setTimeout(()=>finish({success:false,failureReason:"A ELGIN i8 não respondeu em 12 segundos. O envio foi cancelado para não travar o aplicativo.",deviceName,paperWidth:width,mode:"windows-timeout",rawFailure}),12000);
      try{
        printWindow.webContents.print(printOptions,(success,failureReason)=>finish({success,failureReason:failureReason||"",deviceName,paperWidth:width,paperLength:heightMm,mode:elginI8?"windows-elgin-i8-safe":"windows",rawFailure}));
      }catch(err){finish({success:false,failureReason:String(err?.message||err),deviceName,paperWidth:width,mode:"windows-error",rawFailure})}
    });
    return result;'''
if old not in main: raise SystemExit('fallback de impressao da ELGIN i8 nao encontrado')
main=main.replace(old,new,1)
write('electron/main.cjs',main)
print('10.11.09: ELGIN i8 sem varredura COM, com envio unico pelo driver e limite de 12 segundos.')
