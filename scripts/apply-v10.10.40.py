from pathlib import Path
import json
root=Path('app')
def read(p): return (root/p).read_text(encoding='utf-8')
def write(p,s): (root/p).write_text(s,encoding='utf-8')
def replace1(s,a,b,label):
    if a not in s: raise RuntimeError(f'Trecho nao encontrado: {label}')
    return s.replace(a,b,1)

pkg=json.loads(read('package.json'));pkg['version']='10.10.40';write('package.json',json.dumps(pkg,indent=2,ensure_ascii=False))
html=read('public/index.html');html=replace1(html,'id="versionInfo" class="version-info">v10.10.39','id="versionInfo" class="version-info">v10.10.40','versao');write('public/index.html',html)
js=read('public/app.js');js=replace1(js,'const atual="10.10.39"','const atual="10.10.40"','atualizador')

old='''${!osFinalizada101036(o)?`<button type="button" class="danger os-delete-101039" data-delete-os-101039="${o.id}">Excluir OS</button>`:''}'''
new='''<button type="button" class="danger os-delete-101039" data-delete-os-101039="${o.id}">Excluir OS</button>'''
js=replace1(js,old,new,'exclusao disponivel em OS finalizada')

old_guard=""" if(o.status==='Finalizado')return toast('OS finalizada fica protegida no histórico e não pode ser excluída.');
 if(!confirm(`Excluir definitivamente a OS #${o.id} de ${o.clienteNome}?`))return;"""
new_guard=""" const aviso=o.status==='Finalizado'?`ATENÇÃO: a OS #${o.id} está FINALIZADA. Ao excluir, ela será removida definitivamente do histórico. Deseja continuar?`:`Excluir definitivamente a OS #${o.id} de ${o.clienteNome}?`;
 if(!confirm(aviso))return;"""
js=replace1(js,old_guard,new_guard,'confirmacao de exclusao finalizada')

write('public/app.js',js)
print('10.10.40: permite excluir qualquer OS, inclusive Finalizado, com confirmação reforçada para histórico finalizado.')
