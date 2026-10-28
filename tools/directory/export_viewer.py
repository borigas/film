"""Inline a compact copy of schools.json into the game film viewer.

Lives in tools/directory/ of the film repo; pages are found relative to this file. Run from anywhere:
  python -I tools/directory/export_viewer.py            # beta/index.html (default)
  python -I tools/directory/export_viewer.py --main     # index.html (the main site)
  python -I tools/directory/export_viewer.py --both     # both
  python -I tools/directory/export_viewer.py PATH ...   # any page(s) with the markers

Only the fields the viewer's School search needs are exported, as short keys:
  n  name                 a  aliases (list)        s  state
  l  level (0 Union, 1 Union's opponents, 2 their opponents)
  h  [slug, status, lastGame] for Hudl, or 0     (slug lower-cased; status active|stale|none)
  y  [channelId, handle] for YouTube, or 0
  o  otherPlatform text ("" if none)
The data replaces whatever sits between /*SCHOOLS-START*/ and /*SCHOOLS-END*/ in the page,
so the page stays a single self-contained file that also works from file://.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'schools.json')
REPO = os.path.normpath(os.path.join(HERE, '..', '..'))   # tools/directory -> repo root
BETA_PAGE = os.path.join(REPO, 'beta', 'index.html')
MAIN_PAGE = os.path.join(REPO, 'index.html')
START, END = '/*SCHOOLS-START*/', '/*SCHOOLS-END*/'
SLUG_RE = re.compile(r'^[a-z0-9_-]{2,64}$')
CHANNEL_RE = re.compile(r'^UC[A-Za-z0-9_-]{22}$')
HANDLE_RE = re.compile(r'^@[A-Za-z0-9._-]{1,100}$')


def compact(s):
    hudl = s.get('hudl') or None
    h = 0
    if hudl and hudl.get('slug'):
        slug = str(hudl['slug']).strip().lower()
        if SLUG_RE.match(slug):
            status = hudl.get('status') if hudl.get('status') in ('active', 'stale', 'none') else 'none'
            h = [slug, status, str(hudl.get('lastGame') or '')[:10]]
    yt = s.get('youtube') or None
    y = 0
    if yt:
        cid = str(yt.get('channelId') or '')
        handle = str(yt.get('handle') or '')
        cid = cid if CHANNEL_RE.match(cid) else ''
        handle = handle if HANDLE_RE.match(handle) else ''
        if cid or handle:
            y = [cid, handle]
    aliases = []
    for a in s.get('aliases') or []:
        a = str(a).strip()
        if a and a != s['name'] and a not in aliases:
            aliases.append(a)
    return {
        'n': str(s['name']).strip(),
        'a': aliases,
        's': str(s.get('state') or ''),
        'l': int(s.get('level', 2)),
        'h': h,
        'y': y,
        'o': str(s.get('otherPlatform') or ''),
    }


def main():
    args = sys.argv[1:]
    named = {'--beta': [BETA_PAGE], '--main': [MAIN_PAGE], '--both': [BETA_PAGE, MAIN_PAGE]}
    pages = []
    for a in args or ['--beta']:
        pages += named.get(a, [a])
    for page in pages:
        export(os.path.abspath(page))


def export(page):
    with open(SRC, encoding='utf-8') as f:
        schools = json.load(f)
    rows = [compact(s) for s in schools]
    rows.sort(key=lambda r: (r['l'], r['n'].lower()))
    data = json.dumps(rows, ensure_ascii=True, separators=(',', ':'))
    # Safe inside an inline <script>: no "</script", "<!--" or "]]>" can appear.
    data = data.replace('<', '\\u003c').replace('>', '\\u003e')
    with open(page, 'rb') as f:
        html = f.read().decode('utf-8')
    i, j = html.find(START), html.find(END)
    if i < 0 or j < i or html.count(START) != 1 or html.count(END) != 1:
        sys.exit(f'Markers {START} ... {END} not found exactly once in {page}')
    out = html[:i + len(START)] + data + html[j:]
    if out != html:
        with open(page, 'wb') as f:
            f.write(out.encode('utf-8'))
    levels = {k: sum(1 for r in rows if r['l'] == k) for k in (0, 1, 2)}
    print(f'{len(rows)} schools ({levels}) -> {page} ({len(data)} bytes of data)'
          + ('' if out != html else ' [unchanged]'))


if __name__ == '__main__':
    main()
