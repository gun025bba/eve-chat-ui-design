# LLM Chat UI — 디자인 스펙 v1 (Apple 스타일, 다크 우선)

대상: `llm-chat-ui/` (no-build vanilla, iPhone Safari, `/ui/` 서빙). 클래스명/ID는 **기존 코드 그대로** 유지하고 스타일·마크업 일부만 보강합니다. 레퍼런스 구현: `reference/` (index.html, styles.css, app.js — mock 모드 포함).

## 0. 원칙
1. **콘텐츠가 주인공** — 크롬(헤더/입력창)은 반투명·얇게, 답변 텍스트가 화면을 지배.
2. **타이포가 위계를 만든다** — 선·박스 대신 크기/굵기/색 대비로 구분. 테두리 최소화(hairline 0.5px).
3. **여백은 리듬** — 8pt 그리드, 메시지 간 24px, 본문 행간 1.55.
4. **물리적인 모션** — 짧고(≤350ms) 스프링 느낌, 눌림은 즉각(scale .96).
5. **네이티브처럼** — safe-area, 100dvh, 키보드 대응, 탭 하이라이트 제거, 16px 이상 입력.
6. 이모지/유니코드 아이콘(☰ ＋ ↑ ■ ⚙︎ ✎ 🗑) → **인라인 SVG(SF Symbols 느낌, stroke 1.75~2)** 로 교체.

## 1. 색상 토큰 (`:root` 기본 = 다크, `prefers-color-scheme: light`에서 라이트)
| 토큰 | Dark | Light | 용도 |
|---|---|---|---|
| --bg | #000000 | #FFFFFF | 앱 배경(OLED 블랙) |
| --bg-elev | #1C1C1E | #F2F2F7 | 입력창, 시트, 드로어 |
| --bg-elev-2 | #2C2C2E | #E5E5EA | 코드블록 헤더, 칩, 눌림 |
| --fill | rgba(120,120,128,.24) | rgba(120,120,128,.12) | 인라인 코드, 아이콘 버튼 배경 |
| --label | #F5F5F7 | #1D1D1F | 본문 |
| --label-2 | rgba(235,235,245,.62) | rgba(60,60,67,.62) | 보조 텍스트 |
| --label-3 | rgba(235,235,245,.32) | rgba(60,60,67,.32) | placeholder, usage |
| --separator | rgba(84,84,88,.6) | rgba(60,60,67,.18) | hairline |
| --accent | #0A84FF | #007AFF | 전송 버튼, 링크, 포커스 |
| --user-bubble | #2C2C2E | #E9E9EB | 사용자 버블 (파란색 대신 중립 → 프리미엄 톤) |
| --user-fg | #F5F5F7 | #1D1D1F | |
| --danger | #FF453A | #FF3B30 | 중지·오류 |
| --code-bg | #111113 | #F6F6F8 | 코드블록 본문 |
| --material | rgba(22,22,24,.72) | rgba(255,255,255,.72) | 헤더/입력 영역 블러 배경 |
| --scrim | rgba(0,0,0,.5) | rgba(0,0,0,.25) | 드로어/시트 배경 |

`theme-color`: dark `#000000`, light `#FFFFFF`. `color-scheme: dark light`.

## 2. 타이포그래피
`--font: -apple-system, BlinkMacSystemFont, "SF Pro Text", "SF Pro Display", "Apple SD Gothic Neo", system-ui, sans-serif;`
`--mono: ui-monospace, "SF Mono", Menlo, monospace;`
| 토큰 | size/line | weight | 용도 |
|---|---|---|---|
| --t-large | 28/34 | 700, letter-spacing -.02em | 빈 화면 타이틀 |
| --t-title | 17/22 | 600 | 헤더 #title, 시트 제목 |
| --t-body | 17/1.55 | 400 | 답변 본문, 사용자 버블 |
| --t-input | 17/22 | 400 | #input (≥16px 필수 → 줌 방지) |
| --t-callout | 15/20 | 400 | 대화 목록, 칩, 설정 라벨 |
| --t-footnote | 13/18 | 400 | think 본문, 코드 헤더, 메타 |
| --t-caption | 11/13 | 500 | usage, 섹션 라벨(대문자 X, 한국어) |
| 코드 | 14/1.5 mono | | 블록 / 인라인 0.88em |
`-webkit-font-smoothing: antialiased; text-rendering: optimizeLegibility; -webkit-text-size-adjust:100%`. 제목은 `text-wrap: balance`, 본문 `overflow-wrap:anywhere`.

