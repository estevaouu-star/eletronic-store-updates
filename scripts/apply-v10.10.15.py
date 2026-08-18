from pathlib import Path
import json
root=Path('app')
def read(p): return (root/p).read_text(encoding='utf-8')
def write(p,s): (root/p).write_text(s,encoding='utf-8')

pkg=json.loads(read('package.json'));pkg['version']='10.10.15';write('package.json',json.dumps(pkg,indent=2,ensure_ascii=False))
html=read('public/index.html').replace('id="versionInfo" class="version-info">v10.10.14','id="versionInfo" class="version-info">v10.10.15',1);write('public/index.html',html)
js=read('public/app.js').replace('const atual="10.10.14"','const atual="10.10.15"',1)
js += r'''
// 10.10.15 - vias de Ordem de Serviço: cliente e garantia de 3 meses.
const OS_GARANTIA_KEY_101015='eletromix_os_garantias_v1';
function osSec101015(){return document.querySelector('#ordens,#ordensServico,#ordens-servico,#ordensDeServico')}
function fmtDate101015(d){return new Intl.DateTimeFormat('pt-BR').format(d)}
function addMonthsSafe101015(date,months){
 const d=new Date(date);const day=d.getDate();d.setDate(1);d.setMonth(d.getMonth()+months);const last=new Date(d.getFullYear(),d.getMonth()+1,0).getDate();d.setDate(Math.min(day,last));return d;
}
function warrantyStore101015(){try{return JSON.parse(localStorage.getItem(OS_GARANTIA_KEY_101015)||'{}')||{}}catch{return {}}}
function warrantySave101015(x){try{localStorage.setItem(OS_GARANTIA_KEY_101015,JSON.stringify(x))}catch{}}
function osKey101015(el){
 const direct=el.dataset?.id||el.dataset?.osId||el.getAttribute?.('data-os-id')||el.getAttribute?.('data-id');if(direct)return String(direct);
 const text=(el.innerText||'').replace(/\s+/g,' ').trim();const m=text.match(/(?:OS|Ordem|#)\s*#?\s*(\d{1,12})/i);if(m)return m[1];
 let h=0;for(const c of text.slice(0,400))h=((h<<5)-h+c.charCodeAt(0))|0;return 'row-'+Math.abs(h);
}
function cleanOSText101015(el){
 const clone=el.cloneNode(true);clone.querySelectorAll('.os-print-actions-101015,button,.actions').forEach(x=>x.remove());
 return (clone.innerText||'').split('\n').map(s=>s.trim()).filter(Boolean).join('\n');
}
function lojaAtual101015(){return document.querySelector('#storeSelect,#lojaSelect')?.selectedOptions?.[0]?.textContent?.trim()||document.querySelector('.store-select select')?.selectedOptions?.[0]?.textContent?.trim()||''}
function tentarMarcarPronto101015(row){
 const sel=[...row.querySelectorAll('select')].find(s=>[...s.options].some(o=>/pronto|conclu[ií]d/i.test(o.textContent||'')));
 if(!sel)return;
 const opt=[...sel.options].find(o=>/pronto|conclu[ií]d/i.test(o.textContent||''));if(!opt)return;
 if(sel.value!==opt.value){sel.value=opt.value;sel.dispatchEvent(new Event('change',{bubbles:true}))}
}
function printOS101015(row,withWarranty=false){
 const key=osKey101015(row),body=cleanOSText101015(row),today=new Date();let warranty=null;
 if(withWarranty){
  tentarMarcarPronto101015(row);
  const all=warrantyStore101015();warranty=all[key];
  if(!warranty){const start=today,expiry=addMonthsSafe101015(start,3);warranty={inicio:start.toISOString(),fim:expiry.toISOString()};all[key]=warranty;warrantySave101015(all)}
 }
 const title=withWarranty?'ORDEM DE SERVIÇO · VIA COM GARANTIA':'ORDEM DE SERVIÇO · VIA DO CLIENTE';
 const garantia=withWarranty?`<section class="warranty"><h2>Garantia do serviço</h2><div class="dates"><div><span>Serviço concluído em</span><b>${fmtDate101015(new Date(warranty.inicio))}</b></div><div><span>Garantia válida até</span><b>${fmtDate101015(new Date(warranty.fim))}</b></div></div><p>Garantia de 3 meses referente ao serviço executado nesta Ordem de Serviço.</p></section>`:'';
 const win=window.open('','_blank','width=850,height=900');if(!win){toast?.('Permita a janela de impressão para gerar a via.');return}
 win.document.write(`<!doctype html><html><head><meta charset="utf-8"><title>${title}</title><style>@page{margin:12mm}*{box-sizing:border-box}body{font-family:Arial,sans-serif;color:#111;margin:0;font-size:13px}.head{display:flex;justify-content:space-between;align-items:flex-start;border-bottom:3px solid #111;padding-bottom:10px;margin-bottom:14px}.brand{font-size:26px;font-weight:900}.meta{text-align:right;color:#444}.title{font-size:18px;font-weight:900;margin:10px 0}.osdata{white-space:pre-wrap;border:1px solid #bbb;border-radius:8px;padding:14px;line-height:1.45}.warranty{margin-top:16px;border:2px solid #111;border-radius:9px;padding:14px}.warranty h2{margin:0 0 10px;font-size:17px}.dates{display:grid;grid-template-columns:1fr 1fr;gap:12px}.dates div{border:1px solid #bbb;border-radius:7px;padding:10px}.dates span{display:block;font-size:11px;color:#555;margin-bottom:4px}.dates b{font-size:16px}.sign{margin-top:34px;display:grid;grid-template-columns:1fr 1fr;gap:40px}.line{border-top:1px solid #111;padding-top:5px;text-align:center;font-size:11px}</style></head><body><div class="head"><div><div class="brand">Eletromix</div><div>${lojaAtual101015()}</div></div><div class="meta">Emitido em ${fmtDate101015(today)}</div></div><div class="title">${title}</div><div class="osdata"></div>${garantia}<div class="sign"><div class="line">Responsável / Loja</div><div class="line">Cliente</div></div><script>document.querySelector('.osdata').textContent=${JSON.stringify(body)};window.onload=()=>setTimeout(()=>window.print(),200);<\/script></body></html>`);win.document.close();
}
function osRows101015(){
 const sec=osSec101015();if(!sec)return [];
 let rows=[...sec.querySelectorAll('tbody tr,.os-card,.ordem-card,.service-order-card,.ordem-servico-card,[data-os-id]')];
 if(!rows.length)rows=[...sec.querySelectorAll('.card')].filter(x=>(x.innerText||'').trim().length>30);
 return rows.filter(r=>(r.innerText||'').trim().length>10&&!r.closest('thead'));
}
function injectOSPrint101015(){
 osRows101015().forEach(row=>{
  if(row.querySelector('.os-print-actions-101015'))return;
  const box=document.createElement('div');box.className='os-print-actions-101015';box.innerHTML='<button type="button" class="secondary os-via-cliente-101015">Via cliente</button><button type="button" class="primary os-via-garantia-101015">Via com garantia</button>';
  row.appendChild(box);
 });
}
document.addEventListener('click',e=>{
 const c=e.target.closest?.('.os-via-cliente-101015');if(c){e.preventDefault();e.stopPropagation();printOS101015(c.closest('tr,.os-card,.ordem-card,.service-order-card,.ordem-servico-card,[data-os-id],.card'),false);return}
 const g=e.target.closest?.('.os-via-garantia-101015');if(g){e.preventDefault();e.stopPropagation();printOS101015(g.closest('tr,.os-card,.ordem-card,.service-order-card,.ordem-servico-card,[data-os-id],.card'),true);return}
 if(e.target.closest?.('.nav[data-s="ordens"],.nav[data-s="ordensServico"],.nav[data-s="ordens-servico"]'))setTimeout(injectOSPrint101015,80);
},true);
new MutationObserver(()=>{if(osSec101015()?.classList.contains('active'))injectOSPrint101015()}).observe(document.documentElement,{childList:true,subtree:true});
document.addEventListener('DOMContentLoaded',()=>setTimeout(injectOSPrint101015,250));setTimeout(injectOSPrint101015,900);
'''
write('public/app.js',js)
css=read('public/style.css')+r'''
/* 10.10.15 - ações de impressão nas Ordens de Serviço */
.os-print-actions-101015{display:flex;gap:6px;align-items:center;justify-content:flex-end;flex-wrap:wrap;margin-top:8px}.os-print-actions-101015 button{min-height:30px!important;padding:6px 9px!important;font-size:11px!important}.os-via-garantia-101015{white-space:nowrap}
@media(max-width:1100px){.os-print-actions-101015{justify-content:flex-start}.os-print-actions-101015 button{font-size:10px!important;padding:5px 7px!important}}
'''
write('public/style.css',css)
print('10.10.15: Ordens de Serviço ganham Via cliente e Via com garantia de 3 meses, com datas de início e vencimento impressas.')