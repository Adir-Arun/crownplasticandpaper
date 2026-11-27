"""Buying guides for distributors, multi-unit buyers and specific kinds of food business.

Data-driven: each guide is a dict; numbers in spec tables come from assets/spec-map.json.
Written for Crown's angle (nationwide pallet orders from Houston); topics and wording are
deliberately different from the AR Unlimited Supply guides so the two sites don't compete.
"""
import html

import geo
from guides import table, _pal, _tihi, entries, link

E = html.escape
F = geo.F
EX = 'Example figures for illustration only, not Crown quotes. Ask for current pricing.'


def spec_rows(spec, slug):
    out = []
    for e in spec.get(slug, []):
        a = e.get('match') or {}
        if not a:
            continue
        out.append([E(e.get('label') or ''), E(a.get('pack-size', '—')), _tihi(a), _pal(a)])
    return out


def _para(items):
    html_, lis = [], []
    for s in items:
        if s.startswith('- '):
            lis.append('<li>%s</li>' % s[2:])
            continue
        if lis:
            html_.append('<ul class="cpp-guide-list">%s</ul>' % ''.join(lis))
            lis = []
        html_.append('<p>%s</p>' % s)
    if lis:
        html_.append('<ul class="cpp-guide-list">%s</ul>' % ''.join(lis))
    return ''.join(html_)


def _builder(g):
    def fn(spec, products):
        sec = []
        for h2, body in g['sections']:
            if isinstance(body, tuple) and body[0] == 'spec':
                rows = spec_rows(spec, body[1])
                if not rows:
                    continue
                inner = table(body[2], ['Item', 'Case pack', 'Ti × Hi', 'Cases / pallet'], rows) + \
                    '<p class="cpp-guide-note">See the %s page for spec sheets.</p>' % link(products, body[1])
            elif isinstance(body, tuple) and body[0] == 'table':
                inner = table(body[1], body[2], [[E(c) for c in r] for r in body[3]], E(body[4]) if len(body) > 4 else '')
            else:
                inner = _para(body)
            sec.append('<section class="cpp-loc-sec"><h2>%s</h2>%s</section>' % (E(h2), inner))
        if g.get('sources'):
            sec.append('<section class="cpp-loc-sec"><h2>Sources</h2><ul class="cpp-guide-list">%s</ul>%s</section>' % (
                ''.join('<li><a href="%s" rel="noopener" target="_blank">%s</a></li>' % (u, E(t)) for t, u in g['sources']),
                '<p class="cpp-guide-note">%s</p>' % E(g['note']) if g.get('note') else ''))
        elif g.get('note'):
            sec.append('<p class="cpp-guide-note">%s</p>' % E(g['note']))
        return (g['title'], g['desc'], g['h1'], g['answer'], g['facts'], ''.join(sec), g['faq'], g['related'])
    return fn


T = F['tiers']
S = F['ship']

