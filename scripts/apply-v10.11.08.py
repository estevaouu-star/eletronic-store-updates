from pathlib import Path
import json,re
root=Path('app')
def read(p): return (root/p).read_text(encoding='utf-8')
def write(p,s): (root/p).write_text(s,encoding='utf-8')

pkg=json.loads(read('package.json'));pkg['version']='10.11.8';write('package.json',json.dumps(pkg,indent=2,ensure_ascii=False))
html=read('public/index.html');html,n=re.subn(r'(id="versionInfo" class="version-info">v)[0-9.]+',r'\g<1>10.11.08',html,count=1)
if n!=1: raise SystemExit('versao html nao encontrada')
write('public/index.html',html)

js=read('public/app.js');js,n=re.subn(r'const atual="[0-9.]+"(?=,status=)','const atual="10.11.8"',js,count=1)
if n!=1: raise SystemExit('versao atualizador nao encontrada')
js += r'''

// 10.11.08 - logout realmente definitivo: limpa também credenciais de auto-login e captura qualquer botão "Sair".
(function(){
  let logout108Busy=false;
  function limparTudoLogin101108(){
    try{
      const chaves=[
        'es_token','eletromix_session','es_session_10107',
        'es_remember_version','es_remember_login','es_remember_pass',
        'rememberVersion10105','rememberLogin10105','rememberPass10105'
      ];
      chaves.forEach(k=>localStorage.removeItem(k));
      // Remove somente chaves relacionadas a autenticação; mantém impressora, aparência e demais preferências.
      const remover=[];
      for(let i=0;i<localStorage.length;i++){
        const k=localStorage.key(i);if(k&&/(^es_.*(token|session|remember|auth|login|pass)|eletromix.*(session|auth|login|token))/i.test(k))remover.push(k);
      }
      remover.forEach(k=>localStorage.removeItem(k));
      sessionStorage.clear();
    }catch(e){console.warn('[logout101108 storage]',e)}
    try{token='';me=null;caixaAtual=null}catch{}
  }
  async function sair101108(){
    if(logout108Busy)return;logout108Busy=true;
    const oldToken=typeof token!=='undefined'?String(token||''):'';
    limparTudoLogin101108();
    try{await window.eletromix101010?.sessionClear?.()}catch{}
    try{await window.eletromixRemember101011?.clear?.()}catch{}
    try{if(typeof apagarSessao10109==='function')apagarSessao10109()}catch{}
    try{if(oldToken)fetch('/api/logout',{method:'POST',headers:{Authorization:'Bearer '+oldToken,'X-Store-Id':String(typeof lojaId!=='undefined'?lojaId:1)},keepalive:true}).catch(()=>{})}catch{}
    // Recarregar é intencional: mata todas as rotinas antigas de restauração que já possam estar em memória.
    setTimeout(()=>location.reload(),40);
  }
  document.addEventListener('click',e=>{
    const b=e.target?.closest?.('button,a,[role="button"]');if(!b)return;
    const txt=String(b.textContent||'').replace(/\s+/g,' ').trim();
    const ehSair=/^sair$/i.test(txt)||b.matches('#logout,#logoutBtn,#sairBtn,[data-action="logout"],.logout-btn');
    if(!ehSair)return;
    e.preventDefault();e.stopPropagation();e.stopImmediatePropagation();sair101108();
  },true);
  try{logout=function(){sair101108()}}catch{}
})();
'''
write('public/app.js',js)
print('10.11.08: logout limpa token, sessão e credenciais lembradas antes de recarregar; qualquer botão Sair é capturado antes dos handlers antigos.')
