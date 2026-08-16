from pathlib import Path
import json

root=Path('app')
def read(p): return (root/p).read_text(encoding='utf-8')
def write(p,s): (root/p).write_text(s,encoding='utf-8')
def must(s,a,b,label):
    if a not in s: raise RuntimeError(f'Trecho nao encontrado: {label}')
    return s.replace(a,b,1)

# Versão
pkg=json.loads(read('package.json'))
pkg['version']='10.7.5'
# Garante que o electron-builder use o PNG novo do aplicativo.
pkg.setdefault('build',{}).setdefault('win',{})['icon']='electron/assets/icon.png'
write('package.json',json.dumps(pkg,indent=2,ensure_ascii=False))

# Personalização: texto de ajuda e versão visível.
html=read('public/index.html')
html=html.replace('id="versionInfo" class="version-info">v10.7.4','id="versionInfo" class="version-info">v10.7.5')
html=html.replace('PNG, JPG ou WebP. Cada imagem pode ter até aproximadamente 650 KB.','PNG, JPG, WebP ou GIF. Você pode escolher imagens de até 8 MB; o Eletromix otimiza automaticamente antes de salvar.')
write('public/index.html',html)

# Frontend: permite imagens maiores e otimiza automaticamente.
js=read('public/app.js')
js=js.replace('const atual="10.7.4"','const atual="10.7.5"')
old='''async function handleLogoFile(file,key,hiddenId){
  if(!file)return;
  if(file.size>650000)return toast("Use uma imagem menor que aproximadamente 650 KB.");
  if(!/^image\\/(png|jpeg|webp|gif)$/i.test(file.type||""))return toast("Formato de imagem não suportado.");
  const reader=new FileReader();
  reader.onload=()=>{aparencia[key]=String(reader.result||"");if($("#"+hiddenId))$("#"+hiddenId).value=aparencia[key];applyAparencia();};
  reader.readAsDataURL(file);
}'''
new='''function lerImagemComoDataUrl(file){
  return new Promise((resolve,reject)=>{const r=new FileReader();r.onload=()=>resolve(String(r.result||""));r.onerror=()=>reject(new Error("Não foi possível ler a imagem."));r.readAsDataURL(file)});
}
function carregarImagemDataUrl(src){
  return new Promise((resolve,reject)=>{const img=new Image();img.onload=()=>resolve(img);img.onerror=()=>reject(new Error("Imagem inválida ou corrompida."));img.src=src});
}
async function otimizarLogo(file){
  if(file.size>8*1024*1024)throw new Error("Use uma imagem de até 8 MB.");
  const original=await lerImagemComoDataUrl(file);
  const img=await carregarImagemDataUrl(original);
  const max=1400;
  const escala=Math.min(1,max/Math.max(img.naturalWidth||img.width,img.naturalHeight||img.height));
  const w=Math.max(1,Math.round((img.naturalWidth||img.width)*escala));
  const h=Math.max(1,Math.round((img.naturalHeight||img.height)*escala));
  const canvas=document.createElement("canvas");canvas.width=w;canvas.height=h;
  const ctx=canvas.getContext("2d");if(!ctx)throw new Error("Não foi possível processar a imagem.");
  ctx.clearRect(0,0,w,h);ctx.drawImage(img,0,0,w,h);
  let data=canvas.toDataURL("image/webp",0.92);
  if(data.length>2400000)data=canvas.toDataURL("image/webp",0.80);
  if(data.length>3200000)throw new Error("A imagem continua muito grande depois da otimização. Escolha outra imagem.");
  return data;
}
async function handleLogoFile(file,key,hiddenId){
  if(!file)return;
  if(!/^image\\/(png|jpeg|webp|gif)$/i.test(file.type||""))return toast("Formato de imagem não suportado.");
  try{
    toast("Preparando imagem...");
    const data=await otimizarLogo(file);
    aparencia[key]=data;
    const hidden=$("#"+hiddenId);if(hidden)hidden.value=data;
    applyAparencia();
    toast("Imagem carregada. Clique em Salvar personalização.");
  }catch(e){console.error(e);toast(e?.message||"Não foi possível usar essa imagem.");}
}'''
js=must(js,old,new,'upload de logos')
write('public/app.js',js)

