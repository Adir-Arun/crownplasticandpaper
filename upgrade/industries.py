"""/industries/: who we supply, with the products each kind of business actually orders."""
import html

import geo
from locations import crumbs, faq_block, hero, ld

E = html.escape
UPDATED = '2026-11-04'
F = geo.F

INDUSTRIES = [
    {
        'slug': 'restaurants', 'name': 'Restaurants', 'h1': 'Wholesale Disposables for Restaurants',
        'lead': ('Crown Plastic & Paper supplies restaurants with the takeout and back-of-house disposables they reorder every week: '
                 'to-go containers, deli and portion cups, PET cups and lids, cutlery kits, napkins, foil, gloves and trash liners, '
                 'by the case or pallet from our Houston warehouse.'),
        'need': [('Takeout that travels', 'Black-base containers with lids and hinged clamshells keep entrées hot and sauces separate on delivery apps.'),
                 ('Sauces and sides', 'Portion cups from 1oz to 5.5oz with three lid sizes, and deli containers from 8oz to 64oz for sides and soups.'),
                 ('Front and back of house', 'Gloves for the line, foil and food film for prep, napkins for the dining room, liners for the dumpster run.')],
        'products': ['black-containers', 'round-black-containers', 'black-hinged-containers', 'deli-containers', 'portion-cups', 'portion-cups-lids',
                     'pet-cups', 'pet-cup-lids', 'disposable-cutlery-kits', 'dinner-napkins', 'foil-sheets', 'food-film', 'black-nitrile-gloves', 'trash-liners'],
        'guides': ['takeout-container-sizes', 'portion-cup-sizes', 'pet-cup-sizes', 'disposable-gloves-guide'],
        'faq': [('Can a single restaurant order wholesale?', 'Yes. You can order by the case and mix products on one order. Larger orders move into the 6-pallet and 12-pallet price tiers.'),
                ('What takeout container should a restaurant stock?', 'Most restaurants cover their menu with two or three sizes: a 24oz to 32oz rectangular container for entrées, a 16oz round or deli container for soups and sides, and a hinged container for sandwiches.'),
                ('Do you offer credit terms to restaurants?', 'Yes. Approved accounts get Net 30. Apply online through our credit application.'),
                ('Can I pick up in Houston?', 'Yes. Houston pick-up is available at 7350 Langfield Rd, 77092; send your list first so it is staged when you arrive.')],
    },
    {
        'slug': 'food-trucks', 'name': 'Food trucks', 'h1': 'Wholesale Supplies for Food Trucks',
        'lead': ('Food trucks need compact, fast-moving disposables: paper boat trays, hinged containers, pop-up foil sheets, portion cups, napkins, gloves '
                 'and bags. Crown Plastic & Paper sells them by the case with mixed orders welcome, so a truck can stock a little of everything '
                 'without buying a pallet of each.'),
        'need': [('Serve fast from the window', 'Red plaid paper boat trays from 1/4 lb to 5 lb and pop-up foil sheets for burgers, tacos and burritos.'),
                 ('Small storage', 'Mix cases of different items on one order instead of committing to full pallets.'),
                 ('Grab-and-go extras', 'Portion cups for sauces, cutlery kits, beverage napkins and paper bags for to-go orders.')],
        'products': ['paper-boat-trays', 'black-hinged-containers', 'foil-sheets', 'portion-cups', 'portion-cups-lids', 'disposable-cutlery-kits',
                     'beverage-napkins', 'paper-bags', 'checker-deli-paper-wrap', 'vinyl-gloves', 'black-nitrile-gloves'],
        'guides': ['portion-cup-sizes', 'takeout-container-sizes', 'foil-pan-sizes'],
        'faq': [('What paper boat tray sizes do you carry?', 'Red plaid trays in 1/4 lb, 1/2 lb, 1 lb, 2 lb, 3 lb and 5 lb sizes.'),
                ('Is there a minimum order for food trucks?', 'You can order by the case and mix products. Ask for a quote with the cases you need; pallet tiers lower the price as you grow.'),
                ('What foil sheets work for burgers and burritos?', 'Pop-up foil sheets: 9"×10.75" for burgers and sandwiches, 12"×10.75" for burritos and larger wraps, 500 per box and 6 boxes per case.'),
                ('Can I pick up instead of paying freight?', 'Yes, at our Houston warehouse at 7350 Langfield Rd.')],
    },
    {
        'slug': 'catering', 'name': 'Caterers', 'h1': 'Wholesale Catering Supplies',
        'lead': ('Caterers run on steam table pans, lids, round foil pans, large deli containers, cutlery kits and dinner napkins. '
                 'Crown Plastic & Paper stocks full- and half-size foil pans with fitted lids, 64oz deli containers, PFAS-free bagasse plates and '
                 'containers, and the paper goods that go with them, shipped from Houston in %s.' % F['ship']),
        'need': [('Hot holding', 'Full-size deep pans (50 per case) and half-size deep pans (100 per case) with fitted foil lids; two half pans fill one full-size slot.'),
                 ('Plating and serving', 'Bagasse round plates and hinged containers, 6-piece cutlery kits and 2-ply dinner napkins.'),
                 ('Prep and storage', 'Food film in 12", 18" and 24" widths, foil rolls and 64oz deli containers for bulk prep.')],
        'products': ['deep-steam-table-pans', 'foil-lids-for-steam-table-pans', 'round-foil-pans', 'round-foil-pan-lids', 'deli-containers', 'round-plates',
                     'bagasse-hinged-containers', 'disposable-cutlery-kits', 'dinner-napkins', 'food-film', 'foil-rolls'],
        'guides': ['foil-pan-sizes', 'deli-container-sizes', 'takeout-container-sizes'],
        'faq': [('How many steam table pans are in a case?', 'Full-size deep pans pack 50 per case and half-size deep pans pack 100 per case. Lids are sold separately in matching case packs.'),
                ('Do you have compostable catering options?', 'Yes: PFAS-free bagasse (sugarcane fiber) round plates and hinged containers.'),
                ('Can you deliver before a big event?', 'Orders typically ship in %s. For events, order a week ahead so freight transit is covered.' % F['ship']),
                ('Can I combine pans, plates and napkins on one pallet?', 'Yes. Mixed pallets are welcome.')],
    },
    {
        'slug': 'distributors', 'name': 'Distributors and wholesalers', 'h1': 'Food Service Disposables for Distributors and Wholesalers',
        'lead': ('Crown Plastic & Paper is a stocking supplier for distributors and wholesalers: full and mixed pallets of cups, containers, foil, napkins, '
                 'gloves, bags and janitorial paper, with published spec sheets (case pack, Ti × Hi, cases per pallet) for every item, '
                 'pallet price tiers, and Net 30 for approved accounts.'),
        'need': [('Pallet programs', 'Price tiers for Houston pick-up, 6 pallets delivered and 12 pallets delivered; full truckload is the lowest cost per case.'),
                 ('Clean data for your catalog', 'A spec sheet for every product with case pack, Ti × Hi and cases per pallet, plus our 2026 catalog to share with your customers.'),
                 ('Reliable fill', 'Stock is held in our 60,000 sq ft Houston warehouse and ships in %s.' % F['ship'])],
        'products': ['pet-cups', 'portion-cups', 'deli-containers', 'black-containers', 'foil-rolls', 'deep-steam-table-pans', 'interfold-napkins',
                     'blue-nitrile-gloves', 'paper-bags', 'trash-liners', 'jumbo-roll-tissue', 'register-roll-paper'],
        'guides': ['cases-per-pallet', 'pet-cup-sizes', 'takeout-container-sizes', 'disposable-gloves-guide'],
        'faq': [('Do you sell to distributors outside Texas?', 'Yes. We ship to all 48 contiguous states by LTL freight or full truckload. See our service areas for transit times.'),
                ('What are your pallet price tiers?', 'Pricing tiers are %s.' % F['tiers']),
                ('Can I get spec sheets for my catalog?', 'Yes. Every product page has its spec sheet as a PDF, and the 2026 catalog can be downloaded as a PDF.'),
                ('Do you offer Net 30?', 'Yes, %s.' % F['terms'])],
    },
    {
        'slug': 'convenience-stores-grocery', 'name': 'Convenience stores and grocery', 'h1': 'Wholesale Supplies for Convenience Stores and Grocery',
        'lead': ('Convenience stores, markets and grocery delis order the same core supplies: deli containers, portion cups, food film, foil, '
                 'paper bags, poly bags, register rolls, napkins, gloves and trash liners. Crown Plastic & Paper ships them by the case from Houston, '
                 'with mixed orders welcome.'),
        'need': [('Deli and hot case', 'Deli containers from 8oz to 64oz, hinged containers, foil pans and food film for wrapping.'),
                 ('Checkout', 'Thermal and bond register rolls in 2 1/4" and 3 1/8" widths, kraft and white paper bags, and poly bags.'),
                 ('Store upkeep', 'Gloves, hand roll towels and trash liners.')],
        'products': ['deli-containers', 'black-hinged-containers', 'portion-cups', 'food-film', 'foil-sheets', 'paper-bags', 'poly-bags',
                     'register-roll-paper', 'beverage-napkins', 'vinyl-gloves', 'kraft-white-kitchen-roll-towels', 'trash-liners'],
        'guides': ['deli-container-sizes', 'portion-cup-sizes', 'cases-per-pallet'],
        'faq': [('What register roll sizes do you carry?', 'Thermal rolls in 2 1/4"×50\', 2 1/4"×85\', 3 1/8"×230\' and 3 1/8"×273\', and 3"×165\' bond rolls, 50 rolls per case.'),
                ('Do you sell paper bags by the case?', 'Yes. Kraft and white paper bags, 500 per case, in sizes from 2 lb to 12 lb.'),
                ('Can I mix deli supplies and checkout supplies on one order?', 'Yes. Any mix by the case, and mixed pallets are welcome.'),
                ('How fast do orders ship?', 'Orders typically leave our Houston warehouse in %s.' % F['ship'])],
    },
    {
        'slug': 'schools-facilities', 'name': 'Schools and facilities', 'h1': 'Wholesale Supplies for Schools and Facilities',
        'lead': ('Schools, offices and facilities buy cafeteria disposables and janitorial paper in volume. Crown Plastic & Paper supplies molded fiber '
                 'school trays and PFAS-free bagasse plates, cutlery kits and napkins for the cafeteria, and jumbo roll tissue, wrapped bath tissue, hand roll towels, '
                 'C-fold towels and trash liners for restrooms and custodial teams.'),
        'need': [('Cafeteria', 'Molded fiber school trays, PFAS-free bagasse round plates, cutlery kits and napkins.'),
                 ('Restrooms', 'Jumbo roll tissue (750\' and 1,000\'), individually wrapped bath tissue, hand roll towels and C-fold towels.'),
                 ('Custodial', 'Trash liners in 1.00 to 2.00 mil, gloves and stretch film for storage.')],
        'products': ['school-trays', 'round-plates', 'disposable-cutlery-kits', 'single-multi-and-c-fold-napkins', 'jumbo-roll-tissue',
                     'individual-wrapped-bath-tissue', 'kraft-white-kitchen-roll-towels', 'c-fold-towel', 'trash-liners', 'vinyl-gloves', 'stretch-film'],
        'guides': ['cases-per-pallet', 'disposable-gloves-guide'],
        'faq': [('What are your school trays made of?', 'Molded fiber. Our round plates and hinged containers are PFAS-free bagasse (sugarcane fiber).'),
                ('Do you sell janitorial paper?', 'Yes: jumbo roll tissue, individually wrapped bath tissue, hand roll towels, C-fold and multifold towels.'),
                ('Can schools get Net 30 terms?', 'Yes, %s.' % F['terms']),
                ('Do you deliver by the pallet?', 'Yes. Full and mixed pallets ship by LTL freight from Houston; pricing tiers are %s.' % F['tiers'])],
    },
]


