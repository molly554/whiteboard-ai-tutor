import {MODELS, SCENARIOS, t, isZh, scenarioName, verdictName, option, validValue, galleryURL} from './review-ui.js';

// Quiet preview; reduced-motion visitors choose when to start it.
const preview = document.querySelector('#hero-video');
if (preview && !matchMedia('(prefers-reduced-motion: reduce)').matches) {
  preview.muted = true;
  const start = () => {
    // Begin at the diagram, while the full recording remains available in the controls.
    preview.currentTime = Math.min(6, preview.duration / 3);
    preview.play().catch(() => {});
  };
  if (preview.readyState >= 1) start();
  else preview.addEventListener('loadedmetadata', start, { once: true });
}

const controls={sc:document.querySelector('#filter-sc'),model:document.querySelector('#filter-model'),verdict:document.querySelector('#filter-verdict'),cond:document.querySelector('#filter-cond')};
const filterPanel=document.querySelector('#board-filters');
if(filterPanel){
  option(controls.sc,'',t('All questions','全部题目'));
  for(const id of Object.keys(SCENARIOS))option(controls.sc,id,scenarioName(id));
  option(controls.model,'',t('All models','全部模型'));
  for(const [id,name] of Object.entries(MODELS))option(controls.model,id,name);
  option(controls.verdict,'',t('All verdicts','全部结果'));
  for(const id of ['pass','borderline','fail'])option(controls.verdict,id,verdictName(id));
  option(controls.cond,'',t('All settings','全部思考档'));
  option(controls.cond,'low',t('Low thinking','低思考档'));option(controls.cond,'mid',t('Medium thinking','中思考档'));
  const allowed={sc:Object.keys(SCENARIOS),model:Object.keys(MODELS),verdict:['pass','borderline','fail'],cond:['low','mid']};
  const cards=[...document.querySelectorAll('.grid .card')];
  const headings=[...document.querySelectorAll('.model-heading')];
  for(const heading of headings)heading.dataset.originalTitle=heading.textContent;
  let state;
  function read(){const q=new URL(location.href).searchParams;return Object.fromEntries(Object.keys(controls).map(key=>[key,validValue(q.get(key),allowed[key],'')]));}
  function update(push=false){
    const active=Object.values(state).some(Boolean);
    for(const [key,control] of Object.entries(controls))control.value=state[key];
    let count=0;
    for(const card of cards){const visible=Object.entries(state).every(([key,value])=>!value||card.dataset[key]===value);card.hidden=!visible;if(visible)count++;}
    for(const heading of headings){
      const grid=heading.nextElementSibling;const visible=[...grid.querySelectorAll('.card')].filter(card=>!card.hidden).length;
      heading.hidden=active||!visible;grid.hidden=!visible;
      heading.textContent=heading.dataset.originalTitle;
    }
    document.querySelector('#board-results').classList.toggle('is-filtered',active);
    document.querySelector('#filter-count').textContent=t(`Showing ${count} of ${cards.length} reviewed boards`,`显示 ${count} / ${cards.length} 块评审白板`);
    document.querySelector('#empty-boards').hidden=count!==0;
    document.querySelector('#reset-filters').disabled=!active;
    const url=new URL(location.href);for(const [key,value] of Object.entries(state)){url.searchParams.delete(key);if(value)url.searchParams.set(key,value);}
    if(push)history.pushState(null,'',url);else history.replaceState(null,'',url);
    const other=galleryURL(!isZh);other.search=url.search;if(active||url.hash==='#boards')other.hash='boards';
    document.querySelector('.site-header a[lang]').href=other.href;
  }
  function reset(){state={sc:'',model:'',verdict:'',cond:''};update(true);}
  for(const [key,control] of Object.entries(controls))control.addEventListener('change',()=>{state[key]=control.value;update(true);});
  document.querySelector('#reset-filters').addEventListener('click',reset);
  document.querySelector('#empty-reset').addEventListener('click',reset);
  for(const link of document.querySelectorAll('.lb a[href^="#"]'))link.addEventListener('click',event=>{
    const model=link.getAttribute('href').slice(1);if(!Object.hasOwn(MODELS,model))return;
    event.preventDefault();state={sc:'',model,verdict:'',cond:''};update(true);
    document.querySelector('#boards').scrollIntoView({block:'start'});
  });
  window.addEventListener('popstate',()=>{state=read();update();});
  state=read();update();filterPanel.hidden=false;
}
