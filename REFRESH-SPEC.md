# REFRESH-SPEC: 비주얼 리프레시 · Eve 아이콘 · 모션

기준: eve-chat-ui `5aefb4b` (v1.2.0). SPEC.md, NATIVE-SPEC.md 토큰을 **덮어쓰는** 문서예요. 충돌하면 이 문서가 우선해요.
출처 영역(가로 스크롤)은 별도 작업이라 여기서는 다루지 않아요. 아래 칩 스타일은 그 작업과 맞추기 위한 참고예요.

목업: `reference/refresh/mock.html#empty`, `#chat` · 아이콘: `icons/preview.html`

---

## 0. 진단 (390px 다크로 렌더하고 styles.css · app.js를 읽은 결과)

### 왜 "원시적"으로 보이나
1. **면이 모두 평평해요.** 배경 #000 위에 #1C1C1E 박스만 있어요. 위계는 회색 한 단계뿐이고 그라데이션도, 빛을 받는 가장자리(hairline)도, 그림자 깊이도 없어요.
2. **빈 화면에 브랜드가 없어요.** 마크가 44px 아이콘 하나로 떠 있고, 부제에 모델 이름(`Qwen3-30B-A3B-4bit`)이 그대로 보여서 개발 도구처럼 읽혀요. 내비 부제에도 같은 이름이 있어요.
3. **아이콘이 제각각이에요.** 인라인 SVG가 index.html, app.js(`ICON`, `MI`), proactive.js에 흩어져 있고, 획 1.8에 크기 22px로 일괄 적용돼요. 형태 언어(모서리, 끝 처리, 광학 크기)가 서로 달라요.
4. **타입 스케일이 없어요.** 본문 17/1.55를 모든 곳에 쓰고 제목만 굵게 해요. 말풍선, 메타, 캡션의 크기와 굵기 차이가 거의 없어요.
5. **컴포저에 포커스 링이 항상 보여요.** 자동 포커스 상태에서 파란 1px 테두리가 상시 노출되고, 전송 버튼은 비활성일 때 회색 원이에요. 무게 중심이 없어요.

### 왜 애니메이션이 "뚝뚝" 끊기나 (중요도 순)
| # | 위치 | 문제 | 고치는 법 |
|---|---|---|---|
| M1 | app.js:218 `syncVV` → `--vvh` | 키보드가 열리는 동안 매 프레임 앱 높이를 바꿔 **전체 레이아웃을 다시 계산**하고, 같은 프레임에서 `scrollBottom()`까지 불러요 | 높이는 키보드 열림/닫힘 **끝에 한 번만** 바꾸고, 진행 중에는 컴포저만 `transform: translateY()`로 따라가게 해요 (§3.4) |
| M2 | app.js:963 스트리밍 `paint` | 토큰마다 rAF로 `innerHTML` 교체 + `scrollTo` 강제 동기 레이아웃 | 꼬리 부분 갱신은 그대로 두되 스크롤은 `stick`일 때 **100ms에 한 번** 이하로, `scrollTop` 읽기를 쓰기 앞에 모아요. 꼬리 노드에 `contain: content` |
| M3 | styles.css:281, 435, 1264 행 삭제 | `height` 트랜지션 (레이아웃 애니메이션) | 행은 `opacity`+`scale(.98)`로 사라지고, 아래 행들은 **FLIP**(`translateY`)으로 올라와요 |
| M4 | styles.css:585 `.fbp` | `grid-template-rows` 트랜지션 (레이아웃) | `clip-path: inset(0 0 100% 0)` → `inset(0)` + opacity. 높이는 열기 직전 한 번만 확정 |
| M5 | styles.css:111–112 전송 버튼 | `transition: all` + 오버슈트 spring | `transform, opacity`만 명시 |
| M6 | styles.css:32, 104, 256 등 | `box-shadow` 트랜지션 (매 프레임 다시 그림) | 그림자는 의사 요소에 두고 그 요소의 `opacity`만 바꿔요 |
| M7 | styles.css:326, 211 `#app`, `#main` | `border-radius`, `filter` 500ms 트랜지션 (시트 열릴 때 뒤 화면 축소) | `transform: scale()`만. 둥근 모서리는 처음부터 `border-radius`를 주고 `overflow:clip`인 래퍼에 둬요 |
| M8 | 블러 레이어 겹침 | 내비·컴포저·토스트·컨텍스트 메뉴가 동시에 `backdrop-filter`를 켜고, `#ctx`는 전체 화면 blur(24px)를 **opacity 트랜지션과 함께** 그려요 | 동시에 움직이는 블러 표면은 최대 2개. 전체 화면 dim은 blur 없이 rgba만, blur는 메뉴 자체에만 |
| M9 | `.msg` 등장 | 모든 메시지에 `msgIn` 280ms. 스레드를 열 때 `.no-anim`이 빠지는 프레임에 여러 개가 동시에 재생될 수 있어요 | 등장 애니메이션은 **새로 추가된 마지막 1개**에만 (§3.2) |
| M10 | 듀레이션 혼재 | 100/150/180/200/220/250/260/280/300/350/380/420/500ms가 섞여 있고, `ease-spring`(오버슈트)이 크기·위치 모두에 쓰여요 | §3 토큰 4개 + 이징 3개로 통일 |
| M11 | `will-change` | 내비 전환에는 잘 처리됐지만 시트, 토스트, 메뉴에는 없어요 | 움직이기 **직전에 추가하고 끝나면 제거** (상시 금지) |

