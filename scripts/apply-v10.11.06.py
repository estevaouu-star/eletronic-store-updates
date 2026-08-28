from pathlib import Path
import json,re
root=Path('app')
def read(p): return (root/p).read_text(encoding='utf-8')
def write(p,s): (root/p).write_text(s,encoding='utf-8')
pkg=json.loads(read('package.json'));pkg['version']='10.11.6';write('package.json',json.dumps(pkg,indent=2,ensure_ascii=False))
html=read('public/index.html');html,n=re.subn(r'(id="versionInfo" class="version-info">v)[0-9.]+',r'\g<1>10.11.06',html,count=1)
if n!=1: raise SystemExit('versao html nao encontrada')
write('public/index.html',html)
js=read('public/app.js');js,n=re.subn(r'const atual="[0-9.]+"(?=,status=)','const atual="10.11.6"',js,count=1)
if n!=1: raise SystemExit('versao atualizador nao encontrada')
write('public/app.js',js)
main=read('electron/main.cjs')
anchor='''async function sendRawPrinterWindows(deviceName,bytes){'''
pos=main.find(anchor)
if pos<0: raise SystemExit('sendRawPrinterWindows nao encontrado')
helper=r'''async function sendElginI8DirectWindows(bytes){
  // A i8 pode operar como USB Printing ou Virtual COM. Alguns PDVs funcionam pela COM mesmo quando
  // o spooler do Windows nao imprime. Detecta automaticamente portas COM com descricao USB/Elgin/POS.
  const {execFile}=require("child_process");
  const data=bytes.toString("base64");
  const script=String.raw`$ErrorActionPreference='Stop'
$ports=@(Get-CimInstance Win32_SerialPort -ErrorAction SilentlyContinue | Where-Object { ($_.Name+' '+$_.Description+' '+$_.PNPDeviceID) -match 'ELGIN|POS|USB|Serial' })
if(-not $ports -or $ports.Count -eq 0){ throw 'ELGIN i8: nenhuma porta COM/USB serial encontrada' }
$bytes=[Convert]::FromBase64String($env:ELETROMIX_PRINT_DATA)
$last=''
foreach($p in $ports){
  try{
    $port=New-Object System.IO.Ports.SerialPort $p.DeviceID,115200,'None',8,'One'
    $port.WriteTimeout=4000;$port.Open();$port.Write($bytes,0,$bytes.Length);$port.BaseStream.Flush();Start-Sleep -Milliseconds 120;$port.Close()
    Write-Output ('OK|'+$p.DeviceID);exit 0
  }catch{$last=$_.Exception.Message;try{$port.Close()}catch{}}
}
throw ('ELGIN i8 COM falhou: '+$last)`;
  return await new Promise((resolve,reject)=>{
    execFile("powershell.exe",["-NoLogo","-NoProfile","-NonInteractive","-ExecutionPolicy","Bypass","-Command",script],{windowsHide:true,timeout:12000,env:{...process.env,ELETROMIX_PRINT_DATA:data}},(err,stdout,stderr)=>{
      if(err)return reject(new Error(String(stderr||stdout||err.message||err)));
      const out=String(stdout||"").trim();resolve({port:(out.split("|")[1]||"").trim()});
    });
  });
}

'''
main=main[:pos]+helper+main[pos:]
needle='''    const elginI8=/elgin.*\\bi[- ]?8\\b|\\bi[- ]?8\\b.*elgin/i.test(printerLabel);
    if(process.platform==="win32" && !elginI8 && !/pdf|xps|onenote|fax/i.test(deviceName)){'''
replacement='''    const elginI8=/elgin.*\\bi[- ]?8\\b|\\bi[- ]?8\\b.*elgin/i.test(printerLabel);
    // Primeiro tenta comunicacao direta pela Virtual COM da i8, caminho comum em PDVs.
    if(process.platform==="win32" && elginI8){
      try{
        const rect=await printWindow.webContents.executeJavaScript(`(()=>{const el=document.querySelector('.receipt');if(!el)return null;const r=el.getBoundingClientRect();return {x:Math.max(0,Math.floor(r.x)),y:Math.max(0,Math.floor(r.y)),width:Math.max(1,Math.ceil(r.width)),height:Math.max(1,Math.ceil(r.height))}})()`);
        if(rect){const image=await printWindow.webContents.capturePage(rect);const raw=receiptImageToEscPos(image,width);const direct=await sendElginI8DirectWindows(raw);return {success:true,failureReason:"",deviceName,paperWidth:width,mode:"elgin-i8-com",port:direct.port};}
      }catch(err){rawFailure=String(err?.message||err);console.error("[printer] ELGIN i8 direta falhou; tentando driver Windows:",rawFailure)}
    }
    if(process.platform==="win32" && !elginI8 && !/pdf|xps|onenote|fax/i.test(deviceName)){'''
if needle not in main: raise SystemExit('bloco elgin 10.11.05 nao encontrado')
main=main.replace(needle,replacement,1)
write('electron/main.cjs',main)
print('10.11.06: ELGIN i8 tenta Virtual COM/USB serial direta antes do spooler Windows.')