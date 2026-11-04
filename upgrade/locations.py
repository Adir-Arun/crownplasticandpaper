"""Location pages: /locations/, /locations/{state}/, /locations/{state}/{city}/.
Rendered into the site's own header/footer shell by apply.py."""
import html
import json
import re

import location_data
from location_data import TEXAS, METROS, STATES

UPDATED = '2026-11-04'           # bump when location_data.py changes (used as sitemap lastmod)
MIN_STATE_CITIES = 2             # states with fewer cities get no hub page (their city is the page)

E = html.escape


def ld(obj):
    return '<script type="application/ld+json">%s</script>' % json.dumps(obj, ensure_ascii=False).replace('</', '<\\/')


def transit(miles):
    if miles == 0:
        return 'Same or next business day'
    if miles <= 60:
        return 'Next business day'
    if miles <= 300:
        return '1 business day'
    if miles <= 550:
        return '1–2 business days'
    if miles <= 900:
        return '2–3 business days'
    if miles <= 1300:
        return '3–4 business days'
    return '4–5 business days'


class Loc:
    def __init__(self, slug, row):
        (self.name, self.st, self.county, self.miles, self.route, self.food, self.season,
         self.products, self.nearby) = row
        self.slug = slug
        self.state_name, self.state_slug = STATES[self.st]
        self.houston_area = self.miles <= 60

    @property
    def url(self):
        return '/locations/%s/%s/' % (self.state_slug, self.slug)


def all_locations():
    locs = {s: Loc(s, r) for s, r in TEXAS.items()}
    locs.update({s: Loc(s, r) for s, r in METROS.items()})
    return locs


def state_groups(locs):
    groups = {}
    for l in locs.values():
        groups.setdefault(l.state_slug, []).append(l)
    for v in groups.values():
        v.sort(key=lambda l: (l.miles, l.name))
    return groups


def has_hub(state_slug, groups):
    return state_slug == 'texas' or len(groups.get(state_slug, [])) >= MIN_STATE_CITIES


