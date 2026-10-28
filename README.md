# crownplasticandpaper

Static copy of www.crownplasticandpaper.com with an upgrade layer, hosted on Vercel.

## How it works
- `site/` is a snapshot of the WordPress site (pages, images, CSS, JS, fonts).
  Refresh it from GitHub: **Actions > Snapshot live site > Run workflow**. That runs
  `snapshot.sh` (download + `localize.py` + WebP images) and commits the result.
- On every deploy Vercel runs `build.sh`, which applies `upgrade/apply.py` to `site/`.
  All improvements live in `upgrade/`, so a fresh snapshot gets the same upgrades.

## What the upgrade layer does (`upgrade/`)
- Fixes inconsistent contact details (one phone number and email), stale catalog button,
  copyright year, the "Home old" menu item and links that pointed nowhere.
- Accessibility: one H1 per page, working "Skip to content", visible keyboard focus,
  readable alt text, larger touch targets and minimum text sizes on phones.
- Performance: pages use WebP images (about 85% smaller) and decode images async.
- Homepage: nationwide shipping map from Houston.
- Phones: a Call / Get a Quote bar.
- Product search that works without WordPress (`upgrade/search-index.json`).
- Forms open the visitor's email app with the message filled in, since WordPress
  can't receive form posts here.

## Limits of the static copy
Search, login, cart and WordPress form handling don't run on a static site; the upgrade
layer replaces search and forms as described above.
