from pathlib import Path
import json,re
root=Path('app')
def read(p): return (root/p).read_text(encoding='utf-8')
def write(p,s): (root/p).write_text(s,encoding='utf-8')

pkg=json.loads(read('package.json'));pkg['version']='10.11.10';write('package.json',json.dumps(pkg,indent=2,ensure_ascii=False))
html=read('public/index.html');html,n=re.subn(r'(id="versionInfo" class="version-info">v)[0-9.]+',r'\g<1>10.11.10',html,count=1)
if n!=1: raise SystemExit('versao html nao encontrada')
write('public/index.html',html)

js=read('public/app.js');js,n=re.subn(r'const atual="[0-9.]+"(?=,status=)','const atual="10.11.10"',js,count=1)
if n!=1: raise SystemExit('versao atualizador nao encontrada')
js += r'''

// 10.11.10 - bloqueio persistente contra relogin automático após Sair.
(function(){
  const LOGOUT_FLAG='eletromix_manual_logout_101110';

  function logoutBloqueado101110(){
    try{return localStorage.getItem(LOGOUT_FLAG)==='1'}catch{return false}
  }
  function marcarLogout101110(){try{localStorage.setItem(LOGOUT_FLAG,'1')}catch{}}
  function liberarLogout101110(){try{localStorage.removeItem(LOGOUT_FLAG)}catch{}}

  // Neutraliza TODAS as tentativas antigas de auto-login enquanto o logout manual estiver marcado.
  try{
    const autoBase=autoLogin101011;
    autoLogin101011=async function(){if(logoutBloqueado101110())return false;return await autoBase()};
  }catch{}
  try{
    const restoreBase=restoreEletromixSession;
    restoreEletromixSession=async function(){if(logoutBloqueado101110())return false;return await restoreBase()};
  }catch{}
  try{
    const restoreAuthBase=restoreAuth101010;
    restoreAuth101010=async function(){if(logoutBloqueado101110())return false;return await restoreAuthBase()};
  }catch{}

  // Login digitado pelo usuário libera novamente a persistência normal.
  document.addEventListener('submit',e=>{
    if(e.target?.matches?.('#loginForm'))liberarLogout101110();
  },true);

  let busy=false;
  async function sairSemRelogar101110(){
    if(busy)return;busy=true;
    marcarLogout101110();
    const oldToken=typeof token!=='undefined'?String(token||''):'';
    try{token='';me=null;caixaAtual=null}catch{}
    try{
      const remover=[];
      for(let i=0;i<localStorage.length;i++){
        const k=localStorage.key(i);if(k&&k!==LOGOUT_FLAG&&/(token|session|remember|auth|login|pass)/i.test(k))remover.push(k)
      }
      remover.forEach(k=>localStorage.removeItem(k));sessionStorage.clear();
    }catch{}
    try{await window.eletromixRemember101011?.clear?.()}catch{}
    try{await window.eletromix101010?.sessionClear?.()}catch{}
    try{if(typeof apagarSessao10109==='function')apagarSessao10109()}catch{}
    try{if(oldToken)await fetch('/api/logout',{method:'POST',headers:{Authorization:'Bearer '+oldToken,'X-Store-Id':String(typeof lojaId!=='undefined'?lojaId:1)},keepalive:true})}catch{}
    try{showLogin()}catch{document.querySelector('#loginScreen')?.classList.remove('hidden');document.querySelector('#app')?.classList.add('hidden')}
    const u=document.querySelector('#login'),p=document.querySelector('#senha');if(u)u.value='';if(p)p.value='';
    // Não recarrega: o marcador bloqueia os timers antigos já agendados e evita o efeito desloga/loga.
    setTimeout(()=>{busy=false},250);
  }

  document.addEventListener('click',e=>{
    const b=e.target?.closest?.('button,a,[role="button"]');if(!b)return;
    const txt=String(b.textContent||'').replace(/\s+/g,' ').trim();
    if(!(/^sair$/i.test(txt)||b.matches('#logout,#logoutBtn,#sairBtn,[data-action="logout"],.logout-btn')))return;
    e.preventDefault();e.stopPropagation();e.stopImmediatePropagation();sairSemRelogar101110();
  },true);
  try{logout=function(){sairSemRelogar101110()}}catch{}
})();
'''
write('public/app.js',js)
print('10.11.10: logout manual bloqueia rotinas antigas de auto-login ate o usuario entrar novamente de forma manual.')