---

## 1. 비주얼 방향

**한 줄 요약:** "검정 위에 떠 있는 유리판". 순수 검정 바탕, 그 위에 반투명 재질 2단계, 0.5px 빛 가장자리, 아주 약한 에메랄드 광원 하나.

### 1.1 결정 사항과 이유
| 결정 | 이유 |
|---|---|
| 기능 강조색은 **#0A84FF 유지** (전송, 링크, 토글, 선택) | iOS 사용자는 파랑을 "누를 수 있음"으로 읽어요. 바꾸면 학습 비용만 생겨요 |
| 브랜드 에메랄드 **#00D2BE는 "Eve의 존재"에만** (마크, 빈 화면 광원, 제안 칩 아이콘, 선톡 아이콘, 생각 중 표시) | 두 색이 같은 역할을 다투지 않게 해요. 에메랄드는 전체 화면의 3% 이하 |
| 라이트 모드에서는 에메랄드 `#007A72` | TOKENS.md 대비 기준 (AA) |
| 모델 이름은 설정 > 정보로 이동, 화면에는 "로컬 · 비공개" | 사용자가 신경 쓸 정보가 아니에요. 개발 도구 느낌의 주범이에요 |

### 1.2 재질 (깊이)
| 토큰 | 다크 | 라이트 | 쓰는 곳 |
|---|---|---|---|
| `--bg` | `#000` | `#fff` | 바탕 |
| `--layer-1` | `#1C1C1E` | `#F2F2F7` | 그룹, 리스트 셀 |
| `--layer-2` | `#2C2C2E` | `#E5E5EA` | 사용자 말풍선, 눌림 |
| `--material` | `rgba(28,28,30,.66)` + `blur(24px) saturate(180%)` | `rgba(255,255,255,.7)` 동일 | 내비, 컴포저, 토스트, 메뉴 |
| `--card` | `linear-gradient(180deg, rgba(255,255,255,.06), rgba(255,255,255,.03))` | `#fff` | 제안 칩, 확인 카드 |
| `--hair` | `rgba(255,255,255,.08)` (inset 0.5px) | `rgba(0,0,0,.08)` | 모든 카드·재질의 가장자리 |
| `--hair-strong` | `rgba(255,255,255,.12)` | `rgba(0,0,0,.12)` | 컴포저, 떠 있는 요소 |
| `--shadow-float` | `0 8px 24px rgba(0,0,0,.4)` | `0 8px 24px rgba(0,0,0,.08)` | 컴포저, 토스트, 메뉴 (트랜지션 금지, §0 M6) |
| `--glow` | `radial-gradient(50% 60% at 50% 0, rgba(0,210,190,.10), transparent 70%)` | 없음 | 빈 화면 상단 420px, 고정. 움직이지 않아요 |

규칙: 테두리(`border`)는 쓰지 않고 `box-shadow: inset 0 0 0 .5px var(--hair)`만 써요. 블러 표면은 화면당 최대 3개(내비, 컴포저, 떠 있는 것 1개).

