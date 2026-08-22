from pathlib import Path
import json
root=Path('app')
def read(p): return (root/p).read_text(encoding='utf-8')
def write(p,s): (root/p).write_text(s,encoding='utf-8')
def rep(s,a,b):
 if a not in s: raise RuntimeError('versao anterior nao encontrada')
 return s.replace(a,b,1)
pkg=json.loads(read('package.json'));pkg['version']='10.10.50';write('package.json',json.dumps(pkg,indent=2,ensure_ascii=False))
html=read('public/index.html');html=rep(html,'id="versionInfo" class="version-info">v10.10.49','id="versionInfo" class="version-info">v10.10.50');write('public/index.html',html)
js=read('public/app.js');js=rep(js,'const atual="10.10.49"','const atual="10.10.50"')
js += r'''

// 10.10.50 - mantém os dados grandes/fortes e compacta somente a parte inferior para não cortar.
const osViaHtmlBase101050=osViaHtml101036;
osViaHtml101036=function(o,kind){
 let out=osViaHtmlBase101050(o,kind);if(!out||kind==='garantia')return out;
 const css=`<style id="receipt-no-cut-101050">
  .receipt-structured-101025{padding-bottom:0!important;margin-bottom:0!important;page-break-inside:avoid!important;break-inside:avoid!important}
  .receipt-section{padding-top:2px!important;padding-bottom:2px!important;margin-top:0!important;margin-bottom:0!important}
  .receipt-section-title{margin-top:0!important;margin-bottom:1px!important}
  .receipt-text{margin-top:1px!important;margin-bottom:1px!important}
  .receipt-note{font-size:10.5px!important;font-weight:700!important;line-height:1.08!important;margin:3px 0 2px!important;padding:0!important;text-align:center!important}
  .receipt-signature{font-size:11px!important;font-weight:700!important;line-height:1.05!important;margin-top:7px!important;margin-bottom:0!important;padding-top:5px!important;padding-bottom:0!important}
  .receipt-row,.receipt-line{padding-top:0!important;padding-bottom:0!important;line-height:1.15!important}
  @page{margin:1mm 2mm 0 2mm!important}
 </style>`;
 return css+out;
};
'''
write('public/app.js',js)
print('10.10.50: evita corte inferior sem reduzir os dados principais das vias cliente/loja.')
