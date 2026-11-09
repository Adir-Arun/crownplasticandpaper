"""SEO + GEO layer (from the AR Unlimited Supply SEO/GEO strategy, applied to the Crown site):
one set of facts, quotable answers, real spec tables in HTML, FAQ + Organization schema, llms.txt."""
import html
import json
import re

ORIGIN = 'https://crownplasticandpaper.com'

# Single source of truth for every fact the site states.
FACTS = {
    'name': 'Crown Plastic & Paper',
    'phone': '(844) 900-0084', 'phone_e164': '+18449000084',
    'text': '(713) 597-5320', 'whatsapp': '(713) 597-5320',
    'email': 'info@crownplasticandpaper.com',
    'street': '7350 Langfield Rd', 'city': 'Houston', 'region': 'TX', 'zip': '77092',
    'terms': 'Net 30 after credit approval', 'since': '2021',
    'tiers': 'Houston pick-up, delivered 6 pallets, and delivered 12 pallets',
    'ship': '1–2 business days', 'warehouse': '60,000 sq ft', 'states': '48',
}
F = FACTS

QUICK_ANSWER = (
    'Crown Plastic & Paper is a Houston, Texas wholesale distributor of food service disposables: cups, '
    'containers, foil pans, napkins, gloves, bags and janitorial supplies, sold by the case and pallet to '
    'distributors, restaurants and food service businesses in %s states. Orders ship from a %s Houston '
    'warehouse in %s, and approved accounts get Net 30 terms. In business since %s.'
    % (F['states'], F['warehouse'], F['ship'], F['since']))

# Vague FAQ answers on the WordPress pages -> specific, quotable ones (same questions).
FAQ_REWRITES = {
    'You can place an order by contacting our sales team directly via phone, email, or through our website.':
        'Send your product list through the Get a Quote form, call %s, text or WhatsApp %s, or email %s. '
        'You get one wholesale quote for the whole list.' % (F['phone'], F['whatsapp'], F['email']),
    'Yes, we specialize in wholesale distribution and provide competitive pricing for bulk orders.':
        'Yes. Pricing is by the case and pallet in three tiers: %s. Mixed products can share a pallet.' % F['tiers'],
    'Yes, credit terms may be available for approved business accounts.':
        'Yes. Approved business accounts get Net 30 terms. Apply with the online credit application; you can '
        'attach your tax resale certificate there.',
    'We supply products nationwide, ensuring fast and efficient delivery.':
        'Nationwide: we ship to customers in %s states by LTL freight from our Houston, TX warehouse at %s. '
        'Houston-area customers can also pick up.' % (F['states'], F['street']),
    'Delivery times depend on order size and location, but we strive for quick turnaround and reliable shipping.':
        'Orders typically ship from Houston in %s. Transit time after that depends on distance and freight '
        'carrier.' % F['ship'],
    'We accept standard payment methods including bank transfers, cards, and approved business payment terms.':
        'Bank transfer, card, and %s.' % F['terms'],
}


def faq_rewrite(s):
    for old, new in FAQ_REWRITES.items():
        s = s.replace(old, html.escape(new, quote=False))
    return s


# ---------------------------------------------------------------------------------------------------
# Organization + WebSite on every page (the homepage and About had none)
ORG_LD = {
    '@context': 'https://schema.org',
    '@graph': [
        {'@type': ['Organization', 'WholesaleStore'], '@id': ORIGIN + '/#org', 'name': F['name'],
         'legalName': 'Crown Paper And Plastic Inc',
         'alternateName': ['Crown Paper And Plastic Inc', 'Crown Plastic and Paper'],
         'url': ORIGIN + '/', 'logo': ORIGIN + '/icon-512.png',
         'image': ORIGIN + '/wp-content/uploads/2026/01/img_crown_The_Trusted_Choice_of_Distributors.png',
         'telephone': '+1-844-900-0084', 'email': F['email'],
         'address': {'@type': 'PostalAddress', 'streetAddress': F['street'], 'addressLocality': F['city'],
                     'addressRegion': F['region'], 'postalCode': F['zip'], 'addressCountry': 'US'},
         'geo': {'@type': 'GeoCoordinates', 'latitude': 29.8506, 'longitude': -95.5017},
         'areaServed': [{'@type': 'State', 'name': 'Texas'}, {'@type': 'Country', 'name': 'United States'}],
         'knowsAbout': ['food service disposables', 'deli containers', 'foil pans', 'nitrile gloves', 'plastic cups', 'takeout packaging'],
         'sameAs': ['https://www.cybo.com/US-biz/crown-paper-and-plastic-inc', 'https://www.linkedin.com/company/crown-plastic-paper/'],
         'foundingDate': F['since'], 'description': QUICK_ANSWER},
        {'@type': 'WebSite', '@id': ORIGIN + '/#website', 'url': ORIGIN + '/', 'name': F['name'],
         'publisher': {'@id': ORIGIN + '/#org'}},
    ],
}


