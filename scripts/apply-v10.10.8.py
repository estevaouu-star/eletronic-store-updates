from pathlib import Path
import json
root=Path('app')
def read(p): return (root/p).read_text(encoding='utf-8')
def write(p,s): (root/p).write_text(s,encoding='utf-8')

pkg=json.loads(read('package.json'))
pkg['version']='10.10.8'
pkg.setdefault('dependencies',{})
pkg['dependencies'].setdefault('electron-updater','^6.3.9')
write('package.json',json.dumps(pkg,indent=2,ensure_ascii=False))

html=read('public/index.html').replace('id="versionInfo" class="version-info">v10.10.7','id="versionInfo" class="version-info">v10.10.8',1)
write('public/index.html',html)

# Bridge dedicado, sem depender dos nomes/implementacoes antigas que ficaram inconsistentes.
preload_path=None
for candidate in ['electron/preload.cjs','electron/preload.js']:
    if (root/candidate).exists(): preload_path=candidate; break
if not preload_path: raise RuntimeError('Preload Electron nao encontrado')
preload=read(preload_path)
if 'eletromixUpdater108' not in preload:
    preload += r'''

// 10.10.8 - bridge dedicado do atualizador
try {
  const {contextBridge: cb108, ipcRenderer: ir108}=require('electron');
  cb108.exposeInMainWorld('eletromixUpdater108',{
    action:()=>ir108.invoke('updater108:action'),
    status:()=>ir108.invoke('updater108:status'),
    onState:(fn)=>{const h=(_e,s)=>fn(s);ir108.on('updater108:state',h);return()=>ir108.removeListener('updater108:state',h)}
  });
} catch(e) { console.error('[updater108 preload]',e); }
'''
write(preload_path,preload)

main=read('electron/main.cjs')
if 'updater108:action' not in main:
    main += r'''

// 10.10.8 - atualizador interno independente do frontend legado
const {autoUpdater:eletromixAutoUpdater108}=require('electron-updater');
let eletromixUpdate108={status:'idle',version:app.getVersion(),percent:0,message:''};
function emitUpdate108(patch={}){
  eletromixUpdate108={...eletromixUpdate108,...patch};
  try{if(mainWindow&&!mainWindow.isDestroyed())mainWindow.webContents.send('updater108:state',eletromixUpdate108)}catch{}
  return eletromixUpdate108;
}
eletromixAutoUpdater108.autoDownload=false;
eletromixAutoUpdater108.autoInstallOnAppQuit=true;
eletromixAutoUpdater108.on('checking-for-update',()=>emitUpdate108({status:'checking',message:'Verificando atualização...',percent:0}));
eletromixAutoUpdater108.on('update-not-available',i=>emitUpdate108({status:'current',availableVersion:i?.version||app.getVersion(),message:'Atualizado',percent:0}));
eletromixAutoUpdater108.on('update-available',async i=>{
  emitUpdate108({status:'available',availableVersion:i?.version||'',message:'Atualização encontrada',percent:0});
  try{emitUpdate108({status:'downloading',message:'Baixando atualização...',percent:0});await eletromixAutoUpdater108.downloadUpdate()}
  catch(e){emitUpdate108({status:'error',message:String(e?.message||e)})}
});
eletromixAutoUpdater108.on('download-progress',p=>emitUpdate108({status:'downloading',percent:Math.max(0,Math.min(100,Math.round(p?.percent||0))),message:`Baixando ${Math.round(p?.percent||0)}%`}));
eletromixAutoUpdater108.on('update-downloaded',i=>emitUpdate108({status:'downloaded',availableVersion:i?.version||'',percent:100,message:'Pronto para instalar'}));
eletromixAutoUpdater108.on('error',e=>emitUpdate108({status:'error',message:String(e?.message||e)}));
ipcMain.removeHandler('updater108:status');ipcMain.handle('updater108:status',()=>eletromixUpdate108);
ipcMain.removeHandler('updater108:action');ipcMain.handle('updater108:action',async()=>{
  try{
    if(eletromixUpdate108.status==='downloaded'){
      emitUpdate108({status:'installing',message:'Instalando atualização...'});
      setTimeout(()=>eletromixAutoUpdater108.quitAndInstall(false,true),250);
      return eletromixUpdate108;
    }
    if(eletromixUpdate108.status==='downloading'||eletromixUpdate108.status==='checking')return eletromixUpdate108;
    emitUpdate108({status:'checking',message:'Verificando atualização...',percent:0});
    await eletromixAutoUpdater108.checkForUpdates();
    return eletromixUpdate108;
  }catch(e){return emitUpdate108({status:'error',message:String(e?.message||e)})}
});
'''
write('electron/main.cjs',main)

js=read('public/app.js').replace('const atual="10.10.7"','const atual="10.10.8"',1)
js += r'''
// 10.10.8 - botao Atualizar ligado somente ao bridge dedicado acima.
function renderUpdater108(s={}){
 const status=s.status||'idle',pct=Number(s.percent||0);
 const labels={idle:'Verificar atualização',checking:'Verificando...',current:'Atualizado',available:'Atualização encontrada',downloading:`Baixando ${pct}%`,downloaded:'Instalar atualização',installing:'Instalando...',error:'Tentar novamente'};
 document.querySelectorAll('#updateButton,#loginUpdateButton').forEach(b=>{
   b.disabled=status==='checking'||status==='downloading'||status==='installing';
   const text=b.querySelector('#loginUpdateText')||b.querySelector('.update-text');
   if(text)text.textContent=labels[status]||labels.idle;else b.textContent=labels[status]||labels.idle;
   b.dataset.update108=status;
   if(status==='error')b.title=s.message||'Falha ao atualizar';else b.removeAttribute('title');
 });
}
async function updaterAction108(){
 if(!window.eletromixUpdater108){toast?.('Atualizador interno indisponível.');return}
 try{renderUpdater108({status:'checking'});renderUpdater108(await window.eletromixUpdater108.action())}
 catch(e){console.error('[updater108]',e);renderUpdater108({status:'error',message:String(e?.message||e)})}
}
// Substitui a funcao usada pelos listeners das versoes anteriores.
forceUpdate10105=updaterAction108;
document.addEventListener('DOMContentLoaded',async()=>{
 if(!window.eletromixUpdater108)return;
 try{window.eletromixUpdater108.onState(renderUpdater108);renderUpdater108(await window.eletromixUpdater108.status())}catch(e){console.error('[updater108 init]',e)}
});
setTimeout(async()=>{if(window.eletromixUpdater108)try{renderUpdater108(await window.eletromixUpdater108.status())}catch{}},700);
'''
write('public/app.js',js)
print('10.10.8: atualizador interno reconstruido com bridge IPC dedicado, download automatico e instalacao pelo proprio app.')