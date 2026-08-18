from pathlib import Path
import json
root=Path('app')
def read(p): return (root/p).read_text(encoding='utf-8')
def write(p,s): (root/p).write_text(s,encoding='utf-8')

pkg=json.loads(read('package.json'));pkg['version']='10.10.10';write('package.json',json.dumps(pkg,indent=2,ensure_ascii=False))
html=read('public/index.html').replace('id="versionInfo" class="version-info">v10.10.9','id="versionInfo" class="version-info">v10.10.10',1);write('public/index.html',html)

preload_path=None
for candidate in ['electron/preload.cjs','electron/preload.js']:
    if (root/candidate).exists(): preload_path=candidate; break
if not preload_path: raise RuntimeError('Preload Electron nao encontrado')
preload=read(preload_path)
preload += r'''

// 10.10.10 - bridge estável para sessão e atualizador direto
try{
 const {contextBridge:cb101010,ipcRenderer:ir101010}=require('electron');
 cb101010.exposeInMainWorld('eletromix101010',{
   sessionRead:()=>ir101010.invoke('auth101010:read'),
   sessionSave:(s)=>ir101010.invoke('auth101010:save',s),
   sessionClear:()=>ir101010.invoke('auth101010:clear'),
   updateAction:()=>ir101010.invoke('update101010:action'),
   updateState:()=>ir101010.invoke('update101010:state'),
   onUpdate:(fn)=>{const h=(_e,s)=>fn(s);ir101010.on('update101010:state',h);return()=>ir101010.removeListener('update101010:state',h)}
 });
}catch(e){console.error('[101010 preload]',e)}
'''
write(preload_path,preload)

main=read('electron/main.cjs')
main += r'''

// 10.10.10 - sessão persistente em userData e atualizador por download direto do instalador.
const fs101010=require('fs');
const path101010=require('path');
const https101010=require('https');
const {spawn:spawn101010}=require('child_process');
const authFile101010=path101010.join(app.getPath('userData'),'auth-session.json');
function readAuth101010(){try{const x=JSON.parse(fs101010.readFileSync(authFile101010,'utf8'));if(x?.version!==app.getVersion())return null;return x}catch{return null}}
function writeAuth101010(x){try{fs101010.mkdirSync(path101010.dirname(authFile101010),{recursive:true});fs101010.writeFileSync(authFile101010,JSON.stringify({...x,version:app.getVersion()}),'utf8');return true}catch(e){console.error('[auth101010 save]',e);return false}}
function clearAuth101010(){try{fs101010.unlinkSync(authFile101010)}catch{}return true}
ipcMain.removeHandler('auth101010:read');ipcMain.handle('auth101010:read',()=>readAuth101010());
ipcMain.removeHandler('auth101010:save');ipcMain.handle('auth101010:save',(_e,s)=>writeAuth101010(s||{}));
ipcMain.removeHandler('auth101010:clear');ipcMain.handle('auth101010:clear',()=>clearAuth101010());

let update101010={status:'idle',percent:0,message:'',version:app.getVersion(),installer:''};
function emit101010(p={}){update101010={...update101010,...p};try{if(mainWindow&&!mainWindow.isDestroyed())mainWindow.webContents.send('update101010:state',update101010)}catch{}return update101010}
function jsonGet101010(url,redirects=0){return new Promise((resolve,reject)=>{const req=https101010.get(url,{headers:{'User-Agent':'Eletromix-Updater','Accept':'application/vnd.github+json'}},res=>{if(res.statusCode>=300&&res.statusCode<400&&res.headers.location&&redirects<8){res.resume();return resolve(jsonGet101010(res.headers.location,redirects+1))}let b='';res.setEncoding('utf8');res.on('data',d=>b+=d);res.on('end',()=>{if(res.statusCode<200||res.statusCode>=300)return reject(new Error('GitHub respondeu '+res.statusCode));try{resolve(JSON.parse(b))}catch(e){reject(e)}})});req.setTimeout(20000,()=>req.destroy(new Error('Tempo esgotado ao verificar atualização')));req.on('error',reject)})}
function download101010(url,dest,redirects=0){return new Promise((resolve,reject)=>{const tmp=dest+'.part';try{fs101010.mkdirSync(path101010.dirname(dest),{recursive:true});fs101010.rmSync(tmp,{force:true})}catch{}const req=https101010.get(url,{headers:{'User-Agent':'Eletromix-Updater'}},res=>{if(res.statusCode>=300&&res.statusCode<400&&res.headers.location&&redirects<8){res.resume();return resolve(download101010(res.headers.location,dest,redirects+1))}if(res.statusCode<200||res.statusCode>=300){res.resume();return reject(new Error('Download respondeu '+res.statusCode))}const total=Number(res.headers['content-length']||0),out=fs101010.createWriteStream(tmp);let got=0;res.on('data',d=>{got+=d.length;if(total)emit101010({status:'downloading',percent:Math.round(got*100/total),message:`Baixando ${Math.round(got*100/total)}%`})});res.pipe(out);out.on('finish',()=>out.close(()=>{try{const st=fs101010.statSync(tmp);if(st.size<500000)throw new Error('Instalador baixado está incompleto');fs101010.rmSync(dest,{force:true});fs101010.renameSync(tmp,dest);resolve(dest)}catch(e){reject(e)}}));out.on('error',reject)});req.setTimeout(120000,()=>req.destroy(new Error('Tempo esgotado ao baixar atualização')));req.on('error',reject)})}
function versionGreater101010(a,b){const A=String(a).replace(/^v/,'').split('.').map(Number),B=String(b).replace(/^v/,'').split('.').map(Number);for(let i=0;i<Math.max(A.length,B.length);i++){const x=A[i]||0,y=B[i]||0;if(x!==y)return x>y}return false}
async function install101010(){const p=update101010.installer;if(!p||!fs101010.existsSync(p))throw new Error('Instalador baixado não foi encontrado. Baixe novamente.');const st=fs101010.statSync(p);if(st.size<500000)throw new Error('Instalador inválido ou incompleto.');emit101010({status:'installing',message:'Abrindo instalador...'});const child=spawn101010(p,[],{detached:true,stdio:'ignore',windowsHide:false});child.unref();setTimeout(()=>app.quit(),700);return update101010}
ipcMain.removeHandler('update101010:state');ipcMain.handle('update101010:state',()=>update101010);
ipcMain.removeHandler('update101010:action');ipcMain.handle('update101010:action',async()=>{
 try{
  if(update101010.status==='downloaded')return await install101010();
  if(update101010.status==='checking'||update101010.status==='downloading'||update101010.status==='installing')return update101010;
  emit101010({status:'checking',percent:0,message:'Verificando atualização...'});
  const rel=await jsonGet101010('https://api.github.com/repos/estevaouu-star/eletronic-store-updates/releases/latest');
  const v=String(rel?.tag_name||rel?.name||'').replace(/^v/,'');
  if(!v||!versionGreater101010(v,app.getVersion()))return emit101010({status:'current',percent:0,message:'Atualizado'});
  const assets=Array.isArray(rel.assets)?rel.assets:[];
  const asset=assets.find(a=>/setup.*x64.*\.exe$/i.test(a.name||''))||assets.find(a=>/setup.*\.exe$/i.test(a.name||''))||assets.find(a=>/\.exe$/i.test(a.name||''));
  if(!asset?.browser_download_url)throw new Error('A release '+v+' não possui instalador .exe.');
  const dest=path101010.join(app.getPath('userData'),'updates',`Eletromix-Setup-${v}.exe`);
  emit101010({status:'downloading',percent:0,message:'Baixando atualização...',availableVersion:v,installer:''});
  await download101010(asset.browser_download_url,dest);
  return emit101010({status:'downloaded',percent:100,message:'Pronto para instalar',availableVersion:v,installer:dest});
 }catch(e){console.error('[update101010]',e);return emit101010({status:'error',message:String(e?.message||e)})}
});
'''
write('electron/main.cjs',main)

