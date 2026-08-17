from pathlib import Path
import json

root=Path('app')
def read(p): return (root/p).read_text(encoding='utf-8')
def write(p,s): (root/p).write_text(s,encoding='utf-8')
def must(s,a,b,label):
    if a not in s: raise RuntimeError(f'Trecho nao encontrado: {label}')
    return s.replace(a,b,1)

pkg=json.loads(read('package.json'))
pkg['version']='10.8.0'
write('package.json',json.dumps(pkg,indent=2,ensure_ascii=False))

html=read('public/index.html')
html=html.replace('id="versionInfo" class="version-info">v10.7.9','id="versionInfo" class="version-info">v10.8.0')
html=html.replace('Comprimento: automático · modo térmico direto, sem página em branco do driver','Térmico direto otimizado · corte automático · impressão econômica')
write('public/index.html',html)

js=read('public/app.js')
js=js.replace('const atual="10.7.9"','const atual="10.8.0"')
js=js.replace('r.mode==="escpos"?" · térmico direto":""','r.mode==="escpos"?" · térmico direto · corte automático":""')
write('public/app.js',js)

main=read('electron/main.cjs')

# Logo menos carregada em papel térmico: reduz blocos pretos sem clarear o texto do comprovante.
old_logo='.receipt-logo{text-align:center;margin-bottom:5px}.receipt-logo img{max-width:${width===58?35:45}mm;max-height:22mm;object-fit:contain}'
new_logo='.receipt-logo{text-align:center;margin-bottom:5px}.receipt-logo img{max-width:${width===58?35:45}mm;max-height:22mm;object-fit:contain;filter:grayscale(1) contrast(.25) brightness(1.35)}'
main=must(main,old_logo,new_logo,'filtro termico da logo')

# Raster mais claro: texto preto continua sólido, mas tons escuros da logo deixam de virar um bloco preto.
old_threshold='''      const threshold=176+(bayer[(y%4)*4+(x%4)]-7.5)*4;
      if(a>24 && lum<threshold)raster[y*rowBytes+(x>>3)]|=(0x80>>(x&7));'''
new_threshold='''      const threshold=142+(bayer[(y%4)*4+(x%4)]-7.5)*3;
      if(a>24 && lum<threshold)raster[y*rowBytes+(x>>3)]|=(0x80>>(x&7));'''
main=must(main,old_threshold,new_threshold,'densidade termica')

# Avanço curto + comando ESC/POS de corte automático (GS V 66 0).
old_tail='''    raster,
    Buffer.from([0x1b,0x64,0x02])
  ]);'''
new_tail='''    raster,
    // Avança só o necessário para a guilhotina e solicita corte parcial automático.
    Buffer.from([0x1b,0x64,0x03,0x1d,0x56,0x42,0x00])
  ]);'''
main=must(main,old_tail,new_tail,'comando de corte')

