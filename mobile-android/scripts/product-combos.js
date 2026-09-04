(() => {
  if (window.__eletromixProductCombosInstalled) {
    window.__eletromixProductCombosRefresh?.();
    return;
  }
  window.__eletromixProductCombosInstalled = true;

  const style = document.createElement('style');
  style.textContent = `
    .em-editable-combo{position:relative;width:100%;display:block}
    .em-editable-combo>input{width:100%!important;padding-right:46px!important;box-sizing:border-box!important}
    .em-editable-combo-toggle{position:absolute!important;right:2px!important;top:50%!important;transform:translateY(-50%)!important;width:40px!important;height:38px!important;min-height:38px!important;padding:0!important;border:0!important;border-left:1px solid rgba(127,127,127,.28)!important;border-radius:0 8px 8px 0!important;background:transparent!important;color:inherit!important;font-size:18px!important;line-height:1!important;z-index:3!important}
    .em-editable-combo-menu{display:none;position:absolute;left:0;right:0;top:calc(100% + 5px);max-height:240px;overflow:auto;background:#fff;color:#111;border:1px solid #bbb;border-radius:10px;box-shadow:0 12px 30px rgba(0,0,0,.28);z-index:2147483646;padding:5px}
    .em-editable-combo-menu.open{display:block}
    .em-editable-combo-option{display:block;width:100%;padding:11px 12px;border:0;border-bottom:1px solid #eee;background:#fff;color:#111;text-align:left;font:inherit;border-radius:7px}
    .em-editable-combo-option:last-child{border-bottom:0}
    .em-editable-combo-empty{padding:11px 12px;color:#666;font-size:13px}
  `;
  document.head.appendChild(style);

  const normal = value => String(value ?? '').trim();
  const unique = values => [...new Set(values.map(normal).filter(Boolean))]
    .sort((a,b)=>a.localeCompare(b,'pt-BR',{sensitivity:'base'}));

  function productArrays(){
    const arrays=[];
    for(const key of ['produtos','products','listaProdutos','mobileProdutos','__produtos']){
      try{if(Array.isArray(window[key]))arrays.push(window[key])}catch(_){}
    }
    return arrays;
  }

  function collect(field){
    const values=[];
    for(const list of productArrays()){
      for(const p of list){
        if(!p||typeof p!=='object')continue;
        const value=field==='categoria'?(p.categoria??p.category):(p.marca??p.brand);
        if(value)values.push(value);
      }
    }

    document.querySelectorAll(`[data-${field}]`).forEach(el=>values.push(el.getAttribute(`data-${field}`)));
    document.querySelectorAll(`select[name="${field}"] option`).forEach(el=>values.push(el.value||el.textContent));
    document.querySelectorAll(`input[name="${field}"]`).forEach(el=>{if(el.value)values.push(el.value)});

    document.querySelectorAll('.product-card,.produto-card,.product-item,.produto-item,tr').forEach(el=>{
      const text=String(el.innerText||'');
      const re=field==='categoria'?/Categoria\s*:\s*([^\n|•]+)/i:/Marca\s*:\s*([^\n|•]+)/i;
      const match=text.match(re);if(match?.[1])values.push(match[1]);
    });

    try{
      const saved=JSON.parse(localStorage.getItem(`em-combo-${field}`)||'[]');
      if(Array.isArray(saved))values.push(...saved);
    }catch(_){}
    return unique(values);
  }

  function remember(field,value){
    value=normal(value);if(!value)return;
    try{
      const values=unique([...collect(field),value]);
      localStorage.setItem(`em-combo-${field}`,JSON.stringify(values.slice(-200)));
    }catch(_){}
  }

  function closeAll(except){
    document.querySelectorAll('.em-editable-combo-menu.open').forEach(menu=>{
      if(menu!==except)menu.classList.remove('open');
    });
  }

  function renderMenu(input,menu,field){
    const values=collect(field).filter(v=>
      v.localeCompare(normal(input.value),'pt-BR',{sensitivity:'base'})!==0
    );
    menu.innerHTML='';
    if(!values.length){
      const empty=document.createElement('div');
      empty.className='em-editable-combo-empty';
      empty.textContent=`Nenhuma ${field} cadastrada encontrada. Você pode digitar uma nova.`;
      menu.appendChild(empty);
      return;
    }
    values.forEach(value=>{
      const option=document.createElement('button');
      option.type='button';
      option.className='em-editable-combo-option';
      option.textContent=value;
      option.addEventListener('click',()=>{
        input.value=value;
        input.dispatchEvent(new Event('input',{bubbles:true}));
        input.dispatchEvent(new Event('change',{bubbles:true}));
        remember(field,value);
        menu.classList.remove('open');
        input.focus();
      });
      menu.appendChild(option);
    });
  }

  function enhance(input,field){
    if(!input||input.dataset.emEditableCombo==='1'||input.type==='hidden')return;
    input.dataset.emEditableCombo='1';
    const wrap=document.createElement('div');
    wrap.className='em-editable-combo';
    input.parentNode.insertBefore(wrap,input);
    wrap.appendChild(input);

    const toggle=document.createElement('button');
    toggle.type='button';
    toggle.className='em-editable-combo-toggle';
    toggle.setAttribute('aria-label',`Escolher ${field} existente`);
    toggle.textContent='⌄';

    const menu=document.createElement('div');
    menu.className='em-editable-combo-menu';
    wrap.append(toggle,menu);

    toggle.addEventListener('click',event=>{
      event.preventDefault();
      event.stopPropagation();
      const opening=!menu.classList.contains('open');
      closeAll(menu);
      if(opening){
        renderMenu(input,menu,field);
        menu.classList.add('open');
      }else{
        menu.classList.remove('open');
      }
    });
    input.addEventListener('change',()=>remember(field,input.value));
    input.addEventListener('blur',()=>remember(field,input.value));
  }

  function refresh(){
    document.querySelectorAll('input[name="categoria"], input[id*="categoria" i]').forEach(input=>enhance(input,'categoria'));
    document.querySelectorAll('input[name="marca"], input[id*="marca" i]').forEach(input=>enhance(input,'marca'));
  }

  window.__eletromixProductCombosRefresh=refresh;
  document.addEventListener('click',event=>{
    if(!event.target.closest?.('.em-editable-combo'))closeAll();
  });
  new MutationObserver(()=>refresh()).observe(document.documentElement,{childList:true,subtree:true});
  refresh();
  setTimeout(refresh,500);
  setTimeout(refresh,1500);
  setTimeout(refresh,3500);
})();
