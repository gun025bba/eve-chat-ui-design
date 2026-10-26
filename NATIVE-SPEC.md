# NATIVE-SPEC v1 — 홈 화면 PWA를 "진짜 iOS 앱"처럼

대상: `/workspace/llm-chat-ui/` (sw `llmchat-v5`). SPEC.md 토큰/모션 그대로 사용. 기술 기반(standalone 감지, 키보드/visualViewport, manifest, SW)은 프론트 봇이 진행 중이므로 여기서는 **조율에 필요한 부분만** 언급합니다.

## 0. 결정: 탭 바 없음, 내비게이션 스택만 사용
**결정:** `대화 목록(루트) → 채팅(push)` 2단 스택 + 설정은 **시트**. 탭 바(대화/설정)는 만들지 않습니다.
**이유**
1. 탭은 "동등하고 자주 오가는 최상위 영역"용(HIG). 설정은 가끔 들어가는 화면이라 모달 시트가 맞음(메시지·ChatGPT·Claude iOS 앱 모두 같은 구조).
2. 채팅 화면은 하단에 컴포저가 있어서, 탭 바를 두면 하단 크롬이 두 겹이 되고 홈 인디케이터와 겹쳐 세로 공간이 줄어듭니다.
3. 대화 목록이 루트면 "뒤로" 제스처가 자연스럽게 생깁니다. 지금의 햄버거 드로어는 웹/안드로이드 패턴이라 iOS 느낌을 떨어뜨립니다.
**변경:** 모바일(<761px)에서 `#drawer` → **목록 화면 `#listView`**(전체 화면)로 승격, `#main` → **채팅 화면 `#chatView`**. 아이패드/데스크톱(≥761px)은 현재 사이드바 유지(Split View 패턴).
**앱 실행 시:** 마지막으로 연 대화로 바로 들어가고(상태 복원), 그 아래에 목록이 스택으로 깔려 있어 뒤로 스와이프하면 목록이 나옵니다(메시지 앱과 동일).

## 1. 화면 구조 / 마크업 (기존 ID 유지 + 래퍼)
```html
<div id="app" class="nav">                <!-- 고정 앱 셸 -->
  <section id="listView" class="screen">  <!-- 기존 #drawer 내용 이동 -->
    <header class="navbar"><div class="nav-inline-title">대화</div>
      <button id="openSettings" class="icon" aria-label="설정">gear</button>
      <button id="newChat" class="icon" aria-label="새 대화">square.and.pencil</button></header>
    <div class="scroller" id="listScroller">
      <h1 class="large-title">대화</h1>
      <div class="search"><input type="search" placeholder="검색" enterkeyhint="search"></div>
      <ul id="convList"></ul>
    </div>
  </section>
  <section id="chatView" class="screen">  <!-- 기존 #main -->
    <header id="topbar" class="navbar">
      <button id="backBtn" class="nav-back" aria-label="대화 목록">chevron.left <span>대화</span></button>
      <div id="titleWrap">…</div>
      <button id="newChat2" class="icon">…</button></header>
    <div id="messages">…</div> … <form id="composer">…</form>
  </section>
</div>
```
- `.screen{position:absolute;inset:0;overflow:hidden;background:var(--bg)}`. `#menuBtn`/`#scrim`은 모바일에서 제거(≥761px 사이드바에서도 불필요).
- 상태: `#app[data-route="list"|"chat"]`. URL은 `#/c/<id>` 해시로 동기화하고 `history.pushState`/`popstate`로 하드웨어 뒤로가기·히스토리와 일치시킵니다(standalone에는 브라우저 뒤로 버튼이 없으니 앱 내 뒤로가기가 필수).

