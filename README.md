# crownplasticandpaper

Static copy of www.crownplasticandpaper.com, hosted on Vercel.

On every deploy, `build.sh` downloads the live site (pages, images, CSS, JS, fonts)
with `wget` and Vercel serves the result from `site/`.

Notes:
- Forms (contact, newsletter, quote), search and login depend on WordPress and do not work in the static copy.
- Changes made in WordPress appear here after the next deploy.
- `localize.py` downloads files WordPress only references lazily (images, scripts) so the copy does not depend on the live site.
