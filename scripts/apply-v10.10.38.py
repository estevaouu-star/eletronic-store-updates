from pathlib import Path
import json,re
root=Path('app')
def read(p): return (root/p).read_text(encoding='utf-8')
def write(p,s): (root/p).write_text(s,encoding='utf-8')
def replace1(s,a,b,label):
    if a not in s: raise RuntimeError(f'Trecho nao encontrado: {label}')
    return s.replace(a,b,1)

pkg=json.loads(read('package.json'));pkg['version']='10.10.38';write('package.json',json.dumps(pkg,indent=2,ensure_ascii=False))
html=read('public/index.html');html=replace1(html,'id="versionInfo" class="version-info">v10.10.37','id="versionInfo" class="version-info">v10.10.38','versao');write('public/index.html',html)
js=read('public/app.js');js=replace1(js,'const atual="10.10.37"','const atual="10.10.38"','atualizador')
server=read('src/server.ts')

# Status mais formal
server=server.replace('"Acabou de chegar"','"Recebido na loja"')
js=js.replace("'Acabou de chegar'","'Recebido na loja'").replace('Acabou de chegar','Recebido na loja')

# Reforço visual e impressão das vias sem depender de impressão automática antiga.
js += r'''

// 10.10.38 - vias mais legíveis e impressão de garantia restaurada.
function reforcarViaLoja101038(html,o){
  if(!html)return html;
  const marca=[o?.marca,o?.modelo].filter(Boolean).join(' / ')||'Não informado';
  const servico=o?.servicoId?(o?.servicoNome||'Serviço definido'):'EM DIAGNÓSTICO / SERVIÇO A DEFINIR';
  const bloco=`<div class="os-store-highlight-101038"><div><span>MARCA / MODELO</span><strong>${esc(marca)}</strong></div><div><span>TIPO DE SERVIÇO</span><strong>${esc(servico)}</strong></div></div>`;
  if(/<div class="receipt-body[^>]*>/.test(html)) return html.replace(/(<div class="receipt-body[^>]*>)/,'$1'+bloco);
  return bloco+html;
}
const osViaHtmlBase101038=typeof osViaHtml101036==='function'?osViaHtml101036:null;
if(osViaHtmlBase101038){
 osViaHtml101036=function(o,kind){let html=osViaHtmlBase101038(o,kind);if(kind==='loja')html=reforcarViaLoja101038(html,o);return html};
}
function imprimirHtmlOS101038(titulo,html){
 const w=window.open('','_blank','width=860,height=900');if(!w)return toast('Permita pop-ups para imprimir a via.');
 w.document.open();w.document.write(`<!doctype html><html><head><meta charset="utf-8"><title>${esc(titulo)}</title><style>
 body{font-family:Arial,Helvetica,sans-serif;color:#000;background:#fff;margin:0;padding:18px;font-size:15px;line-height:1.42}*{box-sizing:border-box}.receipt,.os-receipt{max-width:760px;margin:0 auto;color:#000!important;background:#fff!important}.receipt *,.os-receipt *{color:#000!important;opacity:1!important}.receipt small,.receipt p,.receipt span,.receipt div,.os-receipt small,.os-receipt p,.os-receipt span,.os-receipt div{font-size:14px!important}.receipt b,.receipt strong,.os-receipt b,.os-receipt strong{font-size:15px!important}.receipt h1,.receipt h2,.receipt h3,.os-receipt h1,.os-receipt h2,.os-receipt h3{color:#000!important}.receipt-row,.receipt-line{border-bottom:1px solid #777!important;padding:7px 0!important}.os-store-highlight-101038{border:3px solid #000;padding:12px;margin:12px 0;display:grid;grid-template-columns:1fr 1fr;gap:12px}.os-store-highlight-101038 span{display:block;font-size:12px!important;font-weight:800;letter-spacing:.4px}.os-store-highlight-101038 strong{display:block;font-size:20px!important;line-height:1.2;margin-top:3px}.receipt-note,.note,.observacao,.receipt-observation{font-size:14px!important;font-weight:600!important;color:#000!important;opacity:1!important}.receipt-note *,.note *,.observacao *,.receipt-observation *{color:#000!important;opacity:1!important}@media print{body{padding:0}.os-store-highlight-101038{break-inside:avoid}}
 </style></head><body>${html}<script>window.onload=()=>setTimeout(()=>window.print(),180)<\/script></body></html>`);w.document.close();
}
function instalarImpressaoGarantia101038(){
 document.addEventListener('click',e=>{
   const b=e.target?.closest?.('[data-print-warranty-101038]');if(!b)return;
   const id=Number(b.dataset.printWarranty101038);const o=(ordensServico||[]).find(x=>x.id===id);if(!o)return toast('Ordem não encontrada.');if(!osGarantiaAtiva101036(o))return toast('A garantia ainda não foi iniciada.');
   const html=osViaHtml101036(o,'garantia');if(!html)return toast('Não foi possível montar a via de garantia.');imprimirHtmlOS101038(`Garantia OS #${o.id}`,html);
 });
}
if(typeof visualizarVia101036==='function'){
 const visualizarViaBase101038=visualizarVia101036;
 visualizarVia101036=function(o,kind){
   if(kind!=='garantia')return visualizarViaBase101038(o,kind);
   if(!osGarantiaAtiva101036(o))return toast('A garantia ainda não foi iniciada pelo técnico.');
   const html=osViaHtml101036(o,'garantia');if(!html)return toast('Não foi possível montar esta via.');
   openModal('Via de garantia',`<div class="os-preview-101036">${html}</div><div class="modal-actions"><button class="primary" type="button" data-print-warranty-101038="${o.id}">Imprimir via de garantia</button><button class="secondary" type="button" onclick="closeModal()">Fechar</button></div>`);
 };
}
instalarImpressaoGarantia101038();
'''

css=read('public/style.css')
css += r'''
/* 10.10.38 - melhor leitura das vias na tela */
.os-preview-101036{background:#fff!important;color:#000!important;padding:18px!important}.os-preview-101036 *{color:#000!important;opacity:1!important}.os-preview-101036 .receipt,.os-preview-101036 .os-receipt{font-size:15px!important;line-height:1.42!important}.os-preview-101036 small,.os-preview-101036 p,.os-preview-101036 span{font-size:14px!important}.os-preview-101036 b,.os-preview-101036 strong{font-size:15px!important}.os-store-highlight-101038{border:3px solid #111;padding:12px;margin:12px 0;display:grid;grid-template-columns:1fr 1fr;gap:12px;background:#fff}.os-store-highlight-101038 span{display:block;font-size:11px!important;font-weight:800!important;letter-spacing:.4px}.os-store-highlight-101038 strong{display:block;font-size:20px!important;line-height:1.2;margin-top:3px;color:#000!important}.receipt-note,.note,.observacao,.receipt-observation{color:#000!important;opacity:1!important;font-weight:600!important}
@media(max-width:600px){.os-store-highlight-101038{grid-template-columns:1fr}.os-store-highlight-101038 strong{font-size:18px!important}}
'''
write('public/app.js',js);write('src/server.ts',server);write('public/style.css',css)
print('10.10.38: status Recebido na loja, vias mais legiveis, garantia imprimivel e destaque de marca/modelo/servico na via da loja.')
