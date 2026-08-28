from pathlib import Path
import json,re
root=Path('app')
def read(p): return (root/p).read_text(encoding='utf-8')
def write(p,s): (root/p).write_text(s,encoding='utf-8')

pkg=json.loads(read('package.json'));pkg['version']='10.11.5';write('package.json',json.dumps(pkg,indent=2,ensure_ascii=False))
html=read('public/index.html');html,n=re.subn(r'(id="versionInfo" class="version-info">v)[0-9.]+',r'\g<1>10.11.05',html,count=1)
if n!=1: raise SystemExit('Versao cabecalho nao encontrada')
write('public/index.html',html)
js=read('public/app.js');js,n=re.subn(r'const atual="[0-9.]+"(?=,status=)','const atual="10.11.5"',js,count=1)
if n!=1: raise SystemExit('Versao atualizador nao encontrada')
write('public/app.js',js)

main=read('electron/main.cjs')
needle='ipcMain.handle("printer:print", async (_event, payload = {}) => {'
pos=main.find(needle)
if pos<0: raise SystemExit('Handler printer:print nao encontrado')
# ELGIN i8: evita caminho RAW/ESC-POS que pode aceitar o job sem imprimir; força o caminho Electron/driver Windows.
insert='''\nfunction eletromixElginI8_101105(name){return /(?:^|\\b)(?:elgin\\s*)?i8(?:\\b|$)/i.test(String(name||""))||/elgin.*i8/i.test(String(name||""));}\n'''
main=main[:pos]+insert+main[pos:]
# Dentro do handler, após resolução do deviceName, os caminhos RAW normalmente testam ESC/POS. Desabilita RAW especificamente para i8.
# Faz substituições conservadoras nas condições mais comuns sem afetar outras impressoras.
patterns=[
 ('if(process.platform==="win32"&&', 'if(process.platform==="win32"&&!eletromixElginI8_101105(deviceName)&&'),
 ("if (process.platform === 'win32' &&", "if (process.platform === 'win32' && !eletromixElginI8_101105(deviceName) &&"),
 ('if (process.platform === "win32" &&', 'if (process.platform === "win32" && !eletromixElginI8_101105(deviceName) &&')
]
changed=0
handler_end=main.find('\nipcMain.handle(',pos+len(needle))
if handler_end<0: handler_end=len(main)
chunk=main[pos:handler_end]
for a,b in patterns:
    if a in chunk:
        chunk=chunk.replace(a,b,1);changed+=1;break
# Se não houver condição RAW reconhecida, ainda preserva código e adiciona marcador para diagnóstico.
main=main[:pos]+chunk+main[handler_end:]
# Electron print fallback: i8 usa silent via driver e nome exato selecionado.
main=main.replace('deviceName,\n      silent:true,','deviceName,\n      silent:true,',1)
write('electron/main.cjs',main)
print('10.11.05: ELGIN i8 prioriza driver do Windows; RAW ESC/POS fica reservado às demais térmicas. condicao=',changed)
