from pathlib import Path
import json,re

root=Path('app')
def read(p): return (root/p).read_text(encoding='utf-8')
def write(p,s): (root/p).write_text(s,encoding='utf-8')

pkg=json.loads(read('package.json'));pkg['version']='10.11.13';write('package.json',json.dumps(pkg,indent=2,ensure_ascii=False))
html=read('public/index.html');html,n=re.subn(r'(id="versionInfo" class="version-info">v)[0-9.]+',r'\g<1>10.11.13',html,count=1)
if n!=1: raise SystemExit('versao html nao encontrada')
write('public/index.html',html)

server=read('src/server.ts')
old='''app.get("/api/lojas",auth,(req,res)=>{
  const u=(req as any).usuario as Usuario;
  const ids=new Set(idsLojasPermitidas(u));
  res.json(db.lojas.filter(l=>ids.has(l.id)));
});'''
new='''app.get("/api/lojas",auth,(req,res)=>{
  const u=(req as any).usuario as Usuario;
  const visiveis=u.cargo==="admin"&&u.acessoTodasLojas===true?db.lojas:lojasPermitidasUsuario(u);
  res.json(visiveis.map(l=>({...l,registros:{produtos:db.produtos.filter(x=>x.lojaId===l.id).length,vendas:db.vendas.filter(x=>x.lojaId===l.id).length,clientes:db.clientes.filter(x=>x.lojaId===l.id).length,vendedores:db.vendedores.filter(x=>x.lojaId===l.id).length,servicos:db.servicos.filter(x=>x.lojaId===l.id).length,ordensServico:db.ordensServico.filter(x=>x.lojaId===l.id).length,movimentos:db.movimentos.filter(x=>x.lojaId===l.id).length,caixas:db.caixas.filter(x=>x.lojaId===l.id).length,diagnosticos:db.diagnosticosSeguranca.filter(x=>x.lojaId===l.id).length}})));
});'''
if old not in server: raise SystemExit('rota de lojas nao encontrada')
server=server.replace(old,new,1)

old_access='''  if(!idsLojasPermitidas(operador).includes(l.id))return res.status(403).json({erro:"Você não possui acesso a esta loja."});'''
new_access='''  const global=operador.cargo==="admin"&&operador.acessoTodasLojas===true;
  if(!global&&!idsLojasPermitidas(operador).includes(l.id))return res.status(403).json({erro:"Você não possui acesso a esta loja."});'''
if old_access not in server: raise SystemExit('controle de edicao de loja nao encontrado')
server=server.replace(old_access,new_access,1)

anchor='''app.get("/api/lojas/resumo-geral",auth,(req,res)=>{'''
delete_route='''app.delete("/api/lojas/:id",auth,adminGlobal,(req,res)=>{
  const id=Number(req.params.id),loja=db.lojas.find(l=>l.id===id);
  if(!loja)return res.status(404).json({erro:"Loja não encontrada."});
  if(loja.ativo)return res.status(400).json({erro:"Desative a loja antes de excluí-la."});
  if(String(req.body?.confirmacao||"").trim().toLowerCase()!==loja.nome.trim().toLowerCase())return res.status(400).json({erro:"Digite o nome exato da loja para confirmar."});
  if(db.lojas.filter(l=>l.ativo&&l.id!==id).length===0)return res.status(400).json({erro:"Mantenha pelo menos uma loja ativa."});
  const removidos={produtos:db.produtos.filter(x=>x.lojaId===id).length,vendas:db.vendas.filter(x=>x.lojaId===id).length,clientes:db.clientes.filter(x=>x.lojaId===id).length,vendedores:db.vendedores.filter(x=>x.lojaId===id).length,servicos:db.servicos.filter(x=>x.lojaId===id).length,ordensServico:db.ordensServico.filter(x=>x.lojaId===id).length,movimentos:db.movimentos.filter(x=>x.lojaId===id).length,caixas:db.caixas.filter(x=>x.lojaId===id).length,diagnosticos:db.diagnosticosSeguranca.filter(x=>x.lojaId===id).length};
  db.produtos=db.produtos.filter(x=>x.lojaId!==id);db.vendas=db.vendas.filter(x=>x.lojaId!==id);db.clientes=db.clientes.filter(x=>x.lojaId!==id);db.vendedores=db.vendedores.filter(x=>x.lojaId!==id);db.servicos=db.servicos.filter(x=>x.lojaId!==id);db.ordensServico=db.ordensServico.filter(x=>x.lojaId!==id);db.movimentos=db.movimentos.filter(x=>x.lojaId!==id);db.caixas=db.caixas.filter(x=>x.lojaId!==id);db.diagnosticosSeguranca=db.diagnosticosSeguranca.filter(x=>x.lojaId!==id);db.lojas=db.lojas.filter(l=>l.id!==id);
  for(const usuario of db.usuarios)usuario.lojaIds=(usuario.lojaIds||[]).filter(lojaId=>Number(lojaId)!==id);
  salvar();res.json({ok:true,loja:{id,nome:loja.nome},removidos});
});

'''
if anchor not in server: raise SystemExit('ancora para exclusao de loja nao encontrada')
server=server.replace(anchor,delete_route+anchor,1)
write('src/server.ts',server)

