"""/guides/: size charts and buying guides built from our own spec sheets (assets/spec-map.json).

These are the pages answer engines quote: one direct answer at the top, a real table, an FAQ.
Every number comes from the spec map (or the 2026 catalog where noted); nothing is estimated.
"""
import html
import re

import geo
from locations import crumbs, faq_block, hero, ld

E = html.escape
UPDATED = '2026-11-04'


def _num(s):
    m = re.search(r'(\d+(?:\.\d+)?)(?:\s*/\s*(\d+))?', s or '')
    if not m:
        return 9e9
    return float(m.group(1)) / float(m.group(2)) if m.group(2) else float(m.group(1))


def _tihi(a):
    """Ti x Hi only when it agrees with cases per pallet (a few spec sheets disagree with themselves)."""
    t, c = a.get('ti-x-hi', ''), a.get('cases-pallets', '')
    m = re.match(r'([\d.]+)\s*x\s*([\d.]+)', t)
    if m and str(c).isdigit() and abs(float(m.group(1)) * float(m.group(2)) - int(c)) < 0.5:
        return t.replace(' x ', ' × ')
    return '—'


def _pal(a):
    c = str(a.get('cases-pallets', ''))
    return c if c.isdigit() else '—'


def table(caption, head, rows, note=''):
    th = ''.join('<th scope="col">%s</th>' % E(h) for h in head)
    tr = ''.join('<tr>%s</tr>' % ''.join(
        ('<th scope="row">%s</th>' if i == 0 else '<td>%s</td>') % c for i, c in enumerate(r)) for r in rows)
    return ('<div class="cpp-guide-table"><table class="cpp-skus-table"><caption>%s</caption><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>%s'
            % (E(caption), th, tr, '<p class="cpp-guide-note">%s</p>' % note if note else ''))


def link(products, slug, text=None):
    p = products.get(slug)
    if not p:
        return E(text or slug)
    return '<a href="%s">%s</a>' % (p[1], E(text or p[0]))


def entries(spec, slug):
    return [e['match'] for e in spec.get(slug, []) if e.get('match')]


# ------------------------------------------------------------------------------------------------
# guide definitions: each returns (title, meta_desc, h1, answer, facts, sections_html, faq, related)

def g_pet(spec, products):
    cups = sorted(entries(spec, 'pet-cups'), key=lambda a: _num(a['size']))
    lids = entries(spec, 'pet-cup-lids')
    rows = [[E(a['size']), E(a['lid-size']), E(a['pack-size']), _pal(a)] for a in cups]
    lid_rows = [[E(a['lid-type']), E(a['lid-size']), E(a['pack-size']), _pal(a)] for a in sorted(lids, key=lambda a: (a['lid-size'], a['lid-type']))]
    fit = {}
    for a in cups:
        fit.setdefault(a['lid-size'], []).append(a['size'])
    fit_txt = '; '.join('%s cups take the %s lid' % (' and '.join(v) if len(v) < 3 else ', '.join(v[:-1]) + ' and ' + v[-1], k)
                        for k, v in sorted(fit.items(), key=lambda kv: _num(kv[0])))
    answer = ('PET cup lids are sized by the cup rim in millimeters, not by ounces. In our line, %s. '
              'Any 98mm lid (flat, flat with straw hole, dome or slip-through) fits every 98mm cup, so one lid stock covers four cup sizes.' % fit_txt)
    sec = ('<section class="cpp-loc-sec"><h2>PET cup sizes and matching lids</h2>%s</section>'
           '<section class="cpp-loc-sec"><h2>PET cup lid types</h2><p>Flat lids with a straw hole are the default for iced coffee, tea and soft drinks. '
           'Dome lids leave room for whipped cream and blended drinks. Slip-through lids let a straw pass without a separate hole.</p>%s</section>'
           '<section class="cpp-loc-sec"><h2>How to choose a cup size</h2><ul class="cpp-guide-list">'
           '<li><b>9oz:</b> kids&rsquo; drinks, samples, water cups and smaller cold desserts.</li>'
           '<li><b>12oz to 16oz:</b> the standard small and medium for iced coffee, tea and soft drinks.</li>'
           '<li><b>20oz to 24oz:</b> large iced drinks, smoothies and boba.</li>'
           '<li><b>32oz:</b> extra-large drinks and party-size servings; it takes its own 107mm lid.</li></ul>'
           '<p>Standardizing on the 98mm rim (12oz to 24oz) is the easiest way to cut lid SKUs: four cup sizes, one lid size.</p></section>') % (
        table('PET cups: rim size, case pack and cases per pallet (from our spec sheets)', ['Cup size', 'Lid size (rim)', 'Case pack', 'Cases / pallet'], rows,
              'The 2026 catalog also lists a 12oz PET cup with a 90mm rim; ask for it on your quote if that is the lid you already stock.'),
        table('PET cup lids', ['Lid type', 'Fits rim', 'Case pack', 'Cases / pallet'], lid_rows))
    faq = [('What size lid fits a 16oz PET cup?', 'Our 16oz PET cup has a 98mm rim, so it takes any 98mm lid: flat, flat with straw hole, dome or slip-through. The same lids fit our 12oz (98mm), 20oz and 24oz cups.'),
           ('Do 12oz and 24oz PET cups use the same lid?', 'Yes, when both are 98mm-rim cups. In our line the 12oz (98mm), 16oz, 20oz and 24oz cups all share the 98mm lid.'),
           ('What lid fits a 32oz PET cup?', 'Our 32oz PET cup has a 107mm rim and takes the 107mm flat lid, packed 500 per case.'),
           ('How many PET cups are in a case?', '1,000 cups per case for 9oz through 24oz, and 500 per case for 32oz.'),
           ('Can I mix cup and lid sizes on one pallet?', 'Yes. Mixed pallets are welcome: combine cups, lids and any other products by the case on one order.')]
    return ('PET Cup Sizes and Lid Fit Chart (9oz to 32oz) | Crown Plastic & Paper',
            'Which lid fits which PET cup: 9oz takes 92mm, 12oz to 24oz take 98mm, 32oz takes 107mm. Case packs, cases per pallet and lid types from our spec sheets.',
            'PET Cup Sizes and Lid Fit Chart', answer,
            [('92mm', '9oz'), ('98mm', '12oz to 24oz'), ('107mm', '32oz'), ('1,000', 'cups per case')],
            sec, faq, ['pet-cups', 'pet-cup-lids', 'portion-cups', 'deli-containers'])


