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
pkg["version"] = "10.10.33"
write("package.json", json.dumps(pkg, indent=2, ensure_ascii=False))

html = read("public/index.html")
html = replace_once(html, 'id="versionInfo" class="version-info">v10.10.32', 'id="versionInfo" class="version-info">v10.10.33', "versão no cabeçalho")
write("public/index.html", html)

js = read("public/app.js")
js = replace_once(js, 'const atual="10.10.32"', 'const atual="10.10.33"', "versão do atualizador")
js += r'''

// 10.10.33 - Ordem de Serviço disponível e utilizável no celular.
function osEhMobile101033(){return window.matchMedia?.('(max-width:760px)')?.matches||/Android|iPhone|iPad|iPod/i.test(navigator.userAgent||'')}
function osLauncherPodeAparecer101033(){
 if(!osEhMobile101033()||!document.querySelector('#ordensServico'))return false;
 try{if(typeof token!=='undefined'&&!token)return false}catch(e){}
 const loginVisible=[...document.querySelectorAll('#login,.login,.login-screen,#loginScreen')].some(el=>{const s=getComputedStyle(el);return s.display!=='none'&&s.visibility!=='hidden'&&!el.hidden});
 return !loginVisible;
}
function osNavExistente101033(){
 return [...document.querySelectorAll('button,a,[role="button"]')].find(el=>{
  if(el.id==='osMobileLauncher101033')return false;
  const alvo=String(el.dataset?.section||el.dataset?.target||el.getAttribute('href')||el.getAttribute('onclick')||'').toLowerCase();
  const texto=String(el.textContent||'').trim().toLowerCase();
  return alvo.includes('ordensservico')||alvo.includes('ordens-servico')||texto==='ordens de serviço'||texto==='ordem de serviço';
 });
}
async function abrirOSMobile101033(){
 const section=document.querySelector('#ordensServico');if(!section)return toast('Tela de Ordens de Serviço não encontrada.');
 const nav=osNavExistente101033();if(nav){try{nav.click()}catch(e){console.error('[OS mobile nav 101033]',e)}}
 const visivel=getComputedStyle(section).display!=='none'&&!section.hidden;
 if(!visivel){document.querySelectorAll('.section').forEach(s=>{s.classList.remove('active');if(s!==section)s.hidden=true});section.hidden=false;section.classList.add('active');section.style.removeProperty('display')}
 try{const jobs=[];if(typeof loadServicos==='function')jobs.push(Promise.resolve(loadServicos()));if(typeof loadOS==='function')jobs.push(Promise.resolve(loadOS()));if(typeof loadClientes==='function'&&(!Array.isArray(clientes)||!clientes.length))jobs.push(Promise.resolve(loadClientes()));if(jobs.length)await Promise.allSettled(jobs)}catch(e){console.error('[OS mobile load 101033]',e)}
 window.scrollTo({top:0,behavior:'smooth'});
}
function instalarOSMobile101033(){
 let button=document.querySelector('#osMobileLauncher101033');
 if(!button){button=document.createElement('button');button.type='button';button.id='osMobileLauncher101033';button.className='os-mobile-launcher-101033';button.innerHTML='<span class="os-mobile-launcher-icon-101033">OS</span><span>Ordens</span>';button.addEventListener('click',abrirOSMobile101033);document.body.appendChild(button)}
 button.hidden=!osLauncherPodeAparecer101033();
 const section=document.querySelector('#ordensServico');if(section){section.classList.add('os-mobile-ready-101033');const newButton=section.querySelector('#novaOSBtn');if(newButton){newButton.type='button';newButton.classList.add('os-mobile-new-101033')}}
}
function ajustarAcoesOSMobile101033(){if(!osEhMobile101033())return;document.querySelectorAll('#ordensServico .os-print-actions-101020').forEach(box=>box.classList.toggle('os-mobile-no-printer-101033',!window.desktopPrinter))}
const osObserver101033=new MutationObserver(()=>{instalarOSMobile101033();ajustarAcoesOSMobile101033()});
osObserver101033.observe(document.documentElement,{childList:true,subtree:true,attributes:true,attributeFilter:['class','hidden']});
window.addEventListener('resize',()=>{instalarOSMobile101033();ajustarAcoesOSMobile101033()},{passive:true});
document.addEventListener('click',event=>{if(event.target.closest?.('#novaOSBtn')&&osEhMobile101033())setTimeout(()=>document.querySelector('#osForm101031 input[name="clienteNome"],#osForm101023 input[name="clienteNome"]')?.focus(),80)});
setTimeout(()=>{instalarOSMobile101033();ajustarAcoesOSMobile101033()},0);setTimeout(()=>{instalarOSMobile101033();ajustarAcoesOSMobile101033()},700);
'''
write("public/app.js", js)

