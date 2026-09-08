import {spawn} from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

const port=32148,base=`http://127.0.0.1:${port}`,dataDir=path.join(os.tmpdir(),`eletromix-role-101130-${Date.now()}`);
const server=spawn(process.execPath,[path.resolve('app/dist/server.js')],{env:{...process.env,ELECTRON_STORE_PORT:String(port),ELECTRON_STORE_DATA_DIR:dataDir},stdio:['ignore','pipe','pipe'],windowsHide:true});
let log='';server.stdout.on('data',d=>log+=d);server.stderr.on('data',d=>log+=d);
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const call=async(url,opt={})=>{const r=await fetch(base+url,opt);let d={};try{d=await r.json()}catch{}return{r,d}};
const headers=t=>({'Content-Type':'application/json',...(t?{Authorization:`Bearer ${t}`}:{})});
const ok=(v,m)=>{if(!v)throw new Error(m)};
try{
 await sleep(1600);
 let x=await call('/api/login',{method:'POST',headers:headers(),body:JSON.stringify({login:'admin',senha:'admin123'})});ok(x.r.ok,'admin não entrou');const a=x.d.token;
 x=await call('/api/lojas',{method:'POST',headers:headers(a),body:JSON.stringify({nome:'Loja Dois'})});ok(x.r.ok,'não criou segunda loja');const loja2=x.d.id;
 x=await call('/api/usuarios',{method:'POST',headers:headers(a),body:JSON.stringify({nome:'Vendedor Um',login:'vendedor1',senha:'teste123',cargo:'vendedor',lojaIds:[1,loja2]})});
 ok(x.r.ok&&x.d.lojaIds.length===1,'vendedor não foi limitado a uma loja');
 x=await call('/api/login',{method:'POST',headers:headers(),body:JSON.stringify({login:'vendedor1',senha:'teste123'})});ok(x.r.ok,'vendedor não entrou');const v=x.d.token;
 x=await call('/api/lojas',{headers:headers(v)});ok(x.r.ok&&x.d.length===1,'vendedor enxergou mais de uma loja');
 x=await call('/api/produtos',{headers:{...headers(v),'X-Store-Id':String(loja2)}});ok(x.r.ok,'vendedor não acessou função operacional');
 x=await call('/api/lojas',{headers:headers(a)});ok(x.r.ok&&x.d.length>=2,'admin não enxergou todas as lojas');
 console.log('TESTE 10.11.30 OK');
}catch(e){console.error(log);console.error(e);process.exitCode=1}finally{server.kill();fs.rmSync(dataDir,{recursive:true,force:true})}
