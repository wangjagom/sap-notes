"""카드 원본(src/*.txt) → ABAP 노트와 같은 모양의 기본 HTML(index.html)"""
import re, html, glob, os

D = os.path.dirname(os.path.abspath(__file__))
ABAP_BASE = os.path.join(D, '..', 'abap', 'base.html')


def inline(t):
    """`code` → <code>, 나머지는 이스케이프"""
    out, parts = [], re.split(r'(``.+?``|`[^`]+`)', t)
    for p in parts:
        if p.startswith('``') and p.endswith('``') and len(p) > 4:
            out.append('<code>%s</code>' % html.escape(p[2:-2].strip()))
        elif p.startswith('`') and p.endswith('`') and len(p) > 1:
            out.append('<code>%s</code>' % html.escape(p[1:-1]))
        else:
            out.append(html.escape(p, quote=False))
    return ''.join(out)


def table(rows):
    head = [c.strip() for c in rows[0].split(' | ')]
    h = '<div class="table-wrap"><table>\n  <thead><tr>%s</tr></thead>\n  <tbody>\n' % ''.join('<th>%s</th>' % inline(c) for c in head)
    for r in rows[1:]:
        cells = [c.strip() for c in r.split(' | ')]
        h += '    <tr>%s</tr>\n' % ''.join('<td>%s</td>' % inline(c) for c in cells)
    return h + '  </tbody>\n</table></div>'


def parse(path):
    lines = open(path, encoding='utf-8').read().split('\n')
    i, items = 0, []
    while i < len(lines):
        ln = lines[i]
        if ln.startswith('@ch ') or ln.startswith('@ap '):
            sid, num, title, lead = [x.strip() for x in ln[4:].split(' | ', 3)]
            items.append(('ch', sid, num, title, lead, ln.startswith('@ap')))
        elif ln.startswith('@kw '):
            items.append(('kw', ln[4:].strip()))
        elif ln.startswith('c:') or ln.startswith('t:') or ln.startswith('tb:'):
            kind = ln.split(':')[0]
            lang = ln[2:].strip() if kind == 'c' else ''
            buf = []
            i += 1
            while i < len(lines) and lines[i] != '.':
                buf.append(lines[i]); i += 1
            items.append((kind, lang, buf))
        elif ln.startswith('m: '):
            items.append(('m', ln[3:].strip()))
        elif ln.strip() == '/m':
            items.append(('/m',))
        elif re.match(r'^[deslw]: ', ln):
            items.append((ln[0], ln[3:].strip()))
        elif ln.strip() and items and items[-1][0] == 'mtext':
            items[-1] = ('mtext', items[-1][1] + ' ' + ln.strip())
        elif ln.strip():
            items.append(('mtext', ln.strip()))
        i += 1
    return items


