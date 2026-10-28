#!/usr/bin/env bash
# Builds a static copy of www.crownplasticandpaper.com at deploy time.
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
echo "files: $(find site -type f | wc -l)  size: $(du -sh site | cut -f1)"
test -f site/index.html
