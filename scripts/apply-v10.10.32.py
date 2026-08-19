from pathlib import Path
import json,re

root=Path('app')
def read(p): return (root/p).read_text(encoding='utf-8')
def write(p,s): (root/p).write_text(s,encoding='utf-8')
def replace1(s,a,b,label):
    if a not in s: raise RuntimeError(label)
    return s.replace(a,b,1)

pkg=json.loads(read('package.json'));pkg['version']='10.10.32';write('package.json',json.dumps(pkg,indent=2,ensure_ascii=False))
html=read('public/index.html');html=replace1(html,'id="versionInfo" class="version-info">v10.10.31','id="versionInfo" class="version-info">v10.10.32','versão');write('public/index.html',html)

server=read('src/server.ts')
# Cancelar/excluir venda deixa de exigir cargo admin, mas continua autenticado e limitado
# à loja da sessão porque os handlers de venda localizam os registros com lojaIdReq(req).
server=re.sub(r'(app\.(?:put|post|delete)\("/api/vendas/[^\"]*(?:cancel|cancelar|:id)[^\"]*",\s*auth),\s*admin,',r'\1,',server,flags=re.I)
write('src/server.ts',server)

js=read('public/app.js');js=replace1(js,'const atual="10.10.31"','const atual="10.10.32"','atualizador')
js += r'''

// 10.10.32 - correção de emergência: campos digitáveis e vendas operáveis pelo vendedor da loja.
linhaVenda101024=function(v){
 const fiscal=v.status==='concluida'?`<button class="edit" type="button" onclick="fiscalVenda(${v.id})">Fiscal</button>`:'';
 const acao=v.status==='concluida'?`<button class="delete" type="button" onclick="cancelVenda(${v.id})">Cancelar</button>`:v.status==='cancelada'?`<button class="delete" type="button" onclick="deleteVenda(${v.id})">Excluir</button>`:'';
 return `<tr><td><b>#${v.id}</b></td><td>${new Date(v.criadoEm).toLocaleTimeString('pt-BR',{hour:'2-digit',minute:'2-digit'})}</td><td>${esc(v.clienteNome)}</td><td>${esc(v.vendedorNome||v.usuarioNome)}</td><td>${esc(v.formaPagamento)}${v.troco?`<small class="sale-change-101024">Troco ${money(v.troco)}</small>`:''}</td><td><b>${money(v.total)}</b></td><td><span class="sale-status-101024 ${v.status}">${v.status==='concluida'?'Finalizada':'Cancelada'}</span></td><td>${v.fiscal?`<span class="fiscal-badge">${v.fiscal.tipo==='rascunho-nfe'?'NF-e':'NFC-e'} rascunho</span>`:'-'}</td><td><div class="row-actions"><button class="edit" type="button" onclick="viewVenda(${v.id})">Ver</button>${fiscal}${acao}</div></td></tr>`;
};

function camposEditaveis101032(root=document){
 root.querySelectorAll?.('form input:not([type="hidden"]),form textarea,form select,.modal input:not([type="hidden"]),.modal textarea,.modal select').forEach(el=>{
  el.style.pointerEvents='auto';
  el.style.userSelect='text';
  if(el.matches('input,textarea'))el.readOnly=false;
  if(!el.dataset?.preserveDisabled101032)el.disabled=false;
  el.removeAttribute('readonly');
  if(!el.dataset?.preserveDisabled101032)el.removeAttribute('disabled');
 });
}
camposEditaveis101032();
new MutationObserver(records=>{for(const r of records)for(const n of r.addedNodes)if(n.nodeType===1)camposEditaveis101032(n)}).observe(document.body,{childList:true,subtree:true});
document.addEventListener('click',e=>{if(e.target?.closest?.('input,textarea,select,#novaOSBtn,.os-edit-101023,.nav'))setTimeout(()=>camposEditaveis101032(),0)},true);

// Ordem de serviço: cliente é nome livre digitado pelo atendente.
const novaOS101032=novaOS;
novaOS=async function(){
 await novaOS101032();
 setTimeout(()=>{
  const form=document.querySelector('#osForm101031,#osForm101023');if(!form)return;
  const cliente=form.querySelector('[name="clienteNome"]');
  if(cliente){cliente.removeAttribute('list');cliente.readOnly=false;cliente.disabled=false;cliente.placeholder='Digite o nome do cliente';cliente.autocomplete='off';cliente.focus()}
  camposEditaveis101032(form);
 },40);
};
'''
write('public/app.js',js)

css=read('public/style.css')+r'''

/* 10.10.32 - restaura interação dos formulários */
form input:not([type="hidden"]),form textarea,form select,.modal input:not([type="hidden"]),.modal textarea,.modal select{pointer-events:auto!important;user-select:text!important;-webkit-user-select:text!important}
.os-form-101023,.os-form-101023 *{pointer-events:auto}
'''
write('public/style.css',css)
print('10.10.32: digitação restaurada, cliente da OS livre e cancelar/excluir venda liberados dentro da loja autenticada.')