## 2. 내비게이션 바 & 라지 타이틀
- 내비게이션 바 높이 44 + `env(safe-area-inset-top)`, 블러 머티리얼(SPEC §6.1). 뒤로 버튼은 `chevron.left`(17pt 굵게) + 이전 화면 이름 “대화”, `--accent` 색, 터치 영역 44, 왼쪽 패딩 8.
- **목록 화면 라지 타이틀**: 34/41 Bold, letter-spacing -.022em, 좌측 정렬 20px. 스크롤하면 축소:
```js
const lt = $('#listView .large-title'), nav = $('#listView .navbar');
new IntersectionObserver(([e]) => nav.classList.toggle('collapsed', !e.isIntersecting),
  { root: $('#listScroller'), rootMargin: '-52px 0px 0px 0px' }).observe(lt);
// 부드러운 비율 효과(선택): scroll에서 rAF로
scroller.addEventListener('scroll', () => requestAnimationFrame(() => {
  const y = scroller.scrollTop; lt.style.transform = y < 0 ? `scale(${1 + Math.min(-y, 60) / 600})` : ''; // 오버스크롤 시 살짝 확대(iOS처럼)
}), { passive: true });
```
```css
.navbar .nav-inline-title{opacity:0;transform:translateY(4px);transition:opacity var(--d-fast) linear,transform var(--d-fast) var(--ease-out);font:600 17px/22px var(--font)}
.navbar.collapsed .nav-inline-title{opacity:1;transform:none}
.navbar.collapsed{box-shadow:0 .5px 0 var(--separator)}
.navbar:not(.collapsed){background:transparent;-webkit-backdrop-filter:none;backdrop-filter:none}
.large-title{font:700 34px/41px var(--font);letter-spacing:-.022em;margin:0;padding:4px 20px 8px;transform-origin:left center}
```
- 채팅 화면은 인라인 타이틀만(현재 `#title` + `#modelName` 유지).

## 3. 대화 목록(루트) 디자인
- iOS 인셋 그룹 대신 **plain 리스트**(메시지 앱 스타일): 행 높이 64~72, 왼쪽 패딩 20. 1줄 제목 17/600, 2줄째에 마지막 답변 미리보기 15 `--label-2`(1줄 말줄임), 오른쪽 상단 시간 15 `--label-2`(오늘=“오후 3:12”, 어제=“어제”, 그 외 “10월 21일”), 오른쪽 `chevron.right` 13 `--label-3`.
- 구분선은 hairline, 왼쪽 20 인셋(마지막 행 없음). 날짜 그룹 라벨은 유지(13/600 `--label-2`, 대문자 변환 안 함).
- 검색창: 36px, `--fill`, r10, 돋보기 아이콘, 17px(줌 방지). 제목/내용으로 필터링.
- 빈 목록: 가운데 “대화 없음” 22/700 + “새 대화를 시작해 보세요” 15 `--label-2` + 버튼.
- **스와이프 액션**(행을 왼쪽으로 밀기): 삭제(빨강 `--danger`) · 이름 변경(회색 `#8E8E93`). 버튼 폭 각 74, 끝까지 밀면 삭제(full swipe). 기존 ✎/🗑 아이콘 버튼은 제거합니다.
- **풀 투 리프레시는 목록에 쓰지 않습니다**(로컬 데이터라 새로 불러올 게 없음). 대신 채팅에서 위로 당기면 이전 메시지가 이미 다 있으므로 역시 불필요합니다. 단, 설정 시트의 모델 목록은 "불러오기" 버튼을 유지합니다. ⇒ 정당한 사용처가 없으므로 구현하지 않습니다.

## 4. Push / Pop 전환 (핵심)
**사양(UINavigationController 재현)**
| 항목 | 값 |
|---|---|
| 들어오는 화면 | translateX(100%) → 0 |
| 나가는 화면 | 0 → translateX(-30%) (패럴랙스 30%) + 어둡게 `rgba(0,0,0,.1)` → 다크에서는 `.25` 오버레이 |
| 들어오는 화면 왼쪽 그림자 | `box-shadow:-8px 0 24px rgba(0,0,0,.25)` |
| 시간 | push 420ms / pop 380ms (손가락 놓은 뒤 남은 거리 비례: `max(180, 380×남은비율)`) |
| 커브 | `cubic-bezier(.32,.72,0,1)` (`--ease-sheet`와 동일, iOS 기본과 가장 비슷) |
| 내비게이션 바 | 타이틀 크로스페이드 + 뒤로 버튼 라벨 슬라이드(-40%→0), 200ms |

