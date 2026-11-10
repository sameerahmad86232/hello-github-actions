import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { CONFIG, ROOT, ownerOf } from '../scripts/shared.mjs';

test('all 20 specialist roles have one unique id and one team',()=>{
 assert.equal(CONFIG.roles.length,20);
 assert.equal(new Set(CONFIG.roles.map(x=>x.id)).size,20);
 for(const a of CONFIG.roles) assert.ok(CONFIG.teams.some(t=>t.id===a.team));
});
test('all owned paths are unique and specialist prompts have mandatory opening',()=>{
 const paths=CONFIG.roles.flatMap(x=>x.writes);
 assert.equal(paths.length,new Set(paths).size);
 for(const r of CONFIG.roles){const p=fs.readFileSync(path.join(ROOT,'agents',r.id+'.md'),'utf8');const team=CONFIG.teams.find(t=>t.id===r.team).name;assert.ok(p.startsWith(`You are ${r.id}, ${team} team.`));}
});
test('all agents are assigned to one of five waves',()=>{
 assert.equal(CONFIG.waves.length,5);
 const ids=CONFIG.waves.flatMap(x=>x.agents);
 assert.equal(ids.length,20);
 assert.equal(new Set(ids).size,20);
});
test('ownership resolves nav-footer and imagery paths',()=>{
 assert.equal(ownerOf('site/sections/footer.html'),'nav-footer');
 assert.equal(ownerOf('site/assets/original.svg'),'imagery');
 assert.equal(ownerOf('site/sections/hero.html'),'hero');
});
test('coach creates four shared contract files and refuses overwrite',()=>{
 const dir=fs.mkdtempSync(path.join(os.tmpdir(),'swarm-test-'));
 try{
  const args=['scripts/coach.mjs','init','--name','Example','--audience','Readers','--cta','Learn more'];
  const first=spawnSync(process.execPath,args,{cwd:ROOT,env:{...process.env,SWARM_WORKSPACE:dir},encoding:'utf8'});
  assert.equal(first.status,0,first.stderr);
  for(const p of ['BRIEF.md','OWNERSHIP.md','site/tokens.css','site/content.json','tasks/hero.md'])assert.ok(fs.existsSync(path.join(dir,p)),p);
  const second=spawnSync(process.execPath,args,{cwd:ROOT,env:{...process.env,SWARM_WORKSPACE:dir},encoding:'utf8'});
  assert.notEqual(second.status,0);
 }finally{fs.rmSync(dir,{recursive:true,force:true})}
});
