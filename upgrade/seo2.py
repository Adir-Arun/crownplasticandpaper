"""Nov 2026 SEO/GEO fix spec: one clean business entity, complete Product data, FAQs on core pages,
internal links (related products, blog -> products, footer link band), sister-company mention."""
import glob
import html
import json
import os
import re

import geo
from locations import faq_block

ORIGIN = geo.ORIGIN
E = html.escape
LD_RE = re.compile(r'<script type="application/ld\+json"[^>]*>(.*?)</script>\s*', re.S)
ENTITY_TYPES = {'Organization', 'LocalBusiness', 'WholesaleStore', 'WebSite', 'Corporation', 'Store'}
PRODUCTS = {}      # slug -> {'name', 'url', 'cat', 'cat_url', 'img'}
TOUCHED = set()    # pages whose visible content changed in this pass (sitemap lastmod)

CAT_NAMES = {'aluminum-products': 'Aluminum Products', 'food-service-supplies': 'Food Service Supplies', 'gloves': 'Disposable Gloves',
             'miscellaneous': 'Janitorial & Miscellaneous', 'paper-napkins': 'Paper Napkins', 'paper-supply': 'Paper Supply',
             'toilet-tissue': 'Toilet Tissue'}


def init(site):
    """Read every product page once: name, category (from its breadcrumb) and image."""
    PRODUCTS.clear()
    for f in sorted(glob.glob(os.path.join(site, 'product', '*', 'index.html'))):
        slug = f.split(os.sep)[-2]
        if slug == 'single-fold-napkins':
            continue
        s = open(f, encoding='utf-8').read()
        h1 = re.search(r'<h1[^>]*class="[^"]*product_title[^"]*"[^>]*>(.*?)</h1>', s, re.S)
        name = html.unescape(re.sub(r'<[^>]+>', '', h1.group(1))).strip() if h1 else slug.replace('-', ' ').title()
        cat_slug = ''
        for m in LD_RE.finditer(s):
            if '"BreadcrumbList"' not in m.group(1):
                continue
            c = re.search(r'/products/product_cat-([a-z-]+)/', m.group(1))
            if c:
                cat_slug = c.group(1)
                break
        img = re.search(r'<meta property="og:image" content="([^"]*)"', s)
        img = img.group(1) if img else ''
        if img.startswith('/'):
            img = ORIGIN + img
        PRODUCTS[slug] = {'name': name, 'url': '/product/%s/' % slug,
                          'cat': CAT_NAMES.get(cat_slug, ''), 'cat_slug': cat_slug, 'img': img}


# ---------------------------------------------------------------- P4 + P5: structured data
def _nodes(d):
    if isinstance(d, dict) and '@graph' in d:
        return d['@graph'], True
    return (d if isinstance(d, list) else [d]), False


def _types(n):
    t = n.get('@type', '')
    return set(t if isinstance(t, list) else [t])


def _reref(o):
    """Point every reference to an old business id at the one entity, #org."""
    if isinstance(o, dict):
        if set(o) == {'@id'} and re.search(r'#(organization|localbusiness|business)$', o['@id']):
            return {'@id': ORIGIN + '/#org'}
        return {k: _reref(v) for k, v in o.items()}
    if isinstance(o, list):
        return [_reref(v) for v in o]
    return o


