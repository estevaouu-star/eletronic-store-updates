from pathlib import Path
import json, re

root=Path("app")
def read(path): return (root/path).read_text(encoding="utf-8")
def write(path,value): (root/path).write_text(value,encoding="utf-8")

pkg=json.loads(read("package.json"));pkg["version"]="10.11.16";write("package.json",json.dumps(pkg,indent=2,ensure_ascii=False))
html=read("public/index.html");html,count=re.subn(r'(id="versionInfo" class="version-info">v)[0-9.]+',r'\g<1>10.11.16',html,count=1)
if count!=1: raise SystemExit("versão HTML não encontrada")
write("public/index.html",html)
js=read("public/app.js");js,count=re.subn(r'const atual="[0-9.]+"(?=,status=)','const atual="10.11.16"',js,count=1)
if count!=1: raise SystemExit("versão do atualizador não encontrada")
write("public/app.js",js)

main=read("electron/main.cjs")
anchor='ipcMain.handle("printer:print", async (_event, payload = {}) => {'
if anchor not in main: raise SystemExit("handler de impressão não encontrado")
helper=r'''async function printElginI8GdiWindows(deviceName,image,widthMm,heightMm){
  const {execFile}=require("child_process"),fs=require("fs"),path=require("path");
  const file=path.join(app.getPath("temp"),`eletromix-elgin-${process.pid}-${Date.now()}.png`);
  fs.writeFileSync(file,image.toPNG());
  const source=String.raw`
using System;
using System.Drawing;
using System.Drawing.Printing;
public static class EletromixElginPrint {
  public static void Run(string printer,string imagePath,int width,int height) {
    using(var bitmap=Image.FromFile(imagePath))
    using(var document=new PrintDocument()) {
      document.PrinterSettings.PrinterName=printer;
      if(!document.PrinterSettings.IsValid) throw new Exception("Driver da ELGIN i8 inválido ou indisponível.");
      document.PrintController=new StandardPrintController();
      document.DocumentName="Eletromix comprovante";
      document.OriginAtMargins=false;
      document.DefaultPageSettings.Margins=new Margins(0,0,0,0);
      document.DefaultPageSettings.Landscape=false;
      document.DefaultPageSettings.Color=false;
      document.DefaultPageSettings.PaperSize=new PaperSize("Eletromix 80mm",width,height);
      document.PrintPage+=(sender,args)=>{
        args.Graphics.PageUnit=GraphicsUnit.Display;
        args.Graphics.DrawImage(bitmap,0,0,width,height);
        args.HasMorePages=false;
      };
      document.Print();
    }
  }
}`;
  const ps=String.raw`$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Drawing
Add-Type -TypeDefinition $env:ELETROMIX_GDI_SOURCE -ReferencedAssemblies System.Drawing
[EletromixElginPrint]::Run($env:ELETROMIX_PRINTER,$env:ELETROMIX_IMAGE,[int]$env:ELETROMIX_WIDTH,[int]$env:ELETROMIX_HEIGHT)
Write-Output 'OK'`;
  const widthInch=Math.max(228,Math.round(Number(widthMm||80)/25.4*100));
  const heightInch=Math.max(110,Math.round(Number(heightMm||40)/25.4*100));
  try{
    return await new Promise((resolve,reject)=>{
      execFile("powershell.exe",["-NoLogo","-NoProfile","-NonInteractive","-ExecutionPolicy","Bypass","-Command",ps],{
        windowsHide:true,timeout:20000,env:{...process.env,ELETROMIX_GDI_SOURCE:source,ELETROMIX_PRINTER:deviceName,ELETROMIX_IMAGE:file,ELETROMIX_WIDTH:String(widthInch),ELETROMIX_HEIGHT:String(heightInch)}
      },(error,stdout,stderr)=>{
        if(error)return reject(new Error(String(stderr||stdout||error.message||error)));
        if(!/OK/.test(String(stdout||"")))return reject(new Error("O Windows não confirmou a impressão pela ELGIN i8."));
        resolve({success:true,failureReason:"",deviceName,paperWidth:widthMm,paperLength:heightMm,mode:"windows-elgin-i8-gdi"});
      });
    });
  }finally{try{fs.unlinkSync(file)}catch{}}
}

'''
if "async function printElginI8GdiWindows" not in main: main=main.replace(anchor,helper+anchor,1)
needle='''    const elginI8=/elgin.*i8|i8.*elgin/i.test(`${selected?.name||deviceName} ${selected?.displayName||""} ${selected?.description||""}`);
    // A ELGIN i8 também precisa receber uma página térmica explícita. Sem isso o spooler'''
replacement='''    const elginI8=/elgin.*i8|i8.*elgin/i.test(`${selected?.name||deviceName} ${selected?.displayName||""} ${selected?.description||""}`);
    if(process.platform==="win32"&&elginI8){
      try{
        const rect=await printWindow.webContents.executeJavaScript(`(()=>{const el=document.querySelector('.receipt');if(!el)return null;const r=el.getBoundingClientRect();return {x:Math.max(0,Math.floor(r.x)),y:Math.max(0,Math.floor(r.y)),width:Math.max(1,Math.ceil(r.width)),height:Math.max(1,Math.ceil(r.height))}})()`);
        if(!rect)throw new Error("Área do comprovante não encontrada.");
        const image=await printWindow.webContents.capturePage(rect);
        return await printElginI8GdiWindows(deviceName,image,width,heightMm);
      }catch(err){
        console.error("[printer] ELGIN i8 GDI falhou:",err);
        return {success:false,failureReason:String(err?.message||err),deviceName,paperWidth:width,mode:"windows-elgin-i8-gdi-error"};
      }
    }
    // Demais impressoras continuam no caminho do Electron.
    // A ELGIN i8 também precisa receber uma página térmica explícita. Sem isso o spooler'''
if needle not in main: raise SystemExit("ponto de entrada ELGIN i8 não encontrado")
main=main.replace(needle,replacement,1)
write("electron/main.cjs",main)
print("10.11.16: ELGIN i8 imprime bitmap pela API GDI nativa do Windows, fora do Electron.")
