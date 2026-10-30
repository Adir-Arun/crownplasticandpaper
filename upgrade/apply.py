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
import urllib.parse

SITE = sys.argv[1] if len(sys.argv) > 1 else 'site'
HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, 'assets')
MARK = 'data-cpp-upgrade'
# Brand palette refresh (chosen Oct 2026): the pale blue-grey and grey-teal become a warm
# stone and a deep blue that sit better with the navy and cream. Set to {} to switch off.
PALETTE = {'EEF5F8': 'F3F1EC', '1F4959': '163A5C', '64748B': '566275', 'F7FAFC': 'F9F8F5'}  # 64748B failed 4.5:1 on stone
PALETTE_RE = re.compile(r'#(%s)\b' % '|'.join(PALETTE), re.I) if PALETTE else None


# Contact form field icons: filled two-tone icons become thin line icons that match the site.
FORM_ICON_RE = re.compile(r'icn_crown_form_(full-name|company-name|email|phone|message)\.svg')


ICON_LINKS = ('<link rel="icon" href="/favicon.ico" sizes="48x48">'
              '<link rel="icon" href="/favicon.svg" type="image/svg+xml">'
              '<link rel="icon" href="/icon-192.png" type="image/png" sizes="192x192">'
              '<link rel="apple-touch-icon" href="/apple-touch-icon.png">')


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
    r'href="((?:\.\./)*)(?:products/)?(?:product_cat-[^"/]*/)?\{\{data\.[a-z_]+\}\}\.html(#[^"]*)?"')
SEARCH_ACTION_RE = re.compile(
    r'action="((?:\.\./)*)(?:products/)?(?:product_cat-[^"/]*/)?\{\{data\.[a-z_]+\}\}\.html"')


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
    s = fix_product_ld(s, url)
    if url == '/faqs/':
        s = faq_ld(s)
    return drop_ratings(s)


def fix_product_ld(s, url):
    """Product data for Google: drop blocks copied from another product (the PET Cups page
    described an aluminum item), and drop placeholder prices ($59.99, $1.00): Crown quotes
    wholesale prices on request, so no price is published."""
    if not url.startswith('/product/'):
        return s
    slug = url.split('/')[2]

    def foreign(it):
        o = it.get('offers') or {}
        if isinstance(o, list):
            o = o[0] if o else {}
        for u in (it.get('url') or '', o.get('url') or ''):
            if '/product/' in u and '/product/%s/' % slug not in u:
                return True
            if 'aluminum-packaging' in u:
                return True
        return False

    title = re.search(r'<h1[^>]*class="[^"]*product_title[^"]*"[^>]*>(.*?)</h1>', s, re.S)
    title = html.unescape(strip_tags(title.group(1))) if title else ''

    def clean(it):
        it.pop('offers', None)
        if title:
            it['name'] = title  # some entries carried the category name
        it['url'] = ORIGIN + url
        return it

    def fix(m):
        if '"Product"' not in m.group(2):
            return m.group(0)
        try:
            data = json.loads(m.group(2))
        except ValueError:
            return m.group(0)
        if isinstance(data, dict) and '@graph' in data:
            data['@graph'] = [clean(it) if it.get('@type') == 'Product' else it
                              for it in data['@graph'] if not (it.get('@type') == 'Product' and foreign(it))]
        elif isinstance(data, dict) and data.get('@type') == 'Product':
            if foreign(data):
                return ''
            clean(data)
        return m.group(1) + json.dumps(data, ensure_ascii=False) + m.group(3)
    s = LDJSON_RE.sub(fix, s)
    if '"@type": "Product"' not in s and '"@type":"Product"' not in s:
        # this page's only product data described another product: describe this one
        name = re.search(r'<h1[^>]*class="[^"]*product_title[^"]*"[^>]*>(.*?)</h1>', s, re.S)
        img = re.search(r'<meta property="og:image" content="([^"]*)"', s)
        desc = re.search(r'<meta name="description" content="([^"]*)"', s)
        if name:
            ld = {'@context': 'https://schema.org', '@type': 'Product', 'name': html.unescape(strip_tags(name.group(1))),
                  'url': ORIGIN + url, 'brand': {'@type': 'Brand', 'name': 'Crown Plastic & Paper'},
                  'manufacturer': {'@id': ORIGIN + '/#business'}}
            if img:
                ld['image'] = img.group(1)
            if desc:
                ld['description'] = html.unescape(desc.group(1))
            s = s.replace('</head>', '<script type="application/ld+json">%s</script>\n</head>' % json.dumps(ld, ensure_ascii=False), 1)
    return s


