from pathlib import Path
import json

root=Path('app')

def read(p): return (root/p).read_text(encoding='utf-8')
def write(p,s): (root/p).write_text(s,encoding='utf-8')
def replace1(s,a,b,label):
    if a not in s: raise RuntimeError(label)
    return s.replace(a,b,1)

pkg=json.loads(read('package.json'))
pkg['version']='10.8.5'
write('package.json',json.dumps(pkg,indent=2,ensure_ascii=False))

html=read('public/index.html')
html=html.replace('id="versionInfo" class="version-info">v10.8.4','id="versionInfo" class="version-info">v10.8.5',1)
html=replace1(html,'<button id="novoUsuarioBtn" class="primary small" type="button">Novo usuário</button>','<div class="access-head-actions"><button id="editarMeuAcessoBtn" class="secondary small" type="button">Editar meu acesso</button><button id="novoUsuarioBtn" class="primary small" type="button">Novo usuário</button></div>','botao de acesso')
write('public/index.html',html)

css=read('public/style.css')
css+='\n/* 10.8.5 */\n.access-head-actions{display:flex;gap:8px;align-items:center;flex-wrap:wrap}\n@media(max-width:720px){.access-head-actions{width:100%}.access-head-actions button{flex:1}}\n'
write('public/style.css',css)

js=read('public/app.js')
old='async function boot(){renderEsIcons();await Promise.all([loadAparencia(),loadConfig(),loadProdutos(),loadServicos(),loadClientes(),loadVendedores(),loadCaixa(),loadLojas()]);renderCart();renderEsIcons();await loadDashboard()}'
new='async function boot(){renderEsIcons();await Promise.all([loadAparencia(),loadConfig(),loadProdutos(),loadServicos(),loadClientes(),loadVendedores(),loadCaixa(),loadLojas()]);if(me?.cargo==="admin")await loadUsuarios();renderCart();renderEsIcons();await loadDashboard()}'
js=replace1(js,old,new,'boot usuarios')
js=replace1(js,'if(nav.dataset.s==="config")await loadConfigForm();','if(nav.dataset.s==="config"){await loadConfigForm();if(me?.cargo==="admin")await loadUsuarios();}','config usuarios')
parallel='document.addEventListener("click",e=>{\n  if(e.target?.closest?.(\'.nav[data-s="config"]\') && me?.cargo==="admin")setTimeout(()=>loadUsuarios().catch(()=>{}),80);\n});\n'
if parallel in js: js=js.replace(parallel,'',1)
anchor='function newUsuario(){\n  if(me?.cargo!=="admin")return toast("Somente o administrador pode criar logins.");'
replacement='function editMeuAcesso(){if(me?.cargo!=="admin")return;if(me?.id)return editUsuario(Number(me.id));}\n'+anchor
js=replace1(js,anchor,replacement,'editar meu acesso')
js=replace1(js,'  $("#novoUsuarioBtn")?.addEventListener("click",newUsuario);','  $("#editarMeuAcessoBtn")?.addEventListener("click",editMeuAcesso);\n  $("#novoUsuarioBtn")?.addEventListener("click",newUsuario);','evento editar meu acesso')
js=js.replace('const atual="10.8.4"','const atual="10.8.5"',1)
write('public/app.js',js)

print('Patch 10.8.5 aplicado.')