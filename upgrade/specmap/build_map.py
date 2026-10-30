"""Builds upgrade/assets/spec-map.json: product slug -> list of {match: {attr: value}, file, label}.
Run once when new spec sheets arrive; apply.py reads the JSON."""
import json, os, re, sys
SPEC_DIR, PRODUCTS, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
files = set(os.listdir(SPEC_DIR))
products = json.load(open(PRODUCTS))

def f(name):
    fn = name if name.endswith('.pdf') else name + '-spec-sheet.pdf'
    if fn not in files:
        raise SystemExit('missing file: ' + fn)
    return fn

GLOVE_SIZE = {'Small': 's', 'Medium': 'm', 'Large': 'l', 'Extra Large': 'xl'}
def rule(slug, a):
    g = lambda k: a.get(k, '')
    if slug == 'bagasse-hinged-containers':
        return {('8" x 8"', '3-Compartment'): '8-x-8-3-compartment-bagasse-hinged-container', ('9" x 9"', '1-Compartment'): '9-x-9-1-compartment-bagasse-hinged-container-991cmfc-200',
                ('9" x 6"', '1-Compartment'): '9-x-6-bagasse-hinged-container-96mfc-250', ('6" x 6"', '1-Compartment'): '6-x-6-bagasse-hinged-container-66mfc-500',
                ('9" x 9"', '3-Compartment'): '9-x-9-3-compartment-bagasse-hinged-container-993cmfc-200'}[(g('size'), g('compartments'))]
    if slug == 'black-hinged-containers':
        return {('6" x 6"', '1-Compartment'): '6-x-6-hinged-container-dchc6-1c', ('9" x 6"', '1-Compartment'): '9-x-6-hinged-container-dchc963-1c',
                ('8" x 8"', '3-Compartment'): '8-x-8-3-compartment-dchc8-3c', ('8" x 8"', '1-Compartment'): '8-x-8-1-compartment-dchc8-1c',
                ('9" x 9"', '3-Compartment'): '9-x-9-3-compartment-dchc9-3c', ('9" x 9"', '1-Compartment'): '9-x-9-1-compartment-dchc9-1c'}[(g('size'), g('compartments'))]
    if slug == 'beverage-napkins':
        return {'Black': '2-ply-black-beverage-napkins-bbn-1000', 'White': '1-ply-white-beverage-napkins-wbn-4000'}[g('color')]
    if slug == 'black-containers':
        if g('shape') == 'Square': return '48oz-square-containers'
        return {'16oz': '16oz-rectangular-black-containers-bcre16', '24oz': '24oz-rectangular-black-containers-bcre-24', '28oz': '28oz-rectangular-black-containers-bcre-28',
                '32oz': '32oz-rectangular-black-containers-bcre-32', '38oz': '38oz-rectangular-black-containers-bcre-38', '58oz': '58oz-rectangular-black-containers-bcre-58'}[g('size')]
    if slug == 'black-nitrile-gloves':
        s = GLOVE_SIZE[g('size')]; return '3-5g-black-nitrile-gloves-10-100-case-%s-bng-%s1000' % (s, s)
    if slug == 'blue-nitrile-gloves':
        s = GLOVE_SIZE[g('size')]; return '3-5g-blue-nitrile-gloves-10-100-case-%s-beng-%s1000' % (s, s)
    if slug == 'synmax-vinyl-black-gloves':
        s = GLOVE_SIZE[g('size')]; return 'black-synmax-vinyl-gloves-10-100-case-%s-bvg-%s1000' % (s, s)
    if slug == 'latex-gloves':
        return {'Small': 'latex-gloves-small-mg-s35s', 'Medium': 'latex-gloves-medium-mg-s35m', 'Large': 'latex-gloves-large-mg-s35l', 'Extra Large': 'latex-gloves-extra-large-mg-s35xl'}[g('size')]
    if slug == 'vinyl-gloves':
        if g('color') == 'Blue': return None          # site has Blue Medium; the zip only has Blue Small
        s = GLOVE_SIZE[g('size')]; return 'vinyl-gloves-clear-10-100-case-%s-cvg-%s-1000' % (s, s)
    if slug == 'checker-deli-paper-wrap':
        return {'Black Checker': '12-x-12-black-checker-fdp12bk', 'Red Checker': '12-x-12-red-checker-fdp12rc', 'Blue Checker': '12-x-12-blue-checker-fdp12bc'}[g('design-color')]
    if slug == 'deep-steam-table-pans':
        return {'Full Size': 'full-size-deep-steam-pans-fsdfp-50', 'Half Size': 'half-size-deep-steam-pans-hsdfp-100'}[g('pan-size')]
    if slug == 'foil-lids-for-steam-table-pans':
        return {'Full Size': 'foil-lids-for-full-size-pans-fsal-50', 'Half Size': 'foil-lids-for-half-size-pans-hsal-100'}[g('pan-size')]
    if slug == 'deli-containers':
        n = g('size').replace('oz', ''); return 'deli-containers-%soz-dc%s-%s' % (n, n, '120' if n == '64' else '240')
    if slug == 'disposable-cutlery-kits':
        if g('kit-type') == 'Spork': return '3pcs-sprk-kit-white-medium-weight-ck3wmwpp-1000'
        return {('Black', 'PP', 'Medium-weight'): '6pcs-cutlery-kit-black-medium-weight-ckmwbpp-250', ('White', 'PP', 'Heavy-weight'): '6pcs-cutlery-kit-white-heavy-weight-pp-ckhwwpp-250',
                ('White', 'PP', 'Medium-weight'): '6pcs-cutlery-kit-white-medium-weight-ckmwwpp-250', ('Black', 'PP', 'Heavy-weight'): '6pcs-cutlery-kit-black-heavy-weight-pp-ckhwbpp-250',
                ('Black', 'PS', 'Heavy-weight'): '6pcs-cutlery-kit-black-heavy-weight-ps-ckhwbps-250'}[(g('color'), g('material'), g('weight-class'))]
    if slug == 'foil-rolls':
        size = g('size').replace('’', "'"); hd = g('roll-type') == 'Heavy Duty'
        w, l = re.match(r'(\d+)" x (\d+)', size).groups()
        return '%s-x%s-foil-rolls-%s-fr%s%s-%s' % (w, l, 'heavy-duty' if hd else 'standard', 'hd' if hd else 's', w, l)
    if slug == 'foil-sheets':
        return {'9" x 10.75"': '9-x10-75-foil-sheets-fs9-500', '12" x 10.75"': '12-x10-75-foil-sheets-fs12-500'}[g('sheet-size')]
    if slug == 'food-film':
        w = re.match(r'(\d+)"', g('size')).group(1); return '%s-x2000-food-film-ff%s-2000' % (w, w)
    if slug == 'interfold-napkins':
        return {'White': 'interfold-napkins-white-ifw6000', 'Kraft': 'interfold-napkins-kraft-ifk6000'}[g('color')]
    if slug == 'interfold-wax-paper':
        w = re.match(r'(\d+)"', g('sheet-size')).group(1); return '%s-x-10-75-interfold-wax-paper-ez-%s' % (w, w)
    if slug == 'jumbo-roll-tissue':
        return {"1000'": '1000-jumbo-roll-tissue', "750'": '750-jumbo-roll-tissue'}[g('roll-length')]
    if slug == 'kraft-white-kitchen-roll-towels':
        if g('roll-type') == 'Kitchen Roll Towel': return '2-ply-kitchen-roll-towel-mftw-4008'
        return {("350'", 'Kraft'): '350-hand-roll-towel-kraft-hrtw300', ("350'", 'White'): '350-hand-roll-towel-white',
                ("800'", 'Kraft'): '800-hand-roll-towel-kraft-hrtw800', ("800'", 'White'): '800-hand-roll-towel-white-mftk-4008'}[(g('length'), g('color'))]
    if slug == 'paper-bags':
        n = g('size-bag-capacity').split()[0]; color = g('color')
        if color == 'Kraft' and n == '1': return None    # no 1 lb kraft sheet in the zip
        if color == 'Kraft': return {'12': '12-kraft'}.get(n, '%s-kraft-bpb-%s' % (n, n))
        return '%s-white-wpb-%s' % (n, n)
    if slug == 'paper-boat-trays':
        return {'1/4 lb': '1-4-lb-red-plaid', '1/2 lb': '1-2-lb-red-plaid', '1 lb': '1-lb-red-plaid', '2 lb': '2-lb-red-plaid', '3 lb': '3-lb-red-plaid', '5 lb': '5-lb-red-plaid'}[g('tray-size-capacity')]
    if slug == 'pet-cup-lids':
        return {('Dome Lid', '98mm'): '98mm-dome-lid-dl-98-1000', ('Flat Lid', '107mm'): '107mm-flat-lid-32oz-flwh107-500',
                ('Flat Lid With Hole', '98mm'): '98mm-flat-lid-with-hole-flwh98-1000', ('Slip Thru Lid', '98mm'): '98mm-slip-thru-stl-98-1000'}[(g('lid-type'), g('lid-size'))]
    if slug == 'pet-cups':
        return {'9oz': '9oz-pet-cups-pet9-92-1000', '12oz': '12oz-pet-cups-98mm-pet12-98-1000', '16oz': '16oz-pet-cups-98mm-pet16-98-1000',
                '20oz': '20oz-pet-cups-98mm-pet20-98-1000', '24oz': '24oz-pet-cups-98mm-pet24-98-1000', '32oz': '32oz-pet-cups-107mm-pet32-500'}[g('size')]
    if slug == 'poly-bags':
        return {'8" x 4" x 18"': '8x4x18-poly-bag-14ib-pb8418', '12" x 6" x 24"': '12x6x24-poly-bag-16ib-pb12624', '23" x 17" x 34"': '23x17x34-poly-bag-14ib-pb231734'}[g('bag-size')]
    if slug == 'portion-cups-lids':
        return {'1oz': 'lids-for-1oz-portion-cups-pcl1-2500', '1.5–2oz': 'lids-for-1-5-2oz-portion-cups-pcl2-2500', '3.25–5.5oz': 'lids-for-3-25-5-5oz-portion-cups-pcl325-2500'}[g('size')]
    if slug == 'portion-cups':
        oz, c = g('size-oz'), g('color')
        if c == 'Black':
            return {'3.25oz': '3-25oz-black-portion-cups-pcb325-2500', '4oz': '4oz-black-portion-cups-pcb4-2500', '5.5oz': '5-5oz-black-portion-cups'}[oz]
        return {'1oz': '1oz-clear-portion-cups-pc1-2500', '1.5oz': '1-5oz-clear-portion-cups-pc15-2500', '2oz': '2oz-clear-portion-cups-pc2-2500', '3.25oz': '3-25oz-clear-portion-cups-pc325-2500',
                '4oz': '4oz-clear-portion-cups-pc4-2500', '5.5oz': '5-5oz-clear-portion-cups-pc55-2500'}[oz]
    if slug == 'register-roll-paper':
        return {'3" x 165\'': '3-x165-bond-paper-trp3-165', '3" x 95\'': '3-x95-thermal-roll-paper', '3 1/8" x 230\'': '3-1-8-x230-thermal-roll-paper-trp230-50',
                '3 1/8" x 273\'': '3-1-8-x273-thermal-roll-paper-trp318-273', '2 1/4" x 50\'': '2-1-4-x50-thermal-roll-paper-trp214-50', '2 1/4" x 85\'': '2-1-4-x85-thermal-roll-paper-trp214-85'}[g('roll-size')]
    if slug == 'round-black-containers':
        return {'16oz': '16oz-round-black-containers', '24oz': '24oz-round-black-containers-bcro-24', '32oz': '32oz-round-black-containers-bcro-32', '48oz': '48oz-round-black-containers-bcro-48'}[g('size')]
    if slug == 'round-foil-pans':
        return {'7"': 'round-foil-pans-7-rfp7-500', '9"': 'round-foil-pans-9-rfp9-500'}[g('size')]
    if slug in ('single-fold-napkins', 'single-multi-and-c-fold-napkins'):
        return {('Single Fold', 'Kraft'): 'single-fold-napkins-kraft', ('Single Fold', 'White'): 'single-fold-napkins-white',
                ('Multifold', 'Kraft'): 'multifold-napkins-kraft', ('Multifold', 'White'): 'multifold-napkins-white'}[(g('napkin-type'), g('color'))]
    if slug == 'trash-liners':
        t = g('thickness').split()[0].replace('.', '-'); return '60gal-black-38x58-llpde-%s-mil' % t
    raise KeyError(slug)