def g_portion(spec, products):
    cups = entries(spec, 'portion-cups')
    clear = sorted({a['size-oz'] for a in cups if a.get('color') == 'Clear'}, key=_num)
    rows = [[E(a['size-oz']), E(a.get('color', '')), E(a['pack-size']), _pal(a)] for a in sorted(cups, key=lambda a: _num(a['size-oz']))]
    rows += [['2oz', 'Black', '2500/Case', '—'], ['3.25oz', 'Black', '2500/Case', '—'], ['4oz', 'Black', '2500/Case', '—']]
    lid_rows = [['0.75oz to 1oz cups', '1oz lid', '2500/Case'], ['1.5oz to 2oz cups', '1.5–2oz lid', '2500/Case'], ['3.25oz to 5.5oz cups', '3.25–5.5oz lid', '2500/Case']]
    answer = ('Portion cups use three lid sizes: one lid for 0.75–1oz cups, one for 1.5–2oz cups, and one for 3.25–5.5oz cups. '
              'We stock clear portion cups in %s and black cups in 2oz, 3.25oz and 4oz, all 2,500 per case.' % ', '.join(clear))
    uses = ('<ul class="cpp-guide-list"><li><b>1oz:</b> ketchup, hot sauce, dipping sauces and samples.</li>'
            '<li><b>1.5oz to 2oz:</b> dressings, salsa and wing sauces.</li>'
            '<li><b>3.25oz to 4oz:</b> side sauces, guacamole, coleslaw, toppings and small desserts.</li>'
            '<li><b>5.5oz:</b> larger sides, fruit and pudding cups.</li></ul>'
            '<p>Black portion cups hide sauce stains and look more upscale on a dine-in plate; clear cups let customers see what they ordered at a glance.</p>')
    sec = ('<section class="cpp-loc-sec"><h2>Portion cup sizes</h2>%s</section>'
           '<section class="cpp-loc-sec"><h2>Which lid fits which portion cup</h2>%s</section>'
           '<section class="cpp-loc-sec"><h2>What each size is used for</h2>%s</section>') % (
        table('Portion cups: color, case pack and cases per pallet', ['Size', 'Color', 'Case pack', 'Cases / pallet'], rows,
              'Black cups are listed in our 2026 catalog; pallet counts for them come with your quote.'),
        table('Portion cup lids', ['Fits', 'Lid', 'Case pack'], lid_rows), uses)
    faq = [('What lid fits a 2oz portion cup?', 'The 1.5–2oz lid. It fits both 1.5oz and 2oz portion cups.'),
           ('Do 3.25oz and 4oz portion cups use the same lid?', 'Yes. One lid size covers 3.25oz, 4oz and 5.5oz portion cups.'),
           ('How many portion cups are in a case?', '2,500 cups per case for every size, and 2,500 lids per case.'),
           ('What is the most common portion cup size for sauces?', 'For to-go sauces and dressings, 1.5oz to 2oz is a common choice; 1oz is typical for ketchup and hot sauce.'),
           ('Do you sell portion cups and lids together?', 'Cups and lids are sold as separate cases so you can match quantities to how you use them. Add both to one quote.')]
    return ('Portion Cup Sizes and Lid Chart (1oz to 5.5oz) | Crown Plastic & Paper',
            'Portion cup lid chart: one lid for 0.75–1oz, one for 1.5–2oz, one for 3.25–5.5oz cups. Sizes, colors, case packs and what each size is used for.',
            'Portion Cup Sizes and Lid Chart', answer,
            [('3 lids', 'cover every size'), ('1oz–5.5oz', 'clear cups'), ('Black', '2oz, 3.25oz, 4oz'), ('2,500', 'per case')],
            sec, faq, ['portion-cups', 'portion-cups-lids', 'deli-containers', 'pet-cups'])