# Backend: a aparência da 10.7.4 ainda era global. Agora fica realmente separada por loja.
server=read('src/server.ts')
old_server='''// Aparência global do sistema
app.get("/api/aparencia",auth,(_req,res)=>{
  const a=db.aparencia as any;
  a.logoTopoDataUrl ??= a.logoDataUrl||"";
  a.logoComprovanteDataUrl ??= a.logoDataUrl||"";
  res.json(a);
});
app.put("/api/aparencia",auth,admin,(req,res)=>{
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
    if(logo && !/^data:image\\/(png|jpeg|jpg|webp|gif);base64,/i.test(logo))throw new Error("Formato de imagem inválido.");
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
new_server='''// Aparência por loja. Cada unidade mantém cores e logos próprias.
function aparenciaDaLoja(req:any):Aparencia{
  const loja=lojaReq(req);
  const banco:any=db as any;
  banco.aparenciaPorLoja ??= {};
  const chave=String(loja.id);
  if(!banco.aparenciaPorLoja[chave])banco.aparenciaPorLoja[chave]=structuredClone(db.aparencia||inicial.aparencia);
  const a=banco.aparenciaPorLoja[chave] as Aparencia;
  a.logoDataUrl ??= "";
  a.logoTopoDataUrl ??= a.logoDataUrl||"";
  a.logoComprovanteDataUrl ??= a.logoDataUrl||"";
  a.nomeSistema ||= "Eletromix";
  return a;
}
app.get("/api/aparencia",auth,(req,res)=>{
  res.json(aparenciaDaLoja(req));
});
app.put("/api/aparencia",auth,admin,(req,res)=>{
  const a=aparenciaDaLoja(req);
  const colorKeys=["corPrincipal","corTopo","corMenu","corFundo","corCartao","corTexto","corTextoSecundario","corBorda","corPerigo"] as const;
  for(const key of colorKeys){
    const value=String(req.body[key]||a[key]);
    if(!/^#[0-9a-fA-F]{6}$/.test(value))return res.status(400).json({erro:`Cor inválida em ${key}.`});
    a[key]=value;
  }
  a.icone=String(req.body.icone||"⚡").slice(0,8);
  a.nomeSistema=String(req.body.nomeSistema||"Eletromix").slice(0,60);
  const validarLogo=(valor:any)=>{
    const logo=String(valor||"");
    if(logo && !/^data:image\\/(png|jpeg|jpg|webp|gif);base64,/i.test(logo))throw new Error("Formato de imagem inválido.");
    if(logo.length>3500000)throw new Error("A imagem é muito grande mesmo após a otimização.");
    return logo;
  };
  try{
    const antigo=validarLogo(req.body.logoDataUrl||"");
    const topo=validarLogo(req.body.logoTopoDataUrl ?? antigo);
    const comprovante=validarLogo(req.body.logoComprovanteDataUrl ?? antigo);
    a.logoDataUrl=topo;
    a.logoTopoDataUrl=topo;
    a.logoComprovanteDataUrl=comprovante;
  }catch(e:any){return res.status(400).json({erro:e.message||"Imagem inválida."});}
  salvar();res.json(a);
});'''
server=must(server,old_server,new_server,'aparencia global -> por loja')
write('src/server.ts',server)

# Correções visuais vistas no print: título empurrado para a direita, logos pequenas/cortadas.
css=read('public/style.css')
css += r'''
/* Eletromix 10.7.5 - correções da tela Personalização */
.section>.title{justify-content:flex-start!important;gap:12px!important;align-items:center!important}
.section>.title>div{min-width:0}
.section>.title>button,.section>.title>.title-actions{margin-left:auto!important}
.section>.title:before{margin-right:0!important;flex:0 0 4px!important}
.system-icon img,.brand-logo img,.preview-logo-wrap img{object-fit:contain!important;display:block!important;transform:scale(1.08)}
.system-icon,.brand-logo{background:#050505!important}
.identity-upload-card{grid-template-columns:74px minmax(0,1fr)!important}
.identity-preview{width:74px!important;height:74px!important;border-radius:15px!important}
.identity-preview img{width:100%!important;height:100%!important;object-fit:contain!important}
.appearance-preview{align-items:center!important}
.preview-logo-wrap{width:64px!important;height:64px!important;background:#050505!important}
.identity-hint{line-height:1.45}
@media(max-width:760px){.identity-upload-card{grid-template-columns:64px minmax(0,1fr)!important}.identity-preview{width:64px!important;height:64px!important}}
'''
write('public/style.css',css)

print('Patch 10.7.5 aplicado: upload de logos otimizado, título corrigido, logos maiores e aparência realmente separada por loja.')
