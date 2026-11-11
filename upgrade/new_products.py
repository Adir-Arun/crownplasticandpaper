"""Products added after the WordPress snapshot was taken.

WordPress is no longer the source for new items, so each one is built here from the page of a
similar product already in the snapshot (same layout, menus and scripts) with its own text, photo
and data. The rest of the upgrade layer then treats it like any other product page.

add_pages(site) runs before the upgrade pass; link(s, prefix) adds the new items to the
"Products" menus and to the product grids on every page.
"""
import html
import os
import re

E = html.escape


def _rep(s, old, new, count=None):
    """Replace and insist the source text was there: if WordPress copy changes, fail the build
    loudly instead of publishing a half-edited page."""
    n = s.count(old)
    if not n or (count is not None and n != count):
        raise RuntimeError('new_products: expected %s x %r, found %d' % (count or '>=1', old[:80], n))
    return s.replace(old, new)


def _drop(s, pattern):
    s2, n = re.subn(pattern, '', s, flags=re.S)
    if not n:
        raise RuntimeError('new_products: nothing matched %r' % pattern[:80])
    return s2


# ------------------------------------------------------------------------------------------------
LUNCH = {
    'slug': 'lunch-napkins',
    'base': 'dinner-napkins',
    'name': 'Lunch Napkins',
    'photo': '/wp-content/uploads/2026/10/Lunch-Napkins-12x12',   # + .png / -300x300.png ... (upgrade/assets/photos)
    'title': 'Lunch Napkins 12" x 12" Wholesale | 6,000 per Case',
    'desc': '12" x 12" lunch napkins in bulk, 6,000 per case (item LN12-6000) for restaurants, cafeterias, '
            'schools and takeout. 36 cases per pallet, shipped from Houston, TX.',
    'tagline': 'Everyday 12" x 12" Size • Bulk 6,000 per Case • Meals, Cafeterias &amp; Takeout',
    'short': '12&#8243; &#215; 12&#8243; lunch napkins, 6,000 per case. The everyday napkin for quick-service '
             'restaurants, cafeterias, school lunch lines, catering and takeout bags.',
    'benefits': [('Everyday Size', '12" x 12"'), ('Bulk Value', '6,000 per Case'),
                 ('Versatile Use', 'Meals &amp; Takeout'), ('Absorbent', 'Quick Cleanup')],
    'overview': [
        "Crown Plastic and Paper's Lunch Napkins (item LN12-6000) are food-safe, absorbent disposable paper napkins "
        "measuring 12 x 12 inches, the everyday size between a beverage napkin and a full 15 x 17 inch dinner napkin.",
        'Lunch napkins are the napkin handed out with every meal at quick-service and fast-casual restaurants, cafeterias, '
        'school and university lunch lines, break rooms, delis, food trucks and catered events, and the one dropped into '
        'takeout and delivery bags.',
        'Sold 6,000 napkins per case, stacked 9 x 4 for 36 cases per pallet, so high-volume kitchens can keep a steady '
        'supply on hand at bulk pricing. Mixed pallets with other Crown products are welcome.',
        'Perfect for restaurant owners, cafeteria and school food service directors, caterers, convenience stores, '
        'foodservice distributors and wholesale resellers looking for bulk 12 x 12 lunch napkins shipped from Houston, Texas.',
    ],
    'features': ['12&quot; x 12&quot; Lunch Napkin Size', 'Absorbent Paper', '6,000 per Case', '36 Cases per Pallet (9 x 4)',
                 'Everyday Meals &amp; Takeout', 'Cafeteria &amp; School Ready', 'Food Safe'],
    # (label, dinner value) -> lunch value; None drops the row
    'spec': [('Napkin Type', 'Dinner', 'Lunch'), ('Ply', '2-Ply', None), ('Pack Size', '3,000/Case', '6,000/Case'),
             ('Ti x Hi', '9 x 5', '9 x 4'), ('Cases/Pallets', '45', '36'), ('Material', 'Paper', 'Paper'),
             ('Color', 'White', 'White'), ('Sheet Size', '15x17 inch', '12x12 inch'), ('Product Type', 'Dinner Napkins', 'Lunch Napkins'),
             ('Usage', 'Dining and full-service meal presentation', 'Everyday meals, cafeterias and takeout'),
             ('Food Safe', 'Yes', 'Yes'), ('Packaging', '3,000 napkins per case', '6,000 napkins per case'),
             ('Storage', 'Store in a cool, dry place', 'Store in a cool, dry place')],
    'apps': [('img-dinner-napkins-Table-Service-Restaurants', 'Table Service Restaurants', 'icn-tall-fold-napkins-Fast-Food-Quick-Service-Chains', 'Quick-Service Restaurants'),
             ('img-dinner-napkins-Catering-Banquet-Halls', 'Catering &amp; Banquet Halls', 'icn-tall-fold-napkins-School-Institutional-Cafeterias', 'School &amp; Institutional Cafeterias'),
             ('img-dinner-napkins-Wedding-Corporate-Events', 'Wedding &amp; Corporate Events', 'img-black-containers-Corporate-Catering', 'Catering &amp; Events'),
             ('img-dinner-napkins-Hotel-Dining-Rooms', 'Hotel Dining Rooms', 'img-black-containers-Restaurant-Takeout', 'Takeout &amp; Delivery')],
    'faqs': [('2-ply vs 1-ply dinner napkins?', 'What size are lunch napkins?',
              '2-ply is softer, more absorbent, and thicker appropriate for table service. 1-ply is more economical for self-serve environments.',
              '12 x 12 inches: larger than a 9 x 9 beverage napkin and smaller than a 15 x 17 dinner napkin.'),
             ('Per case count?', 'Per case count?', '3000 napkins per case.', '6,000 napkins per case.'),
             ('Standard size?', 'How many cases fit on a pallet?', '15x17 inches full dinner napkin size for table service and catering.',
              '36 cases per pallet, stacked 9 cases per layer and 4 layers high.'),
             ('Appropriate for catering events?', 'Good for takeout and cafeterias?',
              'Yes 2-ply quality meets the standard expected at catered dinners, banquets, and formal event meal service.',
              'Yes. Lunch napkins are the everyday napkin for counter service, cafeteria lines and takeout and delivery bags.')],
    'bulk': 'Crown Plastic and Paper specializes in bulk, wholesale, and distributor-level sourcing of Lunch Napkins. '
            '12 x 12 inch lunch napkins sold 6,000 per case, 36 cases per pallet. Pallet options and mixed-product orders are available.',
}


