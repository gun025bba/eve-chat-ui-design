# THREADS-SPEC v1: 서버 저장 스레드 · 피드백 · 마이그레이션 · 오프라인

대상: `llm-chat-ui` v7. SPEC.md(토큰·모션)와 NATIVE-SPEC.md(스택 내비게이션, 목록이 루트, 시트)를 그대로 따르며, 여기서는 추가·변경되는 부분만 정의합니다.
API 경로와 필드는 `llm-serving`에 아직 스레드 API가 없다는 전제에서 UI가 기대하는 **최소 계약 제안**(§0)입니다. 실제 계약이 정해지면 이름만 맞추면 됩니다.

## 0. 데이터 계약 제안 (UI 관점)
| 동작 | 제안 | UI가 필요로 하는 것 |
|---|---|---|
| 목록 | `GET /v1/threads?archived=0\|1&q=&cursor=` | `id, title, updated_at, preview, archived, pinned` |
| 생성 | `POST /v1/threads` (`client_id` 포함) | 서버 `id` 반환. 클라이언트 임시 id → 서버 id 매핑 |
| 수정 | `PATCH /v1/threads/:id` `{title?, archived?, pinned?}` | 낙관적 업데이트 + 롤백 |
| 메시지 | `GET /v1/threads/:id/messages`, `POST …/messages` (`client_msg_id`로 멱등) | 재시도해도 중복이 생기지 않아야 함 |
| 피드백 | `PUT /v1/messages/:id/feedback` `{rating: 1\|-1\|0, reasons?, comment?}` | 0 = 취소 |
| 가져오기 | `POST /v1/threads/import` (배치, 각 항목에 `client_id`) | 항목별 성공/실패 결과 |
멱등 키(`client_id`, `client_msg_id`)는 재시도와 마이그레이션 중복 방지에 꼭 필요합니다.

### 로컬 상태 모델 (app.js `convs` 확장)
```js
// conv: { id, serverId?, title, updated, pinned, archived, sync: 'synced'|'pending'|'failed', messages:[…] }
// msg : { id, serverId?, role, content, usage?, sync: 'synced'|'pending'|'failed', feedback?: {rating, reasons, sync} }
```
- 로컬 캐시(localStorage, 용량이 크면 IndexedDB)가 **화면의 기준**이고, 서버와는 백그라운드 큐(`outbox`)로 동기화합니다(offline-first).
- `outbox`: `[{op, key, payload, tries, nextAt}]`. 앱 시작·`online` 이벤트·포그라운드 복귀·30초 주기로 비웁니다. 백오프는 2·4·8·16·32초, 최대 60초.

## 1. 토큰 추가
| 토큰 | Dark | Light | 용도 |
|---|---|---|---|
| --tint-archive | #FF9F0A | #FF9500 | 보관 스와이프 액션 |
| --tint-good | #30D158 | #34C759 | (사용 자제) 동기화 완료 체크 |
| --tint-warn | #FFD60A | #FFCC00 | 대기 중(pending) 점 |
| --danger | 기존 | 기존 | 실패, 삭제 |
| --thumb-on | var(--label) | var(--label) | 선택된 엄지(채움 아이콘) |
| --banner-bg | rgba(255,159,10,.14) | rgba(255,149,0,.12) | 오프라인 배너 |
피드백 선택 상태에 **초록/빨강은 쓰지 않습니다**(Apple 톤 유지). 선택 여부는 아이콘 채움(fill)과 `--label` 색으로만 구분합니다.

모션 추가: `--d-toast:2800ms`(되돌리기 토스트 노출 시간), 행 접힘 `260ms var(--ease-sheet)`, 엄지 팝 `220ms var(--ease-spring)`, 동기화 점 펄스 `1.4s`. reduced-motion에서는 팝·펄스를 끄고 opacity 전환만 남깁니다.

