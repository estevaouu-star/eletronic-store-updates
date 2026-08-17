from pathlib import Path
import json
root=Path('app')
def read(p): return (root/p).read_text(encoding='utf-8')
def write(p,s): (root/p).write_text(s,encoding='utf-8')

pkg=json.loads(read('package.json')); pkg['version']='10.9.1'; write('package.json',json.dumps(pkg,indent=2,ensure_ascii=False))
html=read('public/index.html').replace('id="versionInfo" class="version-info">v10.9.0','id="versionInfo" class="version-info">v10.9.1',1); write('public/index.html',html)
js=read('public/app.js').replace('const atual="10.9.0"','const atual="10.9.1"',1)
js += r'''
// 10.9.1 - Caixa inspirado estruturalmente no Smart PDV + paginação ultraleve de Produtos
(function(){
 const q=(s,r=document)=>r.querySelector(s), qa=(s,r=document)=>[...r.querySelectorAll(s)];
 function txt(el){return (el?.textContent||'').trim()}
 function caixa(){return q('#caixa')}
 function cards(s){return qa('.product',s).filter(x=>!x.closest('.smart-products-grid'))}
 function barcode(s){return qa('input',s).find(i=>/código|codigo|barras|leia/i.test((i.placeholder||'')+' '+txt(i.parentElement)))}
 function addButton(card){return qa('button',card).find(b=>/adicionar/i.test(txt(b)))}
 function categoryOf(card){const t=txt(card); const m=t.match(/(?:Não informada|Nao informada)\s*[·-]\s*([^·-]+)\s*[·-]\s*Estoque/i); return (m?.[1]||'Geral').trim()}
 function setupCaixa(){
   const s=caixa(); if(!s||s.dataset.smartReal==='1')return; s.dataset.smartReal='1'; s.classList.add('smart-real-pdv');
   qa('.smart-pdv-commandbar',s).forEach(x=>x.remove());
   const catalog=qa('.pdv-catalog-pane',s)[0]||cards(s)[0]?.parentElement; if(!catalog)return;
   const originalCards=cards(s); if(!originalCards.length)return;
   const shell=document.createElement('section'); shell.className='smart-browser';
   shell.innerHTML='<div class="smart-section-title">CATEGORIAS</div><div class="smart-categories"></div><div class="smart-section-title smart-products-title"><span>PRODUTOS</span><button type="button" class="smart-search-toggle" title="Pesquisar produto">⌕ Pesquisar</button></div><div class="smart-searchbox" hidden><input type="search" placeholder="Nome, código, barras, marca ou especificação"><button type="button">Fechar</button></div><div class="smart-products-grid"></div>';
   catalog.innerHTML=''; catalog.appendChild(shell);
   const grid=q('.smart-products-grid',shell), cats=q('.smart-categories',shell), sb=q('.smart-searchbox',shell), si=q('input',sb);
   let active='Todos'; const favKey='eletromix-pdv-favoritos'; let fav=new Set(JSON.parse(localStorage.getItem(favKey)||'[]'));
   const data=originalCards.map((card,idx)=>({card,idx,key:(card.dataset.id||txt(card).slice(0,80)),cat:categoryOf(card),text:txt(card).toLowerCase()}));
   const catNames=['Todos','★ Favoritos','Mais vendidos',...new Set(data.map(x=>x.cat))];
   catNames.forEach(name=>{const b=document.createElement('button');b.type='button';b.className='smart-cat';b.textContent=name;b.onclick=()=>{active=name;render()};cats.appendChild(b)});
   function render(){
     qa('.smart-cat',cats).forEach(b=>b.classList.toggle('active',txt(b)===active)); grid.innerHTML=''; const term=si.value.trim().toLowerCase();
     let list=data.filter(x=>(!term||x.text.includes(term))&&(active==='Todos'||active==='★ Favoritos'&&fav.has(x.key)||active==='Mais vendidos'||x.cat===active));
     if(active==='Mais vendidos') list=list.slice().sort((a,b)=>(+(b.card.dataset.sales||0))-(+(a.card.dataset.sales||0))).slice(0,12);
     list.slice(0,40).forEach(x=>{const tile=document.createElement('article');tile.className='smart-product-tile'; const title=txt(x.card.querySelector('b,strong'))||txt(x.card).split('\n')[0]; const price=(txt(x.card).match(/R\$\s*[\d.,]+/g)||[]).pop()||''; tile.innerHTML='<button class="smart-fav" type="button" title="Favoritar">'+(fav.has(x.key)?'★':'☆')+'</button><div class="smart-product-name"></div><div class="smart-product-meta"></div>'; q('.smart-product-name',tile).textContent=title; q('.smart-product-meta',tile).textContent=price+' · '+x.cat; tile.onclick=e=>{if(e.target.closest('.smart-fav'))return; const b=addButton(x.card); if(b)b.click()}; q('.smart-fav',tile).onclick=()=>{fav.has(x.key)?fav.delete(x.key):fav.add(x.key);localStorage.setItem(favKey,JSON.stringify([...fav]));render()}; grid.appendChild(tile)});
   }
   q('.smart-search-toggle',shell).onclick=()=>{sb.hidden=false;si.focus()}; q('button',sb).onclick=()=>{si.value='';sb.hidden=true;render()}; si.oninput=render; render();
   const bi=barcode(s); if(bi){bi.closest('div')?.classList.add('smart-code-area')}
 }
 function paginateProducts(){
   const s=q('#produtos'); if(!s||s.dataset.page3==='1')return; const list=qa('.product',s); if(list.length<=3)return; s.dataset.page3='1'; let page=1; const size=3; const host=list[0].parentElement; const all=list.map(x=>x.cloneNode(true));
   list.forEach(x=>x.remove());
   const pager=document.createElement('div');pager.className='products-pager';host.insertAdjacentElement('afterend',pager);
   function render(){qa('.product',host).forEach(x=>x.remove()); const start=(page-1)*size; all.slice(start,start+size).forEach(x=>host.appendChild(x.cloneNode(true))); const pages=Math.ceil(all.length/size);pager.innerHTML=''; const prev=document.createElement('button');prev.textContent='‹ Anterior';prev.disabled=page===1;prev.onclick=()=>{page--;render()};pager.appendChild(prev); for(let p=Math.max(1,page-2);p<=Math.min(pages,page+2);p++){const b=document.createElement('button');b.textContent=p;b.className=p===page?'active':'';b.onclick=()=>{page=p;render()};pager.appendChild(b)} const next=document.createElement('button');next.textContent='Próxima ›';next.disabled=page===pages;next.onclick=()=>{page++;render()};pager.appendChild(next)} render();
 }
 document.addEventListener('click',e=>{const n=e.target.closest?.('.nav');if(n){setTimeout(()=>{setupCaixa();paginateProducts()},80)}}); document.addEventListener('DOMContentLoaded',()=>setTimeout(()=>{setupCaixa();paginateProducts()},300)); setTimeout(()=>{setupCaixa();paginateProducts()},700);
})();
'''
write('public/app.js',js)
css=read('public/style.css')+r'''
/* 10.9.1 Smart-PDV estrutural */
.smart-real-pdv .smart-pdv-commandbar{display:none!important}.smart-browser{display:grid;gap:8px}.smart-section-title{background:#173f68;color:#fff;font-size:12px;font-weight:900;letter-spacing:.05em;padding:8px 10px;border-radius:5px}.smart-products-title{display:flex;align-items:center;justify-content:space-between}.smart-search-toggle{border:0;background:rgba(255,255,255,.14);color:#fff;border-radius:5px;padding:5px 10px;font-weight:800;cursor:pointer}.smart-categories{display:grid;grid-template-columns:repeat(4,minmax(110px,1fr));gap:7px;min-height:92px}.smart-cat{min-height:70px;border:1px solid var(--border);border-radius:5px;background:color-mix(in srgb,var(--card-bg) 90%,var(--page-bg));color:var(--text);font-weight:850;cursor:pointer}.smart-cat.active{background:var(--primary);border-color:var(--primary);color:#fff}.smart-searchbox{display:flex;gap:6px}.smart-searchbox input{flex:1}.smart-products-grid{display:grid;grid-template-columns:repeat(5,minmax(100px,1fr));gap:7px;align-content:start;min-height:190px;max-height:48vh;overflow:auto}.smart-product-tile{position:relative;min-height:105px;border:1px solid var(--border);border-radius:6px;padding:26px 8px 9px;background:var(--card-bg);cursor:pointer;display:flex;flex-direction:column;justify-content:flex-end}.smart-product-tile:hover{border-color:var(--primary);box-shadow:0 4px 12px rgba(0,0,0,.08)}.smart-product-name{font-weight:850;font-size:12px;line-height:1.2}.smart-product-meta{font-size:10px;color:var(--muted);margin-top:5px}.smart-fav{position:absolute;right:5px;top:4px;border:0;background:transparent;color:var(--primary);font-size:19px;cursor:pointer}.products-pager{display:flex;gap:6px;align-items:center;justify-content:center;padding:12px;flex-wrap:wrap}.products-pager button{min-width:36px;height:34px;border:1px solid var(--border);border-radius:7px;background:var(--card-bg);color:var(--text);cursor:pointer}.products-pager button.active{background:var(--primary);border-color:var(--primary);color:#fff}.products-pager button:disabled{opacity:.4;cursor:default}@media(max-width:1100px){.smart-products-grid{grid-template-columns:repeat(3,1fr)}.smart-categories{grid-template-columns:repeat(3,1fr)}}
'''
write('public/style.css',css)
print('10.9.1: novo Caixa com categorias/favoritos/pesquisa e aba Produtos paginada de 3 em 3.')