def page(ind, products, origin):
    url = '/industries/%s/' % ind['slug']
    crumb_html, crumb_ld = crumbs([('Home', '/'), ('Who we supply', '/industries/'), (ind['name'], None)], origin)
    facts = [('Ships in', F['ship']), ('Mixed', 'pallets welcome'), ('Net 30', 'after credit approval'), ('Since', F['since'])]
    out = [hero(crumb_html, ind['h1'], ind['lead'], facts), '<div class="cpp-loc" data-cpp-upgrade><div class="cpp-wrap">']
    out.append('<section class="cpp-loc-sec"><h2>What %s need from a supplier</h2><dl class="cpp-facts cpp-facts--1">%s</dl></section>' % (
        E(ind['name'].lower()), ''.join('<div><dt>%s</dt><dd>%s</dd></div>' % (E(a), E(b)) for a, b in ind['need'])))
    cards = []
    for s in ind['products']:
        if s not in products:
            continue
        n, u, d = products[s]
        cards.append('<li><a href="%s"><b>%s</b>%s</a></li>' % (u, E(n), '<span>%s</span>' % E(d[:110]) if d else ''))
    out.append('<section class="cpp-loc-sec"><h2>Products %s order most</h2><ul class="cpp-loc-prods">%s</ul>'
               '<p><a href="/products/">See all products</a> or <a href="/catalog/">flip through the 2026 catalog</a>.</p></section>' % (E(ind['name'].lower()), ''.join(cards)))
    import guides
    gmap = {s: n for s, n, _ in guides.GUIDES}
    out.append('<section class="cpp-loc-sec"><h2>Size guides</h2><ul class="cpp-loc-near">%s</ul></section>' % ''.join(
        '<li><a href="/guides/%s/">%s</a></li>' % (g, E(gmap[g])) for g in ind['guides'] if g in gmap))
    out.append('<section class="cpp-loc-sec"><h2>How ordering works</h2><ol class="cpp-loc-steps"><li><b>Send your list.</b> Products, sizes and case counts through the quote form, by phone, text or WhatsApp %s.</li>'
               '<li><b>Get one wholesale quote.</b> Case and pallet pricing, delivered or Houston pick-up.</li>'
               '<li><b>We ship from Houston.</b> Orders typically leave the warehouse in %s. <a href="/locations/">See transit times to your area.</a></li></ol></section>' % (E(F['whatsapp']), E(F['ship'])))
    others = ''.join('<li><a href="/industries/%s/">%s</a></li>' % (i['slug'], E(i['name'])) for i in INDUSTRIES if i is not ind)
    out.append('<section class="cpp-loc-sec"><h2>Other businesses we supply</h2><ul class="cpp-loc-near">%s</ul></section>' % others)
    out.append('</div></div>')
    out.append(faq_block('%s: common questions' % ind['name'], ind['faq']))
    svc = {'@context': 'https://schema.org', '@type': 'Service', 'name': ind['h1'], 'serviceType': 'Wholesale food service disposables',
           'url': origin + url, 'provider': {'@id': origin + '/#org'}, 'audience': {'@type': 'BusinessAudience', 'audienceType': ind['name']},
           'areaServed': {'@type': 'Country', 'name': 'United States'}}
    out += [crumb_ld, ld(svc)]
    title = '%s | Crown Plastic & Paper' % ind['h1']
    desc = ind['lead'][:155].rsplit(' ', 1)[0].rstrip(',:') + '.'
    return url, title, desc, ''.join(out)