def normalize_ld(s, url):
    """Drop the WordPress plugins' duplicate (and partly fake: 217 area code, 'AB...' address) business entities,
    keep one Product per product page with sku/brand/image/category, then add our single complete entity."""
    is_product = url.startswith('/product/')
    slug = url.split('/')[2] if is_product else ''
    seen_product = [False]
    seen_crumb = [False]

    def fix(m):
        try:
            d = json.loads(m.group(1))
        except ValueError:
            return ''
        nodes, graph = _nodes(d)
        keep = []
        for n in nodes:
            if not isinstance(n, dict):
                continue
            t = _types(n)
            if t & ENTITY_TYPES:
                continue
            if 'FAQPage' in t and not n.get('mainEntity'):
                continue
            if 'BreadcrumbList' in t:
                if seen_crumb[0]:
                    continue
                seen_crumb[0] = True
            if 'WebPage' in t or 'CollectionPage' in t:
                u = (n.get('url') or n.get('@id') or '').split('#')[0]
                if u and u.rstrip('/') != (ORIGIN + url).rstrip('/'):
                    continue          # a page description copied from another page
            if is_product and 'ItemList' in t:
                continue
            if 'Product' in t:
                if not is_product or seen_product[0]:
                    continue
                seen_product[0] = True
                n = product_node(n, slug, url)
            keep.append(_reref(n))
        if not keep:
            return ''
        if graph or len(keep) > 1:
            out = {'@context': 'https://schema.org', '@graph': [dict((k, v) for k, v in n.items() if k != '@context') for n in keep]}
        else:
            out = keep[0]
            out.setdefault('@context', 'https://schema.org')
        return '<script type="application/ld+json">%s</script>\n' % json.dumps(out, ensure_ascii=False).replace('</', '<\\/')

    s = LD_RE.sub(fix, s)
    if is_product and not seen_product[0] and slug in PRODUCTS:
        s = s.replace('</head>', geo.ld(product_node({}, slug, url)) + '\n</head>', 1)
    return s.replace('</head>', geo.ld(geo.ORG_LD) + '\n</head>', 1)


def product_node(n, slug, url):
    p = PRODUCTS.get(slug, {})
    n = dict(n)
    n['@type'] = 'Product'
    n['@id'] = ORIGIN + url + '#product'
    n['name'] = p.get('name') or n.get('name')
    n['url'] = ORIGIN + url
    n['sku'] = 'CPP-' + slug.upper()
    n['brand'] = {'@type': 'Brand', 'name': 'Crown Plastic & Paper'}
    if p.get('img'):
        n['image'] = p['img']
    if p.get('cat'):
        n['category'] = p['cat']
    for k in ('offers', 'aggregateRating', 'review', 'manufacturer', 'seller'):
        n.pop(k, None)
    return n


# ---------------------------------------------------------------- P3: FAQs on core pages
F = geo.F
BASE_FAQ = [
    ('Where is Crown Plastic & Paper located?', 'At %s, %s, %s %s, in a %s warehouse.' % (F['street'], F['city'], F['region'], F['zip'], F['warehouse'])),
    ('Do you sell wholesale to restaurants?', 'Yes. We sell by the case or pallet to restaurants, caterers, distributors and cash-and-carry stores in %s states.' % F['states']),
    ('How fast do orders ship?', 'Usually within %s from Houston, by LTL freight or Houston pick-up.' % F['ship']),
    ('Do you offer Net 30?', 'Yes, after credit approval. Apply online through our credit application.'),
    ('Can I mix products on one pallet?', 'Yes. Cups, containers, foil, gloves and napkins can share a pallet.'),
    ('How do I get pricing?', 'Call %s or request a quote. Pricing tiers are Houston pick-up, 6-pallet delivered and 12-pallet delivered.' % F['phone']),
]
SISTER = ('Is Crown Plastic & Paper related to AR Unlimited Supply?',
          'Yes. Crown Plastic & Paper is a sister company of AR Unlimited Supply LLC (arunlimitedsupply.com), at the same Houston address.')