**구현: View Transitions API 우선, 폴백은 CSS 클래스 전환**
```js
function navigate(route, { dir = 'push', id } = {}) {
  const apply = () => { app.dataset.route = route; if (id) openConv(id); };
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) return apply();
  if (document.startViewTransition) {           // iOS 18+ Safari 지원
    document.documentElement.dataset.dir = dir;
    document.startViewTransition(apply);
  } else fallbackSlide(route, dir, apply);
}
```
```css
#listView{view-transition-name:list} #chatView{view-transition-name:chat}
::view-transition-group(*){animation-duration:420ms;animation-timing-function:cubic-bezier(.32,.72,0,1)}
[data-dir=push]::view-transition-new(chat){animation:slideIn 420ms cubic-bezier(.32,.72,0,1) both}
[data-dir=push]::view-transition-old(list){animation:parallaxOut 420ms cubic-bezier(.32,.72,0,1) both}
[data-dir=pop]::view-transition-old(chat){animation:slideIn 380ms cubic-bezier(.32,.72,0,1) reverse both}
[data-dir=pop]::view-transition-new(list){animation:parallaxOut 380ms cubic-bezier(.32,.72,0,1) reverse both}
@keyframes slideIn{from{transform:translateX(100%)}}
@keyframes parallaxOut{to{transform:translateX(-30%);filter:brightness(.75)}}
```
폴백(그리고 **스와이프 백은 항상 이 방식**): 두 화면 모두 렌더된 상태에서 `transform`만 조작.
```css
.screen{transition:transform var(--nav-d,420ms) var(--ease-sheet);will-change:transform}
#app[data-route=list] #chatView{transform:translateX(100%)}
#app[data-route=chat] #listView{transform:translateX(-30%)}
#listView::after{content:"";position:absolute;inset:0;background:#000;opacity:0;pointer-events:none;transition:opacity var(--nav-d,420ms) var(--ease-sheet)}
#app[data-route=chat] #listView::after{opacity:.25}
#chatView{box-shadow:-8px 0 24px rgba(0,0,0,.25)}
```
- 전환 중 `#app.transitioning{pointer-events:none}` 로 연타 방지.
- 숨겨진 화면은 전환 끝나면 `visibility:hidden; inert` (VoiceOver/탭 포커스 차단).

## 5. 엣지 스와이프 백 (손가락 추적)
- 시작 영역: 화면 왼쪽 **24px** (`env(safe-area-inset-left)` 더함). 가로 이동이 세로보다 커질 때만 잡음(8px 임계).
- iOS Safari 자체의 "뒤로 스와이프"와 충돌: standalone에서는 Safari 제스처가 없으므로 문제없음. 브라우저 탭에서는 Safari 제스처가 우선하므로 **standalone에서만 활성화**.
```js
let g = null; const W = () => innerWidth;
chatView.addEventListener('touchstart', e => {
  const t = e.touches[0]; if (app.dataset.route !== 'chat' || t.clientX > 24) return;
  g = { x0: t.clientX, y0: t.clientY, t0: performance.now(), lock: null, dx: 0 };
}, { passive: true });
chatView.addEventListener('touchmove', e => {
  if (!g) return; const t = e.touches[0], dx = t.clientX - g.x0, dy = t.clientY - g.y0;
  if (!g.lock) { if (Math.hypot(dx, dy) < 8) return; g.lock = Math.abs(dx) > Math.abs(dy) ? 'x' : 'y'; if (g.lock === 'x') app.classList.add('dragging'); }
  if (g.lock !== 'x') return; e.preventDefault();
  g.dx = Math.max(0, dx); const p = g.dx / W();
  chatView.style.transform = `translateX(${g.dx}px)`;
  listView.style.transform = `translateX(${-30 + 30 * p}%)`;
  listView.style.setProperty('--dim', .25 * (1 - p));
}, { passive: false });
chatView.addEventListener('touchend', () => {
  if (!g || g.lock !== 'x') return (g = null);
  const v = g.dx / (performance.now() - g.t0);           // px/ms
  const back = g.dx > W() * .5 || v > .5;                 // 절반 이상 또는 빠른 플릭
  const remain = back ? 1 - g.dx / W() : g.dx / W();
  app.style.setProperty('--nav-d', Math.max(180, 380 * remain) + 'ms');
  app.classList.remove('dragging'); chatView.style.transform = listView.style.transform = ''; listView.style.removeProperty('--dim');
  if (back) history.back(); else app.dataset.route = 'chat';
  g = null;
});
```
```css
#app.dragging .screen{transition:none}
#listView::after{opacity:var(--dim)}  /* 드래그 중 */
```
- 키보드가 열린 상태에서 스와이프 시작 → `input.blur()` 먼저.
- 스트리밍 중 뒤로 가도 생성은 계속(목록 행에 "답변 중…" 표시 + 작은 회전 인디케이터).

