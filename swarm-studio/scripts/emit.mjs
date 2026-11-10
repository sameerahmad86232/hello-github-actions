import { appendEvent, ROLE_IDS } from './shared.mjs';
function arg(k){const i=process.argv.indexOf('--'+k);return i<0?null:process.argv[i+1]??null;}
try{
  const agent=arg('agent'),type=arg('type'),text=arg('text')||'',file=arg('file');
  if(!agent || !type) throw new Error('Usage: node scripts/emit.mjs --agent hero --type start|log|done|error|place --text "message" [--file site/sections/hero.html]');
  if(!ROLE_IDS.has(agent) && agent!=='head-coach')throw new Error('Unknown role');
  const e=appendEvent({agent,type,text,file});console.log(`${e.agent}: ${e.type} ${e.text}`);
}catch(err){console.error(err.message);process.exitCode=1;}
