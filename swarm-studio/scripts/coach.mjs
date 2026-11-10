import fs from 'node:fs';
import path from 'node:path';
import { CONFIG, ROOT, WORKSPACE, appendEvent } from './shared.mjs';
function arg(k,fallback=''){const i=process.argv.indexOf('--'+k);return i===-1?fallback:process.argv[i+1]??fallback;}
function writeOnce(file,contents){const p=path.join(WORKSPACE,file);fs.mkdirSync(path.dirname(p),{recursive:true});if(fs.existsSync(p))throw new Error(`Refusing to overwrite ${file}`);fs.writeFileSync(p,contents,'utf8');}
function clean(v){return String(v).replace(/[\r\n]/g,' ').trim().slice(0,220)}
function init(){
  if(fs.existsSync(path.join(WORKSPACE,'PROJECT.json')))throw new Error('Workspace already initialized. Use a new SWARM_WORKSPACE for another project.');
  const name=clean(arg('name')),audience=clean(arg('audience')),cta=clean(arg('cta'));
  if(!name||!audience||!cta)throw new Error('Required: --name "..." --audience "..." --cta "..."');
  const goal=clean(arg('goal',`Help ${audience} use ${name}.`));
  const pages=arg('pages','Home,Features,FAQ').split(',').map(clean).filter(Boolean).slice(0,12);
  const cssColor=/^#[a-f0-9]{6}$/i;
  const colors=arg('colors','#152a42,#f5f9fc').split(',').map(clean).filter(v=>cssColor.test(v)).slice(0,2);
  if(colors.length<2)throw new Error('Provide two hex colors like --colors "#152a42,#f5f9fc"');
  const project={name,audience,cta,goal,pages,colors,stack:'static HTML / CSS / vanilla JS',created:new Date().toISOString()};
  writeOnce('PROJECT.json',JSON.stringify(project,null,2)+'\n');
  writeOnce('BRIEF.md',`# ${name} — Shared brief\n\nAudience: ${audience}\nGoal: ${goal}\nSingle primary action: ${cta}\nPages/sections: ${pages.join(', ')}\nStack: ${project.stack}\nRules: Original assets, truthful copy, mobile-first responsive output.\n\n_Head Coach bootstrap; strategist owns later refinements._\n`);
  const ownership=CONFIG.roles.flatMap(r=>r.writes.map(p=>`| \`${p}\` | ${r.id} | ${r.reviewOnly?'Report only':'Source owner'} |`));
  writeOnce('OWNERSHIP.md',`# File ownership contract\n\nAll paths are relative to this workspace. Exactly one permanent owner per path. A trailing slash grants ownership of descendants. Only Head Coach may bootstrap existing BRIEF.md, tokens.css and content.json before Wave 1; afterward, their specified owner controls edits.\n\n| Path | Owner | Type |\n|---|---|---|\n${ownership.join('\n')}\n`);
  writeOnce('site/tokens.css',`:root {\n  --brand: ${colors[0]};\n  --canvas: ${colors[1]};\n  --ink: ${colors[0]};\n  --surface: ${colors[1]};\n  --accent: ${colors[0]};\n  --space-1: .5rem; --space-2: 1rem; --space-3: 1.5rem; --space-4: 2rem; --space-5: 4rem;\n  --radius: 1rem; --content-width: 72rem;\n  --font-body: system-ui, sans-serif; --font-display: system-ui, sans-serif;\n}\nbody { margin: 0; font-family: var(--font-body); color: var(--ink); background: var(--canvas); }\n`);
  writeOnce('site/content.json',JSON.stringify({brand:name,audience,hero:{eyebrow:name,heading:goal,body:`Designed for ${audience}.`,cta},pages},null,2)+'\n');
  const teams=Object.fromEntries(CONFIG.teams.map(t=>[t.id,t.name]));
  for(const role of CONFIG.roles){
    const src=fs.readFileSync(path.join(ROOT,'agents',role.id+'.md'),'utf8');
    writeOnce('tasks/'+role.id+'.md',src+`\n## Project context\nRead \`PROJECT.json\`, \`BRIEF.md\` and \`OWNERSHIP.md\`. Work within this workspace only.\n\n## Deliverable\nReturn a report signed \`${role.id}\` in at most five lines.\n`);
  }
  appendEvent({agent:'head-coach',type:'log',text:`Initialized ${name} contracts and 20 role tasks (not started)`});
  console.log(`Created workspace at ${WORKSPACE}; 20 role tasks ready. No agents have been run.`);
}
try{switch(process.argv[2]){case 'init':init();break;case 'roles':console.log(CONFIG.roles.map(r=>`${r.id} [${r.team}] ${r.writes.join(', ')}`).join('\n'));break;default:console.log('Commands: init --name ... --audience ... --cta ... [--goal ...] [--pages ...] [--colors "#123456,#ffffff"], roles');}}catch(e){console.error(e.message);process.exitCode=1;}