# ------------------------------------------------------------------------------------------------
def crumbs(items, origin):
    """items: [(name, url_or_None)]"""
    vis = '<span aria-hidden="true">/</span>'.join(
        ('<a href="%s">%s</a>' % (u, E(n)) if u else '<span aria-current="page">%s</span>' % E(n)) for n, u in items)
    data = {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': i + 1, 'name': n, **({'item': origin + u} if u else {})} for i, (n, u) in enumerate(items)]}
    return '<nav class="cpp-cat-crumbs" aria-label="Breadcrumb">%s</nav>' % vis, ld(data)


def hero(crumb_html, h1, lead, facts):
    strip = ''.join('<li><b>%s</b> %s</li>' % (E(a), E(b)) for a, b in facts)
    return ('<section class="cpp-cat-hero" data-cpp-upgrade aria-labelledby="cpp-loc-title"><div class="cpp-cat-hero-in"><div class="cpp-cat-hero-copy">'
            '%s<h1 id="cpp-loc-title">%s</h1><p class="cpp-cat-line">%s</p><ul class="cpp-cat-facts">%s</ul>'
            '<div class="cpp-cat-actions"><a class="cpp-hbtn cpp-hbtn--main" href="/get-your-quote/">Request a Quote'
            '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg></a>'
            '<a class="cpp-cat-tel" href="tel:+18449000084">or call (844) 900-0084</a></div>'
            '</div></div></section>') % (crumb_html, E(h1), E(lead), strip)


def faq_block(title, qa):
    items = ''.join('<details class="cpp-faq-item"%s><summary>%s<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 9l6 6 6-6"/></svg></summary><p>%s</p></details>'
                    % (' open' if i == 0 else '', E(q), E(a)) for i, (q, a) in enumerate(qa))
    data = {'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [
        {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in qa]}
    return ('<section class="cpp-faq cpp-cat-faq" aria-labelledby="cpp-loc-faq"><div class="cpp-wrap">'
            '<h2 id="cpp-loc-faq">%s</h2><div class="cpp-faq-list">%s</div></div></section>%s') % (E(title), items, ld(data))


STEPS = ('<ol class="cpp-loc-steps"><li><b>Send your list.</b> Products, sizes and case counts through the quote form, by phone, text or WhatsApp.</li>'
         '<li><b>Get one wholesale quote.</b> Case and pallet pricing for the whole list, with freight to your dock.</li>'
         '<li><b>We ship from Houston.</b> Orders typically leave the warehouse in 24–48 hours.</li></ol>')


# ------------------------------------------------------------------------------------------------
def city_page(l, locs, groups, products, origin, spec_sizes):
    """products: slug -> (name, url, short description)"""
    t = transit(l.miles)
    hub = has_hub(l.state_slug, groups)
    items = [('Home', '/'), ('Locations', '/locations/')]
    if hub:
        items.append((l.state_name, '/locations/%s/' % l.state_slug))
    items.append(('%s, %s' % (l.name, l.st), None))
    crumb_html, crumb_ld = crumbs(items, origin)

    if l.slug == 'houston':
        lead = ('Crown Plastic & Paper is a Houston wholesale distributor of food service disposables. Our warehouse is at 7350 Langfield Rd '
                '(77092), so Houston restaurants, caterers and distributors can pick up or get local delivery, usually the same or next business day.')
        facts = [('Warehouse', 'in Houston, 77092'), ('Pick-up', 'at 7350 Langfield Rd'), ('Ships in', '24–48 hours'), ('Net 30', 'after credit approval')]
    elif l.houston_area:
        lead = ('Crown Plastic & Paper supplies %s restaurants, caterers and distributors from our Houston warehouse %d miles away (%s). '
                'Orders typically arrive the next business day, or you can pick up in Houston.') % (l.name, l.miles, l.route)
        facts = [('%d miles' % l.miles, 'from our warehouse'), ('Next day', 'typical delivery'), ('Pick-up', 'in Houston'), ('Net 30', 'after credit approval')]
    else:
        lead = ('Crown Plastic & Paper ships wholesale food service disposables to %s, %s by the case and pallet. Orders leave our Houston warehouse in '
                '24–48 hours and typically arrive in %s by LTL freight (%s, about %d miles).') % (l.name, l.st, t.lower(), l.route, l.miles)
        facts = [('%s miles' % format(l.miles, ','), 'from Houston'), (t, 'typical transit'), ('LTL freight', 'pallets and mixed pallets'), ('Net 30', 'after credit approval')]
    h1 = 'Wholesale Food Service Disposables in %s, %s' % (l.name, l.st)
    out = [hero(crumb_html, h1, lead, facts), '<div class="cpp-loc" data-cpp-upgrade><div class="cpp-wrap">']

    local = location_data.LOCAL.get(l.slug)
    if local:
        out.append('<section class="cpp-loc-sec"><h2>Food service supply in %s</h2>%s</section>' % (E(l.name), ''.join('<p>%s</p>' % E(x) for x in local)))

    # shipping facts
    rows = [('Ships from', 'Crown warehouse, 7350 Langfield Rd, Houston, TX 77092'),
            ('Distance', 'Local (Houston)' if l.miles == 0 else 'About %s road miles' % format(l.miles, ',')),
            ('Route', l.route),
            ('Typical transit', t + ('' if l.miles == 0 else ' after the order ships')),
            ('How it ships', 'Pick-up or local delivery' if l.houston_area else 'LTL freight: full pallets or mixed pallets, by the case'),
            ('Area', '%s, %s' % (l.county, l.state_name)),
            ('Terms', 'Net 30 after credit approval')]
    out.append('<section class="cpp-loc-sec"><h2>Shipping to %s</h2><dl class="cpp-facts">%s</dl></section>' % (
        E(l.name), ''.join('<div><dt>%s</dt><dd>%s</dd></div>' % (E(a), E(b)) for a, b in rows)))

    # market notes
    out.append('<section class="cpp-loc-sec"><h2>The %s food service market</h2>%s<p><b>Busy seasons:</b> %s</p>%s</section>' % (
        E(l.name), ''.join('<p>%s</p>' % E(x) for x in l.food), E(l.season),
        '' if l.houston_area else '<p>Because freight takes %s, %s buyers usually order a week or two ahead of their busy weeks and keep a pallet of their fastest movers on hand.</p>' % (t.lower(), E(l.name))))

    # products
    cards = []
    for slug in l.products:
        if slug not in products:
            continue
        name, url, desc = products[slug]
        sizes = spec_sizes(slug)
        cards.append('<li><a href="%s"><b>%s</b>%s</a></li>' % (url, E(name), ('<span>%s</span>' % E('Sizes: ' + ', '.join(sizes[:6]) + (' and more' if len(sizes) > 6 else ''))) if sizes else ''))
    out.append('<section class="cpp-loc-sec"><h2>What %s businesses order most</h2><ul class="cpp-loc-prods">%s</ul>'
               '<p><a class="cpp-loc-more" href="/products/">See all products</a></p></section>' % (E(l.name), ''.join(cards)))

    out.append('<section class="cpp-loc-sec"><h2>How ordering works</h2>%s</section>' % STEPS)

    # nearby
    near = [locs[n] for n in l.nearby if n in locs]
    links = ''.join('<li><a href="%s">%s, %s</a> <span>%s</span></li>' % (n.url, E(n.name), n.st, E(transit(n.miles).lower())) for n in near)
    more = ('<li><a href="/locations/%s/">All %s service areas</a></li>' % (l.state_slug, E(l.state_name))) if hub else ''
    out.append('<section class="cpp-loc-sec"><h2>Nearby service areas</h2><ul class="cpp-loc-near">%s%s<li><a href="/locations/">All locations</a></li></ul></section>' % (links, more))
    out.append('</div></div>')

    top = [products[p][0] for p in l.products[:3] if p in products]
    if l.slug == 'houston':
        q1 = ('Can I pick up my order in Houston?', 'Yes. Pick-up is at our warehouse, 7350 Langfield Rd, Houston, TX 77092. Send your list first so the order is staged and ready when you arrive.')
    elif l.houston_area:
        q1 = ('How fast can %s get an order?' % l.name, 'Orders typically ship from our Houston warehouse in 24–48 hours, and %s is about %d miles away (%s), so most deliveries arrive the next business day. You can also pick up in Houston.' % (l.name, l.miles, l.route))
    else:
        q1 = ('How long does shipping from Houston to %s take?' % l.name, 'Orders typically leave our Houston warehouse in 24–48 hours. From there, LTL freight to %s usually takes %s (about %s miles via %s).' % (l.name, t.lower(), format(l.miles, ','), l.route.split(',')[0]))
    qa = [q1,
          ('What do %s food service businesses buy most?' % l.name, '%s are among the most requested, along with whatever the season calls for. %s' % (', '.join(top), l.season)),
          ('Can I mix products on one %s order?' % l.name, 'Yes. Combine any Crown products on the same order and pallet. Pricing is by the case and pallet in three tiers: Houston pick-up, delivered 6 pallets and delivered 12 pallets.'),
          ('Do %s businesses get Net 30 terms?' % l.name, 'Yes, Net 30 is available after credit approval. Apply online with the credit application and attach your tax resale certificate.')]
    out.append(faq_block('%s buyer questions' % l.name, qa))

    service = {'@context': 'https://schema.org', '@type': 'Service', 'serviceType': 'Wholesale food service disposables distribution',
               'name': 'Wholesale food service disposables in %s, %s' % (l.name, l.st), 'provider': {'@id': origin + '/#org'},
               'areaServed': {'@type': 'City', 'name': l.name, 'containedInPlace': {'@type': 'State', 'name': l.state_name}},
               'url': origin + l.url}
    out.append(ld(service) + crumb_ld)
    title = 'Wholesale Food Service Disposables in %s, %s | Crown' % (l.name, l.st)
    if l.houston_area:
        desc = 'Wholesale cups, containers, foil, napkins and gloves for %s, %s from our Houston warehouse %s. Pick-up or next-day delivery, Net 30.' % (
            l.name, l.st, 'on Langfield Rd' if l.slug == 'houston' else '%d miles away' % l.miles)
    else:
        desc = 'Wholesale cups, containers, foil, napkins and gloves shipped to %s, %s from Houston: %s by LTL, by the case or pallet. Net 30.' % (l.name, l.st, t.lower())
    return title, desc[:158], ''.join(out)


def state_page(state_slug, cities, groups, origin, products, spec_sizes):
    name = cities[0].state_name
    crumb_html, crumb_ld = crumbs([('Home', '/'), ('Locations', '/locations/'), (name, None)], origin)
    near, far = cities[0].miles, cities[-1].miles
    if state_slug == 'texas':
        lead = ('Crown Plastic & Paper ships wholesale food service disposables across Texas from our Houston warehouse: next-day across Greater Houston, '
                'about one business day to Austin, San Antonio and Dallas–Fort Worth, and two to three days to El Paso.')
    else:
        lead = ('Crown Plastic & Paper ships wholesale food service disposables to %s from our Houston warehouse by the case and pallet. '
                'Typical LTL transit is %s to %s and %s to %s.') % (name, transit(near).lower(), cities[0].name, transit(far).lower(), cities[-1].name)
    facts = [('%d cities' % len(cities), 'served in %s' % name), ('From Houston', 'one warehouse, one quote'), ('Net 30', 'after credit approval')]
    out = [hero(crumb_html, 'Wholesale Food Service Disposables in %s' % name, lead, facts), '<div class="cpp-loc" data-cpp-upgrade><div class="cpp-wrap">']
    rows = ''.join('<tr><td><a href="%s">%s</a></td><td>%s</td><td>%s</td><td>%s</td></tr>' % (
        c.url, E(c.name), 'Local' if c.miles == 0 else format(c.miles, ','), E(transit(c.miles)), E(c.route.split(',')[0])) for c in cities)
    out.append('<section class="cpp-loc-sec"><h2>Shipping times from Houston</h2><div class="cpp-skus-scroll" tabindex="0" role="region" aria-label="Shipping times">'
               '<table class="cpp-skus-table"><thead><tr><th scope="col">City</th><th scope="col">Road miles</th><th scope="col">Typical transit</th><th scope="col">Route</th></tr></thead>'
               '<tbody>%s</tbody></table></div><p class="cpp-loc-note">Transit is a typical LTL estimate after the order ships; orders leave Houston in 24–48 hours.</p></section>' % rows)
    full = len(cities) <= 4   # small states: give each city its full notes so the page stands on its own
    notes = ''.join('<li><a href="%s"><b>%s</b></a> %s%s</li>' % (
        c.url, E(c.name), E(' '.join(c.food) if full else c.food[0]), (' <i>Busy seasons:</i> ' + E(c.season)) if full else '') for c in cities)
    out.append('<section class="cpp-loc-sec"><h2>Markets we serve in %s</h2><ul class="cpp-loc-notes">%s</ul></section>' % (E(name), notes))
    counts = {}
    for c in cities:
        for i, p in enumerate(c.products):
            counts[p] = counts.get(p, 0) + 10 - i
    top = [p for p, _ in sorted(counts.items(), key=lambda x: -x[1]) if p in products][:6]
    if top:
        out.append('<section class="cpp-loc-sec"><h2>Most ordered in %s</h2><ul class="cpp-loc-prods">%s</ul></section>' % (E(name), ''.join(
            '<li><a href="%s"><b>%s</b>%s</a></li>' % (products[p][1], E(products[p][0]),
                ('<span>%s</span>' % E('Sizes: ' + ', '.join(spec_sizes(p)[:6]))) if spec_sizes(p) else '') for p in top)))
    out.append('<section class="cpp-loc-sec"><h2>How ordering works</h2>%s</section>' % STEPS)
    others = ''.join('<li><a href="/locations/%s/">%s</a></li>' % (s, E(groups[s][0].state_name))
                     for s in sorted(groups) if s != state_slug and has_hub(s, groups))
    out.append('<section class="cpp-loc-sec"><h2>Other service areas</h2><ul class="cpp-loc-near">%s'
               '<li><a href="/locations/">All locations</a></li></ul></section>' % others)
    out.append('</div></div>')
    qa = [('How long does shipping from Houston to %s take?' % name,
           'Orders leave our Houston warehouse in 24\u201348 hours. Typical LTL transit is %s to %s and %s to %s.' % (
               transit(near).lower(), cities[0].name, transit(far).lower(), cities[-1].name) if state_slug != 'texas' else
           'Orders leave our Houston warehouse in 24\u201348 hours. Greater Houston usually gets them the next business day; Austin, San Antonio and Dallas\u2013Fort Worth about one business day after shipping; El Paso two to three.'),
          ('Do you ship full pallets and mixed pallets to %s?' % name,
           'Both. Order by the case and mix products on the same pallet, or order full pallets. Pricing tiers are Houston pick-up, delivered 6 pallets and delivered 12 pallets.'),
          ('Can %s businesses open a Net 30 account?' % name,
           'Yes. Net 30 is available after credit approval. Apply with the online credit application and attach your tax resale certificate.')]
    out.append(faq_block('%s buyer questions' % name, qa) + crumb_ld)
    title = 'Wholesale Food Service Disposables in %s | Crown Plastic & Paper' % name
    desc = 'Wholesale cups, containers, foil, napkins and gloves shipped across %s from our Houston warehouse. Shipping times by city, Net 30.' % name
    return title, desc[:158], ''.join(out)


def hub_page(locs, groups, origin):
    crumb_html, crumb_ld = crumbs([('Home', '/'), ('Locations', None)], origin)
    lead = ('Every Crown Plastic & Paper order ships from one warehouse in Houston, Texas. We deliver across Greater Houston, ship by the case and pallet '
            'across Texas, and send LTL freight to food service businesses throughout the South, Southeast, Midwest and Mountain West.')
    facts = [('%d cities' % len(locs), 'with shipping details'), ('%d states' % len(groups), 'served from Houston'), ('24–48 hrs', 'to leave the warehouse')]
    out = [hero(crumb_html, 'Service Areas: Wholesale Food Service Disposables Shipped from Houston', lead, facts),
           '<div class="cpp-loc" data-cpp-upgrade><div class="cpp-wrap">']
    order = ['texas'] + sorted((s for s in groups if s != 'texas'), key=lambda s: groups[s][0].miles)
    blocks = []
    for s in order:
        cities = groups[s]
        head = ('<a href="/locations/%s/">%s</a>' % (s, E(cities[0].state_name))) if has_hub(s, groups) else E(cities[0].state_name)
        blocks.append('<div class="cpp-loc-state"><h3>%s</h3><ul>%s</ul></div>' % (head, ''.join(
            '<li><a href="%s">%s</a> <span>%s</span></li>' % (c.url, E(c.name), E(transit(c.miles).lower())) for c in cities)))
    out.append('<section class="cpp-loc-sec"><h2>Cities we serve</h2><div class="cpp-loc-states">%s</div>'
               '<p class="cpp-loc-note">Not listed? We ship to most of the continental US. <a href="/get-your-quote/">Send your list</a> and we\'ll quote freight to your dock.</p></section>' % ''.join(blocks))
    out.append('<section class="cpp-loc-sec"><h2>How ordering works</h2>%s</section>' % STEPS)
    out.append('</div></div>' + crumb_ld)
    title = 'Service Areas | Wholesale Food Service Disposables from Houston | Crown'
    desc = 'Where Crown Plastic & Paper ships: Greater Houston, all of Texas and %d states across the South, Midwest and West. Transit times by city.' % (len(groups) - 1)
    return title, desc[:158], ''.join(out)


def all_pages(products, origin, spec_sizes):
    """-> list of (url, title, description, body_html, extra_head_ld)"""
    locs = all_locations()
    groups = state_groups(locs)
    pages = [('/locations/',) + hub_page(locs, groups, origin)]
    for s, cities in groups.items():
        if has_hub(s, groups):
            pages.append(('/locations/%s/' % s,) + state_page(s, cities, groups, origin, products, spec_sizes))
    for l in locs.values():
        pages.append((l.url,) + city_page(l, locs, groups, products, origin, spec_sizes))
    redirects = [('/locations/%s/' % s, cities[0].url) for s, cities in groups.items() if not has_hub(s, groups)]
    return pages, redirects, locs