def faq_ld(s):
    """FAQPage data from the FAQ accordion, so search and AI answers can quote it."""
    items = []
    for m in re.finditer(r'<details[^>]*class="e-n-accordion-item"[^>]*>(.*?)</details>', s, re.S):
        q = re.search(r'e-n-accordion-item-title-text">(.*?)</div>', m.group(1), re.S)
        a = m.group(1).split('</summary>', 1)[-1]
        q, a = strip_tags(q.group(1)) if q else '', strip_tags(a)
        if q and a and q not in [i['name'] for i in items]:
            items.append({'@type': 'Question', 'name': html.unescape(q),
                          'acceptedAnswer': {'@type': 'Answer', 'text': html.unescape(a)}})
    if not items:
        return s
    ld = {'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': items}
    return s.replace('</head>', '<script type="application/ld+json">%s</script>\n</head>' % json.dumps(ld, ensure_ascii=False), 1)


def indexable(s, url):
    r = re.search(r"<meta name=[\"']robots[\"'] content=[\"']([^\"']*)", s)
    return not (r and 'noindex' in r.group(1)) and not SITEMAP_SKIP.search(url)


TILE_NAMES = ['Cups', 'Containers', 'Foil Products', 'Napkins', 'Cutlery', 'Paper Bags', 'School Trays',
              'Register Paper', 'Toilet Tissue', 'Paper Towels', 'Can Liners', 'Gloves']


def div_span(s, start):
    """(start, end) of the <div> element that opens at `start` (end is after its </div>)."""
    depth, i = 0, start
    tag = re.compile(r'<(/?)div\b[^>]*>')
    for m in tag.finditer(s, start):
        depth += -1 if m.group(1) else 1
        if depth == 0:
            return start, m.end()
    return start, start

CUSTOMER_TILES = {
    'Wholesalers': 'Pallets of Crown PET lids stacked in the Houston warehouse',
    'Food Distributors': 'Food distributor receiving a Crown supply order',
    'Cash and Carry': 'Cash and carry store aisle stocked with food service supplies',
    'Hospitals': 'Hospital receiving a delivery of disposable supplies',
    'Schools': 'School cafeteria serving lunch with disposable trays',
    'Chain Restaurants': 'Chain restaurant staff serving guests',
    'Catering Services': 'Catering line plated for an event',
    'More Businesses': 'Assorted Crown food service packaging',
}
# the About Us grid still carried the old site's labels
CUSTOMER_LEGACY = {'Restaurants': 'Wholesalers', 'Hospitality': 'Food Distributors', 'Food and Beverage': 'Cash and Carry',
                   'Retail': 'Hospitals', 'Clean Restaurants': 'Chain Restaurants',
                   'and more businesses across various industries': 'More Businesses'}


# category page headers: (name, line, photo, alt)
CAT_HEADERS = {
    'gloves': ('Disposable Gloves', 'Nitrile, vinyl and latex gloves by the case for food service, janitorial and healthcare buyers.',
               'crown-cat-gloves', 'Cases of Crown disposable vinyl gloves stacked on pallets in the Houston warehouse'),
    'food-service-supplies': ('Food Service Supplies', 'PET and portion cups with lids, deli and take-out containers, cutlery kits, food film and paper bags.',
                              'crown-cat-food-service-supplies', 'Pallets of Crown 28 oz rectangular black containers in the Houston warehouse'),
    'paper-napkins': ('Paper Napkins', 'Interfold, tall fold, dinner and beverage napkins in bulk cases.',
                      'crown-cat-paper-napkins', 'Stacked cases of Crown white tall fold napkins'),
    'paper-supply': ('Paper Supply', 'Kitchen roll towels, C-fold towels, multi-fold and single-fold napkins.',
                     'crown-cat-paper-supply', 'Racks of Crown paper cases along a warehouse aisle'),
    'aluminum-products': ('Aluminum Products', 'Foil rolls and sheets, round and steam table pans, lids and plates.', None, None),
    'miscellaneous': ('Janitorial & Miscellaneous', 'Trash liners, poly bags, stretch film, wax and deli papers, register rolls and school trays.',
                      'crown-cat-miscellaneous', 'Pallets of can liners on warehouse racking'),
    'toilet-tissue': ('Toilet Tissue', 'Jumbo roll and individually wrapped bath tissue by the case.', None, None),
}


