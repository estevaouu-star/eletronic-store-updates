from pathlib import Path
import json
root=Path('app')
def read(p): return (root/p).read_text(encoding='utf-8')
def write(p,s): (root/p).write_text(s,encoding='utf-8')
def rep(s,a,b):
 if a not in s: raise RuntimeError(f'nao encontrado: {a}')
 return s.replace(a,b,1)
pkg=json.loads(read('package.json'));pkg['version']='10.10.51';write('package.json',json.dumps(pkg,indent=2,ensure_ascii=False))
html=read('public/index.html');html=rep(html,'id="versionInfo" class="version-info">v10.10.50','id="versionInfo" class="version-info">v10.10.51');write('public/index.html',html)
js=read('public/app.js');js=rep(js,'const atual="10.10.50"','const atual="10.10.51"')
js += r'''

// 10.10.51 - preserva o visual aprovado e elimina o corte inferior nas vias cliente/loja.
const osViaHtmlBase101051=osViaHtml101036;
osViaHtml101036=function(o,kind){
 let out=osViaHtmlBase101051(o,kind);if(!out||kind==='garantia')return out;
 const fit=`<style id="receipt-fit-bottom-101051">
 html,body{height:auto!important;min-height:0!important;overflow:visible!important}
 body{padding-bottom:0!important;margin-bottom:0!important}
 .receipt-structured-101025{height:auto!important;min-height:0!important;max-height:none!important;overflow:visible!important;padding-bottom:0!important;margin-bottom:0!important}
 .receipt-structured-101025 .receipt-note{font-size:11px!important;line-height:1.08!important;margin:4px 0 2px!important;padding:0!important;font-weight:700!important}
 .receipt-structured-101025 .receipt-signature{font-size:10px!important;line-height:1.05!important;margin:5px 0 0!important;padding:0!important;min-height:0!important}
 .receipt-structured-101025 .receipt-section{margin-top:2px!important;margin-bottom:2px!important;padding-top:2px!important;padding-bottom:2px!important}
 .receipt-structured-101025 p{margin-top:1px!important;margin-bottom:1px!important}
 @page{size:auto;margin:1.5mm 2mm 0 2mm!important}
 @media print{html,body,.receipt-structured-101025{height:auto!important;max-height:none!important;overflow:visible!important;page-break-after:auto!important}.receipt-structured-101025:last-child{margin-bottom:0!important;padding-bottom:0!important}}
 </style>`;
 return fit+out;
};
'''
write('public/app.js',js)
print('10.10.51: corte inferior corrigido sem alterar garantia nem dados principais.')