BUYER = [
    # ================================================================ distributors & wholesale buying
    {'slug': 'pallet-price-tiers', 'group': 'Distributors and pallet buying', 'short': 'Pallet price tiers (6 and 12 pallets)',
     'title': 'Pallet Price Tiers: Ordering 6 or 12 Pallets of Disposables',
     'desc': 'How tiered pallet pricing works for food service disposables: Houston pick-up, 6-pallet and 12-pallet delivered tiers, mixed pallets and when to move up a tier.',
     'h1': 'How tiered pallet pricing works: pick-up, 6 pallets and 12 pallets',
     'answer': 'Crown prices disposables in three tiers: %s. The more pallets on one delivery, the lower the price per case, because freight and handling are shared across more product. Pallets can be mixed, so a 6- or 12-pallet order can combine cups, containers, foil, gloves and paper.' % T,
     'facts': [('3', 'price tiers'), ('6 / 12', 'pallet delivered tiers'), ('Mixed', 'pallets welcome'), ('48', 'states served')],
     'sections': [('Which tier fits you', [
         '- <b>Houston pick-up:</b> local buyers who collect with their own truck, any quantity by the case.',
         '- <b>6 pallets delivered:</b> regional distributors, restaurant groups and c-store chains reordering monthly.',
         '- <b>12 pallets delivered:</b> distributors filling a warehouse; about half a 53-foot trailer floor.',
         'If you sit just under a tier, compare the price drop on the next tier with the cost of carrying the extra stock for a few more weeks. Fast-moving items such as gloves and cups usually justify moving up.']),
         ('Building a tiered order', [
         'Start with the items you sell or use every week, fill whole pallets of those, then use the last pallet positions for slower items as a mixed pallet. Our cases-per-pallet guide shows Ti × Hi for every SKU so you can plan full layers.'])],
     'faq': [('Can the 6 pallets be different products?', 'Yes. Each pallet can be a different product, and pallets can be mixed.'),
             ('Do you ship tiered orders outside Texas?', 'Yes, to customers in %s states by LTL or truckload freight from Houston.' % F['states']),
             ('How fast do pallet orders ship?', 'Orders typically leave our Houston warehouse in %s.' % S)],
     'related': ['black-nitrile-gloves', 'pet-cups', 'deli-containers', 'foil-sheets']},

    {'slug': 'how-many-pallets-on-a-truck', 'group': 'Distributors and pallet buying', 'short': 'Pallets per truckload',
     'title': 'How Many Pallets Fit on a 53-Foot Truck? | Crown Plastic & Paper',
     'desc': 'A 53-foot dry van holds about 26 standard pallets single-stacked. What limits a load of disposables (space or weight), stacking, and how to plan a full truckload.',
     'h1': 'How many pallets fit on a 53-foot truck?',
     'answer': 'A 53-foot dry van trailer holds about 26 standard 48 × 40 inch pallets on the floor, two across and 13 deep. Disposables such as cups, containers and napkins are light and bulky, so a load usually fills the floor before it reaches the weight limit. Dense items such as register rolls or foil rolls can hit weight first.',
     'facts': [('26', 'floor pallets, 53 ft van'), ('48 × 40', 'standard pallet'), ('2 × 13', 'loading pattern'), ('Mixed', 'loads welcome')],
     'sections': [('Space or weight: which runs out first', [
         'Paper cups, foam alternatives, containers and napkins weigh little per pallet, so 26 pallets is usually the limit. Rolls of foil, film and register paper are heavy, so a load of those can reach the legal weight limit with fewer pallets. Mixing light and heavy items helps use both space and weight.',
         'Double-stacking is possible only when pallets are built to bear weight and the carrier agrees; many disposables cases crush, so assume single-stacked unless told otherwise.']),
         ('Smaller trucks', [
         '- 48-foot trailer: about 24 floor pallets.',
         '- 26-foot box truck: about 12 floor pallets.',
         '- Sprinter-type van: usually 2 to 4 pallets, depending on the model.']),
         ('Planning a full load', [
         'List your top items by monthly use, round each to full pallets, and fill the remaining positions with mixed pallets. Our 12-pallet tier fills about half a 53-foot trailer floor.'])],
     'faq': [('How many pallets fit on a 53 ft trailer?', 'About 26 standard 48 × 40 pallets single-stacked.'),
             ('How many pallets fit on a 26 ft box truck?', 'About 12 standard pallets on the floor.'),
             ('Can I order a full truckload of mixed disposables?', 'Yes. Mixed truckloads are common for distributors.')],
     'related': ['pet-cups', 'interfold-napkins', 'foil-rolls', 'register-roll-paper']},

    {'slug': 'build-a-mixed-pallet', 'group': 'Distributors and pallet buying', 'short': 'How to build a mixed pallet',
     'title': 'How to Build a Mixed Pallet of Food Service Disposables',
     'desc': 'Plan a mixed pallet of cups, containers, foil, gloves and paper: heavy cases on the bottom, full layers, height limits and what to tell your supplier.',
     'h1': 'How to build a mixed pallet of disposables',
     'answer': 'A mixed pallet combines several products on one pallet so you pay one freight charge. Put heavy, strong cases (foil rolls, register rolls, gloves) at the bottom, light and crushable cases (cups, containers, napkins) on top, keep it within the pallet footprint and under the carrier height limit, and order in full layers where you can.',
     'facts': [('1', 'freight charge'), ('Heavy', 'cases at the bottom'), ('Full', 'layers when possible'), ('Any', 'product mix')],
     'sections': [('Rules of thumb', [
         '- Heavy and dense at the bottom: foil and film rolls, register rolls, gloves, trash liners.',
         '- Light and crushable on top: cups, lids, takeout containers, napkins.',
         '- No overhang: cases that hang over the edge get crushed in transit.',
         '- Full layers: a product\'s Ti (cases per layer) tells you how many cases make a clean layer.',
         '- Stretch-wrapped and labeled: one label per pallet with the PO and a packing list.']),
         ('How to order one', [
         'Send the list of products and case counts. We confirm how they build, suggest rounding to full layers where it saves space, and quote the pallet with freight to your ZIP code.'])],
     'faq': [('Is a mixed pallet more expensive than a full pallet of one item?', 'Usually not per case; freight is charged on the pallet, so a well-built mixed pallet is efficient.'),
             ('What is the height limit for a pallet?', 'It depends on the carrier and your dock; many LTL shipments stay under about 6 to 7 feet. Ask us when quoting.'),
             ('Can I mix products from different categories?', 'Yes: gloves, cups, foil, paper and bags can share one pallet.')],
     'related': ['black-nitrile-gloves', 'foil-rolls', 'pet-cups', 'trash-liners']},

    {'slug': 'choose-a-wholesale-disposables-supplier', 'group': 'Distributors and pallet buying', 'short': 'Choosing a wholesale supplier',
     'title': 'How to Choose a Wholesale Disposables Supplier: Checklist',
     'desc': 'Checklist for distributors and multi-unit buyers comparing disposables suppliers: fill rate, lead time, spec sheets, case barcodes, pallet tiers, freight and terms.',
     'h1': 'How to choose a wholesale disposables supplier',
     'answer': 'Judge a disposables supplier on more than price: in-stock rate on your core items, how fast orders ship, whether every item has a spec sheet with case pack, barcode and Ti × Hi, clear pallet pricing, freight quotes to your ZIP code, and payment terms. A low price on items that are often out of stock costs more in the end.',
     'facts': [('Fill rate', 'first question to ask'), ('Spec', 'sheet for every SKU'), (S, 'ship time'), ('Net 30', 'for approved accounts')],
     'sections': [('Supplier checklist', [
         '- <b>Stock:</b> does the supplier keep your top 20 items in stock, and in what warehouse?',
         '- <b>Lead time:</b> how many days from order to shipment? Ours is typically %s.' % S,
         '- <b>Product data:</b> spec sheets with case pack, dimensions, weight, GTIN barcode and Ti × Hi.',
         '- <b>Consistency:</b> same size, thickness and case pack every order, and no substitutions without asking.',
         '- <b>Pricing:</b> clear case and pallet tiers, and freight quoted with the products.',
         '- <b>Terms:</b> Net 30 or similar for approved accounts.',
         '- <b>Samples:</b> can you test sizes before committing to pallets?']),
         ('Run a trial', [
         'Before moving everything, trial one or two pallets of your fastest items. Check how the order arrives, how the pallets are built and whether the paperwork matches.'])],
     'faq': [('What is a fill rate?', 'The share of ordered cases that ship complete and on time. Ask suppliers for theirs on your core items.'),
             ('Should I use one supplier or two?', 'Many buyers keep a primary and a backup for their highest-volume items.'),
             ('Do you provide spec sheets?', 'Yes, our product pages link spec sheets for most items.')],
     'related': ['black-nitrile-gloves', 'deli-containers', 'pet-cups', 'interfold-napkins']},

    {'slug': 'margin-vs-markup-for-distributors', 'group': 'Distributors and pallet buying', 'short': 'Margin vs markup for resellers',
     'title': 'Margin vs Markup: Pricing Disposables for Resale',
     'desc': 'How distributors price disposables for resale: the difference between margin and markup, a conversion table, and a worked example per case and per piece.',
     'h1': 'Margin vs markup: pricing disposables for resale',
     'answer': 'Markup is profit as a share of your cost; margin is profit as a share of the selling price. A case you buy for $40 and sell for $50 has a 25% markup but a 20% margin. Distributors usually set prices from a target margin: price = landed cost ÷ (1 − margin).',
     'facts': [('25%', 'markup = 20% margin'), ('Landed', 'cost includes freight'), ('Per piece', 'customers compare'), ('Per case', 'you invoice')],
     'sections': [('Conversion table', ('table', 'Margin and markup equivalents', ['Target margin', 'Equivalent markup', 'Price for a $40.00 landed case'],
                                    [['15%', '17.6%', '$47.06'], ['20%', '25.0%', '$50.00'], ['25%', '33.3%', '$53.33'], ['30%', '42.9%', '$57.14'], ['35%', '53.8%', '$61.54']], EX)),
                  ('Start from landed cost', [
                      'Landed cost per case = (product cost + inbound freight + handling) ÷ cases received. Buying by the pallet lowers both the product price and freight per case, which is where most reseller margin is made.',
                      'Customers often compare per piece, so check your price per piece against what they pay today: a 1,000-count glove case at $50 is 5 cents a glove.'])],
     'faq': [('What margin do disposables distributors make?', 'It varies by customer size and category; set your own target from your costs and the market.'),
             ('How do I convert margin to markup?', 'Markup = margin ÷ (1 − margin). A 20% margin is a 25% markup.'),
             ('Should freight be in my cost?', 'Yes. Use landed cost, including inbound freight, or your margin is overstated.')],
     'related': ['black-nitrile-gloves', 'pet-cups', 'black-containers', 'foil-sheets']},

    {'slug': 'reorder-point-formula', 'group': 'Distributors and pallet buying', 'short': 'Reorder point and safety stock',
     'title': 'Reorder Point Formula for Disposables Inventory',
     'desc': 'When to reorder cups, containers and gloves: reorder point = daily use × lead time + safety stock. Worked examples for a distributor and a restaurant group.',
     'h1': 'Reorder point and safety stock for disposables',
     'answer': 'Reorder point = average daily use × lead time in days + safety stock. When stock on hand falls to that number, place the order. Lead time is the days from placing the order to having it on your shelf, including shipping, not just the supplier\'s ship time.',
     'facts': [('ROP', '= use × lead time + safety'), ('Lead time', 'order to shelf'), ('Cases', 'unit to count in'), ('Weekly', 'review cycle')],
     'sections': [('Worked example', ('table', 'Reorder points for a regional distributor (in cases)', ['Item', 'Cases sold per day', 'Lead time (days)', 'Safety stock', 'Reorder point'],
                                    [['Nitrile gloves, L', '6', '7', '15', '57'], ['16 oz PET cups', '4', '7', '10', '38'], ['Deli containers 16 oz', '3', '7', '8', '29'], ['Interfold napkins', '2', '7', '5', '19']], EX)),
                  ('Setting safety stock', [
                      'A simple rule is a few days of average use; raise it for items with uneven demand or long transit. Review it monthly and after any stock-out.',
                      'Ordering on a fixed schedule (for example a 6-pallet order every two weeks) is easier to manage: order up to a target level each time instead of tracking each item\'s reorder point.'])],
     'faq': [('What is a reorder point?', 'The stock level that triggers a new order so you receive it before running out.'),
             ('What lead time should I use?', 'Days from placing the order until the product is on your shelf: processing, ship time (ours is typically %s) and transit.' % S),
             ('How much safety stock is enough?', 'Several days of average use for steady items, more for items with spiky demand.')],
     'related': ['black-nitrile-gloves', 'pet-cups', 'deli-containers', 'interfold-napkins']},

    {'slug': 'inventory-turns-for-disposables', 'group': 'Distributors and pallet buying', 'short': 'Inventory turns and ABC analysis',
     'title': 'Inventory Turns & ABC Analysis for Disposables Distributors',
     'desc': 'Measure inventory turns on disposables, rank SKUs with ABC analysis, and decide which items to buy by the pallet and which to buy by the case.',
     'h1': 'Inventory turns and ABC analysis for disposables',
     'answer': 'Inventory turns = cost of goods sold ÷ average inventory value. ABC analysis ranks SKUs by sales: A items (the top sellers, often 20% of SKUs and most of the volume) are bought by the full pallet, B items by mixed pallet, and C items by the case or dropped.',
     'facts': [('A', 'items: full pallets'), ('B', 'items: mixed pallets'), ('C', 'items: by the case'), ('Turns', 'COGS ÷ avg inventory')],
     'sections': [('How to run it', [
         '- Export 12 months of sales by SKU.',
         '- Sort by sales value and add a running total.',
         '- A = SKUs making up the first ~80% of sales, B = the next ~15%, C = the rest.',
         '- Set buying rules per class and review every quarter.']),
         ('Typical A items in disposables', [
         'Gloves, the two or three best-selling cup sizes and their lids, hinged and black takeout containers, deli containers, foil sheets and interfold napkins tend to be A items for food service distributors.'])],
     'faq': [('What is a good inventory turn for disposables?', 'It depends on your business model; track your own trend and compare A, B and C items.'),
             ('Should I drop C items?', 'Only if customers will not miss them; some C items keep accounts loyal. Buy them by the case.'),
             ('How often should I redo the ABC ranking?', 'Quarterly is common.')],
     'related': ['black-nitrile-gloves', 'black-hinged-containers', 'foil-sheets', 'pet-cup-lids']},

    {'slug': 'receiving-ltl-freight-checklist', 'group': 'Distributors and pallet buying', 'short': 'Receiving an LTL delivery',
     'title': 'Receiving an LTL Pallet Delivery: Checklist',
     'desc': 'What to check when a pallet delivery of disposables arrives: count, inspect, note damage on the bill of lading before signing, photos and what to do next.',
     'h1': 'Receiving an LTL pallet delivery: a checklist',
     'answer': 'Before signing for an LTL delivery, count the pallets against the bill of lading, look for crushed, wet or torn cases and broken wrap, and write any shortage or damage on the delivery receipt with photos. A clean signature tells the carrier everything arrived in good order, which makes later claims hard.',
     'facts': [('Count', 'pallets vs BOL'), ('Inspect', 'before signing'), ('Note', 'damage on receipt'), ('Photos', 'of every issue')],
     'sections': [('At the door', [
         '- Count pallets (and cases if wrap is broken) against the bill of lading.',
         '- Look for crushed corners, punctured or wet cases and torn wrap.',
         '- Write exceptions on the delivery receipt, for example "1 pallet, 3 cases crushed", before signing.',
         '- Take photos of the pallets on the truck and after unloading.',
         '- If you cannot inspect fully, write "subject to inspection" only if the carrier allows it; specific notes are stronger.']),
         ('After delivery', [
         'Open and check cases within a day or two and tell your supplier about any concealed damage straight away, with photos and the PRO number. Keep the packaging until the issue is settled.'])],
     'faq': [('What is a bill of lading?', 'The shipping document listing what the carrier picked up; you check the delivery against it.'),
             ('What if I find damage after signing?', 'Report it to the supplier immediately with photos; concealed damage claims have short windows.'),
             ('Do I need a dock to receive pallets?', 'No, but without one ask for liftgate delivery when you order.')],
     'related': ['stretch-film', 'pet-cups', 'deep-steam-table-pans', 'interfold-napkins']},

    {'slug': 'multistate-resale-certificate', 'group': 'Distributors and pallet buying', 'short': 'Resale certificates across states',
     'title': 'Buying Wholesale Across States With a Resale Certificate',
     'desc': 'How distributors buy disposables tax-free for resale from out-of-state suppliers: state resale certificates, the MTC uniform multijurisdiction certificate and caveats.',
     'h1': 'Buying for resale across state lines: resale certificates',
     'answer': 'Distributors buying disposables to resell usually give the supplier a resale or exemption certificate so sales tax is not charged. When the supplier is in another state, you can often use your own state\'s certificate or the Multistate Tax Commission\'s Uniform Sales & Use Tax Certificate, but acceptance and registration rules differ by state.',
     'facts': [('Resale', 'certificate on file'), ('MTC', 'uniform certificate'), ('State', 'rules vary'), ('Net 30', 'application accepts it')],
     'sections': [('How it works', [
         'Give your supplier a completed certificate before the first tax-free order. The supplier keeps it on file and does not charge tax on qualifying purchases for resale.',
         'The MTC notes that it cannot guarantee any state will accept its uniform certificate, that some states require you to be registered in the state where you buy, and that sellers can refuse a certificate. Check with your state revenue department.']),
         ('With Crown', [
         'Attach your resale certificate to the online credit application, or send it with your first quote request.'])],
     'faq': [('Can I use my home state resale certificate with a Texas supplier?', 'Often yes, but rules vary; check your state and confirm with the supplier.'),
             ('What is the MTC uniform certificate?', 'A multijurisdiction sales and use tax certificate accepted by many member states, with state-specific conditions.'),
             ('Do restaurants qualify for resale certificates?', 'Some items they pass to customers may qualify depending on the state; check your state\'s guidance.')],
     'note': 'General information, not tax advice.',
     'sources': [('FAQ: Uniform Sales and Use Tax Certificate (Multistate Tax Commission)', 'https://mtc.gov/resources/faq-uniform-sales-and-use-tax-certificate/')],
     'related': ['black-nitrile-gloves', 'pet-cups', 'paper-bags', 'disposable-cutlery-kits']},

    {'slug': 'price-per-thousand-explained', 'group': 'Distributors and pallet buying', 'short': 'Price per thousand (per M)',
     'title': 'Price Per Thousand (Per M) for Disposables Explained',
     'desc': 'Compare cups, lids, gloves and portion cups across different case packs with price per thousand (per M): formula, examples and common mistakes.',
     'h1': 'Price per thousand (per M): comparing disposables across case packs',
     'answer': 'Price per M (per thousand) = case price ÷ pieces per case × 1,000. It puts quotes with different case packs on the same footing: a $45 case of 1,000 cups is $45.00 per M, while a $26 case of 500 is $52.00 per M, so the more expensive case is the better buy.',
     'facts': [('M', '= 1,000 pieces'), ('÷ pack × 1,000', 'formula'), ('Add', 'freight per M'), ('Same', 'spec to compare')],
     'sections': [('Examples', ('table', 'Same item, different case packs', ['Quote', 'Case price', 'Pieces per case', 'Price per M'],
                               [['A', '$45.00', '1,000', '$45.00'], ['B', '$26.00', '500', '$52.00'], ['C', '$100.00', '2,500', '$40.00']], EX)),
                  ('Common mistakes', [
                      '- Comparing case prices when case packs differ.',
                      '- Ignoring thickness or weight: a lighter cup or thinner glove is cheaper per M but not the same product.',
                      '- Leaving out freight: add freight per M (freight ÷ total pieces × 1,000).'])],
     'faq': [('What does "per M" mean?', 'Per thousand pieces, from the Roman numeral M.'),
             ('How do I add freight?', 'Divide the freight charge by total pieces and multiply by 1,000, then add it to price per M.'),
             ('Which items are usually priced per M?', 'Cups, lids, portion cups, gloves, napkins and bags.')],
     'related': ['pet-cups', 'portion-cups', 'black-nitrile-gloves', 'beverage-napkins']},

    {'slug': 'ltl-vs-partial-truckload', 'group': 'Distributors and pallet buying', 'short': 'LTL vs volume LTL vs truckload',
     'title': 'LTL vs Volume LTL vs Full Truckload for Pallet Orders',
     'desc': 'Which freight mode fits a disposables order of 1, 6, 12 or 26 pallets: LTL, volume LTL, partial truckload or full truckload, and what each means for cost and handling.',
     'h1': 'LTL, volume LTL, partial or full truckload?',
     'answer': 'For roughly 1 to 5 pallets, standard LTL is usual. Around 6 to 12 pallets, volume LTL or partial truckload often costs less and involves fewer terminal transfers. Above about half a trailer, compare a full truckload, which goes straight from our dock to yours.',
     'facts': [('1–5', 'pallets: LTL'), ('6–12', 'pallets: volume LTL / partial'), ('13–26', 'compare full truckload'), ('48', 'states served')],
     'sections': [('What each mode means', [
         '- <b>LTL:</b> your pallets share a truck and pass through carrier terminals; priced by weight, class and distance.',
         '- <b>Volume LTL / partial truckload:</b> larger shipments quoted on space and weight, usually with less handling.',
         '- <b>Full truckload:</b> the whole trailer is yours, picked up and delivered directly.']),
         ('Matching to our tiers', [
         'Our delivered tiers are 6 and 12 pallets, the range where volume LTL and partial truckload are most often cheaper per pallet than standard LTL. We quote the mode that fits your order and ZIP code.'])],
     'faq': [('Is truckload faster than LTL?', 'Usually, since it does not stop at terminals.'),
             ('Does freight mode change the product price?', 'No, but it changes your landed cost per case.'),
             ('Can you quote freight with the order?', 'Yes, send your ZIP code and we quote products and freight together.')],
     'related': ['pet-cups', 'deli-containers', 'black-nitrile-gloves', 'interfold-napkins']},

    # ================================================================ buying for restaurants & events
    {'slug': 'new-restaurant-disposables-checklist', 'group': 'Buying for restaurants and events', 'short': 'New restaurant disposables checklist',
     'title': 'Opening a Restaurant: Disposables Checklist & First Order',
     'desc': 'The disposables a new restaurant needs before opening day: takeout packaging, cups, gloves, foil and film, paper, restroom and cleaning items, with first-order tips.',
     'h1': 'Opening a restaurant: the disposables checklist',
     'answer': 'Before opening, stock takeout containers and lids, cups and lids, portion cups, cutlery kits, napkins, bags, gloves, foil and food film, register rolls, trash liners and restroom paper. Order a modest first round by the case, track real use for four weeks, then move your fastest items to pallet quantities.',
     'facts': [('12', 'core categories'), ('4 weeks', 'to learn real use'), ('By the case', 'first order'), ('Samples', 'before committing')],
     'sections': [('The checklist', ('table', 'Opening-day disposables', ['Area', 'Items'], [
         ['Takeout', 'Hinged or black containers with lids, deli containers, portion cups and lids'],
         ['Drinks', 'Cold cups and lids, beverage napkins'],
         ['Counter', 'Cutlery kits, napkins, paper bags, register rolls'],
         ['Kitchen', 'Gloves, foil sheets and rolls, food film, foil pans, wax and deli paper'],
         ['Back of house', 'Trash liners, kitchen towels'],
         ['Restrooms', 'Jumbo roll or bath tissue, hand towels']])),
         ('First order tips', [
         'Pick one container family and two or three sizes, one lid size for your cups where possible, and request samples before the first order. Confirm your register roll size with your POS printer.'])],
     'faq': [('How much should my first disposables order be?', 'Enough for three to four weeks at your forecast volume; adjust once you see real use.'),
             ('Which items should I buy by the pallet first?', 'Gloves and your main takeout container, once volume is steady.'),
             ('Can I get samples before opening?', 'Yes, ask us for samples of the sizes you are considering.')],
     'related': ['black-hinged-containers', 'pet-cups', 'black-nitrile-gloves', 'register-roll-paper']},

    {'slug': 'catering-disposables-per-100-guests', 'group': 'Buying for restaurants and events', 'short': 'Catering disposables per 100 guests',
     'title': 'Catering Disposables for 100 Guests: Quantity Guide',
     'desc': 'How many foil pans, lids, plates, cutlery kits, cups and napkins to order for 100 guests, with simple per-guest planning numbers for caterers and events.',
     'h1': 'How many catering disposables do you need for 100 guests?',
     'answer': 'For a 100-guest buffet, plan roughly 6 to 10 half size foil pans with lids (depending on menu), 100 to 120 plates, 100 cutlery kits, 200 to 300 cups and 300 napkins. Planning numbers per guest: 1.2 plates, 1 cutlery kit, 2 to 3 cups and 3 napkins.',
     'facts': [('1.2', 'plates per guest'), ('2–3', 'cups per guest'), ('3', 'napkins per guest'), ('Half pans', '12–20 servings each')],
     'sections': [('Per-guest planning numbers', ('table', 'Quantities for 50, 100 and 200 guests', ['Item', 'Per guest', '50 guests', '100 guests', '200 guests'], [
         ['Plates', '1.2', '60', '120', '240'], ['Cutlery kits', '1', '50', '100', '200'], ['Cups', '2.5', '125', '250', '500'],
         ['Napkins', '3', '150', '300', '600'], ['Half size foil pans + lids', 'menu-based', '4–6', '6–10', '12–18']],
         'Planning estimates; adjust for menu, service style and event length.')),
         ('Pans by dish', [
         'A half size deep pan holds roughly 12 to 20 servings of a main or side; a full size pan about twice that. Order matching lids and a few spare pans for refills and leftovers.'])],
     'faq': [('How many servings does a half size foil pan hold?', 'Roughly 12 to 20, depending on the dish and portion.'),
             ('How many napkins per guest?', 'About three for a buffet, more for messy food.'),
             ('Do you sell foil pans by the case?', 'Yes: half size deep pans 100 per case and full size 50 per case.')],
     'related': ['deep-steam-table-pans', 'foil-lids-for-steam-table-pans', 'disposable-cutlery-kits', 'dinner-napkins']},

    {'slug': 'styrofoam-alternatives', 'group': 'Buying for restaurants and events', 'short': 'Styrofoam container alternatives',
     'title': 'Styrofoam Container Alternatives for Restaurants (2026)',
     'desc': 'Replacing foam takeout containers: bagasse, black plastic, clear PET hinged and foil options compared, and which states restrict foam food containers.',
     'h1': 'Styrofoam container alternatives for restaurants',
     'answer': 'The main replacements for foam clamshells and bowls are PFAS-free bagasse (sugarcane fiber) hinged containers, black plastic microwavable containers with clear lids, clear PET hinged containers and foil pans. Several states, including California, Oregon, New York, Colorado and Virginia, restrict foam food containers.',
     'facts': [('4', 'main alternatives'), ('PFAS-free', 'bagasse option'), ('Microwavable', 'black containers'), ('Mixed', 'pallets welcome')],
     'sections': [('Comparing the options', ('table', 'Foam replacements', ['Option', 'Strengths', 'Watch for'], [
         ['Bagasse hinged', 'Plant fiber, PFAS-free, handles hot food, microwavable', 'Very wet food over long holds'],
         ['Black plastic containers', 'Microwavable, clear lid, tight seal', 'Not ovenable'],
         ['Clear PET hinged', 'Shows the food, good for cold items and salads', 'Not for hot food'],
         ['Foil pans with lids', 'Oven-safe, good for catering', 'Not microwavable']])),
         ('Where foam is restricted', [
         'California, Oregon and New York restrict foam food service containers statewide; Colorado\'s ban took effect January 1, 2024, and Virginia\'s statewide ban for all food vendors takes effect July 1, 2026. Many cities have their own rules. Texas has no statewide ban.'])],
     'faq': [('What is the best replacement for foam clamshells?', 'Bagasse hinged containers for hot food; black plastic containers for saucy, microwave-reheated meals.'),
             ('Are bagasse containers PFAS-free?', 'Our bagasse hinged containers are PFAS-free.'),
             ('Which states ban foam containers?', 'Several, including California, Oregon, New York, Colorado and Virginia. Check current state and city rules.')],
     'note': 'General information; laws change, so check current rules for your location.',
     'sources': [('US states ban polystyrene foam packaging (Packaging Gateway)', 'https://www.packaging-gateway.com/news/us-states-ban-polystyrene-foam-packaging/'),
                 ('State packaging laws taking effect in 2026 (Packaging Dive)', 'https://www.packagingdive.com/news/state-packaging-laws-2026-bags-foam-pfas-hotels/808682/')],
     'related': ['bagasse-hinged-containers', 'black-containers', 'black-hinged-containers', 'deep-steam-table-pans']},

    {'slug': 'pfas-free-takeout-containers', 'group': 'Buying for restaurants and events', 'short': 'PFAS-free takeout containers',
     'title': 'PFAS-Free Takeout Containers: What to Buy and Ask',
     'desc': 'How to source PFAS-free takeout packaging for states with PFAS bans: which materials are affected, what documentation to ask suppliers for, and PFAS-free bagasse options.',
     'h1': 'Buying PFAS-free takeout containers',
     'answer': 'PFAS bans in more than ten states mostly affect molded fiber and paper packaging that was treated to resist grease. To stay compliant, buy fiber items documented as free of intentionally added PFAS and keep the supplier statement on file. Our bagasse hinged containers are PFAS-free.',
     'facts': [('10+', 'states with bans'), ('Fiber', 'items most affected'), ('Statement', 'keep on file'), ('PFAS-free', 'bagasse in stock')],
     'sections': [('What to ask your supplier', [
         '- A written statement that the item has no intentionally added PFAS.',
         '- The material and coating for each fiber item.',
         '- Spec sheets with item numbers so records match invoices.']),
         ('Bagasse containers we stock', ('spec', 'bagasse-hinged-containers', 'Bagasse hinged containers'))],
     'faq': [('Which packaging contains PFAS?', 'Mostly grease-resistant paper and molded fiber, such as some bowls, clamshells and wraps.'),
             ('Are plastic containers affected by PFAS bans?', 'The bans focus on intentionally added PFAS; check each state\'s definition.'),
             ('Are your bagasse containers PFAS-free?', 'Yes.')],
     'note': 'General information, not legal advice.',
     'sources': [('PFAS in food packaging: state compliance deadlines (OFW Law)', 'https://ofwlaw.com/pfas-in-food-packaging-state-compliance-guide/')],
     'related': ['bagasse-hinged-containers', 'black-containers', 'paper-bags', 'deli-containers']},

    {'slug': 'cheapest-takeout-containers', 'group': 'Buying for restaurants and events', 'short': 'Lowest-cost takeout containers',
     'title': 'Cheapest Takeout Containers per Meal: How to Compare',
     'desc': 'Which takeout container costs least per meal depends on size, material, lid and case pack. How to compare hinged, black, deli and bagasse containers per meal.',
     'h1': 'Which takeout containers cost the least per meal?',
     'answer': 'The cheapest container is the smallest one that holds the portion without leaking. Compare containers per meal, including the lid: a container sold as a set with its lid can cost less than a cheaper base plus a separate lid. Hinged containers have a built-in lid; black-base containers come as sets.',
     'facts': [('Per meal', 'include the lid'), ('Smallest', 'size that fits'), ('Sets', 'base + lid'), ('Pallet', 'lowest per piece')],
     'sections': [('Cost drivers', [
         '- Size: each step up in ounces adds material and cost.',
         '- Material: hinged one-piece containers avoid a separate lid; fiber and plastic price differently by market.',
         '- Case pack and pallet tier: buying by the pallet lowers cost per piece.',
         '- Waste: leaks and crushed containers cost more than any price difference.']),
         ('How to test', [
         'Price your two most-used sizes per meal from two suppliers, with lids and freight. Then sample a size down and check whether portions still fit.'])],
     'faq': [('Are hinged containers cheaper than containers with separate lids?', 'Often per meal, because the lid is built in; compare per meal to be sure.'),
             ('Do black containers come with lids?', 'Ours are sold as sets of base and lid, 150 sets per case.'),
             ('Does buying by the pallet lower container cost?', 'Yes, pallet tiers lower the price per case.')],
     'related': ['black-hinged-containers', 'black-containers', 'deli-containers', 'bagasse-hinged-containers']},

    {'slug': 'paper-vs-plastic-takeout-bags', 'group': 'Buying for restaurants and events', 'short': 'Paper vs plastic takeout bags',
     'title': 'Paper vs Plastic Takeout Bags for Restaurants',
     'desc': 'Kraft and white paper bags vs poly bags for takeout and delivery: strength, grease, branding, local bag rules and which bag size fits which order.',
     'h1': 'Paper or plastic bags for takeout?',
     'answer': 'Paper bags stand up for packing, look clean for branding and are accepted where plastic carryout bags are restricted. Poly bags resist moisture and handle heavy, wet orders. Most restaurants use flat-bottom paper bags in two or three sizes for takeout and keep poly bags for large or catering orders.',
     'facts': [('#2–#12', 'paper bag sizes'), ('Kraft / white', 'paper colors'), ('Poly', 'for heavy, wet orders'), ('500', 'paper bags per case')],
     'sections': [('Paper bag sizes we stock', ('spec', 'paper-bags', 'Paper bags')),
                  ('Poly bags we stock', ('spec', 'poly-bags', 'Poly bags'))],
     'faq': [('What size paper bag for one takeout meal?', 'A #8 or #10 bag usually fits one container with sides; #12 for two meals.'),
             ('Are plastic bags banned for restaurants?', 'Some states and cities restrict plastic carryout bags; check local rules.'),
             ('How many paper bags are in a case?', '500.')],
     'related': ['paper-bags', 'poly-bags', 'black-containers', 'disposable-cutlery-kits']},

    {'slug': 'microwave-safe-takeout-containers', 'group': 'Buying for restaurants and events', 'short': 'Microwave-safe containers',
     'title': 'Are Takeout Containers Microwave Safe? | Crown Plastic & Paper',
     'desc': 'Are takeout containers microwave safe? Black-base and bagasse: yes. Foil pans and clear PET: no. A quick chart by container type, plus reheating tips.',
     'h1': 'Are takeout containers microwave safe?',
     'answer': 'Black-base plastic takeout containers and bagasse containers are made for microwave reheating. Foil pans must never go in a microwave. Clear PET hinged containers are for cold food and should not be microwaved. For deli containers, check the item spec sheet.',
     'facts': [('Yes', 'black-base containers'), ('Yes', 'bagasse'), ('No', 'foil pans'), ('No', 'clear PET')],
     'sections': [('Quick reference', ('table', 'Microwave and oven use', ['Container', 'Microwave', 'Oven'], [
         ['Black-base plastic containers', 'Yes', 'No'], ['Bagasse hinged containers', 'Yes', 'No'], ['Foil pans', 'No', 'Yes'],
         ['Clear PET hinged containers', 'No', 'No'], ['Deli containers', 'See spec sheet', 'No']])),
         ('Reheating tips for customers', [
         'Print "microwave safe, remove lid or vent before heating" on a sticker or menu if customers reheat at home. Vent or remove lids, heat in short intervals and stir.'])],
     'faq': [('Can black takeout containers go in the microwave?', 'Yes, our black-base containers are microwavable; vent or remove the lid.'),
             ('Can foil pans go in the microwave?', 'No.'),
             ('Are bagasse containers microwave safe?', 'Yes, for reheating.'),
             ('Are to-go boxes microwave safe?', 'It depends on the material, not the shape. Black-base plastic and bagasse to-go boxes can be reheated; foil pans and clear PET clamshells cannot. If a box has a metal handle or foil lining, keep it out of the microwave.'),
             ('Are deli containers microwave safe?', 'Our heavy duty deli containers are listed as microwave safe for reheating. Vent or remove the lid, heat in short intervals and check the spec sheet for the item you order.')],
     'related': ['black-containers', 'round-black-containers', 'bagasse-hinged-containers', 'deli-containers']},

    {'slug': 'foil-pans-oven-grill-air-fryer', 'group': 'Buying for restaurants and events', 'short': 'Foil pans: oven, grill, air fryer',
     'title': 'Can Foil Pans Go in the Oven, Grill or Air Fryer?',
     'desc': 'Using disposable aluminum pans in the oven, on the grill, in a smoker or air fryer, and why never in a microwave. Tips for catering and BBQ kitchens.',
     'h1': 'Can foil pans go in the oven, on the grill or in an air fryer?',
     'answer': 'Yes. Disposable aluminum pans are made for ovens, grills and smokers, and small round pans fit many air fryers if air can still circulate. Support full pans from underneath when they are full, because thin foil bends. Never put foil pans in a microwave.',
     'facts': [('Oven', 'yes'), ('Grill / smoker', 'yes'), ('Air fryer', 'small pans, with airflow'), ('Microwave', 'never')],
     'sections': [('Tips', [
         '- Carry full pans on a sheet pan or tray; foil flexes under weight.',
         '- Use foil lids for holding and transport; use film only once food has cooled.',
         '- For smokers, deep half pans catch drippings and hold sauced meats.']),
         ('Pans we stock', ('spec', 'deep-steam-table-pans', 'Deep steam table pans'))],
     'faq': [('Do foil pans need to be greased?', 'For baked goods, yes, or line with parchment.'),
             ('Can foil lids go in the oven?', 'Foil lids can; board-backed lids should not.'),
             ('How many half size pans in a case?', '100 per case.')],
     'related': ['deep-steam-table-pans', 'foil-lids-for-steam-table-pans', 'round-foil-pans', 'foil-rolls']},

    {'slug': 'are-pet-cups-recyclable', 'group': 'Buying for restaurants and events', 'short': 'Are PET cups recyclable?',
     'title': 'Are PET Plastic Cups Recyclable? (#1 Plastic)',
     'desc': 'PET cups are resin code #1, the most widely recycled plastic in the US. What that means for clear cold cups and lids, and what customers should know.',
     'h1': 'Are PET plastic cups recyclable?',
     'answer': 'PET (polyethylene terephthalate) is resin identification code #1 and is one of the most widely accepted plastics in curbside recycling. Whether a clear cup is actually recycled depends on the local program, since some accept bottles only. Lids and straws may be different plastics.',
     'facts': [('#1', 'resin code'), ('Clear', 'and stiff'), ('Local', 'program decides'), ('98 mm', 'lid fits 12–24 oz')],
     'sections': [('What to tell customers', [
         'Say "PET #1, check your local recycling program" rather than "100% recyclable". Empty and rinse before recycling.']),
         ('Cups we stock', ('spec', 'pet-cups', 'PET cups'))],
     'faq': [('What number plastic is a PET cup?', '#1.'),
             ('Are PET lids recyclable?', 'Check the resin code on the lid and your local program.'),
             ('Can PET cups hold hot drinks?', 'No, they are for cold drinks.')],
     'related': ['pet-cups', 'pet-cup-lids', 'beverage-napkins', 'portion-cups']},

    {'slug': 'thermal-vs-bond-paper-test', 'group': 'Buying for restaurants and events', 'short': 'Thermal or bond register paper?',
     'title': 'Thermal vs Bond Register Paper: How to Tell & Which to Buy',
     'desc': 'How to tell thermal from bond register rolls (the scratch test), which printers use each, and how to match roll width and length to your POS or card terminal.',
     'h1': 'Thermal or bond register paper: how to tell and which to buy',
     'answer': 'Thermal paper turns black when you scratch it with a fingernail or heat it; bond paper does not. Thermal printers (most POS receipt printers and card terminals) need thermal paper; impact printers, often used for kitchen tickets, use bond paper with an ink ribbon. Then match the width and the roll length your printer holds.',
     'facts': [('Scratch', 'test: black = thermal'), ('3 1/8"', 'common POS width'), ('2 1/4"', 'common terminal width'), ('50', 'rolls per case')],
     'sections': [('Rolls we stock', ('spec', 'register-roll-paper', 'Register rolls')),
                  ('Choosing length', [
                      'Longer rolls mean fewer changes but must fit the printer\'s paper bay; check the maximum roll diameter in the printer manual.'])],
     'faq': [('How do I know if my printer is thermal?', 'If it has no ink ribbon, it is almost certainly thermal.'),
             ('What size is a standard receipt roll?', '3 1/8 inch wide for most POS printers; 2 1/4 inch for many card terminals.'),
             ('Do kitchen printers use thermal or bond?', 'Many use bond paper with a ribbon because it holds up to heat.')],
     'related': ['register-roll-paper', 'beverage-napkins', 'paper-bags', 'pet-cups']},

    {'slug': 'food-film-gauge-and-width', 'group': 'Buying for restaurants and events', 'short': 'Food film widths and lengths',
     'title': 'Food Film (Cling Wrap) Widths & Roll Lengths Guide',
     'desc': 'Choosing food service cling film: 12, 18 and 24 inch widths, 2,000 ft rolls, gauge, cutter boxes and which width fits sheet pans, hotel pans and prep containers.',
     'h1': 'Food film widths and roll lengths: which to buy',
     'answer': 'Food service film comes in 12, 18 and 24 inch widths on long rolls in cutter boxes. 12 inch suits small containers and sandwiches, 18 inch is the all-round size for hotel pans and prep, and 24 inch covers full sheet pans and large trays in one pass.',
     'facts': [('12 / 18 / 24"', 'widths'), ('2,000 ft', 'roll length'), ('18"', 'all-round size'), ('Cutter box', 'with slide cutter')],
     'sections': [('Rolls we stock', ('spec', 'food-film', 'Food film')),
                  ('Matching width to the job', [
                      '- 12 inch: deli containers, sandwiches, small bowls.',
                      '- 18 inch: half and full hotel pans, prep containers.',
                      '- 24 inch: full sheet pans, catering trays, bulk wrapping.'])],
     'faq': [('What width cling film for a full sheet pan?', '24 inch covers it in one pass.'),
             ('How long is a food service film roll?', 'Ours are 2,000 feet.'),
             ('Is food film the same as stretch film?', 'No. Food film is for food; stretch film is for wrapping pallets.')],
     'related': ['food-film', 'foil-rolls', 'deep-steam-table-pans', 'stretch-film']},

    {'slug': 'restaurant-restroom-paper-supplies', 'group': 'Buying for restaurants and events', 'short': 'Restroom paper supplies',
     'title': 'Restaurant Restroom Supplies: Jumbo Rolls, Towels & Liners',
     'desc': 'Restroom paper for restaurants, c-stores and facilities: jumbo roll vs individually wrapped tissue, roll and folded hand towels, liners and how much to stock.',
     'h1': 'Restroom paper supplies for restaurants and facilities',
     'answer': 'Busy restrooms run on jumbo roll tissue (750 or 1,000 ft rolls, fewer changes) or individually wrapped standard rolls, plus roll or folded hand towels and trash liners. Jumbo rolls and hand roll towels cut refill frequency and waste in high-traffic restrooms.',
     'facts': [('750 / 1,000 ft', 'jumbo rolls'), ('12', 'jumbo rolls per case'), ('350 / 800 ft', 'hand roll towels'), ('Fewer', 'refills with jumbo')],
     'sections': [('Jumbo roll tissue', ('spec', 'jumbo-roll-tissue', 'Jumbo roll tissue')),
                  ('Hand and kitchen towels', ('spec', 'kraft-white-kitchen-roll-towels', 'Roll towels'))],
     'faq': [('Jumbo roll or standard rolls?', 'Jumbo rolls for high-traffic restrooms; standard wrapped rolls for low-traffic or single-user restrooms.'),
             ('Kraft or white towels?', 'Kraft costs less; white looks brighter in customer areas.'),
             ('Do I need specific dispensers?', 'Yes, match roll diameter and core size to your dispenser.')],
     'related': ['jumbo-roll-tissue', 'kraft-white-kitchen-roll-towels', 'individual-wrapped-bath-tissue', 'trash-liners']},

    # ================================================================ by type of business
    {'slug': 'bakery-supplies-wholesale', 'group': 'Supplies by type of business', 'short': 'Bakery supplies',
     'title': 'Bakery Disposables Wholesale: Tissue, Wax Paper & More',
     'desc': 'Disposables bakeries and donut shops reorder: bakery tissue, interfold wax paper, deli paper, foil pans, gloves, napkins and bags, by the case or pallet.',
     'h1': 'Bakery and donut shop disposables by the case',
     'answer': 'Bakeries and donut shops reorder bakery tissue for picking up pastries, interfold wax paper for wrapping and lining, deli paper, round and steam table foil pans for baking and catering, gloves, napkins and paper bags. Wax paper and tissue are the items used by the thousands.',
     'facts': [('Tissue', 'for pick-up'), ('Wax paper', '6"–15" sheets'), ('Foil pans', 'bake and carry'), ('Bags', 'kraft and white')],
     'sections': [('Interfold wax paper sizes', ('spec', 'interfold-wax-paper', 'Interfold wax paper')),
                  ('Other bakery items', [
                      '- Bakery tissue for handling pastries (ready-to-eat food should not be touched bare-handed).',
                      '- Round foil pans for pies and baked dishes.',
                      '- Paper bags in #2 to #8 sizes for single items and dozens.'])],
     'faq': [('What size wax paper for donuts?', '6 or 8 inch interfold sheets for single donuts and pastries.'),
             ('What is bakery tissue used for?', 'Picking up and wrapping ready-to-eat baked goods without bare hands.'),
             ('Can I order wax paper by the pallet?', 'Yes, alone or on a mixed pallet.')],
     'related': ['bakery-tissue', 'interfold-wax-paper', 'round-foil-pans', 'paper-bags']},

    {'slug': 'sandwich-and-deli-shop-supplies', 'group': 'Supplies by type of business', 'short': 'Sandwich & deli shop supplies',
     'title': 'Sandwich & Deli Shop Supplies: Wraps, Containers & Gloves',
     'desc': 'What sandwich shops and delis reorder: deli and checker paper, foil sheets, wax paper, food film, hinged containers, deli containers, gloves and bags.',
     'h1': 'Sandwich and deli shop supplies',
     'answer': 'Sandwich shops and delis run on wraps (checker deli paper, foil sheets and interfold wax paper), food film, 6 × 6 and 9 × 6 inch hinged containers, deli containers for sides and soups, vinyl or nitrile gloves, napkins and bags.',
     'facts': [('12" × 12"', 'checker deli paper'), ('Foil sheets', 'hot sandwiches'), ('9" × 6"', 'sandwich + side'), ('Deli cups', 'soups and sides')],
     'sections': [('Checker deli paper', ('spec', 'checker-deli-paper-wrap', 'Checker deli paper')),
                  ('Foil sheets', ('spec', 'foil-sheets', 'Foil sheets'))],
     'faq': [('Foil or deli paper for sandwiches?', 'Foil sheets for hot sandwiches that need heat held; deli paper for cold sandwiches and presentation.'),
             ('Which container for a sandwich with chips?', 'A 9 × 6 inch hinged container.'),
             ('Which gloves for a sandwich line?', 'Vinyl for quick assembly with frequent changes; nitrile for prep.')],
     'related': ['checker-deli-paper-wrap', 'foil-sheets', 'black-hinged-containers', 'vinyl-gloves']},

    {'slug': 'chinese-takeout-restaurant-supplies', 'group': 'Supplies by type of business', 'short': 'Chinese takeout supplies',
     'title': 'Chinese Takeout Restaurant Supplies Wholesale',
     'desc': 'Takeout supplies Chinese and Asian restaurants reorder: deli containers for soups and sauces, round and rectangular black containers, cutlery kits, bags and gloves.',
     'h1': 'Chinese and Asian takeout restaurant supplies',
     'answer': 'Chinese and Asian takeout restaurants use deli containers (8 to 32 oz) for soups, rice and sauces, round and rectangular black containers for entrées and noodles, portion cups for sauces, cutlery kits, napkins, paper bags and gloves. Deli containers are often the highest-volume item.',
     'facts': [('8–32 oz', 'deli containers'), ('240', 'deli containers per case'), ('Round', 'for noodles and soup'), ('Sets', 'black base + lid')],
     'sections': [('Deli containers', ('spec', 'deli-containers', 'Deli containers')),
                  ('Round black containers', ('spec', 'round-black-containers', 'Round black containers'))],
     'faq': [('What size container for wonton soup?', '16 oz for a single serving, 32 oz for family size.'),
             ('Are deli containers good for hot soup?', 'Check the spec sheet for temperature rating; many are used for hot soup to go.'),
             ('How many deli containers in a case?', '240 for 8–32 oz, 120 for 64 oz.')],
     'related': ['deli-containers', 'round-black-containers', 'black-containers', 'disposable-cutlery-kits']},

    {'slug': 'poke-and-bowl-restaurant-supplies', 'group': 'Supplies by type of business', 'short': 'Poke & bowl restaurant supplies',
     'title': 'Poke & Bowl Restaurant Supplies: Round Containers & More',
     'desc': 'Packaging for poke, salad and grain bowl restaurants: round black containers 16–48 oz with lids, portion cups for sauces, cutlery, gloves and bags.',
     'h1': 'Poke, salad and bowl restaurant supplies',
     'answer': 'Bowl concepts mostly use round black containers with clear lids (24 and 32 oz for most bowls, 48 oz for large salads), 2 oz portion cups and lids for sauces and dressings, cutlery kits, nitrile gloves for raw fish prep, napkins and bags.',
     'facts': [('24–32 oz', 'standard bowl'), ('48 oz', 'large salad'), ('2 oz', 'sauce cups'), ('150', 'sets per case')],
     'sections': [('Round black containers', ('spec', 'round-black-containers', 'Round black containers')),
                  ('Portion cups', ('spec', 'portion-cups', 'Portion cups'))],
     'faq': [('What size bowl for poke?', '24 oz for regular, 32 oz for large.'),
             ('Which gloves for raw fish?', 'Nitrile, changed between tasks.'),
             ('Do round containers come with lids?', 'Yes, sold as sets of base and lid.')],
     'related': ['round-black-containers', 'portion-cups', 'portion-cups-lids', 'black-nitrile-gloves']},

    {'slug': 'mediterranean-gyro-shop-supplies', 'group': 'Supplies by type of business', 'short': 'Mediterranean & gyro shop supplies',
     'title': 'Mediterranean & Gyro Shop Supplies: Foil, Containers & Cups',
     'desc': 'Supplies for gyro, shawarma and Mediterranean restaurants: foil sheets for wraps, 3-compartment hinged containers for plates, portion cups for sauces, gloves.',
     'h1': 'Mediterranean, gyro and shawarma shop supplies',
     'answer': 'Gyro and shawarma shops wrap with foil sheets (12 × 10.75 inch fits most pitas and wraps), serve plates in 9 × 9 inch 3-compartment hinged containers, send tzatziki, garlic sauce and tahini in 2 oz portion cups with lids, and use nitrile gloves at the carving station.',
     'facts': [('12" × 10.75"', 'foil sheets for wraps'), ('9" × 9" 3-comp', 'plates'), ('2 oz', 'sauce cups'), ('Nitrile', 'carving station')],
     'sections': [('Foil sheets', ('spec', 'foil-sheets', 'Foil sheets')),
                  ('Hinged containers', ('spec', 'black-hinged-containers', 'Black hinged containers'))],
     'faq': [('What size foil for a gyro wrap?', '12 × 10.75 inch sheets fit most pita and lavash wraps.'),
             ('Which container for a gyro plate?', '9 × 9 inch 3-compartment hinged containers keep rice, salad and meat apart.'),
             ('How many foil sheets in a case?', '3,000: 6 boxes of 500.')],
     'related': ['foil-sheets', 'black-hinged-containers', 'portion-cups', 'black-nitrile-gloves']},

    {'slug': 'coffee-shop-cold-cup-supplies', 'group': 'Supplies by type of business', 'short': 'Coffee shop cold cup supplies',
     'title': 'Coffee Shop Supplies: Cold Cups, Lids & Napkins in Bulk',
     'desc': 'Cold drink supplies for coffee shops: PET cups 9–32 oz, dome, flat and slip-thru lids, beverage napkins and gloves, with lid fit by rim size and case counts.',
     'h1': 'Coffee shop cold cups, lids and napkins in bulk',
     'answer': 'For iced coffee and cold drinks, coffee shops reorder clear PET cups (12, 16, 20 and 24 oz all take one 98 mm lid), flat lids with a straw hole or slip-thru sip lids, dome lids for whipped drinks, beverage napkins and gloves. Standardising on 98 mm sizes keeps lids to one size.',
     'facts': [('98 mm', 'lid fits 12–24 oz'), ('1,000', 'cups per case'), ('3', 'lid styles'), ('4,000', 'white beverage napkins per case')],
     'sections': [('PET cups', ('spec', 'pet-cups', 'PET cups')),
                  ('Lids', ('spec', 'pet-cup-lids', 'PET cup lids'))],
     'faq': [('Which lid for iced coffee without a straw?', 'A slip-thru sip lid.'),
             ('Do 16 and 20 oz cups use the same lid?', 'Yes, both use 98 mm lids.'),
             ('Do you stock hot cups?', 'Our cups are PET cold cups; ask us about other items.')],
     'related': ['pet-cups', 'pet-cup-lids', 'beverage-napkins', 'vinyl-gloves']},

    {'slug': 'school-cafeteria-disposables', 'group': 'Supplies by type of business', 'short': 'School cafeteria disposables',
     'title': 'School Cafeteria Disposables: Trays, Cutlery & Napkins',
     'desc': 'Disposables for school cafeterias and institutional kitchens: compartment school trays, cutlery kits, napkins, portion cups, gloves, liners and planning per student.',
     'h1': 'School cafeteria disposables',
     'answer': 'School and institutional kitchens reorder compartment trays, cutlery kits or sporks, napkins, portion cups for condiments, gloves, foil pans for batch cooking and heavy trash liners. Plan per student per meal and buy the core items by the pallet before each semester.',
     'facts': [('Per meal', 'planning unit'), ('Sporks', 'one-piece option'), ('Pallets', 'before each semester'), ('Net 30', 'for approved accounts')],
     'sections': [('Per-meal planning', ('table', 'Per student per meal', ['Item', 'Typical quantity'], [
         ['Compartment tray', '1'], ['Cutlery kit or spork', '1'], ['Napkins', '1–2'], ['Portion cups (condiments)', '0–2'], ['Gloves (staff)', 'by shift']])),
         ('Cutlery kits', ('spec', 'disposable-cutlery-kits', 'Cutlery and spork kits'))],
     'faq': [('How many trays for 500 students?', '500 per meal served; plan for days per month and a few percent spare.'),
             ('Sporks or full cutlery kits?', 'Sporks for younger students and simpler menus; kits for older students.'),
             ('Can schools get Net 30 terms?', 'Approved accounts get Net 30.')],
     'related': ['school-trays', 'disposable-cutlery-kits', 'beverage-napkins', 'trash-liners']},
]

GROUPS = {g['slug']: g['group'] for g in BUYER}
ENTRIES = [(g['slug'], g['short'], _builder(g)) for g in BUYER]
