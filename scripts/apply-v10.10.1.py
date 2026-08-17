from pathlib import Path
import json
root=Path('app')
def read(p): return (root/p).read_text(encoding='utf-8')
def write(p,s): (root/p).write_text(s,encoding='utf-8')

pkg=json.loads(read('package.json'));pkg['version']='10.10.1';write('package.json',json.dumps(pkg,indent=2,ensure_ascii=False))
html=read('public/index.html').replace('id="versionInfo" class="version-info">v10.10.0','id="versionInfo" class="version-info">v10.10.1',1);write('public/index.html',html)

js=read('public/app.js').replace('const atual="10.10.0"','const atual="10.10.1"',1)
js += r'''
// 10.10.1 - remove definitivamente a barra antiga "Venda rápida" da 10.9.0.
function removerSmartPdvAntigo10101(){
  document.querySelectorAll('.smart-pdv-commandbar').forEach(n=>n.remove());
  document.querySelector('#caixa')?.classList.remove('smart-pdv');
}
// setupSmartPdv antigo era quem recriava a barra. Neutraliza a função após carregar todos os patches.
try{setupSmartPdv=removerSmartPdvAntigo10101}catch{}
const obs10101=new MutationObserver(removerSmartPdvAntigo10101);
document.addEventListener('DOMContentLoaded',()=>{removerSmartPdvAntigo10101();setTimeout(removerSmartPdvAntigo10101,100);setTimeout(removerSmartPdvAntigo10101,500)});
setTimeout(removerSmartPdvAntigo10101,900);
obs10101.observe(document.documentElement,{childList:true,subtree:true});
'''
write('public/app.js',js)

css=read('public/style.css')+r'''
/* 10.10.1 - nenhuma barra Venda Rápida no Caixa */
.smart-pdv-commandbar{display:none!important}.smart-pdv-brand,.smart-pdv-shortcuts{display:none!important}#caixa.smart-pdv{max-width:none!important}
'''
write('public/style.css',css)
print('10.10.1: barra Venda Rapida antiga removida definitivamente; permanecem apenas F1 vendedor, F2 cliente e F10 cobrar.')