CORE_FAQ = {
    '/about-us/': ('About Crown Plastic & Paper: common questions', BASE_FAQ + [SISTER]),
    '/contact-us/': ('Contact and ordering questions', [
        ('What is the best way to reach sales?', 'Call %s, text or WhatsApp %s, email %s, or send the quote form.' % (F['phone'], F['whatsapp'], F['email'])),
        ('Can I pick up an order in Houston?', 'Yes, at %s, %s, %s %s. Send your list first so it is staged when you arrive.' % (F['street'], F['city'], F['region'], F['zip'])),
        BASE_FAQ[2], BASE_FAQ[5]]),
    '/get-your-quote/': ('Quote questions', [
        ('What should I include in a quote request?', 'The products, sizes and number of cases you need, your delivery ZIP code (or Houston pick-up), and how often you reorder.'),
        ('How are wholesale prices set?', 'By tier: Houston pick-up, 6 pallets delivered and 12 pallets delivered. Larger orders get the lower tiers.'),
        BASE_FAQ[4], BASE_FAQ[3]]),
    '/applications/': ('Credit application questions', [
        ('Who can apply for Net 30 terms?', 'Businesses buying for resale or for their own operations, such as distributors, restaurants and caterers.'),
        ('What do I need to apply?', 'Your business details, trade references and your sales tax permit (resale certificate) if you buy for resale.'),
        BASE_FAQ[5]]),
    '/business-partnership/': ('Partnership questions', [
        ('Do you work with distributors and wholesalers?', 'Yes. Distributors buy full and mixed pallets with tiered pricing, spec sheets for every item and Net 30 after credit approval.'),
        ('Do you ship outside Texas?', 'Yes. We ship across the U.S. (except the New York area and California) by LTL freight or full truckload.'),
        BASE_FAQ[4], BASE_FAQ[3]]),
    '/products/': ('Product questions', [
        ('What products does Crown Plastic & Paper sell?', 'Food service disposables and janitorial paper: PET cups and lids, portion cups, deli and takeout containers, foil pans and rolls, napkins, gloves, bags, towels, tissue and trash liners.'),
        ('Is there a spec sheet for each product?', 'Yes. Every product page lists case pack, Ti × Hi and cases per pallet, with a PDF spec sheet.'),
        BASE_FAQ[4], BASE_FAQ[5]]),
    '/catalog/': ('Catalog questions', [
        ('Can I download the catalog?', 'Yes. Use Download PDF on this page to save the 2026 catalog (2.6 MB) and share it with your team.'),
        ('How do I get prices for items in the catalog?', 'Request a quote with the items and case counts you need; prices are set by order tier.'),
        BASE_FAQ[2]]),
    '/guides/': ('Questions about the size guides', [
        ('Where do the numbers in the guides come from?', 'From our product spec sheets: case pack, Ti × Hi and cases per pallet for every item.'),
        BASE_FAQ[4], BASE_FAQ[5]]),
    '/industries/': ('Questions about who we supply', [BASE_FAQ[1], BASE_FAQ[2], BASE_FAQ[3], BASE_FAQ[4]]),
    '/locations/': ('Service area questions', [
        ('Where do you ship?', 'Across the U.S. except the New York area and California, from our Houston warehouse by LTL freight or full truckload, plus Houston pick-up.'),
        ('How long does shipping take?', 'Orders leave Houston in %s. Texas cities usually receive them the next business day; most of the South and Midwest in 1–3 business days.' % F['ship']),
        BASE_FAQ[4]]),
}


def _valid_faq(s):
    for m in LD_RE.finditer(s):
        if '"FAQPage"' in m.group(1) and '"mainEntity"' in m.group(1):
            return True
    return False


def insert_before_footer(s, block):
    for marker in ('<section class="cpp-pre"', '<footer data-elementor-type="footer"', '<footer'):
        k = s.find(marker)
        if k > 0:
            return s[:k] + block + s[k:]
    return s


def product_faq(slug, spec_map):
    p = PRODUCTS.get(slug, {'name': slug.replace('-', ' ')})
    name = p['name']
    es = [e['match'] for e in spec_map.get(slug, []) if e.get('match')]
    qa = []
    sizes = geo.product_sizes(spec_map.get(slug, []))
    if sizes:
        qa.append(('What sizes do %s come in?' % name, 'We stock %s in %s.' % (name, ', '.join(sizes))))
    packs = sorted({a.get('pack-size') or a.get('pack-configuration', '').split(' (')[0] for a in es} - {''})
    if packs:
        qa.append(('How many %s are in a case?' % name, 'Case pack: %s.' % ', '.join(packs)))
    pal = sorted({int(a['cases-pallets']) for a in es if str(a.get('cases-pallets', '')).isdigit()})
    if pal:
        qa.append(('How many cases of %s fit on a pallet?' % name, '%s cases per pallet, per our spec sheet.' % (pal[0] if len(pal) == 1 else '%d to %d' % (pal[0], pal[-1]))))
    qa += [('Can I mix %s with other products on one pallet?' % name, 'Yes. Mixed pallets are welcome.'),
           ('How fast does it ship?', 'Orders typically leave our Houston warehouse in %s. Approved accounts get Net 30.' % F['ship'])]
    return qa


