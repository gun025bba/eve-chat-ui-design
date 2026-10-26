# 기존 앱(llm-chat-ui/) 적용 가이드
스택: no-build vanilla (index.html/styles.css/app.js/sw.js/manifest), 게이트웨이 `/ui` 정적 마운트(~/llm-serving/web). 문서상 접속: README 참조(`:8000/ui/`).

순서 (클래스/ID는 기존 유지):
1. styles.css: `reference/styles.css`의 `:root` 토큰·리셋을 그대로 교체 이식 → 이후 섹션별 교체.
2. index.html: 유니코드 아이콘 → SVG(reference 참고), `#title` 아래 `#modelName`, `#toBottom` 추가, `#composer` 안에 `.field` 래퍼, send 버튼에 `.i-up`/`.i-stop`, theme-color dark `#000000`, viewport에 `interactive-widget=resizes-content`.
3. 설정 dialog: 기존 필드(sBase/sKey/sModel select+loadModels/sSystem/sShowThink/sNoThink) 유지하고 `.grabber`, `.sheet-head`, `.sec`, `.group` 마크업으로 감싸기. 체크박스는 CSS만으로 스위치.
4. app.js:
   - `fillAssistant`: 첫 토큰 전 `.typing`, think 요약 라벨/`.live` shimmer, 코드블록 `.code-head` 마크업, `.fresh` 페이드, 완료 후 `.actions`(복사/재생성 + `.usage` 이동).
   - 렌더를 rAF throttle.
   - `setBusy`: textContent 교체 대신 `.stop` 클래스만 토글, 빈 입력 시 disabled.
   - visualViewport → `--vvh`, ResizeObserver → `--composer-h`, 스크롤 리스너 → `#topbar.scrolled` / `#toBottom.show`.
   - 터치 기기에서 Enter=줄바꿈.
   - `addError`: 아이콘 + `.btn.retry` pill.
   - 빈 상태 → `.empty` + `.chips`.
   - 히스토리 렌더 시 `#messages.no-anim`.
5. sw.js 캐시 버전 올리기(이전 CSS가 캐시되지 않도록).
리뷰 항목은 SPEC.md §9.
