from pathlib import Path
import json
root=Path('app')
def read(p): return (root/p).read_text(encoding='utf-8')
def write(p,s): (root/p).write_text(s,encoding='utf-8')
pkg=json.loads(read('package.json'));pkg['version']='10.6.3';write('package.json',json.dumps(pkg,indent=2,ensure_ascii=False))

js=read('public/app.js')
js += r'''
// 10.6.3: recria o item NFC-e dentro do menu lateral correto e elimina qualquer botão solto.
function eletromixCorrigirNfceMenu(){
  const referencia=document.querySelector('.nav-item[data-page="produtos"]') || document.querySelector('.nav-item[data-page="clientes"]') || document.querySelector('.nav-item[data-page="caixa"]');
  const menu=referencia?.parentElement;
  if(!menu)return;

  document.querySelectorAll('.nav-item[data-page="nfce"]').forEach(el=>el.remove());

  const btn=document.createElement('button');
  btn.type='button';
  btn.className='nav-item';
  btn.dataset.page='nfce';
  btn.innerHTML='<span class="nav-icon">▤</span><span>NFC-e</span>';

  const config=menu.querySelector('.nav-item[data-page="configuracoes"], .nav-item[data-page="settings"]');
  if(config) menu.insertBefore(btn,config);
  else menu.appendChild(btn);

  const page=document.querySelector('#page-nfce');
  if(page && !page.classList.contains('active')){
    page.hidden=true;
    page.style.display='none';
  }
}

document.addEventListener('DOMContentLoaded',()=>setTimeout(eletromixCorrigirNfceMenu,0));
setTimeout(eletromixCorrigirNfceMenu,50);
'''
write('public/app.js',js)

css=read('public/style.css')
css += '''\n/* 10.6.3 - item NFC-e idêntico aos demais itens da navegação */\n.nav-item[data-page="nfce"]{width:auto!important;max-width:none!important;min-width:0!important;align-self:stretch!important}\n'''
write('public/style.css',css)
print('Patch 10.6.3 aplicado: NFC-e recriada dentro do menu lateral correto.')
