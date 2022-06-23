import sys
import logging
from pysitemap import crawler

if __name__ == '__main__':
    if '--iocp' in sys.argv:
        from asyncio import events, windows_events
        sys.argv.remove('--iocp')
        logging.info('using iocp')
        el = windows_events.ProactorEventLoop()
        events.set_event_loop(el)

    # root_url = sys.argv[1]
    root_url = 'https://www.meyerperin.com'
    crawler(root_url, out_file='sitemap.xml', exclude_urls=[".pdf", ".jpg", ".png", ".csv", ".gz", ".pptx", ".ppt", ".docx", ".xlsx"])
