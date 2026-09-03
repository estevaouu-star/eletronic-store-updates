from pathlib import Path
import json,re

root=Path("app")
def read(path): return (root/path).read_text(encoding="utf-8")
def write(path,value): (root/path).write_text(value,encoding="utf-8")

pkg=json.loads(read("package.json"));pkg["version"]="10.11.20";write("package.json",json.dumps(pkg,indent=2,ensure_ascii=False))
html=read("public/index.html");html,n=re.subn(r'(id="versionInfo" class="version-info">v)[0-9.]+',r'\g<1>10.11.20',html,count=1)
if n!=1: raise SystemExit("versão HTML não encontrada")
write("public/index.html",html)
js=read("public/app.js");js,n=re.subn(r'const atual="[0-9.]+"(?=,status=)','const atual="10.11.20"',js,count=1)
if n!=1: raise SystemExit("versão atualizador não encontrada")
write("public/app.js",js)

main=read("electron/main.cjs")
branch=r'''    if(process.platform==="win32"&&elginI8){
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
'''
if main.count(branch)!=1: raise SystemExit("desvio PowerShell ELGIN não encontrado")
main=main.replace(branch,"",1)
old='''    // A ELGIN i8 também precisa receber uma página térmica explícita. Sem isso o spooler
    // aceita o trabalho usando o tamanho padrão do driver, mas a impressora não avança o papel.
    const printOptions={
      silent:true,
      printBackground:true,
      deviceName,
      margins:{marginType:"none"},
      pageSize:{width:Math.round(width*1000),height:Math.round(heightMm*1000)},
      landscape:false,
      scaleFactor:100,
      pagesPerSheet:1,
      collate:false,
      copies:1
    };'''
new='''    // A ELGIN i8 usa exatamente o papel padrão do driver que passou no teste físico.
    const printOptions=elginI8
      ? {silent:true,printBackground:true,deviceName,margins:{marginType:"none"},landscape:false,copies:1}
      : {silent:true,printBackground:true,deviceName,margins:{marginType:"none"},pageSize:{width:Math.round(width*1000),height:Math.round(heightMm*1000)},landscape:false,copies:1};'''
if main.count(old)!=1: raise SystemExit("opções Electron 10.11.15 não encontradas")
main=main.replace(old,new,1)
main=main.replace('mode:elginI8?"windows-elgin-i8-80mm":"windows"','mode:elginI8?"windows-elgin-i8-driver-native":"windows"',1)
write("electron/main.cjs",main)
print("10.11.20: remove PowerShell e imprime ELGIN i8 pelo Electron no papel padrão do driver validado.")
