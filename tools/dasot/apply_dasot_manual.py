#!/usr/bin/env python3
"""사용 안내(manual.html)를 「다섯 벌」 청 벌로 바꾼다. 쓰기: python apply_dasot_manual.py manual.html"""
import io, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
p = sys.argv[1]
s = io.open(p, encoding='utf-8', newline='').read()
css = io.open(os.path.join(HERE, 'manual.css'), encoding='utf-8').read().strip('\n')
i = s.index('<style>'); j = s.index('</style>', i) + 8
s = s[:i] + '<style>\n' + css + '\n</style>' + s[j:]
if 'name="theme-color"' not in s:
    s = s.replace('<title>', '<meta name="theme-color" content="#8fcbf7">\n<title>', 1)
s = re.sub(r'\n?<div class="saekdong" aria-hidden="true"><i></i><i></i><i></i><i></i></div>', '', s)
s = re.sub(r'<strong style="color:var\(--[a-z]+\)">', '<strong>', s)          # 상태 표시의 박힌 색
NOTE = ('<p class="small">목록 대조와 이미지 대조에서는 <strong>화면 머리의 색</strong>도 결과를 따릅니다. '
        '경보후보가 하나라도 있으면 붉은색, 전문히트뿐이면 노란색으로 바뀌고, 통과뿐이면 바뀌지 않습니다. '
        '통과에 따로 색을 두지 않은 것은 통과가 안심의 표시가 아니기 때문입니다. 단건 검색은 색이 바뀌지 않습니다.</p>\n\n')
ANCHOR = '<p class="small">경보 기준은 조절할 수 있습니다.'
if NOTE not in s:
    assert ANCHOR in s, '결과 읽는 법 자리를 찾지 못함'
    s = s.replace(ANCHOR, NOTE + ANCHOR, 1)
s = s.replace('(예: <b>v3.6p</b>)', '(예: <b>v3.7p</b>)').replace('배포본 v3.6p', '배포본 v3.7p').replace('고침 2026-11-13', '고침 2026-11-25')
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('저장:', p, 'style= 남은 색:', len(re.findall(r'style="color', s)), 'v3.6 남음:', s.count('v3.6'))
