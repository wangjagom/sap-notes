"""첫 화면 → public/index.html (노트와 같은 글꼴·색)"""
import os, re, json, html

H = os.path.dirname(os.path.abspath(__file__)) + '/'
ROOT = H + '../../'
S = H + '../shared/'

NOTES = [
    {'slug': 'sap-ui5', 'icon': 't-window-blue-E', 'title': 'SAPUI5 수업 정리 노트',
     'desc': '자바스크립트 기초부터 데이터 바인딩까지. 콘솔에서 바로 따라 해 볼 수 있는 예제와 수업 프로젝트(0108~0220, Lev05) 흐름으로 정리했어요.',
     'tags': ['자바스크립트', 'XML View', '바인딩', '필터·정렬']},
    {'slug': 'abap', 'icon': 't-db-blue-E', 'title': 'SAP ABAP 수업 정리 노트',
     'desc': 'SAP GUI 첫 화면부터 ABAP 문법, ABAP Dictionary, View와 Search Help까지. 실제 SAP 화면 사진과 함께 배운 순서대로 정리했어요.',
     'tags': ['SE38', 'SE11', 'SELECT', '인터널 테이블'], 'updated': '11월 26일 수업까지 반영'},
]
TOOLS = [{'title': 'ERD 설계 도구', 'desc': '테이블 관계를 그려 보는 도구', 'url': 'https://wangjagom.github.io/erd-designer/'}]


def counts(slug):
    p = open(ROOT + 'public/%s/index.html' % slug, encoding='utf-8').read()
    kw = len(re.findall(r'<div class="kw" id="kw-', p))
    ch = len(re.findall(r'<section class="chapter" id="ch-', p))
    return ch, kw


def card(n):
    ch, kw = counts(n['slug'])
    unit = '부' if n['slug'] == 'sap-ui5' else '장'
    tags = ''.join('<li>%s</li>' % html.escape(t) for t in n['tags'])
    return '''<li><a class="note" href="%s/">
  <svg class="ic" viewBox="0 0 64 64" aria-hidden="true" focusable="false"><use href="#%s"/></svg>
  <div class="body">
    <b>%s</b>
    <p>%s</p>
    <ul class="tags">%s</ul>
    <span class="meta">%d%s · 키워드 %d개%s</span>
  </div>
  <span class="go" aria-hidden="true">→</span>
</a></li>''' % (n['slug'], n['icon'], html.escape(n['title']), html.escape(n['desc']), tags, ch, unit, kw, (' · ' + n['updated']) if n.get('updated') else '')


CSS = '''
:root{--bg:#fff;--ink:#030712;--ink-2:#374151;--muted:#6b7280;--line:rgb(3 7 18/.07);--line-strong:rgb(3 7 18/.14);
--wash:#f9fafb;--accent:#0ea5e9;--accent-ink:#0369a1;--accent-soft:rgb(14 165 233/.1);
--font-body:'Pretendard',-apple-system,BlinkMacSystemFont,'Apple SD Gothic Neo','Malgun Gothic',sans-serif;color-scheme:light}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink-2);font-family:var(--font-body);font-size:16.5px;line-height:1.8;
letter-spacing:-.012em;word-break:keep-all;overflow-wrap:anywhere;-webkit-font-smoothing:antialiased}
main{max-width:760px;margin:0 auto;padding:80px 24px 96px}
.kicker{margin:0 0 8px;font-size:14px;font-weight:600;color:var(--accent)}
h1{margin:0;color:var(--ink);font-size:40px;line-height:1.3;font-weight:700;letter-spacing:-.028em}
.intro{margin:14px 0 0;color:var(--ink-2)}
.how{margin:10px 0 0;font-size:14.5px;color:var(--muted);line-height:1.7}
h2{margin:56px 0 14px;font-size:14px;font-weight:600;color:var(--muted)}
ul.list{display:grid;gap:14px;padding:0;margin:0;list-style:none}
.note{display:grid;grid-template-columns:56px 1fr 20px;gap:18px;align-items:start;padding:24px;border:1px solid var(--line-strong);
border-radius:16px;color:inherit;text-decoration:none;transition:background .15s,border-color .15s}
.note:hover{background:var(--wash);border-color:var(--accent)}
.note:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.note .ic{width:56px;height:56px}
.note b{display:block;color:var(--ink);font-size:19px;font-weight:700;line-height:1.45}
.note p{margin:6px 0 12px;font-size:15px;line-height:1.7}
.tags{display:flex;flex-wrap:wrap;gap:6px;padding:0;margin:0 0 10px;list-style:none}
.tags li{padding:0 9px;border-radius:999px;background:var(--accent-soft);color:var(--accent-ink);font-size:12.5px;font-weight:600;line-height:1.8}
.meta{font-size:13.5px;color:var(--muted)}
.go{color:var(--muted);font-size:18px;align-self:center;transition:transform .15s,color .15s}
.note:hover .go{color:var(--accent);transform:translateX(3px)}
.tool{display:flex;justify-content:space-between;gap:12px;padding:16px 20px;border:1px solid var(--line-strong);border-radius:14px;
color:inherit;text-decoration:none}
.tool:hover{background:var(--wash);border-color:var(--accent)}
.tool b{color:var(--ink);font-weight:700}
.tool span{font-size:14.5px;color:var(--muted)}
footer{margin-top:64px;font-size:13px;color:var(--muted)}
@media(max-width:560px){main{padding:56px 20px 72px}h1{font-size:32px}
.note{grid-template-columns:44px 1fr;gap:14px;padding:20px}.note .ic{width:44px;height:44px}.go{display:none}
.tool{flex-direction:column;gap:0}}
'''


def build():
    cards = '\n'.join(card(n) for n in NOTES)
    tools = '\n'.join('<li><a class="tool" href="%s" target="_blank" rel="noopener"><b>%s ↗</b><span>%s</span></a></li>' % (
        t['url'], html.escape(t['title']), html.escape(t['desc'])) for t in TOOLS)
    page = '''<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>SAP 수업 노트</title>
<meta name="description" content="SAP CODE 부트캠프에서 배운 SAPUI5와 ABAP을 키워드와 한 줄 설명으로 정리한 노트">
<style>%s%s</style>
</head>
<body>
%s
<main>
  <p class="kicker">SAP CODE 부트캠프</p>
  <h1>SAP 수업 노트</h1>
  <p class="intro">수업에서 배운 SAPUI5와 ABAP을 배운 순서대로, 키워드와 한 줄 설명으로 정리했어요.</p>
  <p class="how">노트마다 "핵심만"으로 훑어보고, 이해가 안 되는 곳만 "자세히"로 펼쳐 보면 돼요. 목차의 검색으로 키워드를 바로 찾을 수 있어요.</p>
  <h2>노트</h2>
  <ul class="list">
%s
  </ul>
  <h2>도구</h2>
  <ul class="list">
%s
  </ul>
  <footer>글은 CC BY-NC-SA 4.0 · 코드는 MIT · 글꼴 Pretendard(OFL)</footer>
</main>
</body>
</html>
''' % (open(S + 'fonts.css', encoding='utf-8').read(), CSS, open(S + 'icons.svg', encoding='utf-8').read(), cards, tools)
    open(ROOT + 'public/index.html', 'w', encoding='utf-8').write(page)
    print('home ok', [counts(n['slug']) for n in NOTES])


if __name__ == '__main__':
    build()