## 6. 시트 (설정 / 설치 안내 / 액션)
- **디텐트**: `medium`(화면 높이 50%) / `large`(상단 safe-area + 10px 남김). 설정 = large, 설치 안내 = medium(콘텐츠 높이에 맞춤), 모델 선택 = medium→large.
- 등장 스프링: `transform: translateY(100%) → 0`, 500ms `cubic-bezier(.32,.72,0,1)`; 뒤 화면 `#app`은 scale(.94) + r10 + brightness(.8)  (iOS "카드" 효과, large에서만).
- 드래그로 닫기: grabber 또는 시트 상단 56px(또는 스크롤 위치 0일 때 콘텐츠)에서 아래로 드래그 → 1:1 추적, 위로 드래그는 고무줄(`dy*0.2`). 놓을 때 `dy > 높이×0.3` 또는 속도 > 0.6px/ms면 닫힘, 아니면 원위치 스프링 300ms. medium↔large는 가장 가까운 디텐트로 스냅.
```js
function sheetDrag(sheet, onClose) {
  let y0, t0, dy = 0, h;
  const grab = sheet.querySelector('.grabber, .sheet-head');
  grab.addEventListener('touchstart', e => { y0 = e.touches[0].clientY; t0 = performance.now(); h = sheet.offsetHeight; sheet.style.transition = 'none'; }, { passive: true });
  grab.addEventListener('touchmove', e => { dy = e.touches[0].clientY - y0; const y = dy < 0 ? dy * .2 : dy; sheet.style.transform = `translateY(${y}px)`; document.body.style.setProperty('--sheet-p', 1 - Math.max(0, dy) / h); }, { passive: true });
  grab.addEventListener('touchend', () => {
    const v = dy / (performance.now() - t0); sheet.style.transition = '';
    if (dy > h * .3 || v > .6) { sheet.style.transform = 'translateY(100%)'; sheet.addEventListener('transitionend', onClose, { once: true }); }
    else sheet.style.transform = ''; dy = 0;
  });
}
```
- `dialog`를 계속 쓰되 `::backdrop` 투명도는 `--sheet-p`로 연동. 시트 안 스크롤은 `overscroll-behavior:contain`.
- 시트 상단 내비게이션: 왼쪽 “취소”, 가운데 제목 17/600, 오른쪽 “완료”(600, `--accent`). 저장 버튼 대신 “완료”로 통일(iOS 설정 시트 관례). 변경 사항이 있을 때 드래그로 닫으면 확인 액션 시트(“변경 사항 폐기”) 표시.