def faqs(s, url, spec_map):
    if url in CORE_FAQ and not _valid_faq(s):
        title, qa = CORE_FAQ[url]
        s = insert_before_footer(s, faq_block(title, qa))
        TOUCHED.add(url)
    elif url.startswith('/product/') and not _valid_faq(s):
        slug = url.split('/')[2]
        s = insert_before_footer(s, faq_block('Questions about %s' % PRODUCTS.get(slug, {}).get('name', 'this product'), product_faq(slug, spec_map)))
    if url == '/about-us/' and 'cpp-sister' not in s:
        s = insert_before_footer(s, '<section class="cpp-sister" data-cpp-upgrade><div class="cpp-wrap"><p>Crown Plastic &amp; Paper is a sister company of '
                                    '<a href="https://arunlimitedsupply.com/">AR Unlimited Supply</a>, operating from the same Houston warehouse at 7350 Langfield Rd.</p></div></section>')
    return s


# ---------------------------------------------------------------- P6: internal links
def related(s, url):
    if not url.startswith('/product/') or 'cpp-related' in s:
        return s
    slug = url.split('/')[2]
    me = PRODUCTS.get(slug)
    if not me:
        return s
    same = [p for k, p in PRODUCTS.items() if k != slug and p['cat_slug'] == me['cat_slug']]
    other = [p for k, p in PRODUCTS.items() if k != slug and p['cat_slug'] != me['cat_slug']]
    pick = (same + other)[:4]
    cards = ''.join('<li><a href="%s"><b>%s</b><span>%s</span></a></li>' % (p['url'], E(p['name']), E(p['cat'])) for p in pick)
    links = []
    if me['cat_slug']:
        links.append('<a href="/products/product_cat-%s/">All %s</a>' % (me['cat_slug'], E(me['cat'].lower())))
    links.append('<a href="/locations/texas/houston/">Wholesale supply in Houston</a>')
    links.append('<a href="/catalog/">2026 catalog</a>')
    block = ('<section class="cpp-related" data-cpp-upgrade aria-labelledby="cpp-related-h"><div class="cpp-wrap"><h2 id="cpp-related-h">Related products</h2>'
             '<ul class="cpp-loc-prods">%s</ul><p class="cpp-related-links">%s</p></div></section>') % (cards, ' · '.join(links))
    TOUCHED.add(url)
    return insert_before_footer(s, block)


BLOG_LINKS = [
    (r'takeout-bags', ['paper-bags', 'poly-bags', 'black-hinged-containers']),
    (r'food-packaging-for-your-business|packaging-can-improve|reduce-operating', ['black-containers', 'deli-containers', 'black-hinged-containers']),
    (r'register-rolls', ['register-roll-paper']),
    (r'dinner-napkin', ['dinner-napkins', 'interfold-napkins', 'beverage-napkins']),
    (r'portion-cups', ['portion-cups', 'portion-cups-lids', 'deli-containers']),
    (r'hot-and-cold-foods|temperature', ['black-hinged-containers', 'deep-steam-table-pans', 'foil-lids-for-steam-table-pans']),
    (r'food-storage-bags', ['poly-bags', 'food-film', 'deli-containers']),
    (r'tableware-for-catering', ['disposable-cutlery-kits', 'round-plates', 'dinner-napkins']),
    (r'tamper-evident', ['deli-containers', 'black-containers', 'portion-cups-lids']),
    (r'bulk-purchasing', ['pet-cups', 'black-nitrile-gloves', 'deli-containers']),
    (r'wholesale-distribution|international-sourcing|competitive-marketplace', ['pet-cups', 'blue-nitrile-gloves', 'foil-rolls']),
]


def blog_links(s, url):
    if 'cpp-article-products' in s or not re.search(r'<meta property="article:section"', s):
        return s
    for pat, slugs in BLOG_LINKS:
        if re.search(pat, url):
            break
    else:
        return s
    items = ''.join('<li><a href="%s">%s wholesale</a>%s</li>' % (PRODUCTS[k]['url'], E(PRODUCTS[k]['name']),
                    ' <span>in %s</span>' % E(PRODUCTS[k]['cat']) if PRODUCTS[k]['cat'] else '') for k in slugs if k in PRODUCTS)
    if not items:
        return s
    block = ('<aside class="cpp-article-products" data-cpp-upgrade><div class="cpp-wrap"><h2>Products in this article</h2><ul>%s</ul>'
             '<p>Need a size chart? See our <a href="/guides/">food service packaging size guides</a>.</p></div></aside>' % items)
    TOUCHED.add(url)
    return insert_before_footer(s, block)


