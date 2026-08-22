from pathlib import Path
import json
root=Path('app')
def read(p): return (root/p).read_text(encoding='utf-8')
def write(p,s): (root/p).write_text(s,encoding='utf-8')
def replace1(s,a,b,label):
    if a not in s: raise RuntimeError(f'Trecho nao encontrado: {label}')
    return s.replace(a,b,1)

pkg=json.loads(read('package.json'));pkg['version']='10.10.45';write('package.json',json.dumps(pkg,indent=2,ensure_ascii=False))
html=read('public/index.html');html=replace1(html,'id="versionInfo" class="version-info">v10.10.44','id="versionInfo" class="version-info">v10.10.45','versao');write('public/index.html',html)
js=read('public/app.js');js=replace1(js,'const atual="10.10.44"','const atual="10.10.45"','atualizador')

js += r'''

// 10.10.45 - deixa apenas um Excluir OS e um Imprimir garantia por cartão.
function normalizarAcoesOS101045(){
 document.querySelectorAll('.os-card-101023[data-os-id]').forEach(card=>{
  const id=Number(card.dataset.osId);const o=(ordensServico||[]).find(x=>Number(x.id)===id);if(!o)return;
  const footer=card.querySelector('footer');if(!footer)return;
  [...card.querySelectorAll('button')].forEach(b=>{
    const t=(b.textContent||'').trim().toLowerCase();
    if(t==='excluir os'||t==='excluir definitivamente'||t==='imprimir garantia')b.remove();
  });
  const printBox=card.querySelector('.os-print-actions-101020')||footer;
  if(o.prontoEm&&o.garantiaAte){
    const warranty=document.createElement('button');warranty.type='button';warranty.className='primary';warranty.textContent='Imprimir garantia';warranty.onclick=e=>{e.preventDefault();e.stopPropagation();imprimirGarantia101043(id,warranty)};printBox.appendChild(warranty);
  }
  const del=document.createElement('button');del.type='button';del.className='danger';del.textContent='Excluir OS';del.onclick=e=>{e.preventDefault();e.stopPropagation();excluirOS101043(id)};footer.appendChild(del);
 });
}
const renderOSBase101045=renderOS;
renderOS=function(){renderOSBase101045();setTimeout(normalizarAcoesOS101045,0)};
setTimeout(normalizarAcoesOS101045,0);

// Aumenta e engrossa a tipografia real de TODAS as vias impressas.
const osViaHtmlBase101045=osViaHtml101036;
osViaHtml101036=function(o,kind){
 let out=osViaHtmlBase101045(o,kind);if(!out)return out;
 const css=`<style id="receipt-readable-101045">
 html,body{background:#fff!important;color:#000!important}
 body,.receipt,.os-receipt,.receipt-101030{font-family:Arial,Helvetica,sans-serif!important;font-size:18px!important;font-weight:700!important;line-height:1.4!important;color:#000!important}
 body *,.receipt *,.os-receipt *,.receipt-101030 *{color:#000!important;opacity:1!important;text-shadow:none!important;font-weight:700!important}
 b,strong{font-size:19px!important;font-weight:900!important}
 h1{font-size:26px!important;font-weight:900!important} h2{font-size:23px!important;font-weight:900!important} h3{font-size:20px!important;font-weight:900!important}
 small{font-size:16px!important;font-weight:700!important}.receipt-row,.receipt-line{padding:3px 0!important}
 @media print{html,body,.receipt,.os-receipt,.receipt-101030{font-size:18px!important;font-weight:700!important;color:#000!important}}
 </style>`;
 return css+out;
};
'''
write('public/app.js',js)
print('10.10.45: duplicatas removidas e letras das vias maiores e mais grossas.')
