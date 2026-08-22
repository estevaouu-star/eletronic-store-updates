from pathlib import Path
import json,re
root=Path('app')
def read(p): return (root/p).read_text(encoding='utf-8')
def write(p,s): (root/p).write_text(s,encoding='utf-8')
def rep(s,a,b):
 if a not in s: raise RuntimeError('versao anterior nao encontrada')
 return s.replace(a,b,1)
pkg=json.loads(read('package.json'));pkg['version']='10.10.48';write('package.json',json.dumps(pkg,indent=2,ensure_ascii=False))
html=read('public/index.html');html=rep(html,'id="versionInfo" class="version-info">v10.10.47','id="versionInfo" class="version-info">v10.10.48');write('public/index.html',html)
js=read('public/app.js');js=rep(js,'const atual="10.10.47"','const atual="10.10.48"')
js += r'''

// 10.10.48 - aplica estilos INLINE nos elementos reais da via cliente/loja; garantia permanece intacta.
const osViaHtmlBase101048=osViaHtml101036;
osViaHtml101036=function(o,kind){
 let out=osViaHtmlBase101048(o,kind);if(!out)return out;
 if(kind==='garantia')return out;
 // Remove reforço anterior da 10.10.47 para evitar conflito.
 out=out.replace(/<style id="receipt-client-store-like-warranty-101047">[\s\S]*?<\/style>/g,'');
 const add=(cls,style)=>{const rx=new RegExp(`<([a-zA-Z0-9]+)([^>]*class=["'][^"']*${cls}[^"']*["'][^>]*)>`,'g');out=out.replace(rx,(m,tag,attrs)=>{if(/style=["']/.test(attrs))return `<${tag}${attrs.replace(/style=["']([^"']*)["']/,`style="$1;${style}"`)}>`;return `<${tag}${attrs} style="${style}">`})};
 add('receipt-structured-101025','font-family:Arial,Helvetica,sans-serif!important;font-size:14px!important;font-weight:700!important;line-height:1.22!important;color:#000!important;width:100%!important;max-width:100%!important;overflow:visible!important;');
 add('receipt-section','font-size:14px!important;font-weight:700!important;line-height:1.22!important;margin:0!important;padding:5px 0!important;border-top:1px dashed #000!important;');
 add('receipt-section-title','font-size:15px!important;font-weight:900!important;line-height:1.15!important;letter-spacing:.5px!important;margin-bottom:2px!important;');
 add('receipt-kicker','font-size:13px!important;font-weight:900!important;line-height:1.15!important;letter-spacing:1px!important;');
 add('receipt-doc-number','font-size:20px!important;font-weight:900!important;line-height:1.08!important;margin:3px 0!important;');
 add('receipt-text','font-size:14px!important;font-weight:700!important;line-height:1.22!important;margin:2px 0!important;');
 add('receipt-note','font-size:12px!important;font-weight:700!important;line-height:1.22!important;text-align:center!important;margin:5px 0!important;');
 add('receipt-signature','font-size:12px!important;font-weight:700!important;line-height:1.2!important;margin-top:12px!important;text-align:center!important;');
 // Força também linhas geradas pelo helper linhaRecibo101025, independente do nome exato da classe.
 out=out.replace(/<(div|span)([^>]*class=["'][^"']*(?:receipt-row|receipt-line)[^"']*["'][^>]*)>/g,(m,t,a)=>`<${t}${a} style="font-size:14px!important;font-weight:700!important;line-height:1.22!important;padding:1px 0!important;color:#000!important;">`);
 out=out.replace(/<h2([^>]*)>/g,'<h2$1 style="font-size:20px!important;font-weight:900!important;line-height:1.08!important;margin:3px 0!important;color:#000!important;">');
 out=out.replace(/<p([^>]*)>/g,'<p$1 style="font-size:14px!important;font-weight:700!important;line-height:1.22!important;margin:2px 0!important;color:#000!important;">');
 return out;
};
'''
write('public/app.js',js)
print('10.10.48: estilos inline aplicados nas classes reais das vias cliente e loja; garantia preservada.')
