#!/usr/bin/env python3
"""Apply the site upgrades to the static snapshot in site/ (in place).

Runs on every Vercel build. The snapshot itself stays a faithful copy of the
WordPress site; every change we make lives here, so a fresh snapshot can be
taken at any time and the same upgrades are applied on top of it.

Usage: python3 upgrade/apply.py [site_dir]
"""
import html
import json
import os
import re
import shutil
import sys

SITE = sys.argv[1] if len(sys.argv) > 1 else 'site'
HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, 'assets')
MARK = 'data-cpp-upgrade'
ORIGIN = 'https://www.crownplasticandpaper.com'

PHONE_TEXT = '(844) 900-8801'
PHONE_TEL = 'tel:+18449008801'
EMAIL = 'info@crownplasticandpaper.com'
CATALOG = 'https://heyzine.com/flip-book/0ee04dad9c.html#page/13'
YEAR = '2026'

# Where the placeholder links (originally "#") should point, by link text.
PLACEHOLDER_TARGETS = {
    'about': 'about-us/',
    'aluminum products': 'products/product_cat-aluminum-products/',
    'food service supplies': 'products/product_cat-food-service-supplies/',
    'gloves': 'products/product_cat-gloves/',
    'miscellaneous': 'products/product_cat-miscellaneous/',
    'paper napkins': 'products/product_cat-paper-napkins/',
    'paper supply': 'products/product_cat-paper-supply/',
    'toilet tissue': 'products/product_cat-toilet-tissue/',
    'bulk': 'get-your-quote/',
}
PLACEHOLDER_RE = re.compile(
    r'href="((?:\.\./)*)products/product_cat-aluminum-products-or-[^"]*?\{\{data\.gallery_thumbnail_src\}\}\.html#?"')
SEARCH_ACTION_RE = re.compile(
    r'action="((?:\.\./)*)products/product_cat-aluminum-products-or-[^"]*?\{\{data\.gallery_thumbnail_src\}\}\.html"')


def strip_tags(s):
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', s)).strip()


def rel_prefix(path):
    depth = os.path.relpath(path, SITE).count(os.sep)
    return '../' * depth


def page_url(path):
    rel = os.path.relpath(path, SITE).replace(os.sep, '/')
    if rel == 'index.html':
        return '/'
    if rel.endswith('/index.html'):
        return '/' + rel[:-len('index.html')]
    return '/' + rel


def fix_placeholders(s):
    def repl(m):
        prefix = m.group(1)
        tail = s[m.end():m.end() + 900]
        text = strip_tags(tail.split('</a>', 1)[0].split('>', 1)[-1]).lower()
        if 'catalog' in text:
            return 'href="%s" target="_blank" rel="noopener"' % CATALOG
        for key, target in PLACEHOLDER_TARGETS.items():
            if text.startswith(key):
                return 'href="%s%s"' % (prefix, target)
        return 'href="#"'
    s = PLACEHOLDER_RE.sub(repl, s)
    s = SEARCH_ACTION_RE.sub(lambda m: 'action="%sproducts/"' % m.group(1), s)
    return s


def nice_alt(m):
    attr, val = m.group(1), m.group(2)
    v = val
    if re.match(r'^(icn|element|ic|icon)[_-]', v, re.I):
        return '%s=""' % attr
    if re.match(r'^img[_-]', v, re.I):
        v = re.sub(r'^img[_-]+', '', v, flags=re.I)
        v = re.sub(r'^(crown|arus?|aru|home|blog|post|our[_ -]customers)[_-]+', '', v, flags=re.I)
        v = re.sub(r'^(crown|arus?|aru|home|blog|post|our[_ -]customers)[_-]+', '', v, flags=re.I)
        v = re.sub(r'[_-]+', ' ', v)
        v = re.sub(r'\b(Raw|new|copy space|\d+)$', '', v, flags=re.I).strip()
        return '%s="%s"' % (attr, html.escape(v[:1].upper() + v[1:], quote=True))
    return m.group(0)


