from pathlib import Path
import json,re

root=Path("app")
def read(path): return (root/path).read_text(encoding="utf-8")
def write(path,value): (root/path).write_text(value,encoding="utf-8")

pkg=json.loads(read("package.json"));pkg["version"]="10.11.17";write("package.json",json.dumps(pkg,indent=2,ensure_ascii=False))
html=read("public/index.html");html,n=re.subn(r'(id="versionInfo" class="version-info">v)[0-9.]+',r'\g<1>10.11.17',html,count=1)
if n!=1: raise SystemExit("versão HTML não encontrada")
write("public/index.html",html)
js=read("public/app.js");js,n=re.subn(r'const atual="[0-9.]+"(?=,status=)','const atual="10.11.17"',js,count=1)
if n!=1: raise SystemExit("versão do atualizador não encontrada")
write("public/app.js",js)

main=read("electron/main.cjs")
new_helper=r'''async function printElginI8GdiWindows(deviceName,image,widthMm,heightMm){
  const {execFile}=require("child_process"),fs=require("fs"),path=require("path");
  const file=path.join(app.getPath("temp"),`eletromix-elgin-${process.pid}-${Date.now()}.png`);
  fs.writeFileSync(file,image.toPNG());
  const ps=String.raw`$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Drawing
$image=[System.Drawing.Image]::FromFile($env:ELETROMIX_IMAGE)
$document=New-Object System.Drawing.Printing.PrintDocument
$document.PrinterSettings.PrinterName=$env:ELETROMIX_PRINTER
if(-not $document.PrinterSettings.IsValid){throw 'Driver da ELGIN i8 inválido ou indisponível.'}
$document.PrintController=New-Object System.Drawing.Printing.StandardPrintController
$document.DocumentName='Eletromix comprovante'
$document.OriginAtMargins=$false
$document.DefaultPageSettings.Margins=New-Object System.Drawing.Printing.Margins -ArgumentList 0,0,0,0
$document.DefaultPageSettings.Landscape=$false
$document.DefaultPageSettings.Color=$false
$paper=New-Object System.Drawing.Printing.PaperSize -ArgumentList 'Eletromix 80mm',[int]$env:ELETROMIX_WIDTH,[int]$env:ELETROMIX_HEIGHT
$document.DefaultPageSettings.PaperSize=$paper
$width=[int]$env:ELETROMIX_WIDTH
$height=[int]$env:ELETROMIX_HEIGHT
$handler=[System.Drawing.Printing.PrintPageEventHandler]{
  param($sender,$eventArgs)
  $eventArgs.Graphics.PageUnit=[System.Drawing.GraphicsUnit]::Display
  $eventArgs.Graphics.DrawImage($image,0,0,$width,$height)
  $eventArgs.HasMorePages=$false
}
$document.add_PrintPage($handler)
try{$document.Print();Write-Output 'OK'}finally{$document.remove_PrintPage($handler);$document.Dispose();$image.Dispose()}`;
  const widthInch=Math.max(228,Math.round(Number(widthMm||80)/25.4*100));
  const heightInch=Math.max(110,Math.round(Number(heightMm||40)/25.4*100));
  try{
    return await new Promise((resolve,reject)=>{
      execFile("powershell.exe",["-NoLogo","-NoProfile","-NonInteractive","-ExecutionPolicy","Bypass","-Command",ps],{
        windowsHide:true,timeout:20000,env:{...process.env,ELETROMIX_PRINTER:deviceName,ELETROMIX_IMAGE:file,ELETROMIX_WIDTH:String(widthInch),ELETROMIX_HEIGHT:String(heightInch)}
      },(error,stdout,stderr)=>{
        if(error)return reject(new Error(String(stderr||stdout||error.message||error)));
        if(!/OK/.test(String(stdout||"")))return reject(new Error("O Windows não confirmou a impressão pela ELGIN i8."));
        resolve({success:true,failureReason:"",deviceName,paperWidth:widthMm,paperLength:heightMm,mode:"windows-elgin-i8-gdi-native"});
      });
    });
  }finally{try{fs.unlinkSync(file)}catch{}}
}'''
pattern=r'async function printElginI8GdiWindows\(deviceName,image,widthMm,heightMm\)\{.*?\n\}(?=\n\nipcMain\.handle\("printer:print")'
main,n=re.subn(pattern,lambda _m:new_helper,main,count=1,flags=re.S)
if n!=1: raise SystemExit("ponte GDI da 10.11.16 não encontrada")
write("electron/main.cjs",main)
print("10.11.17: impressão ELGIN i8 usa PowerShell/System.Drawing nativos, sem compilar C# em tempo de execução.")
