# SOURCES-SPEC — 답변 출처 컴팩트화 + 가로 넘침 차단

상태: v1 (2026-10-27) · 대상: gun025bba/eve-chat-ui `main` 5aefb4b · 우선순위: 긴급

## 0. 원인 (재현 확인)
390px 뷰포트, 실제 `styles.css`로 재현: `#messages.scrollWidth` 726 / `clientWidth` 390.

1. **주원인 — `styles.css:571` `.sources ol{display:grid}`**: 열 정의가 없어서 암묵적 `auto` 트랙이 생기고, `li`는 기본 `min-width:auto`예요. 그래서 트랙 최소 폭 = 내용의 min-content예요. `.st`가 `white-space:nowrap`(`:575`)이라 제목 전체 길이가 min-content가 되고, `.st{min-width:0}`는 flex 축소에만 쓰이고 grid 트랙의 min-content 계산에는 영향을 주지 않아요. 결과적으로 `ol`이 706px까지 늘어나요. `ol`에 `grid-template-columns:minmax(0,1fr)`만 넣어도 390/390으로 해소돼요.
2. **부원인 — `styles.css:572` `.sources a{margin:0 -6px}`**: 음수 좌우 마진 때문에 6px씩 버블 밖으로 나가요.
3. **넘침이 화면 전체로 번지는 이유 — `styles.css:40` `#messages{overflow-y:auto}`**: `overflow-x`를 지정하지 않아 auto로 계산돼요. 자식 하나만 넘쳐도 대화 영역 전체가 가로로 스크롤돼요.
4. 렌더 위치: `app.js:123-127` `renderSources()`가 모든 출처를 제목·도메인 목록으로 펼쳐 그려요(면적 과다).

## 1. 전역 가드 (먼저, 패치로 바로 배포)
```css
html,body{overflow-x:clip}
#messages{overflow-x:clip}                 /* 페이지는 절대 가로 스크롤 안 함 */
.msg,.msg>*,.bubble,.md,.md *{min-width:0}  /* flex/grid 자식 기본값 제거 */
.bubble{overflow-wrap:anywhere;word-break:keep-all}  /* 긴 URL은 끊고 한국어는 어절 유지 */
.codeblock pre,.md table{display:block;max-width:100%;overflow-x:auto;overscroll-behavior-x:contain}
.md table{width:max-content}                /* 표·코드는 자체 가로 스크롤 */
.md img,.md video{max-width:100%;height:auto}
```
- grid는 항상 `grid-template-columns:minmax(0,1fr)`(또는 `repeat(n,minmax(0,1fr))`)로 써요. 열 없는 `display:grid` 금지.
- 음수 가로 마진 금지. 탭 영역 확장은 `::before{inset:-6px}`로 해요.
- 회귀 테스트: 390px에서 긴 제목·긴 URL·넓은 표·긴 코드 줄이 있는 답변을 렌더해 `#messages.scrollWidth <= clientWidth`를 확인해요.

## 2. 인라인 인용 마커
- 위첨자 캡슐: 높이 16, 좌우 패딩 5, radius 8, `rgba(10,132,255,.16)` 배경, `#0A84FF` 글자, 11px/600, `font-variant-numeric:tabular-nums`. 앞 글자와 1px 간격.
- 연속 인용 `[1,2]`은 캡슐 하나에 `1·2`로 묶어요(가로 폭 절약).
- 탭 영역: `::before{inset:-14px -6px}`로 44pt를 확보해요. 시각 크기는 그대로예요.
- 탭 → 아래 출처 행을 펼치고 해당 항목으로 스크롤해 0.6s 하이라이트(`--fill`)해요. 바로 외부로 나가지 않아요. 길게 누르면 링크 미리보기(브라우저 기본)를 그대로 둬요.
- `aria-label="출처 1, 기상청"`.

## 3. 접힌 출처 행 (기본)
답변 아래 한 줄, 왼쪽 정렬 캡슐 버튼:
`[파비콘 최대 3개 겹침] 출처 N개 ›`
- 높이 44, 좌우 패딩 12, radius 22, 배경 `#1C1C1E`, 글자 13px/500 `--label-2`, `width:max-content;max-width:100%`.
- 파비콘: 20×20 원형, 테두리 2px `#1C1C1E`, 겹침 `margin-left:-6px`. 순서는 인용 번호 순이고 같은 도메인은 하나만 써요. 이미지 실패 시 도메인 첫 글자 모노그램(`--fill` 배경)으로 대체해요. 파비콘은 `https://<domain>/favicon.ico`를 직접 쓰지 말고 서버가 주는 값이 있을 때만 쓰고, 없으면 모노그램이에요(외부 요청·추적 방지).
- `N`은 고유 출처 수. 1개면 `출처 1개`.
- `<button aria-expanded="false" aria-controls>`.

## 4. 펼친 목록
- 390px 미만~760px: 행 아래에 인라인으로 펼쳐요(시트 아님, 대화 흐름 유지). 출처 6개 초과면 처음 5개 + `모두 보기` → 바텀 시트(기존 메모리 시트 스타일, grabber, detent medium).
- 각 항목: `display:grid;grid-template-columns:20px minmax(0,1fr);gap:2px 10px`, 패딩 10/12, 최소 높이 44, radius 12, 배경 `#1C1C1E`, 항목 간 2px.
  - 1열: 번호 캡슐(기존 `.sn`).
  - 제목: 15px/20px, 흰색, **2줄 clamp**(`-webkit-line-clamp:2`), keep-all + anywhere.
  - 도메인: 12px `--label-2`, 한 줄 ellipsis, `www.` 제거.
  - 전체가 링크(`target=_blank rel="noopener noreferrer"`), 눌림 상태 `--fill`.
- 셰브론은 ›에서 ⌄로 회전해요.

## 5. 칩 (도메인 전용 표기가 필요한 곳)
- 도메인만, `max-width:160px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis`, 높이 28(탭 영역 44), radius 14. 칩 줄은 `flex-wrap:wrap`이에요. 가로 스크롤 줄은 쓰지 않아요.

## 6. 모션
- 펼침/접힘: height + opacity 280ms `cubic-bezier(.32,.72,0,1)`, 항목 stagger 20ms(최대 5개).
- `prefers-reduced-motion:reduce`: 애니메이션 없이 즉시 전환, 하이라이트는 색만.

## 7. 스트리밍 중
- 출처는 답변 완료 후에만 행으로 보여 줘요. 스트리밍 중에는 인용 캡슐만 나오고, 출처가 도착하면 행이 120ms 페이드인해요(레이아웃 점프 없이 하단에 추가).

## 8. 접근성
- 행: `aria-expanded`, 목록 `role=list`, 항목 링크 `aria-label="1. 제목, 도메인, 새 창에서 열림"`.
- 모든 탭 대상 44pt. 대비 4.5:1 이상(`--label-2` on `#1C1C1E` 확인).

## 9. 완료 기준
1. 390/375/320px에서 어떤 답변이든 `#messages` 가로 스크롤 0.
2. 기본 상태에서 출처가 차지하는 높이 = 44px 한 줄.
3. 표·코드블록은 자체 스크롤, 페이지는 고정.
4. 리뷰 샷: `review-shots/sources/before.png`, `after.png`(커밋 안 함).
