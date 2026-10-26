# PROACTIVE-MEMORY-SPEC v1: 선톡 · 메모리 · 공통 확인 카드

대상: `llm-chat-ui`(Eve 웹 채팅). SPEC.md(토큰·모션), NATIVE-SPEC.md(스택 내비게이션, 시트, 컨텍스트 메뉴), THREADS-SPEC.md(목록·토스트·outbox), REVIEW-FEEDBACK.md(칩 패턴)를 그대로 따르고, 여기서는 **추가·변경만** 정의합니다.
근거 문서: eve-serving `docs/architecture/proactive-messaging.md`(이하 PM), `docs/architecture/memory.md`(이하 MEM), `docs/tool-platform.md` §3.2·§10.3(이하 TP). 필드 이름은 문서 그대로 쓰고, 문서에 없는 것은 **[Q#]** 로 표시해 §Q 열린 질문에 모았습니다.

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
- 위치: 브리핑·watch는 **job 전용 스레드**("Eve 브리핑", job당 하나), follow-up은 **원 스레드**.
- in-app 알림 = `GET /v1/notifications`(origin='proactive' AND read_at IS NULL), 읽음 = `POST /v1/messages/{id}/read`.
- UI 갱신: 앱 열기, `visibilitychange→visible`, 포그라운드 60초 주기 폴링(PM §2.1, SSE는 TBD). 오프라인이면 폴링 중단.
- 메시지 목록 응답에 `origin`·`job_id`·`read_at`이 포함돼야 합니다 **[Q1]**. 목록 행 미읽음 개수 **[Q2]**.

## A2. 스레드 안 표시
선톡은 "사용자 질문 없이 Eve가 먼저 말한 것"이므로 **답변과 같은 무버블 본문(17/1.55)** 을 유지하고, 위에 **출처 줄 하나**만 더합니다. 박스·배경색·색상 테두리는 쓰지 않습니다(콘텐츠가 주인공).

```html
<div class="msg assistant proactive" data-origin="proactive" data-job="01J…" data-unread>
  <div class="origin-line">
    <svg class="origin-ic">[sparkle 또는 sun.horizon / bell]</svg>
    <span class="origin-label">Eve가 먼저 보냄 · 아침 브리핑</span>
    <time datetime="2026-10-27T07:30:00+09:00">오전 7:30</time>
  </div>
  <div class="bubble">…</div>
  <div class="actions">복사 · 👍 · 👎</div>
</div>
```
- `.origin-line`: 13/18(--t-footnote) `--origin`, 아이콘 14px stroke 1.75, 간격 6px, 본문과 8px. 아이콘: 브리핑 `sun.horizon`, watch `bell`, follow-up `arrow.uturn.forward`, 알 수 없음 `sparkle`. 템플릿 이름(“아침 브리핑”)은 job 정보에서 받음 **[Q3]**, 없으면 `Eve가 먼저 보냄`만.
- **시각 표시가 기본 표시입니다**: 일반 답변은 시각을 안 보이지만 선톡은 "언제 왔는지"가 의미라 항상 표시. 규칙: 오늘 `오전 7:30`, 어제 `어제 오전 7:30`, 이번 주 `월요일 오전 7:30`, 그 외 `10월 21일 오전 7:30`. `Intl.DateTimeFormat('ko-KR',{hour:'numeric',minute:'2-digit'})`, 시간대는 기기 기준.
- **답변과의 차이**: (1) 출처 줄, (2) 앞에 사용자 버블이 없음, (3) 다시 생성 버튼 없음(재생성할 사용자 턴이 없음), (4) 👍/👎·사유 칩(REVIEW-FEEDBACK)은 동일하게 제공.
- **그룹핑**
  - 선톡 앞에는 **시간 구분선**을 둡니다: 직전 메시지와 30분 이상 떨어졌거나 날짜가 바뀌면 가운데 정렬 `.day-sep` 11/13(--t-caption) `--label-3` "오늘 오전 7:30". 출처 줄의 시각과 중복되면 출처 줄 시각을 숨김.
  - 같은 job의 연속 선톡(사이에 사용자 메시지 없음): 두 번째부터 출처 줄은 시각만(라벨·아이콘 생략), 간격 12px(SPEC "같은 역할 연속").
  - quiet hours 동안 쌓였다가 종료 시각에 나온 요약(PM §4) → 한 개 메시지로 오고, 출처 라벨 "조용한 시간 동안 · 요약" **[Q4]**.
  - follow-up이 원 스레드에 들어오면 앞의 대화와 24px + `.day-sep`로 분리. 
- **미읽음 표시(스레드 안)**: 처음 열 때 미읽음 선톡이 있으면 첫 미읽음 위에 `.unread-sep` "새 메시지" (13/500 `--badge`, 양옆 hairline `--badge` 30%)를 두고 그 위치로 스크롤(`block:'start'`, 내비바 아래 12px). 1.5초 후 구분선만 300ms fade, 자리 유지. 일반 답변은 미읽음 개념 없음.
- 스트리밍 없음: 선톡은 완성본으로 도착 → 등장 애니메이션(280ms fade+8px)만, 커서·타이핑 점 없음. 스레드를 보고 있는 중 폴링으로 도착하면 바닥 근처(80px)일 때만 자동 스크롤, 아니면 `#toBottom` 위에 "새 메시지 1" pill(--badge 배경, 13/600, 높이 28).

## A3. 미읽음 배지
### A3.1 스레드 목록 행
- 행 왼쪽 여백(16px 안쪽)에 **파란 점 10px `--badge`**(Mail 방식). 2개 이상이면 시간 자리 오른쪽에 숫자 pill: 높이 20, 최소폭 20, 패딩 0 6, r999, `--badge` 배경 `--badge-fg` 12/600 tabular-nums, 99+ 상한. 미읽음 행 제목 600 → 그대로, **미리보기는 `--label`로 진하게**(읽음은 `--label-2`).
- 정렬: 기존 `updated_at` 순 그대로(선톡 도착이 updated_at을 올린다고 가정 **[Q2]**). "Eve 브리핑" 스레드는 행 아이콘 자리에 sun.horizon 16px `--label-2`로 job 스레드임을 표시 **[Q5]**.
- 스와이프 액션 추가(THREADS §2.4 앞쪽): 미읽음 행에 **[읽음으로 표시 (--accent)]** 오른쪽 스와이프. 읽은 행에는 없음(“안 읽음으로 표시”는 서버 기능 없음 → 제공 안 함).

### A3.2 앱 / 타이틀
- 목록 라지 타이틀 "대화" 옆이 아니라 **채팅 화면 뒤로 버튼**에 숫자: `‹ 대화 (3)` → iOS처럼 `‹ 3`이 아니라 라벨 오른쪽에 작은 pill(위 규격, 높이 18). 지금 보는 스레드를 제외한 미읽음 합계.
- 문서 제목: `document.title = n ? '(n) Eve' : 'Eve'`(Safari 탭 표시).
- 홈 화면 아이콘 배지: `navigator.setAppBadge(n)` / `clearAppBadge()` 지원 시에만(standalone, 알림 권한 필요, 2차 Web Push와 함께). 미지원이면 무시, 오류 표시 없음.
- 합계 n = `GET /v1/notifications` 결과 개수(사용자 전체 미읽음 선톡).

### A3.3 지움 규칙
1. 스레드 화면이 **보이는 상태(visible, 포그라운드)에서 해당 선톡 메시지가 뷰포트에 50% 이상 1초 노출**되면 읽음(IntersectionObserver). 스레드를 열기만 하고 화면 밖이면 읽지 않음.
2. 읽음 처리: 로컬 즉시(낙관적, 배지·점 감소) → `POST /v1/messages/{id}/read`를 outbox(THREADS §0)에 넣어 전송. 여러 개면 메시지별 POST를 묶어 순차 전송 **[Q6: 스레드 단위 일괄 읽음 API]**.
3. 스와이프 "읽음으로 표시" = 해당 스레드 미읽음 전부 읽음.
4. 실패: 로컬 상태 유지하고 재시도(백오프). 다음 폴링에서 서버가 여전히 미읽음이면 서버 우선.
5. 다른 기기에서 읽은 것 → 폴링에서 사라지면 점·배지 제거(180ms fade).

## A4. 제안 확인 카드 (선톡 쪽)
- follow-up("내일 9시에 다시 알려드릴까요?")은 모델 제안 → `pending_actions` 확인 → job 생성(PM §1). 확인 카드는 **§C 공통 카드, variant `proactive`**.
- scheduler가 만든 제안(watch 결과에서 write 작업 제안 등)은 **토큰 없는 제안**: 카드를 열 때(뷰포트 진입) `POST /v1/actions/{id}/reissue`로 토큰 발급 → 그 전에는 버튼 `확인` 비활성 + "준비 중…". provenance(actor=scheduler, job_id)와 tainted 표시 필수(PM §3, TP §3.2).
- tainted 스레드에서 나온 follow-up 제안은 서버가 만들지 않음(PM §1) → UI에서 별도 처리 없음.

## A5. 설정 › 선톡 (`#settings` large 시트 안 섹션)
iOS 그룹 리스트(SPEC §6.14): 섹션 라벨 13 `--label-2`, 그룹 `--bg-elev-2` r10, 행 44, hairline.

```
선톡
┌──────────────────────────────────────┐
│ Eve가 먼저 말하기               [ ◯ ] │  ← settings.proactive.enabled (기본 off)
└──────────────────────────────────────┘
 Eve가 브리핑이나 알림을 먼저 보낼 수 있어요. 하루 최대 3번.   (13 --label-2, footer)

(켜졌을 때만 아래 그룹이 280ms 높이 보간으로 펼쳐짐)
조용한 시간
┌──────────────────────────────────────┐
│ 시작                        오후 10:00 │  ← quiet_start "22:00"
│ 종료                        오전 8:00  │  ← quiet_end   "08:00"
└──────────────────────────────────────┘
 이 시간에 온 메시지는 알림 없이 보관했다가 끝날 때 한 번에 알려 드려요.

하루 알림 수
│ 하루 최대                    3번  [− +] │  ← daily_cap 0..10 (stepper)

선톡에서 메모리 사용          [ ◯ ]          ← proactive.memory_read (기본 off)
 켜면 이름·선호·진행 중인 일만 참고해요.
```
- 시각 행: 탭하면 행 아래 인라인 `<input type="time" step="900">`(iOS 휠) 펼침, 17px, 값 표시 `--accent`. 저장 형식 `HH:MM`(24h), 표시 `오후 10:00`. 시작=종료면 저장 거부 + 행 아래 13 `--danger` "시작과 종료가 같을 수 없어요". 자정 넘김(22→08) 정상.
- 저장: NATIVE §6 시트 관례대로 "완료" 시 PATCH. 토글은 즉시 낙관적 반영 + 실패 시 롤백·토스트 "설정을 저장하지 못했어요 · 다시 시도". 엔드포인트 미정 **[Q7]**. 서버가 알 수 없는 키를 거부하므로 위 5개 키만 보냄.
- 서버/운영 전역 off(`GW_PROACTIVE_ENABLED=false`·`proactive_off`)면 토글 비활성 + footer "지금은 이 기능을 쓸 수 없어요" **[Q8: 전역 상태 노출 필드]**.
- **잠금 화면 미리보기 설정 없음**: 행을 만들지 않습니다. 2차 Web Push에서도 알림 문구는 SW 고정 문구 "Eve에게서 새 메시지가 있어요"(PM §2.4)이며 내용·제목·발신 job 이름을 넣지 않습니다. 알림 권한 요청 행("알림 받기")은 2차에서 standalone일 때만, 사용자 탭으로만 요청.
- 끄면: job 실행 중단(서버). 기존 선톡 메시지·미읽음은 그대로 남음. 확인 액션 시트 없음(되돌릴 수 있는 설정).

## A6. 상태 · 빈 상태 · 오류
| 상황 | 표현 |
|---|---|
| 선톡 꺼짐, 브리핑 스레드 없음 | 목록에 아무것도 추가하지 않음 |
| 켰지만 아직 메시지 없음 | 설정 footer에 "첫 브리핑은 다음 예정 시각에 와요"만. 빈 브리핑 스레드는 만들지 않음 |
| 브리핑 스레드에 메시지 0 | 빈 상태: sun.horizon 44 `--label-3` + "아직 받은 브리핑이 없어요" 17/600 + "설정에서 시간을 바꿀 수 있어요" 15 `--label-2` |
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
- 버튼: 보조(왼쪽) = `--fill` 배경 `--label`; 주(오른쪽) = `--accent` 배경 흰 글자; **파괴적 주 버튼** = `--danger` 배경 흰 글자(variant forget, 툴의 삭제/전송류). iOS 관례대로 주 버튼 오른쪽.
- 외부 이미지·링크 자동 로드 금지(TP §10.3). URL은 텍스트로만, 탭 불가.
- 채팅 텍스트 "응/네"는 승인으로 쓰지 않음(TP §10.3). 카드 버튼으로만 승인.

## C2. variant
| variant | 아이콘 | 제목 | 본문(④) | 주 버튼 | 보조 | 주 스타일 |
|---|---|---|---|---|---|---|
| `remember` | brain(또는 bookmark) | 메모리에 저장할까요? | 정규화된 최종 텍스트 따옴표 인용 17/1.55 + 아래 kind 칩 13 `--label-2`(`선호`·`사실`·`프로필`·`할 일 · 30일 뒤 만료`) | 저장 | 취소 | accent |
| `forget` | trash | 메모리에서 지울까요? | 매칭 항목 체크 목록 (B2) | N개 지우기 | 취소 | **danger** |
| `proactive` | bell.badge / calendar.badge.clock | 다시 알려 드릴까요? | `summary` 17 + 일시 줄 15 `--label-2`("10월 28일 (화) 오전 9:00") + 위치 "이 대화에서" | 알림 예약 | 괜찮아요 | accent |
| `tool` | 툴 manifest 아이콘, 없으면 wrench | `summary` 그대로 (예 "10/28 15:00 치과 일정 추가") | `payload_view` 키·값 표: 키 13 `--label-2` / 값 15 `--label`, 행 hairline, 최대 6행 + "모두 보기"(시트) | 실행 (툴 정의 동사 우선, 예 "추가") | 취소 | write=accent / send·delete=danger |

버튼 문구 규칙: 주 버튼은 **동사**(저장·지우기·예약·추가·보내기), "확인/예" 금지. 보조는 "취소"(proactive만 "괜찮아요"). 파괴적이면 개수 포함("2개 지우기").

## C3. 상태 표
| 상태 | 서버 `status` (TP) | UI |
|---|---|---|
| `pending` | `pending` (토큰 있음) | 버튼 2개 활성. 만료 30초 전부터 ⑥ "30초 뒤 만료" 카운트(1초 갱신, aria-live 없음) |
| `pending·preparing` | `pending`, `token_sha256` NULL(scheduler) | 뷰포트 진입 시 `reissue` 호출 중: 주 버튼 비활성 + 스피너 14 + "준비 중…" |
| `submitting` | (approve 요청 중) → `executing` | 누른 버튼에 스피너, 두 버튼 비활성, 카드 opacity 유지(흐리게 하지 않음) |
| `confirmed` | `executed` | 버튼 줄 → 결과 줄(220ms 높이 보간): checkmark 14 `--label-2` + 13/18 `--label-2` "저장했어요"/"2개 지웠어요"/"10월 28일 오전 9:00에 알려 드릴게요"/"실행했어요". 카드 본문은 남기되 `--label-2`로 낮춤 |
| `declined` | `rejected` | 결과 줄 "취소했어요" `--label-3`, 본문 접힘(제목만 남긴 1줄 카드, 높이 44) |
| `expired` | `expired` 또는 410 `action_expired` | 버튼 제거, "시간이 지나 취소됐어요" `--label-3` + 오른쪽 텍스트 버튼 "다시 요청"(→ 컴포저에 아무것도 prefill하지 않고, 모델에 재제안 요청 메시지 전송 **[Q9]**). 토큰만 만료(`token_expires_at`)이고 제안은 유효 → 자동으로 `reissue` 1회 후 pending 유지(총 3회 상한, 넘으면 expired 표시) |
| `error` | `failed`, 네트워크 오류, 422 `payload_mismatch`, 403 `not_owner` | exclamationmark.circle `--danger` + 13 `--label-2` 이유("실행하지 못했어요"/"내용이 바뀌어 실행하지 않았어요"/"연결이 끊겼어요") + [다시 시도](네트워크 오류일 때만; 422·403·failed는 재시도 없음) |
| (409 `action_already_decided`) | 저장된 결과 | 다른 기기에서 처리됨 → 해당 결과 상태로 바로 전환, 토스트 없음 |
| `pending·offline` | — | 주 버튼 비활성 + ⑥ "연결되면 확인할 수 있어요". approve는 **outbox에 넣지 않음**(토큰이 짧고 1회용) |

- 새로고침/재진입: `GET /v1/actions?status=pending`으로 카드 복원(토큰 없음) → 뷰포트 진입 시 `reissue`로 토큰 받기(= preparing 상태).
- 결정된 카드(confirmed/declined/expired)는 스레드 히스토리에 결과 줄 형태로 계속 남음(스레드 로드 시 `pending_actions` 요약, TP §10.3).
- SSE `chat.completion.action_result` 수신 시 같은 상태 전환.

## C4. 데이터 훅 (UI가 기대하는 모양)
SSE `chat.completion.confirmation`(TP §10.3) 필드를 그대로 받습니다:
```js
// card = { action_id, tool, tool_version, summary, payload_view, payload_hash,
//          confirm_token?, expires_at, token_expires_at?[Q10], tainted,
//          provenance: { actor: 'user'|'scheduler', job_id } }
// variant 결정 (UI):
//   tool === 'memory.propose' && payload_view.op === 'delete' → 'forget'   [Q11]
//   tool === 'memory.propose'                                → 'remember'
//   tool이 follow-up job 생성 툴                              → 'proactive' [Q12]
//   그 외                                                     → 'tool'
// 위험 스타일: scope가 send/delete류면 danger  [Q13: SSE에 scope 없음]
```
API:
- 승인 `POST /v1/actions/{id}/approve` `{confirm_token, payload_hash}` (CSRF·Origin; 브라우저 fetch는 Origin 자동)
- 거절 `POST /v1/actions/{id}/reject`
- 토큰 발급/재발급 `POST /v1/actions/{id}/reissue`
- 복원 `GET /v1/actions?status=pending`
JS 인터페이스(프론트 구현 가이드):
```js
renderConfirmCard(card, { mount, onSettled })   // DOM 생성, state='pending'|'preparing'
setCardState(action_id, state, { message, result })
// 이벤트: 'confirm' {action_id, payload_hash, selected?}  'decline' {action_id}
```
클래스: `.confirm-card[data-variant=remember|forget|proactive|tool][data-state=pending|preparing|submitting|confirmed|declined|expired|error]`, `.cc-head .cc-taint .cc-prov .cc-body .cc-actions .cc-primary.cc-danger .cc-secondary .cc-result .cc-meta`.

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
API: `GET /v1/memory`, `POST /v1/memory/items`, `PATCH /v1/memory/items/{id}`(text, pinned, expires_at), `DELETE /v1/memory/items/{id}`, `DELETE /v1/memory`, `GET /v1/memory/export`. 토글 `memory_enabled`(기본 on, `users.settings`).

## B1. '기억해' 카드 = §C variant `remember`
- 사용자가 "기억해 …"라고 해도 바로 저장하지 않고 항상 카드(MEM §2-1). 본문은 **서버가 정규화한 최종 텍스트**(payload_view) 그대로 — UI에서 편집 불가(해시 바인딩). 수정하고 싶으면 저장 후 설정에서 편집.
- kind 칩 표시, task면 "30일 뒤 만료" 부가.
- 결과 줄: "저장했어요 · 메모리 보기"(텍스트 링크 → 설정 › 메모리 push).
- 서버 거부(시크릿 필터·상한·taint): 카드가 아니라 모델 답변으로 오는 것으로 가정 **[Q14]**. 카드 error 상태 문구: "저장하지 않았어요: 비밀번호나 키처럼 보여요" / "메모리가 가득 찼어요(200개)".

## B2. '잊어줘' 카드 = §C variant `forget`
```
[trash] 메모리에서 지울까요?
 ☑ 아침 브리핑은 한국어로 짧게 받는 걸 선호        선호 · 10월 26일
 ☑ 주말엔 브리핑 안 받기                          선호 · 10월 20일
─────────────────
[ 취소 ]                       [ 2개 지우기 ]   (danger)
지운 항목은 암호화된 백업에 최대 7일 남았다가 사라져요.   (11/13 --label-3)
```
- 확실한 매칭(1개 이상): 모두 **체크된 상태**로 시작. 모호한 매칭(여러 후보·확신 낮음, MEM §2-4): 제목 "어떤 걸 지울까요?", **모두 해제 상태**로 시작, 후보 최대 8개 + "N개 더 보기". 구분 필드 **[Q11]**.
- 행: 체크박스(원형 22px, 체크 시 `--danger` 채움 + 흰 체크), 텍스트 15/20 `--label` 최대 3줄 말줄임, 아래 13 `--label-2` kind·created 날짜. 행 전체 탭 영역 44pt 이상.
- 주 버튼 문구는 선택 개수 실시간("1개 지우기"), 0개면 비활성 + "지울 항목을 골라 주세요".
- **부분 선택 문제**: `payload_hash`가 "삭제할 id 목록"에 바인딩되므로 사용자가 일부를 해제하면 해시가 달라짐 → approve 본문에 선택 id를 보낼지, 재제안을 받을지 미정 **[Q15]**. 결정 전 임시안: 체크 변경 시 approve에 `selected_ids` 추가 전송을 가정하고 UI는 그대로 둠.
- 매칭 없음: 카드 없이 모델 답변 "찾지 못했어요" + UI가 답변 아래 텍스트 링크 "메모리 관리 열기"(→ 설정 › 메모리)를 붙임(MEM §2-4 "설정 화면 안내") **[Q16: 신호 필드]**.
- 결과 줄: "2개 지웠어요". undo 없음(확인 카드가 이미 확인 단계).

## B3. 설정 › 메모리 화면 `#memoryView`
설정 시트(large) 안 행 "메모리 · 23개 ›" → 시트 내부 스택 push(NATIVE 시트 내비, 뒤로 "설정", 인라인 타이틀 "메모리", 오른쪽 `+`).
```
┌──────────────────────────────────────┐
│ 메모리 사용                     [ ● ] │  memory_enabled
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
- **끄기**(`memory_enabled=false`): 확인 액션 시트 없이 즉시 반영, 목록은 그대로 보이되 `--label-3`로 낮추고 상단 footer "꺼져 있어요. 저장된 메모리는 남아 있지만 대화에 쓰지 않아요". 끈 상태에서도 편집·삭제 가능.
- **모든 메모리 지우기**: 액션 시트 "모든 메모리를 지울까요? 백업 사본도 복구할 수 없게 돼요." / [모두 지우기](danger) / 취소. 되돌리기 없음. `DELETE /v1/memory`.
- 내보내기: `GET /v1/memory/export` → 파일 다운로드(`eve-memory-YYYY-MM-DD.json`), iOS는 공유 시트.
- 빈 상태: brain 44 `--label-3` + "아직 기억한 게 없어요" 17/600 + "대화 중에 '기억해'라고 하거나 + 로 직접 추가할 수 있어요" 15 `--label-2`.
- 로딩: 행 스켈레톤 3개(THREADS §2.6). 오류: "메모리를 불러오지 못했어요" + [다시 시도]. 메모리 파일 손상으로 읽기 전용(MEM §7 S5-R6): 상단 `--banner-bg` 줄 "지금은 메모리를 바꿀 수 없어요" + `+`·스와이프·편집 비활성 **[Q17: 읽기 전용 신호]**.
- 스레드별 "메모리 없이" 옵션(MEM §3)은 채팅 컨텍스트 메뉴 항목으로 후속 과제 **[Q18]**.

## B4. 접근성
- 목록 `role="list"`, 행 `aria-label="선호, 아침 브리핑은 한국어로 짧게 받는 걸 선호, 고정됨"`. 스와이프 액션은 VoiceOver 맞춤 동작(`aria-` 대신 행 안 숨김 버튼 "삭제", "고정")으로도 제공.
- 되돌리기 토스트 `role="status"`, 버튼 포커스 가능, 2.8s → VoiceOver 사용 중(포커스가 토스트 안)이면 타이머 정지.
- 편집 입력 `aria-describedby`로 오류 문구 연결, 오류 시 `aria-invalid="true"`. 모든 행·버튼 44pt, `keep-all`, reduced-motion은 opacity만.

---

## Q. 열린 질문 (API·문서 공백)
| # | 질문 | 관련 |
|---|---|---|
| Q1 | 메시지 조회 응답(`GET /v1/threads/:id/messages`)에 `origin`·`job_id`·`read_at` 포함 여부 | PM §3, threads-api |
| Q2 | 스레드 목록에 `unread_count`(proactive 미읽음) 필드, 선톡 도착 시 `threads.updated_at` 갱신 여부 | PM §2.1 |
| Q3 | 출처 라벨용 job/템플릿 표시 이름(TP는 카드에 "job 이름" 표시를 요구하지만 SSE `provenance`에는 `actor`·`job_id`만 있음) | TP §3.2, §10.3 |
| Q4 | quiet hours 종료 요약 메시지를 구분하는 표시(필드 또는 dedupe_key 규칙) | PM §4 |
| Q5 | 스레드가 job 전용 스레드인지 알리는 필드(예: thread `job_id`/`kind`) | PM §3 |
| Q6 | 스레드 단위 일괄 읽음 API(`POST /v1/threads/{id}/read` 등). 없으면 메시지별 POST N회 | PM §2.1 |
| Q7 | `users.settings` 조회·수정 엔드포인트(예: `GET/PATCH /v1/settings`)와 키 경로: `settings.proactive.{enabled,quiet_start,quiet_end,daily_cap,memory_read}`, `memory_enabled`는 최상위인지 `settings.memory.enabled`인지 | PM §3, MEM §3 |
| Q8 | 운영 전역 off(`GW_PROACTIVE_ENABLED`/`proactive_off`)를 UI가 알 수 있는 필드 | PM §1, §4 |
| Q9 | 만료된 제안의 "다시 요청" 경로(새 모델 턴으로 재제안 vs 없음) | TP §3.2 |
| Q10 | SSE confirmation에 `token_expires_at` 포함 여부(카운트다운·자동 reissue에 필요). 현재 `expires_at`만 | TP §10.3 |
| Q11 | `memory.propose` payload_view 형태: `op`(`add`/`delete`), `text`, `kind`, delete의 `items:[{id,text,kind,created_at}]`, 모호 여부(`ambiguous: true` 또는 `candidates`) | MEM §2 |
| Q12 | follow-up job 생성 툴 이름과 payload_view(`when`, `thread_id`, 표시용 일시) | PM §1 |
| Q13 | 카드의 위험 스타일 결정을 위한 `scope`(write/send/delete) SSE 노출 | TP §3 |
| Q14 | 시크릿 필터·상한·taint 거부 시 카드 미생성 + 모델 답변인지, 카드 error인지 | MEM §2, §7 |
| Q15 | 잊어줘 카드에서 사용자가 일부 해제할 때: approve에 `selected_ids`를 보내 서버가 부분집합 검증? 또는 재제안? (`payload_hash`는 id 목록에 바인딩) | MEM §2-4, S10-L4 |
| Q16 | "매칭 없음"을 UI가 알 신호(설정 안내 링크용) | MEM §2-4 |
| Q17 | 메모리 읽기 전용 상태 노출 필드(`GET /v1/memory` 응답) | MEM §7 |
| Q18 | 스레드별 "메모리 없이" 옵션의 API 필드 | MEM §3 |

## 구현 순서 (프론트엔드)
1. A1 데이터·폴링, A2 스레드 표시(출처 줄·시각·그룹·새 메시지 구분선)
2. A3 배지(목록 점/pill, 뒤로 버튼, document.title)와 읽음 규칙(IntersectionObserver + outbox)
3. A5 설정 섹션(토글·조용한 시간·하루 수) — 엔드포인트는 Q7 확정 전 mock
4. §C 공통 카드(상태 표 전부, mock SSE로) → A4 proactive variant
5. B1·B2 카드 variant, B3 메모리 화면, B4
6. QA: reduced-motion, VoiceOver, 오프라인, 토큰 만료·재발급 3회, 409, 두 기기 읽음 동기화, 한글 keep-all, sw 캐시 버전 올림