def org_ld(s):
    if '/#website"' in s or '</head>' not in s:
        return s
    return s.replace('</head>', '<script type="application/ld+json">%s</script>\n</head>' % json.dumps(ORG_LD, ensure_ascii=False), 1)


def ld(obj):
    return '<script type="application/ld+json">%s</script>' % json.dumps(obj, ensure_ascii=False).replace('</', '<\\/')


# ---------------------------------------------------------------------------------------------------
# Product data from the spec map (variations as listed on each product page)
SIZE_KEYS = ['size', 'size-oz', 'sheet-size', 'roll-size', 'bag-size', 'tray-size-capacity', 'size-bag-capacity',
             'pan-size', 'lid-size', 'capacity', 'roll-length', 'length', 'size-dimensions']
LABELS = {
    'size': 'Size', 'size-oz': 'Size', 'sheet-size': 'Sheet size', 'roll-size': 'Roll size', 'bag-size': 'Bag size',
    'tray-size-capacity': 'Tray size', 'size-bag-capacity': 'Bag size', 'pan-size': 'Pan size', 'lid-size': 'Lid size',
    'capacity': 'Capacity', 'roll-length': 'Roll length', 'length': 'Length', 'size-dimensions': 'Dimensions',
    'color': 'Color', 'design-color': 'Design', 'color-design': 'Design', 'shape': 'Shape', 'material': 'Material',
    'compartments': 'Compartments', 'kit-type': 'Kit', 'pcs': 'Pieces', 'weight-class': 'Weight', 'weight': 'Weight',
    'thickness': 'Thickness', 'gauge': 'Gauge', 'ply': 'Ply', 'roll-type': 'Type', 'lid-type': 'Lid type',
    'napkin-type': 'Type', 'paper-type': 'Paper', 'product-type': 'Type',
    'pack-size': 'Case pack', 'pack-configuration': 'Pack', 'ti-x-hi': 'Ti × Hi', 'cases-pallets': 'Cases / pallet',
}
LAST = ['pack-size', 'pack-configuration', 'ti-x-hi', 'cases-pallets']


def _num(v):
    v = str(v or '').lower()
    m = re.match(r'^(\d+)/(\d+)', v)
    if m:
        return int(m.group(1)) / int(m.group(2))
    m = re.match(r'^(\d+(?:\.\d+)?)', v)
    if m:
        return float(m.group(1))
    words = {'small': 1001, 'medium': 1002, 'large': 1003, 'extra large': 1004}
    return words.get(v, 2000)


def size_of(entry):
    for k in SIZE_KEYS:
        if entry['match'].get(k):
            return entry['match'][k]
    return ''


def product_sizes(entries):
    seen, out = set(), []
    for e in sorted(entries, key=lambda e: _num(size_of(e))):
        v = size_of(e)
        if v and v not in seen and v != 'N/A':
            seen.add(v)
            out.append(v)
    return out


def _uniq(vals):
    out = []
    for v in vals:
        if v and v != 'N/A' and v not in out:
            out.append(v)
    return out