## 3. 간격·반경
- spacing: `--s1 4 · --s2 8 · --s3 12 · --s4 16 · --s5 20 · --s6 24 · --s8 32 · --s10 40 · --s12 48`
- 페이지 좌우 패딩 20px (+safe-area), 본문 최대폭 720px 중앙.
- 메시지 간 24px, 같은 역할 연속 12px. 문단 간 0.75em.
- radii: `--r-xs 6`(인라인 코드) `--r-sm 10`(버튼, 목록 항목) `--r-md 14`(코드블록) `--r-lg 20`(사용자 버블, 칩) `--r-xl 24`(입력 필드) `--r-sheet 16`(시트 상단) `--r-full 999`.
- 터치 타깃 최소 44×44.

## 4. 모션
| 토큰 | 값 |
|---|---|
| --d-instant | 100ms (press) |
| --d-fast | 180ms (hover/색 전환, 아이콘 교체) |
| --d-base | 280ms (메시지 등장, 칩) |
| --d-slow | 380ms (드로어, 시트) |
| --ease-out | cubic-bezier(.22,1,.36,1) — 기본 |
| --ease-spring | cubic-bezier(.34,1.36,.64,1) — 약한 오버슈트(버튼 등장, 스크롤 버튼) |
| --ease-sheet | cubic-bezier(.32,.72,0,1) — iOS 시트/드로어 |
- 메시지 등장: `opacity 0→1, translateY(8px)→0`, 280ms ease-out.
- 스트리밍 토큰: 새 텍스트 덩어리 `opacity .35→1` 220ms (아래 7.4).
- 눌림: `:active{transform:scale(.96)}` 100ms, 해제 180ms spring. 
- `@media (prefers-reduced-motion: reduce)`: 모든 transition/animation 0.01ms, 타이핑 점은 정적 opacity, 블러 유지.

## 5. 레이아웃 셸 (`#app`, `#main`)
- `html,body{height:100%; background:var(--bg); overscroll-behavior:none}` ; `#app{height:100dvh}` (fallback 100vh) + JS로 `--vvh` = `visualViewport.height` 갱신해 키보드 시 `#app{height:var(--vvh)}`.
- `#messages`는 유일한 스크롤 영역. 헤더/컴포저는 `position:absolute`로 위에 떠 있고, `#messages`에 `padding-top: header높이+safe-top`, `padding-bottom: 컴포저높이(ResizeObserver로 --composer-h)`.
- `* { -webkit-tap-highlight-color: transparent }`, 버튼 `touch-action:manipulation; user-select:none`.

## 6. 컴포넌트

### 6.1 헤더 `#topbar`
- 높이 44 + `env(safe-area-inset-top)`. 배경 `--material` + `backdrop-filter: saturate(180%) blur(20px)` (+`-webkit-`). 하단 hairline은 **스크롤됐을 때만** (`#topbar.scrolled{box-shadow:0 .5px 0 var(--separator)}`).
- 구성: `#menuBtn`(sidebar SVG) · `#title`(17/600, 한 줄 말줄임, 아래 모델명 11px --label-3 `<small id="modelName">` 선택) · `#newChat2`(square.and.pencil SVG).
- `.icon`: 44×44, 배경 투명, 아이콘 22px --label, active시 `--fill` 배경 + scale .92.

### 6.2 대화 목록 드로어 `#drawer` + `#scrim`
- 모바일: 폭 `min(84vw, 320px)`, `--bg-elev`, `translateX(-100%)` → `#app.open` 시 0, 380ms `--ease-sheet`. `#main`은 함께 `translateX(24px)` + scale(.98) (선택, 깊이감).
- `#scrim`: 항상 렌더, `opacity 0; pointer-events:none` → open 시 opacity 1. (현재 `display:none` 토글은 페이드가 안 되므로 교체.)
- 상단: "대화" 타이틀 28/700 + 새 대화 버튼(아이콘). 목록 항목 `#convList li`: 높이 44, 패딩 0 12, 15px, `--r-sm`; `.active` = `--bg-elev-2`. 이름 변경/삭제 버튼은 평소 숨김 → `li.active`일 때만 노출(또는 길게 누름). 날짜 그룹 라벨(오늘/어제/지난 7일) 13px --label-2 권장.
- 하단 `.drawer-foot`: 설정 버튼(gearshape SVG + "설정"), safe-area-bottom.
- 스와이프: 왼쪽 가장자리 20px에서 오른쪽 드래그로 열기, 드로어에서 왼쪽 드래그로 닫기(선택, pointer events).
- ≥761px: 고정 사이드바, hairline 오른쪽 경계.

