import {MODELS, SCENARIOS, loadJSON} from './review-ui.js';

const $=selector=>document.querySelector(selector);
const params=new URL(location.href).searchParams;
const zh=params.get('lang')==='zh';
const t=(en,cn)=>zh?cn:en;
document.documentElement.lang=zh?'zh-CN':'en';
const labels={
 'preview-title':['Lesson PDF preview','课件 PDF 预览'],
 'preview-eyebrow':['COMPLETE LESSON · A4 LANDSCAPE','完整讲解 · A4 横向'],
 'preview-help':['Review the pages, then choose Print / Save as PDF. Closing or cancelling the print dialog does not reset your source player.','先查看完整课件，再点击“打印 / 另存为 PDF”。关闭预览或取消打印不会重置原播放器。'],
 'print-pdf':['Print / Save as PDF','打印 / 另存为 PDF'],
 'preview-zoom':['Actual size','实际大小'], 'close-preview':['Close preview','关闭预览'],
 'desktop-note':['For best results, use desktop Chrome or Edge. Keep A4 landscape at the default scale and turn browser headers/footers off. Saving on phones depends on the browser and system.','建议使用电脑端 Chrome 或 Edge，保留 A4 横向和默认缩放，关闭浏览器额外的页眉页脚。手机保存方式取决于浏览器和系统。'],
 'error-title':['The preview could not be prepared','课件预览未能生成'],
 'error-help':['Check your connection, try again, or open the lesson in the player.','请检查网络后重试，或在播放器中打开这份讲解。'],
 'retry-preview':['Try again','重试'], 'close-help':['You can close this tab to return to your original player.','请关闭此标签页，回到原来的播放器。'],
 'open-replay':['Open replay ↗','打开回放 ↗']
};
for(const [id,values] of Object.entries(labels))$('#'+id).textContent=t(...values);
document.title=t('Lesson PDF preview - Whiteboard AI Tutor','课件 PDF 预览 - Whiteboard AI Tutor');
$('#paper-collection').setAttribute('aria-label',t('Lesson pages','课件页面'));
$('#gallery-link').href=zh?'gallery.zh.html':'index.html';
const languageURL=new URL(location.href);languageURL.searchParams.set('lang',zh?'en':'zh');$('#preview-language').href=languageURL.href;$('#preview-language').textContent=zh?'English':'中文';
let generation=0,renderer=null,actualSize=false,request=null;

