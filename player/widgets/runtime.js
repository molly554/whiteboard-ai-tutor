/* Widget runtime — stage-2 experiment for a protocol v1.1 draft.
 *
 * A "widget" op does not draw anything itself. It names a hand-written widget kind and gives parameters;
 * the widget expands (params → ordinary v1 ops, with coordinates computed by code), and the player diffs
 * the result against what is already on the board:
 *   new id        → built and revealed with the usual handwriting animation
 *   changed spec  → replaced in place (numeric parameters are tweened)
 *   gone id       → removed
 * Widgets also hand back "handles": things the student may drag once playback is idle. Dragging changes one
 * parameter, the widget is re-expanded, and the drop becomes a structured event that getState() reports.
 *
 * This file only defines things. It uses globals of the player page (objs, layer, build, reveal, wait, anim,
 * validateOp, INSTANT, TOKEN, inStep, runningFlag, paused) at call time, never at load time.
 */
const WIDGETS={};
const widgets=new Map();          // widget id → {id, kind, params, ids:Set, handles:[], step}
const studentEvents=[];
function registerWidget(kind,def){WIDGETS[kind]=def;}

function widgetCheck(op){
  if(typeof op.id!=='string'||!op.id)return 'missing id';
  if(!WIDGETS[op.kind])return `unknown widget kind ${JSON.stringify(op.kind)}`;
  if(op.params!==undefined&&(typeof op.params!=='object'||op.params===null||Array.isArray(op.params)))return 'params must be an object';
  return null;
}

function resetWidgets(){
  widgets.clear();studentEvents.length=0;WD=null;
  const h=document.getElementById('hit');if(h)h.innerHTML='';
  const f=document.getElementById('fb');if(f){f.textContent='';f.className='';}
  renderEvents();
}

/* ───────── re-expanding a widget and diffing it against the board ───────── */
function lerpParam(def,key,a,b,k){
  if(def.lerp){const r=def.lerp(key,a,b,k);if(r!==undefined)return r;}
  if(typeof a==='number'&&typeof b==='number')return a+(b-a)*k;
  if(a&&b&&typeof a.x==='number'&&typeof b.x==='number')return {x:a.x+(b.x-a.x)*k,y:a.y+(b.y-a.y)*k};
  return k>=1?b:a;
}
async function syncWidget(w,p,step,opts,tok){
  const def=WIDGETS[w.kind],r=def.expand(p),seen=new Set();
  for(const raw of r.ops){
    const op={...raw,id:w.id+'.'+raw.id};seen.add(op.id);
    const err=validateOp(op);
    if(err){console.warn('widget op skipped:',err,op);continue;}
    const cur=objs.get(op.id);
    if(!cur){
      const o=build(op,layer,step,!!opts.reveal&&!INSTANT);o.widget=w.id;objs.set(op.id,o);w.ids.add(op.id);
      if(opts.reveal&&!INSTANT){await reveal(o,tok);await wait(160,tok);}
    }else if(JSON.stringify(cur.spec)!==JSON.stringify(op)){
      const o=build(op,layer,cur.step,false);o.widget=w.id;
      layer.insertBefore(o.g,cur.g);cur.g.remove();objs.set(op.id,o);
    }
  }
  for(const id of [...w.ids])if(!seen.has(id)){const o=objs.get(id);if(o)o.g.remove();objs.delete(id);w.ids.delete(id);}
  w.params=p;w.handles=r.handles||[];
}
// like anim(), but keeps running while the lesson is paused (a student's answer is given while it waits)
async function tween(ms,fn,tok){
  const t0=performance.now();fn(0);
  for(;;){await frame();if(tok!==TOKEN)throw CANCEL;const k=Math.min(1,(performance.now()-t0)/ms);fn(k);if(k>=1)return;}
}
async function morph(w,to,step,tok,ms,free){
  const def=WIDGETS[w.kind],from=w.params,run=free?tween:anim;
  const keys=(def.animate||[]).filter(k=>JSON.stringify(from[k])!==JSON.stringify(to[k])&&from[k]!==undefined&&to[k]!==undefined);
  if(keys.length&&w.ids.size&&!INSTANT){
    await run(ms||700,k=>{const p={...to};keys.forEach(key=>{p[key]=lerpParam(def,key,from[key],to[key],k);});syncWidget(w,p,step,{reveal:false},tok);},tok);
  }
}
async function doWidget(op,step,tok){
  const def=WIDGETS[op.kind];
  let w=widgets.get(op.id);
  if(!w){w={id:op.id,kind:op.kind,params:{...def.defaults},ids:new Set(),handles:[],step};widgets.set(op.id,w);}
  w.step=step;
  const fb=document.getElementById('fb');if(fb){fb.textContent='';fb.className='';}
  let to={...w.params,...(op.params||{})};
  if(def.normalize)to=def.normalize(to,op.params||{});   // e.g. named positions → numbers, a new question resets the old answer
  await morph(w,to,step,tok);
  await syncWidget(w,to,step,{reveal:true},tok);
  renderHandles();
  // a question waits for the student: reuse the "pause after this step" mechanism; the student resumes after reading the feedback
  if(to.ask&&!to.answered&&runningFlag&&!INSTANT)stepOnce=true;
}

