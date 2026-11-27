import re, html
import os
U = os.path.dirname(os.path.abspath(__file__)) + '/'
S = U + '../shared/'
OUT = U + '../../public/sap-ui5/index.html'
import subprocess, sys
subprocess.run([sys.executable, U + 'conv.py'], check=True)
src = open(U + 'base.html').read()
body = src[src.index('<body>') + len('<body>'):]

ICONS = {'ch-0': 't-book-x-E', 'ch-1': 't-box-x-E', 'ch-2': 't-sign-x-E', 'ch-3': 't-puzzle-x-E', 'ch-4': 't-pencil-blue-E',
         'ch-5': 't-note-x-E', 'ch-6': 't-window-blue-E', 'ch-7': 't-layers-blue-E', 'ch-8': 't-chain-x-E', 'ch-9': 't-table-blue-E',
         'ch-10': 't-dropdown-x-E', 'ch-11': 't-magnifier-x-E', 'ch-12': 't-check-green-E', 'ch-13': 't-db-blue-E', 'ch-14': 't-warn-x-E',
         'ch-15': 't-cabinet-x-E', 'appx-a': 't-magnifier-x-E', 'appx-b': 't-note-x-E', 'appx-c': 't-book-teal-E', 'appx-d': 't-book-x-E'}
GROUPS = [('시작하기', ['ch-0']), ('자바스크립트 기초', ['ch-1', 'ch-2', 'ch-3', 'ch-4', 'ch-5']),
          ('UI5 앱 만들기', ['ch-6', 'ch-7']), ('데이터 바인딩', ['ch-8', 'ch-9', 'ch-10', 'ch-11', 'ch-12']),
          ('종합과 문제 해결', ['ch-13', 'ch-14']), ('개발 도구', ['ch-15']),
          ('부록', ['appx-a', 'appx-b', 'appx-c', 'appx-d'])]

def strip(x): return html.unescape(re.sub('<[^>]+>', '', x)).strip()

# 1) 장 머리: 아이콘 + eyebrow + 제목
def head_fix(m):
    sid, inner = m.group(1), m.group(2)
    def rep(h):
        return ('<div class="part-head"><svg class="p-ic" viewBox="0 0 64 64" aria-hidden="true" focusable="false"><use href="#%s"/></svg>'
                '<h2><span class="eyebrow">%s</span><span class="h2t">%s</span></h2></div>') % (ICONS.get(sid, 't-book-x-E'), h.group(1), h.group(2))
    inner = re.sub(r'<p class="ch-num">(.*?)</p>\s*<h2>(.*?)</h2>', rep, inner, count=1, flags=re.S)
    return '<section class="chapter" id="%s">%s</section>' % (sid, inner)
body = re.sub(r'<section class="chapter" id="([\w-]+)">(.*?)</section>', head_fix, body, flags=re.S)

# 2) 코드 블록 → 어두운 패널
LANG = {'js': 'JavaScript', 'xml': 'XML', 'json': 'JSON', 'text': '구조'}
body = re.sub(r'<pre><code class="(js|xml|json|text)">(.*?)</code></pre>',
              lambda m: '<figure class="code" data-lang="%s"><figcaption><span>%s</span><button type="button" class="copy" aria-label="코드 복사">복사</button></figcaption><pre><code class="%s">%s</code></pre></figure>' % (m.group(1), LANG[m.group(1)], m.group(1), m.group(2)),
              body, flags=re.S)

# 3) 문법 틀 → 연한 패널, 한글 자리표시는 주황
def tpl(m):
    t = m.group(1)
    t = re.sub(r'([가-힣]+(?:[ ][가-힣]+)*)', r'<span class="ph">\1</span>', t)
    return '<figure class="code syntax"><figcaption><span>문법 틀</span></figcaption><pre><code>%s</code></pre></figure>' % t
body = re.sub(r'<p class="tpl">(.*?)</p>', tpl, body, flags=re.S)

# 4) 표: 휴대폰에서 카드로 쌓이게 data-cols, data-label
def table(m):
    t = m.group(0)
    heads = [strip(h) for h in re.findall(r'<th[^>]*>(.*?)</th>', t, re.S)]
    if not heads: return t
    t = t.replace('<table', '<table data-cols="%d"' % len(heads), 1)
    def row(r):
        i = [0]
        def cell(c):
            lab = heads[i[0]] if i[0] < len(heads) else ''
            i[0] += 1
            return '<td data-label="%s"' % html.escape(lab) if lab else '<td'
        return re.sub(r'<td(?=[\s>])', cell, r.group(0))
    return re.sub(r'<tr>.*?</tr>', row, t, flags=re.S)