function el(tag,text,className){const node=document.createElement(tag);if(text!==undefined)node.textContent=text;if(className)node.className=className;return node;}
function readRequest(){
 const run=params.get('run'),s=params.get('s');
 if(run){
  if(!/^[a-z0-9][a-z0-9.-]{1,179}$/.test(run)||run.includes('..'))throw new Error('Invalid recording ID');
  const sc=Object.keys(SCENARIOS).find(id=>run.includes('-'+id+'-'))||params.get('sc');
  if(!Object.hasOwn(SCENARIOS,sc))throw new Error('Unknown scenario');
  return {run,sc};
 }
 if(!Object.hasOwn(SCENARIOS,s))throw new Error('Choose a lesson in the player first');
 return {s};
}
function replayURL(req){
 const url=new URL('player/index.html',document.baseURI);url.searchParams.set('lang',zh?'zh':'en');
 for(const [key,value] of Object.entries(req))url.searchParams.set(key,value);
 if(params.get('from')==='compare')for(const key of ['from','cond','a','b'])if(params.has(key))url.searchParams.set(key,params.get(key));
 return url;
}
function status(en,cn){$('#preview-status').textContent=t(en,cn);}
async function waitForPlayer(frame,token){
 const start=performance.now();
 while(performance.now()-start<35000){
  if(token!==generation||!frame.isConnected)throw new Error('Cancelled');
  const api=frame.contentWindow?.__wb;
  if(api?.error)throw new Error(api.error);
  if(api?.ready)return api;
  await new Promise(resolve=>setTimeout(resolve,40));
 }
 throw new Error('Lesson loading timed out');
}
function makeSheet(meta,shot,continued){
 const stage=el('div',undefined,'page-stage'),wrapper=el('div',undefined,'sheet-wrapper');
 const sheet=el('article',undefined,'sheet'+(continued?' continuation':''));sheet.dataset.step=shot.index;sheet.dataset.kind=shot.kind;
 const header=el('header',undefined,'sheet__header'),kicker=el('p',undefined,'page-kicker');
 let step=shot.kind==='context'?t('Board at interruption','打断时的白板'):t(`Step ${shot.index} / ${meta.totalSteps}`,`第 ${shot.index} / ${meta.totalSteps} 步`);
 if(continued)step+=t(' (continued)','（续）');
 kicker.append(el('span','WHITEBOARD AI TUTOR'),el('span',step));
 header.append(kicker,el('h2',meta.question||meta.title||t('Whiteboard lesson','白板讲解')),el('p',meta.detail,'sheet-meta'));sheet.append(header);
 if(!continued){
  const board=el('div',undefined,'paper-board');
  const parsed=new DOMParser().parseFromString(shot.svg,'image/svg+xml');if(parsed.querySelector('parsererror'))throw new Error('Invalid board SVG');
  const svg=document.importNode(parsed.documentElement,true);svg.setAttribute('role','img');svg.setAttribute('aria-label',step);board.append(svg);
  if(!shot.objectIds.length)board.append(el('p',t('No visible marks at this step.','这一步没有可见的板书内容。'),'empty-board-note'));
  sheet.append(board);
 }
 const caption=el('div',undefined,'explanation');caption.append(el('p',shot.kind==='context'?t('Student question (original language)','学生追问（原始语言）'):t('Explanation (original language)','讲解文本（原始语言）'),'explanation-label'));
 const text=el('p','', 'narration');caption.append(text);sheet.append(caption);
 const footer=el('footer',undefined,'sheet__footer');const link=el('a',t('Replay lesson - Whiteboard AI Tutor','回放来源 - Whiteboard AI Tutor'));link.href=meta.replay;
 footer.append(link,el('span','', 'page-number'));sheet.append(footer);wrapper.append(sheet);stage.append(wrapper);$('#paper-collection').append(stage);
 return {sheet,text};
}
function fitText(node,chars){
 let low=0,high=chars.length;
 while(low<high){const mid=Math.ceil((low+high)/2);node.textContent=chars.slice(0,mid).join('');if(node.scrollHeight<=node.clientHeight+1)low=mid;else high=mid-1;}
 if(low===0&&chars.length)throw new Error('Page has no room for narration');
 if(low<chars.length){
  for(let i=low-1;i>=Math.floor(low*.65);i--)if(/\s/.test(chars[i])){low=i+1;break;}
 }
 node.textContent=chars.slice(0,low).join('');return low;
}
function paginate(meta,shots){
 for(const shot of shots){
  let remaining=Array.from((shot.kind==='context'?shot.say:[shot.title,shot.say].filter(Boolean).join('\n')).trim()),continued=false;
  do{
   const page=makeSheet(meta,shot,continued);const used=fitText(page.text,remaining);remaining=remaining.slice(used);continued=true;
  }while(remaining.length);
 }
 const pages=[...document.querySelectorAll('.sheet')];
 pages.forEach((page,i)=>{page.querySelector('.page-number').textContent=t(`Page ${i+1} / ${pages.length}`,`第 ${i+1} / ${pages.length} 页`);});
 return pages.length;
}
function scalePages(){
 for(const sheet of document.querySelectorAll('.sheet')){
  const wrapper=sheet.parentElement,stage=wrapper.parentElement;const scale=actualSize?1:Math.min(1,(stage.clientWidth-4)/sheet.offsetWidth);
  sheet.style.transform=`scale(${scale})`;wrapper.style.width=sheet.offsetWidth*scale+'px';wrapper.style.height=sheet.offsetHeight*scale+'px';
 }
}
async function init(){
 const token=++generation;window.__pdfReady=false;renderer?.remove();renderer=null;$('#paper-collection').replaceChildren();
 $('#preview-error').hidden=true;$('#preview-status').hidden=false;$('#print-pdf').disabled=true;$('#preview-zoom').disabled=true;$('#page-summary').textContent='';
 status('Loading the lesson…','正在加载讲解…');
 let frame;
 try{
  request=readRequest();const replay=replayURL(request);$('#open-replay').href=replay.href;
  frame=document.createElement('iframe');frame.className='render-frame';frame.title=t('Isolated lesson renderer','独立课件渲染器');frame.setAttribute('aria-hidden','true');frame.tabIndex=-1;
  const source=new URL(replay);source.searchParams.set('pdf','1');source.searchParams.delete('board');frame.src=source.href;renderer=frame;document.body.append(frame);
  const reviewPromise=request.run?loadJSON('results/review/results.json'):Promise.resolve([]);
  const [api,reviews]=await Promise.all([waitForPlayer(frame,token),reviewPromise]);if(token!==generation)return;
  const lesson=await api.lessonSnapshots((step,total)=>status(`Preparing step ${step} / ${total}…`,`正在准备第 ${step} / ${total} 步…`));
  if(token!==generation)return;
  const review=reviews.find(row=>row.run_id===request.run);
  const slug=request.run&&Object.keys(MODELS).find(id=>request.run.includes('-'+id+'-'));
  const model=slug?MODELS[slug]:t('Reference example','参考示例');
  const setting=request.run?(request.run.includes('-mid-')?t('Medium thinking','中思考档'):t('Low thinking','低思考档')):t('Not a benchmark result','非评测结果');
  const assessment=review?(!review.lenient?t('Fail','不通过'):review.strict?t('Pass','通过'):t('Borderline','边界')):t('Not in the reviewed sample','未纳入盲评样本');
  const meta={...lesson,detail:[model,setting,review?.id,assessment,t('Recorded model output','模型原始录制结果')].filter(Boolean).join(' · '),replay:replay.href};
  frame.remove();frame=null;renderer=null;await document.fonts.ready;if(token!==generation)return;
  status('Laying out the complete lesson…','正在排版完整课件…');const pages=paginate(meta,lesson.snapshots);scalePages();
  document.title=('Whiteboard AI Tutor - '+(lesson.question||lesson.title||model)+' - '+model).replace(/[\\/:*?"<>|]/g,'-').slice(0,150);
  $('#page-summary').textContent=t(`${lesson.totalSteps} steps · ${pages} pages · A4 landscape`,`${lesson.totalSteps} 步 · ${pages} 页 · A4 横向`);
  $('#preview-status').hidden=true;$('#print-pdf').disabled=false;$('#preview-zoom').disabled=false;
  window.__pdfLesson=lesson;window.__pdfReady=true;
 }catch(err){
  if(token!==generation)return;
  $('#paper-collection').replaceChildren();$('#preview-status').hidden=true;$('#preview-error').hidden=false;
  console.warn('Lesson PDF preview could not be prepared:',err);
 }finally{frame?.remove();if(renderer===frame)renderer=null;}
}
$('#retry-preview').addEventListener('click',init);
$('#preview-zoom').addEventListener('click',()=>{actualSize=!actualSize;$('#preview-zoom').setAttribute('aria-pressed',String(actualSize));$('#preview-zoom').textContent=actualSize?t('Fit pages','适应屏幕'):t('Actual size','实际大小');scalePages();});
window.addEventListener('resize',scalePages);
$('#print-pdf').addEventListener('click',()=>{if(window.__pdfReady)window.print();});
$('#close-preview').addEventListener('click',()=>{$('#close-help').hidden=false;window.close();});
init();
