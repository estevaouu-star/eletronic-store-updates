from pathlib import Path
import json,re
root=Path('app')
def read(p): return (root/p).read_text(encoding='utf-8')
def write(p,s): (root/p).write_text(s,encoding='utf-8')
def replace1(s,a,b,label):
    if a not in s: raise RuntimeError(f'Trecho nao encontrado: {label}')
    return s.replace(a,b,1)

pkg=json.loads(read('package.json'));pkg['version']='10.10.41';write('package.json',json.dumps(pkg,indent=2,ensure_ascii=False))
html=read('public/index.html');html=replace1(html,'id="versionInfo" class="version-info">v10.10.40','id="versionInfo" class="version-info">v10.10.41','versao');write('public/index.html',html)
js=read('public/app.js');js=replace1(js,'const atual="10.10.40"','const atual="10.10.41"','atualizador')
server=read('src/server.ts')

# GARANTIA: nunca inferir/iniciar garantia só por criar, carregar ou mudar status.
# Somente req.body.iniciarGarantia===true pode preencher prontoEm/garantiaAte.
server=server.replace('for(const o of db.ordensServico){garantirDatasOS101030(o,true);migrarStatusOS101036(o)};', 'for(const o of db.ordensServico){migrarStatusOS101036(o)};')
server=server.replace('for(const o of db.ordensServico)garantirDatasOS101030(o,true);', 'for(const o of db.ordensServico){ /* garantia somente por acionamento manual */ }')
server=server.replace('for(const o of lista)changed=garantirDatasOS101030(o,true)||changed;', '/* 10.10.41: não aciona/migra garantia ao listar OS */')
server=server.replace('  garantirDatasOS101030(o,true);\n', '')
server=server.replace('    garantirDatasOS101030(o,false);\n', '')
# Corrige dados criados indevidamente: OS que ainda não foi finalizada não deve nascer com garantia.
# Preserva garantias de OS Finalizado, que podem ser legítimas/históricas.
marker='const migrarStatusOS101036=(o:any)=>{'
if marker in server and 'LIMPAR_GARANTIA_INDEVIDA_101041' not in server:
    pos=server.find(marker)
    # injeta uma limpeza no carregamento, após migração dos status
    target='for(const o of db.ordensServico){migrarStatusOS101036(o)};'
    repl='for(const o of db.ordensServico){migrarStatusOS101036(o); /* LIMPAR_GARANTIA_INDEVIDA_101041 */ if(o.status!=="Finalizado"&&o.prontoEm){delete o.prontoEm;delete o.garantiaAte}};'
    server=server.replace(target,repl,1)

# Exclusão: garantir endpoint DELETE para qualquer OS da loja, inclusive finalizada.
# Remove eventual proteção antiga no DELETE.
server=server.replace('if(o.status==="Finalizado")return res.status(409).json({erro:"Esta ordem de serviço foi finalizada e está bloqueada para alterações."});','if(req.method!=="DELETE"&&o.status==="Finalizado")return res.status(409).json({erro:"Esta ordem de serviço foi finalizada e está bloqueada para alterações."});')

js += r'''

// 10.10.41 - garantia manual de verdade + ações de OS restauradas.
function osGarantiaAtiva101041(o){return Boolean(o&&o.prontoEm&&o.garantiaAte)}

// Corrige a apresentação: OS recém-criada/sem acionamento mostra garantia não iniciada.
const renderOSBase101041=renderOS;
renderOS=function(){
 renderOSBase101041();
 document.querySelectorAll('.os-card-101023[data-os-id]').forEach(card=>{
   const o=(ordensServico||[]).find(x=>Number(x.id)===Number(card.dataset.osId));if(!o)return;
   const footer=card.querySelector('footer');if(!footer)return;
   const divs=footer.querySelectorAll(':scope > div');
   if(divs[1]&&!osGarantiaAtiva101041(o))divs[1].innerHTML='<span>Garantia</span><b>Não acionada</b>';
 });
};

function imprimirGarantia101041(o){
 if(!osGarantiaAtiva101041(o))return toast('Acione a garantia antes de imprimir.');
 const html=osViaHtml101036(o,'garantia');if(!html)return toast('Não foi possível montar a via de garantia.');
 if(typeof imprimirHtmlOS101038==='function')return imprimirHtmlOS101038(`Garantia OS #${o.id}`,html);
 visualizarVia101036(o,'garantia');
}

async function acionarGarantia101041(o,button){
 if(osGarantiaAtiva101041(o))return imprimirGarantia101041(o);
 if(!confirm(`Acionar agora os 3 meses de garantia da OS #${o.id}? A data e hora atuais serão o início da garantia.`))return;
 if(button){button.disabled=true;button.textContent='Acionando garantia...'}
 try{
   const r=await api(`/api/ordens-servico/${o.id}`,{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify({iniciarGarantia:true})});
   const data=await r.json().catch(()=>({}));if(!r.ok)throw new Error(data.erro||'Não foi possível acionar a garantia.');
   await loadOS();closeModal();toast(`Garantia da OS #${o.id} acionada.`);
 }catch(e){toast(e?.message||'Erro ao acionar garantia.');if(button){button.disabled=false;button.textContent='Acionar garantia'}}
}

// Substitui a edição por um complemento de ações confiável, sem remover os campos existentes.
const editOSBase101041=editOS;
editOS=function(id){
 editOSBase101041(id);
 setTimeout(()=>{
   const o=(ordensServico||[]).find(x=>Number(x.id)===Number(id));if(!o)return;
   const form=document.querySelector('#editOSForm101023');if(!form)return;
   let actions=form.querySelector('.os-warranty-actions-101041');if(actions)actions.remove();
   actions=document.createElement('div');actions.className='os-warranty-actions-101041';
   actions.innerHTML=osGarantiaAtiva101041(o)
     ? `<button type="button" class="primary" id="printWarranty101041">Imprimir garantia</button><span>Garantia acionada: ${dataHoraRecibo101025(o.prontoEm)} até ${dataHoraRecibo101025(o.garantiaAte)}</span>`
     : `<button type="button" class="primary" id="startWarranty101041">Acionar garantia</button><span>A garantia só começa quando este botão for acionado.</span>`;
   form.appendChild(actions);
   document.querySelector('#startWarranty101041')?.addEventListener('click',e=>acionarGarantia101041(o,e.currentTarget));
   document.querySelector('#printWarranty101041')?.addEventListener('click',()=>imprimirGarantia101041(o));

   // Exclusão dentro da OS também fica sempre disponível.
   let del=form.querySelector('#deleteOS101041');
   if(!del){del=document.createElement('button');del.type='button';del.id='deleteOS101041';del.className='danger';del.textContent='Excluir definitivamente';form.appendChild(del)}
   del.onclick=()=>excluirOS101039(Number(o.id));
 },0);
};
'''
write('public/app.js',js);write('src/server.ts',server)
print('10.10.41: garantia somente manual, botão Acionar garantia restaurado, impressão após acionamento e exclusão de OS disponível.')
