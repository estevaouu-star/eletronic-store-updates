from pathlib import Path
import json
root=Path('app')
def read(p): return (root/p).read_text(encoding='utf-8')
def write(p,s): (root/p).write_text(s,encoding='utf-8')
def rep(s,a,b):
 if a not in s: raise RuntimeError('versao anterior nao encontrada')
 return s.replace(a,b,1)
pkg=json.loads(read('package.json'));pkg['version']='10.10.49';write('package.json',json.dumps(pkg,indent=2,ensure_ascii=False))
html=read('public/index.html');html=rep(html,'id="versionInfo" class="version-info">v10.10.48','id="versionInfo" class="version-info">v10.10.49');write('public/index.html',html)
js=read('public/app.js');js=rep(js,'const atual="10.10.48"','const atual="10.10.49"')
js += r'''

// 10.10.49 - Via do cliente e Via da loja passam pelo MESMO gerador usado pela garantia.
imprimirOS101030=async function(row,kind,button){
 const ordem=osAtual101025(row);if(!ordem)return toast('Selecione uma ordem de serviço para imprimir.');
 if(kind==='garantia'&&!osGarantiaAtiva101036(ordem))return toast('A garantia ainda não foi iniciada pelo técnico.');
 if(osPrintInFlight101020)return toast('A impressão da OS já foi enviada. Aguarde um instante.');
 if(!window.desktopPrinter)return toast('Módulo de impressão do Windows não está disponível.');
 const original=button?.textContent||'';
 // CORREÇÃO: não usa mais osReceipt101030 diretamente. Usa osViaHtml101036, igual ao fluxo da garantia.
 const html=osViaHtml101036(ordem,kind);
 if(!html)return toast('Não foi possível montar esta via.');
 osPrintInFlight101020=true;if(button){button.disabled=true;button.textContent='Imprimindo...'}
 try{
  loadPrinterSettings();
  const result=await window.desktopPrinter.print({html,deviceName:printerSettings.deviceName,paperWidth:printerSettings.paperWidth,itemCount:1});
  if(!result?.success)throw new Error(result?.failureReason||'A impressora não respondeu.');
  if(result.deviceName){printerSettings.deviceName=result.deviceName;savePrinterSettings()}
  const nomes={cliente:'Via do cliente',loja:'Via da loja',garantia:'Via de garantia'};
  toast(`${nomes[kind]} enviada para a impressora.`);
 }catch(e){console.error('[OS térmica 101049]',e);toast(`Falha ao imprimir: ${String(e?.message||e)}`)}
 finally{osPrintInFlight101020=false;if(button){button.disabled=false;button.textContent=original}}
};
'''
write('public/app.js',js)
print('10.10.49: cliente/loja agora usam osViaHtml101036, o mesmo pipeline visual da garantia.')
