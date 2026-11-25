"""본명조 300·500을 검색기에 필요한 글자만 추려 woff2로 만든다.
쓰기: python tools/make_fonts.py index.html manual.html fonts
"""
import sys, json, re, os
from fontTools.ttLib import TTCollection
from fontTools import subset

SRC = '/usr/share/fonts/opentype/noto/NotoSerifCJK-%s.ttc'
index_html, manual_html, out = sys.argv[1:4]
os.makedirs(out, exist_ok=True)

s = open(index_html, encoding='utf-8').read()
def blk(i):
    a = s.find('<script id="%s"' % i); a = s.find('>', a) + 1
    return s[a:s.find('</script>', a)]
# 한자는 유물명에 나오는 것만 싣는다 — 원문 전체(851자)를 실으면 파일이 두 배가 된다
dbtext = ''.join(str(r.get('유물명', '')) for r in json.loads(blk('db-data')) + json.loads(blk('lost-data')))
han = {c for c in dbtext if 0x3400 <= ord(c) <= 0x9fff or 0xf900 <= ord(c) <= 0xfaff}
# KS X 1001 한글 2350자
hangul = set()
for hi in range(0xB0, 0xC9):
    for lo in range(0xA1, 0xFF):
        try: hangul.add(bytes([hi, lo]).decode('euc-kr'))
        except UnicodeDecodeError: pass
ascii_ = {chr(c) for c in range(0x20, 0x7f)}
punct = set('·‘’“”…–—―「」『』〈〉《》※→↗℃×㎝㎜')
ui = set(re.sub(r'<[^>]+>', '', open(manual_html, encoding='utf-8').read())) | set('還至本處査')
ui = {c for c in ui if ord(c) > 0x7f}
t500 = hangul | han | ascii_ | punct | ui
t300 = set('還至本處') | {' '}

def kr_index(path):
    for i, f in enumerate(TTCollection(path).fonts):
        if (f['name'].getDebugName(16) or f['name'].getDebugName(1)) == 'Noto Serif CJK KR': return i
    raise SystemExit('KR face not found in ' + path)

def build(weight_name, text, dest):
    path = SRC % weight_name
    opt = subset.Options(); opt.flavor = 'woff2'; opt.font_number = kr_index(path)
    opt.layout_features = ['vert', 'vrt2', 'kern', 'locl']; opt.name_IDs = [1, 2]; opt.notdef_outline = True
    opt.desubroutinize = True
    font = subset.load_font(path, opt)
    sub = subset.Subsetter(opt); sub.populate(text=''.join(sorted(text))); sub.subset(font)
    subset.save_font(font, dest, opt)
    print(dest, os.path.getsize(dest), 'bytes,', len(font.getBestCmap()), 'glyphs mapped')

build('Light', t300, os.path.join(out, 'dasot-serif-300.woff2'))
build('Medium', t500, os.path.join(out, 'dasot-serif-500.woff2'))
print('hangul', len(hangul), 'han', len(han))