def cat_header(slug, count):
    name, line, photo, alt = CAT_HEADERS[slug]
    img = ('<div class="cpp-cat-hero-media"><img src="/wp-content/uploads/2026/10/%s.webp" width="900" height="600" alt="%s" '
           'fetchpriority="high" decoding="async"></div>' % (photo, html.escape(alt))) if photo else ''
    return ('<section class="cpp-cat-hero%s" data-cpp-upgrade aria-labelledby="cpp-cat-title"><div class="cpp-cat-hero-in">'
            '<div class="cpp-cat-hero-copy">'
            '<nav class="cpp-cat-crumbs" aria-label="Breadcrumb"><a href="/">Home</a><span aria-hidden="true">/</span>'
            '<a href="/products/">Products</a><span aria-hidden="true">/</span><span aria-current="page">%s</span></nav>'
            '<h1 id="cpp-cat-title">Wholesale %s</h1><p class="cpp-cat-line">%s</p>'
            '<p class="cpp-cat-meta">%d products <span aria-hidden="true">·</span> Ships from Houston in 24–48 hrs</p>'
            '<div class="cpp-cat-actions"><a class="cpp-hbtn cpp-hbtn--main" href="/get-your-quote/">Request a Quote'
            '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg></a>'
            '<a class="cpp-cat-tel" href="tel:+18449008804">or call (844) 900-8804</a></div>'
            '</div>%s</div></section>') % (' cpp-cat-hero--photo' if photo else '', html.escape(name), html.escape(name),
                                          html.escape(line), count, img)


def close_open_styles(s):
    """A few WordPress pages have a <style> block that is never closed (an HTML widget with custom CSS),
    so the browser treats the rest of the page - footer, scripts - as CSS. Close it where the CSS ends."""
    out, pos = [], 0
    for m in re.finditer(r'<style\b[^>]*>', s):
        if m.start() < pos:
            continue
        close = s.find('</style>', m.end())
        tag = re.search(r'\n\s*<(?!/?style\b)[a-zA-Z!/]', s[m.end():])
        if tag and (close < 0 or m.end() + tag.start() < close):
            cut = m.end() + tag.start()
            out.append(s[pos:cut] + '</style>')
            pos = cut
    out.append(s[pos:])
    return ''.join(out)


def filter_combo(s, url):
    """Multi-category filter pages (/products/product_cat-a-or-b/) were saved with every
    category on them: keep only the categories in the URL."""
    m = re.match(r'^/products/product_cat-([a-z-]+-or-[a-z-]+)/$', url)
    if not m:
        return s
    wanted = {w.replace('-', ' ').title() for w in m.group(1).split('-or-')}
    out, pos = [], 0
    for t in re.finditer(r'<h2 class="ts-category-title">([^<]*)</h2>', s):
        g = s.find('<div class="ts-category-product-grid"', t.end())
        if g < 0 or g - t.end() > 200:
            continue
        end = div_span(s, g)[1]
        if html.unescape(t.group(1)).strip().title() not in wanted:
            out.append(s[pos:t.start()])
            pos = end
    out.append(s[pos:])
    return ''.join(out)


def section_span(s, el_id):
    m = re.search(r'<div class="elementor-element elementor-element-%s ' % el_id, s)
    return div_span(s, m.start()) if m else None


HOME_FAQ = ['How can I place an order?', 'Do you offer bulk pricing?', 'Do you supply eco-friendly or compostable products?',
            'Where do you deliver?', 'How long does delivery take?']
BEST_SELLERS = ['pet-cups', 'portion-cups', 'deli-containers', 'round-foil-pans', 'blue-nitrile-gloves', 'paper-bags',
                'dinner-napkins', 'trash-liners']


