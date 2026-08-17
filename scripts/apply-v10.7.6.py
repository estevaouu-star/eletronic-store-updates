from pathlib import Path
import json

root=Path('app')
def read(p): return (root/p).read_text(encoding='utf-8')
def write(p,s): (root/p).write_text(s,encoding='utf-8')
def must(s,a,b,label):
    if a not in s: raise RuntimeError(f'Trecho nao encontrado: {label}')
    return s.replace(a,b,1)

# Versão
pkg=json.loads(read('package.json'))
pkg['version']='10.7.6'
write('package.json',json.dumps(pkg,indent=2,ensure_ascii=False))

# Versão exibida no aplicativo.
html=read('public/index.html')
html=html.replace('id="versionInfo" class="version-info">v10.7.5','id="versionInfo" class="version-info">v10.7.6')
write('public/index.html',html)

# O código principal de impressão já existia, mas o preload não expunha desktopPrinter
# para a interface. Sem esta ponte, listar/testar/imprimir nunca chegava ao Electron.
preload=read('electron/preload.cjs')
if 'desktopPrinter' not in preload:
    preload += '''\ncontextBridge.exposeInMainWorld("desktopPrinter",{\n list:()=>ipcRenderer.invoke("printer:list"),\n print:(payload)=>ipcRenderer.invoke("printer:print",payload)\n});\n'''
write('electron/preload.cjs',preload)

# Torna o backend Electron de impressão mais tolerante a impressora renomeada/desconectada,
# espera logos carregarem e usa altura real do comprovante para bobinas 58/80 mm.
main=read('electron/main.cjs')
old='''ipcMain.handle("printer:list", async () => {
  if (!mainWindow) return [];
  const printers = await mainWindow.webContents.getPrintersAsync();
  return printers.map(p => ({
    name: p.name,
    displayName: p.displayName || p.name,
    description: p.description || "",
    status: p.status,
    isDefault: Boolean(p.isDefault)
  }));
});

ipcMain.handle("printer:print", async (_event, payload = {}) => {
  let deviceName = String(payload.deviceName || "");
  if(!deviceName && mainWindow){
    const available=await mainWindow.webContents.getPrintersAsync();
    const preferred=available.find(p=>/epson|tm-|thermal|receipt|pos/i.test(`${p.name} ${p.displayName||""} ${p.description||""}`)) || available.find(p=>p.isDefault);
    if(preferred)deviceName=preferred.name;
  }
  const width = Number(payload.paperWidth) === 58 ? 58 : 80;
  const itemCount = Math.max(1, Number(payload.itemCount) || 1);
  const heightMm = Math.min(900, Math.max(140, 100 + itemCount * 13));
  const printWindow = new BrowserWindow({
    show: false,
    webPreferences: { contextIsolation: true, sandbox: true }
  });

  try {
    const html = receiptPrintHtml(String(payload.html || ""), width);
    await printWindow.loadURL(`data:text/html;charset=utf-8,${encodeURIComponent(html)}`);
    await new Promise(resolve => setTimeout(resolve, 120));

    const result = await new Promise(resolve => {
      printWindow.webContents.print({
        silent: true,
        printBackground: true,
        deviceName: deviceName || undefined,
        margins: { marginType: "none" },
        pageSize: { width: width * 1000, height: heightMm * 1000 }
      }, (success, failureReason) => resolve({ success, failureReason: failureReason || "" }));
    });
    return result;
  } catch (err) {
    return { success: false, failureReason: String(err?.message || err) };
  } finally {
    if (!printWindow.isDestroyed()) printWindow.destroy();
  }
});'''
new='''ipcMain.handle("printer:list", async () => {
  try {
    if (!mainWindow) return [];
    const printers = await mainWindow.webContents.getPrintersAsync();
    return printers.map(p => ({
      name: p.name,
      displayName: p.displayName || p.name,
      description: p.description || "",
      status: p.status,
      isDefault: Boolean(p.isDefault)
    }));
  } catch (err) {
    console.error("[printer] Falha ao listar impressoras:", err);
    return [];
  }
});

ipcMain.handle("printer:print", async (_event, payload = {}) => {
  const width = Number(payload.paperWidth) === 58 ? 58 : 80;
  let deviceName = String(payload.deviceName || "").trim();
  let available = [];
  try { available = mainWindow ? await mainWindow.webContents.getPrintersAsync() : []; } catch {}

  // Se a impressora salva mudou de nome, foi reinstalada ou desconectou, escolhe novamente.
  if(deviceName && !available.some(p=>p.name===deviceName)) deviceName="";
  if(!deviceName){
    const preferred = available.find(p=>/epson|bematech|elgin|daruma|control.?id|thermal|t[eé]rmica|receipt|pos|tm-|mp-/i.test(`${p.name} ${p.displayName||""} ${p.description||""}`))
      || available.find(p=>p.isDefault)
      || available[0];
    if(preferred) deviceName=preferred.name;
  }
  if(!deviceName) return {success:false,failureReason:"Nenhuma impressora instalada foi encontrada pelo Windows."};

  const printWindow = new BrowserWindow({
    show: false,
    width: 520,
    height: 900,
    webPreferences: { contextIsolation: true, sandbox: true }
  });

  try {
    const html = receiptPrintHtml(String(payload.html || ""), width);
    await printWindow.loadURL(`data:text/html;charset=utf-8,${encodeURIComponent(html)}`);

    // Aguarda fontes/imagens (principalmente a logo do comprovante) antes de imprimir.
    await printWindow.webContents.executeJavaScript(`Promise.all(Array.from(document.images||[]).map(img=>img.complete?Promise.resolve():new Promise(r=>{img.onload=r;img.onerror=r}))).then(()=>true)`);
    await new Promise(resolve => setTimeout(resolve, 180));

    // Calcula a altura real do comprovante para evitar páginas gigantes ou corte em bobina.
    const px = await printWindow.webContents.executeJavaScript(`Math.max(document.body?.scrollHeight||0,document.documentElement?.scrollHeight||0,220)`);
    const heightMm = Math.min(600, Math.max(60, Math.ceil(Number(px||220) * 25.4 / 96 + 8)));

    const result = await new Promise(resolve => {
      printWindow.webContents.print({
        silent: true,
        printBackground: true,
        deviceName,
        margins: { marginType: "none" },
        pageSize: { width: width * 1000, height: heightMm * 1000 }
      }, (success, failureReason) => resolve({ success, failureReason: failureReason || "", deviceName, paperWidth: width }));
    });
    if(!result.success) console.error("[printer] Falha:", result.failureReason, "device=",deviceName);
    return result;
  } catch (err) {
    console.error("[printer] Erro ao imprimir:", err);
    return { success: false, failureReason: String(err?.message || err), deviceName };
  } finally {
    if (!printWindow.isDestroyed()) printWindow.destroy();
  }
});'''
main=must(main,old,new,'handlers de impressao Electron')
write('electron/main.cjs',main)

