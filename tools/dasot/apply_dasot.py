#!/usr/bin/env python3
"""도난국가유산 검색기 — 화면을 「다섯 벌」로 바꾸는 적용 스크립트 (v3.7)

쓰기:
    python apply_dasot.py <검색기.html> [--style style.css] [--out 새파일.html] [--no-bump]

· 공개판(index.html)과 내부 정본 양쪽에 같은 방법으로 쓴다.
· 표시 층만 바꾼다. 매칭 엔진·내장 DB·사진 지문은 건드리지 않는다.
· 여러 번 돌려도 결과가 같다. 바꿀 자리를 찾지 못하면 아무것도 쓰지 않고 멈춘다.
· --no-bump: 판 표기(engine)와 계보(lineage)를 건드리지 않는다.
"""
import argparse, io, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
LINEAGE = ' → 20261125(v3.7p 화면을 「다섯 벌」 디자인으로 — 환지본처 흑 벌·작업 탭 청 벌·목록 대조와 이미지 대조는 결과에 따라 적/황 벌. 표시 전용, 엔진·DB 무변경)'

HOME_OLD = '<h2>환지본처 <span class="small" style="font-weight:400">還至本處 · 제자리로 돌아가기까지</span></h2>'
HOME_NEW = '<h2 class="spine"><span class="hj">還至本處</span><span class="rd">환지본처　제자리로 돌아가기까지</span></h2>'

HELP_ANCHOR = '    <h3>한계</h3>'
HELP_NEW = ('    <p>목록 대조와 이미지 대조에서는 <b>화면 머리의 색</b>도 결과를 따릅니다 — 경보후보(이미지 대조는 동일 사진 유력)가 하나라도 있으면 붉은색, '
            '전문히트(유사 사진 가능)뿐이면 노란색이고, 통과뿐이면 바뀌지 않습니다. 통과에 따로 색을 두지 않은 것은 통과가 안심의 표시가 아니기 때문입니다. '
            '단건 검색은 판정을 내지 않으므로 색이 바뀌지 않습니다.</p>\n')

PUBLISH_ANCHOR = "doc.querySelectorAll('nav button').forEach(x=>x.classList.toggle('on',x.dataset.tab==='home'));"
PUBLISH_ADD = ("\n  doc.querySelector('body').setAttribute('data-theme','heuk');  /* 발행본은 환지본처(흑 벌)로 열린다 */"
               "\n  {const tc=doc.querySelector('meta[name=\"theme-color\"]');if(tc)tc.setAttribute('content','#000000');}")

THEME_JS = r'''<script id="dasot-theme">
/* ===== 벌 전환 (v3.7 · 표시 전용 — 점수·판정 계산 무관여) =====
   화면에 이미 그려진 판정 표시를 읽어 <body data-theme>만 바꾼다.
   환지본처 = 흑. 목록 대조·이미지 대조 = 경보후보가 있으면 적, 전문히트뿐이면 황, 그 밖에는 청.
   단건 검색은 엔진이 판정을 내지 않으므로 청 그대로 둔다. */
(function(){
  var SEL={batch:['batchOut','[data-st="alert"]','[data-st="hit"]'],
           image:['hashOut','.cand.alert','.cand.hit']};
  function themeOf(tab){
    if(tab==='home')return 'heuk';
    var s=SEL[tab], o=s&&document.getElementById(s[0]);
    if(o){ if(o.querySelector(s[1]))return 'jeok'; if(o.querySelector(s[2]))return 'hwang'; }
    return 'cheong';
  }
  function apply(){
    var on=document.querySelector('nav button.on'), t=themeOf(on?on.dataset.tab:'home');
    if(document.body.getAttribute('data-theme')!==t)document.body.setAttribute('data-theme',t);
    var m=document.querySelector('meta[name="theme-color"]');
    var c=getComputedStyle(document.body).getPropertyValue('--plane').trim();
    if(m&&c&&m.getAttribute('content')!==c)m.setAttribute('content',c);
  }
  var mo=new MutationObserver(apply);
  var nav=document.querySelector('nav');
  if(nav)mo.observe(nav,{attributes:true,attributeFilter:['class'],subtree:true});
  ['batchOut','hashOut'].forEach(function(id){var e=document.getElementById(id);if(e)mo.observe(e,{childList:true});});
  apply();
})();
</script>
'''


