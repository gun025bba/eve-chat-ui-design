'use strict';
// Reference implementation — vanilla, no build. Streams from OpenAI-compatible /v1/chat/completions; mock mode without backend.
const $ = s => document.querySelector(s);
const ICON = {
  copy: '<svg viewBox="0 0 24 24"><rect x="9" y="9" width="12" height="12" rx="2"/><path d="M5 15V5a2 2 0 0 1 2-2h8"/></svg>',
  check: '<svg viewBox="0 0 24 24"><path d="M5 12l5 5 9-10"/></svg>',
  regen: '<svg viewBox="0 0 24 24"><path d="M21 12a9 9 0 1 1-3-6.7L21 8"/><path d="M21 3v5h-5"/></svg>',
  warn: '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M12 8v5M12 16.5v.01"/></svg>',
  chev: '<svg class="chev" viewBox="0 0 24 24"><path d="M9 6l6 6-6 6"/></svg>',
  del: '<svg viewBox="0 0 24 24"><path d="M4 7h16M10 11v6M14 11v6M6 7l1 13h10l1-13M9 7V4h6v3"/></svg>',
};
const esc = s => s.replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
function inline(s) { // s escaped
  return s.replace(/`([^`]+)`/g, '<code>$1</code>').replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>').replace(/(^|[^*])\*([^*\s][^*]*)\*/g, '$1<em>$2</em>');
}
function renderMarkdown(src) {
  const out = []; const lines = src.split('\n'); let i = 0, para = [], list = null;
  const flushP = () => { if (para.length) { out.push('<p>' + inline(esc(para.join('\n'))).replace(/\n/g, '<br>') + '</p>'); para = []; } };
  const flushL = () => { if (list) { out.push(`<${list.t}>` + list.items.map(x => '<li>' + inline(esc(x)) + '</li>').join('') + `</${list.t}>`); list = null; } };
  while (i < lines.length) {
    const l = lines[i]; let m;
    if ((m = l.match(/^```\s*([\w+-]*)/))) {
      flushP(); flushL(); const lang = m[1]; const buf = []; i++;
      while (i < lines.length && !/^```/.test(lines[i])) buf.push(lines[i++]);
      i++;
      out.push(`<div class="codeblock"><div class="code-head"><span class="lang">${esc(lang || 'code')}</span><button type="button" class="copy">${ICON.copy}<span>복사</span></button></div><pre><code>${esc(buf.join('\n'))}</code></pre></div>`);
      continue;
    }
    if ((m = l.match(/^(#{1,3})\s+(.*)/))) { flushP(); flushL(); out.push(`<h${m[1].length}>${inline(esc(m[2]))}</h${m[1].length}>`); }
    else if ((m = l.match(/^\s*([-*]|\d+\.)\s+(.*)/))) { flushP(); const t = /\d/.test(m[1]) ? 'ol' : 'ul'; if (!list || list.t !== t) { flushL(); list = { t, items: [] }; } list.items.push(m[2]); }
    else if (!l.trim()) { flushP(); flushL(); }
    else { flushL(); para.push(l); }
    i++;
  }
  flushP(); flushL(); return out.join('');
}
function splitThink(t) {
  const m = t.match(/^\s*<think>([\s\S]*?)(<\/think>|$)([\s\S]*)/);
  return m ? { think: m[1].trim(), done: !!m[2], body: m[3] } : { think: '', done: true, body: t };
}

const S = Object.assign({ base: '', key: '', model: '', system: '', mock: false, showThink: false }, JSON.parse(localStorage.getItem('ref.settings') || '{}'));
let convs = JSON.parse(localStorage.getItem('ref.convs') || '[]'), cur = convs[0]?.id, ctrl = null, stick = true;
const save = () => { localStorage.setItem('ref.convs', JSON.stringify(convs)); localStorage.setItem('ref.settings', JSON.stringify(S)); };
const conv = () => convs.find(c => c.id === cur);
const uid = () => Math.random().toString(36).slice(2, 10);

/* ---------- viewport / keyboard ---------- */
const vv = window.visualViewport;
function syncVV() { document.documentElement.style.setProperty('--vvh', (vv ? vv.height : innerHeight) + 'px'); if (stick) scrollBottom(); }
vv && (vv.addEventListener('resize', syncVV), vv.addEventListener('scroll', () => window.scrollTo(0, 0)));
syncVV();
new ResizeObserver(([e]) => document.documentElement.style.setProperty('--composer-h', e.target.offsetHeight + 'px')).observe($('#composer'));

/* ---------- render ---------- */
const box = $('#messages');
function scrollBottom(smooth) { box.scrollTo({ top: box.scrollHeight, behavior: smooth ? 'smooth' : 'auto' }); }
box.addEventListener('scroll', () => {
  const d = box.scrollHeight - box.scrollTop - box.clientHeight;
  stick = d < 80; $('#toBottom').classList.toggle('show', d > 200); $('#topbar').classList.toggle('scrolled', box.scrollTop > 4);
}, { passive: true });
$('#toBottom').onclick = () => { stick = true; scrollBottom(true); };

function renderList() {
  const ul = $('#convList'); ul.innerHTML = '';
  convs.forEach(c => {
    const li = document.createElement('li'); li.className = c.id === cur ? 'active' : '';
    li.innerHTML = `<span>${esc(c.title)}</span><button aria-label="삭제">${ICON.del}</button>`;
    li.onclick = e => { if (e.target.closest('button')) { convs = convs.filter(x => x !== c); if (cur === c.id) cur = convs[0]?.id; save(); renderAll(); return; } cur = c.id; renderAll(); closeDrawer(); };
    ul.appendChild(li);
  });
}
const CHIPS = [['코드 리뷰', '이 함수의 개선점을 알려줘'], ['요약', '긴 글을 핵심 3줄로 정리해줘'], ['번역', '자연스러운 영어 문장으로 바꿔줘'], ['아이디어', '주말에 할 사이드 프로젝트 추천']];
function renderEmpty() {
  box.innerHTML = `<div class="empty"><div class="mark"></div><h1>무엇을 도와드릴까요?</h1><small>${esc(S.mock ? 'Mock 모드' : (S.model || '로컬 모델'))}</small>
  <div class="chips">${CHIPS.map((c, i) => `<button class="chip" style="animation-delay:${80 + i * 40}ms" data-q="${esc(c[1])}"><b>${c[0]}</b><span>${c[1]}</span></button>`).join('')}</div></div>`;
  box.querySelectorAll('.chip').forEach(b => b.onclick = () => send(b.dataset.q));
}
function addMsg(role) {
  const el = document.createElement('div'); el.className = 'msg ' + role;
  el.innerHTML = '<div class="bubble"></div>'; box.appendChild(el); return el;
}
function fillAssistant(el, text, live, meta) {
  const b = el.querySelector('.bubble'); const p = splitThink(text);
  const wasOpen = el.querySelector('details.think')?.open;
  let html = '';
  if (p.think) {
    const thinking = live && !p.done;
    const open = wasOpen ?? (thinking || S.showThink);
    html += `<details class="think${thinking ? ' live' : ''}"${open ? ' open' : ''}><summary>${ICON.chev}<span>${thinking ? '생각하는 중…' : '생각 과정'}</span></summary><div class="think-body">${esc(p.think)}</div></details>`;
  }
  if (live && !p.body.trim() && (!p.think || p.done)) html += '<span class="typing"><i></i><i></i><i></i></span>';
  else html += `<div class="md${live ? ' cursor' : ''}">${renderMarkdown(p.body)}</div>`;
  b.innerHTML = html;
  if (live) { const last = b.querySelector('.md > :last-child'); if (last && last.lastChild?.nodeType === 3) { /* fade newest text */ const t = last.lastChild; const n = Math.min(12, t.data.length); const sp = document.createElement('span'); sp.className = 'fresh'; sp.textContent = t.data.slice(-n); t.data = t.data.slice(0, -n); last.appendChild(sp); } }
  b.querySelectorAll('.copy').forEach(btn => btn.onclick = () => copy(btn, btn.closest('.codeblock').querySelector('code').textContent, true));
  el.querySelector('.actions')?.remove();
  if (!live && meta !== false) {
    const a = document.createElement('div'); a.className = 'actions';
    a.innerHTML = `<button aria-label="복사" class="c">${ICON.copy}</button><button aria-label="다시 생성" class="r">${ICON.regen}</button>${meta?.usage ? `<span class="usage">${esc(meta.usage)}</span>` : ''}`;
    a.querySelector('.c').onclick = e => copy(e.currentTarget, p.body.trim());
    a.querySelector('.r').onclick = regenerate;
    el.appendChild(a);
  }
}
function copy(btn, text, label) {
  navigator.clipboard?.writeText(text);
  const old = btn.innerHTML; btn.innerHTML = ICON.check + (label ? '<span>복사됨</span>' : '');
  setTimeout(() => btn.innerHTML = old, 1500);
}
function renderMessages() {
  const c = conv(); box.innerHTML = '';
  $('#title').textContent = c?.title || '새 대화';
  $('#modelName').textContent = S.mock ? 'Mock' : (S.model || '');
  if (!c || !c.messages.length) return renderEmpty();
  box.classList.add('no-anim');
  c.messages.forEach((m, i) => {
    if (m.role === 'user') addMsg('user').querySelector('.bubble').textContent = m.content;
    else fillAssistant(addMsg('assistant'), m.content, false, i === c.messages.length - 1 ? { usage: m.usage } : false);
  });
  requestAnimationFrame(() => { box.classList.remove('no-anim'); stick = true; scrollBottom(); });
}
function renderAll() { renderList(); renderMessages(); }
function addError(msg, retry) {
  const el = addMsg('error'); const b = el.querySelector('.bubble');
  b.innerHTML = `${ICON.warn}<span style="flex:1">${esc(msg)}</span>`;
  if (retry) { const r = document.createElement('button'); r.className = 'btn retry'; r.textContent = '다시 시도'; r.onclick = () => { el.remove(); generate(); }; b.appendChild(r); }
  scrollBottom(true);
}

/* ---------- composer ---------- */
const input = $('#input'), sendBtn = $('#sendBtn');
const isTouch = matchMedia('(pointer:coarse)').matches;
function grow() { input.style.height = 'auto'; input.style.height = Math.min(input.scrollHeight, 160) + 'px'; if (!ctrl) sendBtn.disabled = !input.value.trim(); }
input.addEventListener('input', grow);
input.addEventListener('keydown', e => { if (e.key === 'Enter' && !e.shiftKey && !isTouch && !e.isComposing) { e.preventDefault(); $('#composer').requestSubmit(); } });
$('#composer').onsubmit = e => { e.preventDefault(); if (ctrl) return ctrl.abort(); const t = input.value.trim(); if (t) send(t); };
function setBusy(b) { sendBtn.classList.toggle('stop', b); sendBtn.disabled = b ? false : !input.value.trim(); sendBtn.setAttribute('aria-label', b ? '중지' : '전송'); }

function send(text) {
  let c = conv();
  if (!c) { c = { id: uid(), title: '새 대화', messages: [] }; convs.unshift(c); cur = c.id; }
  if (!c.messages.length) { box.innerHTML = ''; c.title = text.slice(0, 30); $('#title').textContent = c.title; }
  c.messages.push({ role: 'user', content: text }); save(); renderList();
  box.querySelector('.actions')?.remove();
  addMsg('user').querySelector('.bubble').textContent = text;
  input.value = ''; grow(); stick = true; scrollBottom(true);
  generate();
}
function regenerate() {
  const c = conv(); if (ctrl || !c) return;
  if (c.messages.at(-1)?.role === 'assistant') c.messages.pop();
  box.querySelector('.msg.assistant:last-of-type')?.remove(); generate();
}

async function* mockStream(signal) {
  const txt = '<think>사용자의 요청을 정리하고 예시 코드를 준비한다.</think>좋아요! 간단한 예시를 보여드릴게요.\n\n**핵심 포인트**\n- 시스템 폰트와 넉넉한 여백\n- 부드러운 `스트리밍` 표시\n- 다크 모드 우선\n\n```js\nconst greet = name => `Hello, ${name}!`;\nconsole.log(greet("World"));\n```\n\n더 궁금한 점이 있으면 말씀해 주세요.';
  await new Promise(r => setTimeout(r, 700));
  for (let i = 0; i < txt.length;) { if (signal.aborted) return; const n = 1 + (Math.random() * 4 | 0); yield txt.slice(i, i += n); await new Promise(r => setTimeout(r, 28)); }
}
async function* apiStream(messages, signal, meta) {
  const url = (S.base || '').replace(/\/$/, '') + '/v1/chat/completions';
  const body = { messages, stream: true, stream_options: { include_usage: true } }; if (S.model) body.model = S.model;
  const res = await fetch(url, { method: 'POST', signal, headers: { 'Content-Type': 'application/json', ...(S.key ? { Authorization: 'Bearer ' + S.key } : {}) }, body: JSON.stringify(body) });
  if (!res.ok) { let m = ''; try { m = (await res.json()).error?.message; } catch {} const e = new Error(`${res.status} ${m || res.statusText}`); e.retry = [429, 502, 503, 504].includes(res.status); throw e; }
  const rd = res.body.getReader(), dec = new TextDecoder(); let buf = '', inThink = false;
  for (;;) {
    const { value, done } = await rd.read(); if (done) break;
    buf += dec.decode(value, { stream: true }); let i;
    while ((i = buf.indexOf('\n')) >= 0) {
      const line = buf.slice(0, i).trim(); buf = buf.slice(i + 1);
      if (!line.startsWith('data:')) continue; const d = line.slice(5).trim(); if (d === '[DONE]') return;
      let j; try { j = JSON.parse(d); } catch { continue; }
      if (j.error) throw new Error(j.error.message || '스트림 오류');
      if (j.usage) meta.usage = j.usage;
      const dl = j.choices?.[0]?.delta || {}; const r = dl.reasoning_content || dl.reasoning;
      if (r) { yield (inThink ? '' : '<think>') + r; inThink = true; }
      if (dl.content) { yield (inThink ? '</think>' : '') + dl.content; inThink = false; }
    }
  }
}
async function generate() {
  const c = conv(); const el = addMsg('assistant'); let text = '', raf = 0; const meta = {}; const t0 = performance.now();
  fillAssistant(el, '', true); scrollBottom(true);
  ctrl = new AbortController(); setBusy(true);
  const paint = () => { raf = 0; fillAssistant(el, text, true); if (stick) scrollBottom(); };
  try {
    const msgs = (S.system ? [{ role: 'system', content: S.system }] : []).concat(c.messages.map(m => ({ role: m.role, content: m.content.replace(/^\s*<think>[\s\S]*?<\/think>/, '') })));
    const it = S.mock ? mockStream(ctrl.signal) : apiStream(msgs, ctrl.signal, meta);
    for await (const chunk of it) { text += chunk; if (!raf) raf = requestAnimationFrame(paint); }
  } catch (e) {
    if (e.name !== 'AbortError') { cancelAnimationFrame(raf); if (!text) el.remove(); else fillAssistant(el, text, false); ctrl = null; setBusy(false); return addError(e.message === 'Failed to fetch' ? '서버에 연결할 수 없어요. 설정을 확인하거나 Mock 모드를 켜 보세요.' : e.message, true); }
  }
  cancelAnimationFrame(raf); ctrl = null; setBusy(false);
  const secs = ((performance.now() - t0) / 1000).toFixed(1);
  const usage = meta.usage ? `${meta.usage.completion_tokens} tok · ${(meta.usage.completion_tokens / secs).toFixed(0)} tok/s` : `${secs}s`;
  if (text) { c.messages.push({ role: 'assistant', content: text, usage }); save(); }
  fillAssistant(el, text, false, { usage });
}

/* ---------- drawer & settings ---------- */
const closeDrawer = () => $('#app').classList.remove('open');
$('#menuBtn').onclick = () => $('#app').classList.add('open');
$('#scrim').onclick = closeDrawer;
const newChat = () => { if (ctrl) ctrl.abort(); cur = null; renderAll(); closeDrawer(); if (!isTouch) input.focus(); };
$('#newChat').onclick = $('#newChat2').onclick = newChat;
const dlg = $('#settings');
$('#openSettings').onclick = () => { $('#sBase').value = S.base; $('#sKey').value = S.key; $('#sModel').value = S.model; $('#sSystem').value = S.system; $('#sMock').checked = S.mock; $('#sShowThink').checked = S.showThink; closeDrawer(); dlg.showModal(); };
$('#cancelSettings').onclick = () => dlg.close();
dlg.addEventListener('click', e => { if (e.target === dlg) dlg.close(); });
$('#settingsForm').onsubmit = () => { Object.assign(S, { base: $('#sBase').value.trim(), key: $('#sKey').value.trim(), model: $('#sModel').value.trim(), system: $('#sSystem').value, mock: $('#sMock').checked, showThink: $('#sShowThink').checked }); save(); renderMessages(); };
// first run: no backend reachable on file:// → mock
if (location.protocol === 'file:' && !localStorage.getItem('ref.settings')) S.mock = true;
renderAll();
