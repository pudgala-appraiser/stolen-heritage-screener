"""manual.html을 A4 책자 PDF(manual.pdf)로 만든다.
쓰기: python tools/make_manual_pdf.py manual.html manual.pdf
두 번 찍는다 — 한 번 찍어 각 장이 몇 쪽에 왔는지 읽고, 차례에 쪽 번호를 넣어 다시 찍는다.
쪽 번호는 PDF에만 들어가고 manual.html은 바꾸지 않는다. 크롬(또는 크로미움)과 playwright, pypdf가 필요하다.
"""
import asyncio, os, sys
from playwright.async_api import async_playwright
from pypdf import PdfReader

src, dst = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
CHROME = os.environ.get('CHROME', '/usr/bin/google-chrome')

def chapter_pages(pdf):
    r = PdfReader(pdf)
    texts = [(p.extract_text() or '') for p in r.pages]
    return texts, len(r.pages)

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=CHROME, args=['--no-sandbox'])
        pg = await b.new_page(); await pg.goto('file://' + src); await pg.evaluate('document.fonts.ready')
        opt = dict(format='A4', print_background=True, prefer_css_page_size=True)
        heads = await pg.evaluate("[...document.querySelectorAll('main h2[id]')].map(h=>[h.id,h.textContent.replace(/\\s+/g,'')])")
        tmp = dst + '.pass1'; await pg.pdf(path=tmp, **opt)
        texts, n = chapter_pages(tmp); os.remove(tmp)
        pages = {}
        for hid, title in heads:
            if hid == 's0': continue
            # 쪽마다 글의 첫 줄은 꼬리말(쪽 번호·문서 이름)이고, 장이 시작하는 쪽은 둘째 줄이 장 제목이다
            hit = [i + 1 for i, t in enumerate(texts) if i >= 2 and len(t.split('\n')) > 1 and t.split('\n')[1].replace(' ', '') == title]
            if len(hit) != 1: raise SystemExit('장 제목 쪽을 하나로 못 정함: %s %s' % (title, hit))
            pages[hid] = hit[0]
        await pg.evaluate("(m)=>document.querySelectorAll('.toc .pg[data-for]').forEach(e=>{e.textContent=m[e.dataset.for]||''})", pages)
        await pg.pdf(path=dst, **opt); await b.close()
    r = PdfReader(dst)
    if len(r.pages) != n: raise SystemExit('두 번째 찍을 때 쪽수가 달라짐: %d → %d' % (n, len(r.pages)))
    print(dst, len(r.pages), '쪽', os.path.getsize(dst) // 1024, 'KB', pages)

asyncio.run(main())
