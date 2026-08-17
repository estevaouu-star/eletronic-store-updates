from pathlib import Path
import json

root=Path('app')
def read(p): return (root/p).read_text(encoding='utf-8')
def write(p,s): (root/p).write_text(s,encoding='utf-8')

pkg=json.loads(read('package.json'))
pkg['version']='10.7.9'
write('package.json',json.dumps(pkg,indent=2,ensure_ascii=False))

html=read('public/index.html')
html=html.replace('id="versionInfo" class="version-info">v10.7.8','id="versionInfo" class="version-info">v10.7.9')
html=html.replace('Comprimento: automático, começando no topo e terminando logo após o conteúdo','Comprimento: automático · modo térmico direto, sem página em branco do driver')
write('public/index.html',html)

js=read('public/app.js')
js=js.replace('const atual="10.7.8"','const atual="10.7.9"')
js=js.replace('if(status)status.textContent=`Impresso em ${r.deviceName||printerSettings.deviceName}.`;','if(status)status.textContent=`Impresso em ${r.deviceName||printerSettings.deviceName}${r.mode==="escpos"?" · térmico direto":""}.`;')
write('public/app.js',js)

main=read('electron/main.cjs')
start=main.find('ipcMain.handle("printer:print", async (_event, payload = {}) => {')
end=main.find('\n\napp.whenReady()',start)
if start<0 or end<0: raise RuntimeError('Handler printer:print não encontrado')

