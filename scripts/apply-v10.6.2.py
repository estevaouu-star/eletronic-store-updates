from pathlib import Path
import json
root=Path('app')
def read(p): return (root/p).read_text(encoding='utf-8')
def write(p,s): (root/p).write_text(s,encoding='utf-8')
pkg=json.loads(read('package.json'));pkg['version']='10.6.2';write('package.json',json.dumps(pkg,indent=2,ensure_ascii=False))
js=read('public/app.js')
js += r'''
// 10.6.2: coloca o botão NFC-e dentro do mesmo menu lateral das outras abas.
function corrigirPosicaoNavNfce(){
  const btn=document.querySelector('.nav-item[data-page="nfce"]');
  if(!btn)return;
  const outras=[...document.querySelectorAll('.nav-item[data-page]')].filter(x=>x!==btn);
  const referencia=outras.find(x=>x.dataset.page==='fiscal')||outras[outras.length-1]||null;
  const menu=referencia?.parentElement||null;
  if(!menu)return;
  if(btn.parentElement!==menu){
    if(referencia&&referencia.parentElement===menu) menu.insertBefore(btn,referencia);
    else menu.appendChild(btn);
  }
  btn.removeAttribute('style');
}
document.addEventListener('DOMContentLoaded',corrigirPosicaoNavNfce);
setTimeout(corrigirPosicaoNavNfce,0);
'''
write('public/app.js',js)
css=read('public/style.css')
css += '''\n/* 10.6.2: NFC-e usa exatamente o mesmo tamanho/fluxo das demais abas laterais */\n.nav-item[data-page="nfce"]{width:100%;max-width:none}\n'''
write('public/style.css',css)
print('Patch 10.6.2 aplicado: botão NFC-e movido para o mesmo menu lateral das outras abas.')
