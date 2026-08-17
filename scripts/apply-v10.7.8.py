from pathlib import Path
import json

root=Path('app')
def read(p): return (root/p).read_text(encoding='utf-8')
def write(p,s): (root/p).write_text(s,encoding='utf-8')
def must(s,a,b,label):
    if a not in s: raise RuntimeError(f'Trecho nao encontrado: {label}')
    return s.replace(a,b,1)

pkg=json.loads(read('package.json'))
pkg['version']='10.7.8'
write('package.json',json.dumps(pkg,indent=2,ensure_ascii=False))

html=read('public/index.html')
html=html.replace('id="versionInfo" class="version-info">v10.7.7','id="versionInfo" class="version-info">v10.7.8')
html=html.replace('Comprimento: automático conforme o conteúdo','Comprimento: automático, começando no topo e terminando logo após o conteúdo')
write('public/index.html',html)

js=read('public/app.js')
js=js.replace('const atual="10.7.7"','const atual="10.7.8"')
write('public/app.js',js)

main=read('electron/main.cjs')
# Evita conflito entre @page auto e o tamanho exato definido na impressão.
main=main.replace('@page{margin:0;size:${width}mm auto}','@page{margin:0!important}')

old='''    const measuredMm = Number(receiptPx||0) * 25.4 / 96;
    // Só deixa uma pequena folga para a guilhotina/avanço final da impressora.
    const heightMm = Math.min(1000, Math.max(32, Math.ceil(measuredMm + 4)));
    console.log('[printer] comprimento automatico:', {receiptPx, measuredMm, heightMm, width});

    const result = await new Promise(resolve => {
      printWindow.webContents.print({
        silent: true,
        printBackground: true,
        deviceName,
        margins: { marginType: "none" },
        pageSize: { width: width * 1000, height: heightMm * 1000 }
      }, (success, failureReason) => resolve({ success, failureReason: failureReason || "", deviceName, paperWidth: width }));
    });'''

new='''    const measuredMm = Number(receiptPx||0) * 25.4 / 96;
    // Folga final pequena: suficiente para a guilhotina, sem gerar dezenas de centímetros em branco.
    const heightMm = Math.min(1000, Math.max(28, Math.ceil(measuredMm + 3)));
    const innerMm = width === 58 ? 52 : 72;
    const leftMm = Math.max(0,(width-innerMm)/2);

    // Alguns drivers térmicos centralizam verticalmente uma página personalizada.
    // Fixamos o comprovante em 0,0 e damos ao HTML exatamente a mesma altura enviada ao driver.
    // Assim o conteúdo começa imediatamente no topo da bobina e o corte acontece logo depois dele.
    await printWindow.webContents.executeJavaScript(`(()=>{
      const st=document.createElement('style');
      st.id='eletromix-exact-print-page';
      st.textContent='@page{size:${width}mm ${heightMm}mm!important;margin:0!important}' +
        'html,body{position:relative!important;width:${width}mm!important;height:${heightMm}mm!important;min-height:0!important;max-height:${heightMm}mm!important;margin:0!important;padding:0!important;overflow:hidden!important}' +
        '.receipt{position:absolute!important;top:0!important;left:${leftMm}mm!important;margin:0!important;width:${innerMm}mm!important;max-width:${innerMm}mm!important;transform:none!important}';
      document.head.appendChild(st);
      document.documentElement.scrollTop=0;document.body.scrollTop=0;
      return {top:document.querySelector('.receipt')?.getBoundingClientRect()?.top||0,height:document.querySelector('.receipt')?.getBoundingClientRect()?.height||0};
    })()`);
    await new Promise(resolve => setTimeout(resolve, 80));
    console.log('[printer] pagina termica exata:', {receiptPx, measuredMm, heightMm, width, innerMm});

    const result = await new Promise(resolve => {
      printWindow.webContents.print({
        silent: true,
        printBackground: true,
        deviceName,
        margins: { marginType: "none" },
        pageSize: { width: Math.round(width * 1000), height: Math.round(heightMm * 1000) }
      }, (success, failureReason) => resolve({ success, failureReason: failureReason || "", deviceName, paperWidth: width, paperLength: heightMm }));
    });'''
main=must(main,old,new,'pagina termica exata')
write('electron/main.cjs',main)

css=read('public/style.css')
css += '''\n/* 10.7.8 - comprovante sem avanço em branco antes do conteúdo */\n.printer-auto-length{font-weight:600}\n'''
write('public/style.css',css)

print('Patch 10.7.8 aplicado: comprovante ancorado no topo e pagina termica com altura exata.')
