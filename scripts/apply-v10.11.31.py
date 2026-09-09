from pathlib import Path
import json,re

root=Path("app")
def read(p): return (root/p).read_text(encoding="utf-8")
def write(p,s): (root/p).write_text(s,encoding="utf-8")
def must(s,a,b,label):
    if a not in s: raise SystemExit("trecho ausente: "+label)
    return s.replace(a,b,1)

pkg=json.loads(read("package.json"))
if pkg.get("version")!="10.11.30": raise SystemExit("base precisa ser 10.11.30")
pkg["version"]="10.11.31"
write("package.json",json.dumps(pkg,indent=2,ensure_ascii=False))

html=read("public/index.html")
html,n=re.subn(r'(id="versionInfo" class="version-info">v)10\.11\.30',r'\g<1>10.11.31',html,count=1)
if n!=1: raise SystemExit("versao HTML ausente")
write("public/index.html",html)

js=read("public/app.js")
js=must(js,'const atual="10.11.30"','const atual="10.11.31"',"versao JS")
write("public/app.js",js)

main=read("electron/main.cjs")
old='''    const selected=available.find(p=>p.name===deviceName);
    const elginI8=/elgin.*i8|i8.*elgin/i.test(`${selected?.name||deviceName} ${selected?.displayName||""} ${selected?.description||""}`);
    // A ELGIN i8 usa exatamente o papel padrão do driver que passou no teste físico.
    const printOptions=elginI8'''
new='''    const selected=available.find(p=>p.name===deviceName);
    const elginI8=/elgin.*i8|i8.*elgin/i.test(`${selected?.name||deviceName} ${selected?.displayName||""} ${selected?.description||""}`);
    // Epson e demais térmicas: fixa o documento no topo e limita a página à altura real.
    // Isso restaura a correção comprovada da 10.7.8 e elimina o avanço de papel em branco.
    if(!elginI8){
      const innerMm=width===58?52:72;
      const leftMm=Math.max(0,(width-innerMm)/2);
      await printWindow.webContents.executeJavaScript(`(()=>{
        document.getElementById('eletromix-exact-print-page')?.remove();
        const st=document.createElement('style');
        st.id='eletromix-exact-print-page';
        st.textContent='@page{size:${width}mm ${heightMm}mm!important;margin:0!important}' +
          'html,body{position:relative!important;width:${width}mm!important;height:${heightMm}mm!important;min-height:0!important;max-height:${heightMm}mm!important;margin:0!important;padding:0!important;overflow:hidden!important}' +
          '.receipt{position:absolute!important;top:0!important;left:${leftMm}mm!important;margin:0!important;width:${innerMm}mm!important;max-width:${innerMm}mm!important;transform:none!important}';
        document.head.appendChild(st);
        document.documentElement.scrollTop=0;document.body.scrollTop=0;
        return true;
      })()`);
      await new Promise(resolve=>setTimeout(resolve,80));
    }
    // A ELGIN i8 usa exatamente o papel padrão do driver que passou no teste físico.
    const printOptions=elginI8'''
main=must(main,old,new,"pagina Epson com altura exata")
write("electron/main.cjs",main)

print("10.11.31: altura exata restaurada para Epson; fluxo Elgin preservado.")