## 2. 스레드 목록 (`#listView`)
NATIVE §0 결정을 유지합니다. 모바일은 목록이 루트 화면이고, ≥761px는 사이드바입니다. "side sheet"는 넓은 화면의 사이드바를 말하며, 모바일에서는 별도 드로어를 만들지 않습니다.

### 2.1 내비게이션 바 / 툴바
- 왼쪽 `#openSettings`, 오른쪽 `#newChat`(square.and.pencil)는 기존과 같습니다.
- 라지 타이틀 "대화" 아래 `.search`는 기존과 같습니다. **검색은 서버 우선**: 입력 후 250ms debounce로 `q`를 보내고, 결과가 오기 전에는 로컬 필터 결과를 바로 보여줍니다. 검색 중에는 navbar 아래에 2px 진행 바(`.search-progress`, `--accent`, indeterminate)를 표시합니다.
- 목록 맨 아래에 "보관함" 행 `#archivedRow`: archivebox 아이콘, 15px, 개수 배지(`--label-3`), chevron. 탭하면 보관함 화면을 push합니다(§2.5).

### 2.2 새 스레드
- `#newChat`: 로컬에서 즉시 생성(`sync:'pending'`)하고 채팅 화면을 push합니다. 서버 `POST /threads`는 **첫 메시지를 보낼 때** 같이 보냅니다(빈 스레드가 서버에 쌓이지 않게).
- 첫 메시지 후 제목은 처음 30자로 정하고, 서버가 제목을 생성하면(선택 기능) 180ms 크로스페이드로 교체합니다.

### 2.3 이름 변경 (`prompt()` 제거)
- **인라인 편집이 기본**: 컨텍스트 메뉴나 스와이프의 "이름 변경"을 누르면 `.row-title`이 `<input class="row-edit">`로 바뀝니다(17/600, 배경 `--fill`, r8, 패딩 4 8, 글자 전체 선택, `enterkeyhint="done"`).
  - Enter 또는 blur: 저장(낙관적). Esc 또는 빈 값: 취소.
  - 편집 중에는 행 탭과 스와이프를 막고(`.row.editing`), 키보드가 행을 가리지 않게 `scrollIntoView({block:'center'})`합니다.
- **채팅 화면에서**: `#title`을 탭하면 작은 **알림 시트** `#renameSheet`(mini-sheet)를 엽니다. 제목 "대화 이름", 텍스트 필드 1개, 취소/저장. 시트는 키보드 바로 위에 붙습니다(`bottom: calc(100% - var(--vvh))`).
```js
function startRename(row, c) {
  row.classList.add('editing');
  const t = row.querySelector('.row-title');
  const inp = Object.assign(document.createElement('input'), { className: 'row-edit', value: c.title, enterKeyHint: 'done' });
  t.replaceWith(inp); inp.focus(); inp.select();
  const done = ok => { inp.onblur = null; const v = inp.value.trim(); row.classList.remove('editing');
    if (ok && v && v !== c.title) updateThread(c, { title: v }); else renderList(); };
  inp.onkeydown = e => { if (e.key === 'Enter') { e.preventDefault(); done(true); } if (e.key === 'Escape') done(false); };
  inp.onblur = () => done(true);
}
```
`renameConv`는 `startRename`(목록) / `openRenameSheet`(채팅)로 대체합니다.

