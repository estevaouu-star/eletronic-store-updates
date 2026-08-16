from pathlib import Path
import json,re,base64,struct

root=Path('app')
def read(p): return (root/p).read_text(encoding='utf-8')
def write(p,s): (root/p).write_text(s,encoding='utf-8')
def must(s,a,b,label):
    if a not in s: raise RuntimeError(f'Trecho nao encontrado: {label}')
    return s.replace(a,b,1)

# Nova identidade enviada pelo usuário. A mesma arte é usada no executável/janela;
# as logos do topo e do comprovante continuam personalizáveis separadamente.
ICON_B64='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'
icon_png=base64.b64decode(ICON_B64)
(root/'electron/assets').mkdir(parents=True,exist_ok=True)
(root/'public').mkdir(parents=True,exist_ok=True)
(root/'electron/assets/icon.png').write_bytes(icon_png)
(root/'public/eletromix-app-icon.png').write_bytes(icon_png)
# ICO simples contendo o PNG 128x128.
ico=struct.pack('<HHH',0,1,1)+struct.pack('<BBBBHHII',128,128,0,0,1,32,len(icon_png),22)+icon_png
(root/'electron/assets/icon.ico').write_bytes(ico)

pkg=json.loads(read('package.json'));pkg['version']='10.7.4';write('package.json',json.dumps(pkg,indent=2,ensure_ascii=False))

html=read('public/index.html')
html=html.replace('id="versionInfo" class="version-info">v10.7.3','id="versionInfo" class="version-info">v10.7.4')
html=html.replace('<img src="eletromix-logo.jpg" alt="Eletromix">','<img src="eletromix-app-icon.png" alt="Eletromix">')
old='''        <label>Ícone simples</label><input name="icone" id="appearanceIcon" placeholder="⚡" maxlength="8">
        <label>Imagem / logo</label><input id="appearanceLogoFile" type="file" accept="image/png,image/jpeg,image/webp,image/gif">
        <input type="hidden" name="logoDataUrl" id="appearanceLogoData">
        <p class="muted" style="font-size:12px">A imagem substitui o ícone no topo. Prefira PNG, JPG ou WebP pequeno.</p>'''
new='''        <label>Ícone simples (fallback)</label><input name="icone" id="appearanceIcon" placeholder="⚡" maxlength="8">
        <div class="identity-section-head"><h3>Logos</h3><p>Escolha imagens diferentes para o topo do Eletromix e para o comprovante.</p></div>
        <div class="identity-upload-grid">
          <div class="identity-upload-card">
            <div class="identity-preview" id="appearanceTopLogoPreview"><img src="eletromix-app-icon.png" alt="Logo do sistema"></div>
            <div class="identity-upload-copy"><b>Logo do sistema</b><span>Aparece no topo do aplicativo.</span></div>
            <input id="appearanceTopLogoFile" type="file" accept="image/png,image/jpeg,image/webp,image/gif">
            <input type="hidden" name="logoTopoDataUrl" id="appearanceTopLogoData">
            <button type="button" class="secondary small logo-clear" data-logo-clear="top">Usar logo padrão</button>
          </div>
          <div class="identity-upload-card">
            <div class="identity-preview receipt" id="appearanceReceiptLogoPreview"><span>Sem logo</span></div>
            <div class="identity-upload-copy"><b>Logo do comprovante</b><span>Aparece somente na notinha/comprovante.</span></div>
            <input id="appearanceReceiptLogoFile" type="file" accept="image/png,image/jpeg,image/webp,image/gif">
            <input type="hidden" name="logoComprovanteDataUrl" id="appearanceReceiptLogoData">
            <button type="button" class="secondary small logo-clear" data-logo-clear="receipt">Remover do comprovante</button>
          </div>
        </div>
        <p class="muted identity-hint">PNG, JPG ou WebP. Cada imagem pode ter até aproximadamente 650 KB.</p>'''
html=must(html,old,new,'logos da personalizacao')
old_presets='''        <div class="color-presets">
          <button type="button" class="theme-preset" data-theme="blue">Azul</button>
          <button type="button" class="theme-preset" data-theme="red">Vermelho</button>
          <button type="button" class="theme-preset" data-theme="green">Verde</button>
          <button type="button" class="theme-preset" data-theme="purple">Roxo</button>
          <button type="button" class="theme-preset" data-theme="dark">Escuro</button>
        </div>'''
