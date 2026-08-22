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

// 10.10.47 - no APP/SISTEMA: cliente e loja usam a mesma tipografia legível da garantia.
const osViaHtmlBase101047=osViaHtml101036;
osViaHtml101036=function(o,kind){
 let out=osViaHtmlBase101047(o,kind);if(!out)return out;
 // Remove estilos tipográficos acumulados para não haver conflito entre versões.
 out=out.replace(/<style id="(?:thermal-readable-101044|receipt-readable-101045|receipt-safe-101046)">[\s\S]*?<\/style>/g,'');
 const css=`<style id="receipt-unified-101047">
 html,body{margin:0!important;padding:0!important;background:#fff!important;color:#000!important;-webkit-print-color-adjust:exact!important;print-color-adjust:exact!important}
 body,.receipt,.os-receipt,.receipt-101030{font-family:Arial,Helvetica,sans-serif!important;font-size:14px!important;font-weight:700!important;line-height:1.28!important;color:#000!important;max-width:100%!important;overflow:hidden!important}
 body *,.receipt *,.os-receipt *,.receipt-101030 *{color:#000!important;opacity:1!important;text-shadow:none!important;box-sizing:border-box!important}
 p,div,span,td{font-size:14px!important;font-weight:700!important;line-height:1.28!important}
 b,strong{font-size:15px!important;font-weight:900!important}h1{font-size:21px!important;font-weight:900!important}h2{font-size:19px!important;font-weight:900!important}h3{font-size:16px!important;font-weight:900!important}
 small{font-size:12px!important;font-weight:700!important;line-height:1.25!important}.receipt-row,.receipt-line{padding:2px 0!important}
 img{max-width:100%!important;height:auto!important}
 @media print{html,body{width:100%!important}body,.receipt,.os-receipt,.receipt-101030{font-size:14px!important;font-weight:700!important;line-height:1.28!important}}
 </style>`;
 return css+out;
};
'''
write('public/app.js',js)
print('10.10.47: vias cliente e loja igualadas a legibilidade da garantia no app.')
