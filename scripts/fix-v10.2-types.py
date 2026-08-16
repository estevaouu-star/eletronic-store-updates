from pathlib import Path
p=Path('app/src/server.ts')
s=p.read_text(encoding='utf-8')
s=s.replace('let pagamentosVenda:{forma:string;valor:number}[]=[];','let pagamentosVenda:{forma:string;valor:number;recebido?:number}[]=[];',1)
p.write_text(s,encoding='utf-8')
print('Tipos de pagamento 10.2 corrigidos.')
