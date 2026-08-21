from pathlib import Path
import json
root=Path('app')
def read(p): return (root/p).read_text(encoding='utf-8')
def write(p,s): (root/p).write_text(s,encoding='utf-8')
def replace1(s,a,b,label):
    if a not in s: raise RuntimeError(f'Trecho nao encontrado: {label}')
    return s.replace(a,b,1)

pkg=json.loads(read('package.json'));pkg['version']='10.10.39';write('package.json',json.dumps(pkg,indent=2,ensure_ascii=False))
html=read('public/index.html');html=replace1(html,'id="versionInfo" class="version-info">v10.10.38','id="versionInfo" class="version-info">v10.10.39','versao');write('public/index.html',html)
js=read('public/app.js');js=replace1(js,'const atual="10.10.38"','const atual="10.10.39"','atualizador')

# Restaura o botão de exclusão perdido quando o render das OS foi refeito na 10.10.36.
old='''<button type="button" class="secondary os-edit-101023" data-edit-os="${o.id}">${osFinalizada101036(o)?'Ver ordem / vias':'Abrir / atualizar'}</button></footer></article>'''
new='''<div class="os-actions-101039"><button type="button" class="secondary os-edit-101023" data-edit-os="${o.id}">${osFinalizada101036(o)?'Ver ordem / vias':'Abrir / atualizar'}</button>${!osFinalizada101036(o)?`<button type="button" class="danger os-delete-101039" data-delete-os-101039="${o.id}">Excluir OS</button>`:''}</div></footer></article>'''
js=replace1(js,old,new,'botao excluir OS')

js += r'''

// 10.10.39 - exclusão de OS não finalizada restaurada.
async function excluirOS101039(id){
 const o=(ordensServico||[]).find(x=>x.id===Number(id));
 if(!o)return toast('Ordem de serviço não encontrada.');
 if(o.status==='Finalizado')return toast('OS finalizada fica protegida no histórico e não pode ser excluída.');
 if(!confirm(`Excluir definitivamente a OS #${o.id} de ${o.clienteNome}?`))return;
 try{
   const r=await api(`/api/ordens-servico/${o.id}`,{method:'DELETE'});
   const data=await r.json().catch(()=>({}));
   if(!r.ok)throw new Error(data.erro||'Não foi possível excluir a ordem.');
   await loadOS();
   toast(`OS #${o.id} excluída.`);
 }catch(e){toast(e?.message||'Erro ao excluir a ordem de serviço.')}
}
document.addEventListener('click',e=>{
 const b=e.target?.closest?.('[data-delete-os-101039]');
 if(!b)return;
 e.preventDefault();e.stopPropagation();
 excluirOS101039(Number(b.dataset.deleteOs101039));
});
'''
write('public/app.js',js)

css=read('public/style.css')
css += r'''
/* 10.10.39 - ações da OS */
.os-actions-101039{display:flex;gap:7px;align-items:center;flex-wrap:wrap}.os-delete-101039{background:#fff!important;color:#b42318!important;border:1px solid #f0b4ae!important}.os-delete-101039:hover{background:#fff0ee!important}
'''
write('public/style.css',css)
print('10.10.39: opção Excluir OS restaurada para ordens não finalizadas.')
