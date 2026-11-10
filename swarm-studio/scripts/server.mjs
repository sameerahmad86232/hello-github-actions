import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { ROOT, WORKSPACE, CONFIG, appendEvent, ownerOf, readEvents, safeWorkspacePath } from './shared.mjs';

const PORT=Number(process.env.PORT||4173), HOST=process.env.HOST||'127.0.0.1';
const clients=new Set();
const MIME={'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.css':'text/css; charset=utf-8','.json':'application/json; charset=utf-8','.svg':'image/svg+xml','.png':'image/png','.jpg':'image/jpeg','.webp':'image/webp'};
const htmlEscape=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function file(pathname){try{return fs.readFileSync(safeWorkspacePath(pathname),'utf8')}catch{return ''}}
function emitLive(evt){for(const r of clients){try{r.write(`data: ${JSON.stringify(evt)}\n\n`)}catch{clients.delete(r)}}}
function record(evt){const e=appendEvent(evt);emitLive(e);return e}
function buildPreview(){
  const exists=fs.existsSync(safeWorkspacePath('site/index.html'));
  if(exists)return fs.readFileSync(safeWorkspacePath('site/index.html'));
  const fragments=['nav','hero','main','closing','footer'].map(k=>file('site/sections/'+k+'.html')).filter(Boolean);
  if(!fragments.length)return `<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Awaiting actual build</title><style>body{font:16px system-ui;background:#f1f5f9;color:#1e293b;margin:0;padding:32px}.waiting{border:2px dashed #cbd5e1;border-radius:20px;padding:38px;max-width:500px;margin:5vh auto}h1{font-size:1.5rem}</style><div class="waiting"><h1>No site sections written yet</h1><p>Start your coding agents. The preview will rebuild when real section files appear.</p></div></html>`;
  let name='Preview in progress';try{name=JSON.parse(file('PROJECT.json')).name||name}catch{}
  return `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${htmlEscape(name)}</title><link rel="stylesheet" href="/site/tokens.css"><link rel="stylesheet" href="/site/layout.css"><link rel="stylesheet" href="/site/theme.css"><link rel="stylesheet" href="/site/motion.css"></head><body>${fragments.join('\n')}<script src="/site/app.js" defer></script></body></html>`;
}
function send(res,code,body,type='application/json; charset=utf-8'){
  res.writeHead(code,{'Content-Type':type,'Cache-Control':'no-store','X-Content-Type-Options':'nosniff','X-Frame-Options':'SAMEORIGIN'});res.end(body);
}
function resource(res,base,relative){
  let full=path.resolve(base,relative);
  if(!(full===base || full.startsWith(base+path.sep)))return send(res,403,'Forbidden','text/plain');
  try{const stat=fs.statSync(full);if(!stat.isFile())return send(res,404,'Not found','text/plain');const ext=path.extname(full).toLowerCase();res.writeHead(200,{'Content-Type':MIME[ext]||'application/octet-stream','Cache-Control':'no-store','X-Content-Type-Options':'nosniff'});fs.createReadStream(full).pipe(res);}catch{return send(res,404,'Not found','text/plain')}
}
function state(){
 const events=readEvents(),active=new Set(), statuses={};let peak=0;
 for(const e of events){if(e.type==='start'){active.add(e.agent);statuses[e.agent]='working'}if(e.type==='done'||e.type==='error'){active.delete(e.agent);statuses[e.agent]=e.type==='done'?'done':'error'}peak=Math.max(peak,active.size)}
 const now=Date.now(),files=events.filter(e=>e.type==='file');
 return {agents:CONFIG.roles,teams:CONFIG.teams,waves:CONFIG.waves,events,metrics:{live:active.size,changes:files.length,opsPerSecond:files.filter(e=>now-Date.parse(e.at)<1000).length,elapsedMs:events.length?now-Date.parse(events[0].at):0,peakParallel:peak},statuses};
}
const server=http.createServer(async(req,res)=>{
 let pathname;try{pathname=decodeURIComponent(new URL(req.url,`http://${req.headers.host||'localhost'}`).pathname)}catch{return send(res,400,'Bad URL','text/plain')}
 if(req.method==='GET' && pathname==='/api/state')return send(res,200,JSON.stringify(state()));
 if(req.method==='GET' && pathname==='/api/events'){
  res.writeHead(200,{'Content-Type':'text/event-stream','Cache-Control':'no-store','Connection':'keep-alive','X-Accel-Buffering':'no'});res.write(': connected\n\n');clients.add(res);req.on('close',()=>clients.delete(res));return;
 }
 if(req.method==='POST' && pathname==='/api/emit'){
  const origin=req.headers.origin;if(origin && new URL(origin).host!==req.headers.host)return send(res,403,JSON.stringify({error:'Origin not allowed'}));
  if(req.headers['content-type']?.split(';')[0]!=='application/json')return send(res,415,JSON.stringify({error:'JSON only'}));
  let input='';for await(const c of req){input+=c;if(input.length>5000)return send(res,413,JSON.stringify({error:'Too large'}));}
  try{const payload=JSON.parse(input);if(!['start','log','done','error','place','move'].includes(payload.type))throw Error('Not an agent event');const e=record(payload);return send(res,200,JSON.stringify(e));}catch(e){return send(res,400,JSON.stringify({error:e.message}));}
 }
 if(req.method==='GET' && (pathname==='/preview/'||pathname==='/preview'))return send(res,200,buildPreview(),'text/html; charset=utf-8');
 if(req.method==='GET' && pathname.startsWith('/site/'))return resource(res,path.join(WORKSPACE,'site'),pathname.slice(6));
 if(req.method==='GET' && (pathname==='/'||pathname==='/index.html'))return resource(res,path.join(ROOT,'studio'),'index.html');
 if(req.method==='GET' && pathname.startsWith('/studio/'))return resource(res,path.join(ROOT,'studio'),pathname.slice(8));
 return send(res,404,'Not found','text/plain');
});

let previous=new Map();
function walk(dir,rel='site'){
 const current=new Map();if(!fs.existsSync(dir))return current;
 for(const ent of fs.readdirSync(dir,{withFileTypes:true})){
  const relative=`${rel}/${ent.name}`,p=path.join(dir,ent.name);
  if(ent.isSymbolicLink())continue;
  if(ent.isDirectory()){for(const [k,v] of walk(p,relative))current.set(k,v)}
  else if(ent.isFile()){const s=fs.statSync(p);current.set(relative,`${s.size}:${s.mtimeMs}`)}
 }
 return current;
}
function scan(){const files=walk(path.join(WORKSPACE,'site'));for(const [f,sig] of files){if(previous.get(f)!==sig){const owner=ownerOf(f);record({agent:'filesystem',type:'file',file:f,text:`${owner?`${owner}'s owned path`:'Unassigned path'} changed: ${f}`});}}previous=files;}
previous=walk(path.join(WORKSPACE,'site'));setInterval(scan,900).unref();
server.listen(PORT,HOST,()=>console.log(`Swarm Studio listening at http://${HOST}:${PORT} (workspace ${WORKSPACE})`));