js=read('public/app.js').replace('const atual="10.10.9"','const atual="10.10.10"',1)
js += r'''
// 10.10.10 - restauração de sessão pelo processo principal, não pelo localStorage.
async function saveAuth101010(){if(!window.eletromix101010||!token||!me)return;try{await window.eletromix101010.sessionSave({token,me,storeId:storeId||null})}catch(e){console.error('[auth101010 save]',e)}}
async function restoreAuth101010(){
 if(!window.eletromix101010||me)return false;
 let s=null;try{s=await window.eletromix101010.sessionRead()}catch(e){console.error('[auth101010 read]',e);return false}
 if(!s?.token||!s?.me)return false;
 token=s.token;me=s.me;if(s.storeId)storeId=s.storeId;
 try{await api('/api/lojas');showApp();await loadStores();await loadAll();return true}catch(e){console.warn('[auth101010 restore]',e);token='';me=null;try{await window.eletromix101010.sessionClear()}catch{}return false}
}
const showAppBase101010=showApp;showApp=function(){showAppBase101010();saveAuth101010()};
document.addEventListener('click',e=>{if(e.target.closest?.('#logoutBtn,[data-action="logout"],.logout-btn'))window.eletromix101010?.sessionClear?.()},true);
document.addEventListener('DOMContentLoaded',()=>restoreAuth101010());setTimeout(restoreAuth101010,60);setTimeout(restoreAuth101010,500);setTimeout(restoreAuth101010,1400);

function renderUpdate101010(s={}){const st=s.status||'idle',p=Number(s.percent||0);const labels={idle:'Verificar atualização',checking:'Verificando...',current:'Atualizado',downloading:`Baixando ${p}%`,downloaded:'Instalar atualização',installing:'Abrindo instalador...',error:'Tentar novamente'};document.querySelectorAll('#updateButton,#loginUpdateButton').forEach(b=>{b.disabled=['checking','downloading','installing'].includes(st);const t=b.querySelector('#loginUpdateText')||b.querySelector('.update-text');if(t)t.textContent=labels[st]||labels.idle;else b.textContent=labels[st]||labels.idle;b.title=st==='error'?(s.message||'Erro ao atualizar'):''})}
async function updateAction101010(){if(!window.eletromix101010)return;try{renderUpdate101010({status:'checking'});renderUpdate101010(await window.eletromix101010.updateAction())}catch(e){renderUpdate101010({status:'error',message:String(e?.message||e)})}}
forceUpdate10105=updateAction101010;try{updaterAction108=updateAction101010}catch{}
document.addEventListener('DOMContentLoaded',async()=>{if(!window.eletromix101010)return;try{window.eletromix101010.onUpdate(renderUpdate101010);renderUpdate101010(await window.eletromix101010.updateState())}catch{}});setTimeout(async()=>{if(window.eletromix101010)try{renderUpdate101010(await window.eletromix101010.updateState())}catch{}},700);
'''
write('public/app.js',js)
print('10.10.10: updater baixa instalador para pasta estável e abre o arquivo real; sessão fica em userData via Electron e é restaurada antes/depois do bootstrap.')