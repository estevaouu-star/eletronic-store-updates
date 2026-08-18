from pathlib import Path
import json

root = Path("app")


def read(path: str) -> str:
    return (root / path).read_text(encoding="utf-8")


def write(path: str, content: str) -> None:
    (root / path).write_text(content, encoding="utf-8")


pkg = json.loads(read("package.json"))
pkg["version"] = "10.10.20"
write("package.json", json.dumps(pkg, indent=2, ensure_ascii=False))

html = read("public/index.html").replace(
    'id="versionInfo" class="version-info">v10.10.19',
    'id="versionInfo" class="version-info">v10.10.20',
    1,
)
write("public/index.html", html)

main = read("electron/main.cjs")
old_auth = "function readAuth101010(){try{const x=JSON.parse(fs101010.readFileSync(authFile101010,'utf8'));if(x?.version!==app.getVersion())return null;return x}catch{return null}}"
new_auth = "function readAuth101010(){try{const x=JSON.parse(fs101010.readFileSync(authFile101010,'utf8'));return x?.token?x:null}catch{return null}}"
if old_auth not in main:
    raise SystemExit("Leitura da sessão 10.10.10 não encontrada.")
main = main.replace(old_auth, new_auth, 1)

old_remember = """  if(p?.version!==app.getVersion()){clearRemember101011();return null}
  if(!p?.login||!p?.password)return null;"""
new_remember = """  // A credencial criptografada continua válida após fechar, reabrir ou atualizar o aplicativo.
  if(!p?.login||!p?.password)return null;"""
if old_remember not in main:
    raise SystemExit("Leitura de credenciais 10.10.11 não encontrada.")
main = main.replace(old_remember, new_remember, 1)
write("electron/main.cjs", main)

