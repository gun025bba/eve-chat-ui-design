# NATIVE 리뷰 — v6 (llmchat-v6) vs NATIVE-SPEC.md

**총평: 통과(조건부).** 스펙 대부분이 충실하게 구현됨. 스크린샷(list/chat/install/settings) 기준 iOS 네이티브 앱과 거의 구분이 안 되는 수준. 아래 Must 2건(내비게이션 히스토리 경쟁 조건, Safari 탭의 이중 전환)만 고치면 배포 OK.
미구현 인정 항목(medium 디텐트, 백그라운드 복귀 "이어서 생성", 이름 변경 `prompt()`)은 Nice로 분류.

## 확인 ✅
- 스택 구조: `#listView` 루트 / `#chatView` push, `data-route`, `inert` 동기화, `#/c/<id>` 해시, 부팅 시 `list` replaceState 후 `chat` pushState → 뒤로가면 목록(메시지 앱과 동일). `?new=1` 숏컷, `?source=pwa` 제거 OK.
- 전환: View Transitions(push 420/pop 380, 패럴랙스 -30% + 어둡게) + CSS 폴백, reduced-motion 분기, 전환 중 `visibility` 처리.
- 엣지 스와이프: standalone·좁은 화면 한정, 24px+`--sal`, 8px 방향 잠금, 순간 속도 사용, 고무줄, 남은 거리 비례 시간, 키보드 blur. 훌륭함.
- 라지 타이틀 → 인라인(IntersectionObserver), 오버스크롤 확대, 검색, 72px 행·미리보기·시간·chevron·hairline, 스와이프 삭제/이름 변경, 컨텍스트 메뉴/액션 시트.
- 시트: 취소/완료, 드래그 닫기 + 고무줄 + 스냅 스프링, 변경 사항 확인, backdrop 연동.
- safe area: navbar/목록/검색/행/컴포저 가로 inset, `kb-open` 하단 패딩, `color-scheme` meta.
- manifest: any/maskable 분리 ✅, shortcuts, `apple-touch-startup-image` 22개(다크/라이트) 파일 모두 존재 ✅.
- A2HS 시트: standalone/설치됨/30일 dismiss 체크, `beforeinstallprompt` 분기, 저장소 분리 안내 문구 ✅, 설정에 "홈 화면에 추가 방법" 행(비 standalone만) ✅.
- 터치: `touchstart` noop로 `:active` 활성화, `buzz()`는 iOS 제외(올바름).
- 상태 복원: route/scroll/draft, `visibilitychange`+`pagehide` 저장 ✅.
- **회귀 없음**: M1 stable/tail(`stableCut`), M2 `keep-all`, S1 `*(중지됨)*`, S5 backdrop .55, S7 `include_usage` 모두 유지. sw `llmchat-v6` + 업데이트 토스트 ✅.

## Must-fix
### M1. 뒤로 버튼 연타 → 히스토리 과다 소모 (Safari 탭에서는 페이지 이탈)
`back()`이 현재 route 확인 없이 `history.back()`을 호출하고, `history.state`는 popstate가 오기 전까지 여전히 `chat` → 빠르게 두 번 누르면 `ignorePop=2`, `history.back()` 2회 → 앱 시작 이전 항목으로 넘어감(브라우저 탭: 이전 사이트/빈 페이지, standalone: 첫 진입 상태 꼬임). 스와이프 commit 직후 뒤로 버튼도 같은 문제.
```js
let popping = false;
function back() {
  if (app.dataset.route === 'list' || popping) return;          // 이미 목록이거나 진행 중
  if (input === document.activeElement) input.blur();
  if (history.state?.route === 'chat') { popping = true; ignorePop++; history.back(); }
  else history.replaceState({ route: 'list' }, '', '#/');
  animateTo('list', 'pop');
}
window.addEventListener('popstate', e => {
  popping = false;
  if (ignorePop) { ignorePop--; return; }
  …
});
// 스와이프 commit 분기도 back()과 동일하게 popping 가드 사용:
if (commit) { buzz(8); slide('list','pop',dur); if (!popping && history.state?.route === 'chat') { popping = true; ignorePop++; history.back(); } else if (!popping) history.replaceState({ route:'list' }, '', '#/'); }
```
`go('chat')`도 `popping` 중이면 popstate 이후로 미루기(`if (popping) return setTimeout(() => go(route), 50)`).

