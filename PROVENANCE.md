# Provenance

This release is a snapshot of commit `c79afc6` of the authors' private repository, without its history.
The table lists every commit of that repository in order, with its time and subject, so that readers can
see what was fixed before which result (for example the development-set decisions, the exploratory
truncation plan and the human-scoring sample were committed before the test answers were judged).
The full history will be made public after review. Commit subjects are partly in Korean.

| commit | time | subject |
| --- | --- | --- |
| `75096c4` | 2026-11-10T22:32:40+09:00 | G0: 환경 확인 스크립트와 Modelfile |
| `f5a69d6` | 2026-11-10T22:33:34+09:00 | G0: dev/test 분할과 SAFE-Mem 부분집합 목록 (seed 20261028) |
| `0c051d0` | 2026-11-11T10:52:43+09:00 | 실험 코드와 프롬프트 v1 (등록 osf.io/[withheld for review] 이후, dev 전) |
| `d7b8eff` | 2026-11-11T11:14:40+09:00 | 허위 사실 생성 프롬프트 개선: 짧은 W, 1인칭 메모, 질문 복사 금지 (dev 전, 시험 생성 결과 반영) |
| `0ca7e1c` | 2026-11-11T11:17:05+09:00 | 선호도 문항용 허위 사실 생성 안내 추가 (dev 전) |
| `332987c` | 2026-11-11T03:03:32Z | 허위 사실 생성 n3 (500문항) + 품질 확인용 50문항 추출 |
| `0942413` | 2026-11-11T12:05:58+09:00 | 재생성 시 거절 이유를 프롬프트에 추가, 실패 문항만 재생성하는 옵션 (dev 전) |
| `59ef0dc` | 2026-11-11T03:10:02Z | 실패 24문항 재생성 (거절 이유 피드백) |
| `a7756dc` | 2026-11-11T12:14:31+09:00 | 허위 사실 50문항 품질 확인: 실패 3/50, 통과 (AI 초안, 저자 확인) |
| `5ca076e` | 2026-11-11T13:38:25+09:00 | SAFE-Mem 실행 연결 코드 (등록본 2.5절, 충실도 기록 5.7절) |
| `1fc8446` | 2026-11-11T07:03:15Z | SAFE-Mem progress answers_safemem_n3_kaggle_s0.jsonl: 5/40 |
| `f61ca00` | 2026-11-11T07:13:05Z | SAFE-Mem progress answers_safemem_n3_kaggle_s1.jsonl: 5/40 |
| `4d103da` | 2026-11-11T21:53:09Z | 버그 수정: SAFE-Mem 진행 저장 (작업 중 파일이 있어도 rebase, 두 샤드 동시 저장 잠금, 실패 시 로그 표시). 답변 생성은 변경 없음 |
| `50c1ffe` | 2026-11-12T06:57:55+09:00 | 채점 기준 고정(결과 보기 전), 판정 표본에 질문 유형 칸, 결과 표·그림 코드 |
| `36368fd` | 2026-11-12T06:31:28Z | SAFE-Mem progress answers_safemem_n3_kaggle_s1.jsonl: 10/40 |
| `336f611` | 2026-11-12T06:41:36Z | SAFE-Mem progress answers_safemem_n3_kaggle_s0.jsonl: 10/40 |
| `d54d98e` | 2026-11-12T08:46:55Z | SAFE-Mem progress answers_safemem_n3_kaggle_s1.jsonl: 15/40 |
| `f4e62d8` | 2026-11-12T09:00:13Z | SAFE-Mem progress answers_safemem_n3_kaggle_s0.jsonl: 15/40 |
| `498b952` | 2026-11-12T10:50:28Z | SAFE-Mem progress answers_safemem_n3_kaggle_s1.jsonl: 20/40 |
| `3a630f8` | 2026-11-12T11:15:02Z | SAFE-Mem progress answers_safemem_n3_kaggle_s0.jsonl: 20/40 |
| `8579059` | 2026-11-12T12:58:02Z | SAFE-Mem progress answers_safemem_n3_kaggle_s1.jsonl: 25/40 |
| `7c086ae` | 2026-11-12T13:37:01Z | SAFE-Mem progress answers_safemem_n3_kaggle_s0.jsonl: 25/40 |
| `0f7f421` | 2026-11-12T15:04:44Z | SAFE-Mem progress answers_safemem_n3_kaggle_s1.jsonl: 30/40 |
| `b1219a7` | 2026-11-12T16:24:06Z | SAFE-Mem progress answers_safemem_n3_kaggle_s0.jsonl: 26/40 |
| `55d13a7` | 2026-11-12T16:49:15Z | SAFE-Mem progress answers_safemem_n3_kaggle_s0.jsonl: 27/40 |
| `b66328e` | 2026-11-13T02:03:57+09:00 | dev 답변 8,344행과 실행 기록 (중단·재개, 폐기 4행, 잘린 답 978행) |
| `f14d6fe` | 2026-11-12T17:13:10Z | SAFE-Mem progress answers_safemem_n3_kaggle_s0.jsonl: 28/40 |
| `58f8367` | 2026-11-12T17:32:02Z | SAFE-Mem progress answers_safemem_n3_kaggle_s0.jsonl: 29/40 |
| `4114367` | 2026-11-12T17:57:24Z | dev 판정 결과 (gemma4:12b, 두 GPU에 나눠 판정 후 원래 순서로 합침) |
| `661b37b` | 2026-11-12T17:59:54Z | SAFE-Mem progress answers_safemem_n3_kaggle_s0.jsonl: 30/40 |
| `9854d57` | 2026-11-12T18:26:40Z | SAFE-Mem progress answers_safemem_n3_kaggle_s0.jsonl: 31/40 |
| `4dd1d03` | 2026-11-12T18:49:41Z | SAFE-Mem progress answers_safemem_n3_kaggle_s0.jsonl: 32/40 |
| `21a90d2` | 2026-11-13T03:52:45+09:00 | 반복 실행 변동 확인용 답변 (run 1, run 2: D0·D5_50, C2, var50) 과 실행 기록 |
| `2149099` | 2026-11-12T19:02:02Z | 반복 실행 변동 확인용 판정 (run 1, run 2; gemma4:12b) |
| `9d27a38` | 2026-11-12T19:09:58Z | SAFE-Mem progress answers_safemem_n3_kaggle_s0.jsonl: 33/40 |
| `a4a6109` | 2026-11-12T19:31:04Z | SAFE-Mem progress answers_safemem_n3_kaggle_s0.jsonl: 34/40 |
| `beaa06f` | 2026-11-12T19:56:10Z | SAFE-Mem progress answers_safemem_n3_kaggle_s0.jsonl: 35/40 |
| `a11df2d` | 2026-11-12T20:17:56Z | SAFE-Mem progress answers_safemem_n3_kaggle_s0.jsonl: 36/40 |
| `d309607` | 2026-11-12T20:43:20Z | SAFE-Mem progress answers_safemem_n3_kaggle_s0.jsonl: 37/40 |
| `1e2ae64` | 2026-11-12T21:08:01Z | SAFE-Mem progress answers_safemem_n3_kaggle_s0.jsonl: 38/40 |
| `c5fcf88` | 2026-11-12T21:31:10Z | SAFE-Mem progress answers_safemem_n3_kaggle_s0.jsonl: 39/40 |
| `ae2f163` | 2026-11-12T21:55:00Z | SAFE-Mem progress answers_safemem_n3_kaggle_s0.jsonl: 40/40 |
| `ba3de0f` | 2026-11-13T09:25:45+09:00 | dev 결정 고정: 공격 확인 통과(39.7%p), 상한 50%, 가산 여유 0.05, 반복 변동 0/98 -> test 1회 (등록본 5.4절) |
| `d8a332c` | 2026-11-13T01:08:48Z | SAFE-Mem progress answers_safemem_n3_kaggle_s2.jsonl: 1/40 |
| `a51f72e` | 2026-11-13T01:17:41Z | SAFE-Mem progress answers_safemem_n3_kaggle_s1.jsonl: 31/40 |
| `f9d433b` | 2026-11-13T10:26:37+09:00 | 탐색 분석 계획 고정 (test 판정 전): 잘린 답 재판정, 관대 채점, 등록 규칙 결과와 함께 보고 |
| `811cbcf` | 2026-11-13T01:33:46Z | SAFE-Mem progress answers_safemem_n3_kaggle_s2.jsonl: 2/40 |
| `3d8d78c` | 2026-11-13T01:46:24Z | SAFE-Mem progress answers_safemem_n3_kaggle_s1.jsonl: 32/40 |
| `3555726` | 2026-11-13T01:57:04Z | SAFE-Mem progress answers_safemem_n3_kaggle_s2.jsonl: 3/40 |
| `395b7f3` | 2026-11-13T02:10:53Z | SAFE-Mem progress answers_safemem_n3_kaggle_s1.jsonl: 33/40 |
| `c8a1da0` | 2026-11-13T02:17:17Z | SAFE-Mem progress answers_safemem_n3_kaggle_s2.jsonl: 4/40 |
| `51f5f0d` | 2026-11-13T02:38:19Z | SAFE-Mem progress answers_safemem_n3_kaggle_s1.jsonl: 34/40 |
| `bf672f4` | 2026-11-13T02:40:44Z | SAFE-Mem progress answers_safemem_n3_kaggle_s2.jsonl: 5/40 |
| `98644e7` | 2026-11-13T03:06:52Z | SAFE-Mem progress answers_safemem_n3_kaggle_s1.jsonl: 35/40 |
| `b4af3ee` | 2026-11-13T03:08:09Z | SAFE-Mem progress answers_safemem_n3_kaggle_s2.jsonl: 6/40 |
| `367bd03` | 2026-11-13T03:30:27Z | SAFE-Mem progress answers_safemem_n3_kaggle_s2.jsonl: 7/40 |
| `db4c7e9` | 2026-11-13T03:37:45Z | SAFE-Mem progress answers_safemem_n3_kaggle_s1.jsonl: 36/40 |
| `8470317` | 2026-11-13T03:53:14Z | SAFE-Mem progress answers_safemem_n3_kaggle_s2.jsonl: 8/40 |
| `5c77fbd` | 2026-11-13T04:09:04Z | SAFE-Mem progress answers_safemem_n3_kaggle_s1.jsonl: 37/40 |
| `d1d8519` | 2026-11-13T04:22:01Z | SAFE-Mem progress answers_safemem_n3_kaggle_s2.jsonl: 9/40 |
| `6c316ef` | 2026-11-13T04:33:51Z | SAFE-Mem progress answers_safemem_n3_kaggle_s1.jsonl: 38/40 |
| `e190ae3` | 2026-11-13T04:48:02Z | SAFE-Mem progress answers_safemem_n3_kaggle_s2.jsonl: 10/40 |
| `7a76906` | 2026-11-13T05:01:13Z | SAFE-Mem progress answers_safemem_n3_kaggle_s1.jsonl: 39/40 |
| `de2a54f` | 2026-11-13T05:08:04Z | SAFE-Mem progress answers_safemem_n3_kaggle_s2.jsonl: 11/40 |
| `b889aed` | 2026-11-13T05:28:03Z | SAFE-Mem progress answers_safemem_n3_kaggle_s1.jsonl: 40/40 |
| `2b49fb5` | 2026-11-13T05:30:00Z | SAFE-Mem progress answers_safemem_n3_kaggle_s2.jsonl: 12/40 |
| `b518513` | 2026-11-13T05:51:17Z | SAFE-Mem progress answers_safemem_n3_kaggle_s2.jsonl: 13/40 |
| `16f1024` | 2026-11-13T06:13:32Z | SAFE-Mem progress answers_safemem_n3_kaggle_s2.jsonl: 14/40 |
| `1d644cc` | 2026-11-13T06:36:55Z | SAFE-Mem progress answers_safemem_n3_kaggle_s2.jsonl: 15/40 |
| `0542954` | 2026-11-13T07:05:32Z | SAFE-Mem progress answers_safemem_n3_kaggle_s2.jsonl: 16/40 |
| `a3ae04a` | 2026-11-13T07:25:54Z | SAFE-Mem progress answers_safemem_n3_kaggle_s2.jsonl: 17/40 |
| `324ed28` | 2026-11-13T07:50:01Z | SAFE-Mem progress answers_safemem_n3_kaggle_s2.jsonl: 18/40 |
| `20bbaa5` | 2026-11-13T08:13:29Z | SAFE-Mem progress answers_safemem_n3_kaggle_s2.jsonl: 19/40 |
| `43855f0` | 2026-11-13T08:39:24Z | SAFE-Mem progress answers_safemem_n3_kaggle_s2.jsonl: 20/40 |
| `676e16d` | 2026-11-13T09:02:28Z | SAFE-Mem progress answers_safemem_n3_kaggle_s2.jsonl: 21/40 |
| `1a09ae6` | 2026-11-13T09:28:54Z | SAFE-Mem progress answers_safemem_n3_kaggle_s2.jsonl: 22/40 |
| `4d2314a` | 2026-11-13T09:48:29Z | SAFE-Mem progress answers_safemem_n3_kaggle_s2.jsonl: 23/40 |
| `f58e3ca` | 2026-11-13T10:11:54Z | SAFE-Mem progress answers_safemem_n3_kaggle_s2.jsonl: 24/40 |
| `e339de5` | 2026-11-13T10:30:17Z | SAFE-Mem progress answers_safemem_n3_kaggle_s2.jsonl: 25/40 |
| `ba714e1` | 2026-11-13T10:51:35Z | SAFE-Mem progress answers_safemem_n3_kaggle_s2.jsonl: 26/40 |
| `1d8db4f` | 2026-11-13T11:15:17Z | SAFE-Mem progress answers_safemem_n3_kaggle_s2.jsonl: 27/40 |
| `c489f4c` | 2026-11-13T11:39:21Z | SAFE-Mem progress answers_safemem_n3_kaggle_s2.jsonl: 28/40 |
| `2b16764` | 2026-11-13T12:01:46Z | SAFE-Mem progress answers_safemem_n3_kaggle_s2.jsonl: 29/40 |
| `4e30459` | 2026-11-14T03:07:48Z | SAFE-Mem progress answers_safemem_n3_kaggle_s2.jsonl: 30/40 |
| `e4a2d6a` | 2026-11-14T03:35:36Z | SAFE-Mem progress answers_safemem_n3_kaggle_s2.jsonl: 31/40 |
| `5900729` | 2026-11-14T03:38:12Z | 적응형 공격 문장 (등록본 2.7절, gemma4:12b, dev 결정 후) |
| `27c84a6` | 2026-11-14T04:02:31Z | SAFE-Mem progress answers_safemem_n3_kaggle_s2.jsonl: 32/40 |
| `3b40664` | 2026-11-14T04:30:15Z | SAFE-Mem progress answers_safemem_n3_kaggle_s2.jsonl: 33/40 |
| `7c7d8f5` | 2026-11-14T13:30:37+09:00 | 결과 해석 틀과 사람 채점 요약 고정 (test 판정 전) |
| `e48502d` | 2026-11-14T04:57:48Z | SAFE-Mem progress answers_safemem_n3_kaggle_s2.jsonl: 34/40 |
| `f08e74c` | 2026-11-14T05:23:54Z | SAFE-Mem progress answers_safemem_n3_kaggle_s2.jsonl: 35/40 |
| `8eae962` | 2026-11-14T05:49:46Z | SAFE-Mem progress answers_safemem_n3_kaggle_s2.jsonl: 36/40 |
| `9379951` | 2026-11-14T06:16:59Z | SAFE-Mem progress answers_safemem_n3_kaggle_s2.jsonl: 37/40 |
| `6179588` | 2026-11-14T06:44:26Z | SAFE-Mem progress answers_safemem_n3_kaggle_s2.jsonl: 38/40 |
| `e8b5233` | 2026-11-14T07:04:56Z | SAFE-Mem progress answers_safemem_n3_kaggle_s2.jsonl: 39/40 |
| `9ede81c` | 2026-11-14T07:34:07Z | SAFE-Mem progress answers_safemem_n3_kaggle_s2.jsonl: 40/40 |
| `47a369a` | 2026-11-14T19:15:39+09:00 | SAFE-Mem 충실도 확인(등록본 5.7 a-d)과 판정기 검증 추가 계산 스크립트, 해석 틀 H5 규칙 정정 (test 판정 전) |
| `d53a9c2` | 2026-11-15T17:27:48+09:00 | test 답변 9,688행과 실행 기록 (중단 없음, 잘린 답 1,387행) |
| `173262b` | 2026-11-15T09:20:17Z | test 판정 결과 (gemma4:12b, 두 GPU에 나눠 판정 후 원래 순서로 합침) |
| `b11f5f5` | 2026-11-15T09:50:21Z | 잘린 답 재판정(탐색, 계획 f9d433b) + SAFE-Mem 판정 (gemma4:12b) |
| `7405810` | 2026-11-15T18:51:42+09:00 | 판정기 검증 표본 200개와 공격 채점 표본, 키 (사람 채점 전 고정, 키는 채점 후에만 연다) |
| `3569b38` | 2026-11-15T19:28:00+09:00 | 사람 채점 1: 정답 200개 완료 (시작 __:__, 끝 __:__, 휴식 _회, unsure 0). 키는 아직 열지 않음 |
| `7dcaee9` | 2026-11-15T19:39:45+09:00 | 사람 채점 완료: 정답 200개, 공격 90개 (시작 __:__, 끝 __:__, 휴식 _회, unsure 0). 키는 이 커밋 뒤에 연다 |
| `346a016` | 2026-11-15T19:41:17+09:00 | 사람 채점 기록 (실제 시각, 휴식·unsure 0). 키를 열기 전 |
| `ccf78ab` | 2026-11-15T19:42:04+09:00 | 판정기 검증 결과: 정답 일치 91.0% (kappa 0.807), 잘리지 않은 행 97.1% (0.939), 공격 90.0% (0.800) |
| `a488b9a` | 2026-11-15T19:43:09+09:00 | 확증 결과: H1 지지(+8.2pt), H2 판단 불가, H3 기각(-7.1pt), H4 판단 불가, H5 지지(-48.3pt). 판정기 검증 결과 UTF-8로 다시 저장 |
| `7f141d6` | 2026-11-15T19:43:55+09:00 | SAFE-Mem 충실도(등록본 5.7): 파싱 실패 0.0%, C0에서 D6' 44.2% vs D0 61.7% (p=0.0015) -> 저장 파이프라인 성능 낮음 경고 발동 |
| `f8c7da3` | 2026-11-15T19:44:51+09:00 | 탐색 분석(계획 f9d433b): 잘린 답 재판정 시 532/1387 정답, 다섯 판정 모두 동일, H1 +12.3pt (확증 +8.2pt) |
| `c8cf99d` | 2026-11-15T19:49:07+09:00 | 절충 그림: 몰린 조건의 이름표 위치 조정 (계산 변경 없음) |
| `228c594` | 2026-11-15T20:02:58+09:00 | 판정기 검증 불일치 18건 분류 (저자 확정, AI 초안 참고): 잘림 규칙 13, 판정기 오류 5, 사람 오류 1(172, 잘린 행) |
| `ec9dfea` | 2026-11-15T21:51:23+09:00 | 적응형 공격 답변 1,368행과 실행 기록 (첫 시도 21/79 폐기 후 15/85로 재실행), 불일치 확인 파일 |
| `f749388` | 2026-11-15T13:14:58Z | 적응형 공격 판정 결과 (gemma4:12b, 두 GPU에 나눠 판정 후 원래 순서로 합침) |
| `6f5282d` | 2026-11-15T22:18:30+09:00 | 결과 표·그림 (적응형 공격 포함): accuracy/asr/contrasts 표, 절충 그림, summary.json |
| `cd08167` | 2026-11-15T22:24:20+09:00 | 공개용 익명 사본 도구와 심사자 안내 (적응형 공격 문장 제외) |
| `c79afc6` | 2026-11-15T22:25:38+09:00 | 공개 사본 도구: UTF-16 파일도 익명화하고, 마지막에 사본 전체에서 이름이 남았는지 다시 검사 |

Tags: `decisions-frozen` at `6ab1c9b`, `dev-freeze` at `c4fbdeb`