def g_deli(spec, products):
    d = sorted(entries(spec, 'deli-containers'), key=lambda a: _num(a['size']))
    rows = [[E(a['size']), E(a['pack-size']), _tihi(a), _pal(a)] for a in d]
    answer = ('Heavy duty deli containers come in %s. The 8oz through 32oz sizes pack 240 per case and the 64oz packs 120 per case. '
              'Use 8oz to 12oz for sides and sauces, 16oz for soups and salads, 24oz to 32oz for entrées and family sides, and 64oz for catering and bulk prep.'
              % ', '.join(a['size'] for a in d))
    sec = ('<section class="cpp-loc-sec"><h2>Deli container sizes</h2>%s</section>'
           '<section class="cpp-loc-sec"><h2>Choosing a size</h2><ul class="cpp-guide-list">'
           '<li><b>8oz:</b> sides, dips, dressings and small salads.</li>'
           '<li><b>12oz:</b> rice, beans, small soups and fruit.</li>'
           '<li><b>16oz (one pint):</b> the standard soup and salad cup.</li>'
           '<li><b>24oz to 32oz (one quart):</b> entrées, large soups, family sides and kitchen prep.</li>'
           '<li><b>64oz:</b> catering portions and bulk storage in the walk-in.</li></ul></section>') % (
        table('Heavy duty deli containers: case pack and pallet configuration', ['Size', 'Case pack', 'Ti × Hi', 'Cases / pallet'], rows,
              'Ti × Hi is cases per layer × layers per pallet. Where a spec sheet&rsquo;s layers and total disagree we show the total only.'))
    faq = [('How many ounces is a pint deli container?', 'A pint deli container holds 16oz. A quart holds 32oz.'),
           ('How many deli containers are in a case?', '240 per case for 8oz, 12oz, 16oz, 24oz and 32oz, and 120 per case for 64oz.'),
           ('What size deli container is best for soup?', '16oz for a single serving and 32oz for a quart or a family portion.'),
           ('Can I order several deli container sizes on one pallet?', 'Yes. Mixed pallets are welcome, so you can combine sizes by the case.')]
    return ('Deli Container Sizes Chart (8oz to 64oz) | Crown Plastic & Paper',
            'Heavy duty deli container sizes from 8oz to 64oz: case packs (240 or 120), cases per pallet, and which size to use for soups, sides and catering.',
            'Deli Container Sizes Chart', answer,
            [('8oz–64oz', '6 sizes'), ('240', 'per case, 8–32oz'), ('120', 'per case, 64oz'), ('16oz', 'one pint')],
            sec, faq, ['deli-containers', 'portion-cups', 'black-containers', 'round-black-containers'])