### M2. Safari 탭에서 시스템 뒤로 스와이프 시 전환이 두 번 재생
Safari(비 standalone)의 가장자리 스와이프/툴바 뒤로는 자체 스냅샷 애니메이션 후 `popstate`를 보냄 → 앱이 다시 380ms pop 전환을 재생해 화면이 "되감기"처럼 튐. Safari 18+는 `PopStateEvent.hasUAVisualTransition` 제공.
```js
window.addEventListener('popstate', e => {
  popping = false;
  if (ignorePop) { ignorePop--; return; }
  const st = e.state || { route: 'list' }; …(대화 전환 동일)…
  const r = st.route === 'chat' ? 'chat' : 'list';
  if (e.hasUAVisualTransition) return setRoute(r);   // 브라우저가 이미 애니메이션함
  animateTo(r, r === 'chat' ? 'push' : 'pop');
});
```

## Should
- **S1. A2HS 안내 화살표 위치**(install-dark.png): ↓가 "나중에" 바로 위에 있어 '나중에를 누르라'로 읽힘. 화살표를 시트 **맨 아래, 안전 영역 위**(공유 버튼 방향)로 옮기고 "나중에"는 그 위 또는 우상단 × 하나로 통일(현재 ×와 나중에가 중복).
```css
.a2hs-arrow{position:absolute;left:50%;bottom:calc(4px + env(safe-area-inset-bottom));transform:translateX(-50%)}
```
  아이패드(상단 공유 버튼)·iOS 26(··· 메뉴 안 공유)은 화살표 숨김 및 문구 “주소창 옆 ··· → 공유” 분기.
- **S2. 라이트 모드 그룹 셀 색**(settings-light.png): 셀 `#E5E5EA`가 시트 배경 `#F2F2F7`과 대비가 낮아 회색 덩어리처럼 보임. iOS grouped 규칙: 배경 `#F2F2F7`, 셀 **#FFFFFF**.
```css
@media (prefers-color-scheme:light){dialog .group,#a2hs .steps{background:#fff}}
```
- **S3. 시트 드래그 닫기 속도 계산**: `v = dy / (now - t0)`은 평균 속도라 천천히 끌다가 튕기면 안 닫힘. 엣지 스와이프처럼 마지막 move 간 순간 속도를 사용(`s.v=(y-s.yl)/(now-s.tl)`), 임계 .6px/ms 유지.
- **S4. 전환 중 스와이프/탭 겹침**: View Transition 진행 중(`.vt`)에 엣지 스와이프가 시작되면 VT 스냅샷 위에서 실제 화면을 움직여 깜빡임. touchstart에 `if (app.classList.contains('vt')) return;` 추가.
- **S5. 시트 열림 시 뒤 화면 카드 축소**(§6) 확인 필요: settings-light에서 상단 상태바 띠가 검정으로 보이는 것은 의도대로지만, 라이트 모드에선 `#000` 대신 iOS처럼 `#000` 배경 + 앱 카드 r10이 보여야 함 — 카드가 거의 안 보임(scale .94가 적용 안 됐거나 large 높이가 너무 큼). large 디텐트 top = `env(safe-area-inset-top) + 10px` 확인.

## Nice
- N1. medium 디텐트(설치 안내·모델 선택용) — 현재 콘텐츠 높이 시트로 충분, v7.
- N2. 백그라운드 복귀 시 끊긴 스트림에 "이어서 생성" 버튼(`visibilitychange` 후 `genId`가 있었는데 controller가 죽었으면 표시).
- N3. 이름 변경 `prompt()` → 행 안 인라인 편집 또는 작은 알림 시트(텍스트 필드 1개, 취소/저장). `prompt()`는 standalone에서 "LLM Chat" 대신 도메인이 표시되어 이질적.
- N4. 목록 미리보기 "[코드]" → 코드 첫 줄 일부(`print(1)`)를 mono로 보여주면 더 정보적.
- N5. 목록 navbar의 설정(톱니) 아이콘: iOS 관례상 왼쪽 상단은 "편집"이 흔함. 현재도 충분히 자연스러움.
- N6. 실기기 QA 체크리스트: standalone 엣지 스와이프 vs iOS 시스템 제스처 충돌 여부(iOS 17+ 일부 버전은 standalone에서도 히스토리 스와이프 제공 — 그 경우 M2 패치가 같이 해결), 회전, 키보드 열린 채 push/pop, 백그라운드 30분 후 복귀(상태 복원).

## 보여줄 스크린샷
- llm-chat-ui/tests/shots/list-dark.png (라지 타이틀 목록 — 가장 "앱"다움)
- llm-chat-ui/tests/shots/install-dark.png (홈 화면 추가 안내 시트)
