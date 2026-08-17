from pathlib import Path
import re
root=Path('app')
def read(p): return (root/p).read_text(encoding='utf-8')
def write(p,s): (root/p).write_text(s,encoding='utf-8')

# Sessão persistente no backend: o token deixa de morrer quando o app fecha.
server=read('src/server.ts')
old='const sessoes = new Map<string,{usuarioId:number;expira:number}>();'
new='''type SessaoPersistente108={token:string;usuarioId:number;expira:number};
const dbSessao108=db as any;
if(!Array.isArray(dbSessao108.sessoesPersistentes))dbSessao108.sessoesPersistentes=[];
const sessoes = new Map<string,{usuarioId:number;expira:number}>((dbSessao108.sessoesPersistentes as SessaoPersistente108[]).filter(s=>s&&s.token&&s.expira>Date.now()).map(s=>[s.token,{usuarioId:s.usuarioId,expira:s.expira}]));
function salvarSessaoPersistente108(token:string,usuarioId:number){
  const expira=Date.now()+3650*24*60*60*1000;
  sessoes.set(token,{usuarioId,expira});
  const a=(dbSessao108.sessoesPersistentes as SessaoPersistente108[]).filter(s=>s.token!==token&&s.expira>Date.now());
  a.push({token,usuarioId,expira});dbSessao108.sessoesPersistentes=a;salvar();
}'''
if old not in server: raise RuntimeError('Mapa de sessoes nao encontrado')
server=server.replace(old,new,1)
server,n=re.subn(r'sessoes\.set\(token,\{usuarioId:u\.id,expira:Date\.now\(\)\+8\*60\*60\*1000\}\);','salvarSessaoPersistente108(token,u.id);',server,count=1)
if n!=1: raise RuntimeError('Criacao da sessao no login nao encontrada')
write('src/server.ts',server)

# Corrige a área de Categorias: a 10.10.7 aplicou scroll no container errado.
js=read('public/app.js')
js += r'''
// 10.10.8 fix - scroll só na grade real de categorias.
function corrigirCategorias108(){
 document.querySelectorAll('#caixa .categorias-scroll-10107').forEach(e=>e.classList.remove('categorias-scroll-10107'));
 const cats=document.querySelector('#pdvCategorias');if(cats)cats.classList.add('pdv-categorias-scroll-108');
}
document.addEventListener('DOMContentLoaded',()=>setTimeout(corrigirCategorias108,80));
document.addEventListener('click',e=>{if(e.target.closest?.('.nav[data-s="caixa"]'))setTimeout(corrigirCategorias108,40)},true);
setTimeout(corrigirCategorias108,300);setTimeout(corrigirCategorias108,900);
'''
write('public/app.js',js)
css=read('public/style.css')+r'''
/* 10.10.8 fix - desfaz a deformação visual e rola somente categorias */
#caixa .categorias-scroll-10107{max-height:none!important;overflow:visible!important;padding-right:0!important}
#caixa #pdvCategorias.pdv-categorias-scroll-108{max-height:142px!important;overflow-y:auto!important;overflow-x:hidden!important;overscroll-behavior:contain!important;scrollbar-width:thin!important;padding-right:4px!important;align-content:start!important}
#caixa #pdvCategorias.pdv-categorias-scroll-108::-webkit-scrollbar{width:7px}#caixa #pdvCategorias.pdv-categorias-scroll-108::-webkit-scrollbar-thumb{background:#ffffff35;border-radius:8px}
'''
write('public/style.css',css)
print('10.10.8 fix: sessao persiste entre reinicios e Categorias voltam ao layout correto com scroll interno.')