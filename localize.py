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
URL_RE = re.compile(r'https?:(?:\\?/){2}(?:www\.)?crownplasticandpaper\.com((?:\\?/)[^\s"\'<>()\\&]*(?:\\/[^\s"\'<>()\\&]*)*)')
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


def elementor_chunks():
    """Elementor loads widget scripts on demand from webpack chunks that no page links to."""
    out = set()
    for runtime, base in (
        ('wp-content/plugins/elementor/assets/js/webpack.runtime.min.js', '/wp-content/plugins/elementor/assets/js/'),
        ('wp-content/plugins/elementor-pro/assets/js/webpack-pro.runtime.min.js', '/wp-content/plugins/elementor-pro/assets/js/'),
    ):
        f = os.path.join(ROOT, runtime)
        d = os.path.dirname(f)
        cands = [f] + ([os.path.join(d, n) for n in os.listdir(d) if n.startswith(os.path.basename(f) + '@')] if os.path.isdir(d) else [])
        cands = [c for c in cands if os.path.exists(c)]
        if not cands:
            continue
        s = open(cands[0], encoding='utf-8', errors='ignore').read()
        for name in set(re.findall(r'"([a-z0-9-]+\.[0-9a-f]{20}\.bundle\.min\.js)"', s)):
            out.add(base + name)
    return out


def main():
    seen = set()
    chunks = elementor_chunks()
    print('elementor chunks: %d' % len(chunks))
    for p in sorted(chunks):
        download(p, seen)
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

    # drop junk saved from HTML-escaped URLs (e.g. 'img.png&quot;,&quot;srcset...') by earlier runs
    import shutil
    for d, dirs, fs in os.walk(ROOT, topdown=True):
        for name in list(dirs):
            if '&quot;' in name or '&#' in name or '&amp;' in name:
                shutil.rmtree(os.path.join(d, name), ignore_errors=True)
                dirs.remove(name)
        for name in fs:
            if '&quot;' in name or '&#' in name or '&amp;' in name:
                os.remove(os.path.join(d, name))

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
