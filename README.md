# eve-chat-ui-design

Eve 웹 채팅 UI의 디자인 저장소예요. 디자인 사양, 리뷰 기록, 참고용 구현, 로고 에셋을 담고 있어요. 앱 코드는 별도 저장소에 있어요.

## 디자인 원칙

- **Apple식 미니멀리즘**: 여백을 넉넉히 두고, 장식보다 타이포그래피로 위계를 잡아요.
- **다크 모드 우선**: 배경 `#000`, 레이어 `#1C1C1E`, 포인트 컬러 `#0A84FF`.
- **시스템 타이포그래피**: `-apple-system` 계열 시스템 폰트, 본문 17/1.55, 한글은 `keep-all`.
- **모션 토큰**: push 420ms, pop 380ms, `cubic-bezier(.32,.72,0,1)`, `prefers-reduced-motion` 존중.
- **네이티브 iOS PWA 감각**: 스택 내비게이션, 세이프 에어리어, 홈 화면 standalone 모드, 엣지 스와이프 뒤로 가기.
- **에메랄드 로고**: 오픈 프레임 마크, `#00D2BE`(다크) / `#007A72`(라이트).

## 파일 구조

```
SPEC.md            기본 디자인 사양(토큰, 컴포넌트, 채팅 UX)
NATIVE-SPEC.md     네이티브 iOS PWA 사양(내비게이션, 전환, 세이프 에어리어)
THREADS-SPEC.md    서버 저장 스레드 사양
INTEGRATION.md     참고 구현 적용 가이드
REVIEW.md          구현 리뷰
REVIEW-NATIVE.md   네이티브 사양 구현 리뷰
reference/         참고 구현(index.html, styles.css, app.js)
logo/final/        확정 로고: 마크 SVG, 앱 아이콘, 파비콘, PWA 아이콘, TOKENS.md
logo/              로고 시안 기록(v1–v5)
```
