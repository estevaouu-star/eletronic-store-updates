from pathlib import Path
import json
root=Path('app')
def read(p): return (root/p).read_text(encoding='utf-8')
def write(p,s): (root/p).write_text(s,encoding='utf-8')
def must(s,a,b,label):
    if a not in s: raise RuntimeError(f'Trecho não encontrado: {label}')
    return s.replace(a,b,1)
pkg=json.loads(read('package.json'));pkg['version']='10.6.0';write('package.json',json.dumps(pkg,indent=2,ensure_ascii=False))
# Adiciona módulo NFC-e separado e seguro: configuração e validação em homologação. Não transmite nem simula autorização.
html=read('public/index.html')
nav='''<button class="nav-item" data-page="fiscal">'''
if nav in html:
    html=html.replace(nav,'''<button class="nav-item" data-page="nfce"><span class="nav-icon">▤</span><span>NFC-e</span></button>\n      '''+nav,1)
else:
    marker='''<main class="content">'''
    html=must(html,marker,'''<button class="nav-item" data-page="nfce"><span class="nav-icon">▤</span><span>NFC-e</span></button>\n    '''+marker,'nav nfce fallback')
page='''
<section id="page-nfce" class="page">
  <div class="page-header"><div><h2>NFC-e</h2><p>Configuração fiscal e preparação para emissão em homologação.</p></div><span class="nfce-badge">HOMOLOGAÇÃO</span></div>
  <div class="nfce-warning"><b>Ambiente de testes</b><span>Esta versão não transmite NFC-e nem marca documento como autorizado. A emissão real só será habilitada após certificado, CSC e integração SEFAZ estarem configurados e validados.</span></div>
  <div class="grid-2 nfce-grid">
    <div class="panel"><h3>Configuração fiscal da empresa</h3><form id="nfceConfigForm" class="form-grid">
      <div class="full"><label>Razão social</label><input name="razaoSocial"></div><div><label>CNPJ</label><input name="cnpj"></div><div><label>Inscrição Estadual</label><input name="ie"></div>
      <div><label>UF</label><input name="uf" maxlength="2" value="SP"></div><div><label>Código do município (IBGE)</label><input name="cMun"></div><div><label>Regime tributário (CRT)</label><select name="crt"><option value="">Selecione</option><option value="1">1 - Simples Nacional</option><option value="2">2 - Simples Nacional excesso sublimite</option><option value="3">3 - Regime Normal</option><option value="4">4 - MEI</option></select></div>
      <div><label>Série NFC-e</label><input name="serie" type="number" min="1" value="1"></div><div><label>CSC ID</label><input name="cscId"></div><div class="full"><label>CSC</label><input name="csc" type="password" autocomplete="off"></div>
      <div class="full"><label>Certificado digital</label><input name="certificadoNome" placeholder="Será conectado na etapa de transmissão" disabled></div>
      <button class="primary full" type="submit">Salvar configuração de homologação</button>
    </form></div>
    <div class="panel"><h3>Prontidão para NFC-e</h3><div id="nfceChecklist" class="nfce-checklist"></div><hr><h3>Produtos com dados fiscais pendentes</h3><p class="muted">Para emissão real, os produtos precisarão das classificações fiscais corretas definidas com o contador.</p><div id="nfceProdutosPendentes"></div></div>
  </div>
  <div class="panel"><div class="section-head"><div><h3>Preparar NFC-e</h3><p class="muted">Selecione uma venda concluída para validar os dados antes da futura transmissão.</p></div></div><div id="nfceVendas"></div></div>
</section>
'''
html=must(html,'</main>',page+'\n</main>','pagina nfce')
write('public/index.html',html)
js=read('public/app.js')
js += r'''
const NFCE_CONFIG_KEY="eletromix_nfce_config_v1";
function nfceConfig(){try{return JSON.parse(localStorage.getItem(NFCE_CONFIG_KEY)||"{}")||{}}catch{return {}}}
function nfceSalvarConfig(e){e.preventDefault();const d=Object.fromEntries(new FormData(e.target));localStorage.setItem(NFCE_CONFIG_KEY,JSON.stringify(d));renderNfce();toast("Configuração fiscal de homologação salva neste computador.")}
function nfcePendenciasConfig(c){const campos=[["razaoSocial","Razão social"],["cnpj","CNPJ"],["ie","Inscrição Estadual"],["uf","UF"],["cMun","Município (IBGE)"],["crt","Regime tributário"],["serie","Série"],["cscId","CSC ID"],["csc","CSC"]];return campos.filter(([k])=>!String(c[k]||"").trim()).map(([,n])=>n)}
function nfceProdutoPendente(p){const f=[];if(!String(p.ncm||"").trim())f.push("NCM");if(!String(p.cfop||"").trim())f.push("CFOP");if(!String(p.cest||"").trim())f.push("CEST (quando aplicável)");return f}
async function renderNfce(){
 const form=$("#nfceConfigForm");if(!form)return;const c=nfceConfig();Object.entries(c).forEach(([k,v])=>{if(form.elements[k])form.elements[k].value=v});
 const falt=nfcePendenciasConfig(c);const ck=$("#nfceChecklist");if(ck)ck.innerHTML=`<div class="nfce-check ${falt.length?"bad":"ok"}"><b>${falt.length?"Configuração incompleta":"Configuração básica preenchida"}</b><span>${falt.length?`Falta: ${falt.map(esc).join(", ")}`:"Ainda falta conectar e validar certificado + SEFAZ antes da emissão real."}</span></div><div class="nfce-check bad"><b>Transmissão SEFAZ</b><span>Desativada nesta versão. Nenhuma nota será marcada como autorizada sem resposta real da SEFAZ.</span></div>`;
 const pp=(window.produtos||[]).map(p=>({p,f:nfceProdutoPendente(p)})).filter(x=>x.f.length);const ph=$("#nfceProdutosPendentes");if(ph)ph.innerHTML=pp.slice(0,20).map(x=>`<div class="pending-row"><span>${esc(x.p.nome||x.p.codigo)}</span><b>${x.f.join(", ")}</b></div>`).join("")||'<p class="muted">Nenhuma pendência básica detectada.</p>';
 const vh=$("#nfceVendas");if(vh){let vs=[];try{vs=await(await api("/api/vendas")).json()}catch{};vs=Array.isArray(vs)?vs.filter(v=>v.status==="concluida").slice(0,20):[];vh.innerHTML=vs.map(v=>`<div class="nfce-sale"><div><b>Venda #${v.id}</b><span>${esc(v.clienteNome||"Consumidor final")} · ${money(v.total)}</span></div><button class="secondary small" onclick="nfceValidarVenda(${v.id})">Validar para NFC-e</button></div>`).join("")||'<p class="muted">Nenhuma venda concluída encontrada.</p>'}
}
async function nfceValidarVenda(id){const c=nfceConfig(),erros=nfcePendenciasConfig(c);let vs=await(await api("/api/vendas")).json(),v=(Array.isArray(vs)?vs:[]).find(x=>x.id===id);if(!v)return toast("Venda não encontrada.");const ids=new Set((v.itens||[]).map(i=>i.produtoId));(window.produtos||[]).filter(p=>ids.has(p.id)).forEach(p=>{const f=nfceProdutoPendente(p);if(f.length)erros.push(`${p.nome}: ${f.join(", ")}`)});if(erros.length)return openModal("NFC-e ainda não está pronta",`<div class="nfce-validation"><p>Corrija estas informações antes da emissão fiscal:</p>${erros.map(x=>`<div class="pending-row"><span>${esc(x)}</span></div>`).join("")}<p class="muted">Nenhum documento foi transmitido à SEFAZ.</p></div>`);openModal("Validação NFC-e",`<div class="nfce-validation"><div class="nfce-check ok"><b>Validação cadastral concluída</b><span>A venda #${id} passou pelas verificações básicas.</span></div><p><b>Próxima etapa:</b> certificado digital, geração/assinatura do XML, validação XSD, QR Code/CSC e autorização síncrona da SEFAZ em homologação.</p><p class="muted">Esta tela não é uma autorização fiscal.</p></div>`)}
document.addEventListener("submit",e=>{if(e.target?.id==="nfceConfigForm")nfceSalvarConfig(e)});
document.addEventListener("click",e=>{const n=e.target?.closest?.('[data-page="nfce"]');if(n)setTimeout(renderNfce,50)});
'''
write('public/app.js',js)
css=read('public/style.css')
css += '''\n.nfce-badge{font-size:11px;font-weight:900;padding:7px 10px;border-radius:999px;background:#fff3cd;color:#7a5700}.nfce-warning{display:flex;gap:12px;align-items:flex-start;padding:13px 15px;margin-bottom:14px;border:1px solid #f0cf69;background:#fff9e8;border-radius:12px}.nfce-warning span{font-size:12px}.nfce-grid{align-items:start}.nfce-checklist{display:grid;gap:8px}.nfce-check{display:grid;gap:3px;padding:11px;border-radius:10px}.nfce-check.ok{background:#eaf8ee;color:#17652e}.nfce-check.bad{background:#fff2f0;color:#8c2820}.nfce-check span{font-size:11px}.nfce-sale{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:10px 0;border-bottom:1px solid var(--border)}.nfce-sale>div{display:grid;gap:2px}.nfce-sale span{font-size:11px;color:var(--muted)}.nfce-validation{display:grid;gap:10px}.pending-row{width:100%;display:flex;justify-content:space-between;gap:12px;padding:9px 10px;border:0;border-bottom:1px solid var(--border);background:transparent;text-align:left}.pending-row b{font-size:10px;text-align:right}@media(max-width:700px){.nfce-sale{align-items:flex-start;flex-direction:column}}\n'''
write('public/style.css',css)
print('Patch 10.6.0 aplicado: módulo NFC-e em homologação, sem transmissão simulada.')