def g_takeout(spec, products):
    rect = sorted(entries(spec, 'black-containers'), key=lambda a: _num(a['size']))
    rnd = sorted(entries(spec, 'round-black-containers'), key=lambda a: _num(a['size']))
    hinged = entries(spec, 'black-hinged-containers')
    bag = entries(spec, 'bagasse-hinged-containers')
    r1 = [[E(a['size']), E(a.get('shape', 'Rectangular')), E(a['pack-size']), _pal(a)] for a in rect] + \
         [[E(a['size']), 'Round', E(a['pack-size']), _pal(a)] for a in rnd]
    hk = lambda a: (_num(a['size']), a.get('compartments', ''))
    r2 = [[E(a['size']), E(a.get('compartments', '')), 'Black plastic', E(a['pack-size']), _pal(a)] for a in sorted(hinged, key=hk)] + \
         [['6" x 6"', '1-Compartment', 'Clear PET', '400/Case', '—'], ['8" x 8"', '1-Compartment', 'Clear PET', '200/Case', '—'], ['9" x 9"', '1-Compartment', 'Clear PET', '200/Case', '—'], ['9" x 9"', '3-Compartment', 'Clear PET', '200/Case', '—']] + \
         [[E(a['size']), E(a.get('compartments', '')), 'Bagasse (PFAS-free)', E(a['pack-size']), _pal(a)] for a in sorted(bag, key=hk)]
    answer = ('Our takeout containers come in three families: black-base containers sold as sets with lids in %s rectangular, a 48oz square and %s round; '
              'black and clear PET hinged containers from 6"×6" to 9"×9" (1 or 3 compartments); and PFAS-free bagasse hinged containers. '
              'Black-base containers pack 150 sets per case; black hinged containers pack 150 per case (6"×6": 300).'
              % (', '.join(a['size'] for a in rect if a.get('shape') != 'Square'), ', '.join(a['size'] for a in rnd)))
    sec = ('<section class="cpp-loc-sec"><h2>Black-base containers (rectangular, square and round)</h2>%s</section>'
           '<section class="cpp-loc-sec"><h2>Hinged containers (clamshells)</h2>%s</section>'
           '<section class="cpp-loc-sec"><h2>Matching container to menu</h2><ul class="cpp-guide-list">'
           '<li><b>16oz to 24oz rectangular:</b> single entrées, rice bowls and lunch specials.</li>'
           '<li><b>28oz to 38oz rectangular:</b> full plates with sides, pasta and stir-fry.</li>'
           '<li><b>48oz to 58oz:</b> family meals and catering trays.</li>'
           '<li><b>Round 16oz to 48oz:</b> soups, noodles, salads and poke.</li>'
           '<li><b>6"×6" hinged:</b> sandwiches, burgers and desserts. <b>9"×6":</b> sandwiches with sides. '
           '<b>8"×8" and 9"×9":</b> full meals; choose 3-compartment to keep sides apart.</li>'
           '<li><b>Bagasse:</b> the compostable, PFAS-free choice where foam or plastic is restricted.</li></ul></section>') % (
        table('Black-base takeout containers (sold as sets: base and lid)', ['Size', 'Shape', 'Case pack', 'Cases / pallet'], r1),
        table('Hinged containers', ['Size', 'Compartments', 'Material', 'Case pack', 'Cases / pallet'], r2,
              'Clear PET hinged containers are listed in our 2026 catalog; pallet counts come with your quote.'))
    faq = [('What size takeout container do I need for a full meal?', 'For an entrée with sides, a 28oz to 38oz rectangular black container or an 8"×8" or 9"×9" hinged container (3-compartment keeps sides separate).'),
           ('How many takeout containers are in a case?', 'Black-base rectangular, square and round containers pack 150 sets per case. Black hinged containers pack 150 per case, except 6"×6" at 300. Clear PET hinged: 200 to 400. Bagasse hinged: 200 to 500 depending on size.'),
           ('Are your bagasse containers PFAS-free?', 'Yes. Our bagasse (sugarcane fiber) hinged containers are PFAS-free.'),
           ('Do black containers come with lids?', 'Yes. Our black-base rectangular, square and round containers are sold as sets (base and lid), 150 sets per case.'),
           ('Can I mix container sizes on one order?', 'Yes. Order any mix by the case; mixed pallets are welcome.')]
    return ('Takeout Container Sizes Chart: Black, Round, Hinged and Bagasse | Crown Plastic & Paper',
            'Takeout container size chart: black rectangular 16oz–58oz, round 16oz–48oz, hinged 6"×6" to 9"×9" and PFAS-free bagasse. Case packs and what to use for each menu item.',
            'Takeout Container Sizes Chart', answer,
            [('16oz–58oz', 'black-base'), ('6"–9"', 'hinged'), ('PFAS-free', 'bagasse option'), ('150', 'per case, most sizes')],
            sec, faq, ['black-containers', 'round-black-containers', 'black-hinged-containers', 'bagasse-hinged-containers'])