## 7. 컨텍스트 메뉴 / 길게 누르기
- 대상: 사용자 메시지, 어시스턴트 답변, 목록 행, 코드블록.
- 트리거: 500ms 길게 누르기(이동 10px 넘으면 취소), 데스크톱 우클릭.
- 표시(iOS 컨텍스트 메뉴 재현): 배경 블러 `backdrop-filter: blur(24px)` + 어둡게 .35, 눌린 요소 **복제본**을 원래 위치에서 scale(1.02)로 띄움(250ms spring `cubic-bezier(.34,1.36,.64,1)`), 그 아래/위에 메뉴(폭 250, r13, `rgba(30,30,32,.82)` 블러, 행 44, 15px 텍스트 + 오른쪽 SF 스타일 아이콘, hairline 구분, 파괴적 항목 `--danger`).
- 메뉴 항목: 사용자 메시지 = 복사 · 수정 후 다시 보내기 · 삭제 / 답변 = 복사 · 다시 생성 · 공유(`navigator.share`) · 텍스트 선택 / 목록 행 = 이름 변경 · 고정 · 삭제 / 코드 = 코드 복사 · 공유.
- 길게 누르기 시작 시 요소 scale(.97) 150ms로 "눌림 예고"(햅틱 대체). 닫기: 바깥 탭, 180ms 페이드.
```js
function longPress(el, cb) { let t, x, y;
  el.addEventListener('touchstart', e => { ({ clientX: x, clientY: y } = e.touches[0]); el.classList.add('pressing'); t = setTimeout(() => { el.classList.remove('pressing'); cb(el); }, 500); }, { passive: true });
  const cancel = () => { clearTimeout(t); el.classList.remove('pressing'); };
  el.addEventListener('touchmove', e => { const p = e.touches[0]; if (Math.hypot(p.clientX - x, p.clientY - y) > 10) cancel(); }, { passive: true });
  el.addEventListener('touchend', cancel); el.addEventListener('contextmenu', e => { e.preventDefault(); cancel(); cb(el); });
}
```
- 기본 iOS 콜아웃 차단: 메시지 요소에 `-webkit-touch-callout:none; -webkit-user-select:none` (메뉴의 "텍스트 선택"을 누르면 해당 요소만 `user-select:text` 허용 모드로 전환).

## 8. 터치 피드백 (햅틱 대체)
iOS 웹은 `navigator.vibrate` 미지원 → **시각적 피드백 + 예외적 실제 햅틱**.
| 요소 | 눌림 | 해제 |
|---|---|---|
| 아이콘 버튼 `.icon`, `.nav-back` | opacity .35, 0ms (iOS 내비게이션 바는 축소가 아니라 흐려짐) | 200ms 복귀 |
| 목록 행 `#convList li` | 배경 `--fill` 즉시 | 300ms 페이드 아웃 (push 후에도 돌아오면 잠깐 하이라이트) |
| 채움 버튼 `.primary`, `.send`, `.chip` | scale(.96) + brightness(.9) 100ms | 스프링 180ms |
| 스위치 | 노브 폭 27→33 늘어남 (iOS 동작) | |
| 컨텍스트 메뉴 진입 | scale(.97) 150ms → 1.02 팝 | |
- `:active`는 iOS에서 `touchstart` 리스너가 있어야 작동 → `document.addEventListener('touchstart',()=>{}, {passive:true})` 한 줄 추가.
- 스크롤 중 눌림 표시가 깜빡이지 않게 행 하이라이트는 80ms 지연(`transition-delay:80ms` on 진입만).
- **실제 햅틱**: iOS 18+ Safari에서 `<input type="checkbox" switch>` 토글은 시스템 햅틱을 냄. 설정 스위치는 반드시 이 요소 사용. (숨겨진 switch를 프로그래밍으로 클릭해 햅틱을 내는 트릭은 동작이 불안정·비공식이므로 쓰지 않음.)

## 9. 상태바 & safe area (조율 포인트만)
- `black-translucent` + `viewport-fit=cover` 유지 → 콘텐츠가 상태바 밑까지. 내비게이션 바 블러가 상태바 영역도 덮도록 `padding-top:env(safe-area-inset-top)` 포함 높이.
- 라이트 모드에서도 `black-translucent`면 상태바 글자가 흰색이라 안 보임 → 라이트에서는 내비게이션 바 블러 배경(흰 72%) 위에 표시되므로 **상단에 항상 블러 바가 있어야 함**. 라지 타이틀 상태(투명 바)에서도 상단 safe-area 영역에는 `--bg` 채움을 둡니다: `.navbar:not(.collapsed)::before{content:"";position:absolute;inset:0 0 auto;height:env(safe-area-inset-top);background:var(--bg)}`. (iOS PWA는 상태바 글자색을 동적으로 바꿀 수 없음.)
- 가로 모드: 노치 쪽 `env(safe-area-inset-left/right)`를 내비게이션 바·목록 행·메시지·컴포저 좌우 패딩에 `max(20px, env(...))`로 적용(이미 메시지/컴포저는 적용됨 → 목록 행·navbar 추가).
- 홈 인디케이터: 컴포저 하단 `max(8px, env(safe-area-inset-bottom))` 유지, **키보드가 열리면** 인디케이터가 사라지므로 `body.kb-open #composer{padding-bottom:8px}` (프론트 봇의 visualViewport 로직에서 `kb-open` 클래스만 토글해 주세요: `innerHeight - vv.height > 120`).
- 목록 화면 하단도 `padding-bottom: calc(env(safe-area-inset-bottom) + 20px)`.