def home_faq(s):
    items = []
    for m in re.finditer(r'<details[^>]*class="e-n-accordion-item"[^>]*>(.*?)</details>', s, re.S):
        q = re.search(r'e-n-accordion-item-title-text">(.*?)</div>', m.group(1), re.S)
        q = strip_tags(q.group(1)) if q else ''
        if q in HOME_FAQ and q not in [x[0] for x in items]:
            items.append((q, strip_tags(m.group(1).split('</summary>', 1)[-1])))
    items.sort(key=lambda x: HOME_FAQ.index(x[0]))
    rows = ''.join('<details class="cpp-faq-item"%s><summary>%s<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 9l6 6 6-6"/></svg></summary><p>%s</p></details>'
                   % (' open' if i == 0 else '', html.escape(html.unescape(q)), html.escape(html.unescape(a))) for i, (q, a) in enumerate(items))
    return ('<section class="cpp-faq" data-cpp-upgrade aria-labelledby="cpp-faq-title"><div class="cpp-wrap">'
            '<h2 id="cpp-faq-title">Frequently Asked Questions</h2><div class="cpp-faq-list">%s</div>'
            '<p class="cpp-faq-more"><a href="/faqs/">See all questions<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg></a></p>'
            '</div></section>') % rows


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


# Links that were left as "#" in WordPress (blog keywords, a hidden old footer): give them
# real destinations. Internal links from articles to products also help search engines.
DEAD_LINKS = {
    'disposable napkins': '/products/product_cat-paper-napkins/',
    'wholesale food packaging': '/products/',
    'takeout bags for restaurants': '/product/paper-bags/',
    'disposable tableware': '/product/round-plates/',
    'food storage bags for restaurants': '/product/poly-bags/',
    'wholesale distribution': '/business-partnership/',
    'disposable portion cups': '/product/portion-cups/',
    'food delivery packaging': '/products/product_cat-food-service-supplies/',
    'international sourcing': '/about-us/',
    'tamper evident food packaging': '/product/deli-containers/',
    'contact us': '/contact-us/',
    'request a quote': '/get-your-quote/',
    'browse products': '/products/',
    'products': '/products/',
    'privacy policy': '/privacy-policy/',
    'terms &amp; conditions': '/terms-conditions/',
    'accessibility statement': '/accessibility-statement/',
    'do not sell my personal information': '/do-not-sell-my-personal-information/',
}