def g_foil(spec, products):
    pans = entries(spec, 'round-foil-pans')
    steam = entries(spec, 'deep-steam-table-pans')
    slids = entries(spec, 'foil-lids-for-steam-table-pans')
    sheets = entries(spec, 'foil-sheets')
    rolls = entries(spec, 'foil-rolls')
    r1 = [['%s round pan' % E(a['size']), E(a['pack-size']), _pal(a)] for a in sorted(pans, key=lambda a: _num(a['size']))]
    r1 += [['%s deep steam table pan' % E(a['pan-size']), E(a['pack-size']), _pal(a)] for a in sorted(steam, key=lambda a: a['pan-size'], reverse=True)]
    r1 += [['Foil lid, %s pan' % E(a['pan-size'].lower()), E(a['pack-size']), _pal(a)] for a in sorted(slids, key=lambda a: a['pan-size'], reverse=True)]
    r1 += [['Board lid, 7" round pan', '500/Case', '—'], ['Board lid, 9" round pan', '500/Case', '—']]
    r2 = [['%s foil sheets' % E(a['sheet-size']), E(a['pack-size']), _pal(a)] for a in sheets]
    r2 += [['14" x 10.5" cushion foil', '6/500', '—']]
    r2 += [['%s roll, %s' % (E(a['size']), E(a['roll-type'].lower())), E(a['pack-size']), _pal(a)] for a in sorted(rolls, key=lambda a: (_num(a['size']), a['size'], a['roll-type']))]
    answer = ('A half-size steam table pan is exactly half a full-size pan, so two half pans fill one full-size slot in a chafer or steam table. '
              'We stock full-size deep pans (50 per case), half-size deep pans (100 per case) and fitted foil lids for both, plus 7" and 9" round pans (500 per case) '
              'with board lids, pop-up foil sheets and 12" and 18" foil rolls in standard and heavy duty.')
    sec = ('<section class="cpp-loc-sec"><h2>Foil pans and lids</h2>%s</section>'
           '<section class="cpp-loc-sec"><h2>Foil sheets and rolls</h2>%s</section>'
           '<section class="cpp-loc-sec"><h2>Standard or heavy duty foil?</h2><p>Standard foil covers wrapping, lining and short holds. '
           'Heavy duty is thicker: it resists tearing on bones and sharp edges and holds up on the grill and in long oven holds. '
           'Pop-up foil sheets (9"×10.75" and 12"×10.75") are pre-cut for fast wrapping of burgers, burritos and sandwiches.</p></section>') % (
        table('Foil pans and lids', ['Item', 'Case pack', 'Cases / pallet'], r1),
        table('Foil sheets and rolls', ['Item', 'Case pack', 'Cases / pallet'], r2,
              'Cushion foil and board lids are listed in our 2026 catalog; pallet counts come with your quote.'))
    faq = [('How many half-size pans fit in a full-size steam table slot?', 'Two. A half-size pan is half of a full-size pan, so two sit side by side in one full-size opening.'),
           ('How many foil pans are in a case?', 'Full-size deep steam table pans: 50 per case. Half-size deep: 100 per case. 7" and 9" round pans: 500 per case.'),
           ('Do your foil pans come with lids?', 'Lids are sold separately so you only buy what you need: foil lids for full- and half-size pans, and board lids for 7" and 9" round pans.'),
           ('What foil roll sizes do you carry?', '12"×1000\' standard, 18"×500\' standard and heavy duty, and 18"×1000\' standard and heavy duty.'),
           ('What is pop-up foil?', 'Pre-cut, interfolded foil sheets that dispense one at a time. We stock 9"×10.75" and 12"×10.75", 500 sheets per box, 6 boxes per case.')]
    return ('Foil Pan, Sheet and Roll Sizes Chart | Crown Plastic & Paper',
            'Foil pan sizes: full- and half-size steam table pans, 7" and 9" round pans, lids, pop-up foil sheets and 12" and 18" rolls. Case packs and pallet counts from our spec sheets.',
            'Foil Pan, Sheet and Roll Sizes', answer,
            [('2 half pans', '= 1 full-size slot'), ('50 / 100', 'full / half pans per case'), ('500', 'round pans per case'), ('12" & 18"', 'foil rolls')],
            sec, faq, ['deep-steam-table-pans', 'foil-lids-for-steam-table-pans', 'round-foil-pans', 'foil-sheets', 'foil-rolls'])


