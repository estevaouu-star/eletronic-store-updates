from pathlib import Path
import json

root = Path("app")

def read(path: str) -> str:
    return (root / path).read_text(encoding="utf-8")

def write(path: str, content: str) -> None:
    (root / path).write_text(content, encoding="utf-8")

def replace_once(content: str, old: str, new: str, label: str) -> str:
    if old not in content:
        raise SystemExit(f"Trecho não encontrado: {label}")
    return content.replace(old, new, 1)

pkg = json.loads(read("package.json"))
pkg["version"] = "10.10.31"
write("package.json", json.dumps(pkg, indent=2, ensure_ascii=False))

html = read("public/index.html")
html = replace_once(html, 'id="versionInfo" class="version-info">v10.10.30', 'id="versionInfo" class="version-info">v10.10.31', "versão no cabeçalho")
write("public/index.html", html)

js = read("public/app.js")
js = replace_once(js, 'const atual="10.10.30"', 'const atual="10.10.31"', "versão do atualizador")

js += r'''

// 10.10.31 - restaura cancelar/excluir venda e deixa o cliente da OS como nome digitado livremente.
linhaVenda101024=function(v){
 const podeFiscal=me?.cargo==='admin'&&v.status==='concluida';
 const acaoVenda=v.status==='concluida'
  ?`<button class="delete" type="button" onclick="cancelVenda(${v.id})">Cancelar</button>`
  :v.status==='cancelada'
   ?`<button class="delete" type="button" onclick="deleteVenda(${v.id})">Excluir</button>`:'';
 return `<tr><td><b>#${v.id}</b></td><td>${new Date(v.criadoEm).toLocaleTimeString('pt-BR',{hour:'2-digit',minute:'2-digit'})}</td><td>${esc(v.clienteNome)}</td><td>${esc(v.vendedorNome||v.usuarioNome)}</td><td>${esc(v.formaPagamento)}${v.troco?`<small class="sale-change-101024">Troco ${money(v.troco)}</small>`:''}</td><td><b>${money(v.total)}</b></td><td><span class="sale-status-101024 ${v.status}">${v.status==='concluida'?'Finalizada':'Cancelada'}</span></td><td>${v.fiscal?`<span class="fiscal-badge">${v.fiscal.tipo==='rascunho-nfe'?'NF-e':'NFC-e'} rascunho</span>`:'-'}</td><td><div class="row-actions"><button class="edit" type="button" onclick="viewVenda(${v.id})">Ver</button>${podeFiscal?`<button class="edit" type="button" onclick="fiscalVenda(${v.id})">Fiscal</button>`:''}${acaoVenda}</div></td></tr>`;
};

novaOS=async function(){
 try{await loadServicos()}catch(e){console.error('[OS serviços 101031]',e);return toast('Não foi possível carregar os serviços.')}
 openModal('Nova ordem de serviço',`<form id="osForm101031" class="os-form-101023"><section><h4>Cliente e aparelho</h4><div class="form-grid"><div><label>Cliente *</label><input name="clienteNome" type="text" autocomplete="off" placeholder="Digite o nome do cliente" required></div><div><label>Telefone</label><input name="telefone" inputmode="tel" placeholder="(00) 00000-0000"></div><div><label>Aparelho *</label><input name="aparelho" placeholder="Ex.: Celular, notebook" required></div><div><label>Marca</label><input name="marca"></div><div><label>Modelo</label><input name="modelo"></div><div><label>Serviço</label><select name="servicoId" id="osServico101031">${osServiceOptions101023('')}</select><small id="osServicoHelp101031" class="os-field-help-101023">Diagnóstico inicial, sem serviço definido.</small></div></div></section><section><h4>Atendimento</h4><label>Problema relatado</label><textarea name="problemaRelatado" rows="3" placeholder="Descreva o que o cliente informou..."></textarea><div class="form-grid"><div><label>Valor combinado (opcional)</label><input name="valor" type="number" min="0" step="0.01" placeholder="Usar preço do serviço"></div><div><label>Observações internas</label><input name="observacoes"></div></div></section><button type="submit" class="primary os-submit-101023">Criar ordem de serviço</button></form>`);
 const form=document.querySelector('#osForm101031'),select=document.querySelector('#osServico101031'),help=document.querySelector('#osServicoHelp101031');
 select?.addEventListener('change',()=>{const service=servicos.find(s=>String(s.id)===select.value);if(help)help.textContent=service?`${service.nome} · preço cadastrado ${money(service.preco)}`:'Diagnóstico inicial, sem serviço definido.'});
 form.onsubmit=async event=>{
  event.preventDefault();const button=form.querySelector('button[type="submit"]');button.disabled=true;button.textContent='Criando ordem...';
  try{
   const raw=Object.fromEntries(new FormData(form));if(!String(raw.valor||'').trim())delete raw.valor;
   const response=await api('/api/ordens-servico',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(raw)}),data=await response.json().catch(()=>({}));
   if(!response.ok)throw new Error(data.erro||'Não foi possível criar a ordem.');
   closeModal();await loadOS();toast(`Ordem #${data.id} criada.`);
  }catch(e){console.error('[criar OS 101031]',e);toast(e?.message||'Erro ao criar ordem.');button.disabled=false;button.textContent='Criar ordem de serviço'}
 };
};
'''
write("public/app.js", js)

print("10.10.31: ações Cancelar/Excluir restauradas em Vendas e cliente da OS como campo de nome livre.")
