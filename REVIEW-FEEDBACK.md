# REVIEW-FEEDBACK — v17 (199f7bd) 👍/👎 사유 UI

검토 범위: 코드 리뷰, 로컬 mock(tests/mock.py)으로 tests/feedback_reasons.py 실행(ALL PASS), Playwright 390×844 @3x 다크/라이트 스크린샷.
배포 URL은 이 환경에서 접속되지 않아(tailnet 전용) 실기기 iOS Safari 검증은 하지 못했습니다.

## 판정: 조건부 승인 (Must 1건만 고치면 됨)

## 사양과 다른 5곳
1. '사유'/'사유 N' 재오픈 버튼: **승인.** 사양에 재오픈 진입점이 없었으니 필요한 보완입니다. 13px label-2, 44px 히트 영역, aria-label("피드백 사유 N개 수정")도 좋습니다. app.js:682-686, styles.css:582-584
2. 스크롤 40px 임계값: **승인.** 탭 직후 레이아웃 흔들림으로 잘못 skip되는 것을 막아 줍니다. 메모에 포커스가 있을 때 제외하는 처리도 맞습니다. app.js:766-770
3. 라이트 선택 bg rgba(0,122,255,.12), border .5: **승인.** 사양 수정으로 받아들입니다(.18은 라이트에서 너무 진함).
4. 세로 padding 5px: **승인.** 5+20+5+1+1 = 32px이고, min-height:32px도 유지됩니다.
5. 칩 없이 건너뛰면 요청을 보내지 않음: **승인.** 평가는 이미 저장됐고, 변경이 없으면 보내지 않습니다(_dirty 또는 changed 체크).

## Must-fix
- M1. 메모 칸이 열리면 '메모 추가'가 hidden이 되면서 `.fbp-foot`(space-between)의 자식이 하나만 남아 **완료 버튼이 왼쪽으로 붙습니다**(스크린샷 *-2-down-selected-memo.png). 위치가 바뀌면 안 됩니다. → styles.css:603-605 `.fbp-done{margin-left:auto}`

## Nice-to-fix
- N1. `.fbp-count`에 aria-live="polite"가 있어 120자를 넘으면 타이핑할 때마다 VoiceOver가 숫자를 읽습니다. live를 빼거나 0자/10자 남았을 때만 알리세요. app.js:730
- N2. iOS 메모 포커스: `focus({preventScroll:true})` 상태에서 키보드가 올라오면, 입력칸이 #composer 위 메시지 영역 아래쪽에 있을 경우 키보드나 composer에 가려질 수 있습니다. kb-open일 때 visualViewport 기준으로 `inp.scrollIntoView({block:'nearest'})`를 1회 호출하세요. 실기기 확인이 필요합니다. app.js:735, styles.css:389
- N3. Esc는 포커스가 패널 안에 있을 때만 동작합니다(app.js:749). 썸 버튼에 포커스가 있을 때도 Esc로 skip되도록 `.actions`에도 바인딩하세요.
- N4. Dynamic Type: 칩, 힌트, 메모가 px로 고정이라 iOS 텍스트 크기 설정이 반영되지 않습니다. 앱 전체 이슈라 별도 과제로 남깁니다. styles.css:590, 597
- N5. 메모 input 포커스 테두리가 흰색 2px로 강합니다. 다른 sheet-input과 같게 accent 1px 또는 separator 강조로 맞추세요. styles.css:601
- N6. iOS Safari의 한글 IME에서 Enter keydown이 compositionend 직후 isComposing=false로 한 번 더 올 수 있습니다. keyCode 229도 함께 제외하세요. app.js:748

## 확인 완료 (문제 없음)
칩 문구와 key, 순서 / 힌트 13/18 / 260ms 이징 / 다중 선택 줄바꿈 / 기타를 고르면 메모 자동 오픈과 포커스 / 140자, 카운터 120자 초과 시에만 표시 / 완료↔건너뛰기 accent 전환 / 고마워요 1.5s / 새 메시지 전송 시 자동 skip하고 선택 저장(app.js:854) / 썸 전환 시 초기화, 같은 썸 재탭 시 취소 / 응답당 패널 1개 / 재오픈 시 복원 / aria-pressed, role=group, aria-label / 강제 포커스 없음 / live 안내 2종 / reduced-motion은 opacity만 / outbox 재사용과 400 처리 / 한글 keep-all(body 상속, '질문을 잘못 이해했어요' 칩 정상) / 패널은 완료된 응답에만 붙어 스트리밍 프리즈 로직(app.js:616)에 영향 없음.