### 1.3 타입 스케일 (SF / system, 한글은 Apple SD Gothic Neo 폴백, `word-break: keep-all`)
| 토큰 | 크기/행간 | 굵기 | 자간 | 쓰는 곳 |
|---|---|---|---|---|
| `--t-large` | 34/41 | 700 | -0.4px | 목록 큰 제목 |
| `--t-title` | 28/34 | 700 | -0.4px | 빈 화면 제목 |
| `--t-headline` | 17/22 | 600 | -0.2px | 내비 제목, 시트 제목 |
| `--t-body` | 16/24 | 400 | 0 | **답변 본문** (17→16, 행간 1.5 고정) |
| `--t-bubble` | 16/22 | 400 | 0 | 사용자 말풍선 |
| `--t-callout` | 15/20 | 400·600 | 0 | 리스트 셀, 칩 제목(600) |
| `--t-footnote` | 13/18 | 400 | 0 | 칩 설명, 메타, 미리보기 |
| `--t-caption` | 12/16 | 500 | 0.2px | 내비 부제, 배지, 출처 칩 |

입력창은 iOS 확대 방지를 위해 **17px 유지**. 숫자에는 `font-variant-numeric: tabular-nums`(시간, 배지).

### 1.4 간격과 모서리
- 간격은 4/8 그리드: `4 8 12 16 20 24 32 40`. 화면 좌우 여백 16, 메시지 사이 20, 사용자 → 답변 20, 그룹 사이 32.
- 모서리: `--r-xs 6` (코드 인라인), `--r-sm 10` (행, 작은 버튼), `--r-md 16` (카드, 칩, 코드블록), `--r-lg 20` (말풍선), `--r-xl 26` (컴포저), `--r-sheet 12` (시트 상단), 원형 `999`.
- 모서리 안쪽 요소는 `바깥 r − 안쪽 여백` 규칙 (컴포저 26 − 6 = 전송 버튼 원 20 → 36px 원).

### 1.5 말풍선
- **사용자:** `--layer-2`, 패딩 10/14, 모서리 `20 20 6 20`(꼬리 쪽만 6), 최대 폭 78%, `--t-bubble`. 연속 메시지면 위쪽 모서리도 6.
- **Eve 답변:** 말풍선 없이 본문 그대로 (지금 방식 유지). 폭 최대 720px. 단락 간격 10px, 목록 들여쓰기 20px.
- **코드블록:** `#0E0E10`, `--r-md`, `inset .5px var(--hair)`, 헤더 32px(언어 `--t-caption` + 복사 아이콘).
- **동작 줄:** 아이콘 18px, 탭 영역 36×36(줄 전체 높이 44 확보), 색 `--label-3`, 눌림/켜짐은 `--label`. 답변이 끝난 뒤에만 페이드 인.
- **출처:** 높이 26 캡슐 칩(파비콘 14 + 이름, `--t-caption`), 최대 2개 + `+N`. 한 줄을 넘지 않아요 (세부는 별도 작업).

### 1.6 컴포저
- 화면 아래에 떠 있는 캡슐: `--material` + `--hair-strong` + `--shadow-float`, 모서리 26, 패딩 6, 좌우 12 띄움, 아래 `max(10px, safe-area)`.
- 뒤에는 `linear-gradient(transparent, var(--bg) 40%)` 페이드(블러 아님)로 메시지가 자연스럽게 사라져요.
- 포커스 링 **삭제**. 포커스 시 `--hair-strong`이 `rgba(255,255,255,.18)`로 바뀌는 것만 (의사 요소 opacity로, M6).
- 전송 버튼: 36px 원. 비어 있으면 `--layer-2` 바탕 + `--label-3` 아이콘, 입력이 생기면 `--accent` 바탕 + 흰 아이콘(획 2.25). 바탕은 두 레이어를 겹쳐 두고 **opacity만** 바꿔요. 생성 중에는 `stop` 아이콘으로 교차 페이드.
- 웹 검색 버튼: 36px 원, 꺼짐 `--label-2`, 켜짐 `--accent` 아이콘 + `rgba(10,132,255,.16)` 바탕.

### 1.7 빈 화면
- 마크 56px를 `#141517` 둥근 사각(r 16) 안에 넣고 `inset .5px rgba(255,255,255,.1)` + `0 8px 32px rgba(0,210,190,.18)` 광원.
- 제목 "무엇을 도와드릴까요?" (`--t-title`), 부제 "Eve는 이 기기 가까이에서 실행돼요" (`--t-footnote`, `--label-2`). 모델 이름은 빼요.
- 제안 칩 2×2: `--card` + `--hair`, r 16, 패딩 14, 위에 에메랄드 아이콘 18px(source, sparkle, globe, think), 제목 `--t-callout` 600, 설명 `--t-footnote` 한 줄(넘치면 2줄까지).
- 상단에 `--glow` 고정. 등장은 마크 → 제목 → 칩 순서로 40ms 간격 스태거, 각 `--d-slow` `--ease-out` (§3).