new_presets='''        <div class="preset-heading"><h3>Predefinições</h3><span>Mais opções em vermelho e preto para combinar com a identidade Eletromix.</span></div>
        <div class="color-presets enhanced">
          <button type="button" class="theme-preset featured" data-theme="eletromix"><b>Eletromix</b><small>Vermelho + preto</small></button>
          <button type="button" class="theme-preset" data-theme="redStrong"><b>Vermelho forte</b><small>Mais vivo</small></button>
          <button type="button" class="theme-preset" data-theme="redBlack"><b>Vermelho / preto</b><small>Contraste alto</small></button>
          <button type="button" class="theme-preset" data-theme="blackRed"><b>Preto / vermelho</b><small>Escuro</small></button>
          <button type="button" class="theme-preset" data-theme="wine"><b>Vinho</b><small>Vermelho fechado</small></button>
          <button type="button" class="theme-preset" data-theme="redSoft"><b>Vermelho claro</b><small>Leve</small></button>
          <button type="button" class="theme-preset" data-theme="red"><b>Vermelho clássico</b><small>Equilibrado</small></button>
          <button type="button" class="theme-preset" data-theme="dark"><b>Preto</b><small>Escuro neutro</small></button>
          <button type="button" class="theme-preset" data-theme="blue"><b>Azul</b><small>Clássico</small></button>
          <button type="button" class="theme-preset" data-theme="green"><b>Verde</b><small>Alternativo</small></button>
          <button type="button" class="theme-preset" data-theme="purple"><b>Roxo</b><small>Alternativo</small></button>
        </div>'''
html=must(html,old_presets,new_presets,'predefinicoes de cores')
write('public/index.html',html)

js=read('public/app.js')
js=js.replace('const atual="10.7.3"','const atual="10.7.4"')
old_apply='''  if($("#systemIcon")){
    if(aparencia.logoDataUrl){
      $("#systemIcon").innerHTML=`<img src="${aparencia.logoDataUrl}" alt="Logo">`;
      $("#systemIcon").classList.add("has-image");
    }else{
      $("#systemIcon").textContent=aparencia.icone||"⚡";
      $("#systemIcon").classList.remove("has-image");
    }
  }'''
new_apply='''  const topLogo=aparencia.logoTopoDataUrl||aparencia.logoDataUrl||"eletromix-app-icon.png";
  if($("#systemIcon")){
    $("#systemIcon").innerHTML=`<img src="${topLogo}" alt="Logo">`;
    $("#systemIcon").classList.add("has-image");
  }'''
js=must(js,old_apply,new_apply,'logo no topo')
js=js.replace('''  if($("#previewLogoWrap")){
    $("#previewLogoWrap").innerHTML=aparencia.logoDataUrl?`<img src="${aparencia.logoDataUrl}" alt="Logo">`:`<span id="previewIcon">${esc(aparencia.icone||"⚡")}</span>`;
  }''','''  if($("#previewLogoWrap"))$("#previewLogoWrap").innerHTML=`<img src="${topLogo}" alt="Logo">`;
  renderLogoCustomPreviews();''')
js=js.replace('''  if($("#appearanceLogoData"))$("#appearanceLogoData").value=aparencia.logoDataUrl||"";
  applyAparencia();''','''  if($("#appearanceTopLogoData"))$("#appearanceTopLogoData").value=aparencia.logoTopoDataUrl||aparencia.logoDataUrl||"";
  if($("#appearanceReceiptLogoData"))$("#appearanceReceiptLogoData").value=aparencia.logoComprovanteDataUrl||aparencia.logoDataUrl||"";
  applyAparencia();''')
js=js.replace('''  body.logoDataUrl=$("#appearanceLogoData")?.value||"";''','''  body.logoTopoDataUrl=$("#appearanceTopLogoData")?.value||"";
  body.logoComprovanteDataUrl=$("#appearanceReceiptLogoData")?.value||"";
  body.logoDataUrl=body.logoTopoDataUrl;''')