# Troca o PowerShell criado a cada impressão por um worker persistente. O Add-Type é compilado
# uma única vez quando o Eletromix abre; as impressões seguintes vão direto para o spooler RAW.
start=main.find('async function sendRawPrinterWindows(deviceName,bytes){')
end=main.find('\n\nipcMain.handle("printer:print"',start)
if start<0 or end<0: raise RuntimeError('sendRawPrinterWindows nao encontrado')
worker=r'''let rawPrinterWorker=null;
let rawPrinterSeq=0;
const rawPrinterPending=new Map();

function ensureRawPrinterWorker(){
  if(rawPrinterWorker && !rawPrinterWorker.killed && rawPrinterWorker.stdin?.writable)return rawPrinterWorker;
  const {spawn}=require("child_process");
  const script=String.raw`$ErrorActionPreference='Stop'
$ProgressPreference='SilentlyContinue'
Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
public static class RawPrinterFast {
  [StructLayout(LayoutKind.Sequential, CharSet=CharSet.Unicode)] public struct DOC_INFO_1 { public string pDocName; public string pOutputFile; public string pDataType; }
  [DllImport("winspool.drv", SetLastError=true, CharSet=CharSet.Unicode)] public static extern bool OpenPrinter(string pPrinterName,out IntPtr phPrinter,IntPtr pDefault);
  [DllImport("winspool.drv", SetLastError=true)] public static extern bool ClosePrinter(IntPtr hPrinter);
  [DllImport("winspool.drv", SetLastError=true, CharSet=CharSet.Unicode)] public static extern int StartDocPrinter(IntPtr hPrinter,int Level,ref DOC_INFO_1 pDocInfo);
  [DllImport("winspool.drv", SetLastError=true)] public static extern bool EndDocPrinter(IntPtr hPrinter);
  [DllImport("winspool.drv", SetLastError=true)] public static extern bool StartPagePrinter(IntPtr hPrinter);
  [DllImport("winspool.drv", SetLastError=true)] public static extern bool EndPagePrinter(IntPtr hPrinter);
  [DllImport("winspool.drv", SetLastError=true)] public static extern bool WritePrinter(IntPtr hPrinter,byte[] pBytes,int dwCount,out int dwWritten);
}
"@
while (($line=[Console]::In.ReadLine()) -ne $null) {
  if([string]::IsNullOrWhiteSpace($line)){continue}
  $id='?'
  try {
    $job=$line|ConvertFrom-Json
    $id=[string]$job.id
    $bytes=[Convert]::FromBase64String([string]$job.data)
    $h=[IntPtr]::Zero;$docStarted=$false;$pageStarted=$false
    if(-not [RawPrinterFast]::OpenPrinter([string]$job.printer,[ref]$h,[IntPtr]::Zero)){throw "OpenPrinter falhou: $([Runtime.InteropServices.Marshal]::GetLastWin32Error())"}
    try {
      $doc=New-Object 'RawPrinterFast+DOC_INFO_1';$doc.pDocName='Eletromix - Comprovante';$doc.pDataType='RAW'
      if([RawPrinterFast]::StartDocPrinter($h,1,[ref]$doc)-le 0){throw "StartDocPrinter falhou: $([Runtime.InteropServices.Marshal]::GetLastWin32Error())"};$docStarted=$true
      if(-not [RawPrinterFast]::StartPagePrinter($h)){throw "StartPagePrinter falhou: $([Runtime.InteropServices.Marshal]::GetLastWin32Error())"};$pageStarted=$true
      [int]$written=0
      if(-not [RawPrinterFast]::WritePrinter($h,$bytes,$bytes.Length,[ref]$written)){throw "WritePrinter falhou: $([Runtime.InteropServices.Marshal]::GetLastWin32Error())"}
      if($written-ne $bytes.Length){throw "Impressão RAW incompleta: $written de $($bytes.Length) bytes"}
    } finally {
      if($pageStarted){[RawPrinterFast]::EndPagePrinter($h)|Out-Null}
      if($docStarted){[RawPrinterFast]::EndDocPrinter($h)|Out-Null}
      if($h-ne [IntPtr]::Zero){[RawPrinterFast]::ClosePrinter($h)|Out-Null}
    }
    [Console]::Out.WriteLine('__ELETROMIX__'+$id+'|OK')
  } catch {
    $msg=([string]$_.Exception.Message).Replace("`r",' ').Replace("`n",' ')
    [Console]::Out.WriteLine('__ELETROMIX__'+$id+'|ERR|'+$msg)
  }
}`;
  const child=spawn("powershell.exe",["-NoLogo","-NoProfile","-NonInteractive","-ExecutionPolicy","Bypass","-Command",script],{windowsHide:true,stdio:["pipe","pipe","pipe"]});
  child.stdout.setEncoding("utf8");child.stderr.setEncoding("utf8");
  let buf="";
  child.stdout.on("data",chunk=>{
    buf+=chunk;
    let nl;
    while((nl=buf.indexOf("\n"))>=0){
      const line=buf.slice(0,nl).trim();buf=buf.slice(nl+1);
      if(!line.startsWith("__ELETROMIX__"))continue;
      const parts=line.slice(14).split("|");const id=parts.shift();const status=parts.shift();
      const pending=rawPrinterPending.get(id);if(!pending)continue;
      rawPrinterPending.delete(id);clearTimeout(pending.timer);
      status==="OK"?pending.resolve():pending.reject(new Error(parts.join("|")||"Falha no spooler térmico."));
    }
  });
  child.stderr.on("data",data=>{const s=String(data||"").trim();if(s)console.error("[printer-worker]",s)});
  child.on("exit",()=>{
    if(rawPrinterWorker===child)rawPrinterWorker=null;
    for(const [id,p] of rawPrinterPending){clearTimeout(p.timer);p.reject(new Error("Serviço de impressão térmica foi encerrado."));rawPrinterPending.delete(id)}
  });
  rawPrinterWorker=child;
  return child;
}

async function sendRawPrinterWindows(deviceName,bytes){
  const worker=ensureRawPrinterWorker();
  const id=String(++rawPrinterSeq);
  return new Promise((resolve,reject)=>{
    const timer=setTimeout(()=>{rawPrinterPending.delete(id);reject(new Error("A impressora demorou demais para responder."))},12000);
    rawPrinterPending.set(id,{resolve,reject,timer});
    worker.stdin.write(JSON.stringify({id,printer:deviceName,data:bytes.toString("base64")})+"\n",err=>{
      if(!err)return;
      const p=rawPrinterPending.get(id);if(!p)return;rawPrinterPending.delete(id);clearTimeout(p.timer);reject(err);
    });
  });
}'''
main=main[:start]+worker+main[end:]

