export const MODELS = {
  'gemini-4-argon': 'Gemini 4 Argon',
  'haiku-5.5': 'Claude Haiku 5.5',
  'gemini-3.8-flash': 'Gemini 3.8 Flash',
  'sonnet-5.5': 'Claude Sonnet 5.5',
  'deepseek-v4-pro': 'DeepSeek V4 Pro',
  'deepseek-flash': 'DeepSeek V4.1 Flash'
};
export const SCENARIOS = {
  'r1-seasons': ['Why do we have seasons?', '为什么会有四季？'],
  'r1-pythagoras': ['Why does the Pythagorean theorem work?', '勾股定理为什么成立？'],
  'r1-quadratic': ['Solve x² − 5x + 6 = 0; switch method midway', '解方程：中途换一种方法'],
  'r1-supply-demand': ['What happens when demand rises?', '需求增加时，价格会怎样？'],
  'r1-photosynthesis': ['Where does photosynthesis happen? (Chinese)', '光合作用发生在哪里？'],
  'r1-i1-seasons-distance': ['Interruption: farther from the Sun, but hotter?', '打断：地球更远，为什么更热？'],
  'r1-i2-demand-simpler': ['Interruption: show demand a simpler way', '打断：能换个简单的讲法吗？'],
  'r1-i3-arrow-meaning': ['Interruption: what does this arrow mean?', '打断：这条箭头是什么意思？']
};
export const isZh = document.documentElement.lang.startsWith('zh');
export const t = (en, zh) => isZh ? zh : en;
export const scenarioName = id => SCENARIOS[id]?.[isZh ? 1 : 0] || id;
export const verdict = row => !row.lenient ? 'fail' : row.strict ? 'pass' : 'borderline';
export const verdictName = key => ({pass:t('Pass','通过'),borderline:t('Borderline','边界'),fail:t('Fail','不通过')})[key];
export const settingName = cond => cond === 'mid' ? t('Medium thinking','中思考档') : t('Low thinking','低思考档');
export function option(select, value, label) {
  const el = document.createElement('option'); el.value = value; el.textContent = label; select.append(el);
}
export function validValue(value, allowed, fallback) {
  return allowed.includes(value) ? value : fallback;
}
export function comparisonURL(state, zh = isZh) {
  const url = new URL(zh ? 'compare.zh.html' : 'compare.html', document.baseURI);
  url.search = new URLSearchParams({sc:state.sc,cond:state.cond,a:state.a,b:state.b}).toString();
  return url;
}
export function galleryURL(zh = isZh) {
  return new URL(zh ? 'gallery.zh.html' : 'index.html', document.baseURI);
}
export async function loadJSON(path) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 20000);
  try {
    const response = await fetch(new URL(path, document.baseURI), {signal:controller.signal});
    if (!response.ok) throw new Error(`Cannot load ${path}: ${response.status}`);
    return await response.json();
  } finally { clearTimeout(timer); }
}
