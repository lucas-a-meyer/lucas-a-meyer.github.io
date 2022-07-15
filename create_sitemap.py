import os
from re import L
import pandas as pd
import datetime as dt


posts_dir = "docs/posts"

site_pages = []
site_root = "https://www.meyerperin.com/posts"
for root, dirs, files in os.walk(posts_dir):
    for name in files:
        d = {}
        target = os.path.join(root, name)
        last_updated_timestamp = os.path.getmtime (target)
        last_updated_time = dt.datetime.utcfromtimestamp(last_updated_timestamp)
        d["lastmod"] = last_updated_time.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        url_target = f"{site_root}{target[len(posts_dir):]}"
        d["loc"] = url_target
        site_pages.append(d)

df_sites = pd.DataFrame(site_pages)
df_sites.to_xml("docs/sitemap.xml", index=False, row_name="url", root_name="urlset", namespaces={"": "http://www.sitemaps.org/schemas/sitemap/0.9"})
# requests.get