def spec_table(slug, entries, title):
    """Quick facts + a real <table> of every variation, with its spec sheet."""
    if not entries or not entries[0]['match']:
        return ''
    keys = []
    for e in entries:
        for k in e['match']:
            if k not in keys:
                keys.append(k)
    # drop columns that say the same thing on every row (shown in quick facts instead)
    vary = [k for k in keys if len(set(e['match'].get(k, '') for e in entries)) > 1 or k in LAST]
    vary = [k for k in vary if k not in LAST] + [k for k in LAST if k in vary]
    rows = sorted(entries, key=lambda e: (_num(size_of(e)), json.dumps(e['match'], sort_keys=True)))
    head = ''.join('<th scope="col">%s</th>' % html.escape(LABELS.get(k, k.replace('-', ' ').title())) for k in vary)
    body = ''.join('<tr>%s<td><a href="/spec-sheets/%s" target="_blank" rel="noopener">PDF</a></td></tr>' % (
        ''.join('<td>%s</td>' % html.escape(e['match'].get(k, '') or '—') for k in vary), html.escape(e['file']))
        for e in rows)
    constant = [(k, entries[0]['match'][k]) for k in keys if k not in vary and entries[0]['match'].get(k) not in ('', 'N/A')]
    sizes = product_sizes(entries)
    packs = _uniq(e['match'].get('pack-size') or e['match'].get('pack-configuration', '').split(' (')[0] for e in entries)
    pallets = sorted({int(e['match']['cases-pallets']) for e in entries if str(e['match'].get('cases-pallets', '')).isdigit()})
    facts = []
    if sizes:
        facts.append(('Sizes', ', '.join(sizes)))
    facts += [(LABELS.get(k, k.title()), v) for k, v in constant if k not in LAST]
    if packs:
        facts.append(('Case pack', ', '.join(packs)))
    if pallets:
        facts.append(('Cases per pallet', str(pallets[0]) if len(pallets) == 1 else '%d–%d' % (pallets[0], pallets[-1])))
    facts += [('Ships from', 'Houston, TX in %s' % F['ship']), ('Terms', F['terms'])]
    dl = ''.join('<div><dt>%s</dt><dd>%s</dd></div>' % (html.escape(a), html.escape(b)) for a, b in facts)
    return ('<section class="cpp-skus" data-cpp-upgrade aria-labelledby="cpp-skus-title">'
            '<h2 id="cpp-skus-title" class="cpp-skus-h">%s at a glance</h2><dl class="cpp-facts">%s</dl>'
            '<div class="cpp-skus-scroll" tabindex="0" role="region" aria-label="%s sizes and case packs">'
            '<table class="cpp-skus-table"><caption>%d options · every option has its own spec sheet</caption>'
            '<thead><tr>%s<th scope="col">Spec sheet</th></tr></thead><tbody>%s</tbody></table></div></section>'
            ) % (html.escape(title), dl, html.escape(title), len(rows), head, body)


def insert_after_specs_heading(s, block, div_span):
    m = re.search(r'<h3 class="elementor-heading-title[^"]*">\s*Specifications\s*</h3>', s)
    if not m:
        return s
    start = s.rfind('<div class="elementor-element ', 0, m.start())
    if start < 0:
        return s
    end = div_span(s, start)[1]
    return s[:end] + block + s[end:]