def footer_band(cities, guides_list, industries_list):
    cats = ''.join('<li><a href="/products/product_cat-%s/">%s</a></li>' % (k, E(v)) for k, v in CAT_NAMES.items())
    city = ''.join('<li><a href="%s">%s</a></li>' % (u, E(n)) for u, n in cities)
    gd = ''.join('<li><a href="%s">%s</a></li>' % (u, E(n)) for u, n in guides_list)
    ind = ''.join('<li><a href="%s">%s</a></li>' % (u, E(n)) for u, n in industries_list)
    return ('<nav class="cpp-footlinks" data-cpp-upgrade aria-label="Popular pages"><div class="cpp-wrap">'
            '<div><h2>Wholesale products</h2><ul>%s<li><a href="/catalog/">2026 catalog</a></li></ul></div>'
            '<div><h2>Service areas</h2><ul><li><a href="/locations/texas/houston/">Wholesale foodservice supplies Houston</a></li>%s<li><a href="/locations/">All service areas</a></li></ul></div>'
            '<div><h2>Size guides</h2><ul>%s</ul></div>'
            '<div><h2>Who we supply</h2><ul>%s</ul></div>'
            '</div></nav>') % (cats, city, gd, ind)


def add_footer_band(s, band):
    if 'cpp-footlinks' in s:
        return s
    k = s.find('<footer data-elementor-type="footer"')
    return s[:k] + band + s[k:] if k > 0 else s


# ---------------------------------------------------------------- images: alt text, dimensions, image sitemap
from PIL import Image as _PIL   # noqa: E402

FILENAME_ALT = re.compile(r'(^img[ _]|\bimg\b|\.png|\.jpe?g|\.webp|^[A-Za-z]{1,3}\d+$|^\d+x\d+$|^image$|shamerock|handy wacks)', re.I)
DECORATIVE_ALT = {'arrow', 'Back'}
_DIMS = {}
IMAGES = {}        # url -> [(abs image url, caption)] for the image sitemap


def _local_dims(site, src):
    if src.startswith('data:') or src.startswith('http') and not src.startswith(ORIGIN):
        return None
    path = os.path.join(site, re.sub(r'^(?:https?://[^/]+)?/?(?:\.\./)*', '', src.split('?')[0]))
    if path in _DIMS:
        return _DIMS[path]
    dims = None
    try:
        if path.endswith('.svg'):
            t = open(path, encoding='utf-8', errors='ignore').read(2000)
            vb = re.search(r'viewBox="[\d.]+[ ,]+[\d.]+[ ,]+([\d.]+)[ ,]+([\d.]+)"', t)
            if vb:
                dims = (round(float(vb.group(1))), round(float(vb.group(2))))
        else:
            with _PIL.open(path) as im:
                dims = im.size
    except Exception:
        dims = None
    _DIMS[path] = dims
    return dims


def _humanize(src):
    stem = os.path.basename(src.split('?')[0])
    stem = re.sub(r'(\.(png|jpe?g|webp|svg))+$', '', stem, flags=re.I)
    stem = re.sub(r'-\d+x\d+$', '', stem)
    words = [w for w in re.split(r'[_\-\s]+', stem) if w and w.lower() not in
             ('img', 'icn', 'ar', 'crown', 'main', 'raw', 'photo', 'bg', 'product', 'hero', 'copy', 'final', 'new', 'scaled')]
    return ' '.join(words)


