#!/usr/bin/env bash
# Takes a fresh static snapshot of www.crownplasticandpaper.com into site/.
# Run by the "Snapshot live site" GitHub Action (Actions tab > Run workflow).
set -u
SITE=www.crownplasticandpaper.com
command -v wget >/dev/null 2>&1 || dnf install -y wget >/dev/null 2>&1 || yum install -y wget >/dev/null 2>&1
rm -rf mirror site && mkdir -p mirror
cd mirror
wget --mirror --page-requisites --adjust-extension --convert-links --no-parent \
  --restrict-file-names=windows -e robots=off --timeout=30 --tries=3 \
  --span-hosts --domains=crownplasticandpaper.com,www.crownplasticandpaper.com \
  --reject-regex='(wp-json|/feed/|xmlrpc|wp-login|wp-admin|replytocom|/login/|/my-account/|/cart/|/checkout/|add-to-cart|\?s=)' \
  --user-agent='Mozilla/5.0 (compatible; site-copy)' \
  https://$SITE/ 2>&1 | tail -n 5 || true
cd ..
if [ -d mirror/$SITE ]; then mv mirror/$SITE site; else mv mirror/crownplasticandpaper.com site; fi
echo "Localizing remaining live-site assets..."
(command -v python3 >/dev/null 2>&1 || dnf install -y python3 >/dev/null 2>&1) && python3 localize.py || echo "localize step failed (copy still works, some assets load from live site)"
echo "Creating WebP versions of large images..."
python3 -m pip install -q pillow >/dev/null 2>&1 || true
python3 upgrade/optimize_images.py site || echo "image optimization skipped"
echo "files: $(find site -type f | wc -l)  size: $(du -sh site | cut -f1)"
test -f site/index.html
