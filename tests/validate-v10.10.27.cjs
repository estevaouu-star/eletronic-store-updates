const fs = require('fs');
const path = require('path');
const {spawn} = require('child_process');

const dataDir = fs.mkdtempSync(path.join(__dirname, 'eletromix-101027-'));
fs.writeFileSync(path.join(dataDir, 'cloud.json'), JSON.stringify({enabled:false,url:'',publishableKey:'',syncId:'test',secret:'',pollSeconds:60}));
const port = 31343;
const base = `http://127.0.0.1:${port}`;
const server = spawn(process.execPath, ['dist/server.js'], {
  cwd: path.resolve(__dirname, '../app'),
  env: {...process.env, ELECTRON_STORE_DATA_DIR: dataDir, ELECTRON_STORE_PORT: String(port)},
  stdio: ['ignore', 'pipe', 'pipe']
});
server.stdout.on('data', data => process.stdout.write(data));
server.stderr.on('data', data => process.stderr.write(data));

const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
async function waitServer(){
  for(let i=0;i<80;i++){
    try{const response=await fetch(base);if(response.ok)return}catch{}
    await sleep(100);
  }
  throw new Error('Servidor não iniciou.');
}
async function request(url, options={}, expected=200){
  const response=await fetch(base+url,options);
  const body=await response.json().catch(()=>({}));
  if(response.status!==expected)throw new Error(`${url}: esperado ${expected}, recebido ${response.status} ${JSON.stringify(body)}`);
  return body;
}

(async()=>{
  try{
    await waitServer();
    const login=await request('/api/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({login:'admin',senha:'admin123'})});
    const headers={Authorization:`Bearer ${login.token}`,'Content-Type':'application/json','X-Store-Id':'1'};
    const imageUrl='https://eletromix-mobile.estevaouu.chatgpt.site/assets/produto-teste.jpg';
    const created=await request('/api/produtos',{method:'POST',headers,body:JSON.stringify({codigo:'IMG-101027',nome:'Produto com imagem',categoria:'Teste',marca:'Eletromix',imagemUrl,precoCusto:10,precoVenda:20,estoque:1})},201);
    if(created.imagemUrl!==imageUrl)throw new Error('Imagem não foi salva no cadastro do produto.');
    const updatedUrl='https://eletromix-mobile.estevaouu.chatgpt.site/assets/produto-atualizado.jpg';
    const updated=await request(`/api/produtos/${created.id}`,{method:'PUT',headers,body:JSON.stringify({imagemUrl:updatedUrl})});
    if(updated.imagemUrl!==updatedUrl)throw new Error('Imagem não foi atualizada.');
    const products=await request('/api/produtos',{headers});
    if(products.find(product=>product.id===created.id)?.imagemUrl!==updatedUrl)throw new Error('Imagem não voltou na consulta de produtos.');
    await request(`/api/produtos/${created.id}`,{method:'PUT',headers,body:JSON.stringify({imagemUrl:'javascript:alert(1)'})},400);
    console.log('PASS v10.10.27: imagem salva, consultada e endereço inseguro bloqueado.');
  } finally {
    server.kill();
  }
})().catch(error=>{console.error(error);server.kill();process.exitCode=1});