# Reutiliza a janela invisível de renderização em vez de criar/destruir uma nova a cada clique.
needle='''ipcMain.handle("printer:print", async (_event, payload = {}) => {'''
helper='''let thermalRenderWindow=null;
function getThermalRenderWindow(){
  if(!thermalRenderWindow || thermalRenderWindow.isDestroyed()){
    thermalRenderWindow=new BrowserWindow({show:false,width:520,height:900,webPreferences:{contextIsolation:true,sandbox:true}});
    thermalRenderWindow.on("closed",()=>{thermalRenderWindow=null});
  }
  return thermalRenderWindow;
}

ipcMain.handle("printer:print", async (_event, payload = {}) => {'''
main=must(main,needle,helper,'janela termica persistente')
old_window='''  const printWindow = new BrowserWindow({show:false,width:520,height:900,webPreferences:{contextIsolation:true,sandbox:true}});'''
main=must(main,old_window,'  const printWindow=getThermalRenderWindow();','criacao da janela termica')
main=main.replace('await new Promise(resolve=>setTimeout(resolve,160));','await new Promise(resolve=>setTimeout(resolve,25));',1)
# Janela é reutilizada; não destruir após cada comprovante.
main=main.replace('''  }finally{
    if(!printWindow.isDestroyed())printWindow.destroy();
  }
});''','''  }finally{
    // Mantém a janela invisível pronta para a próxima impressão.
  }
});''',1)

# Pré-aquece o worker RAW ao abrir o programa para a primeira impressão também ser mais rápida.
main=main.replace('''    createWindow();
    createTray();''','''    createWindow();
    createTray();
    if(process.platform==="win32")setTimeout(()=>{try{ensureRawPrinterWorker()}catch(err){console.error("[printer] Falha ao pré-aquecer worker:",err)}},150);''',1)
main=main.replace('''app.on("before-quit", () => {
  quitting = true;
});''','''app.on("before-quit", () => {
  quitting = true;
  try{rawPrinterWorker?.stdin?.end()}catch{}
});''',1)

write('electron/main.cjs',main)
print('Patch 10.8.0 aplicado: corte automatico, logo mais clara e impressao RAW persistente/mais rapida.')