body = re.sub(r'<table.*?</table>', table, body, flags=re.S)

# 5) 머리말
body = re.sub(r'<header class="masthead">.*?</header>', '''<header class="masthead" id="top">
  <p class="kicker">SAP CODE 부트캠프 수업 노트</p>
  <h1>SAPUI5 수업 정리 노트</h1>
  <p class="sub">자바스크립트 기초부터 데이터 바인딩까지, 키워드와 한 줄 설명으로 정리했어요.</p>
  <p class="meta"><span>0~5부 자바스크립트</span><span>6~13부 UI5</span><span>수업 프로젝트 0108~0220 · Lev05</span></p>
  <p class="intro-line">0~5부 예제는 브라우저 콘솔(F12)에 붙여넣으면 바로 실행돼요. "주의"는 꼭 지킬 점, "비유"는 낯선 개념을 익숙한 것에 빗댄 설명이에요. "더 알아보기"는 처음엔 안 봐도 돼요. 코드의 <code>XX</code>는 내 번호 자리예요.</p>
</header>''', body, count=1, flags=re.S)

# 6) 메뉴: 묶음별로 다시 만들기
secs = {}
for m in re.finditer(r'<section class="chapter" id="([\w-]+)">(.*?)</section>', body, re.S):
    sid, inner = m.group(1), m.group(2)
    num = strip(re.search(r'<span class="eyebrow">(.*?)</span>', inner).group(1))
    title = strip(re.search(r'<span class="h2t">(.*?)</span>', inner).group(1))
    kws = [(k.group(1), strip(k.group(2))) for k in re.finditer(r'<div class="kw" id="(kw-[\w]+-\d+)"><div class="kw-name[^"]*">(.*?)</div>', inner, re.S)]
    
    secs[sid] = (num, title, kws)
def short(n): return n.replace('부록 ', '').replace('부', '')
parts = []
for g, ids in GROUPS:
    parts.append('<p class="grp-head">%s</p><ol class="tree">' % g)
    for sid in ids:
        if sid not in secs: continue
        num, title, kws = secs[sid]
        if kws:
            ctrl = '<button type="button" class="chev" aria-expanded="false" aria-controls="sub-%s" aria-label="%s 개념 펼치기"></button>' % (sid, html.escape(title))
            sub = '<ul class="kws" id="sub-%s">%s</ul>' % (sid, ''.join('<li><a href="#%s">%s</a></li>' % (i, html.escape(n)) for i, n in kws))
        else:
            ctrl, sub = '<span class="gap"></span>', ''
        parts.append('<li><div class="ch-row"><a class="ch-link" href="#%s"><span>%s</span><span>%s</span></a>%s</div>%s</li>' % (sid, short(num), html.escape(title), ctrl, sub))
    parts.append('</ol>')
nav = '''<nav class="nav" id="nav" aria-label="개념 메뉴">
  <a class="nav-brand" href="#top">SAPUI5 수업 정리 노트</a>
  <div class="view-toggle vt-nav" role="group" aria-label="보기 방식"><button type="button" data-mode="core" aria-pressed="true">핵심만</button><button type="button" data-mode="full" aria-pressed="false">자세히</button></div>
  <div class="nav-head">
    <input id="nav-q" class="nav-search" type="search" placeholder="개념 검색" autocomplete="off" aria-label="개념 검색">
    <button type="button" class="nav-close" id="nav-close" aria-label="메뉴 닫기"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg></button>
  </div>
  <ul class="results" id="results" hidden></ul>
  <div id="tree">%s</div>
</nav>''' % ''.join(parts)
body = re.sub(r'<nav class="nav" id="nav".*?</nav>', lambda m: nav, body, count=1, flags=re.S)

# 7) 위 막대
body = re.sub(r'<header class="topbar">.*?</header>', '''<header class="topbar">
  <button type="button" id="menu-btn" aria-controls="nav" aria-expanded="false"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg><span>목차</span></button>
  <span class="tb-title" id="tb-cur" aria-live="polite"></span>
  <div class="view-toggle vt-top" role="group" aria-label="보기 방식"><button type="button" data-mode="core" aria-pressed="true">핵심만</button><button type="button" data-mode="full" aria-pressed="false">자세히</button></div>
  <button type="button" id="search-btn" aria-controls="nav" aria-label="검색"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="M20 20l-4-4"/></svg></button>
</header>''', body, count=1, flags=re.S)

