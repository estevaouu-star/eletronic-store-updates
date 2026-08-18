from pathlib import Path
import json
root=Path('app')
def read(p): return (root/p).read_text(encoding='utf-8')
def write(p,s): (root/p).write_text(s,encoding='utf-8')

pkg=json.loads(read('package.json'));pkg['version']='10.10.11';write('package.json',json.dumps(pkg,indent=2,ensure_ascii=False))
html=read('public/index.html').replace('id="versionInfo" class="version-info">v10.10.10','id="versionInfo" class="version-info">v10.10.11',1);write('public/index.html',html)

preload_path=None
for candidate in ['electron/preload.cjs','electron/preload.js']:
    if (root/candidate).exists(): preload_path=candidate; break
if not preload_path: raise RuntimeError('Preload Electron nao encontrado')
preload=read(preload_path)
if 'eletromixRemember101011' not in preload:
    preload += r'''

// 10.10.11 - credenciais lembradas via safeStorage do sistema operacional
try{
 const {contextBridge:cb101011,ipcRenderer:ir101011}=require('electron');
 cb101011.exposeInMainWorld('eletromixRemember101011',{
   save:(login,password)=>ir101011.invoke('remember101011:save',{login,password}),
   read:()=>ir101011.invoke('remember101011:read'),
   clear:()=>ir101011.invoke('remember101011:clear')
 });
}catch(e){console.error('[remember101011 preload]',e)}
'''
write(preload_path,preload)

main=read('electron/main.cjs')
if 'remember101011:save' not in main:
    main += r'''

// 10.10.11 - auto-login confiável: salva credenciais criptografadas pelo Windows/macOS/Linux.
const {safeStorage:safeStorage101011}=require('electron');
const rememberFile101011=path101010.join(app.getPath('userData'),'remember-login.bin.json');
function clearRemember101011(){try{fs101010.rmSync(rememberFile101011,{force:true})}catch{}return true}
function writeRemember101011(login,password){
 try{
  if(!safeStorage101011.isEncryptionAvailable())throw new Error('Criptografia segura do sistema operacional indisponível.');
  const payload={version:app.getVersion(),login:String(login||''),password:safeStorage101011.encryptString(String(password||'')).toString('base64')};
  if(!payload.login||!password)throw new Error('Login ou senha vazios.');
  fs101010.mkdirSync(path101010.dirname(rememberFile101011),{recursive:true});
  fs101010.writeFileSync(rememberFile101011,JSON.stringify(payload),'utf8');
  return {ok:true};
 }catch(e){console.error('[remember101011 save]',e);return {ok:false,error:String(e?.message||e)}}
}
function readRemember101011(){
 try{
  const p=JSON.parse(fs101010.readFileSync(rememberFile101011,'utf8'));
  if(p?.version!==app.getVersion()){clearRemember101011();return null}
  if(!p?.login||!p?.password)return null;
  if(!safeStorage101011.isEncryptionAvailable())return null;
  return {login:p.login,password:safeStorage101011.decryptString(Buffer.from(p.password,'base64'))};
 }catch{return null}
}
ipcMain.removeHandler('remember101011:save');ipcMain.handle('remember101011:save',(_e,p)=>writeRemember101011(p?.login,p?.password));
ipcMain.removeHandler('remember101011:read');ipcMain.handle('remember101011:read',()=>readRemember101011());
ipcMain.removeHandler('remember101011:clear');ipcMain.handle('remember101011:clear',()=>clearRemember101011());
'''
write('electron/main.cjs',main)

js=read('public/app.js').replace('const atual="10.10.10"','const atual="10.10.11"',1)
js += r'''
// 10.10.11 - não depende de token sobreviver ao fechamento. Faz login automático com credencial criptografada.
let autoLogin101011Running=false;
const loginBase101011=login;
login=async function(e){
 const user=document.querySelector('#login')?.value||'';
 const pass=document.querySelector('#senha')?.value||'';
 await loginBase101011(e);
 if(me&&token&&user&&pass){try{await window.eletromixRemember101011?.save(user,pass)}catch(err){console.error('[remember101011 save frontend]',err)}}
};
async function autoLogin101011(){
 if(autoLogin101011Running||me||!window.eletromixRemember101011)return false;
 const screen=document.querySelector('#loginScreen');if(screen&&screen.classList.contains('hidden'))return false;
 autoLogin101011Running=true;
 try{
  const c=await window.eletromixRemember101011.read();if(!c?.login||!c?.password)return false;
  const u=document.querySelector('#login'),p=document.querySelector('#senha');if(!u||!p)return false;
  u.value=c.login;p.value=c.password;
  await login({preventDefault(){}});
  return !!me;
 }catch(err){console.error('[autoLogin101011]',err);return false}
 finally{autoLogin101011Running=false}
}
// Sair manualmente apaga a credencial lembrada; fechar a janela não apaga.
document.addEventListener('click',e=>{if(e.target.closest?.('#logoutBtn,[data-action="logout"],.logout-btn'))window.eletromixRemember101011?.clear?.()},true);
document.addEventListener('DOMContentLoaded',()=>setTimeout(autoLogin101011,80));
setTimeout(autoLogin101011,180);setTimeout(autoLogin101011,700);setTimeout(autoLogin101011,1600);
'''
write('public/app.js',js)
print('10.10.11: login persistente usa safeStorage do sistema e reloga automaticamente; atualização continua no downloader direto da 10.10.10.')