/* ───────── handles: dragging once playback is idle ───────── */
const canInteract=()=>!inStep&&!(runningFlag&&!paused);
let WD=null;
function boardPt(ev){
  const s=document.getElementById('board'),pt=s.createSVGPoint();pt.x=ev.clientX;pt.y=ev.clientY;
  const r=pt.matrixTransform(s.getScreenCTM().inverse());return {x:r.x,y:r.y};
}
function renderHandles(){
  const hit=document.getElementById('hit');hit.innerHTML='';
  for(const w of widgets.values())for(const h of w.handles){
    const g=h.hit;let e;
    if(g.type==='line')e=mk('line',{x1:g.x1,y1:g.y1,x2:g.x2,y2:g.y2,stroke:'transparent','stroke-width':g.w||56,'stroke-linecap':'round'},hit);
    else e=mk('circle',{cx:g.cx,cy:g.cy,r:g.r||46,fill:'transparent'},hit);
    e.setAttribute('class','whit');
    e.addEventListener('pointerdown',ev=>{
      if(!canInteract())return;
      ev.preventDefault();document.getElementById('board').setPointerCapture?.(ev.pointerId);
      WD={w,h,from:w.params[h.param]};
    });
  }
}
{
  const bs=document.getElementById('board');
  bs.addEventListener('pointermove',ev=>{
    if(!WD)return;
    const v=WD.h.value(boardPt(ev),WD.w.params);
    syncWidget(WD.w,{...WD.w.params,[WD.h.param]:v},WD.w.step,{reveal:false},TOKEN);
  });
  const up=async()=>{try{
    if(!WD)return;
    const {w,h,from}=WD;WD=null;
    const to=w.params[h.param],def=WIDGETS[w.kind];
    const res=h.onDrop?h.onDrop(w.params,{from,to}):null;
    const ev={t:new Date().toLocaleTimeString('en-GB'),widget:w.id,kind:w.kind,event:'drag',param:h.param,from,to};
    if(res&&res.result)ev.result=res.result;
    ev.state=def.summary?def.summary(w.params):undefined;
    studentEvents.push(ev);renderEvents();
    const fb=document.getElementById('fb');
    if(res&&res.say){fb.textContent=(res.ok===true?'✓ ':res.ok===false?'✗ ':'')+res.say;fb.className=res.ok===true?'ok':res.ok===false?'bad':'';}
    if(res&&res.patch){const to2={...w.params,...res.patch};await morph(w,to2,w.step,TOKEN,350,true);await syncWidget(w,to2,w.step,{reveal:false},TOKEN);
      ev.state=def.summary?def.summary(w.params):undefined;renderEvents();}
    renderHandles();
  }catch(e){if(e!==CANCEL)throw e;}};
  bs.addEventListener('pointerup',up);bs.addEventListener('pointercancel',up);
  setInterval(()=>document.body.classList.toggle('canDrag',canInteract()),150);
}
function renderEvents(){
  const p=document.getElementById('evlog');if(!p)return;
  const box=document.getElementById('events');
  box.style.display=studentEvents.length?'block':'none';
  p.textContent=studentEvents.slice(-8).reverse().map(e=>JSON.stringify(e)).join('\n');
}
function widgetState(){
  return {
    widgets:[...widgets.values()].map(w=>({id:w.id,kind:w.kind,params:(WIDGETS[w.kind].publicParams?WIDGETS[w.kind].publicParams(w.params):w.params),state:WIDGETS[w.kind].summary?WIDGETS[w.kind].summary(w.params):undefined})),
    student_events:studentEvents.slice(-10)
  };
}
