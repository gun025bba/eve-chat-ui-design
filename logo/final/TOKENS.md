# 최종 로고: Open Frame (에메랄드)

v5 `emerald/01-open-frame`을 확정안으로 정리했습니다. 다시 만들려면 `python3 build.py`(rsvg-convert와 ImageMagick 필요). 미리보기는 `preview.png`.

## 색 토큰
| 토큰 | 값 | 용도 |
|---|---|---|
| `--brand-accent-dark` | `#00D2BE` | 어두운 배경의 커서와 강조 (#0B0B0C 대비 10.3:1) |
| `--brand-accent-light` | `#007A72` | 밝은 배경의 커서와 강조 (흰 배경 대비 5.2:1, AA 통과) |
| `--brand-silver` | `#C4C9CF` | 어두운 배경의 프레임 획 (#0B0B0C 대비 11.8:1) |
| `--brand-ink` | `#121417` | 밝은 배경의 프레임 획 |
| `--brand-black` | `#0B0B0C` | 다크 UI 배경 |
| `--brand-icon-bg` | `#141517` | 앱 아이콘과 파비콘 배경 (순수 검정 위에서도 보이도록 살짝 밝게) |
| `--brand-icon-edge` | `#2A2D31` | 앱 아이콘의 희미한 가장자리 선 |

## 사용 규칙
- 다크 배경에는 `mark-dark.svg`, 라이트 배경에는 `mark-light.svg`를 씁니다. `#00D2BE`는 밝은 배경에서 대비가 1.9:1밖에 안 되므로 쓰지 않습니다.
- 한 가지 색만 써야 할 때(인쇄, 워터마크, 시스템 템플릿 아이콘)는 `mark-mono-*.svg`를 씁니다.
- 여백은 마크 높이의 25% 이상을 둡니다. 최소 크기는 16px이며, 16px보다 작게는 쓰지 않습니다.
- 회전, 늘리기, 그라디언트, 그림자, 프레임의 열린 부분을 닫는 변형은 하지 않습니다.
- 에메랄드는 커서(포인트) 한 곳에만 씁니다. 프레임은 실버 또는 잉크 색으로 둡니다.

## 파일
`mark-dark.svg`, `mark-light.svg`, `mark-mono-dark.svg`, `mark-mono-light.svg`, `app-icon.svg`, `favicon.svg`, `favicon.ico`(16, 32, 48), `favicon-16.png`, `favicon-32.png`, `apple-touch-icon.png`(180, 불투명), `icon-192.png`, `icon-512.png`, `icon-maskable.svg`, `icon-maskable-192.png`, `icon-maskable-512.png`(마크가 가운데 80% 안전 영역 안에 들어감)

## HTML / manifest
```html
<link rel="icon" href="/ui/favicon.ico" sizes="48x48">
<link rel="icon" href="/ui/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/ui/apple-touch-icon.png">
<meta name="theme-color" content="#0B0B0C">
```
```json
"icons": [
  { "src": "icon-192.png", "sizes": "192x192", "type": "image/png" },
  { "src": "icon-512.png", "sizes": "512x512", "type": "image/png" },
  { "src": "icon-maskable-192.png", "sizes": "192x192", "type": "image/png", "purpose": "maskable" },
  { "src": "icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable" }
],
"theme_color": "#0B0B0C",
"background_color": "#0B0B0C"
```
