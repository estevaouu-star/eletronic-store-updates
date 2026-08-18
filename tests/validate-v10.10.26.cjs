const fs = require('fs');
const path = require('path');
const {spawn} = require('child_process');

const dataDir = fs.mkdtempSync(path.join(__dirname, 'eletromix-101026-'));
const port = 31342;
const base = `http://127.0.0.1:${port}`;
const server = spawn(process.execPath, ['dist/server.js'], {
  cwd: path.resolve(__dirname, '../app'),
  env: {...process.env, ELECTRON_STORE_DATA_DIR: dataDir, ELECTRON_STORE_PORT: String(port)},
  stdio: ['ignore', 'pipe', 'pipe']
});
server.stdout.on('data', d => process.stdout.write(d));
server.stderr.on('data', d => process.stderr.write(d));

const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
async function waitServer(){
  for(let i=0;i<80;i++){
    try{const r=await fetch(base);if(r.ok)return}catch{}
    await sleep(100);
  }
  throw new Error('Servidor não iniciou.');
}
async function request(url, opt={}, expected=200){
  const r=await fetch(base+url,opt);
  const body=await r.json().catch(()=>({}));
  if(r.status!==expected)throw new Error(`${url}: esperado ${expected}, recebido ${r.status} ${JSON.stringify(body)}`);
  return body;
}
const headers = token => ({Authorization:`Bearer ${token}`,'Content-Type':'application/json','X-Store-Id':'1'});

(async()=>{
  try{
    await waitServer();
    const root=await request('/api/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({login:'admin',senha:'admin123'})});
    const rootHeaders=headers(root.token);
    const cachoeiro=await request('/api/lojas',{method:'POST',headers:rootHeaders,body:JSON.stringify({nome:'Cachoeiro'})},201);
    const guaratiba=await request('/api/lojas',{method:'POST',headers:rootHeaders,body:JSON.stringify({nome:'Guaratiba'})},201);
    const scoped=await request('/api/usuarios',{method:'POST',headers:rootHeaders,body:JSON.stringify({nome:'ADM Cachoeiro',login:'adm-cachoeiro',senha:'senha-segura',cargo:'admin',lojaIds:[cachoeiro.id],acessoTodasLojas:false})},201);
    if(scoped.acessoTodasLojas||scoped.lojaIds.join(',')!==String(cachoeiro.id))throw new Error('Escopo inicial do administrador incorreto.');

    const loginScoped=await request('/api/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({login:'adm-cachoeiro',senha:'senha-segura'})});
    const scopedHeaders={...headers(loginScoped.token),'X-Store-Id':String(cachoeiro.id)};
    const shops=await request('/api/lojas',{headers:scopedHeaders});
    if(shops.length!==1||shops[0].id!==cachoeiro.id)throw new Error('Administrador restrito visualizou outra loja.');
    const visibleUsers=await request('/api/usuarios',{headers:scopedHeaders});
    if(visibleUsers.some(u=>u.id===root.usuario.id))throw new Error('Administrador restrito visualizou outro administrador.');

    await request(`/api/usuarios/${root.usuario.id}`,{method:'PUT',headers:scopedHeaders,body:JSON.stringify({nome:'Tentativa'})},403);
    const self=await request(`/api/usuarios/${scoped.id}`,{method:'PUT',headers:scopedHeaders,body:JSON.stringify({nome:'ADM Cachoeiro 2',lojaIds:[guaratiba.id],acessoTodasLojas:true})});
    if(self.acessoTodasLojas||self.lojaIds.join(',')!==String(cachoeiro.id))throw new Error('Administrador conseguiu aumentar o próprio acesso.');
    await request('/api/usuarios',{method:'POST',headers:scopedHeaders,body:JSON.stringify({nome:'Invasão',login:'fora',senha:'senha',cargo:'vendedor',lojaIds:[guaratiba.id]})},403);
    await request('/api/usuarios',{method:'POST',headers:scopedHeaders,body:JSON.stringify({nome:'Vendedor local',login:'local',senha:'senha',cargo:'vendedor',lojaIds:[cachoeiro.id]})},201);
    await request(`/api/usuarios/${scoped.id}`,{method:'PUT',headers:rootHeaders,body:JSON.stringify({nome:'Alteração indevida'})},403);
    await request('/api/lojas',{method:'POST',headers:scopedHeaders,body:JSON.stringify({nome:'Loja indevida'})},403);
    await request('/api/backup',{headers:scopedHeaders},403);
    await request('/api/email/preparar-relatorio',{method:'POST',headers:scopedHeaders,body:JSON.stringify({email:'teste@example.com',tipo:'dia',lojaId:String(guaratiba.id)})},400);
    const consolidated=await request('/api/relatorios/consolidado',{headers:scopedHeaders});
    if(consolidated.lojas.length!==1||consolidated.lojas[0].loja.id!==cachoeiro.id)throw new Error('Relatório consolidado vazou outra loja.');
    console.log('PASS v10.10.26: escopo de lojas e isolamento entre administradores.');
  }finally{
    server.kill();
  }
})().catch(error=>{console.error(error);server.kill();process.exitCode=1});