# 8) 추가 스크립트: 복사 버튼, 위 막대에 지금 장 이름
extra = '''<script>
(function () {
  // JS·XML·JSON 색칠: 주석, 문자열, 키워드
  function escH(t) { return t.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;'); }
  var JSK = /^(const|let|var|function|return|if|else|for|of|in|async|await|new|this|true|false|null|undefined|break|continue|while|typeof)$/;
  function hiJs(src) {
    var out = '', i = 0, n = src.length;
    while (i < n) {
      var c = src[i], r = src.slice(i);
      if (c === '/' && src[i + 1] === '/') { var e = src.indexOf('\\n', i); if (e < 0) e = n; out += '<span class="tk-c">' + escH(src.slice(i, e)) + '</span>'; i = e; continue; }
      if (c === '"' || c === "'" || c === '`') {
        var j = i + 1; while (j < n && src[j] !== c && src[j] !== '\\n') { if (src[j] === '\\\\') j++; j++; }
        out += '<span class="tk-s">' + escH(src.slice(i, j + 1)) + '</span>'; i = j + 1; continue;
      }
      var m = /^[A-Za-z_$][\\w$]*/.exec(r);
      if (m) { out += JSK.test(m[0]) ? '<span class="tk-k">' + m[0] + '</span>' : escH(m[0]); i += m[0].length; continue; }
      out += escH(c); i++;
    }
    return out;
  }
  function hiXml(src) {
    var re = /(<!--[\\s\\S]*?-->)|("[^"\\n]*")|(<\\/?)([\\w:.]+)/g, out = '', last = 0, m;
    while ((m = re.exec(src))) {
      out += escH(src.slice(last, m.index));
      if (m[1]) out += '<span class="tk-c">' + escH(m[1]) + '</span>';
      else if (m[2]) out += '<span class="tk-s">' + escH(m[2]) + '</span>';
      else out += escH(m[3]) + '<span class="tk-k">' + m[4] + '</span>';
      last = re.lastIndex;
    }
    return out + escH(src.slice(last));
  }
  document.querySelectorAll('pre code.js, pre code.json').forEach(function (el) { el.innerHTML = hiJs(el.textContent); });
  document.querySelectorAll('pre code.xml').forEach(function (el) { el.innerHTML = hiXml(el.textContent); });
  document.querySelectorAll('.copy').forEach(function (b) {
    b.addEventListener('click', function () {
      var code = b.closest('figure').querySelector('pre').innerText;
      var done = function () { b.textContent = '복사됨'; b.dataset.state = 'done'; setTimeout(function () { b.textContent = '복사'; delete b.dataset.state; }, 1400); };
      try { navigator.clipboard.writeText(code).then(done, function () {}); } catch (e) {}
    });
  });
  var lb = document.createElement('div'); lb.className = 'lightbox'; lb.innerHTML = '<img alt="">'; document.body.appendChild(lb);
  document.querySelectorAll('.shot img').forEach(function (im) {
    im.addEventListener('click', function () { lb.querySelector('img').src = im.src; lb.querySelector('img').alt = im.alt; lb.classList.add('open'); });
  });
  lb.addEventListener('click', function () { lb.classList.remove('open'); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') lb.classList.remove('open'); });
  var vbtns = document.querySelectorAll('.view-toggle button');
  function setMode(m) {
    document.body.classList.toggle('core', m === 'core');
    vbtns.forEach(function (b) { b.setAttribute('aria-pressed', b.dataset.mode === m ? 'true' : 'false'); });
    try { localStorage.setItem('note-view', m); } catch (e) {}
  }
  vbtns.forEach(function (b) { b.addEventListener('click', function () { setMode(b.dataset.mode); }); });
  var saved = null;
  try { saved = localStorage.getItem('note-view'); } catch (e) {}
  setMode(saved || 'core');
  var cur = document.getElementById('tb-cur');
  if (cur && 'IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { var t = e.target.querySelector('.h2t'), n = e.target.querySelector('.eyebrow'); if (t) cur.textContent = (n ? n.textContent + ' · ' : '') + t.textContent; } });
    }, { rootMargin: '-20% 0px -75% 0px' });
    document.querySelectorAll('section.chapter').forEach(function (s) { io.observe(s); });
  }
})();
</script>
</body>'''
body = body.replace('</body>', extra, 1)

head = '''<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>SAPUI5 수업 정리 노트</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>
''' + open(S + 'fonts.css').read() + open(S + 'v4.css').read() + '''
</style>
</head>
<body>
''' + open(S + 'icons.svg').read() + '\n'
out = head + body
open(OUT, 'w').write(out)
print(len(out), 'bytes', out.count('class="code"'), 'code', out.count('code syntax'), 'tpl', out.count('data-cols'), 'tables', out.count('part-head'), 'heads')