pat=r'async function handleLogoFile\(file\)\{.*?\n\}'
new_handler=r'''function renderLogoCustomPreviews(){
  const top=aparencia.logoTopoDataUrl||aparencia.logoDataUrl||"eletromix-app-icon.png";
  const receipt=aparencia.logoComprovanteDataUrl||aparencia.logoDataUrl||"";
  const a=$("#appearanceTopLogoPreview"),b=$("#appearanceReceiptLogoPreview");
  if(a)a.innerHTML=`<img src="${top}" alt="Logo do sistema">`;
  if(b)b.innerHTML=receipt?`<img src="${receipt}" alt="Logo do comprovante">`:`<span>Sem logo</span>`;
}
async function handleLogoFile(file,key,hiddenId){
  if(!file)return;
  if(file.size>650000)return toast("Use uma imagem menor que aproximadamente 650 KB.");
  if(!/^image\/(png|jpeg|webp|gif)$/i.test(file.type||""))return toast("Formato de imagem não suportado.");
  const reader=new FileReader();
  reader.onload=()=>{aparencia[key]=String(reader.result||"");if($("#"+hiddenId))$("#"+hiddenId).value=aparencia[key];applyAparencia();};
  reader.readAsDataURL(file);
}'''
js,n=re.subn(pat,new_handler,js,count=1,flags=re.S)
if n!=1: raise RuntimeError('handleLogoFile nao encontrado')
# Temas: foco em vermelho/preto, mantendo os anteriores.
pat=r'const themes=\{.*?\n\};\nfunction applyTheme'
new_themes=r'''const themes={
  eletromix:{corPrincipal:"#e10600",corTopo:"#190606",corMenu:"#120d0d",corFundo:"#f8f3f3",corCartao:"#ffffff",corTexto:"#211717",corTextoSecundario:"#7b6767",corBorda:"#ead3d3",corPerigo:"#b60000"},
  redStrong:{corPrincipal:"#f01414",corTopo:"#260505",corMenu:"#fff8f8",corFundo:"#fff1f1",corCartao:"#ffffff",corTexto:"#251313",corTextoSecundario:"#825d5d",corBorda:"#f0caca",corPerigo:"#c40000"},
  redBlack:{corPrincipal:"#df1010",corTopo:"#0b0b0d",corMenu:"#171719",corFundo:"#f5f2f2",corCartao:"#ffffff",corTexto:"#1d1919",corTextoSecundario:"#746969",corBorda:"#dfd6d6",corPerigo:"#b80000"},
  blackRed:{corPrincipal:"#ef2323",corTopo:"#08090b",corMenu:"#111216",corFundo:"#0d0e11",corCartao:"#17181d",corTexto:"#f5f5f6",corTextoSecundario:"#b6b0b0",corBorda:"#33343a",corPerigo:"#ff4545"},
  wine:{corPrincipal:"#9f1239",corTopo:"#24070f",corMenu:"#fff8fa",corFundo:"#f9f1f3",corCartao:"#ffffff",corTexto:"#2b151c",corTextoSecundario:"#80616a",corBorda:"#ead3da",corPerigo:"#9f1239"},
  redSoft:{corPrincipal:"#d93636",corTopo:"#321717",corMenu:"#fffafa",corFundo:"#fbf5f5",corCartao:"#ffffff",corTexto:"#2b2020",corTextoSecundario:"#806e6e",corBorda:"#eadede",corPerigo:"#b42323"},
  red:{corPrincipal:"#c62828",corTopo:"#2a1010",corMenu:"#fffafa",corFundo:"#f8f2f2",corCartao:"#ffffff",corTexto:"#261818",corTextoSecundario:"#7b6464",corBorda:"#ead7d7",corPerigo:"#9d1010"},
  dark:{corPrincipal:"#e02727",corTopo:"#08090b",corMenu:"#17181d",corFundo:"#101114",corCartao:"#1c1d22",corTexto:"#f0f1f3",corTextoSecundario:"#aeb1b8",corBorda:"#34363d",corPerigo:"#ef5350"},
  blue:{corPrincipal:"#1769e0",corTopo:"#101820",corMenu:"#ffffff",corFundo:"#f4f6f8",corCartao:"#ffffff",corTexto:"#17202a",corTextoSecundario:"#6b7680",corBorda:"#e1e6ea",corPerigo:"#c62828"},
  green:{corPrincipal:"#198754",corTopo:"#10291f",corMenu:"#f9fffb",corFundo:"#f1f7f4",corCartao:"#ffffff",corTexto:"#173126",corTextoSecundario:"#63786d",corBorda:"#d7e6dd",corPerigo:"#c62828"},
  purple:{corPrincipal:"#7b2cbf",corTopo:"#24102f",corMenu:"#fcf9ff",corFundo:"#f6f1fa",corCartao:"#ffffff",corTexto:"#2b1b34",corTextoSecundario:"#75677d",corBorda:"#e4d8ec",corPerigo:"#c62828"}
};
function applyTheme'''
js,n=re.subn(pat,new_themes,js,count=1,flags=re.S)
if n!=1: raise RuntimeError('themes nao encontrado')
# Comprovante usa logo própria.
js=js.replace('${aparencia.logoDataUrl?`<div class="receipt-logo"><img src="${aparencia.logoDataUrl}" alt="Logo"></div>`:""}', '${(aparencia.logoComprovanteDataUrl||aparencia.logoDataUrl)?`<div class="receipt-logo"><img src="${aparencia.logoComprovanteDataUrl||aparencia.logoDataUrl}" alt="Logo"></div>`:""}')
# Listeners dos dois uploads.
js=js.replace('''  const logo=$("#appearanceLogoFile");
  if(logo)logo.addEventListener("change",e=>handleLogoFile(e.target.files?.[0]));''','''  const logoTop=$("#appearanceTopLogoFile"),logoReceipt=$("#appearanceReceiptLogoFile");
  if(logoTop)logoTop.addEventListener("change",e=>handleLogoFile(e.target.files?.[0],"logoTopoDataUrl","appearanceTopLogoData"));
  if(logoReceipt)logoReceipt.addEventListener("change",e=>handleLogoFile(e.target.files?.[0],"logoComprovanteDataUrl","appearanceReceiptLogoData"));''')
