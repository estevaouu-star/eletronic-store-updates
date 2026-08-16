from pathlib import Path
import json,re
root=Path('app')
def read(p): return (root/p).read_text(encoding='utf-8')
def write(p,s): (root/p).write_text(s,encoding='utf-8')

pkg=json.loads(read('package.json'));pkg['version']='10.6.4';write('package.json',json.dumps(pkg,indent=2,ensure_ascii=False))

# Corrige estruturalmente o menu: remove qualquer botão NFC-e solto e recria DENTRO do <aside> existente.
html=read('public/index.html')
html=re.sub(r'\s*<button[^>]*class="[^"]*nav-item[^"]*"[^>]*data-page="nfce"[^>]*>.*?</button>\s*','\n',html,flags=re.S|re.I)
btn='''\n      <button class="nav-item" data-page="nfce"><span class="nav-icon">▤</span><span>NFC-e</span></button>\n'''
# Insere obrigatoriamente dentro da barra lateral real, antes do fechamento do primeiro aside.
m=re.search(r'</aside\s*>',html,re.I)
if not m:
    raise RuntimeError('Não encontrei o fechamento </aside> da barra lateral.')
html=html[:m.start()]+btn+html[m.start():]
write('public/index.html',html)

js=read('public/app.js')
js += r'''
// 10.6.4: proteção final contra NFC-e fora da barra lateral.
function garantirNfceNaSidebar(){
  const aside=document.querySelector('aside');
  if(!aside)return;
  const botoes=[...document.querySelectorAll('.nav-item[data-page="nfce"]')];
  if(!botoes.length)return;
  const principal=botoes[0];
  botoes.slice(1).forEach(b=>b.remove());
  if(principal.parentElement!==aside) aside.appendChild(principal);
  principal.style.cssText='';
}
document.addEventListener('DOMContentLoaded',garantirNfceNaSidebar);
setTimeout(garantirNfceNaSidebar,0);
'''
write('public/app.js',js)

css=read('public/style.css')
css += '''\n/* 10.6.4: NFC-e é somente um item normal do menu lateral */\naside .nav-item[data-page="nfce"]{width:100%;position:static!important;float:none!important;margin-left:0!important;margin-right:0!important}\n'''
write('public/style.css',css)
print('Patch 10.6.4 aplicado: NFC-e inserida estruturalmente dentro do aside/sidebar.')
