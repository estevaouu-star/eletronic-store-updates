from pathlib import Path
import json,re

root=Path('app')
def read(p): return (root/p).read_text(encoding='utf-8')
def write(p,s): (root/p).write_text(s,encoding='utf-8')

pkg=json.loads(read('package.json'))
pkg['version']='10.7.1'
write('package.json',json.dumps(pkg,indent=2,ensure_ascii=False))

html=read('public/index.html')
html=html.replace('<div class="system-brand"><span id="systemIcon" class="system-icon app-brand-icon brand-logo"><img src="eletromix-logo.jpg" alt="Eletromix"></span><div><h1 id="storeName">Eletromix</h1><span>Gestão inteligente para sua loja</span></div></div>',
'''<div class="system-brand"><span id="systemIcon" class="system-icon app-brand-icon brand-logo"><img src="eletromix-logo.jpg" alt="Eletromix"></span><div class="brand-copy"><h1 id="storeName">Eletromix</h1></div></div>''')
old='<div class="header-actions"><button id="updateButton" class="update-pill" type="button"><span class="update-dot"></span><span id="updateText">Atualizado</span></button>'
new='''<div class="header-actions"><div class="version-cluster"><span id="versionInfo" class="version-info">v10.7.1</span><button id="updateButton" class="update-pill" type="button"><span class="update-dot"></span><span id="updateText">Atualizado</span></button></div>'''
if old not in html: raise RuntimeError('Bloco do atualizador não encontrado')
html=html.replace(old,new,1)
write('public/index.html',html)

js=read('public/app.js')
js=re.sub(r'\$\("#storeName"\)\.textContent=[^;]+;', '$("#storeName").textContent="Eletromix";', js)
pat=r'function renderUpdateState\(s\)\{const b=\$\("#updateButton"\),t=\$\("#updateText"\);if\(!b\|\|!t\)return;b\.dataset\.state=s\?\.status\|\|"idle";t\.textContent=.*?;\}'
repl='''function renderUpdateState(s){
  const b=$("#updateButton"),t=$("#updateText"),v=$("#versionInfo");if(!b||!t)return;
  const atual="10.7.1",status=s?.status||"idle",disponivel=String(s?.version||"").replace(/^v/i,"");
  b.dataset.state=status;
  t.textContent=status==="available"?"Atualizar":status==="downloading"?`Baixando ${s.percent||0}%`:status==="downloaded"?"Instalar agora":status==="checking"?"Verificando...":status==="error"?"Tentar novamente":"Atualizado";
  if(v){
    v.dataset.state=status;
    v.innerHTML=status==="available"&&disponivel?`<span class="version-current">v${atual}</span><span class="version-arrow">→</span><strong>v${disponivel}</strong>`:`<span class="version-current">v${atual}</span>`;
    v.title=status==="available"&&disponivel?`Versão instalada: ${atual} · Nova versão: ${disponivel}`:`Versão instalada: ${atual}`;
  }
}'''
js,n=re.subn(pat,repl,js,count=1,flags=re.S)
if n!=1: raise RuntimeError('renderUpdateState não encontrado')
write('public/app.js',js)

