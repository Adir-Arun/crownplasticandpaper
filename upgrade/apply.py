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
# Brand palette refresh (chosen Oct 2026): the pale blue-grey and grey-teal become a warm
# stone and a deep blue that sit better with the navy and cream. Set to {} to switch off.
PALETTE = {'EEF5F8': 'F3F1EC', '1F4959': '163A5C'}
PALETTE_RE = re.compile(r'#(%s)\b' % '|'.join(PALETTE), re.I) if PALETTE else None


def recolor(s):
    return PALETTE_RE.sub(lambda m: '#' + PALETTE[m.group(1).upper()], s) if PALETTE_RE else s


POLISH = True  # visual polish layer (upgrade/assets/polish.css); set False to switch it off
ORIGIN = 'https://www.crownplasticandpaper.com'

PHONE_TEXT = '(844) 900-8804'
PHONE_TEL = 'tel:+18449008804'
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
    r'href="((?:\.\./)*)products/product_cat-aluminum-products-or-[^"]*?\{\{data\.gallery_thumbnail_src\}\}\.html(#[^"]*)?"')
SEARCH_ACTION_RE = re.compile(
    r'action="((?:\.\./)*)products/product_cat-aluminum-products-or-[^"]*?\{\{data\.gallery_thumbnail_src\}\}\.html"')


BRAND_OLD = 'AR Unlimited Supply'
BRAND_NEW = 'Crown Plastic & Paper'
LDJSON_RE = re.compile(r'(<script[^>]*application/ld\+json[^>]*>)(.*?)(</script>)', re.S)


BUSINESS_LD = {
    '@context': 'https://schema.org',
    '@type': 'WholesaleStore',
    '@id': ORIGIN + '/#business',
    'name': 'Crown Plastic & Paper',
    'url': ORIGIN + '/',
    'logo': ORIGIN + '/wp-content/uploads/2026/01/icn_crown_logo.svg',
    'telephone': '+1-844-900-8804',
    'email': EMAIL,
    'address': {'@type': 'PostalAddress', 'streetAddress': '7350 Langfield Rd', 'addressLocality': 'Houston',
                'addressRegion': 'TX', 'postalCode': '77092', 'addressCountry': 'US'},
    'areaServed': 'US',
    'description': 'Wholesale disposable food service packaging: cups, containers, foil, paper and gloves, shipped from Houston, Texas.',
}


# ---------------------------------------------------------------------------------------
# SEO audit fixes (Oct 2026 crawl of the live site)
CATEGORY_NAMES = {
    'aluminum-products': 'Aluminum Foil Products', 'food-service-supplies': 'Food Service Supplies',
    'gloves': 'Disposable Gloves', 'miscellaneous': 'Janitorial & Miscellaneous Supplies',
    'paper-napkins': 'Paper Napkins', 'paper-supply': 'Paper Supplies', 'toilet-tissue': 'Toilet Tissue',
}
# Near-copies of the AR Unlimited Supply legal pages: keep them out of Google, keep links followed.
NOINDEX_PAGES = {'/terms-conditions/', '/privacy-policy/', '/accessibility-statement/',
                 '/do-not-sell-my-personal-information/', '/category/uncategorized/'}
# Real articles that WordPress had set to noindex.
INDEX_PAGES = {'/choosing-the-right-food-packaging-for-your-business/',
               '/why-bulk-purchasing-saves-money-for-food-businesses/'}
# Two products shared one title; the latex page carried the nitrile copy.
FIX_TITLES = {
    '/product/latex-gloves/': ('Disposable Latex Gloves | Wholesale Bulk Supply USA',
                               'Disposable latex gloves in bulk cases for food handling, janitorial and commercial use. '
                               'Wholesale pricing from Crown Plastic & Paper in Houston, TX.'),
}
DEFAULT_OG_IMAGE = ORIGIN + '/wp-content/uploads/2026/01/img_crown_The_Trusted_Choice_of_Distributors.png'
INDEX_ROBOTS = 'follow, index, max-snippet:-1, max-video-preview:-1, max-image-preview:large'
SITEMAP_SKIP = re.compile(r'^/product/single-fold-napkins/|^/(?:\d{4}/|category/[^/]+/page/|products/page/|blog/page/|feed/)|-or-|-[23]/$')