# Frontend: trata erros corretamente, atualiza status e corrige o nome do teste.
js=read('public/app.js')
js=js.replace('const atual="10.7.5"','const atual="10.7.6"')
old_direct='''async function directPrintReceipt(){
  if(!window.desktopPrinter)return toast("Impressão direta disponível somente no aplicativo Windows.");
  if(!printerSettings.deviceName){await refreshPrinters();if(!printerSettings.deviceName)return toast("Selecione uma impressora em Configurações.")}
  const payload=receiptPrintPayload();if(!payload)return toast("Comprovante não encontrado.");
  const status=$("#printerStatus");if(status)status.textContent="Enviando para a impressora...";
  const r=await window.desktopPrinter.print(payload);
  if(r?.success){if(status)status.textContent="Comprovante enviado para a impressora.";toast("Comprovante impresso.")}else{if(status)status.textContent="Falha na impressão.";toast(`Falha ao imprimir: ${r?.failureReason||"erro desconhecido"}`)}
}'''
new_direct='''async function directPrintReceipt(){
  if(!window.desktopPrinter)return toast("Módulo de impressão do Windows não está disponível.");
  try{
    if(!printerSettings.deviceName){await refreshPrinters();if(!printerSettings.deviceName)return toast("Selecione uma impressora em Configurações.")}
    const payload=receiptPrintPayload();if(!payload)return toast("Comprovante não encontrado.");
    const status=$("#printerStatus");if(status)status.textContent="Enviando para a impressora...";
    const r=await window.desktopPrinter.print(payload);
    if(r?.success){
      if(r.deviceName && r.deviceName!==printerSettings.deviceName){printerSettings.deviceName=r.deviceName;savePrinterSettings();}
      if(status)status.textContent=`Impresso em ${r.deviceName||printerSettings.deviceName}.`;
      toast("Comprovante enviado para a impressora.");
    }else{
      const motivo=r?.failureReason||"erro desconhecido";
      if(status)status.textContent=`Falha: ${motivo}`;
      toast(`Falha ao imprimir: ${motivo}`);
    }
  }catch(err){
    console.error("Falha na impressão",err);
    const motivo=String(err?.message||err||"erro desconhecido");
    if($("#printerStatus"))$("#printerStatus").textContent=`Falha: ${motivo}`;
    toast(`Falha ao imprimir: ${motivo}`);
  }
}'''
js=must(js,old_direct,new_direct,'directPrintReceipt')
js=js.replace('<div class="receipt"><h2>Eletronic Store</h2><p>TESTE DE IMPRESSÃO</p>','<div class="receipt"><h2>ELETROMIX</h2><p>TESTE DE IMPRESSÃO</p>')
write('public/app.js',js)

print('Patch 10.7.6 aplicado: ponte Electron de impressão restaurada e impressão térmica 58/80 mm reforçada.')