css=read('public/style.css')
css += r'''
/* Eletromix 10.7.1 — refinamento visual mais marcante */
:root{--ui-radius:16px;--ui-radius-sm:11px;--ui-shadow:0 10px 30px rgba(16,24,32,.075);--ui-shadow-hover:0 16px 38px rgba(16,24,32,.11)}
body{background:radial-gradient(circle at 84% -10%,color-mix(in srgb,var(--accent) 10%,transparent),transparent 32%),radial-gradient(circle at 18% 8%,color-mix(in srgb,var(--accent) 5%,transparent),transparent 28%),var(--page-bg)!important}
header{height:68px!important;padding:0 24px!important;background:color-mix(in srgb,var(--topbar) 94%,#fff 6%)!important;border-bottom:1px solid #ffffff14;box-shadow:0 8px 30px rgba(5,12,18,.15)!important;backdrop-filter:blur(14px)}
.system-brand{gap:12px!important}.system-icon{width:40px!important;height:40px!important;border-radius:12px!important;box-shadow:0 7px 18px #0004}.brand-copy{display:flex;align-items:center}.system-brand h1{font-size:22px!important;font-weight:850;letter-spacing:-.035em!important;line-height:1}
.header-actions{gap:10px!important}.version-cluster{display:flex;align-items:center;gap:7px;padding:4px 5px 4px 9px;border:1px solid #ffffff12;background:#ffffff09;border-radius:13px}.version-info{display:flex;align-items:center;gap:5px;color:#d5dde4!important;font-size:10.5px!important;font-weight:750;letter-spacing:.01em;white-space:nowrap}.version-info strong{color:#fff;font-size:11px}.version-arrow{opacity:.5}.update-pill{border:1px solid #ffffff16!important;background:#ffffff0d!important;border-radius:9px!important;padding:7px 9px!important}.update-pill:hover{background:#ffffff18!important}.update-pill[data-state="available"]{background:color-mix(in srgb,#f2b84b 18%,transparent)!important;border-color:#f2b84b55!important}.update-pill[data-state="downloaded"]{background:color-mix(in srgb,#50c878 18%,transparent)!important;border-color:#50c87855!important}
.layout{min-height:calc(100vh - 68px)!important;gap:0}aside{width:224px!important;top:68px!important;height:calc(100vh - 68px)!important;padding:16px 10px 20px!important;background:color-mix(in srgb,var(--sidebar) 97%,var(--page-bg) 3%)!important;border-right:1px solid color-mix(in srgb,var(--border) 82%,transparent)!important;box-shadow:8px 0 28px rgba(18,30,40,.035)}
.nav{min-height:42px!important;padding:10px 12px!important;margin:2px 4px!important;border-radius:11px!important;font-size:13.5px!important;transition:background .16s ease,border-color .16s ease,transform .16s ease!important}.nav:hover{transform:translateX(2px)!important;background:color-mix(in srgb,var(--accent) 7%,transparent)!important}.nav.active{background:linear-gradient(90deg,color-mix(in srgb,var(--accent) 14%,var(--sidebar)),color-mix(in srgb,var(--accent) 7%,var(--sidebar)))!important;border-color:color-mix(in srgb,var(--accent) 22%,var(--border))!important;box-shadow:inset 3px 0 0 var(--accent),0 5px 14px color-mix(in srgb,var(--accent) 8%,transparent)!important}
main{max-width:1420px!important;margin:24px auto!important;padding:0 24px 34px!important}.section{animation:sectionIn .18s ease}.section.active{display:block}@keyframes sectionIn{from{opacity:.4;transform:translateY(3px)}to{opacity:1;transform:none}}
.title{margin-bottom:17px!important;padding:0 2px}.title h2{font-size:25px;letter-spacing:-.035em;font-weight:830;color:var(--text-main)}.title p{font-size:13px;margin-top:4px!important}.title:before{content:"";width:4px;height:30px;border-radius:99px;background:linear-gradient(180deg,var(--accent),color-mix(in srgb,var(--accent) 45%,transparent));align-self:center;margin-right:-3px}
.card,.settings-block{border-radius:var(--ui-radius)!important;border:1px solid color-mix(in srgb,var(--border) 78%,transparent)!important;box-shadow:var(--ui-shadow)!important;background:color-mix(in srgb,var(--card-bg) 98%,var(--page-bg) 2%)!important}.card{padding:20px!important;margin-bottom:16px!important}.card h3{letter-spacing:-.018em;font-weight:800}.card:hover{border-color:color-mix(in srgb,var(--border) 60%,var(--accent) 10%)!important}
.stat{position:relative;overflow:hidden}.stat:after{content:"";position:absolute;width:80px;height:80px;border-radius:50%;right:-28px;top:-32px;background:color-mix(in srgb,var(--accent) 8%,transparent)}.stat b{font-weight:850;letter-spacing:-.035em}
input,select,textarea{border-radius:var(--ui-radius-sm)!important;border:1px solid color-mix(in srgb,var(--border) 88%,transparent)!important;transition:border-color .15s ease,box-shadow .15s ease,background .15s ease!important}input:hover,select:hover,textarea:hover{border-color:color-mix(in srgb,var(--border) 55%,var(--accent) 25%)!important}input:focus,select:focus,textarea:focus{outline:none!important;border-color:color-mix(in srgb,var(--accent) 68%,var(--border))!important;box-shadow:0 0 0 3px color-mix(in srgb,var(--accent) 12%,transparent)!important}
.primary,.secondary,.danger{border-radius:10px!important;min-height:39px;box-shadow:none;transition:transform .14s ease,box-shadow .14s ease,filter .14s ease!important}.primary:hover,.secondary:hover,.danger:hover{transform:translateY(-1px)!important;filter:brightness(.99)}.primary:hover{box-shadow:0 7px 18px color-mix(in srgb,var(--accent) 23%,transparent)!important}.primary:active,.secondary:active{transform:translateY(0)!important}
.product{border-radius:12px!important;border-color:color-mix(in srgb,var(--border) 82%,transparent)!important;transition:transform .13s ease,border-color .13s ease,box-shadow .13s ease!important}.product:hover{transform:translateY(-1px);border-color:color-mix(in srgb,var(--accent) 30%,var(--border))!important;box-shadow:0 7px 18px rgba(20,30,40,.06)}
table{border-collapse:separate!important;border-spacing:0}thead th{background:color-mix(in srgb,var(--page-bg) 70%,var(--card-bg));border-bottom:1px solid var(--border)!important;font-size:10.5px!important;letter-spacing:.055em}thead th:first-child{border-radius:10px 0 0 10px}thead th:last-child{border-radius:0 10px 10px 0}tbody tr{transition:background .12s ease}tbody tr:hover{background:color-mix(in srgb,var(--accent) 4%,transparent)}td{border-bottom-color:color-mix(in srgb,var(--border) 72%,transparent)!important}
.modal{backdrop-filter:blur(5px)}.modal-card{border-radius:20px!important;box-shadow:0 28px 90px rgba(0,0,0,.3)!important}.modal-head{padding-bottom:10px;border-bottom:1px solid color-mix(in srgb,var(--border) 70%,transparent)}
.settings-block{padding:22px!important}.nfce-settings-block{position:relative;overflow:hidden}.nfce-settings-block:before{content:"";position:absolute;inset:0 0 auto;height:3px;background:linear-gradient(90deg,var(--accent),color-mix(in srgb,var(--accent) 25%,transparent));opacity:.8}.nfce-info-card{border-radius:13px!important}.nfce-ready-card{border-radius:13px!important}#toast{border-radius:12px!important;box-shadow:0 14px 34px #0003!important}
::-webkit-scrollbar{width:10px;height:10px}::-webkit-scrollbar-thumb{background:color-mix(in srgb,var(--text-muted) 28%,transparent);border:3px solid transparent;background-clip:padding-box;border-radius:99px}::-webkit-scrollbar-track{background:transparent}
@media(max-width:1100px){aside{width:174px!important}.nav{font-size:12.5px!important;padding:9px!important}main{padding:0 14px 26px!important}.title h2{font-size:22px}.card{padding:15px!important}}
@media(max-width:760px){header{height:auto!important;min-height:58px!important;padding:8px 12px!important;gap:8px}.system-brand h1{font-size:18px!important}.version-info{display:none}.version-cluster{padding:3px}.layout{min-height:0!important}aside{position:static!important;width:100%!important;height:auto!important;display:flex!important;padding:9px!important;box-shadow:none}.nav{width:auto!important;min-width:max-content!important;margin:0 2px!important}.title:before{display:none}main{margin:14px auto!important;padding:0 12px 24px!important}.card{border-radius:14px!important}}
'''
write('public/style.css',css)
print('Patch 10.7.1 aplicado: visual refinado, nome Eletromix fixo e versão do atualizador visível.')
