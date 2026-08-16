from pathlib import Path
import json,re
root=Path('app')
def read(p): return (root/p).read_text(encoding='utf-8')
def write(p,s): (root/p).write_text(s,encoding='utf-8')

def inject_before_config_end(html, block):
    start=html.find('<section id="config" class="section">')
    if start<0: raise RuntimeError('Seção Configurações não encontrada')
    end=html.find('</section>', start)
    if end<0: raise RuntimeError('Fim da seção Configurações não encontrado')
    return html[:end]+block+'\n'+html[end:]

pkg=json.loads(read('package.json'))
pkg['version']='10.7.0'
write('package.json',json.dumps(pkg,indent=2,ensure_ascii=False))

html=read('public/index.html')
# 10.7 parte da base limpa 10.5: NFC-e fica DENTRO de Configurações, não cria item lateral nem seção solta.
nfce='''
<div class="settings-divider"></div>
<div class="settings-block nfce-settings-block">
  <div class="settings-block-head">
    <div>
      <span class="eyebrow">FISCAL</span>
      <h3>NFC-e</h3>
      <p>Prepare os dados fiscais da loja para futura emissão em homologação. O caixa normal continua independente.</p>
    </div>
    <span class="status-pill warning">Homologação</span>
  </div>
  <div class="nfce-info-card">
    <div class="nfce-info-icon">i</div>
    <div><b>Modo seguro</b><p>Esta versão organiza e valida os dados, mas ainda não transmite nem simula autorização da SEFAZ.</p></div>
  </div>
  <form id="nfceConfigForm" class="form-grid nfce-form">
    <div class="full"><label>Razão social</label><input name="razaoSocial" placeholder="Nome empresarial"></div>
    <div><label>CNPJ</label><input name="cnpj" placeholder="00.000.000/0000-00"></div>
    <div><label>Inscrição Estadual</label><input name="ie" placeholder="Inscrição estadual"></div>
    <div><label>UF</label><input name="uf" maxlength="2" value="SP"></div>
    <div><label>Código do município (IBGE)</label><input name="cMun" placeholder="Ex.: 3518404"></div>
    <div><label>Regime tributário (CRT)</label><select name="crt"><option value="">Selecione</option><option value="1">1 - Simples Nacional</option><option value="2">2 - Simples Nacional - excesso sublimite</option><option value="3">3 - Regime Normal</option><option value="4">4 - MEI</option></select></div>
    <div><label>Série NFC-e</label><input name="serie" type="number" min="1" value="1"></div>
    <div><label>CSC ID</label><input name="cscId" placeholder="Identificador do CSC"></div>
    <div class="full"><label>CSC</label><input name="csc" type="password" autocomplete="off" placeholder="Código de Segurança do Contribuinte"></div>
    <div class="full nfce-actions"><button class="primary" type="submit">Salvar configuração fiscal</button><button class="secondary" id="nfceValidarConfig" type="button">Verificar pendências</button></div>
  </form>
  <div id="nfceChecklist" class="nfce-checklist"></div>
</div>
'''
html=inject_before_config_end(html,nfce)
write('public/index.html',html)