js=read('public/app.js');js,n=re.subn(r'const atual="[0-9.]+"(?=,status=)','const atual="10.11.13"',js,count=1)
if n!=1: raise SystemExit('versao atualizador nao encontrada')
old_render='''  $("#tableLojas").innerHTML=lojas.map(l=>`<tr><td><b>${esc(l.nome)}</b></td><td>${esc(l.cnpj||"-")}</td><td>${esc(l.telefone||"-")}</td><td>${esc(l.endereco||"-")}</td><td class="${l.ativo?"status-ok":"status-off"}">${l.ativo?"Ativa":"Inativa"}</td><td><div class="row-actions"><button class="edit" onclick="editLoja(${l.id})">Editar</button></div></td></tr>`).join("");'''
new_render='''  $("#tableLojas").innerHTML=lojas.map(l=>{const r=l.registros||{},total=Object.values(r).reduce((s,n)=>s+Number(n||0),0);return `<tr><td><b>${esc(l.nome)}</b><small style="display:block;color:#6b7680">${total} registros · ${Number(r.produtos||0)} produtos · ${Number(r.vendas||0)} vendas</small></td><td>${esc(l.cnpj||"-")}</td><td>${esc(l.telefone||"-")}</td><td>${esc(l.endereco||"-")}</td><td class="${l.ativo?"status-ok":"status-off"}">${l.ativo?"Ativa":"Inativa"}</td><td><div class="row-actions"><button class="edit" onclick="editLoja(${l.id})">Editar</button>${!l.ativo?`<button class="delete" onclick="excluirLoja101113(${l.id})">Excluir tudo</button>`:""}</div></td></tr>`}).join("");'''
if old_render not in js: raise SystemExit('renderizacao de lojas nao encontrada')
js=js.replace(old_render,new_render,1)
insert='''
async function excluirLoja101113(id){
 const l=lojas.find(x=>x.id===id);if(!l||l.ativo)return toast("Desative a loja antes de excluir.");
 const r=l.registros||{},total=Object.values(r).reduce((s,n)=>s+Number(n||0),0);
 const confirmacao=prompt(`ATENÇÃO: serão apagados definitivamente ${total} registros de ${l.nome}, incluindo ${Number(r.produtos||0)} produtos e ${Number(r.vendas||0)} vendas.\\n\\nDigite exatamente o nome da loja para confirmar:`);
 if(confirmacao===null)return;
 const resp=await api(`/api/lojas/${id}`,{method:"DELETE",headers:{"Content-Type":"application/json"},body:JSON.stringify({confirmacao})}),out=await resp.json();
 if(!resp.ok)return toast(out.erro||"Não foi possível excluir a loja.");
 localStorage.removeItem(`es_printer_store_${id}`);await loadLojas();toast(`${l.nome} e todos os dados vinculados foram excluídos.`);
}
window.excluirLoja101113=excluirLoja101113;
'''
marker='''async function loadAllStores(){'''
if marker not in js: raise SystemExit('ancora frontend lojas nao encontrada')
js=js.replace(marker,insert+'\n'+marker,1)