def g_gloves(spec, products):
    rows = []
    for slug, name in (('blue-nitrile-gloves', 'Blue nitrile'), ('black-nitrile-gloves', 'Black nitrile'),
                       ('vinyl-gloves', 'Clear vinyl'), ('synmax-vinyl-black-gloves', 'Black vinyl (Synmax)'), ('latex-gloves', 'Latex (white)')):
        es = entries(spec, slug)
        if not es:
            continue
        order = ['Small', 'Medium', 'Large', 'Extra Large']
        sizes = sorted({a['size'] for a in es}, key=lambda s: order.index(s) if s in order else 9)
        rows.append([link(products, slug, name), E(es[0].get('weight', '')), E(', '.join(s.replace('Extra Large', 'XL') for s in sizes)),
                     '10/100 (1,000 gloves)', _pal(es[0])])
    cmp_rows = [['Nitrile', 'Latex-free; strongest puncture and chemical resistance; snug fit', 'Raw meat and seafood, prep, cleaning, all-day kitchen use'],
                ['Vinyl', 'Lowest cost; looser fit; latex-free', 'Short tasks: sandwich line, serving, quick changes'],
                ['Latex', 'Very elastic, close fit; natural rubber latex can cause allergies', 'Non-food tasks where latex is allowed']]
    answer = ('Nitrile gloves are the best all-round food service glove: latex-free, more puncture-resistant than vinyl and fitted for long shifts. '
              'Vinyl is the low-cost choice for short tasks with frequent changes. Latex fits closely but carries an allergy risk, and some states restrict latex in food service. '
              'Our standard gloves are 3.5g and pack 10 boxes of 100 per case (1,000 gloves).')
    sec = ('<section class="cpp-loc-sec"><h2>Nitrile vs vinyl vs latex</h2>%s</section>'
           '<section class="cpp-loc-sec"><h2>Gloves we stock</h2>%s</section>'
           '<section class="cpp-loc-sec"><h2>Glove sizing tips</h2><p>Measure around the palm just below the knuckles: under 7.5" is usually Small, 7.5"–8.5" Medium, 8.5"–9.5" Large and over 9.5" XL. '
           'A glove that is too loose snags and slows prep; too tight tears early. Most kitchens stock Medium and Large in the highest volume.</p></section>') % (
        table('Glove materials compared', ['Material', 'What it is like', 'Best for'], cmp_rows),
        table('Disposable gloves in stock', ['Glove', 'Weight', 'Sizes', 'Case pack', 'Cases / pallet'], rows,
              'Food handling rules vary by state and county; check your local health code, especially for latex.'))
    faq = [('Which disposable gloves are best for food service?', 'Nitrile is the most versatile: latex-free, puncture-resistant and comfortable for long shifts. Vinyl works for short, low-risk tasks where gloves change often.'),
           ('Are nitrile gloves better than vinyl?', 'For durability, yes: nitrile resists punctures and tears better and fits more closely. Vinyl costs less and is fine for brief tasks like assembling sandwiches.'),
           ('How many gloves are in a case?', '1,000: ten boxes of 100 gloves.'),
           ('What does 3.5g mean on gloves?', 'It is the weight of one glove in grams, a common measure of thickness. 3.5g is a standard everyday weight for food service.'),
           ('Why choose black nitrile gloves?', 'Black gloves hide stains and look clean on an open line; they are popular in barbecue and open-kitchen restaurants.')]
    return ('Disposable Gloves Guide: Nitrile vs Vinyl vs Latex for Food Service | Crown Plastic & Paper',
            'Nitrile vs vinyl vs latex gloves for food service: which to use for which task, sizes, 3.5g weight and 1,000 gloves per case. Blue and black nitrile, clear and black vinyl, latex.',
            'Disposable Gloves: Nitrile vs Vinyl vs Latex', answer,
            [('Nitrile', 'best all-round'), ('3.5g', 'standard weight'), ('S–XL', 'sizes'), ('1,000', 'gloves per case')],
            sec, faq, ['blue-nitrile-gloves', 'black-nitrile-gloves', 'vinyl-gloves', 'synmax-vinyl-black-gloves', 'latex-gloves'])