## 10. 앱다운 레이아웃 원칙
- 고정 앱 셸: `html,body{position:fixed;inset:0;overflow:hidden;overscroll-behavior:none}`; 스크롤은 `.scroller`/`#messages`만, 각각 `overscroll-behavior-y:contain` (바운스는 내부 스크롤러에서만 일어나게 → 앱처럼 보임).
- 크롬 텍스트 선택 금지: `.navbar,.icon,button,#convList,.chip,.large-title{-webkit-user-select:none;user-select:none;-webkit-touch-callout:none}`. 메시지 본문은 컨텍스트 메뉴의 "텍스트 선택"으로만.
- `img,svg{-webkit-user-drag:none;pointer-events:none}`(아이콘 안 svg가 탭 대상이 되지 않게).
- 링크: 답변 속 외부 링크는 standalone에서 앱 밖(Safari)으로 열림 → `target="_blank"` 유지(현재 OK). 앱 내부 이동은 링크 대신 버튼으로.
- 실행 깜빡임 방지: `<html style="background:#000">` 인라인 + `<meta name="color-scheme" content="dark light">`, CSS 로드 전 흰 화면 방지. 초기 렌더는 상태 복원 후 `#app`에 `.ready` 클래스 → 그때 200ms 페이드인(스플래시 → 앱이 끊김 없이).
- **상태 복원**: `LS.current`(이미 있음) + 추가로 `route`, `#messages.scrollTop`, 컴포저 초안(`draft:<id>`)을 `visibilitychange(hidden)`/`pagehide`에서 저장. iOS는 백그라운드 PWA를 자주 종료하므로 재실행 시 같은 대화·같은 스크롤·초안을 그대로 복원.
- 오프라인: `navigator.onLine`/fetch 실패 시 내비게이션 바 아래 **얇은 배너**(32px, `--bg-elev`, 13px “오프라인 — Tailscale 연결을 확인하세요”, wifi.slash 아이콘) 슬라이드 다운 280ms. 컴포저는 비활성화하지 않고 보낼 때 오류 처리(기존 재시도).

## 11. 홈 화면 추가 안내 시트
**조건:** iOS Safari + 비 standalone (`!(matchMedia('(display-mode: standalone)').matches || navigator.standalone)`) + 아직 닫지 않음 + 두 번째 방문 또는 첫 대화 완료 후(첫 실행에 바로 띄우지 않음).
**디자인 (medium 시트, 콘텐츠 높이):**
```
 ───── (grabber)
 [앱 아이콘 64px, r14, 그림자]
 홈 화면에 추가하기            ← 22/700
 전체 화면으로, 앱처럼 빠르게 열 수 있어요   ← 15 --label-2, 가운데
 ┌─────────────────────────────┐   ← --bg-elev-2, r12
 │ ① [share 아이콘] 아래 공유 버튼을 누르고  │  17, 행 52
 │ ② [plus.square] '홈 화면에 추가' 선택     │
 │ ③ 오른쪽 위 '추가'                         │
 └─────────────────────────────┘
 [ 나중에 ]  ← 텍스트 버튼 17 --accent
```
- 단계 번호는 24px 원(`--fill`, 13/600). Safari 공유 아이콘은 SF 스타일 SVG(사각형 + 위 화살표).
- iPhone은 공유 버튼이 하단 툴바(또는 iOS 26 하단 탭 바의 ··· 메뉴) → 시트 아래쪽에 작은 아래 화살표가 1.5s 간격으로 살짝 바운스(reduced-motion 시 정지). iPad는 상단이므로 화살표 숨김.
- 닫기: “나중에”, 드래그, 배경 탭 → `localStorage['a2hs.dismissed']=Date.now()`; **30일 동안 다시 안 띄움**. 설치 후(standalone 진입) 키 영구 `installed`.
- 설정 시트 하단에도 "홈 화면에 추가 방법" 행 상시 제공(비 standalone일 때만).
```js
const standalone = matchMedia('(display-mode: standalone)').matches || navigator.standalone;
const iOS = /iP(hone|ad|od)/.test(navigator.userAgent) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
const d = +localStorage.getItem('a2hs.dismissed') || 0;
if (iOS && !standalone && Date.now() - d > 30 * 864e5 && +localStorage.getItem('visits') >= 2) openSheet('#a2hs', 'medium');
```

