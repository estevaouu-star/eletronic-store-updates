from pathlib import Path
import json
root=Path('app')
def read(p): return (root/p).read_text(encoding='utf-8')
def write(p,s): (root/p).write_text(s,encoding='utf-8')
def rep(s,a,b):
 if a not in s: raise RuntimeError('versao anterior nao encontrada')
 return s.replace(a,b,1)
pkg=json.loads(read('package.json'));pkg['version']='10.10.47';write('package.json',json.dumps(pkg,indent=2,ensure_ascii=False))
html=read('public/index.html');html=rep(html,'id="versionInfo" class="version-info">v10.10.46','id="versionInfo" class="version-info">v10.10.47');write('public/index.html',html)
js=read('public/app.js');js=rep(js,'const atual="10.10.46"','const atual="10.10.47"')
js += r'''

// 10.10.47 - GARANTIA APROVADA INTACTA; cliente e loja recebem o mesmo padrão tipográfico dela.
const osViaHtmlBase101047=osViaHtml101036;
osViaHtml101036=function(o,kind){
 let out=osViaHtmlBase101047(o,kind);if(!out)return out;
 if(kind==='garantia') return out;
 out=out.replace(/<style id="receipt-balanced-101046">[\s\S]*?<\/style>/g,'');
 const css=`<style id="receipt-client-store-like-warranty-101047">
 html,body{margin:0!important;padding:0!important;background:#fff!important;color:#000!important;-webkit-print-color-adjust:exact!important;print-color-adjust:exact!important;overflow:visible!important}
 body,.receipt,.os-receipt,.receipt-101030{font-family:Arial,Helvetica,sans-serif!important;font-size:14px!important;font-weight:700!important;line-height:1.22!important;color:#000!important;width:100%!important;max-width:100%!important;overflow:visible!important;overflow-wrap:anywhere!important}
 body *,.receipt *,.os-receipt *,.receipt-101030 *{color:#000!important;opacity:1!important;text-shadow:none!important;box-sizing:border-box!important;max-width:100%!important}
 .receipt span,.receipt p,.receipt div,.os-receipt span,.os-receipt p,.os-receipt div,.receipt-101030 span,.receipt-101030 p,.receipt-101030 div{font-size:14px!important;font-weight:700!important;line-height:1.22!important}
 b,strong{font-size:15px!important;font-weight:900!important}small{font-size:12px!important;font-weight:700!important;line-height:1.2!important}
 h1{font-size:20px!important;font-weight:900!important;line-height:1.08!important;margin:2px 0!important}h2{font-size:18px!important;font-weight:900!important;line-height:1.1!important;margin:2px 0!important}h3{font-size:16px!important;font-weight:900!important;line-height:1.1!important;margin:2px 0!important}
 .receipt-row,.receipt-line{padding:1px 0!important;gap:4px!important}.receipt-row>*:last-child,.receipt-line>*:last-child{text-align:right!important;min-width:0!important;white-space:normal!important}
 img{max-width:100%!important;height:auto!important}@page{margin:2mm!important}
 @media print{html,body,.receipt,.os-receipt,.receipt-101030{font-size:14px!important;font-weight:700!important;width:100%!important;max-width:100%!important;overflow:visible!important}}
 </style>`;
 return css+out;
};
'''
write('public/app.js',js)
print('10.10.47: garantia preservada; cliente e loja no mesmo padrão legível.')