def g_pallet(spec, products):
    rows = []
    skip = {'single-fold-napkins'}   # duplicate of single-multi-and-c-fold-napkins
    for slug, es in spec.items():
        if slug in skip:
            continue
        es = [e['match'] for e in es if e.get('match')]
        if not es or not any(_pal(a) != '—' for a in es):
            continue
        for a in es:
            if _pal(a) == '—':
                continue
            variant = ' · '.join(v for k, v in a.items() if k not in ('ti-x-hi', 'cases-pallets', 'pack-size', 'pack-configuration', 'weight') and v not in ('N/A', ''))
            pack = a.get('pack-size') or a.get('pack-configuration', '').split(' (')[0]
            name = products.get(slug, (slug.replace('-', ' ').title(),))[0]
            rows.append((name, variant, pack, _tihi(a), _pal(a), slug))
    rows.sort(key=lambda r: (r[0], _num(r[1]), r[1]))
    seen, trs = set(), []
    for name, variant, pack, tihi, pal, slug in rows:
        key = (name, variant, pack, pal)
        if key in seen:
            continue
        seen.add(key)
        trs.append([link(products, slug, name), E(variant), E(pack), tihi, pal])
    answer = ('Ti × Hi is how a pallet is built: Ti is the number of cases in one layer and Hi is the number of layers. Multiply them to get cases per pallet; '
              'for example, 15 × 8 means 15 cases per layer, 8 layers high, 120 cases. Our pallets range from 24 cases (large items such as 16oz to 20oz PET cups) '
              'to 360 cases (small register rolls). You do not have to order full pallets of one item: mixed pallets are welcome, and pricing tiers are %s.' % geo.F['tiers'])
    sec = ('<section class="cpp-loc-sec"><h2>Cases per pallet for every product</h2>%s</section>'
           '<section class="cpp-loc-sec"><h2>Ordering by the pallet</h2><ul class="cpp-guide-list">'
           '<li><b>Mixed pallets:</b> combine different products by the case on one pallet.</li>'
           '<li><b>Price tiers:</b> %s.</li>'
           '<li><b>Freight:</b> pallets ship by LTL freight from Houston in %s; a full truckload is the lowest cost per case.</li>'
           '<li><b>Receiving:</b> tell us if you need a liftgate, an appointment or a dock delivery when you order.</li></ul></section>') % (
        table('Cases per pallet (from our spec sheets)', ['Product', 'Variant', 'Case pack', 'Ti × Hi', 'Cases / pallet'], trs,
              'Ti × Hi is shown only where the layer count matches the pallet total on the spec sheet. Pallet counts can change with packaging; your quote confirms them.'),
        E(geo.F['tiers']), E(geo.F['ship']))
    faq = [('What does Ti × Hi mean?', 'Ti is the number of cases per layer on the pallet and Hi is the number of layers. Ti × Hi = cases per pallet. A 15 × 8 pallet holds 120 cases.'),
           ('How many cases are on a pallet of gloves?', '120 cases (15 × 8). Each case holds 1,000 gloves, so a pallet is 120,000 gloves.'),
           ('Can I order a mixed pallet?', 'Yes. Mixed pallets are welcome: combine any products by the case.'),
           ('What are your pallet price tiers?', 'Pricing is set by tier: %s.' % geo.F['tiers']),
           ('How fast do pallets ship?', 'Orders typically leave our Houston warehouse in %s.' % geo.F['ship'])]
    return ('Cases per Pallet and Ti × Hi for Every Product | Crown Plastic & Paper',
            'Pallet quantities for food service disposables: Ti × Hi and cases per pallet for cups, containers, foil, napkins, gloves, bags and more. Mixed pallets welcome.',
            'Cases per Pallet (Ti × Hi) for Every Product', answer,
            [('Ti × Hi', '= cases per pallet'), ('24–360', 'cases per pallet'), ('Mixed', 'pallets welcome'), ('3 tiers', 'pick-up, 6 and 12 pallets')],
            sec, faq, [])


GUIDES = [
    ('pet-cup-sizes', 'PET cup sizes and lid fit', g_pet),
    ('portion-cup-sizes', 'Portion cup sizes and lids', g_portion),
    ('deli-container-sizes', 'Deli container sizes', g_deli),
    ('takeout-container-sizes', 'Takeout container sizes', g_takeout),
    ('foil-pan-sizes', 'Foil pans, sheets and rolls', g_foil),
    ('disposable-gloves-guide', 'Nitrile vs vinyl vs latex gloves', g_gloves),
    ('cases-per-pallet', 'Cases per pallet (Ti × Hi)', g_pallet),
]

# product slug -> guide URL, for the "Size guide" link on product pages
PRODUCT_GUIDE = {}
FAQS = []          # (question, answer) from every guide, for llms-full.txt