### 1.8 그 밖
- 내비: 높이 52(44 + 부제), 제목 `--t-headline`, 부제 `--t-caption` `--label-3`. 스크롤 전에는 투명, 스크롤 후 `--material`(이건 transition 없이 opacity 레이어 교차, M6).
- 목록 셀: 높이 64, 제목 `--t-callout` 600, 미리보기 `--t-footnote` `--label-2` 1줄, 시간 `--t-caption` 우측 상단. 구분선은 텍스트 시작점부터 0.5px.
- 확인 카드(.confirm-card)·시트·토스트도 `--card`/`--material` + `--hair`로 통일.

---

## 2. Eve 아이콘 세트

위치: `icons/` · 원본 생성기 `icons/build.py` · 개별 파일 `icons/svg/*.svg` · 스프라이트 `icons/sprite.svg` · 미리보기 `icons/preview.html`

### 2.1 그리드 규칙
- 24×24 viewBox, 라이브 영역 20×20 (사방 2px 여백). 원형은 지름 16, 사각은 14 기준으로 광학 크기를 맞춰요.
- 획 **1.75**, `stroke-linecap: round`, `stroke-linejoin: round`, 채움 없음. 렌더 크기 17px 이하에서는 획 2로 올려요(작은 크기에서 얇아 보이는 것 보정).
- 모서리 반경 2.5–3 (카드형), 화살표는 각 6px 날개. 형태는 **가장 적은 획**으로: 장식 선, 그림자, 이중선 금지.
- 색은 `currentColor`. 에메랄드는 CSS에서 `color`로만 줘요.

### 2.2 목록 (38개)
| 이름 | 쓰는 곳 | 기존 대체 |
|---|---|---|
| chevron-left / right / down | 뒤로, 셀 이동, 생각 접기·출처 펼치기 | `.chev`, nav-back |
| compose | 새 대화 | 펜+선 |
| settings | 설정 (슬라이더 두 줄, 톱니 대신) | 톱니 |
| search | 대화 검색 | |
| globe | 웹 검색 토글, 제안 칩 "번역" | |
| send / stop | 전송 / 생성 중지 | `.i-up`, `.i-stop` |
| arrow-down | 맨 아래로 | |
| copy / check | 복사 / 복사됨·완료 | ICON.copy, ICON.check |
| regenerate | 다시 생성 | ICON.regen |
| thumb-up / thumb-down | 피드백 | ICON.up/down |
| edit | 이름 변경, 메시지 편집 | ICON.edit |
| trash | 삭제 (빨강은 CSS로) | ICON.trash |
| archive / restore | 보관 / 복원 | |
| share / download | 메모리 내보내기 (공유 시트 / 다운로드) | |
| close / more / plus | 닫기, 더 보기, 메모리 추가(지금은 텍스트 "+") | |
| warning / info | 오류, 안내 | ICON.warn |
| link / source | 출처 링크, 출처 칩·문서 | ICON.globe(출처) |
| think | 생각 과정, 제안 칩 "아이디어" | |
| sun-horizon / eye / followup / sparkle | 선톡 template_kind: briefing / watch / followup / 기본 | proactive.js origin-ic |
| memory | 메모리 설정, 기억 카드 | |
| bell / moon / lock | 선톡 알림 / 조용한 시간 / 잠금 화면 미리보기 | |
| offline | 오프라인 배너 | |

### 2.3 적용 방법
1. `icons/sprite.svg` 내용을 index.html `<body>` 맨 앞에 인라인으로 넣어요 (외부 `<use href="file#">`는 iOS Safari PWA에서 캐시 문제가 있어서 인라인).
2. 사용: `<svg class="i" aria-hidden="true"><use href="#i-copy"/></svg>`. 아이콘만 있는 버튼은 버튼에 `aria-label`.
3. CSS: `.i{width:22px;height:22px;fill:none;stroke:currentColor;stroke-width:1.75;stroke-linecap:round;stroke-linejoin:round;flex:none}` · `.i-sm{width:18px;height:18px}` · `.i-xs{width:16px;height:16px;stroke-width:2}`.
4. 전역 `svg{...}` 규칙은 지우고 `.i`로 옮겨요 (로고·진행 링 같은 다른 SVG까지 획이 바뀌는 문제 해결).
5. app.js `ICON`/`MI`, proactive.js 아이콘 문자열은 `icon('copy')` 헬퍼 하나로 바꿔요: `const icon = (n, c='') => \`<svg class="i ${c}" aria-hidden="true"><use href="#i-${n}"/></svg>\``.