SINGLE = {'bakery-tissue': ['6-x-10-75-bakery-tissue-t-6p'], 'c-fold-towel': ['c-fold-towel-cftw-2400'], 'cushion-foil-wrap': ['10-5-x-14-cushion-foil-wrap-fsw66u'],
          'dinner-napkins': ['2-ply-dinner-napkins-dn2p3000'], 'individual-wrapped-bath-tissue': ['individual-wrapped-bath-tissue'], 'menu-tissue-paper': ['12-x-12-menu-tissue-paper-ft12mu'],
          'patty-wax-paper': ['5-5-x-5-5-patty-wax-paper-p-55'], 'round-plates': ['9-round-plates-9mfrp-500'], 'school-trays': ['school-trays-mft-500'],
          'stretch-film': ['18-x1500x80g'], 'tall-fold-napkins': ['tall-fold-napkins-tfn-10000'],
          'round-foil-pan-lids': ['board-lids-for-7-round-pans-rfpl7-500', 'board-lids-for-9-round-pans-rfpl9-500', 'round-dome-lid-7', 'round-dome-lid-9']}
SINGLE_LABEL = {'board-lids-for-7-round-pans-rfpl7-500': '7" board lid', 'board-lids-for-9-round-pans-rfpl9-500': '9" board lid', 'round-dome-lid-7': '7" dome lid', 'round-dome-lid-9': '9" dome lid'}
SKIP_ATTRS = ('cases-pallets', 'ti-x-hi', 'pack-size', 'pack-configuration', 'weight', 'gauge')

out, used, gaps = {}, set(), []
for slug, p in products.items():
    entries = []
    if not p['vars']:
        for name in SINGLE[slug]:
            fn = f(name); used.add(fn); entries.append({'match': {}, 'file': fn, 'label': SINGLE_LABEL.get(name, '')})
    else:
        for v in p['vars']:
            a = v['attrs']; name = rule(slug, a)
            label = ' · '.join(x for k, x in a.items() if k not in SKIP_ATTRS and x and x != 'N/A')
            if name is None:
                gaps.append(slug + ': ' + label); continue
            fn = f(name); used.add(fn)
            entries.append({'match': {k: x for k, x in a.items()}, 'file': fn, 'label': label})
    out[slug] = entries
json.dump(out, open(OUT, 'w'), indent=1, ensure_ascii=False)
print('products:', len(out), '| sheets placed:', sum(len(v) for v in out.values()), '| distinct files used:', len(used))
print('options without a sheet:', gaps)
print('files not used:', sorted(files - used))
