from pathlib import Path
import json,re

root=Path("app")
def read(path): return (root/path).read_text(encoding="utf-8")
def write(path,value): (root/path).write_text(value,encoding="utf-8")

pkg=json.loads(read("package.json"));pkg["version"]="10.11.19";write("package.json",json.dumps(pkg,indent=2,ensure_ascii=False))
html=read("public/index.html");html,n=re.subn(r'(id="versionInfo" class="version-info">v)[0-9.]+',r'\g<1>10.11.19',html,count=1)
if n!=1: raise SystemExit("versão HTML não encontrada")
write("public/index.html",html)
js=read("public/app.js");js,n=re.subn(r'const atual="[0-9.]+"(?=,status=)','const atual="10.11.19"',js,count=1)
if n!=1: raise SystemExit("versão do atualizador não encontrada")
write("public/app.js",js)

main=read("electron/main.cjs")
old="""$width=[System.Convert]::ToInt32($env:ELETROMIX_WIDTH)
$height=[System.Convert]::ToInt32($env:ELETROMIX_HEIGHT)
$paper=[System.Drawing.Printing.PaperSize]::new('Eletromix 80mm',$width,$height)
$document.DefaultPageSettings.PaperSize=$paper
$handler=[System.Drawing.Printing.PrintPageEventHandler]{
  param($sender,$eventArgs)
  $eventArgs.Graphics.PageUnit=[System.Drawing.GraphicsUnit]::Display
  $eventArgs.Graphics.DrawImage($image,0,0,$width,$height)
  $eventArgs.HasMorePages=$false
}"""
new="""$handler=[System.Drawing.Printing.PrintPageEventHandler]{
  param($sender,$eventArgs)
  $eventArgs.Graphics.PageUnit=[System.Drawing.GraphicsUnit]::Pixel
  $pageWidth=[Math]::Max(1,[int]$eventArgs.Graphics.VisibleClipBounds.Width)
  $scale=$pageWidth/[double]$image.Width
  $drawHeight=[Math]::Max(1,[int][Math]::Round($image.Height*$scale))
  $eventArgs.Graphics.DrawImage($image,0,0,$pageWidth,$drawHeight)
  $eventArgs.HasMorePages=$false
}"""
if main.count(old)!=1: raise SystemExit("bloco PaperSize 10.11.18 não encontrado")
main=main.replace(old,new,1)
main=main.replace('mode:"windows-elgin-i8-gdi-papersize-fixed"','mode:"windows-elgin-i8-driver-paper"',1)
write("electron/main.cjs",main)
print("10.11.19: usa o papel já configurado no driver ELGIN i8, sem criar tamanho personalizado.")
