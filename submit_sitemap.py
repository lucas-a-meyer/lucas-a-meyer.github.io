import requests
import time
import json

wait = 60
url = "https://www.meyerperin.com/sitemap.xml"
print(f"Waiting {wait} seconds to submit sitemap...")
time.sleep(wait)
r = requests.get(f"https://www.google.com/ping?sitemap={url}")
print(f"Sitemap {url} submitted to Google with response {r.status_code}")

headers = {"Content-Type": "application/json; charset=utf-8"}
headers["Host"]="www.bing.com"

indexnow_url = "https://www.bing.com/indexnow"
with open ("docs/sitemap.json") as fj:
    indexnow_json = json.load(fj)

response = requests.post(indexnow_url, json=indexnow_json, headers=headers)
print(f"Submitted to IndexNow with response {response.status_code}")
