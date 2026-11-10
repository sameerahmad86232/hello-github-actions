import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

export const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
export const WORKSPACE = path.resolve(process.env.SWARM_WORKSPACE || path.join(ROOT,'workspace'));
export const CONFIG = JSON.parse(fs.readFileSync(path.join(ROOT,'config/roles.json'),'utf8'));
export const ROLE_IDS = new Set(CONFIG.roles.map(r=>r.id));
export const EVENT_TYPES = new Set(['start','log','done','error','place','file','move']);
export function ownerOf(relativePath){
  const p=relativePath.replaceAll('\\','/');
  return CONFIG.roles.find(role=>role.writes.some(x=>x.endsWith('/')?p.startsWith(x):p===x))?.id ?? null;
}
export function safeWorkspacePath(relative){
  if(typeof relative !== 'string' || relative.includes('\0')) throw new Error('Invalid path');
  const abs=path.resolve(WORKSPACE,relative);
  if(abs !== WORKSPACE && !abs.startsWith(WORKSPACE+path.sep))throw new Error('Path outside workspace');
  return abs;
}
export function appendEvent({agent,type,text='',file=null,lane=null,x=null,ms=null}){
  if(!ROLE_IDS.has(agent) && agent!=='head-coach' && agent!=='filesystem')throw new Error('Unknown agent');
  if(!EVENT_TYPES.has(type))throw new Error('Unknown event type');
  if(file!==null){safeWorkspacePath(file);if(type==='place' && !fs.existsSync(safeWorkspacePath(file)))throw new Error('File does not exist; cannot claim placement');}
  fs.mkdirSync(WORKSPACE,{recursive:true});
  const obj={id:`${Date.now()}-${Math.random().toString(36).slice(2,10)}`,at:new Date().toISOString(),agent,type,text:String(text).slice(0,280),file,lane,x,ms};
  fs.appendFileSync(path.join(WORKSPACE,'events.jsonl'),JSON.stringify(obj)+'\n');
  return obj;
}
export function readEvents(limit=500){
  try{return fs.readFileSync(path.join(WORKSPACE,'events.jsonl'),'utf8').split('\n').filter(Boolean).slice(-limit).map(x=>{try{return JSON.parse(x)}catch{return null}}).filter(Boolean)}catch{return []}
}
