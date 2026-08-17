from pathlib import Path

p=Path('app/src/server.ts')
s=p.read_text(encoding='utf-8')
old='app.get("/api/usuarios",auth,admin,(_req,res)=>res.json(db.usuarios.map(({senhaHash,...u})=>({...u,lojaIds:idsLojasPermitidas(u)}))));'
new='''app.get("/api/usuarios",auth,admin,(_req,res)=>res.json(db.usuarios.map(u=>{\n  const {senhaHash,...safe}=u;\n  return {...safe,lojaIds:idsLojasPermitidas(u)};\n})));'''
if old not in s:
    raise RuntimeError('Trecho de usuários 10.8.4 não encontrado para correção de tipagem')
s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')
print('Tipagem 10.8.4 corrigida: usuário completo é usado ao calcular lojas permitidas.')
