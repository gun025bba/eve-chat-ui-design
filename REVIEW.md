# 디자인·코드 리뷰 — /workspace/llm-chat-ui (SPEC v1 대비)

**총평: 통과(조건부).** 토큰·컴포넌트·모션·Safari 대응이 스펙과 거의 1:1로 반영됨. 스크린샷(shots/*-dark.png) 기준 프리미엄 톤 달성. XSS 안전, sw 캐시 v4 + network-first OK. 아래 Must 2건만 고치고 배포 권장.

## 확인된 항목 ✅
- 토큰(다크/라이트), 17/1.55 본문, 720px 폭, hairline, SVG 아이콘, 헤더 블러 + `.scrolled`.
- 어시스턴트 무버블, 사용자 중립 버블(우하단 6px), 코드블록 헤더바+복사(이벤트 위임), think shimmer/‘생각 과정 · N초’, 타이핑 점 + 3초 후 ‘모델 준비 중…’, 액션 바+usage, 오류 pill 재시도.
- 드로어 날짜 그룹, scrim 페이드, 하단 시트 설정 + iOS 스위치, 빈 상태 칩 stagger.
- viewport-fit=cover + interactive-widget, theme-color #000, visualViewport→--vvh, ResizeObserver→--composer-h, 터치 Enter=줄바꿈, isComposing 처리, reduced-motion 2곳.
- XSS: 모든 마크다운은 escape 후 변환, 링크는 `https?://`만, 제목/오류는 textContent. 문제 없음.
- 스트리밍 rAF throttle 적용.

## Must-fix
### M1. 스트리밍 중 매 프레임 전체 재렌더 → think 본문 스크롤/선택 리셋 + O(n²)
`fillAssistant`가 rAF마다 `bubble.innerHTML`을 통째 교체 → (a) 생각 과정을 펼쳐 스크롤하던 위치가 매 프레임 맨 위로 튐, (b) 긴 답변(수천 토큰)에서 전체 마크다운 재파싱으로 iPhone 프레임 드랍, (c) 스트리밍 중 텍스트 선택 불가.
패치(think/답변 영역을 분리해 변경분만 갱신):
```js
// fillAssistant 상단, live일 때 빠른 경로
if (live && bubble._think !== undefined) {
  const det = bubble.querySelector('details.think');
  if (det && think !== null) {
    const tb = det.querySelector('.think-body');
    if (tb.textContent.length !== think.length) { const atEnd = tb.scrollHeight - tb.scrollTop - tb.clientHeight < 20; tb.textContent = think; if (atEnd) tb.scrollTop = tb.scrollHeight; }
    const isThinking = thinking; det.classList.toggle('live', isThinking);
    det.querySelector('summary span').textContent = isThinking ? '생각하는 중…' : '생각 과정';
    if (!answer.trim() && isThinking) return;
  }
  let md = bubble.querySelector('.md');
  if (md && answer.trim()) {
    // 완성된 블록(마지막 빈 줄/닫힌 ``` 이전)은 캐시, 마지막 블록만 다시 렌더
    const cut = stableCut(answer);                       // 아래 helper
    if (cut !== bubble._cut) { md.querySelector('.stable').innerHTML = renderMarkdown(answer.slice(0, cut)); bubble._cut = cut; }
    md.querySelector('.tail').innerHTML = renderMarkdown(answer.slice(cut));
    /* .fresh 처리는 .tail에만 */ return;
  }
}
// 전체 렌더 시 .md 안을 <div class="stable"></div><div class="tail"></div> 로 구성하고 bubble._think = think; bubble._cut = 0;