def _lunch_page(s):
    p = LUNCH
    old_slug, new_slug = p['base'], p['slug']

    # --- structured data: the big Rank Math graph described dinner napkins (with a placeholder price);
    #     drop it and let fix_product_ld() write this product's own Product data.
    s = _drop(s, r'<script type="application/ld\+json"[^>]*>\s*\{\s*"@context": "https://schema.org",\s*"@graph".*?</script>\s*')
    s = _rep(s, '{"@type":"ListItem","position":3,"item":{"name":"Dinner Napkins","@id":"/product/dinner-napkins/"}}',
             '{"@type":"ListItem","position":3,"item":{"name":"Lunch Napkins","@id":"/product/lunch-napkins/"}}', 1)

    # --- head
    s = re.sub(r'<title>[^<]*</title>', '<title>%s</title>' % E(p['title']), s, count=1)
    for k in ('og:title', 'twitter:title'):
        s = re.sub(r'(<meta (?:property|name)="%s" content=")[^"]*' % k, lambda m: m.group(1) + E(p['title']), s)
    for k in ('description', 'og:description', 'twitter:description'):
        s = re.sub(r'(<meta (?:property|name)="%s" content=")[^"]*' % k, lambda m: m.group(1) + E(p['desc']), s)
    s = _rep(s, '<meta property="og:image:alt" content="Dinner Napkins" />', '<meta property="og:image:alt" content="Lunch Napkins" />', 1)
    s = re.sub(r'<meta property="og:updated_time" content="[^"]*" />', '<meta property="og:updated_time" content="2026-11-11T12:00:00+00:00" />', s)
    s = _rep(s, '&raquo; Dinner Napkins Comments Feed', '&raquo; Lunch Napkins Comments Feed', 1)

    # --- URLs of this page (links to the dinner page itself use ../dinner-napkins/ and stay)
    s = _rep(s, '/product/dinner-napkins/', '/product/lunch-napkins/')
    s = _rep(s, '%2Fproduct%2Fdinner-napkins%2F', '%2Fproduct%2Flunch-napkins%2F')
    s = s.replace('<li><a href="index.html">Dinner Napkins</a></li>',
                  '<li><a href="../dinner-napkins/index.html">Dinner Napkins</a></li><li><a href="index.html">Lunch Napkins</a></li>')

    # --- gallery: one photo (the dinner page also showed a 2-ply close-up and its carton)
    for img in ('Dinner-Napkins-2ply', 'White-Dinner-Napkins-Cartyon'):
        s = _drop(s, r'<div class="wvg-gallery-image"><div><div class="wvg-single-gallery-image-container"><img [^>]*?/%s\.png"[^>]*></div></div></div>' % img)
        s = _drop(s, r'<div class="wvg-gallery-thumbnail-image"><div><img [^>]*?alt="%s"[^>]*><noscript>.*?</noscript></div></div>' % img.replace('-', ' '))
    s = _rep(s, '2026/02/Dinner-Napkins-Bulk', p['photo'].replace('/wp-content/uploads/', ''))
    s = s.replace('2026\\/02\\/Dinner-Napkins-Bulk', p['photo'].replace('/wp-content/uploads/', '').replace('/', '\\/'))
    s = _rep(s, 'alt="Dinner Napkins Bulk" title="Dinner Napkins - Bulk"', 'alt="12 x 12 white lunch napkins" title="Lunch Napkins"')

    # --- breadcrumb, title and summary
    s = _rep(s, 'Paper Napkins</a>&nbsp;&#47;&nbsp;Dinner Napkins</nav>', 'Paper Napkins</a>&nbsp;&#47;&nbsp;Lunch Napkins</nav>', 1)
    s = re.sub(r'(<h1[^>]*class="[^"]*product_title[^"]*"[^>]*>)\s*Dinner Napkins\s*(</h1>)', r'\1Lunch Napkins\2', s, count=1)
    s = _rep(s, 'Table Service Quality • Folds Neatly for Place Settings • White Table-Service Color', p['tagline'], 1)
    s = _rep(s, '2-ply dinner napkins, 15&#215;17&#8243;, 3000 per case. Softer and more absorbent for table service restaurants, '
                'catering events, and upscale institutional dining experiences.', p['short'], 1)
    for (o1, o2), (n1, n2) in zip([('Premium Feel', 'Soft Touch'), ('Double Layer', 'Extra Strength'), ('Elegant Look', 'Table Ready'),
                                   ('High Absorbency', 'Spill Control')], p['benefits']):
        s = _rep(s, '<h4 class="benefit-title">%s</h4><p class="benefit-text">%s</p>' % (o1, o2),
                 '<h4 class="benefit-title">%s</h4><p class="benefit-text">%s</p>' % (n1, n2))

    # --- overview: replace the five dinner paragraphs with ours
    m = re.search(r'<p class="overview-text">Crown Plastic and Paper&#039;s 2-Ply Dinner Napkins.*?bulk 2-ply dinner napkins\.</p>', s, re.S)
    if not m:
        raise RuntimeError('new_products: overview not found')
    s = s[:m.start()] + ''.join('<p class="overview-text">%s</p>' % E(x, quote=False) for x in p['overview']) + s[m.end():]

    # --- key features
    old_feats = ['15x17&quot; Full Dinner Napkin Size', '2-Ply Soft &amp; Absorbent', '3000 per Case', 'White Professional Color',
                 'Table Service Quality', 'Catering &amp; Banquet Appropriate', 'Folds Neatly for Place Settings']
    for o, n in zip(old_feats, p['features']):
        s = _rep(s, '<div class="key-feature-text">%s</div>' % o, '<div class="key-feature-text">%s</div>' % n)

    # --- specifications (two copies: compact table and the styled one)
    for label, old, new in p['spec']:
        compact = '<tr><th class="spec-feature">%s</th><td class="spec-details">%s</td></tr>' % (label, old)
        s = _rep(s, compact, '' if new is None else compact.replace('>%s</td>' % old, '>%s</td>' % new))
        styled = re.compile(r'<tr>\s*<th class="spec-feature">%s</th>\s*<td class="spec-details">%s</td>\s*</tr>' % (re.escape(label), re.escape(old)))
        if not styled.search(s):
            raise RuntimeError('new_products: styled spec row %s' % label)
        s = styled.sub('' if new is None else
                       (lambda m, old=old, new=new: m.group(0).replace('>%s</td>' % old, '>%s</td>' % new)), s)

    # --- applications
    for oimg, otitle, nimg, ntitle in p['apps']:
        s = _rep(s, '2026/02/%s.png' % oimg, '2026/02/%s.png' % nimg)
        s = _rep(s, '<h4 class="application-title">%s</h4>' % otitle, '<h4 class="application-title">%s</h4>' % ntitle)

    # --- FAQs and bulk paragraph
    for oq, nq, oa, na in p['faqs']:
        for o, n in ((oq, nq), (oa, na)):
            s, k = re.subn(r'>\s*%s\s*<' % re.escape(o), lambda m, n=n: '>%s<' % E(n, quote=False), s)
            if not k:
                raise RuntimeError('new_products: FAQ text %r' % o)
    s = _rep(s, 'Crown Plastic and Paper specializes in bulk, wholesale, and distributor-level sourcing of Dinner Napkins. '
                'Soft 2-ply white dinner napkins 15x17 inches sold 3000 per case. Pallet options and mixed-size orders may be available '
                'depending on requirements.', E(p['bulk'], quote=False), 1)
    return s