js = read("public/app.js").replace(
    'const atual="10.10.19"', 'const atual="10.10.20"', 1
)
js += r'''

// 10.10.20 - sessão permanente, F2 sem bloquear Novo Cliente e duas vias térmicas separadas da OS.

// A sessão do Electron não depende da versão instalada. Confirma o token no backend
// e restaura o mesmo usuário e a mesma loja sem pedir o login novamente.
saveAuth101010=async function(){
 if(!window.eletromix101010||!token||!me)return false;
 try{return await window.eletromix101010.sessionSave({token,me,storeId:Number(lojaId)||null})}
 catch(e){console.error('[auth101020 save]',e);return false}
};
restoreAuth101010=async function(){
 if(!window.eletromix101010||me)return false;
 let s=null;try{s=await window.eletromix101010.sessionRead()}catch(e){console.error('[auth101020 read]',e);return false}
 if(!s?.token)return false;
 token=String(s.token);localStorage.setItem('es_token',token);
 if(Number(s.storeId)>0){lojaId=Number(s.storeId);localStorage.setItem('es_store_id',String(lojaId))}
 try{
  const r=await fetch('/api/me',{headers:{Authorization:'Bearer '+token,'X-Store-Id':String(lojaId)}});
  if(!r.ok)throw new Error('Sessão salva inválida');
  me=await r.json();caixaAtual=me.caixa||null;ajustarLojaAoUsuario();showApp();await boot();return true;
 }catch(e){
  console.warn('[auth101020 restore]',e);token='';me=null;localStorage.removeItem('es_token');
  try{await window.eletromix101010.sessionClear()}catch{}return false;
 }
};
document.addEventListener('DOMContentLoaded',()=>setTimeout(restoreAuth101010,10));
setTimeout(restoreAuth101010,180);setTimeout(restoreAuth101010,900);

// Monta uma notinha térmica e manda direto para o mesmo motor do comprovante do Caixa.
function osPrintText101020(row){
 const clone=row.cloneNode(true);
 clone.querySelectorAll('.os-print-actions-101015,.os-print-actions-101020,.os-via-unica-101017,button,.actions').forEach(x=>x.remove());
 return (clone.innerText||'').split('\n').map(x=>x.trim()).filter(Boolean);
}
function osReceipt101020(row,kind){
 const garantia=kind==='garantia',lines=osPrintText101020(row),today=new Date();
 let warranty=null;
 if(garantia)warranty=garantirGarantia101017(row);
 const title=garantia?'VIA DE GARANTIA':'VIA DO CLIENTE';
 const details=lines.map(line=>`<tr><td colspan="3">${escapePrint101017(line)}</td></tr>`).join('');
 const warrantyHtml=garantia?`<div class="receipt-total"><span>INÍCIO</span><span>${fmtDate101015(new Date(warranty.inicio))}</span></div><div class="receipt-total"><span>GARANTIA ATÉ</span><span>${fmtDate101015(new Date(warranty.fim))}</span></div><p>Garantia de 3 meses referente ao serviço executado nesta Ordem de Serviço.</p>`:'';
 return `<div class="receipt"><h2>ELETROMIX</h2><p>${escapePrint101017(lojaAtual101015()||'Ordem de Serviço')}</p><table><tbody><tr><th colspan="3">ORDEM DE SERVIÇO · ${title}</th></tr><tr><td colspan="3">Emitido em ${fmtDate101015(today)}</td></tr>${details}</tbody></table>${warrantyHtml}<p>________________________________</p><p>Assinatura do cliente</p></div>`;
}
let osPrintInFlight101020=false;
async function imprimirOSDireto101020(row,kind,button){
 if(!row)return;
 if(osPrintInFlight101020)return toast('A impressão da OS já foi enviada. Aguarde um instante.');
 if(!window.desktopPrinter)return toast('Módulo de impressão do Windows não está disponível.');
 const original=button?.textContent||'';osPrintInFlight101020=true;
 if(button){button.disabled=true;button.textContent='Imprimindo...'}
 try{
  loadPrinterSettings();
  const result=await window.desktopPrinter.print({html:osReceipt101020(row,kind),deviceName:printerSettings.deviceName,paperWidth:printerSettings.paperWidth,itemCount:1});
  if(!result?.success)throw new Error(result?.failureReason||'A impressora não respondeu.');
  if(result.deviceName){printerSettings.deviceName=result.deviceName;savePrinterSettings()}
  toast(kind==='garantia'?'Via de garantia enviada para a impressora.':'Via do cliente enviada para a impressora.');
 }catch(e){console.error('[OS térmica 101020]',e);toast(`Falha ao imprimir: ${String(e?.message||e)}`)}
 finally{osPrintInFlight101020=false;if(button){button.disabled=false;button.textContent=original}}
}
function syncOSPrint101020(){
 osRows101015().forEach(row=>{
  const boxes=[...row.querySelectorAll('.os-print-actions-101020')];boxes.slice(1).forEach(x=>x.remove());
  if(boxes[0])return;
  const box=document.createElement('div');box.className='os-print-actions-101020';
  box.innerHTML='<button type="button" class="secondary os-via-cliente-101020">Imprimir via do cliente</button><button type="button" class="primary os-via-garantia-101020">Imprimir via de garantia</button>';
  const host=row.matches('tr')?(row.lastElementChild||row):row;host.appendChild(box);
 });
}
document.addEventListener('click',event=>{
 const button=event.target.closest?.('.os-via-cliente-101020,.os-via-garantia-101020');
 if(button){
  event.preventDefault();event.stopImmediatePropagation();
  const row=button.closest('tr,.os-card,.ordem-card,.service-order-card,.ordem-servico-card,[data-os-id],.card');
  imprimirOSDireto101020(row,button.classList.contains('os-via-garantia-101020')?'garantia':'cliente',button);return;
 }
 if(event.target.closest?.('.nav[data-s="ordens"],.nav[data-s="ordensServico"],.nav[data-s="ordens-servico"]'))setTimeout(syncOSPrint101020,80);
},true);
new MutationObserver(()=>{if(osSec101015()?.classList.contains('active'))syncOSPrint101020()}).observe(document.documentElement,{childList:true,subtree:true});
document.addEventListener('DOMContentLoaded',()=>setTimeout(syncOSPrint101020,300));setTimeout(syncOSPrint101020,900);
'''
write("public/app.js", js)

css = read("public/style.css") + r'''

/* 10.10.20 - F2 não cobre Novo Cliente; somente as duas ações térmicas finais da OS aparecem. */
#caixa .pdv1094-field>.shortcut10100-f2{right:78px!important;pointer-events:none!important}
#caixa #newClientShortcut{position:relative;z-index:2;pointer-events:auto!important}
.os-print-actions-101015,.os-via-unica-101017{display:none!important}
.os-print-actions-101020{display:flex;gap:7px;align-items:center;justify-content:flex-end;flex-wrap:wrap;margin-top:8px}
.os-print-actions-101020 button{min-height:32px!important;padding:7px 10px!important;font-size:11px!important;white-space:nowrap}
@media(max-width:1100px){.os-print-actions-101020{justify-content:flex-start}}
'''
write("public/style.css", css)

print("10.10.20: Novo Cliente liberado, login persistente e duas vias de OS com impressão térmica direta.")
