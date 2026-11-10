const $=s=>document.querySelector(s);
const state={roles:[],teams:[],events:[],statuses:{},metrics:{},selected:null};
const colorByTeam={};
function el(tag,cls,text){const e=document.createElement(tag);if(cls)e.className=cls;if(text!=null)e.textContent=text;return e}
function update(snapshot){state.roles=snapshot.agents||[];state.teams=snapshot.teams||[];state.events=snapshot.events||[];state.statuses=snapshot.statuses||{};state.metrics=snapshot.metrics||{};for(const t of state.teams)colorByTeam[t.id]=t.color;render()}
function fmtTime(ms){const seconds=Math.max(0,Math.floor(ms/1000));return `${Math.floor(seconds/60)}:${String(seconds%60).padStart(2,'0')}`}
function render(){
 $('#live').textContent=state.metrics.live??0;$('#changes').textContent=state.metrics.changes??0;$('#ops').textContent=state.metrics.opsPerSecond??0;$('#elapsed').textContent=fmtTime(state.metrics.elapsedMs||0);$('#peak').textContent=state.metrics.peakParallel??0;
 const roster=$('#roster');roster.replaceChildren();
 for(const team of state.teams){
  const heading=el('div','team-heading',team.name.toUpperCase());heading.style.setProperty('--team',team.color);roster.append(heading);
  for(const role of state.roles.filter(r=>r.team===team.id)){
   const status=state.statuses[role.id]||'idle',b=el('button','agent'+(state.selected===role.id?' selected':''));b.type='button';b.style.setProperty('--agent',team.color);b.title=role.goal;b.setAttribute('aria-pressed',String(state.selected===role.id));
   b.append(el('span','cursor','⌖'),el('span','name',role.id),el('span','status '+status,status));b.addEventListener('click',()=>{state.selected=state.selected===role.id?null:role.id;render()});roster.append(b);
  }
 }
 const eventBox=$('#activity');eventBox.replaceChildren();const filtered=state.events.filter(e=>!state.selected||e.agent===state.selected||(e.agent==='filesystem'&&e.file&&state.roles.find(r=>r.id===state.selected)?.writes.some(p=>p.endsWith('/')?e.file.startsWith(p):e.file===p))).slice(-100).reverse();
 $('#clear-filter').hidden=!state.selected; if(!filtered.length)eventBox.append(el('p','muted',state.selected?'No recorded events for this agent yet.':'Waiting for real events.'));
 for(const e of filtered){const team=state.roles.find(r=>r.id===e.agent)?.team||state.roles.find(r=>r.writes.some(p=>e.file&&(p.endsWith('/')?e.file.startsWith(p):e.file===p)))?.team;const col=colorByTeam[team]||'#8296a9';const row=el('div','event');row.style.setProperty('--event-color',col);const strip=el('div','stripe'),content=el('div','event-content'),top=el('div','event-top');top.append(el('strong','',e.agent==='filesystem'?'FILE OBSERVER':e.agent),el('time','',new Date(e.at).toLocaleTimeString()));content.append(top,el('p','',e.text||(e.file?e.file:e.type)));row.append(strip,content);eventBox.append(row)}
 const timeline=$('#timeline');timeline.replaceChildren();const e=state.events.filter(x=>x.agent!=='head-coach');const times=e.map(x=>Date.parse(x.at)).filter(Number.isFinite);const min=times.length?Math.min(...times):0;const max=times.length?Math.max(...times):0;const span=Math.max(1000,max-min);
 for(const team of state.teams){const row=el('div','timeline-row');row.append(el('span','lane-name',team.name));const track=el('div','lane-track');track.style.setProperty('--team',team.color);const teamRoles=state.roles.filter(r=>r.team===team.id).map(r=>r.id);const events=e.filter(x=>teamRoles.includes(x.agent)||(x.agent==='filesystem'&&state.roles.find(r=>teamRoles.includes(r.id)&&r.writes.some(p=>x.file&&(p.endsWith('/')?x.file.startsWith(p):x.file===p)))));
  if(!events.length)track.append(el('span','lane-empty','No recorded activity'));
  else for(const ev of events.slice(-200)){const tick=el('span','tick');const x=Math.min(97,Math.max(1,1+((Date.parse(ev.at)-min)/span)*96));tick.style.left=x+'%';tick.title=`${ev.agent}: ${ev.type}${ev.file?' — '+ev.file:''}`;tick.style.opacity=ev.type==='file'?'1':'.55';track.append(tick)}
  row.append(track);timeline.append(row);
 }
}
let timer;
function refreshPreview(){const iframe=$('#website');iframe.src='/preview/?v='+Date.now()}
async function poll(){try{const r=await fetch('/api/state',{cache:'no-store'});if(!r.ok)throw Error('HTTP '+r.status);update(await r.json());$('#connection').textContent='Connected'}catch{$('#connection').textContent='Offline'}}
function start(){poll();setInterval(poll,1800);const sse=new EventSource('/api/events');sse.addEventListener('message',ev=>{try{const e=JSON.parse(ev.data);if(e.type==='file'){clearTimeout(timer);timer=setTimeout(refreshPreview,250)}poll()}catch{}});sse.addEventListener('error',()=>{$('#connection').textContent='Reconnecting'});
 $('.refresh').addEventListener('click',refreshPreview);$('#clear-filter').addEventListener('click',()=>{state.selected=null;render()});for(const b of document.querySelectorAll('[data-width]'))b.addEventListener('click',()=>{for(const x of document.querySelectorAll('[data-width]')){const selected=x===b;x.classList.toggle('selected',selected);x.setAttribute('aria-pressed',String(selected))}$('#preview-shell').classList.toggle('mobile',b.dataset.width==='mobile');$('#preview-size').textContent=b.dataset.width==='mobile'?'Mobile: 390px':'Responsive viewport'});
}
start();
