from pathlib import Path
import json

root=Path('app')
def read(p): return (root/p).read_text(encoding='utf-8')
def write(p,s): (root/p).write_text(s,encoding='utf-8')
def replace1(s,a,b,label):
    if a not in s: raise RuntimeError(f'Trecho nao encontrado: {label}')
    return s.replace(a,b,1)

pkg=json.loads(read('package.json'));pkg['version']='10.10.35';write('package.json',json.dumps(pkg,indent=2,ensure_ascii=False))
html=read('public/index.html');html=replace1(html,'id="versionInfo" class="version-info">v10.10.34','id="versionInfo" class="version-info">v10.10.35','versao');write('public/index.html',html)
js=read('public/app.js');js=replace1(js,'const atual="10.10.34"','const atual="10.10.35"','atualizador')

old=""" const nota=garantia?'Garantia de 3 meses contada a partir do momento em que o serviço foi marcado como pronto. A retirada ou o pagamento posterior não alteram estas datas.':loja?'Arquive esta via na loja e confira o número da OS e o aparelho com a via do cliente no momento da retirada.':'Guarde esta via e apresente-a para conferir e retirar o aparelho.';\n const assinatura=garantia?'Assinatura do funcionário':loja?'Conferência da loja / cliente':'Assinatura do cliente';"""
new=""" const nota=garantia?'Garantia de 3 meses contada a partir do momento em que o serviço foi marcado como pronto. A retirada ou o pagamento posterior não alteram estas datas.':loja?'AUTORIZAÇÃO DO CLIENTE: Ao assinar esta via, o cliente declara que autoriza a execução do serviço descrito nesta Ordem de Serviço e está ciente de que, caso solicite a desistência após o início dos trabalhos, inclusive pedindo a desmontagem, reversão ou retorno do aparelho ao estado anterior, poderá ser cobrada taxa de mão de obra técnica correspondente a 50% do valor do serviço autorizado, quando aplicável e observada a legislação vigente. Arquive esta via na loja.':'Guarde esta via e apresente-a para conferir e retirar o aparelho.';\n const assinatura=garantia?'Assinatura do funcionário':loja?'Assinatura do cliente — autorização e ciência':'Assinatura do cliente';"""
js=replace1(js,old,new,'termo de autorizacao na via da loja')
write('public/app.js',js)
print('10.10.35: via da loja agora inclui autorização do cliente e ciência da taxa de mão de obra de 50% em caso de desistência após início do serviço.')