class Stop(Exception):
    pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('html')
    ap.add_argument('--style', default=os.path.join(HERE, 'style.css'))
    ap.add_argument('--out')
    ap.add_argument('--no-bump', action='store_true')
    a = ap.parse_args()

    s = io.open(a.html, encoding='utf-8', newline='').read()
    css = io.open(a.style, encoding='utf-8').read().strip('\n')
    log = []

    def step(name, done, todo, fn):
        """done: 이미 적용됐는지 / todo: 적용할 자리가 있는지 / fn: 적용"""
        nonlocal s
        if done(s):
            log.append(('그대로', name)); return
        if not todo(s):
            raise Stop(name)
        s = fn(s); log.append(('적용', name))

    try:
        # 1. 스타일 블록 (문서의 첫 <style>)
        new_style = '<style>\n' + css + '\n</style>'
        def put_style(t):
            i = t.index('<style>'); j = t.index('</style>', i) + len('</style>')
            return t[:i] + new_style + t[j:]
        step('스타일 블록', lambda t: new_style in t,
             lambda t: '<style>' in t and '</style>' in t, put_style)

        # 2. 주소창 색·아이콘 — 여는 화면이 흑 벌이므로 먹 바탕에 밝은 글자
        step('theme-color', lambda t: '<meta name="theme-color" content="#1F4E79">' not in t,
             lambda t: '<meta name="theme-color" content="#1F4E79">' in t,
             lambda t: t.replace('<meta name="theme-color" content="#1F4E79">', '<meta name="theme-color" content="#000000">'))
        def icons(t):
            head_end = t.index('</head>')
            h = t[:head_end].replace("fill='%231F4E79'", "fill='%23000000'").replace("fill='%23D9A43B'", "fill='%23ece9e2'").replace("font-weight='600'", "font-weight='500'")
            return h + t[head_end:]
        step('아이콘', lambda t: "fill='%231F4E79'" not in t[:t.index('</head>')] and "fill='%23000000'" in t[:t.index('</head>')],
             lambda t: "fill='%231F4E79'" in t[:t.index('</head>')], icons)

        # 3. body에 여는 벌
        body_re = re.compile(r'(</head>\s*)<body>')    # SheetJS 안의 '<body>' 문자열과 섞이지 않게 </head> 뒤의 것만
        step('body data-theme', lambda t: re.search(r'</head>\s*<body data-theme="[a-z]+">', t) is not None,
             lambda t: bool(body_re.search(t)), lambda t: body_re.sub(r'\1<body data-theme="heuk">', t, count=1))

        # 4. 색동 띠 두 곳, 유실 배지의 박힌 색
        sd = re.compile(r'\n?[ \t]*<div class="saekdong[^"]*" aria-hidden="true"><i></i><i></i><i></i><i></i></div>')
        step('색동 띠 삭제', lambda t: not sd.search(t), lambda t: bool(sd.search(t)), lambda t: sd.sub('', t))
        lb_old = 'id="lostbadge" style="display:none;background:#1f6f78;color:#fff"'
        step('유실 배지 색', lambda t: lb_old not in t,
             lambda t: lb_old in t, lambda t: t.replace(lb_old, 'id="lostbadge" style="display:none"'))

        # 5. 환지본처 — 넉 자를 세로로 세우는 마크업
        home_card_old = '<section class="tab on" id="tab-home">\n<div class="card">'
        home_card_any = re.compile(r'(<section class="tab[^"]*" id="tab-home">\s*<div class="card)(">)')
        step('환지본처 카드', lambda t: re.search(r'id="tab-home">\s*<div class="card home">', t) is not None,
             lambda t: bool(home_card_any.search(t)), lambda t: home_card_any.sub(r'\1 home\2', t, count=1))
        step('환지본처 제목', lambda t: HOME_NEW in t, lambda t: HOME_OLD in t, lambda t: t.replace(HOME_OLD, HOME_NEW))

        # 5-2. 도움말 — 화면 색이 무엇을 뜻하는지 한 문단
        step('도움말 화면 색 문단', lambda t: HELP_NEW in t, lambda t: HELP_ANCHOR in t,
             lambda t: t.replace(HELP_ANCHOR, HELP_NEW + HELP_ANCHOR, 1))

        # 6. 스크립트 속 박힌 색 한 곳, 발행본의 여는 벌
        ok_old = '<b style="color:var(--ok)">'
        step('등록분 표시 색', lambda t: ok_old not in t, lambda t: ok_old in t, lambda t: t.replace(ok_old, '<b>'))
        step('발행본 여는 벌', lambda t: PUBLISH_ANCHOR + PUBLISH_ADD in t, lambda t: PUBLISH_ANCHOR in t,
             lambda t: t.replace(PUBLISH_ANCHOR, PUBLISH_ANCHOR + PUBLISH_ADD, 1))

        # 7. 벌 전환 스크립트 (문서 끝)
        def put_theme(t):
            t = re.sub(r'<script id="dasot-theme">.*?</script>\n?', '', t, flags=re.S)   # 옛 판이 있으면 갈아 끼운다
            i = t.rindex('</body>')
            return t[:i].rstrip('\n') + '\n' + THEME_JS + t[i:]
        step('벌 전환 스크립트', lambda t: THEME_JS in t, lambda t: '</body>' in t, put_theme)

        # 8. 판 표기와 계보
        if not a.no_bump:
            mm = re.search(r'(<script id="db-meta" type="application/json">)(.*?)(</script>)', s, re.S)
            if not mm:
                raise Stop('db-meta 블록')
            meta = json.loads(mm.group(2))
            if json.dumps(meta, ensure_ascii=False, separators=(',', ':')) != mm.group(2):
                raise Stop('db-meta 다시 쓰기(형식이 예상과 다름)')
            eng = str(meta.get('engine', ''))
            if eng.startswith('3.7'):
                log.append(('그대로', '판 표기 ' + eng))
            elif eng.startswith('3.6'):
                meta['engine'] = '3.7' + eng[3:]
                meta['lineage'] = (meta.get('lineage') or meta.get('version', '')) + LINEAGE.replace('v3.7p', 'v' + meta['engine'])
                s = s[:mm.start(2)] + json.dumps(meta, ensure_ascii=False, separators=(',', ':')) + s[mm.end(2):]
                log.append(('적용', '판 표기 ' + eng + ' → ' + meta['engine']))
            else:
                raise Stop('판 표기(engine=%r — 3.6 계열이 아님. --no-bump로 다시 돌리십시오)' % eng)
    except Stop as e:
        for k, n in log:
            print('  [%s] %s' % (k, n))
        print('  [멈춤] 바꿀 자리를 찾지 못했습니다: %s\n아무것도 쓰지 않았습니다.' % e)
        return 1

    for k, n in log:
        print('  [%s] %s' % (k, n))
    out = a.out or a.html
    io.open(out, 'w', encoding='utf-8', newline='').write(s)
    print('저장: %s (%d바이트)' % (out, len(s.encode('utf-8'))))
    return 0


if __name__ == '__main__':
    sys.exit(main())
