from pathlib import Path
import json,re
root=Path('app')
def read(p): return (root/p).read_text(encoding='utf-8')
def write(p,s): (root/p).write_text(s,encoding='utf-8')

pkg=json.loads(read('package.json'));pkg['version']='10.11.4';write('package.json',json.dumps(pkg,indent=2,ensure_ascii=False))
html=read('public/index.html')
html,n=re.subn(r'(id="versionInfo" class="version-info">v)[0-9.]+',r'\g<1>10.11.04',html,count=1)
if n!=1: raise SystemExit('Versão do cabeçalho não encontrada')
write('public/index.html',html)

js=read('public/app.js')
js,n=re.subn(r'const atual="[0-9.]+"(?=,status=)', 'const atual="10.11.4"', js, count=1)
if n!=1: raise SystemExit('Versão do atualizador não encontrada')

js += r'''
/* 10.11.04 - atualização acessível antes do login */
function instalarAtualizacaoLogin101104(){
  const tela=document.querySelector('#loginScreen');
  if(!tela||document.querySelector('#loginUpdateBtn101104'))return;
  const form=document.querySelector('#loginForm');
  if(!form)return;
  const wrap=document.createElement('div');
  wrap.className='login-update-101104';
  wrap.innerHTML='<button id="loginUpdateBtn101104" type="button" class="secondary">Verificar atualização</button><div id="loginUpdateStatus101104">Use este botão se não conseguir entrar neste computador.</div>';
  form.appendChild(wrap);
  document.querySelector('#loginUpdateBtn101104')?.addEventListener('click',()=>{
    const status=document.querySelector('#loginUpdateStatus101104');
    const candidatos=[...document.querySelectorAll('button')].filter(b=>b.id!=='loginUpdateBtn101104'&&!b.closest('#loginScreen'));
    const original=candidatos.find(b=>/atualiz|update/i.test(String(b.textContent||'')+' '+String(b.id||'')+' '+String(b.className||'')));
    if(original){
      if(status)status.textContent='Verificando atualização...';
      original.click();
      return;
    }
    if(status)status.textContent='Não encontrei o atualizador nesta instalação. Baixe a versão mais recente pelo instalador.';
  });
}
document.addEventListener('DOMContentLoaded',instalarAtualizacaoLogin101104);
setTimeout(instalarAtualizacaoLogin101104,500);
'''
write('public/app.js',js)

css=read('public/style.css')
css += r'''
.login-update-101104{margin-top:14px;padding-top:12px;border-top:1px solid rgba(255,255,255,.1);display:grid;gap:7px}.login-update-101104 button{width:100%;height:42px}.login-update-101104 div{font-size:11px;line-height:1.35;opacity:.72;text-align:center}
'''
write('public/style.css',css)
print('10.11.04: botão de atualização disponível diretamente na tela de login.')