# ---------------------------------------------------------------------------------------------------
# Category pages: answer-first facts strip + category FAQ (visible text = FAQPage data)
def category_block(cat_name, products):
    """products: [(name, url, sizes[])] in page order."""
    with_sizes = [(n, u, sz) for n, u, sz in products if sz]
    qa = []
    if with_sizes:
        lines = '; '.join('%s: %s' % (n, ', '.join(sz[:8]) + (' and more' if len(sz) > 8 else '')) for n, u, sz in with_sizes[:6])
        qa.append(('What %s sizes do you stock?' % cat_name.lower(), '%s. Every size has its own spec sheet on the product page.' % lines))
    qa += [
        ('Can I mix products in one order?', 'Yes. You can combine %s with any other Crown products on the same order and pallet.'
         % cat_name.lower()),
        ('How is wholesale pricing set?', 'By the case and pallet, in three tiers: %s. Request a quote with your list to get pallet pricing.' % F['tiers']),
        ('How fast do orders ship?', 'Orders typically ship from our Houston, TX warehouse in %s, by LTL freight to customers in %s states. '
         'Houston-area customers can also pick up.' % (F['ship'], F['states'])),
        ('Do you offer Net 30 terms?', 'Yes, %s. Apply online with the credit application.' % F['terms']),
    ]
    items = ''.join('<details class="cpp-faq-item"%s><summary>%s<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 9l6 6 6-6"/></svg></summary><p>%s</p></details>'
                    % (' open' if i == 0 else '', html.escape(q), html.escape(a)) for i, (q, a) in enumerate(qa))
    faq_data = {'@context': 'https://schema.org', '@type': 'FAQPage',
                'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in qa]}
    return ('<section class="cpp-faq cpp-cat-faq" data-cpp-upgrade aria-labelledby="cpp-cat-faq-title"><div class="cpp-wrap">'
            '<h2 id="cpp-cat-faq-title">%s: buyer questions</h2><div class="cpp-faq-list">%s</div></div></section>%s'
            ) % (html.escape(cat_name), items, ld(faq_data))


FACT_STRIP = ('<ul class="cpp-cat-facts" aria-label="Ordering at a glance">'
              '<li><b>Net 30</b> after credit approval</li><li><b>Ships in %s</b> from Houston</li>'
              '<li><b>3 price tiers</b> pick-up, 6 or 12 pallets</li><li><b>Mixed pallets</b> welcome</li></ul>'
              ) % F['ship']


# ---------------------------------------------------------------------------------------------------
ROBOTS = """# Crown Plastic & Paper
User-agent: *
Allow: /
Disallow: /api/
Disallow: /upgrade/search-index.json

# AI search and assistants: welcome
User-agent: GPTBot
User-agent: OAI-SearchBot
User-agent: ChatGPT-User
User-agent: PerplexityBot
User-agent: Perplexity-User
User-agent: ClaudeBot
User-agent: Claude-SearchBot
User-agent: Claude-User
User-agent: Google-Extended
User-agent: Applebot-Extended
User-agent: Bingbot
User-agent: Amazonbot
User-agent: meta-externalagent
Allow: /
Disallow: /api/
Disallow: /upgrade/search-index.json

Sitemap: %s/sitemap.xml
""" % ORIGIN


def llms_txt(categories, products, guides, spec_map, full=False):
    """categories/products/guides: [(name, url, desc)]."""
    out = ['# %s' % F['name'], '', '> ' + QUICK_ANSWER, '',
           '## Facts', '',
           '- Business: wholesale distributor of disposable food service packaging and janitorial supplies',
           '- Warehouse: %s, %s, %s %s, USA (%s)' % (F['street'], F['city'], F['region'], F['zip'], F['warehouse']),
           '- Phone: %s · Text and WhatsApp: %s · Email: %s' % (F['phone'], F['whatsapp'], F['email']),
           '- Customers: distributors, wholesalers, restaurant groups, caterers, schools, hospitals, cash and carry; %s states' % F['states'],
           '- In business since: %s' % F['since'],
           '- Mixed products can share an order and pallet',
           '- Pricing: by case and pallet, three tiers: %s; quote on request, no public prices' % F['tiers'],
           '- Terms: %s' % F['terms'],
           '- Shipping: typically ships from Houston in %s; LTL freight nationwide; Houston pick-up available' % F['ship'],
           '- Spec sheets: a PDF for every size on each product page',
           '', '## Ordering', '',
           '- [Get a quote](%s/get-your-quote/): send a product list, get one wholesale quote' % ORIGIN,
           '- [Credit application](%s/applications/): apply for Net 30 terms' % ORIGIN,
           '- [Contact](%s/contact-us/)' % ORIGIN,
           '- [FAQ](%s/faqs/)' % ORIGIN,
           '', '## Product categories', '']
    out += ['- [%s](%s%s): %s' % (n, ORIGIN, u, d) for n, u, d in categories]
    out += ['', '## Products', '']
    for n, u, d in products:
        slug = u.strip('/').split('/')[-1]
        sizes = product_sizes(spec_map.get(slug, []))
        line = '- [%s](%s%s)' % (n, ORIGIN, u)
        if sizes:
            line += ': sizes %s' % ', '.join(sizes)
        if full and d:
            line += ('; ' if sizes else ': ') + d
        out.append(line)
    if full:
        out += ['', '## Spec sheets', '']
        for slug, entries in spec_map.items():
            for e in entries:
                out.append('- %s %s: %s/spec-sheets/%s' % (slug.replace('-', ' '), e.get('label', ''), ORIGIN, e['file']))
    out += ['', '## Guides', '']
    out += ['- [%s](%s%s)' % (n, ORIGIN, u) for n, u, d in guides]
    return '\n'.join(out) + '\n'