js=js.replace('if(status)status.textContent=`Impresso em ${r.deviceName||printerSettings.deviceName}${r.mode==="escpos"?" · térmico direto · corte automático":""}.`;','if(status)status.textContent=`Trabalho enviado para ${r.deviceName||printerSettings.deviceName}${r.mode==="escpos"?" · térmico direto":""}.`; ',1)
js=js.replace('toast(r?.success?"Teste enviado diretamente para a ELGIN i8.":`Falha no teste: ${r?.failureReason||"erro"}`);','toast(r?.success?`Teste enviado para ${r.deviceName||printerSettings.deviceName}. Confira o papel e a fila do Windows.`:`Falha no teste: ${r?.failureReason||"erro"}`);',1)

js+='''\n// 10.11.13 - atualização de autenticação: força uma entrada manual uma única vez nesta versão.\n(function(){try{const k="eletromix_auth_release",v="10.11.13";if(localStorage.getItem(k)===v)return;localStorage.setItem(k,v);localStorage.removeItem("es_token");localStorage.setItem("eletromix_manual_logout_101110","1");Promise.resolve(window.eletromix101010?.sessionClear?.()).catch(()=>{});}catch{}})();\n'''
write('public/app.js',js)

main=read('electron/main.cjs')
helper='''function isVirtualPrinter101113(printer){
  const label=`${printer?.name||""} ${printer?.displayName||""} ${printer?.description||""}`;
  return /onenote|one note|notas|bloco de notas|notepad|pdf|xps|fax|microsoft print|send to/i.test(label);
}

'''
anchor_main='''ipcMain.handle("printer:list", async () => {'''
if 'function isVirtualPrinter101113' not in main:
  if anchor_main not in main: raise SystemExit('handler de impressoras nao encontrado')
  main=main.replace(anchor_main,helper+anchor_main,1)
main=main.replace('const printers = await mainWindow.webContents.getPrintersAsync();','const printers = (await mainWindow.webContents.getPrintersAsync()).filter(p=>!isVirtualPrinter101113(p));',1)
main=main.replace('try { available = mainWindow ? await mainWindow.webContents.getPrintersAsync() : []; } catch {}','try { available = mainWindow ? (await mainWindow.webContents.getPrintersAsync()).filter(p=>!isVirtualPrinter101113(p)) : []; } catch {}',1)
main=main.replace('if(deviceName && !available.some(p=>p.name===deviceName))deviceName="";','if(deviceName && (!available.some(p=>p.name===deviceName)||isVirtualPrinter101113({name:deviceName})))deviceName="";',1)
main=main.replace('const preferred=available.find(p=>/epson|bematech|elgin|daruma|control.?id|thermal|t[eé]rmica|receipt|pos|tm-|mp-|80|58/i.test(`${p.name} ${p.displayName||""} ${p.description||""}`))||available.find(p=>p.isDefault)||available[0];','const preferred=available.find(p=>/elgin.*i8|i8.*elgin/i.test(`${p.name} ${p.displayName||""} ${p.description||""}`))||available.find(p=>/epson|bematech|elgin|daruma|control.?id|thermal|t[eé]rmica|receipt|pos|tm-|mp-|80|58/i.test(`${p.name} ${p.displayName||""} ${p.description||""}`))||available.find(p=>p.isDefault)||available[0];',1)
main=main.replace('if(process.platform==="win32" && !/pdf|xps|onenote|fax/i.test(deviceName)){','if(process.platform==="win32" && !isVirtualPrinter101113({name:deviceName})){',1)
write('electron/main.cjs',main)
print('10.11.13: lojas inativas visiveis e exclusao completa; login renovado; impressao fisica filtrada com prioridade para ELGIN i8.')
