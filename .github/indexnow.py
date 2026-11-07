"""Submit every sitemap URL of the three sites to IndexNow (Bing, Yandex, Seznam, Naver).
Each host proves ownership with its own key file at the site root."""
import json, re, sys, time, urllib.request

SITES = [
    ("crownplasticandpaper.com", "c8f1449ae78498555cb06798fb61d7ba", "/sitemap.xml"),
    ("www.arunlimitedsupply.com", "d670ead75a65015ff22982eb45ab8e9f", "/sitemap_index.xml"),
    ("www.goldabeautystar.co.il", "d365d1f86e9d488ea61aa343c501dd30", "/sitemap.xml"),
]
UA = {"User-Agent": "indexnow-submit/1.0"}


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
        return r.read().decode("utf-8", "replace")


def urls_from(url, seen=None):
    seen = seen if seen is not None else set()
    body = get(url)
    locs = re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", body)
    if "<sitemapindex" in body:
        out = []
        for child in locs:
            if child not in seen:
                seen.add(child)
                out += urls_from(child, seen)
        return out
    # page URLs only (skip image:loc entries, which sit inside <image:image>)
    return [u for u in re.findall(r"<url>\s*<loc>\s*([^<\s]+)", body)]


failed = False
for host, key, sitemap in SITES:
    for _ in range(20):  # wait for the key file to be live
        try:
            if get(f"https://{host}/{key}.txt").strip() == key:
                break
        except Exception as e:
            print(host, "key not live yet:", e)
        time.sleep(15)
    else:
        print(host, "KEY FILE NOT LIVE, skipped"); failed = True; continue
    urls = sorted(set(u for u in urls_from(f"https://{host}{sitemap}") if f"//{host}/" in u))
    body = json.dumps({"host": host, "key": key, "keyLocation": f"https://{host}/{key}.txt",
                       "urlList": urls[:10000]}).encode()
    req = urllib.request.Request("https://api.indexnow.org/indexnow", data=body, method="POST",
                                 headers={"Content-Type": "application/json; charset=utf-8", **UA})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            print(f"{host}: {len(urls)} URLs -> HTTP {r.status}")
    except urllib.error.HTTPError as e:
        print(f"{host}: {len(urls)} URLs -> HTTP {e.code} {e.read()[:300]!r}"); failed = True
sys.exit(1 if failed else 0)