### 6.3 메시지 목록 `#messages`
- 내부 `.msg{max-width:720px; margin:0 auto}`; 등장 애니메이션 `.msg{animation:msgIn var(--d-base) var(--ease-out)}`.
- 히스토리 렌더 시엔 애니메이션 끔 (`#messages.no-anim .msg{animation:none}`).

### 6.4 사용자 메시지 `.msg.user .bubble`
- 오른쪽 정렬, `max-width:82%`, 패딩 10/16, `--r-lg` (오른쪽 아래 모서리 6 — `border-bottom-right-radius:6px`), `--user-bubble`, 17px, `white-space:pre-wrap`.
- 길게 누르면/탭하면 아래 "복사 · 편집" 액션(선택).

### 6.5 어시스턴트 메시지 `.msg.assistant .bubble`
- **버블 없음**: 배경 transparent, 패딩 0, 전체 폭, 17/1.55 --label. (마크업 클래스는 `.bubble` 유지, 의미상 "content")
- 마크다운: p margin .75em 0, h1~h3 = 22/20/17 600, ul/ol padding-left 1.4em, li margin .3em, `strong` 600, blockquote 왼쪽 3px --separator, 링크 --accent.
- 인라인 `code`: mono .88em, `--fill`, 패딩 .1em .35em, `--r-xs`.
- 하단 액션 바 `.actions` (스트리밍 완료 후 fade-in): 복사 · 재생성 아이콘 버튼 32×32 --label-2, 그 옆 `.usage` (11px --label-3, "412 tok · 38 tok/s"). 복사 후 아이콘이 checkmark로 1.5s 전환.

### 6.6 코드 블록 `.codeblock`
```html
<div class="codeblock">
  <div class="code-head"><span class="lang">python</span><button class="copy" aria-label="복사">[svg] 복사</button></div>
  <pre><code>…</code></pre>
</div>
```
- 컨테이너 `--code-bg`, `--r-md`, hairline 테두리 `0 0 0 .5px var(--separator)`, 상하 margin 16px.
- `.code-head`: 높이 36, 패딩 0 12, 13px --label-2, 배경 `--bg-elev`(다크) — `.copy`는 absolute 대신 헤더 우측 텍스트 버튼(현재 absolute 버튼은 코드와 겹침).
- `pre`: 패딩 14/16, 14px mono, `overflow-x:auto`, `-webkit-overflow-scrolling:touch`, 가로 스크롤바 숨김. 화면 밖으로 빠져나가지 않게 `.bubble{min-width:0}`.

### 6.7 생각 과정 `details.think`
- 테두리 대신 접이식 "pill": `summary`는 13px --label-2, 왼쪽 반짝이는 sparkle 아이콘 + "생각하는 중…"(스트리밍) / "생각 과정 · 12초"(완료), 오른쪽 chevron 회전(90°, 180ms).
- 스트리밍 중 summary 텍스트에 shimmer: `background:linear-gradient(90deg,var(--label-3),var(--label),var(--label-3)); background-size:200%; -webkit-background-clip:text; color:transparent; animation:shimmer 1.6s linear infinite`.
- 본문 `.think-body`: 13/1.5 --label-2, 왼쪽 2px --separator 라인, padding-left 12, max-height 40vh 스크롤. 완료 시 자동 접힘(설정 "기본 펼치기" 존중).
- `summary::-webkit-details-marker{display:none}; list-style:none`.

### 6.8 로딩/타이핑 표시 `.typing`
- 첫 토큰 전(TTFT 대기): 어시스턴트 자리에 점 3개 `<span class="typing"><i></i><i></i><i></i></span>` — 6px 원, --label-2, `opacity .3→1 + scale .8→1`, 1.2s, 각 0.15s 지연.
- 큐 대기 3초 이상이면 아래에 13px --label-3 "모델 준비 중…" 노출.

