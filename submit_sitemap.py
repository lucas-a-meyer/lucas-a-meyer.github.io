import requests
import time
import json

wait = 10
url = "https://www.meyerperin.com/sitemap.xml"
print(f"Waiting {wait} seconds to submit sitemap...")
time.sleep(wait)
requests.get("https://www.google.com/ping?sitemap={url}")
print(f"Sitemap {url} submitted to Google")

headers = {"content-type": "application/json", "charset": "utf-8"}
indexnow_url = "https://www.bing.com/indexnow"
with open ("docs/sitemap.json") as fj:
    indexnow_json = json.load(fj)
requests.post(indexnow_url, indexnow_json, headers=headers)