js=read('public/app.js')
js += r'''
// Eletromix 10.7 - NFC-e dentro de Configurações, sem nova aba lateral.
const NFCE_CONFIG_KEY="eletromix_nfce_config_v2";
function nfceConfig(){try{return JSON.parse(localStorage.getItem(NFCE_CONFIG_KEY)||"{}")||{}}catch{return {}}}
function nfcePendencias(c){
  const campos=[["razaoSocial","Razão social"],["cnpj","CNPJ"],["ie","Inscrição Estadual"],["uf","UF"],["cMun","Município (IBGE)"],["crt","Regime tributário"],["serie","Série NFC-e"],["cscId","CSC ID"],["csc","CSC"]];
  return campos.filter(([k])=>!String(c[k]||"").trim()).map(([,n])=>n);
}
function renderNfceConfig(){
  const form=document.querySelector('#nfceConfigForm'); if(!form)return;
  const c=nfceConfig();
  Object.entries(c).forEach(([k,v])=>{if(form.elements[k])form.elements[k].value=v});
  const falt=nfcePendencias(c),box=document.querySelector('#nfceChecklist');
  if(box)box.innerHTML=`<div class="nfce-ready-card ${falt.length?'pending':'ready'}"><div><b>${falt.length?'Configuração incompleta':'Dados básicos preenchidos'}</b><span>${falt.length?`Falta preencher: ${falt.map(esc).join(', ')}`:'Pronto para a próxima etapa de homologação: certificado digital e integração oficial com a SEFAZ.'}</span></div><strong>${falt.length?falt.length:'✓'}</strong></div>`;
}
document.addEventListener('submit',e=>{
  if(e.target?.id!=='nfceConfigForm')return;
  e.preventDefault(); const d=Object.fromEntries(new FormData(e.target));
  localStorage.setItem(NFCE_CONFIG_KEY,JSON.stringify(d)); renderNfceConfig(); toast('Configuração fiscal salva.');
});
document.addEventListener('click',e=>{
  if(e.target?.closest?.('#nfceValidarConfig')){e.preventDefault();renderNfceConfig();const f=nfcePendencias(nfceConfig());toast(f.length?`Ainda faltam ${f.length} informações fiscais.`:'Dados básicos preenchidos.');}
  const nav=e.target?.closest?.('.nav[data-s="config"]'); if(nav)setTimeout(renderNfceConfig,50);
});
document.addEventListener('DOMContentLoaded',renderNfceConfig);
'''
write('public/app.js',js)

css=read('public/style.css')
css += '''
/* Eletromix 10.7 - refinamento visual geral */
:root{--radius-xl:16px;--shadow-soft:0 8px 24px rgba(30,20,20,.06)}
main{padding-top:22px}
.card{border-radius:var(--radius-xl);box-shadow:var(--shadow-soft);border-color:color-mix(in srgb,var(--border) 82%,transparent)}
.title h2{letter-spacing:-.025em}.title p{margin-top:3px}
aside{padding-top:10px}.nav{border-radius:10px;margin:2px 7px;transition:background .15s ease,transform .15s ease}.nav:hover{transform:translateX(2px)}
.primary,.secondary{border-radius:10px;font-weight:750;transition:transform .12s ease,box-shadow .12s ease}.primary:hover,.secondary:hover{transform:translateY(-1px)}
input,select,textarea{border-radius:10px}
.settings-divider{height:1px;background:var(--border);margin:24px 0}
.settings-block{padding:20px;border:1px solid var(--border);border-radius:16px;background:var(--card-bg);box-shadow:var(--shadow-soft)}
.settings-block-head{display:flex;justify-content:space-between;align-items:flex-start;gap:16px;margin-bottom:16px}.settings-block-head h3{font-size:20px;margin:2px 0 4px}.settings-block-head p{margin:0;color:var(--muted);max-width:720px}.eyebrow{font-size:10px;font-weight:900;letter-spacing:.13em;color:var(--primary)}
.status-pill{padding:7px 10px;border-radius:999px;font-size:11px;font-weight:850;white-space:nowrap}.status-pill.warning{background:#fff5d9;color:#765400;border:1px solid #f0d47a}
.nfce-info-card{display:flex;gap:12px;align-items:flex-start;padding:13px 14px;border-radius:12px;background:#fff9e8;border:1px solid #efd47a;margin-bottom:16px}.nfce-info-card p{margin:3px 0 0;font-size:12px;color:#625431}.nfce-info-icon{width:24px;height:24px;border-radius:50%;display:grid;place-items:center;background:#f4c84c;color:#4d3900;font-weight:900;flex:0 0 auto}
.nfce-form{padding-top:4px}.nfce-actions{display:flex;gap:10px;align-items:center}.nfce-checklist{margin-top:14px}.nfce-ready-card{display:flex;justify-content:space-between;gap:18px;align-items:center;padding:13px 14px;border-radius:12px}.nfce-ready-card>div{display:grid;gap:3px}.nfce-ready-card span{font-size:12px}.nfce-ready-card strong{font-size:18px}.nfce-ready-card.pending{background:#fff1ef;color:#8d2d25}.nfce-ready-card.ready{background:#eaf8ef;color:#1f6c38}
@media(max-width:700px){.settings-block-head{flex-direction:column}.nfce-actions{flex-direction:column;align-items:stretch}.nfce-actions button{width:100%}}
'''
write('public/style.css',css)
print('Patch 10.7.0 aplicado: NFC-e dentro de Configurações e refinamento visual geral.')
