from pathlib import Path
import json,re
root=Path('app')
def read(p): return (root/p).read_text(encoding='utf-8')
def write(p,s): (root/p).write_text(s,encoding='utf-8')

pkg=json.loads(read('package.json'));pkg['version']='10.11.7';write('package.json',json.dumps(pkg,indent=2,ensure_ascii=False))
html=read('public/index.html');html,n=re.subn(r'(id="versionInfo" class="version-info">v)[0-9.]+',r'\g<1>10.11.07',html,count=1)
if n!=1: raise SystemExit('versao html nao encontrada')
write('public/index.html',html)

server=read('src/server.ts')
if 'app.post("/api/logout"' not in server:
    server += r'''

// 10.11.07 - encerra a sessão no servidor quando o usuário clica em Sair.
app.post("/api/logout",auth,(req,res)=>{
  const header=String(req.headers.authorization||"");
  const sessionToken=header.startsWith("Bearer ")?header.slice(7):"";
  if(sessionToken)sessoes.delete(sessionToken);
  res.json({ok:true});
});
'''
write('src/server.ts',server)

js=read('public/app.js');js,n=re.subn(r'const atual="[0-9.]+"(?=,status=)','const atual="10.11.7"',js,count=1)
if n!=1: raise SystemExit('versao atualizador nao encontrada')
js += r'''

// 10.11.07 - categoria/marca reutilizáveis no cadastro e edição de produto + logout real.
(function(){
  function valoresProdutos101107(campo){
    const valores=(Array.isArray(window.produtos)?window.produtos:typeof produtos!=='undefined'&&Array.isArray(produtos)?produtos:[])
      .map(p=>String(p?.[campo]||'').trim()).filter(Boolean);
    return [...new Map(valores.map(v=>[v.toLocaleLowerCase('pt-BR'),v])).values()].sort((a,b)=>a.localeCompare(b,'pt-BR'));
  }
  function garantirLista101107(input,campo,label){
    if(!input||input.tagName!=='INPUT')return;
    const id=`produto-${campo}-existentes-101107`;
    input.setAttribute('list',id);input.setAttribute('autocomplete','off');
    let dl=document.getElementById(id);if(!dl){dl=document.createElement('datalist');dl.id=id;document.body.appendChild(dl)}
    const atuais=valoresProdutos101107(campo),valorAtual=String(input.value||'').trim();
    const todos=valorAtual&&!atuais.some(v=>v.toLocaleLowerCase('pt-BR')===valorAtual.toLocaleLowerCase('pt-BR'))?[valorAtual,...atuais]:atuais;
    dl.replaceChildren(...todos.map(v=>{const o=document.createElement('option');o.value=v;return o}));
    const box=input.closest('div,label')||input.parentElement;
    if(box&&!box.querySelector(`.produto-combo-hint-101107[data-campo="${campo}"]`)){
      const small=document.createElement('small');small.className='produto-combo-hint-101107';small.dataset.campo=campo;small.textContent=`Escolha um(a) ${label.toLowerCase()} já existente ou digite um novo.`;box.appendChild(small);
    }
  }
  function melhorarFormProduto101107(root=document){
    const forms=[...root.querySelectorAll?.('form')||[]];
    if(root.matches?.('form'))forms.unshift(root);
    for(const form of forms){
      const categoria=form.querySelector('[name="categoria"]'),marca=form.querySelector('[name="marca"]');
      if(!categoria||!marca)continue;
      garantirLista101107(categoria,'categoria','Categoria');
      garantirLista101107(marca,'marca','Marca');
    }
  }
  document.addEventListener('focusin',e=>{if(e.target?.matches?.('[name="categoria"],[name="marca"]'))melhorarFormProduto101107(e.target.closest('form')||document)});
  const obs=new MutationObserver(muts=>{for(const m of muts)for(const n of m.addedNodes)if(n?.nodeType===1)melhorarFormProduto101107(n)});
  document.addEventListener('DOMContentLoaded',()=>{melhorarFormProduto101107();obs.observe(document.body,{childList:true,subtree:true})});
  setTimeout(()=>melhorarFormProduto101107(),500);

  let saindo101107=false;
  async function sairDeVerdade101107(){
    if(saindo101107)return;saindo101107=true;
    const oldToken=typeof token!=='undefined'?token:'';
    try{if(oldToken)await fetch('/api/logout',{method:'POST',headers:{Authorization:'Bearer '+oldToken,'X-Store-Id':String(typeof lojaId!=='undefined'?lojaId:1)}})}catch(e){console.warn('[logout 101107 servidor]',e)}
    try{localStorage.removeItem('es_token');localStorage.removeItem('eletromix_session');localStorage.removeItem('es_session_10107')}catch{}
    try{await window.eletromix101010?.sessionClear?.()}catch{}
    try{await window.eletromixRemember101011?.clear?.()}catch{}
    try{if(typeof apagarSessao10109==='function')apagarSessao10109()}catch{}
    try{token='';me=null;caixaAtual=null}catch{}
    const login=document.querySelector('#login'),senha=document.querySelector('#senha'),erro=document.querySelector('#loginError');
    if(login)login.value='';if(senha)senha.value='';if(erro)erro.textContent='';
    try{showLogin()}catch{document.querySelector('#loginScreen')?.classList.remove('hidden');document.querySelector('#app')?.classList.add('hidden')}
    saindo101107=false;
  }
  // Captura antes dos listeners antigos: Sair não fecha mais o aplicativo e não preserva sessão.
  document.addEventListener('click',e=>{
    const b=e.target?.closest?.('#logoutBtn,[data-action="logout"],.logout-btn');if(!b)return;
    e.preventDefault();e.stopPropagation();e.stopImmediatePropagation();sairDeVerdade101107();
  },true);
})();
'''
write('public/app.js',js)

css=read('public/style.css')+r'''

/* 10.11.07 - ajuda dos seletores de categoria/marca */
.produto-combo-hint-101107{display:block;margin-top:4px;font-size:11px;line-height:1.3;color:var(--muted,var(--text-muted,#6b7280))}
'''
write('public/style.css',css)
print('10.11.07: categoria e marca aceitam existentes ou novos valores; Sair encerra a sessão sem fechar o app.')