def set_robots(s, value):
    s, n = re.subn(r"<meta name=[\"']robots[\"'] content=[\"'][^\"']*[\"']\s*/?>", '<meta name="robots" content="%s">' % value, s)
    if not n:
        s = s.replace('</head>', '<meta name="robots" content="%s">\n</head>' % value, 1)
    return s


def set_title(s, title, desc=None):
    t = html.escape(title, quote=True)
    s = re.sub(r'<title>[^<]*</title>', lambda m: '<title>%s</title>' % t, s, count=1)
    s = re.sub(r'(<meta (?:property|name)="(?:og:title|twitter:title)" content=")[^"]*', lambda m: m.group(1) + t, s)
    if desc:
        d = html.escape(desc, quote=True)
        if re.search(r'<meta name="description"', s):
            s = re.sub(r'(<meta name="description" content=")[^"]*', lambda m: m.group(1) + d, s)
        else:
            s = s.replace('</head>', '<meta name="description" content="%s">\n</head>' % d, 1)
        s = re.sub(r'(<meta (?:property|name)="(?:og:description|twitter:description)" content=")[^"]*', lambda m: m.group(1) + d, s)
    return s


def drop_ratings(s):
    """No reviews are shown on the site, so star ratings in Google data are not allowed."""
    def clean(o):
        if isinstance(o, dict):
            return {k: clean(v) for k, v in o.items() if k not in ('aggregateRating', 'review')}
        if isinstance(o, list):
            return [clean(v) for v in o]
        return o

    def fix(m):
        if 'aggregateRating' not in m.group(2):
            return m.group(0)
        try:
            data = json.loads(m.group(2))
        except ValueError:
            return m.group(0)
        return m.group(1) + json.dumps(clean(data), ensure_ascii=False) + m.group(3)
    return LDJSON_RE.sub(fix, s)


def seo(s, url):
    cat = re.match(r'^/products/product_cat-([a-z-]+)/$', url)
    if cat and '-or-' not in url:
        slug = cat.group(1)
        name = CATEGORY_NAMES.get(slug, slug.replace('-', ' ').title())
        s = set_robots(s, INDEX_ROBOTS)
        s = set_title(s, 'Wholesale %s | Crown Plastic & Paper' % name,
                      'Buy %s wholesale from Crown Plastic & Paper in Houston, TX. Bulk cases and pallets for '
                      'distributors, restaurants and food service businesses. Request a quote.' % name.lower())
    blogcat = re.match(r'^/category/([a-z-]+)/$', url)
    if blogcat and url not in NOINDEX_PAGES and not re.search(r'<meta name="description"', s):
        name = blogcat.group(1).replace('-', ' ')
        s = set_title(s, '%s Articles | Crown Plastic & Paper' % name.title(),
                      'Guides and articles on %s for food service and wholesale buyers, from Crown Plastic & Paper.' % name)
    if url in FIX_TITLES:
        s = set_title(s, *FIX_TITLES[url])
    if url in NOINDEX_PAGES:
        s = set_robots(s, 'noindex, follow')
    if url in INDEX_PAGES:
        s = set_robots(s, INDEX_ROBOTS)
    if 'og:image' not in s:
        s = s.replace('</head>', '<meta property="og:image" content="%s">\n<meta name="twitter:card" content="summary_large_image">\n</head>' % DEFAULT_OG_IMAGE, 1)
    # One description per page (some pages had two from different plugins).
    seen = []
    s = re.sub(r'<meta name="description"[^>]*>\s*', lambda m: '' if seen else (seen.append(1) or m.group(0)), s)
    return drop_ratings(s)


def indexable(s, url):
    r = re.search(r"<meta name=[\"']robots[\"'] content=[\"']([^\"']*)", s)
    return not (r and 'noindex' in r.group(1)) and not SITEMAP_SKIP.search(url)


