from pathlib import Path
import json,re

root=Path('app')
def read(p): return (root/p).read_text(encoding='utf-8')
def write(p,s): (root/p).write_text(s,encoding='utf-8')
def replace1(s,a,b,label):
    if a not in s: raise RuntimeError(f'Trecho nao encontrado: {label}')
    return s.replace(a,b,1)

pkg=json.loads(read('package.json'));pkg['version']='10.10.34';write('package.json',json.dumps(pkg,indent=2,ensure_ascii=False))
html=read('public/index.html');html=replace1(html,'id="versionInfo" class="version-info">v10.10.33','id="versionInfo" class="version-info">v10.10.34','versao');write('public/index.html',html)
js=read('public/app.js');js=replace1(js,'const atual="10.10.33"','const atual="10.10.34"','atualizador')
server=read('src/server.ts')

SYNC_WORDS=re.compile(r'(sync|sincron|cloud|online|supabase|electronic_store|pull|push)',re.I)

def function_context(text,name):
    pats=[
      re.compile(r'(?:async\s+)?function\s+'+re.escape(name)+r'\s*\([^)]*\)\s*\{',re.I),
      re.compile(r'(?:const|let|var)\s+'+re.escape(name)+r'\s*=\s*(?:async\s*)?\([^)]*\)\s*=>\s*\{',re.I),
      re.compile(r'(?:const|let|var)\s+'+re.escape(name)+r'\s*=\s*(?:async\s*)?[^=;\n]+=>\s*\{',re.I),
    ]
    for p in pats:
      m=p.search(text)
      if m:return text[m.start():m.start()+6000]
    return ''

def candidates(text,where):
    out=[]
    patterns=[
      re.compile(r'setInterval\(\s*([A-Za-z_$][\w$]*)\s*,\s*(\d{3,6})\s*\)',re.S),
      re.compile(r'setInterval\(\s*(?:async\s*)?\(\s*\)\s*=>\s*([A-Za-z_$][\w$]*)\s*\(\s*\)\s*,\s*(\d{3,6})\s*\)',re.S),
    ]
    for p in patterns:
      for m in p.finditer(text):
        name=m.group(1);delay=int(m.group(2));ctx=function_context(text,name);around=text[max(0,m.start()-900):min(len(text),m.end()+900)]
        score=0
        if SYNC_WORDS.search(name):score+=6
        if SYNC_WORDS.search(ctx):score+=4
        if SYNC_WORDS.search(around):score+=3
        if 'electronic_store_pull' in ctx or 'electronic_store_pull' in around:score+=10
        if 3000<=delay<=30000:score+=2
        if score>=6:out.append({'where':where,'start':m.start(),'end':m.end(),'raw':m.group(0),'name':name,'delay':delay,'score':score,'kind':'named'})
    inline=re.compile(r'setInterval\(\s*(?:async\s*)?\(\s*\)\s*=>\s*\{(.{0,5000}?)\}\s*,\s*(\d{3,6})\s*\)',re.S)
    for m in inline.finditer(text):
      body=m.group(1);delay=int(m.group(2));score=(10 if 'electronic_store_pull' in body else 0)+(6 if SYNC_WORDS.search(body) else 0)+(2 if 3000<=delay<=30000 else 0)
      if score>=8:out.append({'where':where,'start':m.start(),'end':m.end(),'raw':m.group(0),'name':None,'delay':delay,'score':score,'kind':'inline','body':body})
    return out

allc=candidates(js,'client')+candidates(server,'server')
if not allc: raise RuntimeError('Polling de sincronizacao nao encontrado; publicacao bloqueada por seguranca.')
allc.sort(key=lambda x:(x['score'],-x['delay']),reverse=True)
best=allc[0]
if len(allc)>1 and allc[1]['score']==best['score']:
    raise RuntimeError('Mais de um polling de sincronizacao equivalente foi encontrado; revisar antes de publicar.')

manual_mode=best['where']
manual_name=best.get('name')
marker='/* SYNC_POLLING_DISABLED_101034: sincronizacao automatica removida para economizar egress */'
if manual_mode=='client':
    js=js[:best['start']]+marker+js[best['end']:]
    if best['kind']=='named': action=f"await Promise.resolve({manual_name}())"
    else:
      helper='async function syncManualLegacy101034(){'+best.get('body','')+'}\n'
      js=js[:best['start']]+helper+js[best['start']:]
      action='await syncManualLegacy101034()'