def render_guide(slug, short, fn, spec, products, origin):
    title, desc, h1, answer, facts, sec, faq, related = fn(spec, products)
    FAQS.extend(faq)
    url = '/guides/%s/' % slug
    crumb_html, crumb_ld = crumbs([('Home', '/'), ('Guides', '/guides/'), (short, None)], origin)
    rel = ''
    if related:
        rel = ('<section class="cpp-loc-sec"><h2>Products in this guide</h2><ul class="cpp-loc-near">%s</ul></section>'
               % ''.join('<li><a href="%s">%s</a></li>' % (products[s][1], E(products[s][0])) for s in related if s in products))
        for s in related:
            PRODUCT_GUIDE.setdefault(s, (url, short))
    others = ''.join('<li><a href="/guides/%s/">%s</a></li>' % (s, E(n)) for s, n, _ in GUIDES if s != slug)
    art = {'@context': 'https://schema.org', '@type': 'Article', 'headline': h1, 'description': desc, 'url': origin + url,
           'mainEntityOfPage': origin + url, 'dateModified': UPDATED, 'datePublished': UPDATED, 'inLanguage': 'en-US',
           'author': {'@id': origin + '/#org'}, 'publisher': {'@id': origin + '/#org'}, 'about': short}
    body = ''.join([
        hero(crumb_html, h1, answer, facts),
        '<div class="cpp-loc cpp-guide" data-cpp-upgrade><div class="cpp-wrap">', sec, rel,
        '<section class="cpp-loc-sec"><h2>How ordering works</h2><ol class="cpp-loc-steps"><li><b>Send your list.</b> Products, sizes and case counts through the quote form, by phone, text or WhatsApp.</li>'
        '<li><b>Get one wholesale quote.</b> Case and pallet pricing for the whole list, delivered or Houston pick-up.</li>'
        '<li><b>We ship from Houston.</b> Orders typically leave the warehouse in %s. Approved accounts get Net 30.</li></ol></section>' % E(geo.F['ship']),
        '<section class="cpp-loc-sec"><h2>More guides</h2><ul class="cpp-loc-near">%s<li><a href="/catalog/">2026 catalog</a></li></ul></section>' % others,
        '<p class="cpp-guide-updated">Updated %s. Figures come from Crown Plastic &amp; Paper product spec sheets.</p>' % 'November 2026',
        '</div></div>', faq_block('Questions about %s' % short.lower().replace('pet', 'PET'), faq), crumb_ld, ld(art)])
    return url, title, desc, body


def hub(origin):
    crumb_html, crumb_ld = crumbs([('Home', '/'), ('Guides', None)], origin)
    cards = ''.join('<li><a href="/guides/%s/"><strong>%s</strong></a></li>' % (s, E(n)) for s, n, _ in GUIDES)
    data = {'@context': 'https://schema.org', '@type': 'CollectionPage', 'name': 'Food service packaging size guides', 'url': origin + '/guides/',
            'hasPart': [{'@type': 'Article', 'name': n, 'url': '%s/guides/%s/' % (origin, s)} for s, n, _ in GUIDES]}
    body = ''.join([
        hero(crumb_html, 'Food Service Packaging Size Guides',
             'Size charts and buying guides built from our own spec sheets: which lid fits which cup, how many cases fit on a pallet, and which container or glove to use for each job.',
             [('%d guides' % len(GUIDES), 'with size charts'), ('Spec-sheet', 'figures'), ('Updated', 'November 2026'), ('Free', 'to use and share')]),
        '<div class="cpp-loc cpp-guide" data-cpp-upgrade><div class="cpp-wrap">',
        '<section class="cpp-loc-sec"><h2>Size charts</h2><ul class="cpp-loc-near cpp-guide-hub">%s</ul></section>' % cards,
        '<section class="cpp-loc-sec"><h2>More reading</h2><ul class="cpp-loc-near"><li><a href="/category/product-guides/">Product guides on our blog</a></li>'
        '<li><a href="/catalog/">2026 product catalog</a></li><li><a href="/locations/">Service areas and transit times</a></li><li><a href="/industries/">Who we supply</a></li></ul></section>',
        '</div></div>', crumb_ld, ld(data)])
    return ('/guides/', 'Food Service Packaging Size Guides and Charts | Crown Plastic & Paper',
            'Free size charts for food service disposables: PET cup lid fit, portion cups, deli and takeout containers, foil pans, gloves and cases per pallet.', body)


def all_pages(spec, products, origin):
    PRODUCT_GUIDE.clear()
    FAQS.clear()
    pages = [render_guide(s, n, fn, spec, products, origin) for s, n, fn in GUIDES]
    return [hub(origin)] + pages
