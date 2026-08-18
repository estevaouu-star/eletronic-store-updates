from pathlib import Path
import json
root=Path('app')
def read(p): return (root/p).read_text(encoding='utf-8')
def write(p,s): (root/p).write_text(s,encoding='utf-8')

pkg=json.loads(read('package.json'));pkg['version']='10.10.14';write('package.json',json.dumps(pkg,indent=2,ensure_ascii=False))
html=read('public/index.html').replace('id="versionInfo" class="version-info">v10.10.13','id="versionInfo" class="version-info">v10.10.14',1);write('public/index.html',html)
js=read('public/app.js').replace('const atual="10.10.13"','const atual="10.10.14"',1)
js += r'''
// 10.10.14 - o perfil 1024x768 não pode bloquear o scroll das outras abas.
function syncSectionScroll101014(){
 const caixaAtivo=!!document.querySelector('#caixa.section.active');
 document.body.classList.toggle('caixa-ativo-101014',caixaAtivo);
}
document.addEventListener('DOMContentLoaded',syncSectionScroll101014);
document.addEventListener('click',e=>{if(e.target.closest?.('.nav'))setTimeout(syncSectionScroll101014,20)},true);
new MutationObserver(syncSectionScroll101014).observe(document.documentElement,{subtree:true,attributes:true,attributeFilter:['class']});
setTimeout(syncSectionScroll101014,120);setTimeout(syncSectionScroll101014,600);
'''
write('public/app.js',js)
css=read('public/style.css')+r'''
/* 10.10.14 - no 1024x768, trava a tela SOMENTE no Caixa. Produtos e demais abas voltam a rolar normalmente. */
body[data-monitor-profile="1024x768"]:not(.caixa-ativo-101014){overflow:auto!important}
body[data-monitor-profile="1024x768"]:not(.caixa-ativo-101014) .layout{height:auto!important;min-height:calc(100vh - 50px)!important;overflow:visible!important}
body[data-monitor-profile="1024x768"]:not(.caixa-ativo-101014) main{height:auto!important;min-height:calc(100vh - 50px)!important;overflow:visible!important}
body[data-monitor-profile="1024x768"]:not(.caixa-ativo-101014) .section.active{height:auto!important;min-height:0!important;overflow:visible!important}
body[data-monitor-profile="1024x768"] #produtos.section.active{height:calc(100vh - 66px)!important;min-height:0!important;overflow-y:auto!important;overflow-x:hidden!important;overscroll-behavior:contain!important;padding-bottom:28px!important}
body[data-monitor-profile="1024x768"] #produtos.section.active .card{overflow:visible!important}
'''
write('public/style.css',css)
print('10.10.14: scroll da aba Produtos restaurado no perfil 1024x768 sem alterar o scroll interno do Caixa.')