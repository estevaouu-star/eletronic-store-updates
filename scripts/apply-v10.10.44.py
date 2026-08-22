from pathlib import Path
import json
root=Path('app')
def read(p): return (root/p).read_text(encoding='utf-8')
def write(p,s): (root/p).write_text(s,encoding='utf-8')
def replace1(s,a,b,label):
    if a not in s: raise RuntimeError(f'Trecho nao encontrado: {label}')
    return s.replace(a,b,1)
pkg=json.loads(read('package.json'));pkg['version']='10.10.44';write('package.json',json.dumps(pkg,indent=2,ensure_ascii=False))
html=read('public/index.html');html=replace1(html,'id="versionInfo" class="version-info">v10.10.43','id="versionInfo" class="version-info">v10.10.44','versao');write('public/index.html',html)
js=read('public/app.js');js=replace1(js,'const atual="10.10.43"','const atual="10.10.44"','atualizador')
# Reforça tipografia no HTML enviado à impressora térmica, não apenas no preview do sistema.
js += r'''

// 10.10.44 - impressão térmica mais legível: fonte maior, mais pesada e contraste máximo.
const osViaHtmlBase101044=osViaHtml101036;
osViaHtml101036=function(o,kind){
 let html=osViaHtmlBase101044(o,kind);if(!html)return html;
 const thermalCss=`<style id="thermal-readable-101044">
  *{color:#000!important;text-shadow:none!important;opacity:1!important;box-sizing:border-box}
  .receipt,.os-receipt,.receipt-101030{font-family:Arial,Helvetica,sans-serif!important;font-size:15px!important;font-weight:600!important;line-height:1.32!important;letter-spacing:.1px!important}
  .receipt span,.receipt p,.receipt div,.os-receipt span,.os-receipt p,.os-receipt div,.receipt-101030 span,.receipt-101030 p,.receipt-101030 div{font-size:15px!important;font-weight:600!important;line-height:1.32!important}
  .receipt b,.receipt strong,.os-receipt b,.os-receipt strong,.receipt-101030 b,.receipt-101030 strong{font-size:16px!important;font-weight:800!important}
  .receipt h1,.receipt h2,.receipt h3,.os-receipt h1,.os-receipt h2,.os-receipt h3,.receipt-101030 h1,.receipt-101030 h2,.receipt-101030 h3{font-weight:900!important;line-height:1.15!important}
  .receipt h1,.os-receipt h1,.receipt-101030 h1{font-size:22px!important}.receipt h2,.os-receipt h2,.receipt-101030 h2{font-size:20px!important}.receipt h3,.os-receipt h3,.receipt-101030 h3{font-size:17px!important}
  .receipt-row,.receipt-line{padding:2px 0!important;min-height:20px!important}
  .receipt small,.os-receipt small,.receipt-101030 small{font-size:13px!important;font-weight:600!important;line-height:1.3!important}
  @media print{body{color:#000!important}.receipt,.os-receipt,.receipt-101030{font-size:15px!important;font-weight:600!important}}
 </style>`;
 return thermalCss+html;
};
'''
write('public/app.js',js)
print('10.10.44: letras das vias aumentadas e engrossadas na impressão térmica.')
