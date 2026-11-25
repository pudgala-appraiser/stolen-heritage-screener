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