def fix_images(s, url, site):
    """Descriptive alt on content images (product photos had file names: 'EZ6', 'img ar gloves main'),
    empty alt on decorative arrows, alt on the logo, width/height where missing. <script> templates are left alone."""
    name = ''
    if url.startswith('/product/'):
        name = PRODUCTS.get(url.split('/')[2], {}).get('name', '')
    h1 = re.search(r'<h1[^>]*>(.*?)</h1>', s, re.S)
    page_name = html.unescape(re.sub(r'<[^>]+>', '', h1.group(1))).strip() if h1 else ''
    found = []
    counter = [0]

    def fix(m):
        t = m.group(0)
        srcs = re.findall(r'\s(?:data-lazy-src|data-src|src)="([^"]*)"', t)
        src = next((x for x in srcs if not x.startswith('data:')), srcs[0] if srcs else '')
        a = re.search(r'\salt="([^"]*)"', t)
        alt = html.unescape(a.group(1)) if a else None
        new = alt
        if 'icn_crown_logo' in src or 'cpp-logo' in t:
            new = alt or 'Crown Plastic & Paper'
        elif alt in DECORATIVE_ALT:
            new = ''
        elif alt == '' and not src.endswith('.svg') and 'gravatar' not in src and not re.search(r'page-\d+-t\.webp|data:', src or 'data:'):
            base = name or page_name or 'Crown Plastic & Paper'
            bw = {w.lower() for w in re.findall(r'\w+', base)}
            hint = ' '.join(w for w in _humanize(src).split() if w.lower().rstrip('s') not in {x.rstrip('s') for x in bw})
            hint = re.sub(r'\s+', ' ', hint.replace(' x', ' x ').replace('_', ' ')).strip(' -,')
            new = '%s, %s' % (base, hint) if re.search(r'[A-Za-z0-9]', hint) else base
        elif alt and FILENAME_ALT.search(alt):
            base = name or page_name or 'Crown Plastic & Paper'
            hint = _humanize(src)
            size = re.search(r'\b(\d+(?:\.\d+)?\s*(?:x\s*\d+(?:\.\d+)?|oz|in)\b)', hint + ' ' + alt, re.I)
            counter[0] += 1
            ez = re.match(r'^ez\s*(\d+)', alt, re.I)
            if ez:
                n_ = ez.group(1)[:2] if ez.group(1).startswith(('10', '12', '15')) else ez.group(1)[:1]
                new = '%s, %s" x 10.75" sheets' % (base, n_)
            elif 'handy wacks' in alt.lower():
                new = '%s, 12" x 10.75" sheets' % base
            elif 'with Box' in alt or 'with Box' in hint or 'box' in hint.lower().split():
                new = '%s, case and box' % base
            elif size:
                new = '%s, %s' % (base, size.group(1))
            elif 'customers hospitals' in alt.lower():
                new = 'Hospital food service supplied by Crown Plastic & Paper'
            elif 'business partnership' in alt.lower():
                new = 'Crown Plastic & Paper business partnership'
            else:
                new = base if counter[0] == 1 else '%s, view %d' % (base, counter[0])
        if new is not None and new != alt:
            t = re.sub(r'\salt="[^"]*"', ' alt="%s"' % html.escape(new, quote=True), t, count=1) if a else t.replace('<img', '<img alt="%s"' % html.escape(new, quote=True), 1)
        elif a is None:
            t = t.replace('<img', '<img alt=""', 1)
        if not (re.search(r'\swidth="', t) and re.search(r'\sheight="', t)):
            d = _local_dims(site, src)
            if d:
                t = re.sub(r'\s(?:width|height)="[^"]*"', '', t).replace('<img', '<img width="%d" height="%d"' % d, 1)
        final_alt = re.search(r'\salt="([^"]*)"', t)
        if final_alt and final_alt.group(1) and not src.startswith('data:') and not src.endswith('.svg') and 'gravatar' not in src:
            found.append((src, html.unescape(final_alt.group(1))))
        return t

    parts = re.split(r'(<script\b.*?</script>|<noscript\b.*?</noscript>)', s, flags=re.S)
    for i in range(0, len(parts), 2):
        parts[i] = re.sub(r'<img\b[^>]*>', fix, parts[i])
    seen = set()
    imgs = []
    for src, cap in found:
        absu = src if src.startswith('http') else ORIGIN + '/' + re.sub(r'^/?(?:\.\./)*', '', src)
        absu = re.sub(r'\.(png|jpe?g)\.webp$', r'.\1.webp', absu)
        if absu in seen or not absu.startswith(ORIGIN):
            continue
        seen.add(absu)
        imgs.append((absu, cap))
    IMAGES[url] = imgs[:10]
    return ''.join(parts)
