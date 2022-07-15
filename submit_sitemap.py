import requests
import time

wait = 10
url = "https://www.meyerperin.com/sitemap.xml"
print(f"Waiting {wait} seconds to submit sitemap...")
time.sleep(wait)
requests.get("https://www.google.com/ping?sitemap={url}")
print(f"Sitemap {url} submitted to Google")
