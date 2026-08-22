from pathlib import Path
import json,re
root=Path('app')
def read(p): return (root/p).read_text(encoding='utf-8')
def write(p,s): (root/p).write_text(s,encoding='utf-8')
def replace1(s,a,b,label):
    if a not in s: raise RuntimeError(f'Trecho nao encontrado: {label}')
    return s.replace(a,b,1)
pkg=json.loads(read('package.json'));pkg['version']='10.10.46';write('package.json',json.dumps(pkg,indent=2,ensure_ascii=False))
html=read('public/index.html');html=replace1(html,'id="versionInfo" class="version-info">v10.10.45','id="versionInfo" class="version-info">v10.10.46','versao');write('public/index.html',html)
js=read('public/app.js');js=replace1(js,'const atual="10.10.45"','const atual="10.10.46"','atualizador')
js += r'''

// 10.10.46 - corrige estilos conflitantes das vias e evita corte na garantia.
const osViaHtmlBase101046=osViaHtml101036;
osViaHtml101036=function(o,kind){
 let out=osViaHtmlBase101046(o,kind);if(!out)return out;
 // remove reforços agressivos das 10.10.44/45 para não acumular CSS e cortar conteúdo
 out=out.replace(/<style id="thermal-readable-101044">[\s\S]*?<\/style>/g,'');
 out=out.replace(/<style id="receipt-readable-101045">[\s\S]*?<\/style>/g,'');
 const cfg=kind==='garantia'
   ? {base:14,bold:15,small:12,h1:20,h2:18,h3:16,line:1.22,pad:1}
   : kind==='loja'
     ? {base:16,bold:17,small:13,h1:23,h2:20,h3:18,line:1.28,pad:2}
     : {base:15,bold:16,small:13,h1:22,h2:19,h3:17,line:1.26,pad:2};
 const css=`<style id="receipt-balanced-101046">
  html,body{margin:0!important;padding:0!important;background:#fff!important;color:#000!important;-webkit-print-color-adjust:exact!important;print-color-adjust:exact!important;overflow:visible!important}
  body,.receipt,.os-receipt,.receipt-101030{font-family:Arial,Helvetica,sans-serif!important;font-size:${cfg.base}px!important;font-weight:700!important;line-height:${cfg.line}!important;color:#000!important;max-width:100%!important;width:100%!important;overflow:visible!important;word-break:normal!important;overflow-wrap:anywhere!important}
  body *,.receipt *,.os-receipt *,.receipt-101030 *{color:#000!important;opacity:1!important;text-shadow:none!important;box-sizing:border-box!important;max-width:100%!important}
  .receipt span,.receipt p,.receipt div,.os-receipt span,.os-receipt p,.os-receipt div,.receipt-101030 span,.receipt-101030 p,.receipt-101030 div{font-size:${cfg.base}px!important;font-weight:700!important;line-height:${cfg.line}!important}
  b,strong{font-size:${cfg.bold}px!important;font-weight:900!important} small{font-size:${cfg.small}px!important;font-weight:700!important;line-height:1.2!important}
  h1{font-size:${cfg.h1}px!important;font-weight:900!important;line-height:1.08!important;margin:2px 0!important} h2{font-size:${cfg.h2}px!important;font-weight:900!important;line-height:1.1!important;margin:2px 0!important} h3{font-size:${cfg.h3}px!important;font-weight:900!important;line-height:1.1!important;margin:2px 0!important}
  .receipt-row,.receipt-line{padding:${cfg.pad}px 0!important;gap:4px!important}.receipt-row>*:first-child,.receipt-line>*:first-child{min-width:0!important}.receipt-row>*:last-child,.receipt-line>*:last-child{text-align:right!important;min-width:0!important;white-space:normal!important}
  img{max-width:100%!important;height:auto!important}
  @page{margin:2mm!important}
  @media print{html,body{width:100%!important;overflow:visible!important}.receipt,.os-receipt,.receipt-101030{width:100%!important;max-width:100%!important;overflow:visible!important}}
 </style>`;
 return css+out;
};
'''
write('public/app.js',js)
print('10.10.46: via loja mais legivel e via garantia sem corte, com estilos separados.')
