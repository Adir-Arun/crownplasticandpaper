"""The /catalog/ page: the 2026 product catalog as a page-turning flipbook on our own domain.

Page images are pre-rendered from the catalog PDF (upgrade/assets/catalog/pages/page-NN-{t,s,l,x}.webp):
  t = 200px thumbnail, s = 800px tall, l = 1600px tall, x = full 200dpi (used by the hover magnifier).
catalog.json holds each page's title and text lines, pulled from the PDF, for search and for search engines.
"""
import html
import json
import os
import re

URL = '/catalog/'
PDF = '/catalog/crown-product-catalog-2026.pdf'
UPDATED = '2026-11-04'
TITLE = '2026 Product Catalog | Crown Plastic & Paper'
DESC = ('Flip through the 2026 Crown Plastic & Paper wholesale catalog: PET cups, portion cups, deli and hinged '
        'containers, foil, napkins, paper bags, gloves, towels and trash liners. Zoom in on any page or download the PDF.')


def load(assets):
    return json.load(open(os.path.join(assets, 'catalog', 'catalog.json'), encoding='utf-8'))


def img(n, size):
    return '/catalog/pages/page-%02d-%s.webp' % (n, size)


def _products(lines):
    """Product names from a page's text: lines that read like a product, not a pack size or spec."""
    out = []
    for l in lines[1:]:
        if re.match(r'^[\d.,/ ]+(/Case|/Box|Sets|Count)?$', l, re.I) or re.match(r'^(Clear|Black|White|LLDPE|HDPE|Standard|Heavy[- ]Duty|Medium Weight|Heavy Weight|Fits \d+mm lids|\d+(\.\d+)? mil|[\d"”.x ]+)$', l, re.I):
            continue
        if len(l) < 4 or len(l) > 70 or l in out:
            continue
        out.append(l)
    return out


