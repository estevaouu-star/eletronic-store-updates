from pathlib import Path
import json
root=Path('app')
def read(p): return (root/p).read_text(encoding='utf-8')
def write(p,s): (root/p).write_text(s,encoding='utf-8')

pkg=json.loads(read('package.json'));pkg['version']='10.10.12';write('package.json',json.dumps(pkg,indent=2,ensure_ascii=False))
html=read('public/index.html').replace('id="versionInfo" class="version-info">v10.10.11','id="versionInfo" class="version-info">v10.10.12',1)

# Injeta configuração de monitor dentro da seção Configurações.
block='''\n<div class="settings-divider"></div>\n<div class="settings-block monitor-profile-settings">\n  <div class="settings-block-head">\n    <div><span class="eyebrow">TELA</span><h3>Perfil do monitor</h3><p>Escolha um layout otimizado para a resolução deste computador. O modo automático detecta o tamanho da tela.</p></div>\n  </div>\n  <div class="form-grid">\n    <div class="full"><label>Versão do layout</label><select id="monitorProfileSelect">\n      <option value="auto">Automático</option>\n      <option value="1024x768">1024 × 768 · Monitor antigo</option>\n      <option value="1366x768">1366 × 768 · HD</option>\n      <option value="1600x900">1600 × 900 · Intermediário</option>\n      <option value="1920x1080">1920 × 1080 · Full HD</option>\n    </select></div>\n    <div class="full monitor-profile-note" id="monitorProfileInfo"></div>\n  </div>\n</div>\n'''
start=html.find('<section id="config" class="section">')
if start<0: raise RuntimeError('Seção Configurações não encontrada')
end=html.find('</section>',start)
if end<0: raise RuntimeError('Fim de Configurações não encontrado')
html=html[:end]+block+html[end:]
write('public/index.html',html)

js=read('public/app.js').replace('const atual="10.10.11"','const atual="10.10.12"',1)
js += r'''
// 10.10.12 - perfis de monitor por computador.
const MONITOR_PROFILE_KEY='eletromix_monitor_profile_v1';
function detectarPerfilMonitor101012(){
 const w=window.screen?.width||window.innerWidth||1366,h=window.screen?.height||window.innerHeight||768;
 if(w<=1100||h<=700)return '1024x768';
 if(w<=1450||h<=800)return '1366x768';
 if(w<=1700||h<=950)return '1600x900';
 return '1920x1080';
}
function aplicarPerfilMonitor101012(valor){
 const escolhido=valor||localStorage.getItem(MONITOR_PROFILE_KEY)||'auto';
 const real=escolhido==='auto'?detectarPerfilMonitor101012():escolhido;
 document.body.dataset.monitorProfile=real;
 document.body.dataset.monitorChoice=escolhido;
 const sel=document.querySelector('#monitorProfileSelect');if(sel)sel.value=escolhido;
 const info=document.querySelector('#monitorProfileInfo');
 if(info)info.textContent=`Tela detectada: ${window.screen?.width||window.innerWidth} × ${window.screen?.height||window.innerHeight}. Layout aplicado: ${real}.`;
}
document.addEventListener('change',e=>{
 if(e.target?.id!=='monitorProfileSelect')return;
 localStorage.setItem(MONITOR_PROFILE_KEY,e.target.value);aplicarPerfilMonitor101012(e.target.value);toast('Perfil do monitor salvo neste computador.');
});
document.addEventListener('click',e=>{if(e.target.closest?.('.nav[data-s="config"]'))setTimeout(()=>aplicarPerfilMonitor101012(),40)},true);
document.addEventListener('DOMContentLoaded',()=>aplicarPerfilMonitor101012());
window.addEventListener('resize',()=>{if((localStorage.getItem(MONITOR_PROFILE_KEY)||'auto')==='auto')aplicarPerfilMonitor101012('auto')});
setTimeout(()=>aplicarPerfilMonitor101012(),200);
'''
write('public/app.js',js)

css=read('public/style.css')+r'''
/* 10.10.12 - perfis de monitor */
.monitor-profile-note{font-size:12px;color:var(--muted);padding:10px 12px;border:1px solid var(--border);border-radius:10px;background:color-mix(in srgb,var(--card-bg) 94%,var(--accent) 6%)}
body[data-monitor-profile="1024x768"] header{min-height:52px!important;padding:6px 10px!important}body[data-monitor-profile="1024x768"] .brand-name{font-size:18px!important}body[data-monitor-profile="1024x768"] aside{width:122px!important}body[data-monitor-profile="1024x768"] .nav{font-size:11px!important;padding:8px 7px!important;margin:1px 4px!important}body[data-monitor-profile="1024x768"] main{padding:10px 10px!important}body[data-monitor-profile="1024x768"] #caixa{gap:8px!important}body[data-monitor-profile="1024x768"] #caixa .title h2{font-size:22px!important}body[data-monitor-profile="1024x768"] #caixa input,body[data-monitor-profile="1024x768"] #caixa select{min-height:36px!important;font-size:12px!important;padding:7px 9px!important}body[data-monitor-profile="1024x768"] #caixa button{min-height:34px!important;font-size:11px!important}body[data-monitor-profile="1024x768"] #caixa .pdv1094-layout,body[data-monitor-profile="1024x768"] #caixa .pdv-layout{grid-template-columns:minmax(360px,42%) minmax(0,58%)!important;gap:8px!important}body[data-monitor-profile="1024x768"] #caixa #pdvCategorias{max-height:112px!important}body[data-monitor-profile="1024x768"] #caixa .pdv1094-products,body[data-monitor-profile="1024x768"] #caixa .pdv-products{font-size:11px!important}body[data-monitor-profile="1024x768"] #caixa .pdv1094-product-card,body[data-monitor-profile="1024x768"] #caixa .pdv-product-card{min-height:74px!important;padding:7px!important}
body[data-monitor-profile="1366x768"] aside{width:150px!important}body[data-monitor-profile="1366x768"] main{padding:14px!important}body[data-monitor-profile="1366x768"] #caixa #pdvCategorias{max-height:132px!important}
body[data-monitor-profile="1600x900"] main{padding:18px!important}body[data-monitor-profile="1600x900"] #caixa #pdvCategorias{max-height:150px!important}
body[data-monitor-profile="1920x1080"] main{padding:22px!important}
'''
write('public/style.css',css)
print('10.10.12: adiciona em Configurações perfis de layout por monitor, incluindo modo compacto 1024x768.')