else:
    server=server[:best['start']]+marker+server[best['end']:]
    if best['kind']!='named' or not manual_name:
      raise RuntimeError('Polling do servidor e inline; publicacao bloqueada para nao criar rota manual insegura.')
    route=f'''\n// 10.10.34 - sincronizacao manual. Sem polling automatico para reduzir egress do Supabase.\napp.post("/api/sync-manual-101034",auth,async (_req,res)=>{{\n  try{{await Promise.resolve({manual_name}());res.json({{ok:true}})}}\n  catch(error){{console.error('[sync manual 10.10.34]',error);res.status(500).json({{erro:'Nao foi possivel sincronizar agora.'}})}}\n}});\n'''
    pos=server.rfind('app.listen(')
    if pos<0: raise RuntimeError('Ponto app.listen nao encontrado para rota de sincronizacao manual.')
    server=server[:pos]+route+server[pos:]
    action="const r=await api('/api/sync-manual-101034',{method:'POST'});if(!r.ok){const d=await r.json().catch(()=>({}));throw new Error(d.erro||'Falha ao sincronizar.')}"

js += f'''\n\n// SYNC_MANUAL_101034 - sem polling em segundo plano.\nlet syncManualBusy101034=false;\nfunction instalarSyncManual101034(){{\n if(document.querySelector('#manualCloudSync101034'))return;\n const button=document.createElement('button');button.type='button';button.id='manualCloudSync101034';button.className='manual-sync-101034';button.innerHTML='<span>↻</span><b>Sincronizar agora</b><small>somente quando você clicar</small>';\n const candidates=[...document.querySelectorAll('div,span,p,small,button')];\n const status=candidates.find(el=>/sincronizando\\s+online|sincroniza.*online/i.test((el.textContent||'').trim()));\n if(status&&status!==document.body){{status.replaceWith(button)}}else{{document.body.appendChild(button)}}\n button.onclick=async()=>{{\n   if(syncManualBusy101034)return;syncManualBusy101034=true;button.disabled=true;button.classList.add('is-syncing');button.querySelector('b').textContent='Sincronizando...';button.querySelector('small').textContent='aguarde um instante';\n   try{{{action};button.querySelector('b').textContent='Sincronizado';button.querySelector('small').textContent='dados atualizados';toast('Sincronização concluída.');setTimeout(()=>location.reload(),500)}}\n   catch(e){{console.error('[sync manual 101034]',e);button.querySelector('b').textContent='Tentar sincronizar';button.querySelector('small').textContent='não foi possível concluir';toast(e?.message||'Erro ao sincronizar.')}}\n   finally{{setTimeout(()=>{{syncManualBusy101034=false;button.disabled=false;button.classList.remove('is-syncing');if(button.querySelector('b')?.textContent==='Sincronizado'){{button.querySelector('b').textContent='Sincronizar agora';button.querySelector('small').textContent='somente quando você clicar'}}}},1500)}}\n }};\n}}\ndocument.addEventListener('DOMContentLoaded',instalarSyncManual101034);setTimeout(instalarSyncManual101034,400);\n'''

css=read('public/style.css')
css += r'''\n/* 10.10.34 - botão de sincronização manual / economia de dados */\n.manual-sync-101034{position:fixed;right:18px;bottom:18px;z-index:9998;display:grid;grid-template-columns:28px auto;grid-template-rows:auto auto;column-gap:9px;align-items:center;min-width:190px;padding:10px 13px;border:1px solid var(--border);border-radius:12px;background:var(--card-bg);color:var(--text);box-shadow:0 10px 30px rgba(0,0,0,.14);cursor:pointer;text-align:left}.manual-sync-101034>span{grid-row:1/3;font-size:22px;line-height:1}.manual-sync-101034>b{font-size:12px}.manual-sync-101034>small{font-size:10px;color:var(--muted)}.manual-sync-101034:hover{border-color:var(--primary)}.manual-sync-101034.is-syncing>span{animation:syncspin101034 .8s linear infinite}.manual-sync-101034:disabled{opacity:.72;cursor:wait}@keyframes syncspin101034{to{transform:rotate(360deg)}}@media(max-width:700px){.manual-sync-101034{right:10px;bottom:10px;min-width:170px}}\n'''
write('public/app.js',js);write('src/server.ts',server);write('public/style.css',css)
report={'version':'10.10.34','mode':manual_mode,'callback':manual_name,'old_interval_ms':best['delay'],'score':best['score'],'candidates':len(allc)}
write('.sync-manual-101034.json',json.dumps(report,indent=2))
print('10.10.34: polling automatico removido; sincronizacao agora e manual.',report)
