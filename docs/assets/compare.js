import {MODELS, SCENARIOS, t, isZh, scenarioName, verdict, verdictName, settingName, option, validValue, comparisonURL, galleryURL, loadJSON} from './review-ui.js';

const $ = selector => document.querySelector(selector);
const keys = Object.keys(MODELS);
let rows = [], missing = [], state;

function readState() {
  const q = new URL(location.href).searchParams;
  const a = validValue(q.get('a'), keys, 'gemini-4-argon');
  let b = validValue(q.get('b'), keys, 'sonnet-5.5');
  if (a === b) b = keys.find(model => model !== a);
  return {sc:validValue(q.get('sc'),Object.keys(SCENARIOS),'r1-pythagoras'),cond:validValue(q.get('cond'),['low','mid'],'low'),a,b};
}

function element(tag, text, className) {
  const node = document.createElement(tag);
  if (text !== undefined) node.textContent = text;
  if (className) node.className = className;
  return node;
}

function metric(label, value) {
  const item = element('div'); item.append(element('dt',label),element('dd',value)); return item;
}

function renderBoard(side) {
  const model = state[side];
  const container = $('#board-'+side); container.replaceChildren();
  const row = rows.find(r => r.model===model && r.scenario===state.sc && r.cond===state.cond);
  const intro = element('div',undefined,'board-meta');
  intro.append(element('p',MODELS[model],'board-model'));
  if (!row) {
    const unavailable = missing.some(r => r.model===model && r.scenario===state.sc && r.cond===state.cond);
    intro.append(element('span',t('No reviewed board','无评审白板'),'v unavailable'));
    const empty = element('div',undefined,'no-board');
    empty.append(element('h3',unavailable ? t('No usable output in this sampled cell','该抽样单元没有可用输出') : t('Not reviewed at this setting','此思考档未评审这道题')));
    empty.append(element('p',unavailable ? t('The original review records no usable output here. No image or review score is available.','原始评测记录中，此模型与场景组合没有可用输出，因此没有板书图片或评审分数。') : t('This question was not included in the medium-thinking review sample. Choose low thinking to compare the recorded boards.','这道题未纳入中思考档的评审样本。可切换到低思考档查看已有白板。')));
    const low = element('button',t('Use low thinking','切换到低思考档'),'button secondary'); low.type='button';
    low.addEventListener('click',()=>{state.cond='low';update(true);}); empty.append(low);
    container.append(intro,empty); return;
  }
  const result = verdict(row);
  intro.append(element('span',verdictName(result),'v '+result),element('span',row.id+' · '+settingName(row.cond),'record-id'));
  const imageLink = element('a',undefined,'board-image');
  imageLink.href='results/review/boards/'+row.id+'.png'; imageLink.target='_blank'; imageLink.rel='noopener';
  imageLink.setAttribute('aria-label',t('Open full-size board: ','打开完整白板：')+MODELS[model]);
  const img=element('img'); img.src=imageLink.href; img.width=1600; img.height=900;
  img.alt=MODELS[model]+' · '+scenarioName(state.sc)+' · '+verdictName(result); imageLink.append(img);
  const imageError=element('p',t('The board image could not be loaded. You can still read the review or open its replay.','白板图片未能加载，仍可阅读评语或打开回放。'),'image-error');imageError.hidden=true;
  img.addEventListener('error',()=>{imageError.hidden=false;});
  const actions=element('div',undefined,'board-actions');
  const replay=element('a',t('▶ Replay this lesson ↗','▶ 单独回放 ↗'),'button primary');
  const replayURL=new URL('player/index.html',document.baseURI);
  replayURL.search=new URLSearchParams({run:row.run_id,sc:row.scenario,lang:isZh?'zh':'en',from:'compare',cond:state.cond,a:state.a,b:state.b}).toString();
  replay.href=replayURL.href; replay.target='_blank'; replay.rel='noopener';
  const full=element('a',t('Full-size board ↗','查看原图 ↗'),'text-link');full.href=imageLink.href;full.target='_blank';full.rel='noopener';
  actions.append(replay,full);
  const review=element('section',undefined,'review-note');
  review.append(element('h3',t('Review notes','评审意见')),element('p',isZh?(row.note_zh||row.note_en):row.note_en));
  const rubric=element('dl',undefined,'rubric');
  const yes=value=>value===1?t('Yes','是'):t('No','否');
  rubric.append(metric(t('Content correct','内容无错'),yes(row.content)),metric(t('Figure matches text','图文一致'),yes(row.match)),metric(t('Layout','版面'),row.layout+' / 2'),metric(t('Explanation complete','讲解完整'),yes(row.pedagogy)));
  if(row.kind==='interrupt')rubric.append(metric(t('Question answered','回答了问题'),yes(row.answers)),metric(t('Board preserved','保留了原白板'),yes(row.placement)));
  review.append(rubric);
  const run=element('dl',undefined,'run-metrics');
  run.append(metric(t('This run: first stroke','本次生成：第一笔'),Number.isFinite(row.first_op)?row.first_op.toFixed(1)+' s':t('No stroke','未绘制')),metric(t('This run: cost','本次生成：成本'),Number.isFinite(row.cost)?'$'+row.cost.toFixed(4):'—'));
  container.append(intro,imageLink,imageError,actions,review,run);
}

