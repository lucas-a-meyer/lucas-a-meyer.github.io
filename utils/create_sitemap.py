import os
from re import L
import pandas as pd
import datetime as dt
import json

posts_dir = ["_site/posts", "_site/articles"]

site_pages = []
url_list = []
site_root = "https://www.meyerperin.com"

for dir in posts_dir:
    # assign folder with dir excluding docs/
    folder = dir[5:]
    for root, dirs, files in os.walk(dir):
        for name in files:
            if name.endswith(".html"):
                d = {}
                target = os.path.join(root, name)
                last_updated_timestamp = os.path.getmtime (target)
                last_updated_time = dt.datetime.utcfromtimestamp(last_updated_timestamp)
                d["lastmod"] = last_updated_time.strftime("%Y-%m-%dT%H:%M:%S.000Z")
                url_target = f"{site_root}{folder}/{target[len(dir)+1:]}"
                d["loc"] = url_target
                site_pages.append(d)
                url_list.append(url_target)

df_sites = pd.DataFrame(site_pages)
df_sites.to_xml("_site/sitemap.xml", index=False, row_name="url", root_name="urlset", namespaces={"": "http://www.sitemaps.org/schemas/sitemap/0.9"})

json_dict = {}
json_dict["host"] = "www.meyerperin.com"
json_dict["key"] = "b2ef8541f4a041a0a2b32fff426e64d8"
json_dict["keyLocation"] = "https://www.meyerperin.com/b2ef8541f4a041a0a2b32fff426e64d8.txt"
json_dict["urlList"] = url_list
with open("_site/sitemap.json", "w") as fj:
    json.dump(json_dict, fj, indent=4)