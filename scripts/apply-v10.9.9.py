from pathlib import Path
import json,re
root=Path('app')
def read(p): return (root/p).read_text(encoding='utf-8')
def write(p,s): (root/p).write_text(s,encoding='utf-8')

pkg=json.loads(read('package.json'));pkg['version']='10.9.9';write('package.json',json.dumps(pkg,indent=2,ensure_ascii=False))
html=read('public/index.html').replace('id="versionInfo" class="version-info">v10.9.8','id="versionInfo" class="version-info">v10.9.9',1)
# Botão de atualização disponível ANTES do login, reutilizando exatamente o atualizador da tela principal.
if 'id="loginUpdateButton"' not in html:
    pat=r'(<button[^>]+type="submit"[^>]*>\s*Entrar\s*</button>)'
    repl=r'''\1
      <button id="loginUpdateButton" class="login-update-button" type="button"><span class="update-dot"></span><span id="loginUpdateText">Verificar atualização</span></button>'''
    html,n=re.subn(pat,repl,html,count=1,flags=re.I)
    if n!=1: raise RuntimeError('Botao Entrar do login nao encontrado')
write('public/index.html',html)

js=read('public/app.js').replace('const atual="10.9.8"','const atual="10.9.9"',1)
# Correção definitiva do crash: a Venda Rápida NUNCA pode tratar #caixa ou containers estruturais como seu painel.
old="function vr1097FindPanel(){const nodes=[...document.querySelectorAll('dialog,.modal,[role=\"dialog\"],section,.panel,.card')];const matches=nodes.filter(n=>/venda r[aá]pida/i.test(n.textContent||'')&&!n.matches('#app,#loginScreen,body,html')&&!n.querySelector('#loginForm'));if(!matches.length)return null;return matches.sort((a,b)=>(a.textContent||'').length-(b.textContent||'').length)[0]}"
new="function vr1097FindPanel(){const nodes=[...document.querySelectorAll('dialog,.modal,[role=\"dialog\"],.panel,.card')];const matches=nodes.filter(n=>/venda r[aá]pida/i.test(n.textContent||'')&&!n.closest('#loginScreen')&&!n.matches('#app,#caixa,.smart-pdv,body,html')&&!n.closest('#caixa')&&!n.querySelector('#loginForm'));if(!matches.length)return null;return matches.sort((a,b)=>(a.textContent||'').length-(b.textContent||'').length)[0]}"
if old not in js: raise RuntimeError('vr1097FindPanel 10.9.8 nao encontrado')
js=js.replace(old,new,1)
# espelha o estado do atualizador no botão da tela de login
js += r'''
// 10.9.9 - atualizador acessível sem autenticação
const renderUpdateState1099=renderUpdateState;
renderUpdateState=function(s){
  renderUpdateState1099(s);
  const b=document.querySelector('#loginUpdateButton'),t=document.querySelector('#loginUpdateText');if(!b||!t)return;
  const status=s?.status||'idle';b.dataset.state=status;
  t.textContent=status==='available'?'Atualizar agora':status==='downloading'?`Baixando ${s.percent||0}%`:status==='downloaded'?'Instalar atualização':status==='checking'?'Verificando...':status==='error'?'Tentar novamente':'Verificar atualização';
};
document.addEventListener('click',e=>{if(e.target?.closest?.('#loginUpdateButton')){e.preventDefault();const main=document.querySelector('#updateButton');if(main)main.click();else if(window.electronAPI?.checkForUpdates)window.electronAPI.checkForUpdates();}});
'''
write('public/app.js',js)
css=read('public/style.css')
css += r'''
/* 10.9.9 - atualização antes do login */
.login-update-button{width:100%;min-height:42px;margin-top:9px;border:1px solid #ffffff20;border-radius:10px;background:#ffffff0b;color:inherit;font-weight:800;display:flex;align-items:center;justify-content:center;gap:8px;cursor:pointer}.login-update-button:hover{background:#ffffff14}.login-update-button[data-state="available"],.login-update-button[data-state="downloaded"]{border-color:var(--accent);background:color-mix(in srgb,var(--accent) 14%,transparent)}.login-update-button .update-dot{width:7px;height:7px;border-radius:50%;background:#52c878}
'''
write('public/style.css',css)
print('10.9.9: crash do login corrigido e botão Atualizar disponível na tela de login.')