---

## 3. 모션

### 3.1 토큰
| 토큰 | 값 | 용도 |
|---|---|---|
| `--d-1` | **120ms** | 눌림, 색·불투명도 토글, 아이콘 교차 |
| `--d-2` | **200ms** | 작은 요소 등장/퇴장, 토스트 퇴장, 칩 펼침 |
| `--d-3` | **320ms** | 메시지 등장, 토스트 등장, 행 이동, 메뉴 |
| `--d-4` | **450ms** | 시트, 화면 전환(push/pop), 드로어 |
| `--ease-standard` | `cubic-bezier(.32,.72,0,1)` | 기본. iOS 시트 곡선. 위치 이동 전부 |
| `--ease-out` | `cubic-bezier(.22,1,.36,1)` | 등장(opacity+작은 이동) |
| `--ease-in` | `cubic-bezier(.4,0,1,1)` | 퇴장. 퇴장은 등장보다 짧게 (`--d-2`) |
| `--ease-spring` | `cubic-bezier(.34,1.3,.64,1)` (오버슈트 약 3%) | **scale에만** (메뉴 팝, 토스트, 전송 버튼 상태). 위치나 크기 레이아웃에는 금지 |
| `--ease-spring-soft` | `linear(0, .25 6%, .6 15%, .86 27%, .98 40%, 1.01 52%, 1, 1)` | 시트 놓기, 스와이프 복귀. `linear()` 미지원이면 `--ease-standard` 폴백 |

`@supports not (transition-timing-function: linear(0,1))`에서 `--ease-spring-soft: var(--ease-standard)`.

### 3.2 상호작용별 표
| 상호작용 | 속성 | 시간 · 이징 | 비고 |
|---|---|---|---|
| 버튼 눌림 | `transform: scale(.96)` | 누를 때 `--d-1` `--ease-out`, 뗄 때 `--d-2` `--ease-spring` | 아이콘 버튼은 scale 대신 opacity .35 (지금 방식 유지) |
| 메시지 등장 (Eve 답변 시작, 받은 메시지) | `opacity 0→1`, `translateY(8px→0)` | `--d-3` `--ease-out` | **새로 붙은 마지막 1개만**. 스레드 열기·과거 로드·재렌더에는 없음 |
| 보내기 (사용자 말풍선) | `opacity 0→1`, `translateY(12px) scale(.98)→none`, `transform-origin: bottom right` | `--d-3` `--ease-standard` | 컴포저에서 올라오는 느낌. 이전 메시지들은 움직이지 않고 스크롤만 |
| 전송 → 중지 버튼 | 두 아이콘 `opacity` + `scale(.6↔1)` 교차 | `--d-1` `--ease-spring` | `transition: all` 금지 |
| 스트리밍 텍스트 | 새 꼬리 노드 `opacity .4→1` | `--d-2` linear | 레이아웃 애니메이션 없음, 스크롤은 100ms 스로틀 (M2) |
| 동작 줄 등장 | `opacity` | `--d-2` `--ease-out`, 지연 80ms | 답변 끝난 뒤 |
| 시트 열기 | `translateY(100%→0)` | `--d-4` `--ease-standard` | 뒤 화면은 `scale(.94)`만 (M7). 배경 dim `opacity` `--d-3` |
| 시트 닫기 | `translateY(→100%)` | `--d-3` `--ease-in`에 가까운 `cubic-bezier(.32,0,.67,0)` | 드래그로 놓으면 남은 거리 비례(최소 200ms) + `--ease-spring-soft` |
| 화면 push / pop | `translateX(100%→0)`, 아래 화면 `-30%` 패럴랙스 | push `--d-4`, pop 400ms, `--ease-standard` | View Transitions 경로도 같은 값 (420/380 → 450/400) |
| 키보드 | 컴포저 `translateY(-kb)` | iOS가 주는 visualViewport 변화를 그대로 따라감(애니메이션 없음) | 레이아웃 높이 `--vvh`는 resize가 **150ms 동안 멈춘 뒤 한 번** 반영 (M1) |
| 토스트 등장 | `opacity`, `translateY(12px) scale(.96)→none` | opacity `--d-2`, transform `--d-3` `--ease-spring` | |
| 토스트 퇴장 | `opacity`, `translateY(8px)` | `--d-2` `--ease-in` | |
| 출처·생각 칩 펼침 | 패널 `clip-path: inset(0 0 100% 0)→inset(0)` + `opacity`, 아래 내용은 FLIP `translateY` | `--d-2` `--ease-standard` | 셰브론 `rotate(0→180deg)` 같은 시간 |
| 피드백 이유 패널 | 위와 같음 (M4) | `--d-3` `--ease-standard` | |
| 컨텍스트 메뉴 | 메뉴 `scale(.85→1)` + opacity, 배경 dim opacity | 메뉴 `--d-3` `--ease-spring`, dim `--d-2` | 배경 blur 금지(M8), 메뉴 자체만 blur |
| 행 삭제·보관 | 행 `opacity→0`, `scale(.98)`; 아래 행 FLIP `translateY` | `--d-2` + `--d-3` `--ease-standard` | `height` 트랜지션 금지 (M3) |
| 스와이프 놓기 | `translateX` | `--d-3` `--ease-spring-soft` | |
| 토글 스위치 | 손잡이 `translateX` | `--d-2` `--ease-spring` | 바탕색은 `--d-1` |
| 빈 화면 등장 | 마크·제목·칩 opacity + `translateY(8px)` | 각 `--d-3` `--ease-out`, 40ms 스태거 | 첫 진입에만 |
| 생각 중·로딩 | shimmer, 점 3개 | 1.2–1.6s linear 반복 | 화면 밖이면 `animation-play-state: paused` |

