from pathlib import Path
import json
root=Path('app')
def read(p): return (root/p).read_text(encoding='utf-8')
def write(p,s): (root/p).write_text(s,encoding='utf-8')
pkg=json.loads(read('package.json'));pkg['version']='10.6.1';write('package.json',json.dumps(pkg,indent=2,ensure_ascii=False))
js=read('public/app.js')
js += r'''
// 10.6.1: garante que a NFC-e seja uma página isolada, como as demais abas.
function eletromixMostrarPaginaExclusiva(nome){
  document.querySelectorAll('.page').forEach(p=>{
    const alvo=p.id===`page-${nome}`;
    p.classList.toggle('active',alvo);
    p.hidden=!alvo;
    p.style.display=alvo?'':'none';
  });
  document.querySelectorAll('.nav-item[data-page]').forEach(b=>b.classList.toggle('active',b.dataset.page===nome));
  if(nome==='nfce') setTimeout(renderNfce,0);
}
document.addEventListener('click',e=>{
  const btn=e.target?.closest?.('.nav-item[data-page]');
  if(!btn)return;
  const nome=btn.dataset.page;
  setTimeout(()=>{
    document.querySelectorAll('.page').forEach(p=>{
      if(p.id==='page-nfce'){
        const on=nome==='nfce';
        p.hidden=!on;
        p.style.display=on?'':'none';
        p.classList.toggle('active',on);
      }
    });
  },0);
});
document.addEventListener('DOMContentLoaded',()=>{
  const p=document.querySelector('#page-nfce');
  if(p){p.hidden=true;p.style.display='none';p.classList.remove('active')}
});
'''
write('public/app.js',js)
css=read('public/style.css')
css += '''\n/* 10.6.1 - NFC-e só aparece quando a aba NFC-e estiver ativa */\n#page-nfce{display:none!important}\n#page-nfce.active:not([hidden]){display:block!important}\n'''
write('public/style.css',css)
print('Patch 10.6.1 aplicado: NFC-e isolada na própria aba.')