def add_pages(site):
    """Write site/product/<slug>/index.html for each new product (from the snapshot's base page)."""
    made = []
    src = os.path.join(site, 'product', LUNCH['base'], 'index.html')
    dst_dir = os.path.join(site, 'product', LUNCH['slug'])
    if os.path.exists(src) and not os.path.exists(os.path.join(dst_dir, 'index.html')):
        s = open(src, encoding='utf-8').read()
        if 'data-cpp-upgrade' in s:
            raise RuntimeError('new_products: run before the upgrade pass, on the raw snapshot')
        os.makedirs(dst_dir, exist_ok=True)
        open(os.path.join(dst_dir, 'index.html'), 'w', encoding='utf-8').write(_lunch_page(s))
        made.append(LUNCH['slug'])
    return made


# ------------------------------------------------------------------------------------------------
# Menus and product grids on every page: list Lunch Napkins right after Dinner Napkins.
_MENU_RE = re.compile(r'<li><a href="(?:\.\./)*(?:product/)?dinner-napkins/index\.html">Dinner Napkins</a></li>(?!<li><a href="[^"]*lunch-napkins/)')
_CARD_RE = re.compile(r'(<div class="product-card">\s*<a href="((?:\.\./)*)product/dinner-napkins/index\.html">.*?</a>\s*</div>)', re.S)


def link(s):
    def menu(m):
        href = m.group(0).split('"')[1].replace('dinner-napkins', 'lunch-napkins')
        return m.group(0) + '<li><a href="%s">Lunch Napkins</a></li>' % href
    s = _MENU_RE.sub(menu, s)

    def card(m):
        if re.search(r'class="product-card">\s*<a href="[^"]*product/lunch-napkins/', s):
            return m.group(1)
        c = m.group(1).replace('product/dinner-napkins/', 'product/lunch-napkins/')
        c = re.sub(r'2026/02/[\w.-]+?(-\d+x\d+)?\.png', lambda k: LUNCH['photo'].replace('/wp-content/uploads/', '') + (k.group(1) or '') + '.png', c)
        c = c.replace('alt="Dinner Napkins"', 'alt="Lunch Napkins"').replace('>Dinner Napkins</h2>', '>Lunch Napkins</h2>')
        return m.group(1) + '\n                ' + c

    return _CARD_RE.sub(card, s)
