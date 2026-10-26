# PROACTIVE-MEMORY-SPEC v2: 선톡 · 메모리 · 공통 확인 카드

대상: `llm-chat-ui`(Eve 웹 채팅). SPEC.md(토큰·모션), NATIVE-SPEC.md(스택 내비게이션, 시트, 컨텍스트 메뉴), THREADS-SPEC.md(목록·토스트·outbox), REVIEW-FEEDBACK.md(칩 패턴)를 그대로 따르고, 여기서는 **추가·변경만** 정의합니다.
근거 문서: eve-serving `docs/architecture/proactive-messaging.md`(이하 PM), `docs/architecture/memory.md`(이하 MEM), `docs/tool-platform.md` §3.2·§10.3(이하 TP). 필드 이름·엔드포인트는 eve-serving `docs/architecture/ui-api-contract.md`(이하 CT, PR #12 — **보안 리뷰 후 머지됨**)를 따릅니다. HTTP 상태 ↔ `error_code`는 CT §3.3이 기준입니다(§C3 매핑 표). Q1–Q18 결정은 §Q, 계약과 UI 요구가 어긋나는 곳은 §F에 모았습니다.

구현 순서: **Part A(선톡) → §C 공통 확인 카드 → Part B(메모리)**. 카드는 A의 제안 카드에 먼저 필요하므로 A와 함께 만듭니다.

## 0. 토큰 추가
| 토큰 | Dark | Light | 용도 |
|---|---|---|---|
| --badge | #0A84FF | #007AFF | 미읽음 점·배지 (= --accent. 빨강 배지는 쓰지 않음, Apple Mail 파란 점 톤) |
| --badge-fg | #FFFFFF | #FFFFFF | 배지 숫자 |
| --origin | rgba(235,235,245,.62) | rgba(60,60,67,.62) | 선톡 출처 표시 (= --label-2) |
| --card-bg | #1C1C1E | #F2F2F7 | 확인 카드 (= --bg-elev) |
| --card-sep | rgba(84,84,88,.6) | rgba(60,60,67,.18) | 카드 내부 hairline (= --separator) |
| --taint-bg | rgba(255,159,10,.14) | rgba(255,149,0,.12) | 외부 콘텐츠 경고 줄 (= --banner-bg) |
| --taint-fg | #FF9F0A | #FF9500 | 경고 아이콘 (= --tint-archive) |
| --switch-on | #30D158 | #34C759 | 스위치 (SPEC §6.14) |

모션 추가: 카드 등장 `280ms var(--ease-out)`(SPEC 메시지 등장과 동일), 카드 상태 전환(버튼 → 결과 줄) `220ms var(--ease-sheet)` 높이 보간 + 180ms 크로스페이드, 배지 숫자 변경 `220ms var(--ease-spring)` scale .6→1, 미읽음 점 사라짐 `180ms` opacity, 행 접힘 `260ms var(--ease-sheet)`(THREADS §2.4), 되돌리기 토스트 `--d-toast:2800ms`.
`prefers-reduced-motion: reduce`: scale·translate·높이 보간 끔 → opacity 전환만(180ms). 배지 팝 없음.

---

# Part A. 선톡 (우선)

## A1. 데이터 (PM §2.1·§3 기준)
- 선톡 메시지 = `messages.role='assistant'` 이고 `origin='proactive'`. 추가 필드 `job_id`, `read_at`, `push_status`.
- 위치(CT Q5, §F-2 해결): **P1에는 job 전용 스레드 종류가 없습니다.** 원 스레드가 있으면(follow-up 등) 그 `thread_id`에 들어갑니다. 원 스레드가 없는 선톡(브리핑·watch)은 **첫 실행 때 서버가 `job_name`을 제목으로 새 스레드를 만들고**, 이후 실행은 그 스레드를 재사용합니다(`scheduled_jobs.thread_id`). 목록에서는 일반 스레드와 똑같이 다루고 미읽음 규칙(A3)만 적용합니다. 별도 아이콘·섹션·빈 상태 없음.
- in-app 알림 = `GET /v1/notifications`(origin='proactive' AND read_at IS NULL), 읽음 = `POST /v1/messages/{id}/read`.
- UI 갱신: 앱 열기, `visibilitychange→visible`, 포그라운드 60초 주기 폴링(PM §2.1, SSE는 TBD). 오프라인이면 폴링 중단.
- 메시지 필드(확정, Q1): `origin`(`user`|`assistant`|`proactive`), `job_id`(선톡일 때만, 그 외 null), `read_at`(null이면 미읽음).
- 추가 필드(CT Q3·Q4): `provenance: {actor:"scheduler", job_id, job_name}`(`job_name`은 서버 고정 템플릿 `display_name`), `kind`: `null`(일반) | `digest`(quiet hours 종료 요약). **모르는 `kind` 값은 `null`처럼 처리.**
- `template_kind`(§F-6 해결): `briefing` | `watch` | `followup` | `null`. 출처 줄 아이콘을 고르는 데만 씁니다(A2).
- 스레드 목록 필드(확정, Q2): 서버가 계산한 `unread_count`. 선톡이 도착하면 `threads.updated_at`이 갱신되고, 목록 정렬은 `updated_at` 기준.

## A2. 스레드 안 표시
선톡은 "사용자 질문 없이 Eve가 먼저 말한 것"이므로 **답변과 같은 무버블 본문(17/1.55)** 을 유지하고, 위에 **출처 줄 하나**만 더합니다. 박스·배경색·색상 테두리는 쓰지 않습니다(콘텐츠가 주인공).

```html
<div class="msg assistant proactive" data-origin="proactive" data-job="01J…" data-unread>
  <div class="origin-line">
    <svg class="origin-ic">[template_kind별 아이콘, A2 표]</svg>
    <span class="origin-label">Eve가 먼저 보냄 · 아침 브리핑</span>
    <time datetime="2026-10-27T07:30:00+09:00">오전 7:30</time>
  </div>
  <div class="bubble">…</div>
  <div class="actions">복사 · 👍 · 👎</div>
</div>
```
- `.origin-line`: 13/18(--t-footnote) `--origin`, 아이콘 14px stroke 1.75, 간격 6px, 본문과 8px. 아이콘은 `template_kind`로 결정(§F-6 해결): `briefing` → `sun.horizon`, `watch` → `eye`, `followup` → `arrow.uturn.forward`, `null`·모르는 값 → `sparkle`. 색은 모두 `--origin`(종류별 색 구분 없음), `aria-hidden`. 템플릿 이름(“아침 브리핑”) = `provenance.job_name`(CT Q3), 없으면 `Eve가 먼저 보냄`만. 텍스트로만 렌더(textContent).
- **시각 표시가 기본 표시입니다**: 일반 답변은 시각을 안 보이지만 선톡은 "언제 왔는지"가 의미라 항상 표시. 규칙: 오늘 `오전 7:30`, 어제 `어제 오전 7:30`, 이번 주 `월요일 오전 7:30`, 그 외 `10월 21일 오전 7:30`. `Intl.DateTimeFormat('ko-KR',{hour:'numeric',minute:'2-digit'})`, 시간대는 기기 기준.
- **답변과의 차이**: (1) 출처 줄, (2) 앞에 사용자 버블이 없음, (3) 다시 생성 버튼 없음(재생성할 사용자 턴이 없음), (4) 👍/👎·사유 칩(REVIEW-FEEDBACK)은 동일하게 제공.
- **그룹핑**
  - 선톡 앞에는 **시간 구분선**을 둡니다: 직전 메시지와 30분 이상 떨어졌거나 날짜가 바뀌면 가운데 정렬 `.day-sep` 11/13(--t-caption) `--label-3` "오늘 오전 7:30". 출처 줄의 시각과 중복되면 출처 줄 시각을 숨김.
  - 같은 job의 연속 선톡(사이에 사용자 메시지 없음): 두 번째부터 출처 줄은 시각만(라벨·아이콘 생략), 간격 12px(SPEC "같은 역할 연속").
  - quiet hours 동안 쌓였다가 종료 시각에 나온 요약(PM §4) → 한 개 메시지로 오고, `kind==='digest'`(CT Q4)일 때 출처 라벨 "조용한 시간 동안 · 요약".
  - follow-up이 원 스레드에 들어오면 앞의 대화와 24px + `.day-sep`로 분리. 
- **미읽음 표시(스레드 안)**: 처음 열 때 미읽음 선톡이 있으면 첫 미읽음 위에 `.unread-sep` "새 메시지" (13/500 `--badge`, 양옆 hairline `--badge` 30%)를 두고 그 위치로 스크롤(`block:'start'`, 내비바 아래 12px). 1.5초 후 구분선만 300ms fade, 자리 유지. 일반 답변은 미읽음 개념 없음.
- 스트리밍 없음: 선톡은 완성본으로 도착 → 등장 애니메이션(280ms fade+8px)만, 커서·타이핑 점 없음. 스레드를 보고 있는 중 폴링으로 도착하면 바닥 근처(80px)일 때만 자동 스크롤, 아니면 `#toBottom` 위에 "새 메시지 1" pill(--badge 배경, 13/600, 높이 28).

## A3. 미읽음 배지
### A3.1 스레드 목록 행
- 행 왼쪽 여백(16px 안쪽)에 **파란 점 10px `--badge`**(Mail 방식). 2개 이상이면 시간 자리 오른쪽에 숫자 pill: 높이 20, 최소폭 20, 패딩 0 6, r999, `--badge` 배경 `--badge-fg` 12/600 tabular-nums, 99+ 상한. 미읽음 행 제목 600 → 그대로, **미리보기는 `--label`로 진하게**(읽음은 `--label-2`).
- 정렬: `updated_at` 순(선톡 도착 시 서버가 갱신, Q2 확정). 점·pill 숫자는 서버 `unread_count`. job 스레드 아이콘 표시는 **P1에서 뺍니다**(CT Q5 보류, §Q).
- 스와이프 액션 추가(THREADS §2.4 앞쪽): 미읽음 행에 **[읽음으로 표시 (--accent)]** 오른쪽 스와이프. 읽은 행에는 없음(“안 읽음으로 표시”는 서버 기능 없음 → 제공 안 함).

### A3.2 앱 / 타이틀
- 목록 라지 타이틀 "대화" 옆이 아니라 **채팅 화면 뒤로 버튼**에 숫자: `‹ 대화 (3)` → iOS처럼 `‹ 3`이 아니라 라벨 오른쪽에 작은 pill(위 규격, 높이 18). 지금 보는 스레드를 제외한 미읽음 합계.
- 문서 제목: `document.title = n ? '(n) Eve' : 'Eve'`(Safari 탭 표시).
- 홈 화면 아이콘 배지: `navigator.setAppBadge(n)` / `clearAppBadge()` 지원 시에만(standalone, 알림 권한 필요, 2차 Web Push와 함께). 미지원이면 무시, 오류 표시 없음.
- 합계 n = `GET /v1/notifications` 결과 개수(사용자 전체 미읽음 선톡).

### A3.3 지움 규칙
1. 스레드 화면이 **보이는 상태(visible, 포그라운드)에서 해당 선톡 메시지가 뷰포트에 50% 이상 1초 노출**되면 읽음(IntersectionObserver). 스레드를 열기만 하고 화면 밖이면 읽지 않음.
2. 읽음 처리: 로컬 즉시(낙관적, 배지·점 감소) → `POST /v1/messages/{id}/read`를 outbox(THREADS §0)에 넣어 전송. 스레드에서 여러 개를 한꺼번에 읽으면 `POST /v1/threads/{id}/read`(CT Q6, 응답 `{unread_count:0}`) 1회. 둘 다 CSRF·Origin 필요.
3. 스와이프 "읽음으로 표시" = `POST /v1/threads/{id}/read`(outbox 경유).
4. 실패: 로컬 상태 유지하고 재시도(백오프). 다음 폴링에서 서버가 여전히 미읽음이면 서버 우선.
5. 다른 기기에서 읽은 것 → 폴링에서 사라지면 점·배지 제거(180ms fade).

## A4. 제안 확인 카드 (선톡 쪽)
- follow-up("내일 9시에 다시 알려드릴까요?")은 모델 제안 → `pending_actions` 확인 → job 생성(PM §1). 확인 카드는 **§C 공통 카드, variant `proactive`**.
- scheduler가 만든 제안(watch 결과에서 write 작업 제안 등)은 토큰 없는 제안이지만 다른 제안과 똑같이 다룸: **토큰은 승인 버튼을 누를 때만** `POST /v1/actions/{id}/reissue`로 받고 곧바로 approve(CT §3.5.4). 뷰포트 진입 시 미리 받지 않음  provenance(actor=scheduler, job_id, job_name)와 tainted 표시 필수(PM §3, TP §3.2).
- tainted 스레드에서 나온 follow-up 제안은 서버가 만들지 않음(PM §1) → UI에서 별도 처리 없음.

## A5. 설정 › 선톡 (`#settings` large 시트 안 섹션)
iOS 그룹 리스트(SPEC §6.14): 섹션 라벨 13 `--label-2`, 그룹 `--bg-elev-2` r10, 행 44, hairline.

```
선톡
┌──────────────────────────────────────┐
│ Eve가 먼저 말하기               [ ◯ ] │  ← proactive.enabled (기본 off)
└──────────────────────────────────────┘
 Eve가 브리핑이나 알림을 먼저 보낼 수 있어요. 하루 최대 3번.   (13 --label-2, footer)

(켜졌을 때만 아래 그룹이 280ms 높이 보간으로 펼쳐짐)
조용한 시간
┌──────────────────────────────────────┐
│ 시작                        오후 10:00 │  ← proactive.quiet_hours.start "22:00"
│ 종료                        오전 8:00  │  ← proactive.quiet_hours.end   "08:00"
└──────────────────────────────────────┘
 이 시간에 온 메시지는 알림 없이 보관했다가 끝날 때 한 번에 알려 드려요.

선톡에서 메모리 사용          [ ◯ ]          ← proactive.memory_read (기본 false, memory.enabled=true일 때만 표시)
 켜면 이름·선호·진행 중인 일만 참고해요.
```
- 시각 행: 탭하면 행 아래 인라인 `<input type="time" step="900">`(iOS 휠) 펼침, 17px, 값 표시 `--accent`. 저장 형식 `proactive.quiet_hours = {"start":"22:00","end":"08:00"}`: 24시간 `HH:MM`, 서버 시간대(서울) 기준, 표시 `오후 10:00`. 시작=종료면 저장 거부 + 행 아래 13 `--danger` "시작과 종료가 같을 수 없어요". end < start면 자정을 넘는 구간(22→08)으로 정상 처리. 기기 시간대가 서울이 아니어도 값은 서울 기준으로 저장·표시하고 footer에 "한국 시간 기준" 부가.
- 하루 최대 횟수: P1 UI에 없음. 서버가 하루 3번으로 고정(footer 문구만 유지). `proactive.daily_cap`(1~3, 낮추기만 가능)은 후속 단계용으로 예약.
- `proactive.memory_read` 행은 `memory.enabled=false`면 숨김(값은 보존).
- 저장: NATIVE §6 시트 관례대로 "완료" 시 PATCH. 토글은 즉시 낙관적 반영 + 실패 시 롤백·토스트 "설정을 저장하지 못했어요 · 다시 시도". API(확정, Q7): `GET /v1/settings`, `PATCH /v1/settings`(부분 수정, 바뀐 키만 전송). 저장 위치 `users.settings` JSONB. P1 키: `proactive.enabled`, `proactive.quiet_hours`, `proactive.memory_read`, `memory.enabled`. 서버가 알 수 없는 키를 거부하므로 이 키만 보냄.
- 서버/운영 전역 off(`GW_PROACTIVE_ENABLED=false`·`proactive_off`)면 토글 비활성 + footer "지금은 이 기능을 쓸 수 없어요". 판단 = `GET /v1/settings`의 읽기 전용 `system.proactive_available===false`(CT Q8). `system` 블록은 PATCH에 절대 넣지 않음(400). `system.tools_available===false`면 `tool` variant 주 버튼 비활성 + ⑥ "지금은 실행할 수 없어요".
- **잠금 화면 미리보기 설정 없음**: 행을 만들지 않습니다. 2차 Web Push에서도 알림 문구는 SW 고정 문구 "Eve에게서 새 메시지가 있어요"(PM §2.4)이며 내용·제목·발신 job 이름을 넣지 않습니다. 알림 권한 요청 행("알림 받기")은 2차에서 standalone일 때만, 사용자 탭으로만 요청.
- 끄면: job 실행 중단(서버). 기존 선톡 메시지·미읽음은 그대로 남음. 확인 액션 시트 없음(되돌릴 수 있는 설정).

## A6. 상태 · 빈 상태 · 오류
| 상황 | 표현 |
|---|---|
| 선톡 꺼짐 | 목록에 아무것도 추가하지 않음 |
| 켰지만 아직 메시지 없음 | 설정 footer에 "첫 브리핑은 다음 예정 시각에 와요"만. 빈 스레드는 만들지 않음 (브리핑 전용 스레드·빈 상태는 P1 없음, CT Q5) |
| 폴링 실패 | 조용히 다음 주기 재시도, 배지는 마지막 값 유지. 오프라인 배너는 THREADS §5.2 그대로 |
| 알림 탭했는데 서버 연결 실패(~5s) | PM §2.3 "연결 필요" 화면: wifi.exclamationmark 44 + "서버에 연결할 수 없어요" 22/700 + "네트워크 연결을 확인한 뒤 다시 시도해 주세요" 15 `--label-2` + [다시 시도] primary 50. `nid`는 로컬 보관, 연결되면 해당 스레드 push. 대화 내용 캐시 없음. (문구에 VPN·호스트 이름 넣지 않음, 상세는 탭 시 펼침) |
| 읽음 POST 실패 | A3.3-4 |
| 메시지 id 404 (다른 기기에서 스레드 삭제) | 배지에서 제거, 토스트 없음 |

## A7. 접근성
- 선톡 메시지 컨테이너 `role="article"` `aria-label="Eve가 먼저 보낸 메시지, 아침 브리핑, 오전 7:30"`; 미읽음이면 앞에 "읽지 않음, ".
- 목록 행 `aria-label`에 "읽지 않은 메시지 3개" 포함. 점·pill은 `aria-hidden`.
- 배지 수 변경은 `aria-live` 쓰지 않음(폴링마다 낭독 방지). 스레드를 보고 있을 때 새 선톡 도착 시에만 `role=status` 숨김 영역에 "Eve가 새 메시지를 보냈어요" 1회.
- 스위치 `<input type="checkbox" switch role="switch" aria-checked>` + `<label>`; 시간 입력 `aria-label="조용한 시간 시작"`. 모든 행 44pt, `keep-all`.

---

# §C. 공통 확인 카드 `.confirm-card` (핵심)

**하나의 컴포넌트**로 4가지를 처리합니다: 메모리 기억(`remember`), 메모리 잊기(`forget`), 선톡 제안(`proactive`), 툴 확인 게이트(`tool`). 모두 같은 서버 흐름(TP §3.2 `pending_actions`)을 탑니다.

## C1. 해부도
```
┌───────────────────────────────────────────┐  --card-bg, r14(--r-md), padding 14 16, hairline 0 0 0 .5px --card-sep
│ [ic 16] 메모리에 저장할까요?          ⓘ  │  ① 헤더: 아이콘 + 제목 15/600 --label, 오른쪽 상세 버튼(선택)
│ ⚠ 외부 콘텐츠를 읽은 뒤 제안된 작업이에요   │  ② taint 줄(tainted일 때만) 13 --label, --taint-bg r8 padding 6 10, 아이콘 --taint-fg
│ 아침 브리핑에서 · 예약 작업                  │  ③ 출처 줄(actor=scheduler일 때만) 13 --label-2
│ ───────────────────────────────────────── │
│ “아침 브리핑은 한국어로 짧게 받는 걸 선호”    │  ④ 본문: variant별 (C2). 17/1.55 기본, payload_view를 그대로 텍스트로
│                                           │
│ [   취소   ]           [   저장   ]        │  ⑤ 버튼 줄: 2개, 각 flex 1, 높이 44, r10, 15/600, 간격 8
│ 2분 뒤 만료                                 │  ⑥ 메타 줄 11/13 --label-3 (만료 임박 30초부터 표시)
└───────────────────────────────────────────┘
```
- 배치: 어시스턴트 메시지 `.bubble` 아래 12px, 본문 폭 전체(최대 720). 메시지당 카드 여러 개면 12px 간격 세로 나열.
- 버튼: 보조(왼쪽) = `--fill` 배경 `--label`; 주(오른쪽) = `--accent` 배경 흰 글자; **파괴적 주 버튼** = `--danger` 배경 흰 글자. danger는 **send scope와 삭제(delete)에만** 씁니다(variant forget, 툴의 전송·삭제). write는 primary(`--accent`)입니다(§F-1 해결). iOS 관례대로 주 버튼 오른쪽.
- 외부 이미지·링크 자동 로드 금지(TP §10.3). URL은 텍스트로만, 탭 불가.
- 채팅 텍스트 "응/네"는 승인으로 쓰지 않음(TP §10.3). 카드 버튼으로만 승인.

## C2. variant
| variant | 아이콘 | 제목 | 본문(④) | 주 버튼 | 보조 | 주 스타일 |
|---|---|---|---|---|---|---|
| `remember` | brain(또는 bookmark) | 메모리에 저장할까요? | 정규화된 최종 텍스트 따옴표 인용 17/1.55 + 아래 kind 칩 13 `--label-2`(`선호`·`사실`·`프로필`·`할 일 · 30일 뒤 만료`) | 저장 | 취소 | accent |
| `forget` | trash | 메모리에서 지울까요? | 매칭 항목 체크 목록 (B2) | N개 지우기 | 취소 | **danger** |
| `proactive` | bell.badge / calendar.badge.clock | 다시 알려 드릴까요? | `summary` 17 + 일시 줄 15 `--label-2` = `payload_view.display` 그대로(서버가 Asia/Seoul로 만든 문자열, CT Q12; `when.at`은 `<time datetime>`에만) + 위치 "이 대화에서" | 알림 예약 | 괜찮아요 | accent |
| `tool` | 툴 manifest 아이콘, 없으면 wrench | `summary` 그대로 (예 "10/28 15:00 치과 일정 추가") | `payload_view` 키·값 표: 키 13 `--label-2` / 값 15 `--label`, 행 hairline, 최대 6행 + "모두 보기"(시트) | 실행 (툴 정의 동사 우선, 예 "추가") | 취소 | write=accent / send·delete=danger |

버튼 문구 규칙: 주 버튼은 **동사**(저장·지우기·예약·추가·보내기), "확인/예" 금지. 보조는 "취소"(proactive만 "괜찮아요"). 파괴적이면 개수 포함("2개 지우기").

## C3. 상태 표
| 상태 | 서버 `status` (TP) | UI |
|---|---|---|
| `pending` | `pending` | 버튼 2개 활성. **토큰 카운트다운 없음**(토큰은 누를 때 발급). 제안 만료(`expires_at`)만 1초 단위로 확인해 지나면 `expired` |
| `submitting` (승인) | 주 버튼 탭 → `reissue` → `approve` 연속 호출 | 주 버튼 스피너, 두 버튼 비활성. reissue 실패(approve 전)는 네트워크 오류만 재시도 가능. 토큰은 함수 지역 변수로만 두고 저장·로그 금지, 한 번 쓰면 버림 |
| `checking` | approve 응답 유실(네트워크 오류) | 서버에서 실행됐을 수 있으므로 **approve를 다시 보내지 않음**. 주 버튼 "확인 중…"(스피너) + ⑥ "결과를 확인하는 중이에요" → `GET /v1/actions/{id}`로 백오프 재조회(최대 6회) → 결과 상태로 전환. 끝내 모르면 `error` "결과를 확인하지 못했어요. 연결되면 다시 확인할게요" + [다시 확인] |
| `revising` (forget 부분 선택) | `revise` 요청 중 → 원 제안 폐기 | 주 버튼 비활성 + 스피너 + "준비 중…", 체크박스 비활성. 응답의 새 제안으로 카드 교체 → `pending`. 400 `invalid`(부분집합 아님)·네트워크 오류 → `error`. 409 `item_gone` → `denied`(item_gone 문구). 409 `conflict` → 저장된 결과로 전환(아래 409 행). 410 `expired` → `expired`(다시 요청 숨김) |
| `submitting` | (approve 요청 중) → `executing` | 누른 버튼에 스피너, 두 버튼 비활성, 카드 opacity 유지(흐리게 하지 않음) |
| `confirmed` | `executed` | 버튼 줄 → 결과 줄(220ms 높이 보간): checkmark 14 `--label-2` + 13/18 `--label-2` "저장했어요"/"2개 지웠어요"/"10월 28일 오전 9:00에 알려 드릴게요"/"실행했어요". 카드 본문은 남기되 `--label-2`로 낮춤 |
| `declined` | `rejected` | 결과 줄 "취소했어요" `--label-3`, 본문 접힘(제목만 남긴 1줄 카드, 높이 44) |
| `expired` | `expired` 또는 410 `expired` (CT §3.3) | 버튼 제거, "시간이 지나 취소됐어요" `--label-3` + 오른쪽 텍스트 버튼 "다시 요청"(CT Q9) → `POST /v1/proposals/{id}/revise`에 **원래와 같은 `item_ids`**(add 제안은 빈 본문) → 새 제안으로 같은 자리 교체(`revising` 표시). **`item_ids`가 없는 제안(tool·proactive·remember)도 빈 본문 revise로 같은 내용이 재발급됩니다**(§F-5 해결). 새 모델 턴·컴포저 prefill 없음. **"다시 요청"을 숨기는 경우는 410뿐**: 원 제안이 처음 만들어진 지 24시간이 지나면 서버가 410을 주고, 그때 "다시 요청"을 없애고 "시간이 지나 취소됐어요"만 남깁니다(400 숨김 폴백·횟수 상한 없음). 다시 요청 중 네트워크 오류는 버튼 유지 + 재시도 가능. 토큰 카운트다운·자동 재발급은 없습니다(토큰은 누를 때 발급, CT §3.5.4) |
| `denied` (CT Q14) | SSE confirmation `status:"denied"`, `error_code`, 본문 없음 | 처음부터 결과 줄만 있는 1줄 카드: exclamationmark.circle `--label-2` + 문구를 `error_code`로 결정 (§F-4 해결). **`summary` 없음**(제목·본문·payload 표시 안 함). 코드별 고정 문구(서버 문자열·내부 정보 표시 금지, 텍스트로만):<br>`secret_detected` "비밀번호나 키처럼 보여서 진행하지 않았어요"<br>`cap_exceeded` "허용된 한도를 넘어서 진행하지 않았어요"<br>`tainted` "외부 내용이 섞인 요청이라 진행하지 않았어요"<br>`scope_denied` "이 작업은 할 수 있는 권한이 없어요"<br>`expired` "시간이 지나 진행하지 않았어요"<br>`not_found` "대상을 찾을 수 없어요"<br>`kill_switch` "지금은 이 기능을 쓸 수 없어요"<br>`invalid` "요청 내용이 올바르지 않아 진행하지 않았어요"<br>`item_gone` "그사이 지워진 항목이 있어서 진행하지 않았어요"<br>`conflict` "이미 처리된 요청이에요"(가능하면 결과를 다시 불러와 그 상태로 전환)<br>`payload_mismatch` "내용이 바뀌어서 진행하지 않았어요"<br>그 외·없음 → "진행하지 않았어요". 버튼·재시도 없음. 모델 답변은 따로 이어짐 |
| `error` | `failed`, 네트워크 오류, 400 `invalid`(HTTP 응답일 때) | exclamationmark.circle `--danger` + 13 `--label-2` 이유("실행하지 못했어요"/"연결이 끊겼어요") + [다시 시도](네트워크 오류일 때만; 4xx·failed는 재시도 없음). HTTP 403(`scope_denied`/`tainted`/`kill_switch`)·404 `not_found`·422(`secret_detected`/`cap_exceeded`)는 `denied`와 같은 코드별 고정 문구로 표시 |
| (409 `conflict`) | 저장된 결과 | 다른 기기에서 이미 approve·void됨 → 결과를 다시 불러와 그 상태로 바로 전환, 토스트 없음. 결과를 못 불러오면 `denied` + "이미 처리된 요청이에요" |

**HTTP ↔ `error_code` 매핑 (CT §3.3 기준, 11개)**

| HTTP | `error_code` | UI |
|---|---|---|
| 400 | `invalid` | error(재시도 없음) / SSE면 denied |
| 403 | `scope_denied` / `tainted` / `kill_switch` | denied 고정 문구 |
| 404 | `not_found` | denied 고정 문구 (다른 사용자 것도 동일 본문) |
| 409 | `item_gone` | denied 고정 문구 |
| 409 | `conflict` | 저장된 결과로 전환, 실패 시 denied 문구 |
| 410 | `expired` | expired, "다시 요청" 숨김 |
| 422 | `secret_detected` / `cap_exceeded` / `payload_mismatch` | denied 고정 문구 |

SSE 거부 카드는 같은 `error_code`만 씁니다(HTTP 없음). **이전 사양과의 충돌(CT 우선으로 정리)**: 옛 이름 `action_expired`→`expired`, `action_already_decided`→`conflict`. `payload_mismatch`(422)는 CT §3.3에 MINOR로 추가돼 유지(본문은 코드만). `not_owner`(403)는 CT에 없어 삭제. 분기는 HTTP 상태가 아니라 본문 `error_code`로 하고, 모르는 코드는 `invalid` 문구 — 다른 사용자 제안은 403이 아니라 404 `not_found`. 메모리 직접 편집의 409(동시 수정, B 화면)는 proposals API가 아니라 CT §3.3 밖이므로 기존 문구를 유지합니다.
| `pending·offline` | — | 주 버튼 비활성 + ⑥ "연결되면 확인할 수 있어요". approve는 **outbox에 넣지 않음**(누를 때 토큰 발급, 1회용) |

- 새로고침/재진입: `GET /v1/actions?status=pending`으로 카드 복원(토큰 없음). 토큰은 승인 버튼을 누를 때만 `reissue`로 받습니다.
- 결정된 카드(confirmed/declined/expired)는 스레드 히스토리에 결과 줄 형태로 계속 남음(스레드 로드 시 `pending_actions` 요약, TP §10.3).
- SSE `chat.completion.action_result` 수신 시 같은 상태 전환.

## C4. 데이터 훅 (UI가 기대하는 모양)
SSE `chat.completion.confirmation`(TP §10.3) 필드를 그대로 받습니다:
```js
// card = { action_id, tool, tool_version, summary, payload_view, payload_hash,
//          expires_at, tainted,   // 토큰 필드 없음
//          scopes: ['memory.write', …], status?, error_code?,
//          provenance: { actor: 'user'|'scheduler', job_id, job_name } }
// variant 결정 (UI):
//   tool === 'memory.propose' && payload_view.op === 'delete' → 'forget'
//   tool === 'memory.propose'                                → 'remember'
//   tool === 'proactive.propose_followup'                    → 'proactive'
//   그 외                                                     → 'tool'
// 위험 스타일(CT Q13): scopes의 verb가 send → danger, payload_view.op==='delete' → danger.
//   write는 primary(accent) — 아키텍트 확정 (§F-1 해결)
// 토큰은 approve 직전 reissue 응답으로만 받음(CT §3.5.4). SSE·actions 목록에는 토큰 없음. token_expires_at 카운트다운·자동 재발급 없음
```
API:
- 승인 `POST /v1/actions/{id}/approve` `{confirm_token, payload_hash}` (CSRF·Origin; 브라우저 fetch는 Origin 자동)
- 거절 `POST /v1/actions/{id}/reject`
- 토큰 발급(승인 버튼을 누를 때만, 곧바로 approve) `POST /v1/actions/{id}/reissue`
- 부분 선택 재제안·만료 후 다시 요청 `POST /v1/proposals/{id}/revise` `{item_ids}`(add는 빈 본문) → 새 제안 `{action_id, payload_view, payload_hash, confirm_token, expires_at, …}`. 카드는 `data-action-id`를 새 id로 바꾸고 원 id는 폐기 처리
- 복원 `GET /v1/actions?status=pending`
JS 인터페이스(프론트 구현 가이드):
```js
renderConfirmCard(card, { mount, onSettled })   // DOM 생성, state='pending'
setCardState(action_id, state, { message, result })
// 이벤트: 'confirm' {action_id, payload_hash}  'revise' {action_id, item_ids}  'decline' {action_id}
```
클래스: `.confirm-card[data-variant=remember|forget|proactive|tool][data-state=pending|revising|submitting|checking|confirmed|declined|expired|error]`, `.cc-head .cc-taint .cc-prov .cc-body .cc-actions .cc-primary.cc-danger .cc-secondary .cc-result .cc-meta`.

## C5. 접근성
- 카드 `role="group"` `aria-labelledby=<제목 id>` `aria-describedby=<본문 id, taint 줄 id>`. `role="alertdialog"`는 쓰지 않음(모달이 아님).
- **강제 포커스 없음**(REVIEW-FEEDBACK와 동일). 등장 시 `role=status` 숨김 영역에 "확인이 필요해요: {제목}" 1회. 상태 전환 결과("저장했어요")도 같은 status 영역에 1회.
- 버튼: `<button>` 실제 요소, 최소 44×44pt, 주 버튼 `aria-describedby`로 taint 경고 연결. 파괴적 버튼은 텍스트로 의미 전달(색만으로 구분하지 않음). submitting 중 `aria-busy="true"`, `aria-disabled`.
- 결정 후 포커스가 사라진 버튼에 있었으면 `.cc-result`(tabindex=-1)로 이동.
- forget 체크 목록: `<fieldset>` + `<legend>` "지울 항목", 각 `<input type="checkbox">` + label 전체가 44pt 행.
- 만료 카운트다운은 live 아님. 만료 순간에만 status 1회 "시간이 지나 취소됐어요".
- reduced-motion: 높이 보간·스피너 회전 끔(스피너 → 정적 "…"), opacity만. 한글 `word-break:keep-all; overflow-wrap:anywhere`(body 상속, 긴 URL·ID는 anywhere). Dynamic Type은 앱 전체 과제(REVIEW-FEEDBACK N4)와 함께.

---

# Part B. 메모리

## B0. 데이터 (MEM §1·§4 기준)
항목: `{id, kind: profile|preference|fact|task, text(≤300자), pinned, confidence: user|confirmed, source:{thread_id, message_id}, created_at, updated_at, expires_at}`. 최대 200개, 64KiB.
API: `GET /v1/memory`, `POST /v1/memory/items`, `PATCH /v1/memory/items/{id}`(text, pinned, expires_at), `DELETE /v1/memory/items/{id}`, `DELETE /v1/memory`, `GET /v1/memory/export`. 토글 `memory.enabled`(기본 on, `GET/PATCH /v1/settings`, Q7 확정).

## B1. '기억해' 카드 = §C variant `remember`
- 사용자가 "기억해 …"라고 해도 바로 저장하지 않고 항상 카드(MEM §2-1). 본문은 **서버가 정규화한 최종 텍스트**(payload_view) 그대로 — UI에서 편집 불가(해시 바인딩). 수정하고 싶으면 저장 후 설정에서 편집.
- kind 칩 표시, task면 "30일 뒤 만료" 부가.
- 결과 줄: "저장했어요 · 메모리 보기"(텍스트 링크 → 설정 › 메모리 push).
- 서버 거부(시크릿 필터·상한·taint): 카드 `denied` 상태(C3, CT Q14). 문구는 `error_code`로 결정, 본문 없음.
- payload_view(CT Q11): `{op:"add", items:[{text, kind}], ambiguous:false}`. 본문 = `items[0].text`(정규화 후).

## B2. '잊어줘' 카드 = §C variant `forget`
```
[trash] 메모리에서 지울까요?
 ☑ 아침 브리핑은 한국어로 짧게 받는 걸 선호        선호
 ☑ 주말엔 브리핑 안 받기                          선호
─────────────────
[ 취소 ]                       [ 2개 지우기 ]   (danger)
지운 항목은 암호화된 백업에 최대 7일 남았다가 사라져요.   (11/13 --label-3)
```
- 확실한 매칭(1개 이상): 모두 **체크된 상태**로 시작. 모호한 매칭: `payload_view.ambiguous===true`(CT Q11) → 제목 "어떤 걸 지울까요?", **모두 해제 상태**로 시작, 후보 최대 8개 + "N개 더 보기". payload_view = `{op:"delete", items:[{id, text, kind}], ambiguous}`.
- 행: 체크박스(원형 22px, 체크 시 `--danger` 채움 + 흰 체크), 텍스트 15/20 `--label` 최대 3줄 말줄임, 아래 13 `--label-2` 메타 줄 = kind · `updated_at`(§F-3 해결). 날짜는 짧게: 오늘 `오늘`, 7일 이내 `3일 전`, 올해 `10월 21일`, 그 전 `2025년 3월 2일`(`Intl.RelativeTimeFormat`/`DateTimeFormat` ko-KR), `<time datetime>`로 감쌈. 비슷한 후보를 구분하는 단서. `updated_at`이 없으면 kind만. 행 전체 탭 영역 44pt 이상.
- 주 버튼 문구는 선택 개수 실시간("1개 지우기"), 0개면 비활성 + "지울 항목을 골라 주세요".
- **부분 선택(확정, Q15)**: `selected_ids`는 쓰지 않음. 체크를 바꾼 뒤 주 버튼을 누르면 `POST /v1/proposals/{id}/revise` `{item_ids}` 전송 → 서버가 원래 목록의 부분집합인지 확인하고 **새 제안**(새 `action_id`·`payload_hash`·`confirm_token`)을 반환, 원래 제안은 폐기. 카드는 `revising`(= preparing 표시) → **같은 자리에서 새 제안으로 교체**(스크롤 위치 유지, 높이 보간 220ms), 새 카드는 선택한 항목만 체크된 pending. 사용자가 새 카드의 주 버튼으로 approve. 모든 항목이 체크된 채면 revise 없이 바로 approve.
- 매칭 없음: 카드 없음, 모델 답변만(CT Q16). **P1에서 "메모리 관리 열기" 링크는 붙이지 않음**(신호 필드 없음, 보류).
- 결과 줄: "2개 지웠어요". undo 없음(확인 카드가 이미 확인 단계).

## B3. 설정 › 메모리 화면 `#memoryView`
설정 시트(large) 안 행 "메모리 · 23개 ›" → 시트 내부 스택 push(NATIVE 시트 내비, 뒤로 "설정", 인라인 타이틀 "메모리", 오른쪽 `+`).
```
┌──────────────────────────────────────┐
│ 메모리 사용                     [ ● ] │  memory.enabled
└──────────────────────────────────────┘
 Eve가 대화에 참고할 정보를 기억해요. 저장할 때는 항상 먼저 물어봐요.

고정됨
│ 📌 이름은 건영                         프로필 │
할 일
│ 다음 주 발표 준비 중          11월 25일 만료 │
선호 · 사실 (최신순)
│ 아침 브리핑은 한국어로 짧게…        선호 › │
...
 23 / 200

[ 메모리 내보내기 ]   (텍스트 버튼 --accent)
[ 모든 메모리 지우기 ] (텍스트 버튼 --danger)
```
- 그룹 순서는 주입 순서와 같게(MEM §3): 고정됨 → 만료 안 된 할 일 → 나머지 `updated_at` 최신순. 행: 텍스트 15/20 2줄 말줄임, 오른쪽 kind 13 `--label-3`, `confidence=user`면 별도 표시 없음, `confirmed`는 13 `--label-3` "대화에서" 부가(출처 힌트). 만료 지난 task는 `--label-3` + "만료됨".
- 행 탭 → 편집 화면 push: textarea 17px(≥16), 300자 카운터(280자 넘을 때만 표시, aria-live 없음 — REVIEW-FEEDBACK N1), kind 세그먼트(프로필/선호/사실/할 일), 고정 스위치, 할 일이면 만료일 행. "완료"로 PATCH. 출처가 있으면 하단 "대화에서 저장됨 · 대화 보기"(source.thread_id로 push).
- **직접 추가(+)**: 같은 편집 화면, **항상 빈 칸**(모델·툴 출력·URL 쿼리·해시·딥링크로 prefill 금지, MEM §4 S5-H3·S5-R3). `POST /v1/memory/items`, 바로 저장(`confidence=user`). 서버 거부 이유는 입력 아래 13 `--danger`로 표시하고 입력값 유지(마스킹·자동 수정 없음): "비밀번호·키·카드번호처럼 보이는 내용은 저장할 수 없어요", "300자까지 쓸 수 있어요", "메모리가 가득 찼어요". 409(동시 수정) → "다른 곳에서 바뀌었어요. 다시 불러올게요" 후 새로고침.
- **스와이프 삭제 + 되돌리기**: 왼쪽 스와이프 [고정/해제 (--accent)] [삭제 (--danger)], 풀 스와이프 = 삭제. 행 접힘 260ms → 토스트 "삭제됨 · 되돌리기" 2.8s, 토스트 보조 문구(처음 1회만) "백업에는 최대 7일 남아요"(MEM §7 S5-R2). **DELETE는 토스트가 사라진 뒤 지연 커밋**(THREADS §2.4와 동일, `pagehide` 시 즉시 커밋). 되돌리면 같은 위치에 다시 펼침, 서버 호출 없음.
- 길게 누르기 컨텍스트 메뉴(NATIVE §7): 편집 · 고정 · 복사 · 삭제.
- **끄기**(`memory.enabled=false`): 확인 액션 시트 없이 즉시 반영, 목록은 그대로 보이되 `--label-3`로 낮추고 상단 footer "꺼져 있어요. 저장된 메모리는 남아 있지만 대화에 쓰지 않아요". 끈 상태에서도 편집·삭제 가능.
- **모든 메모리 지우기**: 액션 시트 "모든 메모리를 지울까요? 백업 사본도 복구할 수 없게 돼요." / [모두 지우기](danger) / 취소. 되돌리기 없음. `DELETE /v1/memory`.
- 내보내기: `GET /v1/memory/export` → 파일 다운로드(`eve-memory-YYYY-MM-DD.json`), iOS는 공유 시트.
- 빈 상태: brain 44 `--label-3` + "아직 기억한 게 없어요" 17/600 + "대화 중에 '기억해'라고 하거나 + 로 직접 추가할 수 있어요" 15 `--label-2`.
- 로딩: 행 스켈레톤 3개(THREADS §2.6). 오류: "메모리를 불러오지 못했어요" + [다시 시도]. 메모리 파일 손상으로 읽기 전용(MEM §7 S5-R6): 상단 `--banner-bg` 줄 "지금은 메모리를 바꿀 수 없어요" + `+`·스와이프·편집 비활성. 판단 = `GET /v1/settings`의 `system.memory_read_only`(CT Q17, `GET /v1/memory`엔 없음).
- 스레드별 "메모리 없이" 옵션: **P1 범위 밖**(CT Q18). 컨텍스트 메뉴 항목을 만들지 않음.

## B4. 접근성
- 목록 `role="list"`, 행 `aria-label="선호, 아침 브리핑은 한국어로 짧게 받는 걸 선호, 고정됨"`. 스와이프 액션은 VoiceOver 맞춤 동작(`aria-` 대신 행 안 숨김 버튼 "삭제", "고정")으로도 제공.
- 되돌리기 토스트 `role="status"`, 버튼 포커스 가능, 2.8s → VoiceOver 사용 중(포커스가 토스트 안)이면 타이머 정지.
- 편집 입력 `aria-describedby`로 오류 문구 연결, 오류 시 `aria-invalid="true"`. 모든 행·버튼 44pt, `keep-all`, reduced-motion은 opacity만.

---

## Q. 결정 목록 (CT 기준)
모든 질문이 CT(eve-serving PR #12 `docs/architecture/ui-api-contract.md`)로 정리됐습니다. **CT는 보안 리뷰를 거쳐 머지됐습니다**(eve-serving 16887e7).

| # | 결정 | 반영 |
|---|---|---|
| Q1 | Message `origin`·`job_id`·`read_at` | A1 |
| Q2 | Thread `unread_count`, `updated_at` 정렬 | A1, A3.1 |
| Q3 | `provenance.job_name`(Message·SSE 둘 다) | A1, A2, C4 |
| Q4 | Message `kind`: `null`\|`digest`, 모르는 값은 `null` 취급 | A1, A2 |
| Q5 | **보류(P1 밖)** — job 전용 스레드 없음. 확장안: Thread `kind:"job"` + `job_id`(MINOR) | A1, A3.1, A6에서 UI 제거 |
| Q6 | `POST /v1/threads/{id}/read` → `{unread_count:0}`, 메시지별 read도 유지 | A3.3 |
| Q7 | `GET/PATCH /v1/settings`(부분 merge) | A5, B0 |
| Q8 | 읽기 전용 `system.{proactive_available, tools_available, memory_read_only}`, PATCH 시 400 | A5 |
| Q9 | 만료 후 "다시 요청" = `revise`에 같은 `item_ids`(add는 빈 본문), 새 모델 턴 없음. item_ids 없는 제안도 빈 본문, 24h 뒤 410일 때만 숨김 | C3 |
| Q10 | ~~SSE `token_expires_at`~~ → 토큰은 누를 때 reissue로만 발급(CT §3.5.4), 카운트다운 없음 | C3, C4 |
| Q11 | `payload_view: {op, items:[{id?, text, kind, updated_at}], ambiguous}` + 후보 `updated_at` | B1, B2 |
| Q12 | 툴 `proactive.propose_followup`, `payload_view: {when:{at}, thread_id, display, template_id}` | C2, C4 |
| Q13 | SSE confirmation `scopes`, danger는 send·delete만 | C1, C2, C4 |
| Q14 | 거부 = 카드 `status:"denied"` + `error_code`(11개 확정, CT §3.3), summary 없음 | C3, B1 |
| Q15 | `revise {item_ids}` 부분집합, 새 제안으로 교체 | B2, C3 |
| Q16 | **보류(P1 밖)** — 매칭 없음 = 카드 없음. 확장안: SSE `tool_result` `status:"no_match"`(MINOR) | B2에서 링크 제거 |
| Q17 | `system.memory_read_only` | B3 |
| Q18 | **보류(P1 밖)** — 스레드별 메모리 끄기. 확장안: `threads.settings` `{"memory":false}` 또는 `PATCH /v1/threads/{id}` | B3에서 UI 제거 |

## F. 계약에 대한 피드백 — 모두 해결됨
아키텍트 답변으로 6개 모두 확정(CT PR #12에 반영, 머지됨).
1. ✅ **위험 스타일(Q13)**: danger는 send scope와 삭제에만, write는 primary(파랑). → C1, C2, C4
2. ✅ **원 스레드 없는 선톡(Q5)**: 첫 실행 때 `job_name` 제목으로 새 스레드 생성, 이후 재사용(`scheduled_jobs.thread_id`). 목록은 일반 미읽음 규칙만. → A1
3. ✅ **잊어줘 후보 날짜(Q11)**: 후보에 `updated_at` 포함, 행 메타 줄에 13 `--label-2` 짧은 날짜. → B2
4. ✅ **denied 카드(Q14)**: summary 없음. `error_code` 11개 확정(`payload_mismatch` 추가), 코드별 고정 문구. 옛 코드(`too_long`, `tainted_thread`) 삭제. → C3, B1
5. ✅ **revise 범위(Q9)**: item_ids 없는 제안도 빈 본문 revise로 재발급. 처음 만든 지 24시간 뒤 410일 때만 "다시 요청" 숨김. 400 숨김 폴백·3회 상한 삭제(토큰 자동 재발급은 폐지 — 누를 때만 발급, 서버 체인 상한 3회는 422 `cap_exceeded`). → C3
6. ✅ **출처 아이콘(Q3)**: Message `template_kind`(briefing/watch/followup). sun.horizon / eye / arrow.uturn.forward, 그 외 sparkle. → A1, A2

## 구현 순서 (프론트엔드)
1. A1 데이터·폴링, A2 스레드 표시(출처 줄·시각·그룹·새 메시지 구분선)
2. A3 배지(목록 점/pill, 뒤로 버튼, document.title)와 읽음 규칙(IntersectionObserver + outbox)
3. A5 설정 섹션(토글·조용한 시간·메모리 사용) — `GET/PATCH /v1/settings`
4. §C 공통 카드(상태 표 전부, mock SSE로) → A4 proactive variant
5. B1·B2 카드 variant, B3 메모리 화면, B4
6. QA: reduced-motion, VoiceOver, 오프라인, 누를 때 토큰 발급·응답 유실 시 checking, revise 410, denied 11개 문구, 409 `item_gone`·`conflict`, 두 기기 읽음 동기화, 한글 keep-all, sw 캐시 버전 올림