css = read("public/style.css") + r'''

/* 10.10.33 - Ordem de Serviço no celular */
.os-mobile-launcher-101033{display:none}
@media(max-width:760px){
 .os-mobile-launcher-101033{position:fixed;right:14px;bottom:calc(14px + env(safe-area-inset-bottom,0px));z-index:9997;display:flex;align-items:center;gap:8px;min-height:48px;padding:8px 14px 8px 8px;border:1px solid var(--border);border-radius:999px;background:var(--card-bg);color:var(--text);box-shadow:0 10px 30px rgba(0,0,0,.22);font:800 12px/1 inherit;cursor:pointer}
 .os-mobile-launcher-101033[hidden]{display:none!important}.os-mobile-launcher-icon-101033{display:grid;place-items:center;width:32px;height:32px;border-radius:50%;background:var(--primary,#b91c1c);color:#fff;font-size:11px;font-weight:950}
 #ordensServico.os-mobile-ready-101033{padding-bottom:90px!important;overflow-x:hidden}
 #ordensServico .os-title-101023{display:grid!important;grid-template-columns:1fr!important;gap:10px!important;align-items:stretch!important}
 #ordensServico .os-mobile-new-101033{width:100%!important;min-height:46px!important;font-size:13px!important}
 #ordensServico .os-stats-101023{display:grid!important;grid-template-columns:repeat(2,minmax(0,1fr))!important;gap:8px!important}
 #ordensServico .os-workspace-101023{padding:10px!important}#ordensServico .os-toolbar-101023{display:grid!important;grid-template-columns:1fr!important;gap:8px!important}
 #ordensServico .os-search-101023,#ordensServico .os-toolbar-101023 select{width:100%!important;min-width:0!important}
 #ordensServico .os-list-101023{display:grid!important;grid-template-columns:1fr!important;gap:10px!important}
 #ordensServico .os-card-101023{min-width:0!important;padding:12px!important;border-radius:14px!important}
 #ordensServico .os-device-101023{display:grid!important;grid-template-columns:1fr!important;gap:8px!important}
 #ordensServico .os-card-101023 footer{display:grid!important;grid-template-columns:1fr 1fr!important;gap:8px!important;align-items:stretch!important}
 #ordensServico .os-card-101023 footer .os-edit-101023{grid-column:1/-1!important;width:100%!important;min-height:44px!important}
 #ordensServico .os-print-actions-101020.os-mobile-no-printer-101033{display:none!important}
 #osForm101031 .form-grid,#osForm101023 .form-grid,#editOSForm101023 .form-grid{display:grid!important;grid-template-columns:1fr!important;gap:10px!important}
 #osForm101031 input,#osForm101031 select,#osForm101031 textarea,#osForm101023 input,#osForm101023 select,#osForm101023 textarea,#editOSForm101023 input,#editOSForm101023 select,#editOSForm101023 textarea{width:100%!important;min-height:44px!important;font-size:16px!important}
 #editOSForm101023 .os-main-actions-101030,#editOSForm101023 .os-danger-actions-101023{display:grid!important;grid-template-columns:1fr!important;gap:8px!important}
 #editOSForm101023 .os-main-actions-101030 button,#editOSForm101023 .os-danger-actions-101023 button{width:100%!important;min-height:46px!important}
}
@media(max-width:380px){#ordensServico .os-stats-101023{grid-template-columns:1fr!important}}
'''
write("public/style.css", css)
print("10.10.33: Ordem de Serviço habilitada e adaptada para uso no celular.")