# Ícone simples não apaga mais as imagens escolhidas.
js=re.sub(r'if\(icon\)icon\.addEventListener\("input",e=>\{aparencia\.icone=e\.target\.value\|\|"⚡";aparencia\.logoDataUrl="";const h=\$\("#appearanceLogoData"\);if\(h\)h\.value="";applyAparencia\(\)\}\);', 'if(icon)icon.addEventListener("input",e=>{aparencia.icone=e.target.value||"⚡";applyAparencia()});', js)
# Limpar logos separadamente.
js += r'''
document.addEventListener("click",e=>{
  const b=e.target?.closest?.(".logo-clear");if(!b)return;
  e.preventDefault();
  if(b.dataset.logoClear==="top"){aparencia.logoTopoDataUrl="";const h=$("#appearanceTopLogoData");if(h)h.value="";toast("Logo do sistema voltou para o padrão Eletromix.");}
  if(b.dataset.logoClear==="receipt"){aparencia.logoComprovanteDataUrl="";aparencia.logoDataUrl="";const h=$("#appearanceReceiptLogoData");if(h)h.value="";toast("Logo removida do comprovante.");}
  applyAparencia();
});
'''
write('public/app.js',js)

server=read('src/server.ts')
# Campos opcionais novos no tipo Aparencia.
mt=re.search(r'type Aparencia\s*=\s*\{(.*?)\n\};',server,re.S)
if not mt: raise RuntimeError('type Aparencia nao encontrado')
block=mt.group(0)
if 'logoTopoDataUrl' not in block:
    block2=block.replace('logoDataUrl:string;','logoDataUrl:string; logoTopoDataUrl?:string; logoComprovanteDataUrl?:string;')
    if block2==block: block2=block[:-3]+'\n  logoTopoDataUrl?:string; logoComprovanteDataUrl?:string;\n};'
    server=server.replace(block,block2,1)
server=server.replace('''    logoDataUrl:"",
    nomeSistema:''','''    logoDataUrl:"",
    logoTopoDataUrl:"",
    logoComprovanteDataUrl:"",
    nomeSistema:''',1)
server=server.replace('app.get("/api/aparencia",auth,(_req,res)=>res.json(db.aparencia));','''app.get("/api/aparencia",auth,(_req,res)=>{
  const a=db.aparencia as any;
  a.logoTopoDataUrl ??= a.logoDataUrl||"";
  a.logoComprovanteDataUrl ??= a.logoDataUrl||"";
  res.json(a);
});''')
pat=r'app\.put\("/api/aparencia",auth,admin,\(req,res\)=>\{.*?\n\}\);'
new_endpoint=r'''app.put("/api/aparencia",auth,admin,(req,res)=>{
  const colorKeys=["corPrincipal","corTopo","corMenu","corFundo","corCartao","corTexto","corTextoSecundario","corBorda","corPerigo"] as const;
  for(const key of colorKeys){
    const value=String(req.body[key]||db.aparencia[key]);
    if(!/^#[0-9a-fA-F]{6}$/.test(value))return res.status(400).json({erro:`Cor inválida em ${key}.`});
    db.aparencia[key]=value;
  }
  db.aparencia.icone=String(req.body.icone||"⚡").slice(0,8);
  db.aparencia.nomeSistema=String(req.body.nomeSistema||"Eletromix").slice(0,60);
  const validarLogo=(valor:any)=>{
    const logo=String(valor||"");
    if(logo && !/^data:image\/(png|jpeg|jpg|webp|gif);base64,/i.test(logo))throw new Error("Formato de imagem inválido.");
    if(logo.length>900000)throw new Error("A imagem é muito grande. Use uma imagem menor.");
    return logo;
  };
  try{
    const antigo=validarLogo(req.body.logoDataUrl||"");
    const topo=validarLogo(req.body.logoTopoDataUrl ?? antigo);
    const comprovante=validarLogo(req.body.logoComprovanteDataUrl ?? antigo);
    db.aparencia.logoDataUrl=topo;
    (db.aparencia as any).logoTopoDataUrl=topo;
    (db.aparencia as any).logoComprovanteDataUrl=comprovante;
  }catch(e:any){return res.status(400).json({erro:e.message||"Imagem inválida."});}
  salvar();res.json(db.aparencia);
});'''
server,n=re.subn(pat,new_endpoint,server,count=1,flags=re.S)
if n!=1: raise RuntimeError('endpoint /api/aparencia PUT nao encontrado')
write('src/server.ts',server)