function update(push = false) {
  for(const id of ['sc','cond','a','b'])$('#'+id).value=state[id];
  const url=comparisonURL(state);
  if(push)history.pushState(null,'',url);else history.replaceState(null,'',url);
  $('#language-link').href=comparisonURL(state,!isZh).href;
  const browse=galleryURL();browse.search=new URLSearchParams({sc:state.sc,cond:state.cond}).toString();browse.hash='boards';
  $('#browse-question').href=browse.href;
  $('#question-title').textContent=scenarioName(state.sc);
  $('#comparison-setting').textContent=settingName(state.cond)+' · '+t('Original recorded outputs','模型原始录制结果');
  $('#share-url').value=url.href;$('#share-fallback').hidden=true;$('#share-status').textContent='';
  $('#sample-notice').hidden=state.cond==='low';
  renderBoard('a');renderBoard('b');
}

function validRows(data) {
  if(!Array.isArray(data)||!data.length)throw new Error('No review rows');
  const seen=new Set();
  for(const row of data){
    const key=[row.model,row.scenario,row.cond].join('|');
    if(!Object.hasOwn(MODELS,row.model)||!Object.hasOwn(SCENARIOS,row.scenario)||!['low','mid'].includes(row.cond)||!/^B\d{2}$/.test(row.id)||!/^[a-z0-9.-]+$/.test(row.run_id)||typeof row.lenient!=='boolean'||typeof row.strict!=='boolean'||typeof row.note_en!=='string'||seen.has(key))throw new Error('Invalid review data');
    seen.add(key);
  }
  return data;
}

async function init() {
  $('#load-error').hidden=true;$('#loading').hidden=false;
  try {
    const data=await Promise.all([loadJSON('results/review/results.json'),loadJSON('results/review/no_output.json')]);
    rows=validRows(data[0]);missing=Array.isArray(data[1])?data[1]:[];
    state=readState();update();$('#loading').hidden=true;$('#comparison-content').hidden=false;
  } catch(err) {
    console.warn('Review data could not be displayed:', err);
    $('#loading').hidden=true;$('#comparison-content').hidden=true;$('#load-error').hidden=false;
  }
}

for(const [id] of Object.entries(SCENARIOS))option($('#sc'),id,scenarioName(id));
for(const [id,name] of Object.entries(MODELS)){option($('#a'),id,name);option($('#b'),id,name);}
for(const id of ['sc','cond','a','b'])$('#'+id).addEventListener('change',()=>{
  if(!state)return;
  const old=state[id];state[id]=$('#'+id).value;
  if(id==='a'&&state.a===state.b)state.b=old;
  if(id==='b'&&state.a===state.b)state.a=old;
  update(true);
});
window.addEventListener('popstate',()=>{if(rows.length){state=readState();update();}});
$('#share-comparison').addEventListener('click',async()=>{
  const url=comparisonURL(state).href;
  try {
    if(!navigator.clipboard?.writeText)throw new Error('Clipboard unavailable');
    await navigator.clipboard.writeText(url);$('#share-status').textContent=t('Comparison link copied.','对比链接已复制。');
  }catch{
    $('#share-fallback').hidden=false;$('#share-url').focus();$('#share-url').select();
    $('#share-status').textContent=t('Copy the selected link to share this comparison.','请复制已选中的链接，分享当前对比。');
  }
});
$('#retry-load').addEventListener('click',init);
init();
