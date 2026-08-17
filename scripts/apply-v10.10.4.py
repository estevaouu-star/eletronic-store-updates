from pathlib import Path
import json
root=Path('app')
def read(p): return (root/p).read_text(encoding='utf-8')
def write(p,s): (root/p).write_text(s,encoding='utf-8')
pkg=json.loads(read('package.json'));pkg['version']='10.10.4';write('package.json',json.dumps(pkg,indent=2,ensure_ascii=False))
html=read('public/index.html').replace('id="versionInfo" class="version-info">v10.10.3','id="versionInfo" class="version-info">v10.10.4',1);write('public/index.html',html)
js=read('public/app.js').replace('const atual="10.10.3"','const atual="10.10.4"',1)
js += r'''
// 10.10.4 - garante que somente a section ativa apareca. Corrige Caixa ficando por cima das outras abas.
function corrigirVisibilidadeAbas10104(){
  document.querySelectorAll('.section').forEach(sec=>{
    const ativa=sec.classList.contains('active');
    sec.style.removeProperty('display');
    if(!ativa)sec.setAttribute('aria-hidden','true');else sec.removeAttribute('aria-hidden');
  });
  const caixa=document.querySelector('#caixa');
  document.body.classList.toggle('caixa-mode-10103',!!caixa?.classList.contains('active'));
}
const obs10104=new MutationObserver(corrigirVisibilidadeAbas10104);
obs10104.observe(document.documentElement,{subtree:true,attributes:true,attributeFilter:['class'],childList:true});
document.addEventListener('click',e=>{if(e.target.closest?.('.nav'))setTimeout(corrigirVisibilidadeAbas10104,0)},true);
document.addEventListener('DOMContentLoaded',corrigirVisibilidadeAbas10104);setTimeout(corrigirVisibilidadeAbas10104,300);
'''
write('public/app.js',js)
css=read('public/style.css')+r'''
/* 10.10.4 - regra final de navegacao: section inativa nunca pode ficar sobre a ativa */
.section:not(.active){display:none!important}.section.active{display:block!important}#caixa.caixa-1094.active{display:flex!important}#caixa.caixa-1094:not(.active){display:none!important}
html:has(body:not(.caixa-mode-10103)){overflow:auto!important}body:not(.caixa-mode-10103){overflow:auto!important}body:not(.caixa-mode-10103) main{overflow:visible!important}body:not(.caixa-mode-10103) .section.active{height:auto!important;min-height:0!important;overflow:visible!important}
'''
write('public/style.css',css)
print('10.10.4: Caixa nao sobrepoe mais as outras abas; somente a section ativa fica visivel.')