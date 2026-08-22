from pathlib import Path
import json
root=Path('app')
def read(p): return (root/p).read_text(encoding='utf-8')
def write(p,s): (root/p).write_text(s,encoding='utf-8')
def rep(s,a,b):
 if a not in s: raise RuntimeError(f'nao encontrado: {a}')
 return s.replace(a,b,1)
pkg=json.loads(read('package.json'));pkg['version']='10.10.52';write('package.json',json.dumps(pkg,indent=2,ensure_ascii=False))
html=read('public/index.html');html=rep(html,'id="versionInfo" class="version-info">v10.10.51','id="versionInfo" class="version-info">v10.10.52');write('public/index.html',html)
js=read('public/app.js');js=rep(js,'const atual="10.10.51"','const atual="10.10.52"')
js += r'''

// 10.10.52 - prioridade visual: MODELO, SERVIÇO, CIÊNCIA/AUTORIZAÇÃO e ASSINATURA.
// Cliente/loja ficam compactas; garantia permanece exatamente como estava aprovada.
const osViaHtmlBase101052=osViaHtml101036;
osViaHtml101036=function(o,kind){
 let out=osViaHtmlBase101052(o,kind);if(!out||kind==='garantia')return out;
 const css=`<style id="receipt-priority-101052">
 html,body{margin:0!important;padding:0!important;height:auto!important;min-height:0!important;overflow:visible!important;color:#000!important;background:#fff!important}
 .receipt-structured-101025{margin:0!important;padding:0!important;height:auto!important;min-height:0!important;max-height:none!important;overflow:visible!important;font-family:Arial,Helvetica,sans-serif!important;color:#000!important}
 /* compacta topo e informações secundárias */
 .receipt-structured-101025 img{max-height:70px!important;width:auto!important;margin:0 auto 2px!important}
 .receipt-structured-101025 h2{font-size:16px!important;line-height:1.02!important;margin:1px 0!important;font-weight:900!important}
 .receipt-structured-101025 .receipt-kicker{font-size:10px!important;line-height:1!important;letter-spacing:.7px!important;margin:0!important;font-weight:800!important}
 .receipt-structured-101025 .receipt-doc-number{font-size:17px!important;line-height:1!important;margin:2px 0!important;font-weight:900!important}
 .receipt-structured-101025>p{font-size:10.5px!important;line-height:1.05!important;margin:1px 0!important;font-weight:600!important}
 .receipt-structured-101025 .receipt-section{margin:0!important;padding:2px 0!important}
 .receipt-structured-101025 .receipt-section-title{font-size:12px!important;line-height:1.05!important;margin:0 0 1px!important;font-weight:900!important}
 .receipt-structured-101025 .receipt-row,.receipt-structured-101025 .receipt-line{font-size:11px!important;line-height:1.08!important;padding:0!important;margin:0!important;min-height:0!important}
 .receipt-structured-101025 .receipt-row span,.receipt-structured-101025 .receipt-line span{font-size:10.5px!important;font-weight:600!important}
 .receipt-structured-101025 .receipt-row b,.receipt-structured-101025 .receipt-line b{font-size:11.5px!important;font-weight:800!important}
 .receipt-structured-101025 .receipt-text{font-size:11px!important;line-height:1.08!important;margin:1px 0!important;font-weight:700!important}
 /* PRIORIDADES: modelo e serviço ficam maiores */
 .receipt-structured-101025 [data-receipt-field="modelo"],
 .receipt-structured-101025 [data-receipt-field="servico"],
 .receipt-structured-101025 .priority-model-101052,
 .receipt-structured-101025 .priority-service-101052{font-size:15px!important;line-height:1.08!important;font-weight:900!important}
 /* texto de ciência/autorização permanece legível e inteiro */
 .receipt-structured-101025 .receipt-note{font-size:11.5px!important;line-height:1.1!important;margin:3px 0 2px!important;padding:0!important;font-weight:700!important;text-align:left!important}
 .receipt-structured-101025 .receipt-signature{font-size:11.5px!important;line-height:1.05!important;margin:7px 0 0!important;padding:0!important;font-weight:800!important;min-height:0!important}
 @page{size:auto;margin:1mm 2mm 0 2mm!important}
 @media print{html,body,.receipt-structured-101025{height:auto!important;max-height:none!important;overflow:visible!important;page-break-after:auto!important}}
 </style>`;
 // Marca explicitamente Modelo e Serviço na estrutura atual, sem mudar conteúdo.
 out=out.replace(/(<span>Modelo<\/span><b)([^>]*>)/i,'$1 class="priority-model-101052"$2');
 out=out.replace(/(<span>Serviço<\/span><b)([^>]*>)/i,'$1 class="priority-service-101052"$2');
 return css+out;
};
'''
write('public/app.js',js)
print('10.10.52 preparada: modelo/servico/ciencia/assinatura priorizados; garantia intacta; sem release automatico.')
