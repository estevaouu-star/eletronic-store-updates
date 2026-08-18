from pathlib import Path
import json
root=Path('app')
def read(p): return (root/p).read_text(encoding='utf-8')
def write(p,s): (root/p).write_text(s,encoding='utf-8')

pkg=json.loads(read('package.json'));pkg['version']='10.10.16';write('package.json',json.dumps(pkg,indent=2,ensure_ascii=False))
html=read('public/index.html').replace('id="versionInfo" class="version-info">v10.10.15','id="versionInfo" class="version-info">v10.10.16',1);write('public/index.html',html)
js=read('public/app.js').replace('const atual="10.10.15"','const atual="10.10.16"',1)
js += r'''
// 10.10.16 - corrige persistência da tela Personalização.
// Fallback local por loja: salva/restaura os campos visuais mesmo se a rotina legada falhar.
function lojaKey101016(){try{return String(storeId||document.querySelector('#storeSelect')?.value||'default')}catch{return 'default'}}
function persKey101016(){return 'eletromix_personalizacao_'+lojaKey101016()}
function personalizacaoSection101016(){
 const active=[...document.querySelectorAll('.section.active')];
 let sec=active.find(s=>/personal/i.test((s.id||'')+' '+(s.textContent||'').slice(0,300)));
 if(sec)return sec;
 const nav=[...document.querySelectorAll('.nav')].find(n=>/personal/i.test(n.textContent||''));
 const id=nav?.dataset?.s;if(id)sec=document.getElementById(id);
 return sec||document.querySelector('#personalizacao,#personalizar,#customizacao,#customization');
}
function collectPers101016(){
 const sec=personalizacaoSection101016();if(!sec)return null;
 const data={};
 sec.querySelectorAll('input,select,textarea').forEach((el,i)=>{
   const type=(el.type||'').toLowerCase();if(type==='file'||type==='password')return;
   const k=el.name||el.id||('field_'+i);if(!k)return;
   if(type==='checkbox'||type==='radio')data[k]={kind:type,checked:!!el.checked,value:el.value};
   else data[k]={kind:'value',value:el.value};
 });
 return data;
}
function savePers101016(){
 const d=collectPers101016();if(!d)return false;
 try{localStorage.setItem(persKey101016(),JSON.stringify(d));return true}catch(e){console.error('[personalizacao save]',e);return false}
}
function restorePers101016(){
 const sec=personalizacaoSection101016();if(!sec)return false;
 let d=null;try{d=JSON.parse(localStorage.getItem(persKey101016())||'null')}catch{return false}
 if(!d)return false;
 sec.querySelectorAll('input,select,textarea').forEach((el,i)=>{
   const type=(el.type||'').toLowerCase();if(type==='file'||type==='password')return;
   const k=el.name||el.id||('field_'+i),v=d[k];if(!v)return;
   if(v.kind==='checkbox'||v.kind==='radio')el.checked=!!v.checked;else if(v.value!=null)el.value=v.value;
   try{el.dispatchEvent(new Event('input',{bubbles:true}));el.dispatchEvent(new Event('change',{bubbles:true}))}catch{}
 });
 return true;
}
function isSavePersonalizacao101016(btn){
 const sec=personalizacaoSection101016();if(!sec||!btn||!sec.contains(btn))return false;
 const t=((btn.textContent||'')+' '+(btn.id||'')+' '+(btn.className||'')).toLowerCase();return /salvar|save|aplicar/.test(t);
}
document.addEventListener('click',e=>{
 const nav=e.target.closest?.('.nav');if(nav&&/personal/i.test(nav.textContent||''))setTimeout(restorePers101016,80);
 const btn=e.target.closest?.('button,input[type="submit"]');if(isSavePersonalizacao101016(btn)){
   // espera a rotina original terminar e grava exatamente o estado que ficou na tela
   setTimeout(()=>{if(savePers101016())try{toast('Personalização salva.')}catch{}},120);
 }
},true);
document.addEventListener('submit',e=>{const sec=personalizacaoSection101016();if(sec&&sec.contains(e.target))setTimeout(savePers101016,120)},true);
document.addEventListener('DOMContentLoaded',()=>setTimeout(restorePers101016,500));
setTimeout(restorePers101016,1200);
'''
write('public/app.js',js)
print('10.10.16: Personalização passa a persistir por loja e restaura os valores ao reabrir a aba.')