### 3.3 공통 규칙
1. **transform과 opacity만** 애니메이션해요. `height, width, top, left, margin, padding, grid-template-*, border-radius, box-shadow, filter, backdrop-filter`는 트랜지션 금지. (예외: `clip-path`는 펼침에만, `stroke-dashoffset`은 진행 링에만.)
2. `transition: all` 금지. 속성을 명시해요.
3. `will-change: transform`은 움직이기 직전 클래스로 붙이고 `transitionend`에서 떼요. 상시 금지.
4. JS로 프레임마다 스타일을 쓰는 애니메이션 금지 (드래그 추적만 예외, 그것도 rAF당 1회 `transform`만).
5. 같은 프레임에 레이아웃 읽기(`scrollHeight`, `offsetHeight`)와 쓰기를 섞지 않아요. 읽기 먼저 모아서.
6. 동시에 움직이는 `backdrop-filter` 표면은 2개까지.

### 3.4 키보드 처리 (M1 상세)
- `visualViewport` resize/scroll 중에는 `--kb` 값만 rAF로 갱신하고, 컴포저와 맨 아래로 버튼이 `transform: translateY(calc(-1 * var(--kb)))`로 따라가요. 메시지 목록에는 `padding-bottom` 대신 같은 값의 스페이서를 **resize가 멈춘 뒤 150ms에** 한 번 반영해요.
- `scrollBottom()`은 키보드 애니메이션이 끝났을 때 한 번만.

### 3.5 동작 줄이기 (`prefers-reduced-motion: reduce`)
- 이동·확대는 모두 없애고 **opacity만 `--d-2`로** 남겨요 (전부 0.01ms로 꺼 버리면 상태 변화가 안 보여요. 지금의 전역 규칙을 이걸로 바꿔요).
- 화면 push/pop, 시트: 교차 페이드 `--d-2`.
- shimmer, 점 3개, 커서 펄스, `hintBounce`: 정지(정적 표시).
- 스와이프 복귀, 토글: 즉시.

---

## 4. 단계
- **P0 (모션 수정 + 아이콘):** §0 M1–M11, §3 토큰 교체, §2 스프라이트 적용과 전역 `svg` 규칙 제거, reduced-motion 교체. 화면 모양은 거의 그대로라 위험이 낮아요.
- **P1 (비주얼 리프레시):** §1 재질·타입·간격·모서리 토큰, 컴포저, 빈 화면, 말풍선, 내비, 목록 셀, 카드 통일.
- 확인 기준: iPhone 실기기 Safari 성능 패널에서 키보드 열기·스트리밍·시트 열기 때 레이아웃/페인트가 프레임마다 생기지 않을 것, 60fps 유지. 탭 영역 44pt 유지.