css=read('public/style.css')
css += r'''
/* Eletromix 10.7.4 - identidade, logos separadas e foco vermelho/preto */
.identity-section-head{margin:18px 0 10px}.identity-section-head h3{margin:0 0 3px!important}.identity-section-head p{margin:0;color:var(--text-muted);font-size:12px}.identity-upload-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px}.identity-upload-card{display:grid;grid-template-columns:62px 1fr;gap:10px 12px;align-items:center;border:1px solid var(--border);border-radius:14px;padding:12px;background:color-mix(in srgb,var(--card-bg) 96%,var(--page-bg))}.identity-preview{width:62px;height:62px;border-radius:14px;display:grid;place-items:center;overflow:hidden;background:#0b0b0c;border:1px solid color-mix(in srgb,var(--border) 70%,#000)}.identity-preview.receipt{background:var(--card-bg)}.identity-preview img{width:100%;height:100%;object-fit:contain}.identity-preview span{font-size:10px;color:var(--text-muted);text-align:center}.identity-upload-copy{display:grid;gap:3px}.identity-upload-copy b{font-size:13px}.identity-upload-copy span{font-size:11px;color:var(--text-muted)}.identity-upload-card input[type="file"]{grid-column:1/-1;margin:0!important;font-size:11px;padding:8px!important}.identity-upload-card .logo-clear{grid-column:1/-1;width:100%}.identity-hint{font-size:11px!important;margin:8px 2px 2px!important}.preset-heading{margin:18px 0 9px}.preset-heading h3{margin:0 0 3px!important}.preset-heading span{font-size:11px;color:var(--text-muted)}.color-presets.enhanced{display:grid!important;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px!important}.color-presets.enhanced .theme-preset{position:relative;display:grid;gap:2px;text-align:left;padding:10px 10px 10px 42px!important;min-height:52px;overflow:hidden}.color-presets.enhanced .theme-preset:before{content:"";position:absolute;left:9px;top:10px;width:23px;height:32px;border-radius:8px;border:1px solid #ffffff42;box-shadow:0 2px 8px #0002}.theme-preset b{font-size:12px}.theme-preset small{font-size:10px;color:var(--text-muted)}.theme-preset.featured{border-color:color-mix(in srgb,#e10600 55%,var(--border))!important;box-shadow:0 0 0 2px color-mix(in srgb,#e10600 8%,transparent)}.theme-preset[data-theme="eletromix"]:before{background:linear-gradient(145deg,#e10600 0 48%,#111 49% 100%)}.theme-preset[data-theme="redStrong"]:before{background:linear-gradient(145deg,#f01414,#7d0000)}.theme-preset[data-theme="redBlack"]:before{background:linear-gradient(145deg,#df1010 0 52%,#111 53%)}.theme-preset[data-theme="blackRed"]:before{background:linear-gradient(145deg,#090909 0 58%,#ef2323 59%)}.theme-preset[data-theme="wine"]:before{background:linear-gradient(145deg,#9f1239,#350713)}.theme-preset[data-theme="redSoft"]:before{background:linear-gradient(145deg,#d93636,#fff0f0)}.theme-preset[data-theme="red"]:before{background:#c62828}.theme-preset[data-theme="dark"]:before{background:linear-gradient(145deg,#111,#e02727)}.theme-preset[data-theme="blue"]:before{background:#1769e0}.theme-preset[data-theme="green"]:before{background:#198754}.theme-preset[data-theme="purple"]:before{background:#7b2cbf}@media(max-width:760px){.identity-upload-grid,.color-presets.enhanced{grid-template-columns:1fr}}
'''
write('public/style.css',css)
print('Patch 10.7.4 aplicado: novo ícone Eletromix, logos separadas e presets vermelho/preto.')