def rebrand(s):
    """This is Crown's site: replace the AR Unlimited Supply name (titles, Google data, text)."""
    if BRAND_OLD not in s:
        return s
    # JSON-LD is JSON, not HTML: a literal "&" there.
    s = LDJSON_RE.sub(lambda m: m.group(1) + m.group(2).replace(BRAND_OLD, BRAND_NEW) + m.group(3), s)
    return s.replace(BRAND_OLD, html.escape(BRAND_NEW))


def fix_ldjson(s):
    """Google structured data: remove /* comments */ (invalid JSON, the aluminum product
    pages had them) and turn root-relative URLs back into absolute ones."""
    def fix(m):
        body = re.sub(r'/\*.*?\*/', '', m.group(2), flags=re.S)
        body = re.sub(r'((?:[:\[,])\s*)"/(?!/)', r'\1"' + ORIGIN + '/', body)
        return m.group(1) + body + m.group(3)
    return LDJSON_RE.sub(fix, s)


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
        frag = m.group(2) or ''
        if len(frag) > 1:  # a real in-page anchor such as the skip link's #content
            return 'href="%s"' % frag
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


def upgrade_html(path, snippets, search_items, sitemap):
    s = open(path, encoding='utf-8', errors='ignore').read()
    if MARK in s:
        return False
    prefix = rel_prefix(path)
    url = page_url(path)

    # --- content consistency -------------------------------------------------
    # The WordPress site shows two wrong numbers (900-0084 and 900-8801); the real one is 900-8804.
    s = re.sub(r'\(844\) 900-(?:0084|8801)', PHONE_TEXT, s)
    s = re.sub(r'tel:[^"]*?844[^"]*?900(?:%20|[-. ])?(?:0084|8801|8804)', PHONE_TEL, s)
    s = re.sub(r'href="tell?:[^"]*?844[^"]*?900[^"]*?(?:0084|8801|8804)"', 'href="%s"' % PHONE_TEL, s)
    s = re.sub(r'844-900-(?:0084|8801)', '844-900-8804', s)  # plain text and schema.org "telephone"
    s = re.sub(r'Sales@www\.crownplasticandpaper\.com', EMAIL, s, flags=re.I)
    s = re.sub(r'sales@arunlimitedsupply\.com', EMAIL, s, flags=re.I)  # header link went to AR's inbox
    s = rebrand(s)
    s = recolor(s)
    s = fix_ldjson(s)
    s = seo(s, url)
    s = s.replace('@www.crownplasticandpaper.com', '@crownplasticandpaper.com')
    s = s.replace('Copyright © 2025 AR Unlimited Supply', 'Copyright © %s Crown Plastic &#038; Paper' % YEAR)
    s = re.sub(r'Copyright © 2025 Crown', 'Copyright © %s Crown' % YEAR, s)
    s = s.replace('View 2025 Catalog', 'View 2026 Catalog')
    s = re.sub(r'<li[^>]*>\s*<a[^>]*page_id=66[^>]*>\s*Home old\s*</a>\s*</li>', '', s)

    # --- broken links ----------------------------------------------------------
    s = fix_placeholders(s)
    s = re.sub(r'href="([^"#?:]*?)index\.html(#[^"]*)?"',
               lambda m: 'href="%s"' % m.group(2) if not m.group(1) and m.group(2) and len(m.group(2)) > 1
               else 'href="%s%s"' % (m.group(1) or './', m.group(2) or ''), s)
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

    # --- industrial additions (POLISH layer): trust strip under the homepage hero, quote band before the footer
    if POLISH:
        if url == '/':
            i = s.find('About Us</h2>')
            j = s.rfind('e-parent', 0, i)
            k = s.rfind('<div', 0, j)
            if i > 0 and k > 0:
                s = s[:k] + snippets['trust'] + s[k:]
        if url not in ('/get-your-quote/', '/contact-us/') and 'cpp-pre' not in s:
            foot = s.find('<footer data-elementor-type="footer"')
            i = s.find('Join Our Newsletter')
            # the homepage has its newsletter band just above the footer: go above that
            k = s.rfind('<div', 0, s.rfind('e-parent', 0, i)) if 0 < i < foot else -1
            if k < 0:
                k = foot
            if k > 0:
                s = s[:k] + snippets['pre'] + s[k:]

    # --- quote page: the bulk-quote plugin shortcode never rendered; use our quote builder
    s = s.replace('<div class="elementor-shortcode">[dppq_bulk_products]</div>',
                  '<div class="elementor-shortcode">%s</div>' % snippets['quote'])

    # --- brand colour for mobile browser chrome, and business details for Google --------
    if 'name="theme-color"' not in s:
        s = s.replace('</head>', '<meta name="theme-color" content="#011425">\n</head>', 1)
    if url in ('/', '/contact-us/'):
        s = s.replace('</head>', '<script type="application/ld+json">%s</script>\n</head>' % json.dumps(BUSINESS_LD), 1)

    # --- injected layer ---------------------------------------------------------
    head = ('<link rel="stylesheet" href="/upgrade/upgrade.css" %s>' % MARK)
    if POLISH:
        head += '<link rel="stylesheet" href="/upgrade/polish.css">'
    s = s.replace('</head>', head + '</head>', 1)
    tail = snippets['bar'] + '<script src="/upgrade/upgrade.js" defer></script>'
    s = s.replace('</body>', tail + '</body>', 1)
    open(path, 'w', encoding='utf-8').write(s)
    if os.path.basename(path) == 'index.html' and indexable(s, url):
        mod = re.search(r'<meta property="article:modified_time" content="([^"]{10})', s)
        sitemap.append((url, mod.group(1) if mod else None))

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
    t = recolor(webp_swap(s, os.path.dirname(path)))
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
        'quote': open(os.path.join(ASSETS, 'quote-form.html'), encoding='utf-8').read(),
        'trust': open(os.path.join(ASSETS, 'trust-strip.html'), encoding='utf-8').read(),
        'pre': open(os.path.join(ASSETS, 'prefooter.html'), encoding='utf-8').read(),
    }
    out = os.path.join(SITE, 'upgrade')
    os.makedirs(out, exist_ok=True)
    for name in ('upgrade.css', 'upgrade.js', 'polish.css'):
        src = open(os.path.join(ASSETS, name), encoding='utf-8').read()
        open(os.path.join(out, name), 'w', encoding='utf-8').write(recolor(src))

    pages = css = 0
    items, sitemap = [], []
    for d, dirs, files in os.walk(SITE):
        if os.path.abspath(d).startswith(os.path.abspath(out)):
            continue
        for f in files:
            p = os.path.join(d, f)
            if f.endswith('.html'):
                pages += upgrade_html(p, snippets, items, sitemap)
            elif f.endswith('.css') or '.css@' in f:
                css += upgrade_css(p)
    seen, uniq = set(), []
    for it in sorted(items, key=lambda x: (x['k'] != 'Category', x['n'].lower())):
        if it['u'] not in seen:
            seen.add(it['u'])
            uniq.append(it)
    json.dump(uniq, open(os.path.join(out, 'search-index.json'), 'w'), ensure_ascii=False, separators=(',', ':'))
    # sitemap.xml and robots.txt (WordPress's were not part of the copy)
    urls = sorted(sitemap, key=lambda x: (x[0] != '/', x[0].count('/'), x[0]))
    with open(os.path.join(SITE, 'sitemap.xml'), 'w', encoding='utf-8') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
        for u, mod in urls:
            f.write('  <url><loc>%s%s</loc>%s</url>\n' % (ORIGIN, html.escape(u), '<lastmod>%s</lastmod>' % mod if mod else ''))
        f.write('</urlset>\n')
    with open(os.path.join(SITE, 'robots.txt'), 'w', encoding='utf-8') as f:
        f.write('User-agent: *\nAllow: /\nDisallow: /upgrade/search-index.json\n\nSitemap: %s/sitemap.xml\n' % ORIGIN)
    print('sitemap: %d urls' % len(urls))
    # Branded "page not found" (Vercel serves /404.html for unknown paths).
    open(os.path.join(SITE, '404.html'), 'w', encoding='utf-8').write(
        recolor(open(os.path.join(ASSETS, '404.html'), encoding='utf-8').read()))
    print('upgraded %d pages, %d stylesheets, %d search entries' % (pages, css, len(uniq)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
