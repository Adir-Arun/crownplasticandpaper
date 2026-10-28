#!/usr/bin/env python3
"""Create a .webp next to every large PNG/JPEG in the snapshot (name.png -> name.png.webp).

The original stays in place (social previews, old links). apply.py points pages
at the .webp only when it exists, and it is only kept when it is at least 10%
smaller than the original. Needs Pillow: pip install pillow
"""
import os
import sys
from concurrent.futures import ProcessPoolExecutor

from PIL import Image

SITE = sys.argv[1] if len(sys.argv) > 1 else 'site'
MIN_BYTES = 15 * 1024


def convert(path):
    out = path + '.webp'
    try:
        if os.path.exists(out) and os.path.getmtime(out) >= os.path.getmtime(path):
            return 0, 0
        size = os.path.getsize(path)
        with Image.open(path) as im:
            im.load()
            if im.mode in ('P', 'LA', 'RGBA'):
                im = im.convert('RGBA')
            elif im.mode != 'RGB':
                im = im.convert('RGB')
            w, h = im.size
            if w > 2400:  # nothing on the site is shown wider than this
                im = im.resize((2400, round(h * 2400 / w)), Image.LANCZOS)
            im.save(out, 'WEBP', quality=80, method=5)
        new = os.path.getsize(out)
        if new > size * 0.9:
            os.remove(out)
            return 0, 0
        return size, new
    except Exception as e:
        print('skip %s (%s)' % (path, e))
        if os.path.exists(out):
            os.remove(out)
        return 0, 0


def main():
    files = []
    for d, _, fs in os.walk(SITE):
        for f in fs:
            if '&' in f:
                continue
            if f.lower().endswith(('.png', '.jpg', '.jpeg')):
                p = os.path.join(d, f)
                if os.path.getsize(p) >= MIN_BYTES:
                    files.append(p)
    before = after = n = 0
    with ProcessPoolExecutor() as ex:
        for b, a in ex.map(convert, files, chunksize=8):
            if b:
                before += b; after += a; n += 1
    print('webp: %d of %d images, %.1f MB -> %.1f MB' % (n, len(files), before / 1048576, after / 1048576))


if __name__ == '__main__':
    main()