def render(items):
    out, kw_open, in_more, sec_open, list_open = [], False, False, False, False
    ch_idx = {}
    cur_sec, n = None, 0
    index_rows = []
    pending_desc = None

    def close_kw():
        nonlocal kw_open
        if kw_open:
            out.append('    </div></div>')
            kw_open = False

    def close_sec():
        nonlocal sec_open, list_open
        close_kw()
        if list_open:
            out.append('  </div>'); list_open = False
        if sec_open:
            out.append('</section>\n'); sec_open = False

    for it in items:
        k = it[0]
        if k == 'ch':
            close_sec()
            _, sid, num, title, lead, is_ap = it
            cur_sec, n = sid, 0
            out.append('<section class="chapter" id="%s">\n  <p class="ch-num">%s</p>\n  <h2>%s</h2>\n  <p class="lead">%s</p>' % (sid, num, inline(title), inline(lead)))
            sec_open = True
            if not is_ap:
                out.append('  <div class="kw-list">'); list_open = True
            continue
        if k == 'kw':
            close_kw()
            n += 1
            kid = 'kw-%s-%d' % (cur_sec.split('-')[1], n)
            name = it[1]
            ko = ' ko' if re.search('[가-힣]', name) else ''
            out.append('    <div class="kw" id="%s"><div class="kw-name%s">%s</div><div class="kw-body">' % (kid, ko, inline(name)))
            kw_open = True
            index_rows.append([kid, name, None, cur_sec])
            continue
        ind = '        ' if in_more else '      '
        if k == 'd':
            out.append(ind + '<p class="kw-desc">%s</p>' % inline(it[1]))
            if index_rows and index_rows[-1][2] is None:
                index_rows[-1][2] = it[1]
        elif k in 'eslw' and len(k) == 1:
            cls = {'e': 'easy', 's': 'kw-sub', 'l': 'like', 'w': 'warn'}[k]
            if in_more: cls = ''
            out.append(ind + ('<p class="%s">%s</p>' % (cls, inline(it[1])) if cls else '<p>%s</p>' % inline(it[1])))
        elif k == 'mtext':
            out.append(ind + '<p>%s</p>' % inline(it[1]))
        elif k == 't':
            out.append(ind + '<p class="tpl">%s</p>' % '\n'.join(html.escape(x) for x in it[2]))
        elif k == 'c':
            out.append(ind + '<pre><code class="%s">%s</code></pre>' % (it[1] or 'text', html.escape('\n'.join(it[2]), quote=False)))
        elif k == 'tb':
            out.append(table(it[2]))
        elif k == 'm':
            out.append('      <details class="more"><summary>%s</summary><div>' % inline(it[1]))
            in_more = True
        elif k == '/m':
            out.append('      </div></details>')
            in_more = False
    close_sec()
    return '\n'.join(out), index_rows


def sort_key(name):
    s = name.lstrip('=.$({[')
    return (0 if re.match('[A-Za-z]', s) else 1, s.lower())


def build():
    files = sorted(glob.glob(os.path.join(D, 'src', '*.txt')))
    items = []
    for f in files:
        items += parse(f)
    body, rows = render(items)
    # 부록 A: 키워드 찾아보기
    rows.sort(key=lambda r: sort_key(r[1]))
    tr = '\n'.join('      <tr><td><a href="#%s">%s</a></td><td>%s</td><td>%s</td></tr>' % (
        r[0], inline(r[1]), inline(r[2] or ''), r[3].split('-')[1]) for r in rows)
    appx_a = '''<section class="chapter" id="appx-a">
  <p class="ch-num">부록 A</p>
  <h2>키워드 찾아보기</h2>
  <p class="lead">본문의 키워드를 ABC순, 가나다순으로 모았어요. 이름을 누르면 그 카드로 가요.</p>
  <label for="kw-search" class="search-hint" style="display:block;margin:0">키워드나 뜻으로 찾기</label>
  <input id="kw-search" class="search" type="search" placeholder="예: bindElement, 바인딩, this" autocomplete="off">
  <p class="search-hint" id="kw-count" aria-live="polite"></p>
  <div class="table-wrap"><table class="wrap-first">
    <thead><tr><th>키워드</th><th>뜻</th><th>부</th></tr></thead>
    <tbody>
%s
    </tbody>
  </table></div>
</section>
''' % tr
    # 부록 B 앞에 부록 A를 넣어요
    i = body.index('<section class="chapter" id="appx-b">')
    body = body[:i] + appx_a + '\n' + body[i:]

    base = open(ABAP_BASE, encoding='utf-8').read()
    head = base[:base.index('<main>')]
    tail = base[base.index('<div id="tip"'):]
    head = head.replace('<title>SAP ABAP 수업 정리 노트</title>', '<title>SAPUI5 수업 정리 노트</title>')
    page = head + '<main>\n<header class="masthead"></header>\n\n' + body + '\n</main>\n</div>\n' + tail
    open(os.path.join(D, 'base.html'), 'w', encoding='utf-8').write(page)
    print(len(rows), 'keywords', body.count('<section'), 'sections')


if __name__ == '__main__':
    build()
