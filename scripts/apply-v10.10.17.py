from pathlib import Path
import json
root=Path('app')
def read(p): return (root/p).read_text(encoding='utf-8')
def write(p,s): (root/p).write_text(s,encoding='utf-8')

pkg=json.loads(read('package.json'));pkg['version']='10.10.17';write('package.json',json.dumps(pkg,indent=2,ensure_ascii=False))
html=read('public/index.html').replace('id="versionInfo" class="version-info">v10.10.16','id="versionInfo" class="version-info">v10.10.17',1);write('public/index.html',html)
js=read('public/app.js').replace('const atual="10.10.16"','const atual="10.10.17"',1)
js += r'''
// 10.10.17 - unifica Via cliente + Garantia e imprime como comprovante térmico, sem abrir nova janela.
function garantirGarantia101017(row){
 const key=osKey101015(row),all=warrantyStore101015();let warranty=all[key];
 if(!warranty){const start=new Date(),expiry=addMonthsSafe101015(start,3);warranty={inicio:start.toISOString(),fim:expiry.toISOString()};all[key]=warranty;warrantySave101015(all)}
 tentarMarcarPronto101015(row);return warranty;
}
function escapePrint101017(s){return String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
function imprimirOSComprovante101017(row){
 if(!row)return;
 const warranty=garantirGarantia101017(row),today=new Date(),body=cleanOSText101015(row),loja=lojaAtual101015()||'Eletromix';
 let old=document.querySelector('#osPrintFrame101017');if(old)old.remove();
 const frame=document.createElement('iframe');frame.id='osPrintFrame101017';frame.setAttribute('aria-hidden','true');frame.style.cssText='position:fixed;right:0;bottom:0;width:1px;height:1px;border:0;opacity:0;pointer-events:none';document.body.appendChild(frame);
 const doc=frame.contentDocument||frame.contentWindow.document;
 const lines=body.split('\n').filter(Boolean).map(x=>`<div class="lineitem">${escapePrint101017(x)}</div>`).join('');
 doc.open();doc.write(`<!doctype html><html><head><meta charset="utf-8"><title>OS - Via cliente com garantia</title><style>
 @page{size:80mm auto;margin:3mm}*{box-sizing:border-box}html,body{margin:0;padding:0;background:#fff;color:#000}body{width:74mm;font-family:Arial,Helvetica,sans-serif;font-size:11px;line-height:1.3}.center{text-align:center}.brand{font-size:19px;font-weight:900;letter-spacing:.4px}.store{font-size:10px;margin-top:1px}.dash{border-top:1px dashed #000;margin:7px 0}.title{font-size:12px;font-weight:900;text-align:center}.meta{display:flex;justify-content:space-between;gap:8px;font-size:9px}.lineitem{padding:2px 0;border-bottom:1px dotted #aaa;word-break:break-word}.warranty{margin-top:7px;border:1px solid #000;padding:6px}.warranty h2{font-size:11px;margin:0 0 5px;text-align:center}.wrow{display:flex;justify-content:space-between;gap:8px;padding:2px 0}.wrow b{text-align:right}.note{font-size:9px;margin-top:5px}.signature{margin-top:17px;padding-top:4px;border-top:1px solid #000;text-align:center;font-size:9px}.footer{text-align:center;font-size:9px;margin-top:8px}.no-print{display:none!important}
 </style></head><body><div class="center"><div class="brand">ELETROMIX</div><div class="store">${escapePrint101017(loja)}</div></div><div class="dash"></div><div class="title">ORDEM DE SERVIÇO · VIA DO CLIENTE</div><div class="meta"><span>Emissão: ${fmtDate101015(today)}</span><span>Garantia: 3 meses</span></div><div class="dash"></div>${lines}<div class="warranty"><h2>GARANTIA DO SERVIÇO</h2><div class="wrow"><span>Serviço concluído:</span><b>${fmtDate101015(new Date(warranty.inicio))}</b></div><div class="wrow"><span>Garantia até:</span><b>${fmtDate101015(new Date(warranty.fim))}</b></div><div class="note">Esta via reúne a retirada do cliente e a garantia referente ao serviço executado nesta Ordem de Serviço.</div></div><div class="signature">Assinatura do cliente</div><div class="footer">Guarde este comprovante durante o período de garantia.</div></body></html>`);doc.close();
 const run=()=>{try{frame.contentWindow.focus();frame.contentWindow.print()}catch(e){console.error('[OS print 101017]',e);toast?.('Não foi possível abrir a impressão.')}setTimeout(()=>frame.remove(),1200)};
 if(doc.readyState==='complete')setTimeout(run,120);else frame.onload=()=>setTimeout(run,120);
}
function unificarBotoesOS101017(){
 osRows101015().forEach(row=>{
  const box=row.querySelector('.os-print-actions-101015');if(!box)return;
  box.innerHTML='<button type="button" class="primary os-via-unica-101017">Imprimir via cliente + garantia</button>';
 });
}
document.addEventListener('click',e=>{const b=e.target.closest?.('.os-via-unica-101017');if(!b)return;e.preventDefault();e.stopImmediatePropagation();imprimirOSComprovante101017(b.closest('tr,.os-card,.ordem-card,.service-order-card,.ordem-servico-card,[data-os-id],.card'))},true);
new MutationObserver(()=>{if(osSec101015()?.classList.contains('active'))setTimeout(unificarBotoesOS101017,0)}).observe(document.documentElement,{childList:true,subtree:true});
document.addEventListener('DOMContentLoaded',()=>setTimeout(unificarBotoesOS101017,350));setTimeout(unificarBotoesOS101017,1000);
'''
write('public/app.js',js)
css=read('public/style.css')+r'''
/* 10.10.17 - ação única de OS */
.os-print-actions-101015 .os-via-unica-101017{white-space:nowrap;min-height:31px!important}
'''
write('public/style.css',css)
print('10.10.17: Via cliente e garantia unificadas; impressão no estilo comprovante térmico 80mm por iframe oculto, sem abrir nova janela.')