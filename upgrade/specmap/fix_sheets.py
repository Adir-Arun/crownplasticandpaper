"""Correct individual values on existing spec-sheet PDFs (upgrade/assets/spec-sheets).

The sheets were generated once from product data; when a figure is corrected we patch the
text in place (same font, size, color and position) instead of regenerating the whole set.
Run from the repo root:  python3 upgrade/specmap/fix_sheets.py
Requires PyMuPDF (pip install pymupdf). Idempotent: a value that is already correct is skipped.

2026-11-27 corrections confirmed by Adir:
  poly bags 1,000 per case; stretch film rolls 1,000 ft (sheet renamed to 18-x1000x80g);
  napkin pallet counts from the 2026 catalog (white beverage 13 x 8 = 104, interfold 45,
  multifold 8 x 6 = 48).
"""
import os
import shutil
import sys

import pymupdf

DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets', 'spec-sheets')

# file -> (new file name or None, [(row label or None for the title, old text, new text)])
FIXES = {
    '8x4x18-poly-bag-14ib-pb8418-spec-sheet.pdf': (None, [('Pack Size', '100/Case', '1,000/Case'),
                                                           ('Ti x Hi', '9 x 10', '8 x 11'), ('Cases / Pallet', '90', '88')]),
    '12x6x24-poly-bag-16ib-pb12624-spec-sheet.pdf': (None, [('Pack Size', '100/Case', '1,000/Case')]),
    '23x17x34-poly-bag-14ib-pb231734-spec-sheet.pdf': (None, [('Pack Size', '100/Case', '1,000/Case')]),
    '18-x1500x80g-spec-sheet.pdf': ('18-x1000x80g-spec-sheet.pdf', [(None, '18"x1500x80G', '18"x1000x80G'),
                                                                    ('Product', '18"x1500x80G', '18"x1000x80G')]),
    '18-x1000x80g-spec-sheet.pdf': (None, [('Ti x Hi', '11 x 6', '10 x 9'), ('Cases / Pallet', '66', '90')]),
    '1-ply-white-beverage-napkins-wbn-4000-spec-sheet.pdf': (None, [('Ti x Hi', '12 x 9', '13 x 8'), ('Cases / Pallet', '108', '104')]),
    'interfold-napkins-white-ifw6000-spec-sheet.pdf': (None, [('Cases / Pallet', '54', '45')]),
    'interfold-napkins-kraft-ifk6000-spec-sheet.pdf': (None, [('Cases / Pallet', '72', '45')]),
    'multifold-napkins-white-spec-sheet.pdf': (None, [('Ti x Hi', '7 x 7', '8 x 6'), ('Cases / Pallet', '49', '48')]),
    'multifold-napkins-kraft-spec-sheet.pdf': (None, [('Ti x Hi', '7 x 7', '8 x 6'), ('Cases / Pallet', '49', '48')]),
    # pallet counts from the 2026 catalog
    '5-lb-red-plaid-spec-sheet.pdf': (None, [('Ti x Hi', '9 x 7', '8 x 5'), ('Cases / Pallet', '63', '40')]),
    'full-size-deep-steam-pans-fsdfp-50-spec-sheet.pdf': (None, [('Ti x Hi', '7 x 4', '6 x 5'), ('Cases / Pallet', '28', '30')]),
    'round-dome-lid-7-spec-sheet.pdf': (None, [('Ti x Hi', '20 x 10', '10 x 5'), ('Cases / Pallet', '200', '50')]),
    'round-dome-lid-9-spec-sheet.pdf': (None, [('Ti x Hi', '20 x 10', '10 x 5'), ('Cases / Pallet', '200', '50')]),
}


def spans(page):
    for b in page.get_text('dict')['blocks']:
        for l in b.get('lines', []):
            for s in l['spans']:
                yield s


def bg_at(pix, x, y):
    r, g, b = pix.pixel(int(x), int(y))[:3]
    return (r / 255, g / 255, b / 255)


def fix(name, new_name, edits):
    src = os.path.join(DIR, name)
    if not os.path.exists(src):
        if new_name and os.path.exists(os.path.join(DIR, new_name)):
            print('already fixed:', new_name)
            return
        raise SystemExit('missing ' + src)
    doc = pymupdf.open(src)
    page = doc[0]
    pix = page.get_pixmap()
    all_spans = list(spans(page))
    todo = []
    for label, old, new in edits:
        if label is None:
            cands = [s for s in all_spans if s['text'].strip() == old and s['size'] >= 16]
        else:
            row = [s for s in all_spans if s['text'].strip() == label]
            if not row:
                raise SystemExit('%s: no row %r' % (name, label))
            y = row[0]['bbox'][1]
            cands = [s for s in all_spans if s['text'].strip() == old and abs(s['bbox'][1] - y) < 2 and s['bbox'][0] > row[0]['bbox'][2]]
        if not cands:
            if any(s['text'].strip() == new for s in all_spans):
                continue
            raise SystemExit('%s: %r not found' % (name, old))
        s = cands[0]
        x0, y0, x1, y1 = s['bbox']
        todo.append((s, new, bg_at(pix, max(0, x0 - 2), (y0 + y1) / 2)))
    if not todo and not new_name:
        print('already fixed:', name)
        return
    for s, new, bg in todo:
        x0, y0, x1, y1 = s['bbox']
        page.add_redact_annot(pymupdf.Rect(x0 - 0.5, y0, x1 + 0.5, y1), fill=bg)
    page.apply_redactions(images=pymupdf.PDF_REDACT_IMAGE_NONE, graphics=pymupdf.PDF_REDACT_LINE_ART_NONE)
    for s, new, bg in todo:
        font = 'hebo' if 'Bold' in s['font'] else 'helv'
        c = s['color']
        color = ((c >> 16 & 255) / 255, (c >> 8 & 255) / 255, (c & 255) / 255)
        x = s['origin'][0]
        if s['size'] >= 16:   # centered title
            w_old = pymupdf.get_text_length(s['text'], fontname=font, fontsize=s['size'])
            w_new = pymupdf.get_text_length(new, fontname=font, fontsize=s['size'])
            x += (w_old - w_new) / 2
        page.insert_text((x, s['origin'][1]), new, fontname=font, fontsize=s['size'], color=color)
    out = os.path.join(DIR, new_name or name)
    tmp = out + '.tmp'
    doc.save(tmp, garbage=3, deflate=True)
    doc.close()
    shutil.move(tmp, out)
    if new_name:
        os.remove(src)
    print('fixed:', new_name or name, [(n) for _, n, _ in todo])


if __name__ == '__main__':
    for name, (new_name, edits) in FIXES.items():
        fix(name, new_name, edits)
    sys.exit(0)
