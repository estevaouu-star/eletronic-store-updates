from pathlib import Path
import json,re

root=Path("app")
def read(path): return (root/path).read_text(encoding="utf-8")
def write(path,value): (root/path).write_text(value,encoding="utf-8")

pkg=json.loads(read("package.json"));pkg["version"]="10.11.21";write("package.json",json.dumps(pkg,indent=2,ensure_ascii=False))
html=read("public/index.html");html,n=re.subn(r'(id="versionInfo" class="version-info">v)[0-9.]+',r'\g<1>10.11.21',html,count=1)
if n!=1: raise SystemExit("versão HTML não encontrada")
write("public/index.html",html)
js=read("public/app.js");js,n=re.subn(r'const atual="[0-9.]+"(?=,status=)','const atual="10.11.21"',js,count=1)
if n!=1: raise SystemExit("versão atualizador não encontrada")
write("public/app.js",js)

main=read("electron/main.cjs")
anchor='''    // A ELGIN i8 usa exatamente o papel padrão do driver que passou no teste físico.
    const printOptions=elginI8'''
insert=r'''    if(elginI8){
      // A i8 tem área realmente imprimível menor que os 80 mm da bobina.
      // Reorganiza o comprovante dentro de 64 mm, sem alterar o driver que já foi validado.
      await printWindow.webContents.executeJavaScript(`(()=>{
        const receipt=document.querySelector('.receipt');
        if(!receipt)return false;
        const style=document.createElement('style');
        style.id='eletromix-elgin-layout-101121';
        style.textContent="@page{margin:0!important}html,body{margin:0!important;padding:0!important;width:100%!important;overflow:visible!important;background:#fff!important;color:#000!important}.receipt{position:relative!important;left:auto!important;right:auto!important;top:0!important;width:64mm!important;max-width:64mm!important;min-width:0!important;margin:0 auto!important;padding:2mm 1.5mm 3mm!important;box-sizing:border-box!important;transform:none!important;overflow:hidden!important;font-family:Arial,sans-serif!important;font-size:12.5px!important;line-height:1.32!important;color:#000!important}.receipt *{box-sizing:border-box!important;max-width:100%!important;color:#000!important}.receipt img{display:block!important;max-width:42mm!important;max-height:14mm!important;width:auto!important;height:auto!important;object-fit:contain!important;margin:0 auto 2mm!important}.receipt table{width:100%!important;max-width:100%!important;border-collapse:collapse!important;table-layout:fixed!important}.receipt th,.receipt td{min-width:0!important;padding:2px 1px!important;overflow-wrap:anywhere!important;word-break:normal!important;vertical-align:top!important}.receipt th:last-child,.receipt td:last-child{text-align:right!important}.receipt [style*=\"display:flex\"],.receipt [style*=\"display: flex\"]{width:100%!important;max-width:100%!important;min-width:0!important;gap:4px!important}.receipt [style*=\"display:flex\"]>*,.receipt [style*=\"display: flex\"]>*{min-width:0!important}.receipt h1,.receipt h2,.receipt h3{text-align:center!important;margin:3px 0!important;line-height:1.2!important}.receipt p{margin:2px 0!important}";
        document.head.appendChild(style);
        let thanked=false;
        for(const node of receipt.querySelectorAll('p,div,span')){
          const text=(node.textContent||'').trim().toLocaleLowerCase('pt-BR').replace(/\s+/g,' ');
          if(text==='obrigado pela preferência!'||text==='obrigado pela preferencia!'){
            if(thanked)node.remove();else thanked=true;
          }
        }
        document.documentElement.scrollTop=0;document.body.scrollTop=0;
        return true;
      })()`);
      await new Promise(resolve=>setTimeout(resolve,80));
    }

    // A ELGIN i8 usa exatamente o papel padrão do driver que passou no teste físico.
    const printOptions=elginI8'''
if main.count(anchor)!=1: raise SystemExit("ponto de layout ELGIN 10.11.20 não encontrado")
main=main.replace(anchor,insert,1)
main=main.replace('mode:elginI8?"windows-elgin-i8-driver-native":"windows"','mode:elginI8?"windows-elgin-i8-aligned":"windows"',1)
write("electron/main.cjs",main)
print("10.11.21: comprovante ELGIN i8 alinhado em área segura de 64 mm, legível e sem rodapé duplicado.")
