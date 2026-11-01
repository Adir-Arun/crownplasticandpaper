#!/usr/bin/env bash
# Tell Bing, Yandex and other IndexNow engines that the site changed.
# Run after a production deploy is live:  bash scripts/indexnow.sh
set -euo pipefail
HOST=crownplasticandpaper.com
KEY=4926503e2eb4d675df74dc7347df8da2
URLS=$(curl -fsS "https://$HOST/sitemap.xml" | grep -o '<loc>[^<]*</loc>' | sed 's#</\?loc>##g' | python3 -c 'import json,sys; print(json.dumps([l.strip() for l in sys.stdin if l.strip()]))')
curl -fsS -X POST https://api.indexnow.org/indexnow -H "Content-Type: application/json; charset=utf-8" \
  -d "{\"host\":\"$HOST\",\"key\":\"$KEY\",\"keyLocation\":\"https://$HOST/$KEY.txt\",\"urlList\":$URLS}" \
  -o /dev/null -w "IndexNow: HTTP %{http_code} for $(echo "$URLS" | python3 -c 'import json,sys;print(len(json.load(sys.stdin)))') URLs\n"