function stableCut(s) { // 열린 코드펜스가 없을 때 마지막 "\n\n" 위치
  const fences = (s.match(/```/g) || []).length;
  if (fences % 2) return s.lastIndexOf('```') > 0 ? s.slice(0, s.lastIndexOf('```')).lastIndexOf('\n\n') + 1 || 0 : 0;
  const i = s.lastIndexOf('\n\n'); return i < 0 ? 0 : i + 2;
}
```
CSS: `.md .stable>:last-child::after{content:none}` (커서는 `.tail`에만), `.md .stable:empty{display:none}`.

### M2. 한국어 줄바꿈 — 단어 중간에서 끊김
빈 상태 칩(empty-dark.png): “알려/줘”, “정리/해줘”, “문장으/로”, “프로젝/트”. 헤더·버블·목록도 동일 위험.
```css
body{word-break:keep-all;overflow-wrap:anywhere}
.codeblock pre,.bubble code{word-break:normal}
```

## Should
- **S1. 중지 표시 문자열 미렌더**: `'_(중지됨)_'` — 렌더러가 `_` 기울임 미지원 → 밑줄이 그대로 보임. `'*(중지됨)*'`로 변경(또는 `.stopped` 메타 라벨로 액션 바 옆에 13px --label-3).
- **S2. 인라인 코드 내부까지 bold/italic 변환**: `` `a*b*c` `` → `<em>` 생성. inlineMd에서 코드 구간을 먼저 placeholder로 빼고 마지막에 복원:
```js
function inlineMd(s){const codes=[];s=s.replace(/`([^`\n]+)`/g,(_,c)=>`\u0000${codes.push(c)-1}\u0000`);
 s=s.replace(/\*\*([^*\n]+)\*\*/g,'<strong>$1</strong>').replace(/(^|[^*])\*([^*\n]+)\*/g,'$1<em>$2</em>')
  .replace(/\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g,'<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>');
 return s.replace(/\u0000(\d+)\u0000/g,(_,i)=>`<code>${codes[i]}</code>`);}
```
- **S3. 설정 모델 필드 잘림**(settings-dark.png “mlx-community/Qwen3-3”): select에 `text-overflow:ellipsis` + 옵션 라벨을 `shortModel()`로(값은 전체 id 유지). 또는 행을 2줄(라벨 위/값 아래)로.
- **S4. 시스템 프롬프트 placeholder “선택”** → “예: 간결하게 한국어로 답해줘” (선택 항목임은 섹션 설명으로).
- **S5. 시트 뒤 배경 dim 약함**: 스크린샷에서 헤더 제목이 거의 그대로 보임. `dialog::backdrop{background:rgba(0,0,0,.55)}` 다크에서 상향, + `body:has(dialog[open]) #main{transform:scale(.96);border-radius:12px;transition:transform var(--d-slow) var(--ease-sheet)}` (iOS 시트 깊이감, 선택).
- **S6. visualViewport resize마다 scrollBottom** → 사용자가 위를 읽던 중 키보드 열면 `stick`이 true일 때만 하므로 OK지만, 키보드 열림 애니메이션 중 수십 번 호출 → `requestAnimationFrame`으로 합치기.
- **S7. usage 보장**: 요청 body에 `stream_options:{include_usage:true}` 추가(게이트웨이가 기본 미포함일 경우 대비; 미지원 서버는 무시).

## Nice
- N1. 헤더 제목이 긴 경우 17px가 꽉 참(chat-dark.png) — `max-width:calc(100% - 104px)` 유지 확인, 스크롤 시 제목 fade-in(초기엔 모델명만) 같은 iOS large-title 패턴 고려.
- N2. 액션 바: 마지막 답변 외에는 숨김 OK. 복사 성공 시 짧은 토스트(“복사됨”, 1.2s, 블러 pill) 추가하면 피드백 강화.
- N3. 빈 상태 마크에 아주 느린 회전(20s linear) — reduced-motion 시 정지.
- N4. 생략된 항목(사용자 메시지 복사/편집, 길게 누르기, 손가락 추적 스와이프)은 v2로.
- N5. sw.js: 배포마다 `CACHE` 버전 수동 증가 필요 — README에 한 줄 명시, 또는 `?v=` 쿼리로 index.html에서 자산 참조.
- N6. 라이트 모드에서 코드블록 헤더 `--bg-elev`와 본문 대비 낮음 → 라이트 `--code-bg:#F6F6F8`, 헤더 `#EDEDF0`.

## 보여줄 스크린샷
- /workspace/llm-chat-test/shots/empty-dark.png
- /workspace/llm-chat-test/shots/chat-dark.png
