from pathlib import Path
import json
root=Path('app')
def read(p): return (root/p).read_text(encoding='utf-8')
def write(p,s): (root/p).write_text(s,encoding='utf-8')
pkg=json.loads(read('package.json'));pkg['version']='10.10.3';write('package.json',json.dumps(pkg,indent=2,ensure_ascii=False))
html=read('public/index.html').replace('id="versionInfo" class="version-info">v10.10.2','id="versionInfo" class="version-info">v10.10.3',1);write('public/index.html',html)
js=read('public/app.js').replace('const atual="10.10.2"','const atual="10.10.3"',1)
js += r'''
// 10.10.3 - restaura navegacao e isola pagamento por venda.
// O patch 10.10.0 travava TODAS as .section por CSS. Marcamos a tela ativa no body para o CSS fixo valer somente no Caixa.
function syncCaixaMode10103(){document.body.classList.toggle('caixa-mode-10103',!!document.querySelector('#caixa.active'))}
const obs10103=new MutationObserver(syncCaixaMode10103);obs10103.observe(document.documentElement,{attributes:true,attributeFilter:['class'],subtree:true,childList:true});
document.addEventListener('click',()=>setTimeout(syncCaixaMode10103,0),true);document.addEventListener('DOMContentLoaded',syncCaixaMode10103);setTimeout(syncCaixaMode10103,300);

function valorTotal10103(){
 // Primeiro usa o total calculado do PDV atual; evita depender apenas do texto #total legado.
 const candidates=['.pdv1094-total strong','.pdv1094-total b','.pdv1094-total-value','#total'];
 for(const s of candidates){const el=document.querySelector(s);if(!el)continue;const raw=String(el.textContent||'');const n=Number(raw.replace(/[^0-9,.-]/g,'').replace(/\./g,'').replace(',','.'));if(Number.isFinite(n)&&n>0)return n}
 try{if(typeof calc==='function'){const n=Number(calc());if(Number.isFinite(n)&&n>0)return n}}catch{}
 return 0;
}
totalVenda1096=valorTotal10103;

// Cada abertura do pagamento começa limpa e já sugere exatamente o restante da venda atual.
const abrirPagamentoBase10103=abrirPagamento1096;
abrirPagamento1096=function(){
 pagamentos1096=[];
 const outro=document.querySelector('#pay1096Outro');if(outro)outro.value='';
 abrirPagamentoBase10103();
 pagamentos1096=[];
 const inp=document.querySelector('#pay1096Valor');if(inp)inp.value=valorTotal10103().toFixed(2).replace('.',',');
 atualizarPagamento1096();
};
// Depois de lançar R$10 de uma venda de R$19, o campo passa automaticamente a sugerir R$9 para a próxima forma.
const addPagamentoBase10103=addPagamento1096;
addPagamento1096=function(tipo){addPagamentoBase10103(tipo);const inp=document.querySelector('#pay1096Valor');if(inp){const r=Math.max(0,valorTotal10103()-pago1096());inp.value=r>0?r.toFixed(2).replace('.',','):''}}
// Ao fechar/finalizar, zera o estado para nunca vazar pagamento para a próxima venda.
const fecharPagamentoBase10103=fecharPagamento1096;
fecharPagamento1096=function(){fecharPagamentoBase10103();pagamentos1096=[];const inp=document.querySelector('#pay1096Valor');if(inp)inp.value='';const outro=document.querySelector('#pay1096Outro');if(outro)outro.value='';renderPagamentos1096()}
'''
write('public/app.js',js)
css=read('public/style.css')+r'''
/* 10.10.3 - desfaz o bloqueio global de navegacao criado na 10.10.0 */
body:not(.caixa-mode-10103){overflow:auto!important}body:not(.caixa-mode-10103) #app{height:auto!important;min-height:100vh!important;overflow:visible!important}body:not(.caixa-mode-10103) .layout{height:auto!important;min-height:calc(100vh - 68px)!important;overflow:visible!important}body:not(.caixa-mode-10103) main{height:auto!important;min-height:0!important;overflow:visible!important}body:not(.caixa-mode-10103) .section{height:auto!important;min-height:0!important;overflow:visible!important}
'''
write('public/style.css',css)
print('10.10.3: abas restauradas; pagamento abre com total/restante correto e nunca reaproveita valores da venda anterior.')