def body(pages, origin):
    n_pages = len(pages)
    toc = [p for p in pages if p['n'] > 2 and p['title'] not in ('Who We Are',)]
    book = []
    for p in pages:
        n = p['n']
        alt = '%s, catalog page %d' % (p['title'], n)
        hard = ' data-density="hard"' if n in (1, n_pages) else ''
        book.append(
            '<div class="cv-page"%s data-n="%d"><img src="%s" srcset="%s 566w, %s 1131w" sizes="(min-width: 900px) 42vw, 92vw" '
            'data-zoom="%s" alt="%s" width="566" height="800" %s decoding="async" draggable="false"></div>'
            % (hard, n, img(n, 's'), img(n, 's'), img(n, 'l'), img(n, 'x'), html.escape(alt),
               'fetchpriority="high"' if n <= 3 else 'loading="lazy"'))
    thumbs = ''.join(
        '<li><button type="button" class="cv-thumb" data-go="%d" aria-label="Go to page %d: %s"><img src="%s" alt="" width="70" height="99" loading="lazy"><span>%d</span></button></li>'
        % (p['n'], p['n'], html.escape(p['title']), img(p['n'], 't'), p['n']) for p in pages)
    toc_html = ''.join(
        '<li><button type="button" data-go="%d"><span>%s</span><span class="cv-toc-n">%d</span></button></li>'
        % (p['n'], html.escape(p['title']), p['n']) for p in toc)
    search_data = [{'n': p['n'], 't': p['title'], 'l': p['lines'][1:]} for p in pages]

    inside = []
    for p in toc:
        prods = _products(p['lines'])
        inside.append('<li><a href="#page/%d" data-go="%d"><img src="%s" alt="" width="70" height="99" loading="lazy">'
                      '<span><strong>%s</strong><span class="cv-in-p">Page %d</span><span class="cv-in-items">%s</span></span></a></li>'
                      % (p['n'], p['n'], img(p['n'], 't'), html.escape(p['title']), p['n'], html.escape(', '.join(prods[:8]))))

    ld = {
        '@context': 'https://schema.org', '@type': 'DigitalDocument', 'name': 'Crown Plastic & Paper 2026 Product Catalog',
        'url': origin + URL, 'encodingFormat': 'application/pdf', 'inLanguage': 'en-US', 'numberOfPages': n_pages,
        'dateModified': UPDATED, 'publisher': {'@id': origin + '/#org'},
        'hasPart': [{'@type': 'WebPageElement', 'name': p['title'], 'url': '%s%s#page/%d' % (origin, URL, p['n'])} for p in toc],
        'associatedMedia': {'@type': 'MediaObject', 'contentUrl': origin + PDF, 'encodingFormat': 'application/pdf'},
    }

    return ('<link rel="stylesheet" href="/catalog/catalog.css?v=1">'
            '<main class="cv" id="catalog">'
            '<header class="cv-head"><div class="cv-head-in">'
            '<p class="cv-eyebrow">2026 Product Catalog</p>'
            '<h1>Our full wholesale line, page by page</h1>'
            '<p class="cv-lead">Cups, containers, foil, paper and janitorial supplies stocked in our Houston warehouse. '
            'Hover over any page to zoom in, or download the PDF to share with your team.</p>'
            '<div class="cv-head-cta"><a class="cv-btn cv-btn--solid" href="/get-your-quote/">Request a Quote</a>'
            '<a class="cv-btn cv-btn--line" href="%(pdf)s" download>Download PDF <span class="cv-muted">(2.6 MB)</span></a></div>'
            '</div></header>'
            '<section class="cv-shell" id="cv-shell" aria-label="Catalog viewer">'
            '<div class="cv-bar" role="toolbar" aria-label="Catalog controls">'
            '<button type="button" class="cv-tool" id="cv-menu" aria-expanded="false" aria-controls="cv-drawer"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 6h16M4 12h16M4 18h10"/></svg><span>Contents</span></button>'
            '<div class="cv-nav"><button type="button" class="cv-tool cv-icon" id="cv-prev" aria-label="Previous page"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15 5l-7 7 7 7"/></svg></button>'
            '<span class="cv-count" id="cv-count" aria-live="polite">1 / %(n)d</span>'
            '<button type="button" class="cv-tool cv-icon" id="cv-next" aria-label="Next page"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 5l7 7-7 7"/></svg></button></div>'
            '<div class="cv-tools">'
            '<button type="button" class="cv-tool cv-fine" id="cv-lens-t" aria-pressed="true" title="Magnifier: hover over a page to zoom"><svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="10.5" cy="10.5" r="6.5"/><path d="M15.5 15.5L21 21M10.5 7.5v6M7.5 10.5h6"/></svg><span>Magnifier</span></button>'
            '<button type="button" class="cv-tool cv-icon" id="cv-zoom" aria-label="Open this page full size" title="Open page full size"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M14 4h6v6M20 4l-7 7M10 20H4v-6M4 20l7-7"/></svg></button>'
            '<button type="button" class="cv-tool cv-icon" id="cv-fs" aria-label="Full screen" title="Full screen"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 3H3v5M16 3h5v5M8 21H3v-5M16 21h5v-5"/></svg></button>'
            '<a class="cv-tool cv-icon" href="%(pdf)s" download aria-label="Download PDF" title="Download PDF"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 4v11M7 10l5 5 5-5M5 20h14"/></svg></a>'
            '</div></div>'
            '<div class="cv-stage" id="cv-stage"><div class="cv-book" id="cv-book">%(book)s</div>'
            '<div class="cv-lens" id="cv-lens" aria-hidden="true"></div>'
            '<p class="cv-hint" id="cv-hint">Hover to magnify &middot; click a page or use &larr; &rarr; to turn</p></div>'
            '<nav class="cv-thumbs" aria-label="Pages"><ol>%(thumbs)s</ol></nav>'
            '<div class="cv-drawer" id="cv-drawer" hidden><div class="cv-drawer-in">'
            '<div class="cv-drawer-head"><strong>Contents</strong><button type="button" class="cv-tool cv-icon" id="cv-close" aria-label="Close contents"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg></button></div>'
            '<label class="cv-search"><svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="10.5" cy="10.5" r="6.5"/><path d="M15.5 15.5L21 21"/></svg>'
            '<input type="search" id="cv-q" placeholder="Search the catalog, e.g. 32oz" autocomplete="off" aria-label="Search the catalog"></label>'
            '<ol class="cv-results" id="cv-results" hidden></ol>'
            '<ol class="cv-toc" id="cv-toc">%(toc)s</ol>'
            '</div></div>'
            '</section>'
            '<section class="cv-inside" aria-labelledby="cv-inside-h"><div class="cv-inside-in">'
            '<h2 id="cv-inside-h">What&rsquo;s inside</h2>'
            '<p>%(cats)d product lines across %(n)d pages. Pick a section to jump straight to it.</p>'
            '<ol class="cv-inside-grid">%(inside)s</ol>'
            '<div class="cv-cta"><div><h2>Need pricing on anything in the catalog?</h2>'
            '<p>Send us your list and we&rsquo;ll quote case and pallet pricing, delivered or Houston pick-up. Approved accounts get Net 30.</p></div>'
            '<div class="cv-cta-btns"><a class="cv-btn cv-btn--solid" href="/get-your-quote/">Request a Quote</a>'
            '<a class="cv-btn cv-btn--line" href="https://wa.me/17135975320">WhatsApp (713) 597-5320</a></div></div>'
            '</div></section>'
            '<div class="cv-zoomview" id="cv-zoomview" hidden role="dialog" aria-modal="true" aria-label="Page full size">'
            '<button type="button" class="cv-zv-close" id="cv-zv-close" aria-label="Close">&times;</button><div class="cv-zv-scroll" id="cv-zv-scroll"><img id="cv-zv-img" alt=""></div><p class="cv-zv-tip">Tap the page to zoom in or out</p></div>'
            '</main>'
            '<script type="application/json" id="cv-data">%(data)s</script>'
            '<script type="application/ld+json">%(ld)s</script>'
            '<script src="/catalog/page-flip.min.js?v=2.0.7" defer></script>'
            '<script src="/catalog/catalog.js?v=1" defer></script>'
            % {'pdf': PDF, 'n': n_pages, 'book': ''.join(book), 'thumbs': thumbs, 'toc': toc_html,
               'cats': len(toc), 'inside': ''.join(inside),
               'data': json.dumps(search_data, ensure_ascii=False).replace('</', '<\\/'),
               'ld': json.dumps(ld, ensure_ascii=False).replace('</', '<\\/')})