### 6.9 스트리밍 표시
- 기존 `.cursor::after "▍"` 깜빡임 → **부드러운 원형 커서**: `.cursor::after{content:"";display:inline-block;width:.55em;height:.55em;border-radius:50%;background:var(--label);margin-left:.15em;vertical-align:baseline;animation:pulse 1s var(--ease-out) infinite}`.
- 토큰 페이드: 매 렌더 시 전체 innerHTML 교체는 유지하되, 렌더 throttle을 `requestAnimationFrame`(최대 ~30fps)로 묶고, 마지막 블록의 새로 추가된 텍스트를 `<span class="fresh">`로 감싸 `@keyframes fadeIn{from{opacity:.25}}` 220ms. (단순 구현: 끝 문단에만 적용.)
- 자동 스크롤: 바닥에서 80px 이내일 때만 따라감(기존 `stick` 로직 유지).

### 6.10 스크롤-투-바텀 `#toBottom`
- 원형 36px, `--bg-elev` + 블러, 아이콘 arrow.down, 컴포저 위 12px 가운데. 바닥에서 >200px일 때 `opacity/translateY(8px)/scale(.9)` → 표시, `--ease-spring`. 탭 시 smooth scroll.

### 6.11 오류/재시도 `.msg.error`
- 붉은 박스 대신: 아이콘(exclamationmark.circle, --danger) + 15px --label-2 메시지 + `.btn.retry` (pill, `--fill` 배경, --label, 13px 600, 높이 32). 배경 `rgba(255,69,58,.08)`, `--r-md`, 패딩 12/14.

### 6.12 빈 상태 `.empty`
- 세로 중앙(컴포저 위 공간), 앱 마크(28px 그라디언트 원 또는 sparkle) → "무엇을 도와드릴까요?" 28/700 → 모델명 13px --label-3.
- 제안 칩 `.chips > button.chip` 2열 그리드(모바일) : `--bg-elev`, `--r-lg`, 패딩 12/14, 타이틀 15/600 + 서브 13 --label-2. 순차 등장 40ms stagger. 탭 → 입력 후 즉시 전송.
- 예: "코드 리뷰 / 이 함수 개선점 알려줘", "요약 / 긴 글을 3줄로", "번역 / 자연스러운 영어로", "아이디어 / 주말 프로젝트 추천".

### 6.13 컴포저 `#composer`
```html
<form id="composer">
  <div class="field">
    <textarea id="input" rows="1" placeholder="메시지" enterkeyhint="send"></textarea>
    <button id="sendBtn" type="submit" class="send" aria-label="전송">[arrow.up svg]</button>
  </div>
</form>
```
- 영역: absolute bottom, 패딩 8 16 `max(8px, env(safe-area-inset-bottom))`, 배경 `linear-gradient(to top, var(--bg) 60%, transparent)` 또는 `--material`+blur.
- `.field`: `--bg-elev`, `--r-xl`, hairline, padding 6 6 6 16, flex align-end. focus-within 시 hairline → `rgba(10,132,255,.5)`.
- `#input`: 17px, 투명 배경, border 0, outline 0, 자동 높이(scrollHeight, 최대 6줄 ≈ 160px), `resize:none`.
- `.send`: 32×32 원, `--accent` + 흰 arrow. 입력이 비면 `--fill` + --label-3, disabled. 활성 전환 시 scale .8→1 spring.
- `.send.stop`: 같은 자리, `--label` 배경에 `--bg` 색 둥근 정사각형(10px, r2) — 아이콘 크로스페이드 180ms.
- Enter: 데스크톱 Enter 전송/Shift+Enter 줄바꿈. **모바일(터치)은 Enter=줄바꿈**, 전송은 버튼.
- 키보드: `visualViewport` resize/scroll → `--vvh` 갱신 + 바닥 고정 시 scrollBottom. iOS가 페이지 스크롤하는 것 방지(`window.scrollTo(0,0)` on focus).

