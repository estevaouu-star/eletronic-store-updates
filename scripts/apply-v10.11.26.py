from pathlib import Path
import json,re

root=Path("app")
def read(path): return (root/path).read_text(encoding="utf-8")
def write(path,value): (root/path).write_text(value,encoding="utf-8")

pkg=json.loads(read("package.json"));pkg["version"]="10.11.26";write("package.json",json.dumps(pkg,indent=2,ensure_ascii=False))
html=read("public/index.html");html,n=re.subn(r'(id="versionInfo" class="version-info">v)[0-9.]+',r'\g<1>10.11.26',html,count=1)
if n!=1: raise SystemExit("versão HTML não encontrada")
write("public/index.html",html)
js=read("public/app.js");js,n=re.subn(r'const atual="[0-9.]+"(?=,status=)','const atual="10.11.26"',js,count=1)
if n!=1: raise SystemExit("versão atualizador não encontrada")
write("public/app.js",js)

main=read("electron/main.cjs")
old_list=re.search(r'ipcMain\.handle\("printer:list", async \(\) => \{.*?\n\}\);\n\n',main,re.S)
if not old_list: raise SystemExit("handler printer:list 10.11.25 não encontrado")
helper=r'''async function getPhysicalPrinters101126(){
  let electronPrinters=[];
  if(mainWindow && !mainWindow.isDestroyed()){
    try{
      electronPrinters=await Promise.race([
        mainWindow.webContents.getPrintersAsync(),
        new Promise((_,reject)=>setTimeout(()=>reject(new Error("electron-printer-timeout")),3500))
      ]);
    }catch(error){console.error("[printer:list:electron]",error)}
  }
  const cleaned=(Array.isArray(electronPrinters)?electronPrinters:[]).filter(p=>!isVirtualPrinter101113(p));
  if(cleaned.length)return cleaned;
  if(process.platform!=="win32")return [];
  try{
    const script="$ErrorActionPreference='Stop'; @(Get-CimInstance Win32_Printer | Select-Object Name,Default,WorkOffline) | ConvertTo-Json -Compress";
    const stdout=await new Promise((resolve,reject)=>{
      execFile("powershell.exe",["-NoLogo","-NoProfile","-NonInteractive","-ExecutionPolicy","Bypass","-Command",script],{windowsHide:true,timeout:8000},(error,out,err)=>{
        if(error)return reject(new Error(String(err||out||error.message||error)));
        resolve(String(out||""));
      });
    });
    const parsed=JSON.parse(stdout||"[]");
    const rows=Array.isArray(parsed)?parsed:(parsed?[parsed]:[]);
    return rows.map(row=>({
      name:String(row.Name||""),
      displayName:String(row.Name||""),
      description:row.WorkOffline?"offline":"",
      status:0,
      isDefault:Boolean(row.Default)
    })).filter(p=>p.name&&!isVirtualPrinter101113(p));
  }catch(error){
    console.error("[printer:list:windows]",error);
    return [];
  }
}

ipcMain.handle("printer:list", async () => getPhysicalPrinters101126());

'''
main=main[:old_list.start()]+helper+main[old_list.end():]
old='''  let available = [];
  try { available = mainWindow ? (await mainWindow.webContents.getPrintersAsync()).filter(p=>!isVirtualPrinter101113(p)) : []; } catch {}
'''
new='''  const available = await getPhysicalPrinters101126();
'''
if old not in main: raise SystemExit("consulta interna do printer:print não encontrada")
main=main.replace(old,new,1)
write("electron/main.cjs",main)
print("10.11.26: detecção Electron + fallback direto Win32 e mesma lista usada no envio.")
