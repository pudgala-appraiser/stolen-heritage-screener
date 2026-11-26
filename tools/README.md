# tools

검색기 실행에는 필요 없는 보조 도구입니다.

검색기는 공개 단일본입니다. 화면 스타일은 `index.html`의 스타일 블록이 정본이고(색·글자 규칙은 그 머리 주석에 있습니다),
사용 안내는 `manual.html`의 스타일 블록이 정본입니다. 화면을 고칠 때는 그 파일을 직접 고칩니다.

## make_fonts.py — 제목용 글꼴 다시 만들기

제목용 본명조 300·500을 필요한 글자(한글 2350자 + 유물명에 나오는 한자)만 추려 `fonts/`에 만듭니다.
새로 등록한 유물명의 한자가 기기 명조로 보이면 다시 만듭니다.
Noto Serif CJK(Light·Medium)와 fonttools·brotli가 필요하며, 글꼴 경로는 스크립트의 `SRC`에 있습니다.

```
python tools/make_fonts.py index.html manual.html fonts
```

## make_manual_pdf.py — 사용 안내 PDF 다시 만들기

`manual.html` 하나가 사용 안내의 원본입니다. 화면으로 읽는 문서이고, 같은 파일을 A4로 찍은 것이 `manual.pdf`입니다.
안내문을 고쳤으면 PDF도 다시 만듭니다. 두 번 찍어 차례에 쪽 번호를 넣습니다(쪽 번호는 PDF에만 들어갑니다).
크롬(또는 크로미움)·playwright·pypdf와, 본문용 Noto Sans CJK KR이 깔려 있어야 합니다.

```
python tools/make_fonts.py index.html manual.html fonts     # 제목에 새 글자가 들어갔으면 먼저
python tools/make_manual_pdf.py manual.html manual.pdf
```

만든 뒤에는 쪽마다 넘겨 보며 그림과 표가 쪽 사이에서 잘리지 않았는지 확인하십시오.
그림의 인쇄 폭은 `<figure style="--pw:70%">`처럼 그림마다 적어 두었습니다 — 쪽이 넘치면 이 값을 줄입니다.

화면 그림(`manual-img/`)은 검색기를 폭 920px, 배율 2로 찍어 번호 표시를 얹은 것입니다. **JPEG로 둡니다** — PNG·WebP는 크롬이 PDF에 풀어서 실어 파일이 세 배가 됩니다.
그림에는 판 번호가 찍혀 있으므로, 화면이 달라지는 판을 낼 때는 그림도 다시 찍습니다.

판을 올릴 때 사용 안내에서 함께 고칠 곳: 표지와 꼬리말의 판 번호(`manual.html`에서 `v4.2`를 찾으면 됩니다), 맨 끝 문서 정보, 그리고 `index.html` 도움말 탭의 PDF 파일 이름.

## embed_pdfjs.py — PDF 판독 라이브러리 갈아 끼우기

PDF 목록 변환 도구는 [pdf.js](https://mozilla.github.io/pdf.js/)(Mozilla, Apache License 2.0)를 `index.html` 안에 넣어 씁니다.
지금 든 것은 pdfjs-dist 6.5.438의 legacy 빌드입니다. 보안 수정이 나오면 새 판으로 갈아 끼웁니다.

```
npm pack pdfjs-dist            # 꾸러미를 받아 풀면 legacy/build/ 에 두 파일이 있습니다
python tools/embed_pdfjs.py index.html pdf.min.mjs pdf.worker.min.mjs
```

갈아 끼운 뒤에는 PDF 몇 개를 변환해 보고 헤더의 통제 시험 배지를 확인하십시오.
표를 읽는 규칙(`pdfListExtract`)과 화면은 `index.html`의 `pdf-convert` 스크립트가 정본입니다.
