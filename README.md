# sap-notes

차근차근 따라가는 학습 노트 사이트예요. 지금은 SAPUI5와 SAP ABAP 수업 정리 노트가 있어요.

주소: https://wangjagom.github.io/sap-notes/

사이트는 Astro로 만들어요. `main`에 push하면 GitHub Actions가 빌드해서 GitHub Pages에 배포해요.
예전 파이썬 빌드(`tools/build.py`)는 결과를 비교하고 그림 조각을 뽑는 용도로만 남아 있어요.

## 노트 (키워드 카드형)

두 노트는 정적 HTML이에요. `notes/`에서 만들어 `public/`에 넣으면 Astro가 그대로 배포해요.

```
notes/
├─ shared/            공통 스타일(v4.css), 글꼴, 아이콘
├─ abap/base.html     ABAP 노트 본문(원본)
├─ abap/build.py      → public/abap/index.html
├─ ui5/src/*.txt      UI5 노트 카드 원본 (아래 문법)
├─ ui5/conv.py        카드 원본 → 본문 HTML
└─ ui5/build.py       → public/sap-ui5/index.html
public/abap/img/      ABAP 노트 화면 사진
```

```bash
python notes/abap/build.py
python notes/ui5/build.py
```

UI5 카드 원본 문법:

```
@ch ch-1 | 1부 | 제목 | 부 소개 한 줄
@kw 키워드 이름
d: 한 줄 정의 (핵심만 보기에서도 보여요)
e: 쉬운 설명   l: 비유   s: 보충   w: 주의
t:            문법 틀 (마침표 한 줄로 끝)
c:js          코드 (js, xml, json, text) (마침표 한 줄로 끝)
tb:           표: "칸 | 칸" 한 줄씩 (마침표 한 줄로 끝)
m: 더 알아보기 제목  ...  /m
```

## 예전 교재

긴 글로 쓴 예전 교재 원본은 `archive/`에 있어요(빌드에 안 써요). 이전 Astro 교재 틀(`src/`, `tools/`)은 다시 쓸 때를 위해 남겨 뒀어요.

## 폴더 구조

```
sap-notes/
├─ content/                       글(원본)
│   ├─ site.json                  첫 화면의 카드·링크 목록
│   ├─ sap-backend/doc.md         SAP 백엔드 총정리 (본문)
│   ├─ sap-backend/book.yaml      교재 설정: 제목, 목차 그룹, 부 아이콘, 외부 링크 (Astro용)
│   ├─ sap-ui5/doc.md             SAPUI5 총정리
│   └─ sap-ui5/book.yaml          교재 설정
├─ src/                           Astro
│   ├─ pages/index.astro          첫 화면
│   ├─ pages/[book]/index.astro   교재 페이지 (content/<주제>/book.yaml 있는 폴더마다 하나)
│   ├─ layouts/BookLayout.astro   교재 틀: 머리말, 목차, 레일, 모바일 서랍, "이 부의 개념"
│   ├─ content.config.ts          Content Collections (교재 로더)
│   ├─ lib/book/                  마크다운 -> 부/개념 구조 (build.py와 같은 규칙)
│   ├─ plugins/                   remark 플러그인: 전용 코드 블록, 표
│   ├─ legacy/                    파이썬 그림 모듈이 만든 정적 조각 (tools/export_legacy.py 결과, 커밋해요)
│   ├─ styles/style.css           교재 스타일
│   └─ scripts/app.js             교재 동작: 페이지 이동, 문제, 문법 탭, 스크롤 애니메이션
├─ tools/                         파이썬
│   ├─ build.py                   예전 빌드 (Astro 결과와 비교할 때만)
│   ├─ export_legacy.py           그림·아이콘·미리보기 카드를 src/legacy/로 뽑기
│   ├─ figures/                   그림·애니메이션 모듈 (registry.py가 이름 -> 그림 목록)
│   └─ _archive/                  빌드에 안 쓰는 옛 실험 파일
├─ fonts/                         Pretendard (파이썬 빌드용, OFL)
└─ .github/workflows/             deploy.yml(main → Pages 배포), astro-build.yml(다른 브랜치 빌드 확인)
```

## 로컬에서 빌드하기

### Astro

Node.js 20 이상이 필요해요. 파이썬은 필요 없어요.

```bash
npm install
npm run dev        # http://localhost:4321/sap-notes/
npm run build      # 타입 검사 + dist/ 생성
npm run preview    # dist/ 미리보기
```

