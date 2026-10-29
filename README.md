# crownplasticandpaper

Static copy of www.crownplasticandpaper.com with an upgrade layer, hosted on Vercel.

## How it works
- `site/` is a snapshot of the WordPress site (pages, images, CSS, JS, fonts).
  Refresh it from GitHub: **Actions > Snapshot live site > Run workflow**. That runs
  `snapshot.sh` (download + `localize.py` + WebP images) and commits the result.
- On every deploy Vercel runs `build.sh`, which applies `upgrade/apply.py` to `site/`.
  All improvements live in `upgrade/`, so a fresh snapshot gets the same upgrades.

## What the upgrade layer does (`upgrade/`)
- Fixes inconsistent contact details (phone (844) 900-8804 and one email), stale catalog button,
  copyright year, the "Home old" menu item and links that pointed nowhere.
- Accessibility: one H1 per page, working "Skip to content", visible keyboard focus,
  readable alt text, larger touch targets and minimum text sizes on phones.
- Performance: pages use WebP images (about 85% smaller) and decode images async.
- Homepage: nationwide shipping map from Houston.
- Phones: a Call / Get a Quote bar.
- Product search that works without WordPress (`upgrade/search-index.json`).
- Forms (contact, quote, newsletter) are delivered by FormSubmit (formsubmit.co) to
  info@crownplasticandpaper.com, with a loading state, confirmation and an email/phone
  fallback if the service can't be reached. FormSubmit needs a one-time activation:
  the first submission sends an "Activate Form" email to that inbox.
- Brand: "AR Unlimited Supply" is replaced with "Crown Plastic & Paper" (titles, Google
  structured data, sharing tags, text) and AR's sales email with info@crownplasticandpaper.com.
- Google structured data: invalid comments removed and URLs made absolute.

## Limits of the static copy
Search, login and cart don't run on a static site; the upgrade layer replaces search and
forms as described above.
