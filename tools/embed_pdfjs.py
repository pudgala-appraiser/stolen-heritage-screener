#!/usr/bin/env python3
"""index.html에 넣어 둔 pdf.js를 새 판으로 갈아 끼운다.

    python tools/embed_pdfjs.py index.html pdf.min.mjs pdf.worker.min.mjs

두 파일은 pdfjs-dist 꾸러미의 legacy/build/ 에 있다(npm pack pdfjs-dist).
갈아 끼운 뒤에는 PDF 몇 개를 변환해 보고, 통제 시험 배지를 확인한다."""
import io, re, sys
idx, main, worker = sys.argv[1:4]
rd = lambda p: io.open(p, encoding='utf-8', newline='').read()
s = rd(idx)
for bid, path in (('pdfjs-main', main), ('pdfjs-worker', worker)):
    lib = rd(path)
    if re.search(r'</script|<!--', lib, re.I):
        sys.exit(path + ': HTML 안에 그대로 넣을 수 없는 글자열(</script 또는 <!--)이 있습니다. 넣지 않았습니다.')
    m = re.search(r'(<script type="text/plain" id="%s">)(.*?)(</script>)' % bid, s, re.S)
    if not m:
        sys.exit('index.html에서 %s 자리를 찾지 못했습니다. 넣지 않았습니다.' % bid)
    s = s[:m.start(2)] + lib + s[m.end(2):]
    print(bid, len(lib), '자')
io.open(idx, 'w', encoding='utf-8', newline='').write(s)
print('저장:', idx)