def hub(origin):
    crumb_html, crumb_ld = crumbs([('Home', '/'), ('Who we supply', None)], origin)
    cards = ''.join('<li><a href="/industries/%s/"><b>%s</b><span>%s</span></a></li>' % (i['slug'], E(i['name']), E(i['need'][0][1][:100]))
                    for i in INDUSTRIES)
    body = ''.join([
        hero(crumb_html, 'Who We Supply',
             'Crown Plastic & Paper supplies restaurants, food trucks, caterers, distributors, convenience stores and schools with food service disposables and janitorial paper, by the case and pallet from Houston.',
             [('Ships in', F['ship']), ('Mixed', 'pallets welcome'), ('Net 30', 'after credit approval'), ('Since', F['since'])]),
        '<div class="cpp-loc" data-cpp-upgrade><div class="cpp-wrap">',
        '<section class="cpp-loc-sec"><h2>Pick your business</h2><ul class="cpp-loc-prods">%s</ul></section>' % cards,
        '<section class="cpp-loc-sec"><h2>Helpful links</h2><ul class="cpp-loc-near"><li><a href="/guides/">Size guides</a></li><li><a href="/catalog/">2026 catalog</a></li>'
        '<li><a href="/locations/">Service areas</a></li><li><a href="/applications/">Credit application</a></li></ul></section>',
        '</div></div>', crumb_ld])
    return ('/industries/', 'Who We Supply: Restaurants, Caterers, Distributors and More | Crown Plastic & Paper',
            'Wholesale food service disposables for restaurants, food trucks, caterers, distributors, convenience stores and schools, shipped from Houston.', body)


def all_pages(products, origin):
    return [hub(origin)] + [page(i, products, origin) for i in INDUSTRIES]
