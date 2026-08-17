from pathlib import Path
import json
root=Path('app')
def read(p): return (root/p).read_text(encoding='utf-8')
def write(p,s): (root/p).write_text(s,encoding='utf-8')
def must(s,a,b,label):
    if a not in s: raise RuntimeError('Trecho nao encontrado: '+label)
    return s.replace(a,b,1)

pkg=json.loads(read('package.json'));pkg['version']='10.9.2';write('package.json',json.dumps(pkg,indent=2,ensure_ascii=False))
html=read('public/index.html').replace('id="versionInfo" class="version-info">v10.9.1','id="versionInfo" class="version-info">v10.9.2',1);write('public/index.html',html)
js=read('public/app.js').replace('const atual="10.9.1"','const atual="10.9.2"',1)
# Sessao persistente: valida token salvo antes de exibir login. Mantem login ate Sair ou 401 real.
js += r'''
// 10.9.2 - restauração persistente da sessão
async function restoreEletromixSession(){
  const saved=localStorage.getItem('es_token');
  if(!saved)return false;
  token=saved;
  try{
    const r=await fetch('/api/me',{headers:{Authorization:'Bearer '+saved,'X-Store-Id':String(lojaId)}});
    if(!r.ok)throw new Error('sessao invalida');
    me=await r.json(); caixaAtual=me.caixa||null; showApp(); await boot(); loadCloudStatus().catch(()=>{}); return true;
  }catch(e){token='';me=null;localStorage.removeItem('es_token');showLogin();return false}
}
document.addEventListener('DOMContentLoaded',()=>{setTimeout(restoreEletromixSession,20)});
'''
# Corrige paginação: não clona todos os cards. Move os 3 atuais para DOM e guarda originais em fragmento JS.
old="const s=q('#produtos'); if(!s||s.dataset.page3==='1')return; const list=qa('.product',s); if(list.length<=3)return; s.dataset.page3='1'; let page=1; const size=3; const host=list[0].parentElement; const all=list.map(x=>x.cloneNode(true));\n   list.forEach(x=>x.remove());"
new="const s=q('#produtos'); if(!s||s.dataset.page3==='1')return; const list=qa('.product',s); if(list.length<=3)return; s.dataset.page3='1'; let page=1; const size=3; const host=list[0].parentElement; const all=[...list];\n   list.forEach(x=>x.remove());"
js=must(js,old,new,'paginacao sem clones')
js=js.replace("all.slice(start,start+size).forEach(x=>host.appendChild(x.cloneNode(true)))","all.slice(start,start+size).forEach(x=>host.appendChild(x))",1)
# Novo layout do caixa: reorganiza os blocos existentes em duas colunas e preserva handlers originais.
js += r'''
(function(){
 function buildPdvLayout(){
  const s=document.querySelector('#caixa');if(!s||s.dataset.layout1092==='1')return;
  const catalog=s.querySelector('.pdv-catalog-columns');if(!catalog)return;
  s.dataset.layout1092='1';s.classList.add('pdv-1092');
  s.querySelectorAll('.smart-pdv-commandbar').forEach(x=>x.remove());
  const cards=[...s.children].filter(x=>x.classList?.contains('card')&&x!==catalog&& !x.contains(catalog));
  const wrap=document.createElement('div');wrap.className='pdv1092-layout';
  const left=document.createElement('div');left.className='pdv1092-left';
  const right=document.createElement('div');right.className='pdv1092-right';
  catalog.parentNode.insertBefore(wrap,catalog);wrap.append(left,right);
  cards.forEach(c=>left.appendChild(c));right.appendChild(catalog);
  const browser=s.querySelector('.smart-browser');if(browser)browser.classList.add('pdv1092-browser');
  const pay=[...left.querySelectorAll('button')].find(b=>/ir para pagamento|finalizar venda|cobrar/i.test(b.textContent||''));if(pay){pay.textContent='COBRAR';pay.classList.add('pdv1092-charge')}
 }
 document.addEventListener('click',e=>{if(e.target.closest?.('.nav[data-s="caixa"]'))setTimeout(buildPdvLayout,60)});
 document.addEventListener('DOMContentLoaded',()=>setTimeout(buildPdvLayout,500));setTimeout(buildPdvLayout,900);
})();
'''
write('public/app.js',js)
css=read('public/style.css')+r'''
/* 10.9.2 - layout PDV em duas áreas, conforme referência */
#caixa.pdv-1092 .smart-pdv-commandbar{display:none!important}#caixa.pdv-1092{max-width:1600px!important}.pdv1092-layout{display:grid;grid-template-columns:minmax(430px,44%) minmax(520px,56%);gap:10px;align-items:start}.pdv1092-left,.pdv1092-right{min-width:0}.pdv1092-left{display:grid;gap:8px}.pdv1092-right>.pdv-catalog-columns{display:block!important;margin:0!important}.pdv1092-right .pdv-catalog-pane{border-radius:7px!important}.pdv1092-browser .smart-categories{grid-template-columns:repeat(4,minmax(90px,1fr))}.pdv1092-browser .smart-products-grid{grid-template-columns:repeat(4,minmax(105px,1fr));max-height:58vh}.pdv1092-charge{width:100%!important;min-height:54px!important;font-size:19px!important;font-weight:900!important}.pdv1092-left .card{margin:0!important}.pdv1092-right .pdv-catalog-columns>.pdv-catalog-pane+ .pdv-catalog-pane{margin-top:8px}@media(max-width:1050px){.pdv1092-layout{grid-template-columns:1fr}.pdv1092-browser .smart-products-grid{grid-template-columns:repeat(3,1fr)}}
'''
write('public/style.css',css)
print('10.9.2 aplicada: layout PDV duas colunas, Produtos 3 por pagina sem clones e sessao persistente.')