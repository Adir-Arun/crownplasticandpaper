#!/usr/bin/env python3
"""Make the static copy self-contained.

wget misses files that WordPress/WP Rocket only reference in data-* attributes
(lazy-loaded images, delayed scripts) or inside inline JSON. This script finds every
remaining absolute URL to the live site in site/, downloads the files that are
assets, and rewrites all absolute links to root-relative ones.
"""
import os
import re
import sys
import urllib.parse
import urllib.request

ROOT = 'site'
HOSTS = ('www.crownplasticandpaper.com', 'crownplasticandpaper.com')
TEXT_EXT = ('.html', '.htm', '.css', '.js', '.json', '.xml', '.svg', '.txt')
ASSET_HINT = re.compile(r'^/(wp-content|wp-includes)/')
# plain and JSON-escaped (https:\/\/www.crownplasticandpaper.com\/...) forms
URL_RE = re.compile(r'https?:(?:\\?/){2}(?:www\.)?crownplasticandpaper\.com((?:\\?/)[^\s"\'<>()\\]*(?:\\/[^\s"\'<>()\\]*)*)')
UA = {'User-Agent': 'Mozilla/5.0 (compatible; site-copy)'}


def text_files():
    for d, _, fs in os.walk(ROOT):
        for f in fs:
            if f.lower().endswith(TEXT_EXT):
                yield os.path.join(d, f)


def local_path(url_path):
    p = urllib.parse.unquote(url_path.split('?')[0].split('#')[0])
    return os.path.join(ROOT, p.lstrip('/'))


def download(url_path, seen):
    clean = url_path.split('#')[0]
    if clean in seen:
        return
    seen.add(clean)
    dest = local_path(clean)
    if os.path.exists(dest) and not os.path.isdir(dest):
        return
    url = 'https://www.crownplasticandpaper.com' + clean
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=30) as r:
            data = r.read()
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, 'wb') as fh:
            fh.write(data)
        print('  + ' + clean.split('?')[0])
    except Exception as e:  # keep going; a missing asset should not fail the build
        print('  ! ' + clean + ' (' + str(e) + ')')


def main():
    seen = set()
    for rnd in range(3):
        found = set()
        for f in text_files():
            try:
                s = open(f, encoding='utf-8', errors='ignore').read()
            except Exception:
                continue
            for m in URL_RE.finditer(s):
                path = m.group(1).replace('\\/', '/')
                if ASSET_HINT.match(path):
                    found.add(path)
        new = [p for p in found if p.split('#')[0] not in seen]
        print('round %d: %d new asset urls' % (rnd + 1, len(new)))
        if not new:
            break
        for p in sorted(new):
            download(p, seen)

    # rewrite absolute links to root-relative (both plain and JSON-escaped forms)
    changed = 0
    for f in text_files():
        s = open(f, encoding='utf-8', errors='ignore').read()
        t = s
        for h in HOSTS:
            t = t.replace('https://' + h + '/', '/').replace('http://' + h + '/', '/')
            t = t.replace('https:\\/\\/' + h + '\\/', '\\/').replace('http:\\/\\/' + h + '\\/', '\\/')
            t = t.replace('"https://' + h + '"', '"/"')
        # query-string asset names saved by wget with --restrict-file-names=windows ("file.css@ver=1")
        if t != s:
            open(f, 'w', encoding='utf-8').write(t)
            changed += 1
    print('rewrote links in %d files' % changed)

    # wget saves "style.css?ver=1" as "style.css@ver=1"; make the plain name exist too
    for d, _, fs in os.walk(ROOT):
        for name in fs:
            if '@' in name:
                base = name.split('@')[0]
                target = os.path.join(d, base)
                if base and not os.path.exists(target):
                    try:
                        os.link(os.path.join(d, name), target)
                    except Exception:
                        pass
    return 0


if __name__ == '__main__':
    sys.exit(main())