### 2.4 스와이프로 보관 + 되돌리기
- 행 왼쪽 스와이프 액션: **[이름 변경 (회색 #8E8E93)] [보관 (--tint-archive)]**. 끝까지 밀면(full swipe, 60% 이상) 바로 **보관**합니다. 삭제는 컨텍스트 메뉴와 보관함으로 옮깁니다(파괴적 동작이 실수로 일어나지 않게).
- 보관 애니메이션: `.row-main` translateX(-100%) 260ms 후 행 높이 → 0(`grid-template-rows:1fr→0fr` 또는 height 260ms `--ease-sheet`), 아래 행들은 자연스럽게 위로 올라옵니다.
- **되돌리기 토스트** `#toast`(기존 재사용): "보관됨" + `되돌리기` 버튼, 2.8초. 되돌리면 행이 같은 위치에 높이 0→원래 높이로 다시 펼쳐지고 서버 PATCH를 취소합니다.
- **서버 PATCH는 토스트가 사라진 뒤에 보냅니다**(지연 커밋). 그 사이에 앱이 백그라운드로 가면(`pagehide`) 바로 커밋합니다.
- 클래스: `.row-actions .ra-archive`(기존 `.ra-del` 자리를 대체), `.row.collapsing`.
```css
.ra-archive{background:var(--tint-archive)} .ra-rename{background:#8E8E93}
.row.collapsing{overflow:hidden;transition:height 260ms var(--ease-sheet),opacity 200ms linear;opacity:0}
```

### 2.5 보관함 화면 `#archiveView`
- 스택에 세 번째 화면으로 push합니다(`data-route="archive"`, 해시 `#/archive`). 뒤로 버튼 라벨은 "대화"이고 인라인 타이틀은 "보관함"(라지 타이틀 없음).
- 행 구조는 같고 제목은 `--label-2`입니다. 스와이프 액션: **[복원 (--accent)] [삭제 (--danger)]**. 삭제는 확인 액션 시트("대화를 영구 삭제할까요? 이 작업은 되돌릴 수 없어요." / 삭제 / 취소)를 거칩니다.
- 보관함 안 스레드를 탭하면 **읽기 전용 채팅**으로 push합니다. 컴포저 자리에 "보관된 대화 · [복원]" 바(`.archived-bar`, 50px, `--bg-elev`)를 표시합니다.
- 비었을 때: archivebox 아이콘 44px `--label-3` + "보관된 대화 없음" 17/600 + "목록에서 왼쪽으로 밀어 보관할 수 있어요" 15 `--label-2`.

### 2.6 날짜 그룹
기존 `groupLabel`(고정됨 / 오늘 / 어제 / 지난 7일 / 이전)에 **지난 30일**과 **월별**("2026년 9월", 올해는 "9월")을 추가합니다. 서버 목록은 커서 기반 무한 스크롤이고, 바닥에서 400px 이내가 되면 다음 페이지를 불러옵니다. 로딩 중에는 행 높이 스켈레톤 3개를 보여줍니다(`--fill` 블록, shimmer 1.6s, reduced-motion에서는 정지).

## 3. 메시지 피드백 (👍/👎)
### 3.1 배치
어시스턴트 액션 바 `.actions` 순서: **복사 · 다시 생성 · 👍 · 👎 · (usage)**. 모든 버튼은 32×32 원형 터치 영역에 아이콘 16px, `--label-2`입니다. 피드백 버튼은 **모든 완료된 답변**에 표시합니다(다시 생성 버튼은 지금처럼 마지막 답변에만). 스트리밍 중이거나 오류가 난 답변에는 표시하지 않습니다.
```html
<div class="actions">
  <button class="c">…</button><button class="r">…</button>
  <button class="fb up" aria-label="좋아요" aria-pressed="false">[hand.thumbsup]</button>
  <button class="fb down" aria-label="별로예요" aria-pressed="false">[hand.thumbsdown]</button>
  <span class="usage">…</span>
</div>
```

### 3.2 상태
| 상태 | 표현 |
|---|---|
| idle | 외곽선 아이콘, `--label-2` |
| pressed (`:active`) | scale .88 + 배경 `--fill`, 100ms |
| selected | **채움 아이콘**, `--thumb-on`, `aria-pressed=true`, 팝 애니메이션 scale 1→1.25→1 220ms spring. 반대쪽 버튼은 opacity .35로 흐려지고 여전히 누를 수 있음(누르면 선택 전환) |
| toggle off | 선택된 버튼을 다시 누르면 rating 0으로 취소. 채움 → 외곽선 크로스페이드 150ms |
| sending | 선택 표시는 즉시(낙관적). 버튼에 `.sending`을 붙여 opacity .6 + 2px 점 펄스(아이콘 오른쪽 위) |
| error | 원래 상태로 롤백 + 아이콘에 작은 `!` 배지(--danger 6px) + 토스트 "피드백을 저장하지 못했어요 · 다시 시도". 오프라인일 때는 롤백하지 않고 `pending`으로 큐에 넣어 나중에 전송 |
| synced | 별도 표시 없음(선택 상태만 남음) |
👍을 누르면 1.2초 동안 토스트 "피드백 감사합니다"를 띄웁니다(선택 사항, 처음 3번만).

### 3.3 👎 이유 시트 (선택 입력)
- 👎을 선택하면 **즉시 rating -1을 저장**하고, 0.3초 뒤 작은 시트 `#fbSheet`(mini-sheet, 콘텐츠 높이)를 올립니다. 시트를 닫아도 피드백은 이미 저장되어 있습니다.
- 내용: 제목 "무엇이 아쉬웠나요?" 17/600 · 칩(다중 선택): `사실과 달라요` `질문을 잘못 이해했어요` `너무 길어요` `너무 짧아요` `코드가 동작하지 않아요` `기타` · 선택 입력 `textarea`("자세히 알려주세요(선택)", 16px 이상) · 버튼 "보내기"(primary, 칩이나 텍스트가 있을 때만 활성) · "건너뛰기" 텍스트 버튼.
- 칩: 높이 36, r18, `--bg-elev-2`. 선택하면 `--label` 배경에 `--bg` 글자, 180ms.
- 하루에 3번 넘게 닫으면 그날은 시트를 띄우지 않고 액션 바에 "이유 추가" 링크만 1회 표시합니다.

## 4. 로컬 → 서버 마이그레이션 (1회)
### 4.1 표시 조건
- 서버가 스레드 API를 지원하고(`GET /v1/threads`가 200), localStorage에 `llmchat.convs`가 1개 이상 있고, `llmchat.migrated`가 없을 때.
- 앱 실행 직후가 아니라 **목록 화면이 처음 보일 때**, 1초 뒤에 띄웁니다. 대화 중에는 끼어들지 않습니다.

### 4.2 시트 `#migrateSheet` (large가 아닌 콘텐츠 높이)
```
 ───── grabber
 [icloud.and.arrow.up 44px, --accent]
 대화를 서버에 저장할까요?                 22/700
 이 기기에 있는 대화 12개를 서버로 옮기면     15 --label-2
 다른 기기에서도 이어서 볼 수 있어요.
 ┌ 대화 12개 · 메시지 318개 · 약 1.2MB ┐   13 --label-3, --bg-elev-2 r10
 [ 서버로 옮기기 ]   primary 50px
 [ 나중에 ]          text-btn
 이 기기 데이터는 옮긴 뒤에도 7일 동안 보관돼요.   12 --label-3
```

### 4.3 진행
- 버튼을 누르면 같은 시트 안에서 내용이 전환됩니다(높이는 220ms로 보간): 원형 진행 링(48px, stroke 4, `--accent`, `stroke-dashoffset` 전환) + "12개 중 5개 저장 중…" + 가는 진행 바. 시트는 드래그로 닫을 수 없고, "백그라운드에서 계속" 텍스트 버튼만 둡니다. 그 버튼을 누르면 목록 상단의 sync 상태(§5.3)에 진행률이 표시됩니다.
- 전송은 배치 `POST /threads/import`(5개씩, 대화마다 `client_id`)로 합니다. 중간에 끊겨도 같은 키로 다시 보내면 되므로 안전합니다.

### 4.4 결과
- **전부 성공**: 링이 체크마크로 바뀌는 모션(stroke draw 300ms) + "대화 12개를 옮겼어요" + "완료". `llmchat.migrated=Date.now()`를 기록하고 로컬 사본은 `llmchat.convs.bak`으로 7일 보관한 뒤 삭제합니다.
- **일부 실패**: exclamationmark.triangle(`--tint-warn`) + "10개를 옮겼어요. 2개는 실패했어요" + 실패 목록(제목 + 이유 한 줄, 15/13, 최대 3개, 더 있으면 "+N") + [실패한 항목 다시 시도](primary) / [나중에](text). 실패한 대화는 목록에서 `sync:'failed'` 배지(§5.1)로 계속 표시되고, outbox가 자동으로 다시 시도합니다.
- **전부 실패 또는 네트워크 오류**: "지금은 옮길 수 없어요" + 이유 + [다시 시도] / [나중에]. `migrated`는 기록하지 않습니다.
- **나중에 / 건너뛰기**: `llmchat.migrateSnooze=+3일`. 3번 미루면 다시 묻지 않고 설정 시트에 "이 기기 대화 서버로 옮기기" 행만 남깁니다. 시트 하단에 "이 기기에만 보관" 텍스트 버튼(`migrated='skip'`)도 둡니다.

## 5. 오프라인 · 저장 실패
### 5.1 메시지별 표시
- 사용자 메시지가 아직 서버에 저장되지 않았으면 버블 아래 오른쪽에 11px `--label-3` "전송 대기 중"과 6px 점(`--tint-warn`, 1.4s 펄스)을 표시합니다. 버블 자체는 불투명하게 유지합니다(iMessage처럼 흐리게 처리하지 않음).
- 실패(`failed`): 버블 왼쪽에 exclamationmark.circle.fill 20px `--danger`를 두고, 아래에 "저장 실패 · **다시 시도**"(--accent)를 표시합니다. 아이콘을 탭하면 액션 시트(다시 시도 / 이 기기에만 보관 / 삭제)를 엽니다.
- 어시스턴트 답변의 생성은 성공했지만 서버 저장이 실패한 경우: `.actions` 끝에 icloud.slash 14px `--label-3`을 표시하고, 탭하면 같은 액션 시트를 엽니다.
- 클래스: `.msg[data-sync=pending|failed]`, `.sync-note`, `.sync-retry`.
- 목록 행: `.row-top time` 자리에 실패 시 `!` 원형 아이콘(--danger 16px), 대기 중이면 시간 앞에 작은 점(--tint-warn). 미리보기가 "전송 대기 중…"으로 바뀌지는 않습니다.

### 5.2 전역 오프라인 배너 (기존 `#offlineBar` 확장)
- **문구를 환경 중립으로 바꿉니다**: "오프라인 — 저장된 대화만 볼 수 있어요" (VPN이나 호스트 이름 같은 환경 정보는 배너에 넣지 않고, 자세한 안내는 탭하면 보이는 상세로 옮깁니다).
- 32px, `--banner-bg`, 13/500, wifi.slash 아이콘. navbar 바로 아래에서 280ms 슬라이드 다운합니다. **목록 화면과 채팅 화면 모두**에 표시합니다(지금은 `chatView`만 있음 → `#app.offline`으로 올림).
- 오프라인에서 전송하면 메시지를 outbox에 넣고 컴포저를 비웁니다. 대신 **답변 생성은 할 수 없으므로** 어시스턴트 자리에 "연결되면 답변을 받아올게요" 13px `--label-3` 카드를 둡니다. 복귀하면 자동으로 생성하고, 카드 오른쪽 × 로 취소할 수 있습니다.
- 복귀: 배너가 "다시 연결됨"(체크, `--tint-good` 아이콘만 초록)으로 1.2초 바뀐 뒤 슬라이드 업합니다.

### 5.3 동기화 상태
- 목록 라지 타이틀 아래(검색창 위) 한 줄 `#syncStatus` 13px `--label-3`. 평소에는 숨기고, 아래 경우에만 표시합니다.
  - 동기화 중: 회전 링 10px + "동기화 중…" (3개 이상 항목이거나 2초 넘게 걸릴 때만)
  - 대기: "변경 사항 3개 대기 중"
  - 실패: "2개 저장 실패 · **다시 시도**" (--danger 점)
  - 마이그레이션 진행: "대화 옮기는 중 5/12"
- 성공 상태("모두 저장됨")는 표시하지 않습니다(조용한 성공이 Apple 원칙).
- 설정 시트에 "동기화" 섹션 추가: 마지막 동기화 시각, 대기/실패 개수, [지금 동기화] 행, [이 기기 캐시 지우기](--danger, 확인 필요).

## 6. 코드 매핑 요약
| 기존 | 변경 |
|---|---|
| `renameConv()` (prompt) | `startRename(row,c)` / `openRenameSheet(c)` |
| `deleteConv()` / `.ra-del` / `swipeDelete` | `archiveConv()` + `.ra-archive` + 되돌리기 토스트. 삭제는 보관함과 컨텍스트 메뉴에서만 |
| `renderList()` | 서버 페이지 + 로컬 병합, `#archivedRow`, `#syncStatus`, 스켈레톤 |
| `groupLabel()` | 지난 30일 + 월별 추가 |
| `fillAssistant` → `.actions` | `.fb.up/.fb.down` 추가, `msg.dataset.sync` |
| `addMsgEl('user')` | `.sync-note` 슬롯 |
| `#offlineBar` (chatView 안) | `#app.offline .offline-bar` 두 화면 공용, 문구 중립화 |
| `showToast(text, act, fn, ms)` | 그대로 재사용(보관 되돌리기, 피드백 오류) |
| `persist()` | `persist()` + `enqueue(op)`; `flushOutbox()` 신설 |
| `data-route` list/chat | + `archive` |
| mini-sheet(`#installSheet` 패턴) | `#renameSheet`, `#fbSheet`, `#migrateSheet` 재사용 |

## 7. 구현 순서
1. **데이터 계층**: conv/msg에 `serverId·sync` 추가, `outbox` + `flushOutbox`(백오프, 멱등 키), API 클라이언트. 서버가 없으면 지금처럼 로컬로만 동작(기능 감지).
2. **목록 서버 연동**: 페이지네이션, 로컬 병합, 날짜 그룹 확장, 서버 검색(debounce) + 진행 바, 스켈레톤.
3. **이름 변경**: 인라인 편집 + 채팅 제목 탭 시트, `prompt()` 제거.
4. **보관**: 스와이프 액션 교체, 접힘 애니메이션, 되돌리기 토스트(지연 커밋), `#archiveView` 라우트, 복원/영구 삭제.
5. **오프라인/동기화 UI**: `#app.offline` 배너, 메시지 `data-sync` 표시와 재시도, `#syncStatus`, 설정 "동기화" 섹션.
6. **피드백**: 액션 바 버튼과 상태, 낙관적 업데이트/롤백/큐, 👎 이유 시트.
7. **마이그레이션 시트**: 표시 조건, 진행, 결과 3종, 스누즈/건너뛰기, `.bak` 7일 보관.
8. QA: 비행기 모드 전환, 전송 중 끊김, 같은 스레드를 두 기기에서 수정(서버 `updated_at`이 더 최신이면 서버 우선 + 토스트 "다른 기기에서 변경됨"), reduced-motion, VoiceOver(`aria-pressed`, 토스트 `role=status`), sw 캐시 버전 올림.

## 8. 접근성 · 문구
- 피드백 버튼은 `aria-pressed`, 토스트와 배너는 `role="status"`, 실패 아이콘 버튼은 `aria-label="저장 실패, 다시 시도"`.
- 문구에는 호스트 이름, IP, 기기 모델명을 넣지 않습니다(사용자에게는 "서버"로 표현).
