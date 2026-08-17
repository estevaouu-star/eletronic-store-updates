from pathlib import Path
import json

root=Path('app')
def read(p): return (root/p).read_text(encoding='utf-8')
def write(p,s): (root/p).write_text(s,encoding='utf-8')
def must(s,a,b,label):
    if a not in s: raise RuntimeError(f'Trecho nao encontrado: {label}')
    return s.replace(a,b,1)

pkg=json.loads(read('package.json'))
pkg['version']='10.7.7'
write('package.json',json.dumps(pkg,indent=2,ensure_ascii=False))

html=read('public/index.html')
html=html.replace('id="versionInfo" class="version-info">v10.7.6','id="versionInfo" class="version-info">v10.7.7')
html=html.replace('<div><label>Largura do papel</label><select id="printerWidth"><option value="80">80 mm</option><option value="58">58 mm</option></select></div>', '<div><label>Largura do papel</label><select id="printerWidth"><option value="80">80 mm</option><option value="58">58 mm</option></select><small class="printer-auto-length">Comprimento: automático conforme o conteúdo</small></div>')
write('public/index.html',html)

js=read('public/app.js')
js=js.replace('const atual="10.7.6"','const atual="10.7.7"')
write('public/app.js',js)

main=read('electron/main.cjs')
old='''    // Calcula a altura real do comprovante para evitar páginas gigantes ou corte em bobina.
    const px = await printWindow.webContents.executeJavaScript(`Math.max(document.body?.scrollHeight||0,document.documentElement?.scrollHeight||0,220)`);
    const heightMm = Math.min(600, Math.max(60, Math.ceil(Number(px||220) * 25.4 / 96 + 8)));

    const result = await new Promise(resolve => {'''
new='''    // Comprimento automático: mede SOMENTE o comprovante, não a altura da janela invisível.
    // A versão anterior usava scrollHeight do documento; como a janela tinha 900 px de altura,
    // isso podia criar uma página muito maior que o conteúdo e desperdiçar bastante bobina.
    const receiptPx = await printWindow.webContents.executeJavaScript(`(()=>{
      const el=document.querySelector('.receipt');
      if(!el)return 0;
      const r=el.getBoundingClientRect();
      return Math.max(r.height,el.scrollHeight||0);
    })()`);
    const measuredMm = Number(receiptPx||0) * 25.4 / 96;
    // Só deixa uma pequena folga para a guilhotina/avanço final da impressora.
    const heightMm = Math.min(1000, Math.max(32, Math.ceil(measuredMm + 4)));
    console.log('[printer] comprimento automatico:', {receiptPx, measuredMm, heightMm, width});

    const result = await new Promise(resolve => {'''
main=must(main,old,new,'calculo de comprimento da bobina')
write('electron/main.cjs',main)

css=read('public/style.css')
css += '''\n/* 10.7.7 - impressão térmica com comprimento automático */\n.printer-auto-length{display:block;margin-top:-4px;color:var(--text-muted);font-size:11px;line-height:1.25}\n'''
write('public/style.css',css)

print('Patch 10.7.7 aplicado: comprimento do comprovante agora e calculado pela altura real do conteudo.')