handler=r'''function receiptImageToEscPos(image,paperWidth){
  // Larguras comuns em cabeças térmicas 203 dpi: 576 pontos (80 mm) e 384 (58 mm).
  const targetWidth = Number(paperWidth)===58 ? 384 : 576;
  const source=image.getSize();
  if(!source.width||!source.height)throw new Error("Não foi possível rasterizar o comprovante.");
  const targetHeight=Math.max(1,Math.round(source.height*targetWidth/source.width));
  const resized=image.resize({width:targetWidth,height:targetHeight,quality:"best"});
  const bitmap=resized.toBitmap();
  const rowBytes=Math.ceil(targetWidth/8);
  const raster=Buffer.alloc(rowBytes*targetHeight,0);
  // Dither leve para preservar a logo e manter texto nítido em impressão monocromática.
  const bayer=[0,8,2,10,12,4,14,6,3,11,1,9,15,7,13,5];
  for(let y=0;y<targetHeight;y++){
    for(let x=0;x<targetWidth;x++){
      const i=(y*targetWidth+x)*4;
      const b=bitmap[i]??255,g=bitmap[i+1]??255,r=bitmap[i+2]??255,a=bitmap[i+3]??255;
      const lum=(r*299+g*587+b*114)/1000;
      const threshold=176+(bayer[(y%4)*4+(x%4)]-7.5)*4;
      if(a>24 && lum<threshold)raster[y*rowBytes+(x>>3)]|=(0x80>>(x&7));
    }
  }
  const xL=rowBytes&255,xH=(rowBytes>>8)&255,yL=targetHeight&255,yH=(targetHeight>>8)&255;
  // ESC @ inicializa; GS L zera margem; GS v 0 imprime o bitmap; ESC d 2 deixa só o avanço mínimo para destacar/cortar.
  return Buffer.concat([
    Buffer.from([0x1b,0x40,0x1d,0x4c,0x00,0x00,0x1b,0x61,0x00]),
    Buffer.from([0x1d,0x76,0x30,0x00,xL,xH,yL,yH]),
    raster,
    Buffer.from([0x1b,0x64,0x02])
  ]);
}

async function sendRawPrinterWindows(deviceName,bytes){
  const fs=require("fs"),os=require("os"),pathLocal=require("path");
  const {execFile}=require("child_process");
  const id=`${process.pid}-${Date.now()}-${Math.random().toString(16).slice(2)}`;
  const bin=pathLocal.join(os.tmpdir(),`eletromix-print-${id}.bin`);
  const ps1=pathLocal.join(os.tmpdir(),`eletromix-print-${id}.ps1`);
  const script=String.raw`param([string]$PrinterName,[string]$FilePath)
$ErrorActionPreference='Stop'
Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
public static class RawPrinter {
  [StructLayout(LayoutKind.Sequential, CharSet=CharSet.Unicode)]
  public struct DOC_INFO_1 { public string pDocName; public string pOutputFile; public string pDataType; }
  [DllImport("winspool.drv", SetLastError=true, CharSet=CharSet.Unicode)] public static extern bool OpenPrinter(string pPrinterName,out IntPtr phPrinter,IntPtr pDefault);
  [DllImport("winspool.drv", SetLastError=true)] public static extern bool ClosePrinter(IntPtr hPrinter);
  [DllImport("winspool.drv", SetLastError=true, CharSet=CharSet.Unicode)] public static extern int StartDocPrinter(IntPtr hPrinter,int Level,ref DOC_INFO_1 pDocInfo);
  [DllImport("winspool.drv", SetLastError=true)] public static extern bool EndDocPrinter(IntPtr hPrinter);
  [DllImport("winspool.drv", SetLastError=true)] public static extern bool StartPagePrinter(IntPtr hPrinter);
  [DllImport("winspool.drv", SetLastError=true)] public static extern bool EndPagePrinter(IntPtr hPrinter);
  [DllImport("winspool.drv", SetLastError=true)] public static extern bool WritePrinter(IntPtr hPrinter,byte[] pBytes,int dwCount,out int dwWritten);
}
"@
$bytes=[IO.File]::ReadAllBytes($FilePath)
$h=[IntPtr]::Zero
if(-not [RawPrinter]::OpenPrinter($PrinterName,[ref]$h,[IntPtr]::Zero)){throw "OpenPrinter falhou: $([Runtime.InteropServices.Marshal]::GetLastWin32Error())"}
$docStarted=$false;$pageStarted=$false
try {
  $doc=New-Object 'RawPrinter+DOC_INFO_1'
  $doc.pDocName='Eletromix - Comprovante';$doc.pOutputFile=$null;$doc.pDataType='RAW'
  if([RawPrinter]::StartDocPrinter($h,1,[ref]$doc)-le 0){throw "StartDocPrinter falhou: $([Runtime.InteropServices.Marshal]::GetLastWin32Error())"}
  $docStarted=$true
  if(-not [RawPrinter]::StartPagePrinter($h)){throw "StartPagePrinter falhou: $([Runtime.InteropServices.Marshal]::GetLastWin32Error())"}
  $pageStarted=$true
  [int]$written=0
  if(-not [RawPrinter]::WritePrinter($h,$bytes,$bytes.Length,[ref]$written)){throw "WritePrinter falhou: $([Runtime.InteropServices.Marshal]::GetLastWin32Error())"}
  if($written-ne $bytes.Length){throw "Impressão RAW incompleta: $written de $($bytes.Length) bytes"}
} finally {
  if($pageStarted){[RawPrinter]::EndPagePrinter($h)|Out-Null}
  if($docStarted){[RawPrinter]::EndDocPrinter($h)|Out-Null}
  if($h-ne [IntPtr]::Zero){[RawPrinter]::ClosePrinter($h)|Out-Null}
}
Write-Output 'OK'
`;
  fs.writeFileSync(bin,bytes);
  fs.writeFileSync(ps1,script,{encoding:"utf8"});
  try{
    await new Promise((resolve,reject)=>{
      execFile("powershell.exe",["-NoLogo","-NoProfile","-NonInteractive","-ExecutionPolicy","Bypass","-File",ps1,deviceName,bin],{windowsHide:true,timeout:20000},(err,stdout,stderr)=>{
        if(err)return reject(new Error(String(stderr||stdout||err.message||err)));
        resolve();
      });
    });
  }finally{
    try{fs.unlinkSync(bin)}catch{}
    try{fs.unlinkSync(ps1)}catch{}
  }
}

ipcMain.handle("printer:print", async (_event, payload = {}) => {
  const width = Number(payload.paperWidth) === 58 ? 58 : 80;
  let deviceName = String(payload.deviceName || "").trim();
  let available = [];
  try { available = mainWindow ? await mainWindow.webContents.getPrintersAsync() : []; } catch {}
  if(deviceName && !available.some(p=>p.name===deviceName))deviceName="";
  if(!deviceName){
    const preferred=available.find(p=>/epson|bematech|elgin|daruma|control.?id|thermal|t[eé]rmica|receipt|pos|tm-|mp-|80|58/i.test(`${p.name} ${p.displayName||""} ${p.description||""}`))||available.find(p=>p.isDefault)||available[0];
    if(preferred)deviceName=preferred.name;
  }
  if(!deviceName)return {success:false,failureReason:"Nenhuma impressora instalada foi encontrada pelo Windows."};

  const printWindow = new BrowserWindow({show:false,width:520,height:900,webPreferences:{contextIsolation:true,sandbox:true}});
  let rawFailure="";
  try{
    const html=receiptPrintHtml(String(payload.html||""),width);
    await printWindow.loadURL(`data:text/html;charset=utf-8,${encodeURIComponent(html)}`);
    await printWindow.webContents.executeJavaScript(`Promise.all(Array.from(document.images||[]).map(img=>img.complete?Promise.resolve():new Promise(r=>{img.onload=r;img.onerror=r}))).then(()=>true)`);
    await new Promise(resolve=>setTimeout(resolve,160));

    // MODO PRINCIPAL: rasteriza somente o comprovante e envia bytes ESC/POS diretamente à fila RAW.
    // Isso ignora por completo o tamanho de página/formulário do driver do Windows, que era a origem
    // do avanço enorme de papel em algumas impressoras térmicas.
    if(process.platform==="win32" && !/pdf|xps|onenote|fax/i.test(deviceName)){
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
    const receiptPx=await printWindow.webContents.executeJavaScript(`(()=>{const el=document.querySelector('.receipt');if(!el)return 0;return Math.max(el.getBoundingClientRect().height,el.scrollHeight||0)})()`);
    const measuredMm=Number(receiptPx||0)*25.4/96;
    const heightMm=Math.min(1000,Math.max(28,Math.ceil(measuredMm+3)));
    const result=await new Promise(resolve=>{
      printWindow.webContents.print({silent:true,printBackground:true,deviceName,margins:{marginType:"none"},pageSize:{width:Math.round(width*1000),height:Math.round(heightMm*1000)}},(success,failureReason)=>resolve({success,failureReason:failureReason||"",deviceName,paperWidth:width,paperLength:heightMm,mode:"windows",rawFailure}));
    });
    return result;
  }catch(err){
    console.error("[printer] Erro ao imprimir:",err);
    return {success:false,failureReason:String(err?.message||err),deviceName,rawFailure};
  }finally{
    if(!printWindow.isDestroyed())printWindow.destroy();
  }
});'''

main=main[:start]+handler+main[end:]
write('electron/main.cjs',main)

print('Patch 10.7.9 aplicado: impressão térmica principal agora usa raster ESC/POS RAW e ignora a página do driver.')