## 12. 아이콘 & 스플래시
**아이콘 디자인**
- 개념: SPEC 빈 상태의 컬러 원(`.mark`)과 같은 아이덴티티 — **검정 배경 위 원뿔형 그라디언트 구(#0A84FF→#BF5AF2→#FF375F→#FF9F0A)**, 가운데 흰색 sparkle(4갈래 별) 혹은 말풍선 실루엣 1개. 텍스트 없음.
- 크기: 1024 마스터 → 180(apple-touch-icon), 192, 512, 512 maskable(안전 영역 80% 원 안에 모든 요소). iOS는 자동으로 모서리를 둥글게 처리하므로 **투명도·라운드 없이 꽉 찬 정사각형**으로 내보냄(투명 PNG는 iOS에서 검정 배경 처리).
- iOS 18 다크/틴트 아이콘은 PWA에서 지정 불가 → 검정 배경 아이콘이 다크 홈 화면에서도 자연스럽게 어울림.
- manifest: `"icons"`에 `purpose:"any"`와 `"maskable"`을 **별도 항목으로 분리**(현재 `"any maskable"` 하나로 합쳐져 있음 → any 용도에서 여백이 과하게 잘림).

**스플래시(apple-touch-startup-image)**
- iOS는 manifest로 스플래시를 만들지 않음 → 기기별 `<link rel="apple-touch-startup-image" media="…">` 필요. 없으면 흰 화면이 번쩍임.
- 디자인: 배경 `#000`(라이트 모드용은 `#fff` 별도 세트, `prefers-color-scheme` media 포함), 정중앙에 아이콘의 구만 120pt, 텍스트 없음 → 앱 첫 화면(빈 상태의 `.mark`)과 같은 위치·크기면 **스플래시→앱이 이어지는 느낌**.
- 생성: 하나의 SVG/HTML에서 스크립트로 일괄 생성(예: `npx pwa-asset-generator icon.svg icons/splash --background "#000" --splash-only --portrait-only` 또는 Playwright로 캡처). 최소 세트(세로): 1320×2868(16 Pro Max), 1206×2622(16 Pro), 1290×2796(15/16 Plus·Pro Max), 1179×2556(15/16·Pro), 1284×2778, 1170×2532, 1125×2436, 828×1792, 750×1334. 아이패드는 선택.
```html
<link rel="apple-touch-startup-image" media="(device-width: 393px) and (device-height: 852px) and (-webkit-device-pixel-ratio: 3) and (orientation: portrait) and (prefers-color-scheme: dark)" href="icons/splash/1179x2556-dark.png">
```

## 13. 모션 표 (NATIVE 추가분)
| 대상 | 시간 | 커브 |
|---|---|---|
| push | 420ms | cubic-bezier(.32,.72,0,1) |
| pop(버튼) | 380ms | 동일 |
| pop(스와이프 놓은 후) | max(180, 380×남은비율) | 동일 |
| 패럴랙스 / 어둡게 | -30% / .25 | 동기화 |
| 라지 타이틀 → 인라인 | 180ms | opacity linear + translateY ease-out |
| 시트 등장 | 500ms | cubic-bezier(.32,.72,0,1) |
| 시트 닫힘 | 300ms | cubic-bezier(.32,.72,0,1) |
| 시트 복귀(스냅) | 300ms | cubic-bezier(.34,1.36,.64,1) |
| 뒤 화면 카드 축소 | 500ms, scale .94, r10 | 시트와 동일 |
| 컨텍스트 메뉴 | 250ms 팝 / 180ms 닫힘 | spring / ease-out |
| 오프라인 배너 | 280ms | ease-out |
| 앱 첫 페이드인 | 200ms | ease-out |
**reduced-motion:** push/pop은 슬라이드 대신 150ms 크로스페이드, 시트는 페이드, 패럴랙스·스케일·바운스 화살표·shimmer 끔. 제스처 추적(손가락 따라오기)은 사용자가 직접 움직이는 것이므로 유지.

## 14. 구현 순서
1. **셸/라우팅**: `#listView`/`#chatView` 분리, `data-route`, history/hash 동기화, 상태 복원(route·스크롤·초안), 첫 페인트 깜빡임 제거. (사이드바 ≥761px 유지)
2. **목록 화면**: 라지 타이틀 축소, 검색, 행 디자인, 빈 목록.
3. **push/pop 전환**: CSS 폴백 먼저 → View Transitions 추가 → reduced-motion.
4. **엣지 스와이프 백**(standalone 한정).
5. **시트 시스템**: 설정을 디텐트 시트로(취소/완료), 드래그로 닫기, 뒤 화면 카드 효과.
6. **터치 피드백** 정리(§8) + 크롬 user-select/callout.
7. **컨텍스트 메뉴/길게 누르기** + 목록 스와이프 액션.
8. **아이콘·스플래시·manifest 아이콘 분리**, 홈 화면 추가 안내 시트.
9. **오프라인 배너**, `kb-open` 하단 패딩, 가로 모드 패딩 점검.
10. sw `CACHE` → `llmchat-v6`, 실기기(standalone) QA: 스와이프, 키보드, 시트, 회전, 백그라운드 복귀.

## 15. iOS PWA 알려진 제약
- 햅틱 API 없음(`navigator.vibrate` 미지원). switch 체크박스만 시스템 햅틱.
- 상태바 글자색은 실행 시 고정(동적 변경 불가). `theme-color` 동적 변경은 Safari 탭에서만 의미 있음.
- 스플래시는 기기별 이미지가 정확히 일치해야 표시. 새 기기 해상도는 매번 추가 필요.
- standalone에는 뒤로/새로고침 버튼 없음 → 앱 내 뒤로가기와 "당겨서 새로고침"이 없으면 멈춘 것처럼 느껴질 수 있음 (오류 화면에 "다시 시도" 버튼 필수).
- 스토리지: PWA와 Safari 탭은 **저장소가 분리**됨 → 홈 화면 앱에서 API 키·대화를 다시 설정해야 함. 설치 안내 시트에 이 사실 한 줄 표시. 오랫동안 안 쓰면(7일 정책) Safari 탭 데이터는 지워질 수 있지만 홈 화면 앱은 예외.
- 백그라운드로 가면 스트리밍 fetch가 몇 초 내 중단될 수 있음 → 복귀 시(`visibilitychange`) 끊긴 답변에 "이어서 생성" 버튼 표시.
- 서비스워커/오프라인 캐시는 HTTPS에서만(현재 HTTP :8000이면 캐시 없음) → `tailscale serve` HTTPS 주소로 설치 권장. 설치한 주소(origin)가 바뀌면 저장소도 새로 시작.
- 푸시 알림은 iOS 16.4+에서 홈 화면 앱만 가능(이번 범위 외).
- `startViewTransition`은 iOS 18+ Safari. 그 이전은 CSS 폴백.
- 외부 링크는 Safari로 빠져나감(앱 내 브라우저 없음).
- `100vh` 버그는 고정 셸 + `--vvh`로 이미 회피.
