import {spawn} from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

const port=32147;
const base=`http://127.0.0.1:${port}`;
const dataDir=path.join(os.tmpdir(),`eletromix-store-access-${Date.now()}`);
fs.rmSync(dataDir,{recursive:true,force:true});

const server=spawn(process.execPath,[path.resolve('app/dist/server.js')],{
  env:{...process.env,ELECTRON_STORE_PORT:String(port),ELECTRON_STORE_DATA_DIR:dataDir},
  stdio:['ignore','pipe','pipe'],windowsHide:true
});
let serverLog='';
server.stdout.on('data',d=>serverLog+=d.toString());
server.stderr.on('data',d=>serverLog+=d.toString());
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
async function json(url,opt={}){
  const r=await fetch(url,opt);let d={};try{d=await r.json()}catch{}
  return {r,d};
}
const headers=(token)=>({'Content-Type':'application/json',...(token?{Authorization:`Bearer ${token}`}:{})});
function assert(cond,msg){if(!cond)throw new Error(msg)}
try{
  await sleep(1800);
  let x=await json(`${base}/api/login`,{method:'POST',headers:headers(),body:JSON.stringify({login:'admin',senha:'admin123'})});
  assert(x.r.ok&&x.d.token,'ADM não conseguiu entrar');
  const adminToken=x.d.token;

  x=await json(`${base}/api/lojas`,{method:'POST',headers:headers(adminToken),body:JSON.stringify({nome:'Loja Dutra'})});
  assert(x.r.ok&&x.d.id,'Falha ao criar Loja Dutra');const dutra=x.d;
  x=await json(`${base}/api/lojas`,{method:'POST',headers:headers(adminToken),body:JSON.stringify({nome:'Loja Centro'})});
  assert(x.r.ok&&x.d.id,'Falha ao criar Loja Centro');const centro=x.d;

  x=await json(`${base}/api/usuarios`,{method:'POST',headers:headers(adminToken),body:JSON.stringify({nome:'Usuário Dutra',login:'dutra',senha:'teste123',cargo:'vendedor',lojaIds:[dutra.id]})});
  assert(x.r.ok&&Array.isArray(x.d.lojaIds)&&x.d.lojaIds.length===1&&x.d.lojaIds[0]===dutra.id,'Permissão de uma loja não foi salva');

  x=await json(`${base}/api/login`,{method:'POST',headers:headers(),body:JSON.stringify({login:'dutra',senha:'teste123'})});
  assert(x.r.ok&&x.d.token,'Usuário Dutra não conseguiu entrar');const dutraToken=x.d.token;
  x=await json(`${base}/api/lojas`,{headers:{Authorization:`Bearer ${dutraToken}`}});
  assert(x.r.ok&&Array.isArray(x.d)&&x.d.length===1&&x.d[0].id===dutra.id,'Usuário Dutra enxergou loja não autorizada');
  x=await json(`${base}/api/usuarios`,{headers:{Authorization:`Bearer ${dutraToken}`}});
  assert(x.r.status===403,'Vendedor conseguiu acessar gestão de logins');
  x=await json(`${base}/api/me`,{headers:{Authorization:`Bearer ${dutraToken}`,'X-Store-Id':String(centro.id)}});
  assert(x.r.ok&&Array.isArray(x.d.lojaIds)&&x.d.lojaIds.length===1&&x.d.lojaIds[0]===dutra.id,'Pedido de loja não autorizada alterou a permissão do usuário');

  x=await json(`${base}/api/usuarios`,{method:'POST',headers:headers(adminToken),body:JSON.stringify({nome:'Usuário Multi',login:'multi',senha:'teste123',cargo:'vendedor',lojaIds:[dutra.id,centro.id]})});
  assert(x.r.ok&&x.d.lojaIds?.length===2,'Permissão de múltiplas lojas não foi salva');
  x=await json(`${base}/api/login`,{method:'POST',headers:headers(),body:JSON.stringify({login:'multi',senha:'teste123'})});
  assert(x.r.ok&&x.d.token,'Usuário multi não conseguiu entrar');
  const multiToken=x.d.token;
  x=await json(`${base}/api/lojas`,{headers:{Authorization:`Bearer ${multiToken}`}});
  assert(x.r.ok&&Array.isArray(x.d)&&x.d.length===2&&x.d.some(l=>l.id===dutra.id)&&x.d.some(l=>l.id===centro.id),'Usuário multi não recebeu exatamente as lojas permitidas');

  x=await json(`${base}/api/usuarios/1`,{method:'PUT',headers:headers(adminToken),body:JSON.stringify({login:'admin-geral',nome:'Administrador Geral',cargo:'admin',ativo:true,lojaIds:[]})});
  assert(x.r.ok&&x.d.login==='admin-geral','ADM não conseguiu alterar o próprio login');
  x=await json(`${base}/api/usuarios`,{headers:{Authorization:`Bearer ${adminToken}`}});
  assert(x.r.ok,'Sessão do ADM deixou de funcionar após editar o próprio login');

  console.log('TESTE 10.8.4 OK: ADM-only, uma loja, múltiplas lojas e edição do próprio ADM validados.');
} catch(e){
  console.error(serverLog);
  console.error(e?.stack||e);
  process.exitCode=1;
} finally {
  server.kill();
  fs.rmSync(dataDir,{recursive:true,force:true});
}