### 6.14 설정 시트 `dialog#settings`
- 모바일: 하단 시트. `dialog{margin:auto 0 0; width:100%; max-width:100%; border-radius:16px 16px 0 0; padding:8px 20px calc(20px + safe-bottom); background:var(--bg-elev)}` 상단 grabber(36×5, r3, --label-3). 등장 `translateY(100%)→0` 380ms `--ease-sheet`, `::backdrop` fade.
- ≥761px: 가운데 모달 480px, r16.
- 내부는 iOS 그룹 리스트: 라벨 13px --label-2(섹션 위), 입력 그룹 `--bg-elev-2` r10, 행 높이 44, 행 사이 hairline. 입력 16px 이상(17 권장). 체크박스 → iOS 스위치 스타일(`input[type=checkbox]{appearance:none;width:51px;height:31px;border-radius:999px}` + ::before 노브, 체크 시 #30D158).
- 버튼: 하단 "저장" 전폭 50px, --accent, r12, 600. "닫기"는 헤더 우측 텍스트 버튼.
- 섹션: 연결(Base URL, API Key, 모델+불러오기) / 대화(시스템 프롬프트) / 생각(기본 펼치기, thinking 끄기).

### 6.15 프레스 상태 (햅틱 느낌)
- 모든 `button`: `transition: transform var(--d-fast) var(--ease-spring), background var(--d-fast)`; `:active{transform:scale(.96); transition-duration:var(--d-instant)}`.
- iOS 18+ Safari: `<input type="checkbox" switch>` 사용 시 실제 햅틱. `navigator.vibrate`는 iOS 미지원 → 시각 피드백으로 대체.

## 7. Mobile Safari 체크리스트
- `<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover, interactive-widget=resizes-content">`
- `apple-mobile-web-app-capable`, `status-bar-style: black-translucent`, theme-color dark `#000`.
- 100dvh + visualViewport, `env(safe-area-inset-*)` 4방향.
- 모든 input/textarea/select font-size ≥16px.
- `-webkit-tap-highlight-color:transparent`, `-webkit-touch-callout:none`(버튼).
- `overscroll-behavior: contain` on #messages, body none.
- 스탠드얼론(홈 화면) 감지 `@media (display-mode: standalone)` → 상단 여백 safe-area만.

## 8. 애니메이션 타이밍 요약
| 대상 | 시간 | easing |
|---|---|---|
| 버튼 눌림/해제 | 100 / 180ms | linear / spring |
| 메시지 등장 | 280ms | ease-out |
| 토큰 페이드 | 220ms | ease-out |
| 타이핑 점 | 1.2s loop, 150ms stagger | ease-in-out |
| 커서 pulse | 1s loop | ease-out |
| think shimmer | 1.6s loop | linear |
| think chevron | 180ms | ease-out |
| 드로어 / 시트 | 380ms | ease-sheet |
| scrim / backdrop | 280ms | ease-out |
| 스크롤 버튼 | 280ms | spring |
| 칩 stagger | 280ms + 40ms×i | ease-out |
| 헤더 hairline | 180ms | linear |

## 9. 현재 코드 리뷰 (`llm-chat-ui/`)
1. 유니코드 아이콘(☰ ＋ ↑ ■ ⚙︎) → 플랫폼별 렌더 차이, 저렴해 보임. SVG로.
2. `--user:#2563eb` Tailwind 블루 + 어시스턴트 회색 버블 → "채팅앱" 느낌. 어시스턴트 버블 제거, 사용자 버블 중립색.
3. 다크 배경 `#111214`, 테두리 `#2a2c31` 다수(topbar/composer border) → 선 과다. hairline+블러로.
4. 헤더/컴포저가 sticky + 불투명 → 콘텐츠가 뒤로 흐르지 않음. absolute + backdrop-filter.
5. `#scrim{display:none}` 토글 → 페이드 불가. drawer transition .2s linear → 380ms ease-sheet.
6. `.codeblock .copy` absolute → 긴 첫 줄 가림. 헤더바로.
7. `▍` steps 깜빡임 → 거침. pulse 원형 커서 + 페이드.
8. 첫 토큰 전 상태 표시 없음(빈 버블+커서) → 타이핑 점.
9. 메시지 등장/버튼 프레스 모션 없음, `prefers-reduced-motion` 없음.
10. 빈 상태가 텍스트 한 줄 → 제안 칩.
11. 스크롤-투-바텀 버튼, 복사/재생성 액션 없음(코드 복사만).
12. `visualViewport` 미사용 → iOS 키보드 시 컴포저 가림/점프 가능.
13. 매 토큰마다 innerHTML 전체 재렌더 → rAF throttle 권장.
14. 설정 dialog가 데스크톱 모달 형태 → 모바일 하단 시트.
15. 체크박스 기본 스타일 → iOS 스위치.