그림 모듈(`tools/figures/`)이나 아이콘 표(`tools/icon_map2.py`)를 고쳤다면 조각을 다시 뽑아요(파이썬 필요).

```bash
python tools/export_legacy.py
```

### 파이썬 (예전 빌드, 비교용)

```bash
python -m venv .venv
# macOS/Linux: source .venv/bin/activate    Windows: .venv\Scripts\activate
pip install -r requirements.txt
python tools/build.py all        # 또는 ui5 / backend
python -m http.server -d site 8000
```

## 새 주제 추가하기

1. `content/<주제>/doc.md`를 써요. 첫 줄은 `# 제목`, 셋째 줄은 날짜예요(이 3줄은 머리말로 바뀌어요). `##`가 부, `###`가 개념 페이지예요.
2. `content/<주제>/book.yaml`을 만들어요. `content/sap-backend/book.yaml`을 복사해서 제목·목차 그룹·부 아이콘만 바꾸면 돼요.
3. `content/site.json`의 `cards`에 한 줄 추가해요.
4. `npm run dev`로 확인해요. 로그에 `unmapped icons: [...]`가 나오면 그 개념의 아이콘을 `tools/icon_map2.py`의 `CONCEPT`에 추가하고 `python tools/export_legacy.py`를 실행해요.

교재끼리 링크는 `../sap-ui5/`처럼 사이트 안 상대 경로로 걸어요.

## 마크다운 전용 문법

| 쓰는 법 | 결과 |
|---|---|
| ` ```abap ` 바로 뒤에 ` ```abap-old ` | 옛/요즘 문법 탭 한 상자 (기본 옛 문법, 선택은 브라우저에 저장) |
| `<div class="syn-only syn-old">` / `syn-new` | 고른 문법일 때만 보이는 블록 |
| ` ```quiz ` (`Q:` 질문, `\| ` 코드 줄, `- ` 보기, 끝에 `✓` 정답, `> ` 오답 힌트, 빈 줄로 문제 구분) | 한 문제씩 푸는 문제 카드 |
| `<details class="more practice">` + `<summary>` | 접힌 문제 묶음 |
| ` ```syntax ` | 문법 틀 (한글은 채우는 자리) |
| `&#91;embedded content: 그림 이름 · 설명\]` (한 줄) | 그림 (`src/legacy/figures/index.json`의 이름) |
| `{? 설명 ?}` | "?" 도움말 |
| `[0205]`, `[0108~0202, Lev05]` | 수업 날짜 태그 |
| `- [ ] 할 일` | 체크 목록 |
| `` `Ctrl + S` `` | 키캡 |
| 본문의 "3부", "3부 배열 메서드" | 그 부·개념으로 가는 링크 (자동) |
| `**굵게**로` (닫는 `**` 뒤에 바로 한글) | 굵게 (CommonMark가 못 닫는 경우를 보정) |

## 교재 작성 규칙

- 토스 스타일 해요체, 초보자가 읽기 쉽게.
- 아직 안 배운 개념을 먼저 쓰지 않아요 (순서 지키기).
- SAP 고유 개념은 영어 그대로 (Domain, Data Element, Check Table, Structure, Internal Table 등).
- ABAP 코드는 옛 문법/요즘 문법을 같은 비중의 탭으로, 기본은 옛 문법. ` ```abap ` 바로 다음에 ` ```abap-old `를 붙이면 탭이 돼요. 두 문법이 같으면 탭 없이 한 블록이에요.
- 뻔한 설명은 넣지 않아요 (예: "SQL은 에스큐엘이라고 읽어요").
- 그림·애니메이션: 아이콘에 색 배경을 넣지 않고, 스크롤로 진행되는 애니메이션을 선호해요.
- 새 섹션(`### 제목`)을 만들면 `tools/icon_map2.py`의 `CONCEPT`에 제목의 `:` 앞부분을 키로 아이콘을 추가해요.
- 문제는 접힌 묶음(`<details class="more practice">`) 안의 ` ```quiz ` 블록에 써요.

## 라이선스

| 영역 | 라이선스 |
|---|---|
| 글 (`content/`) | [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/deed.ko) |
| 코드 (`src/`, `tools/`) | MIT |
| 글꼴 (`fonts/`, npm `pretendard`) | [Pretendard](https://github.com/orioncactus/pretendard), SIL OFL 1.1 |

자세한 내용은 [LICENSE](LICENSE)를 보세요.