def fix_dead_links(s):
    def repl(m):
        text = re.sub(r'<[^>]+>|\s+', ' ', m.group(3)).strip().lower()
        target = DEAD_LINKS.get(text)
        return m.group(1) + target + m.group(2) + m.group(3) + '</a>' if target else m.group(0)
    s = re.sub(r'(<a [^>]*href=")#("[^>]*>)(.{1,2500}?)</a>', repl, s, flags=re.S)
    # the header logo linked to "#" on many pages: it goes home
    return re.sub(r'(data-widget_type="theme-site-logo\.default">\s*<a href=")#(")', r'\1/\2', s)


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
        if text == 'home':  # product-page breadcrumb
            return 'href="/"'
        for key, target in PLACEHOLDER_TARGETS.items():
            if text.startswith(key):
                return 'href="/%s"' % target
        return 'href="#"' if frag == '#' else 'href="/"'  # the logo and other bare links go home
    s = PLACEHOLDER_RE.sub(repl, s)
    s = SEARCH_ACTION_RE.sub('action="/products/"', s)
    # anything the mirror still pointed at its {{data.*}} template stubs goes home
    s = re.sub(r'href="(?:https?://[^"]*)?[^"]*\{\{data\.[^"]*"', 'href="/"', s)
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

    # --- About Us video still showed an AR Unlimited Supply truck: use the Crown warehouse photo
    s = s.replace('/wp-content/uploads/2026/01/img_arus_about_bg.png', '/wp-content/uploads/2026/10/crown-video-cover.webp')  # Crown warehouse: 12 oz PET cup aisle
    s = FORM_ICON_RE.sub(r'icn_crown_form_\1-line.svg', s)

    # --- testimonial titles mixed straight and curly quotes: use curly everywhere
    s = re.sub(r'(<h5 class="elementor-heading-title elementor-size-default">)"([^"<]{3,120})"(</h5>)', '\\1\u201c\\2\u201d\\3', s)

    # --- labels say what happens (HIG writing.md): form buttons, contact title
    s = s.replace('<span class="elementor-button-text">Submit</span>', '<span class="elementor-button-text">Send Message</span>')
    s = s.replace('>Get In Contact<', '>Get in Touch<')

    # --- product page: the button says what it does (HIG writing.md: labels are actions)
    s = re.sub(r'(id="product-detail-quote">.*?<span class="elementor-button-text">)Price Upon Request(</span>)',
               r'\1Request a Quote\2', s, count=1, flags=re.S)

    # --- heading levels: product tiles are items, not sections (H2 -> H3); card, testimonial and
    #     footer titles skipped from H2 to H5 (H5 -> H3). Styling comes from classes, so nothing moves.
    if url == '/':
        s = re.sub(r'<h2 class="elementor-heading-title elementor-size-default">(%s)</h2>' % '|'.join(TILE_NAMES),
                   r'<h3 class="elementor-heading-title elementor-size-default">\1</h3>', s)
    s = re.sub(r'<h5( class="elementor-heading-title[^"]*">)(.*?)</h5>', r'<h3\1\2</h3>', s, flags=re.S)

    # --- category bar: "New Arrivals" (it only linked to the shop page) becomes Disposable Gloves
    gloves = '/products/product_cat-gloves/'
    active = url == gloves
    s = re.sub(r'(menu-item-4234"><a href=")[^"]*(" class="elementor-item)("[^>]*>)New Arrivals</a>',
               lambda m: m.group(1) + gloves + m.group(2) + (' elementor-item-active" aria-current="page' if active else '') + m.group(3) + 'Disposable Gloves</a>', s)

    s = filter_combo(s, url)
    s = close_open_styles(s)
    if url.startswith('/products/product_cat-') and '-or-' in url:
        s = set_robots(s, 'noindex, follow')  # filter combinations are not pages of their own

    # --- broken links ----------------------------------------------------------
    s = fix_placeholders(s)
    s = fix_dead_links(s)
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
        if cat and '-or-' not in url and POLISH and cat.group(1) in CAT_HEADERS:
            h1 = cat_header(cat.group(1), s.count('class="product-card"'))
            s = re.sub(r'(<div id="content"[^>]*>)', lambda m: m.group(1) + h1, s, count=1)
        elif t:
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
        if url not in ('/', '/get-your-quote/', '/contact-us/') and 'cpp-pre' not in s:
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

    # --- browser tab icon: the crown mark alone, transparent, white in dark tabs
    s = re.sub(r'<link rel="(?:icon|apple-touch-icon)"[^>]*>\s*', '', s)
    s = re.sub(r'<meta name="msapplication-TileImage"[^>]*>\s*', '', s)
    s = s.replace('</head>', ICON_LINKS + '\n</head>', 1)

    # --- brand colour for mobile browser chrome, and business details for Google --------
    if 'name="theme-color"' not in s:
        s = s.replace('</head>', '<meta name="theme-color" content="#011425">\n</head>', 1)
    if url in ('/', '/contact-us/'):
        s = s.replace('</head>', '<script type="application/ld+json">%s</script>\n</head>' % json.dumps(BUSINESS_LD), 1)

    # --- homepage round 2: static hero, best sellers, ordering steps, short FAQ, no newsletter
    if url == '/' and POLISH:
        sp = section_span(s, '0aac01e')            # slider hero (3 slides, 2 hidden) -> static hero
        if sp:
            s = s[:sp[0]] + snippets['hero'] + s[sp[1]:]
        sp = section_span(s, '5be266d')            # after the product categories
        if sp:
            s = s[:sp[1]] + snippets['home_x'] + s[sp[1]:]
        sp = section_span(s, '5219eb1')            # 26-question tabbed FAQ -> 5 key questions + link
        if sp:
            s = s[:sp[0]] + home_faq(s[sp[0]:sp[1]]) + s[sp[1]:]
        sp = section_span(s, '2e1d291')            # newsletter: low value for wholesale buyers
        if sp:
            s = s[:sp[0]] + s[sp[1]:]

    # customer photos were shuffled (Schools showed catering, Hospitals a store delivery...):
    # each tile gets the photo file named after its own title
    def match_photo(m):
        block = m.group(0)
        t = re.search(r'(elementor-image-box-title">)([^<]*)<', block)
        if not t:
            return block
        title = html.unescape(t.group(2)).strip()
        title = CUSTOMER_LEGACY.get(title, title)
        if title not in CUSTOMER_TILES:
            return block
        src = '/wp-content/uploads/2026/03/img_crown_home_our_customers-%s.png.webp' % title.replace(' ', '-')
        block = block[:t.start(2)] + html.escape(title) + block[t.end(2):]
        def fix_img(im):
            tag = im.group(0)
            tag = re.sub(r'\s(?:data-lazy-)?(?:srcset|sizes)="[^"]*"', '', tag)
            tag = re.sub(r'(\s(?:data-lazy-)?src=")(?!data:)[^"]*"', r'\g<1>%s"' % src, tag)
            tag = re.sub(r'\salt="[^"]*"', ' alt="%s"' % html.escape(CUSTOMER_TILES[title]), tag)
            return re.sub(r'\stitle="[^"]*"', '', tag)
        return re.sub(r'<img\b[^>]*>', fix_img, block)
    s = re.sub(r'<div class="elementor-element[^"]*elementor-widget-image-box".*?elementor-image-box-title">[^<]*<', match_photo, s, flags=re.S)
    # Wholesalers gets a Crown warehouse photo (pallets of PET lids)
    s = re.sub(r'(?:\.\./)*/?wp-content/uploads/2026/03/img_crown_home_our_customers-Wholesalers[^"\' ,]*?\.png(?:\.webp)?',
               '/wp-content/uploads/2026/10/crown-customers-wholesalers.webp', s)
    s = re.sub(r'(crown-customers-wholesalers\.webp) \d+w(?:, [^"]*)?"', r'\1 540w"', s)

    # --- injected layer ---------------------------------------------------------
    head = ('<link rel="stylesheet" href="/upgrade/upgrade.css" %s>' % MARK)
    if POLISH:
        head += '<link rel="stylesheet" href="/upgrade/polish.css">'
    s = s.replace('</head>', head + '</head>', 1)
    tail = snippets['bar'] + '<script src="/upgrade/upgrade.js" defer></script>'
    s = s.replace('</body>', tail + '</body>', 1)
    s = re.sub(r'href="(?:\.\./)*/?login/"', 'href="/contact-us/"', s)  # hidden old Login button: no such page
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
    t = FORM_ICON_RE.sub(r'icn_crown_form_\1-line.svg', recolor(webp_swap(s, os.path.dirname(path))))
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
        'hero': open(os.path.join(ASSETS, 'hero.html'), encoding='utf-8').read(),
        'home_x': open(os.path.join(ASSETS, 'home-extras.html'), encoding='utf-8').read(),
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
    # homepage best sellers: real product cards from the search index
    home = os.path.join(SITE, 'index.html')
    hs = open(home, encoding='utf-8').read()
    if '<!--cpp-bestsellers-->' in hs:
        by = {it['u']: it for it in uniq}
        cards = []
        for slug in BEST_SELLERS:
            it = by.get('/product/%s/' % slug)
            if not it:
                continue
            cards.append('<li class="cpp-best-card"><a class="cpp-best-link" href="%s"><span class="cpp-best-img"><img src="%s" alt="%s" loading="lazy" decoding="async" width="240" height="240"></span><span class="cpp-best-name">%s</span></a>'
                         '<a class="cpp-best-quote" href="/get-your-quote/?product=%s">Request a Quote</a></li>'
                         % (it['u'], it['i'], html.escape(it['n']), html.escape(it['n']), urllib.parse.quote(it['n'])))
        open(home, 'w', encoding='utf-8').write(hs.replace('<!--cpp-bestsellers-->', ''.join(cards)))

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
    for name in os.listdir(os.path.join(ASSETS, 'icons')):
        shutil.copy(os.path.join(ASSETS, 'icons', name), os.path.join(SITE, name))
    photo_dir = os.path.join(SITE, 'wp-content', 'uploads', '2026', '10')
    os.makedirs(photo_dir, exist_ok=True)
    for name in os.listdir(os.path.join(ASSETS, 'photos')):
        shutil.copy(os.path.join(ASSETS, 'photos', name), os.path.join(photo_dir, name))
    icon_dir = os.path.join(SITE, 'wp-content', 'uploads', '2026', '03')
    if os.path.isdir(icon_dir):
        for name in os.listdir(os.path.join(ASSETS, 'form-icons')):
            shutil.copy(os.path.join(ASSETS, 'form-icons', name),
                        os.path.join(icon_dir, 'icn_crown_form_%s-line.svg' % name[:-4]))
    # Branded "page not found" (Vercel serves /404.html for unknown paths).
    open(os.path.join(SITE, '404.html'), 'w', encoding='utf-8').write(
        recolor(open(os.path.join(ASSETS, '404.html'), encoding='utf-8').read()))
    print('upgraded %d pages, %d stylesheets, %d search entries' % (pages, css, len(uniq)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
