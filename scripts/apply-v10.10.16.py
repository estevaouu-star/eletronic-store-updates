from pathlib import Path
import json
root=Path('app')
def read(p): return (root/p).read_text(encoding='utf-8')
def write(p,s): (root/p).write_text(s,encoding='utf-8')

pkg=json.loads(read('package.json'));pkg['version']='10.10.16';write('package.json',json.dumps(pkg,indent=2,ensure_ascii=False))
html=read('public/index.html').replace('id="versionInfo" class="version-info">v10.10.15','id="versionInfo" class="version-info">v10.10.16',1);write('public/index.html',html)

# Personalização por loja: vendedor pode salvar na própria loja, como já ocorre nas demais rotinas operacionais.
server=read('src/server.ts')
server=server.replace('app.put("/api/aparencia",auth,admin,(req,res)=>{','app.put("/api/aparencia",auth,(req,res)=>{',1)
write('src/server.ts',server)

js=read('public/app.js').replace('const atual="10.10.15"','const atual="10.10.16"',1)
js += r'''
// 10.10.16 - Personalização: confirma o estado salvo por loja e restaura ao reabrir a aba.
function lojaKey101016(){try{return String(storeId||document.querySelector('#storeSelect')?.value||'default')}catch{return 'default'}}
function persKey101016(){return 'eletromix_personalizacao_'+lojaKey101016()}
function personalizacaoSection101016(){
 const active=[...document.querySelectorAll('.section.active')];
 let sec=active.find(s=>/personal/i.test((s.id||'')+' '+(s.textContent||'').slice(0,300)));
 if(sec)return sec;
 const nav=[...document.querySelectorAll('.nav')].find(n=>/personal/i.test(n.textContent||''));
 const id=nav?.dataset?.s;if(id)sec=document.getElementById(id);
 return sec||document.querySelector('#personalizacao,#personalizar,#customizacao,#customization');
}
function collectPers101016(){
 const sec=personalizacaoSection101016();if(!sec)return null;
 const data={};
 sec.querySelectorAll('input,select,textarea').forEach((el,i)=>{
   const type=(el.type||'').toLowerCase();if(type==='file'||type==='password')return;
   const k=el.name||el.id||('field_'+i);if(!k)return;
   if(type==='checkbox'||type==='radio')data[k]={kind:type,checked:!!el.checked,value:el.value};
   else data[k]={kind:'value',value:el.value};
 });
 return data;
}
function savePers101016(){const d=collectPers101016();if(!d)return false;try{localStorage.setItem(persKey101016(),JSON.stringify(d));return true}catch{return false}}
function restorePers101016(){
 const sec=personalizacaoSection101016();if(!sec)return false;let d=null;try{d=JSON.parse(localStorage.getItem(persKey101016())||'null')}catch{return false}if(!d)return false;
 sec.querySelectorAll('input,select,textarea').forEach((el,i)=>{const type=(el.type||'').toLowerCase();if(type==='file'||type==='password')return;const k=el.name||el.id||('field_'+i),v=d[k];if(!v)return;if(v.kind==='checkbox'||v.kind==='radio')el.checked=!!v.checked;else if(v.value!=null)el.value=v.value;try{el.dispatchEvent(new Event('input',{bubbles:true}));el.dispatchEvent(new Event('change',{bubbles:true}))}catch{}});return true;
}
function isSavePersonalizacao101016(btn){const sec=personalizacaoSection101016();if(!sec||!btn||!sec.contains(btn))return false;const t=((btn.textContent||'')+' '+(btn.id||'')+' '+(btn.className||'')).toLowerCase();return /salvar|save|aplicar/.test(t)}
document.addEventListener('click',e=>{const nav=e.target.closest?.('.nav');if(nav&&/personal/i.test(nav.textContent||''))setTimeout(restorePers101016,120);const btn=e.target.closest?.('button,input[type="submit"]');if(isSavePersonalizacao101016(btn))setTimeout(()=>savePers101016(),180)},true);
document.addEventListener('submit',e=>{const sec=personalizacaoSection101016();if(sec&&sec.contains(e.target))setTimeout(savePers101016,180)},true);

// 10.10.16 - Ordem de Serviço usa EXATAMENTE o mesmo mecanismo de impressão térmica do comprovante.
// A rotina antiga de window.open/print da 10.10.15 é removida visualmente e não é mais chamada.
try{injectOSPrint101015=function(){document.querySelectorAll('.os-print-actions-101015').forEach(x=>x.remove())}}catch{}
function limparOSPrintAntigo101016(){document.querySelectorAll('.os-print-actions-101015').forEach(x=>x.remove())}
function osHtmlTermico101016(row,withWarranty){
 const key=osKey101015(row),body=cleanOSText101015(row),today=new Date();let warranty=null;
 if(withWarranty){tentarMarcarPronto101015(row);const all=warrantyStore101015();warranty=all[key];if(!warranty){const start=today,expiry=addMonthsSafe101015(start,3);warranty={inicio:start.toISOString(),fim:expiry.toISOString()};all[key]=warranty;warrantySave101015(all)}}
 const title=withWarranty?'VIA COM GARANTIA':'VIA DO CLIENTE';
 const garantia=withWarranty?`<div class="sep"></div><div><b>GARANTIA DO SERVIÇO</b></div><div>Conclusão: ${fmtDate101015(new Date(warranty.inicio))}</div><div>Válida até: ${fmtDate101015(new Date(warranty.fim))}</div><div>Prazo: 3 meses</div>`:'';
 return `<div class="receipt"><div class="receipt-title"><b>ELETROMIX</b></div><div>${esc(lojaAtual101015())}</div><div class="sep"></div><div><b>ORDEM DE SERVIÇO - ${title}</b></div><div class="sep"></div><div style="white-space:pre-wrap">${esc(body)}</div>${garantia}<div class="sep"></div><div>Emitido em ${fmtDate101015(today)}</div><div style="margin-top:14px">____________________________</div><div>Cliente</div></div>`;
}
async function imprimirOSTermica101016(row,withWarranty=false){
 if(!row)return toast('Ordem de Serviço não encontrada.');
 if(!window.desktopPrinter?.print)return toast('Impressão direta disponível somente no aplicativo Windows.');
 try{
   if(!printerSettings?.deviceName && typeof refreshPrinters==='function')await refreshPrinters();
   if(!printerSettings?.deviceName)return toast('Selecione uma impressora em Configurações.');
   const result=await window.desktopPrinter.print({html:osHtmlTermico101016(row,withWarranty),deviceName:printerSettings.deviceName,paperWidth:Number(printerSettings.paperWidth)===58?58:80,itemCount:withWarranty?18:13});
   if(result?.success)toast(withWarranty?'Via com garantia impressa.':'Via do cliente impressa.');else toast(`Falha ao imprimir: ${result?.failureReason||'erro desconhecido'}`);
 }catch(err){console.error('[OS print]',err);toast(`Falha ao imprimir: ${err?.message||err}`)}
}
function injectOSPrint101016(){
 limparOSPrintAntigo101016();
 osRows101015().forEach(row=>{
   if(row.querySelector('.os-print-101016'))return;
   const actions=row.querySelector('.row-actions,.actions,.os-actions')||row;
   const cliente=document.createElement('button');cliente.type='button';cliente.className='secondary small os-print-101016 os-via-cliente-101016';cliente.textContent='Imprimir via cliente';
   const garantia=document.createElement('button');garantia.type='button';garantia.className='secondary small os-print-101016 os-via-garantia-101016';garantia.textContent='Imprimir garantia';
   actions.appendChild(cliente);actions.appendChild(garantia);
 });
}
document.addEventListener('click',e=>{
 const c=e.target.closest?.('.os-via-cliente-101016');if(c){e.preventDefault();e.stopPropagation();return imprimirOSTermica101016(c.closest('tr,.os-card,.ordem-card,.service-order-card,.ordem-servico-card,[data-os-id],.card'),false)}
 const g=e.target.closest?.('.os-via-garantia-101016');if(g){e.preventDefault();e.stopPropagation();return imprimirOSTermica101016(g.closest('tr,.os-card,.ordem-card,.service-order-card,.ordem-servico-card,[data-os-id],.card'),true)}
 if(e.target.closest?.('.nav[data-s="ordens"],.nav[data-s="ordensServico"],.nav[data-s="ordens-servico"]'))setTimeout(injectOSPrint101016,100);
},true);
new MutationObserver(()=>{limparOSPrintAntigo101016();if(osSec101015()?.classList.contains('active'))injectOSPrint101016()}).observe(document.documentElement,{childList:true,subtree:true});
setTimeout(injectOSPrint101016,600);
'''
write('public/app.js',js)
css=read('public/style.css')+r'''
/* 10.10.16 */
.os-print-actions-101015{display:none!important}.os-print-101016{margin-left:6px!important;white-space:nowrap}
'''
write('public/style.css',css)
print('10.10.16: Personalização salva por loja; OS deixa de abrir impressão do navegador e usa o mesmo motor térmico do comprovante.')