def webp_swap(s, page_dir):
    """Point img/srcset/background URLs at the .webp sibling when one exists."""
    def swap_url(u):
        base = u.split('?')[0].split('#')[0]
        if not re.search(r'\.(png|jpe?g)$', base, re.I):
            return u
        if base.startswith('/'):
            fs = os.path.join(SITE, base.lstrip('/'))
        elif base.startswith('http'):
            return u
        else:
            fs = os.path.normpath(os.path.join(page_dir, base))
        return u.replace(base, base + '.webp') if os.path.exists(fs + '.webp') else u

    def attr_repl(m):
        name, val = m.group(1), m.group(2)
        if 'srcset' in name:
            parts = []
            for item in val.split(','):
                bits = item.strip().split(' ')
                if bits and bits[0]:
                    bits[0] = swap_url(bits[0])
                parts.append(' '.join(bits))
            return '%s="%s"' % (name, ', '.join(parts))
        return '%s="%s"' % (name, swap_url(val))

    s = re.sub(r'\b((?:data-lazy-)?src(?:set)?|data-src|data-srcset)="([^"]+)"', attr_repl, s)
    s = re.sub(r'url\(\s*([\'"]?)([^)\'"]+\.(?:png|jpe?g))\1\s*\)',
               lambda m: 'url(%s%s%s)' % (m.group(1), swap_url(m.group(2)), m.group(1)), s)
    return s


def upgrade_html(path, snippets, search_items):
    s = open(path, encoding='utf-8', errors='ignore').read()
    if MARK in s:
        return False
    prefix = rel_prefix(path)
    url = page_url(path)

    # --- content consistency -------------------------------------------------
    s = s.replace('(844) 900-0084', PHONE_TEXT)
    s = re.sub(r'tel:[^"]*900(?:%20|[-. ])?0084', PHONE_TEL, s)
    s = re.sub(r'tel:\(844\)%20900-8801|tel:844%20900%208801', PHONE_TEL, s)
    s = re.sub(r'Sales@www\.crownplasticandpaper\.com', EMAIL, s, flags=re.I)
    s = s.replace('@www.crownplasticandpaper.com', '@crownplasticandpaper.com')
    s = s.replace('Copyright © 2025 AR Unlimited Supply', 'Copyright © %s Crown Plastic &#038; Paper' % YEAR)
    s = re.sub(r'Copyright © 2025 Crown', 'Copyright © %s Crown' % YEAR, s)
    s = s.replace('View 2025 Catalog', 'View 2026 Catalog')
    s = re.sub(r'<li[^>]*>\s*<a[^>]*page_id=66[^>]*>\s*Home old\s*</a>\s*</li>', '', s)

    # --- broken links ----------------------------------------------------------
    s = fix_placeholders(s)
    s = re.sub(r'href="([^"#?:]*?)index\.html(#[^"]*)?"',
               lambda m: 'href="%s%s"' % (m.group(1) or './', m.group(2) or ''), s)
    canonical = ORIGIN + url
    s = re.sub(r'<link rel="canonical" href="[^"]*"', '<link rel="canonical" href="%s"' % canonical, s)
    s = re.sub(r'<meta property="og:url" content="[^"]*"', '<meta property="og:url" content="%s"' % canonical, s)
    s = re.sub(r'(<meta (?:property|name)="(?:og:image|twitter:image)(?::secure_url)?" content=")/', r'\1' + ORIGIN + '/', s)

    # --- accessibility ---------------------------------------------------------
    s = re.sub(r'\b(alt)="([^"]*)"', nice_alt, s)
    # "Skip to content" had no target: mark the page body as the main landmark.
    if 'id="content"' not in s:
        s = re.sub(r'<div data-elementor-type="(?!header|footer|popup)([^"]+)"',
                   r'<div id="content" role="main" tabindex="-1" data-elementor-type="\1"', s, count=1)
    # Slider pages repeat <h1> per slide; keep the first, the rest become <h2>
    # (sizes come from Elementor classes, so they look the same).
    h1s = [m.start() for m in re.finditer(r'<h1[\s>]', s)]
    if len(h1s) > 1:
        out, last = [], 0
        for n, pos in enumerate(h1s):
            if n == 0:
                continue
            end = s.find('</h1>', pos)
            if end < 0:
                continue
            out.append(s[last:pos]); out.append('<h2' + s[pos + 3:end] + '</h2>'); last = end + 5
        out.append(s[last:]); s = ''.join(out)
    # Every page gets exactly one H1 (category and contact pages had none).
    if not re.search(r'<h1[\s>]', s):
        title = re.search(r'<title>([^<]*)</title>', s)
        t = html.unescape(title.group(1)).split('|')[0].strip() if title else ''
        t = t.replace('AR Unlimited Supply', 'Crown Plastic & Paper')
        cat = re.match(r'^/products/product_cat-([a-z-]+)/$', url)
        if cat and '-or-' not in url:
            t = 'Wholesale ' + cat.group(1).replace('-', ' ').title()
        if t:
            h1 = '<h1 class="cpp-sr-only">%s</h1>' % html.escape(t)
            s = re.sub(r'(<div id="content"[^>]*>)', r'\1' + h1, s, count=1)

    # --- performance -----------------------------------------------------------
    s = webp_swap(s, os.path.dirname(path))
    s = re.sub(r'<img(?![^>]*\bdecoding=)', '<img decoding="async"', s)

    # --- homepage: shipping map ---------------------------------------------
    if url == '/':
        i = s.find('Frequently Asked Questions')
        j = s.rfind('e-parent', 0, i)
        k = s.rfind('<div', 0, j)
        if i > 0 and k > 0:
            s = s[:k] + snippets['map'] + s[k:]

    # --- injected layer ---------------------------------------------------------
    head = ('<link rel="stylesheet" href="/upgrade/upgrade.css" %s>' % MARK)
    s = s.replace('</head>', head + '</head>', 1)
    tail = snippets['bar'] + '<script src="/upgrade/upgrade.js" defer></script>'
    s = s.replace('</body>', tail + '</body>', 1)
    open(path, 'w', encoding='utf-8').write(s)

    # --- search index -------------------------------------------------------------
    kind = None
    if url.startswith('/product/'):
        kind = 'Product'
    elif url.startswith('/products/product_cat-') and '-or-' not in url:
        kind = 'Category'
    if kind and url.endswith('/'):
        t = re.search(r'<h1[^>]*>(.*?)</h1>', s, re.S)
        name = strip_tags(t.group(1)) if t else ''
        cat = re.match(r'^/products/product_cat-([a-z-]+)/$', url)
        if kind == 'Category' and cat:
            name = cat.group(1).replace('-', ' ').title()
        if not name:
            tt = re.search(r'<title>([^<]*)</title>', s)
            name = html.unescape(tt.group(1)).split('|')[0].strip() if tt else ''
        img = re.search(r'<meta property="og:image" content="([^"]*)"', s)
        img = img.group(1).replace(ORIGIN, '') if img else ''
        if img and os.path.exists(os.path.join(SITE, img.lstrip('/')) + '.webp'):
            img += '.webp'
        desc = re.search(r'<meta name="description" content="([^"]*)"', s)
        if name:
            search_items.append({'n': html.unescape(name), 'u': url, 'k': kind, 'i': img,
                                 'd': html.unescape(desc.group(1))[:140] if desc else ''})
    return True


