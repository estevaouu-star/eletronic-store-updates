from pathlib import Path
import json

root = Path("app")


def read(path: str) -> str:
    return (root / path).read_text(encoding="utf-8")


def write(path: str, content: str) -> None:
    (root / path).write_text(content, encoding="utf-8")


pkg = json.loads(read("package.json"))
pkg["version"] = "10.10.21"
nsis = pkg.setdefault("build", {}).setdefault("nsis", {})
nsis["oneClick"] = True
nsis["perMachine"] = False
nsis["allowToChangeInstallationDirectory"] = False
nsis["runAfterFinish"] = True
write("package.json", json.dumps(pkg, indent=2, ensure_ascii=False))

html = read("public/index.html").replace(
    'id="versionInfo" class="version-info">v10.10.20',
    'id="versionInfo" class="version-info">v10.10.21',
    1,
)
write("public/index.html", html)

main = read("electron/main.cjs")
main = main.replace(
    'let quitting = false;',
    '''let quitting = false;

// 10.10.21 - uma única instância. Reabrir o atalho mostra a janela já autenticada.
if(!app.requestSingleInstanceLock())app.exit(0);
app.on("second-instance",()=>{
  if(mainWindow){
    if(mainWindow.isMinimized())mainWindow.restore();
    mainWindow.show();mainWindow.focus();
  }
});''',
    1,
)
main = main.replace('autoUpdater.quitAndInstall(false,true)', 'autoUpdater.quitAndInstall(true,true)', 1)
main = main.replace('eletromixAutoUpdater108.quitAndInstall(false,true)', 'eletromixAutoUpdater108.quitAndInstall(true,true)', 1)

old_install = "async function install101010(){const p=update101010.installer;if(!p||!fs101010.existsSync(p))throw new Error('Instalador baixado não foi encontrado. Baixe novamente.');const st=fs101010.statSync(p);if(st.size<500000)throw new Error('Instalador inválido ou incompleto.');emit101010({status:'installing',message:'Abrindo instalador...'});const child=spawn101010(p,[],{detached:true,stdio:'ignore',windowsHide:false});child.unref();setTimeout(()=>app.quit(),700);return update101010}"
new_install = "async function install101010(){const p=update101010.installer;if(!p||!fs101010.existsSync(p))throw new Error('Instalador baixado não foi encontrado. Baixe novamente.');const st=fs101010.statSync(p);if(st.size<500000)throw new Error('Instalador inválido ou incompleto.');emit101010({status:'installing',message:'Instalando e reiniciando...'});const child=spawn101010(p,['/S','--updated','--force-run'],{detached:true,stdio:'ignore',windowsHide:true});child.unref();setTimeout(()=>{quitting=true;app.quit()},700);return update101010}"
if old_install not in main:
    raise SystemExit("Instalador 10.10.10 não encontrado.")
main = main.replace(old_install, new_install, 1)

old_download_end = """  await download101010(asset.browser_download_url,dest);
  return emit101010({status:'downloaded',percent:100,message:'Pronto para instalar',availableVersion:v,installer:dest});"""
new_download_end = """  await download101010(asset.browser_download_url,dest);
  emit101010({status:'downloaded',percent:100,message:'Download concluído',availableVersion:v,installer:dest});
  return await install101010();"""
if old_download_end not in main:
    raise SystemExit("Final do download 10.10.10 não encontrado.")
main = main.replace(old_download_end, new_download_end, 1)

main += r'''

// 10.10.21 - fecha o aplicativo somente depois de a sessão ter sido salva pelo frontend.
ipcMain.removeHandler('app101021:quit');
ipcMain.handle('app101021:quit',()=>{
 setTimeout(()=>{quitting=true;app.quit()},120);
 return {ok:true};
});
'''
write("electron/main.cjs", main)

preload = read("electron/preload.cjs") + r'''

// 10.10.21 - encerramento controlado, sem transformar Sair em logout.
try{
 const {contextBridge:cb101021,ipcRenderer:ir101021}=require('electron');
 cb101021.exposeInMainWorld('eletromixApp101021',{quit:()=>ir101021.invoke('app101021:quit')});
}catch(e){console.error('[app101021 preload]',e)}
'''
write("electron/preload.cjs", preload)

js = read("public/app.js").replace(
    'const atual="10.10.20"', 'const atual="10.10.21"', 1
)
js += r'''

// 10.10.21 - Sair fecha o Eletromix, mas não apaga login, token ou credencial lembrada.
// O listener fica no window para executar antes dos listeners antigos do document.
window.addEventListener('click',event=>{
 const button=event.target.closest?.('#logoutBtn,[data-action="logout"],.logout-btn');
 if(!button)return;
 event.preventDefault();event.stopPropagation();event.stopImmediatePropagation();
 (async()=>{
  try{
   gravarSessao10109();
   await saveAuth101010();
   if(window.eletromixApp101021?.quit)await window.eletromixApp101021.quit();
   else window.close();
  }catch(e){console.error('[sair 101021]',e);window.close()}
 })();
},true);
'''
write("public/app.js", js)

print("10.10.21: Sair mantém login, instância única e atualização silenciosa com reinício automático.")
