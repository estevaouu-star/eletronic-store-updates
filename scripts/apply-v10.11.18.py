from pathlib import Path
import json,re

root=Path("app")
def read(path): return (root/path).read_text(encoding="utf-8")
def write(path,value): (root/path).write_text(value,encoding="utf-8")

pkg=json.loads(read("package.json"));pkg["version"]="10.11.18";write("package.json",json.dumps(pkg,indent=2,ensure_ascii=False))
html=read("public/index.html");html,n=re.subn(r'(id="versionInfo" class="version-info">v)[0-9.]+',r'\g<1>10.11.18',html,count=1)
if n!=1: raise SystemExit("versão HTML não encontrada")
write("public/index.html",html)
js=read("public/app.js");js,n=re.subn(r'const atual="[0-9.]+"(?=,status=)','const atual="10.11.18"',js,count=1)
if n!=1: raise SystemExit("versão do atualizador não encontrada")
write("public/app.js",js)

main=read("electron/main.cjs")
old="$paper=New-Object System.Drawing.Printing.PaperSize -ArgumentList 'Eletromix 80mm',[int]$env:ELETROMIX_WIDTH,[int]$env:ELETROMIX_HEIGHT"
new="""$width=[System.Convert]::ToInt32($env:ELETROMIX_WIDTH)
$height=[System.Convert]::ToInt32($env:ELETROMIX_HEIGHT)
$paper=[System.Drawing.Printing.PaperSize]::new('Eletromix 80mm',$width,$height)"""
if main.count(old)!=1: raise SystemExit("linha PaperSize problemática não encontrada")
main=main.replace(old,new,1)
main=main.replace("$width=[int]$env:ELETROMIX_WIDTH\n$height=[int]$env:ELETROMIX_HEIGHT\n$handler=","$handler=",1)
main=main.replace('mode:"windows-elgin-i8-gdi-native"','mode:"windows-elgin-i8-gdi-papersize-fixed"',1)
write("electron/main.cjs",main)
print("10.11.18: PaperSize recebe Int32 reais por construtor direto do .NET.")