def upgrade_css(path):
    s = open(path, encoding='utf-8', errors='ignore').read()
    t = webp_swap(s, os.path.dirname(path))
    if t != s:
        open(path, 'w', encoding='utf-8').write(t)
        return True
    return False


def main():
    if not os.path.isdir(SITE):
        print('no site dir: %s' % SITE)
        return 1
    snippets = {
        'map': open(os.path.join(ASSETS, 'map-section.html'), encoding='utf-8').read(),
        'bar': open(os.path.join(ASSETS, 'action-bar.html'), encoding='utf-8').read(),
    }
    out = os.path.join(SITE, 'upgrade')
    os.makedirs(out, exist_ok=True)
    for name in ('upgrade.css', 'upgrade.js'):
        shutil.copy(os.path.join(ASSETS, name), os.path.join(out, name))

    pages = css = 0
    items = []
    for d, dirs, files in os.walk(SITE):
        if os.path.abspath(d).startswith(os.path.abspath(out)):
            continue
        for f in files:
            p = os.path.join(d, f)
            if f.endswith('.html'):
                pages += upgrade_html(p, snippets, items)
            elif f.endswith('.css') or '.css@' in f:
                css += upgrade_css(p)
    seen, uniq = set(), []
    for it in sorted(items, key=lambda x: (x['k'] != 'Category', x['n'].lower())):
        if it['u'] not in seen:
            seen.add(it['u'])
            uniq.append(it)
    json.dump(uniq, open(os.path.join(out, 'search-index.json'), 'w'), ensure_ascii=False, separators=(',', ':'))
    print('upgraded %d pages, %d stylesheets, %d search entries' % (pages, css, len(uniq)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
