import re
import xml.etree.ElementTree as ET
import requests
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
true = True
false = False

class SiteHouseholdFantasySpider(BaseSceneScraper):
    name = 'HouseholdFantasy'
    network = 'Household Fantasy'
    parent = 'Household Fantasy'
    site = 'Household Fantasy'

    selector_map = {
        'title': '//h1/text()',
        'description': '//div[contains(@class,"elementor-widget-theme-post-content")]/div[@class="elementor-widget-container"]/p//text()',
        'performers': '//span[@class="elementor-post-info__terms-list"]/a[contains(@href, "/tag/")]/text()',
        'tags': '//span[@class="elementor-post-info__terms-list"]/a[contains(@href, "/category/")]/text()',
        'external_id': r'',
        'pagination': '',
        'type': 'Scene',
    }

    async def start(self):
        meta = {}
        meta['page'] = self.page

        start_url = 'https://householdfantasy.com/post-sitemap.xml'
        yield scrapy.Request(start_url, callback=self.get_scenes, meta=meta)

    def get_scenes(self, response):
        ns = {
            's': 'http://www.sitemaps.org/schemas/sitemap/0.9',
            'image': 'http://www.google.com/schemas/sitemap-image/1.1',
        }
        root = ET.fromstring(response.text)
        for entry in root.findall('s:url', ns):
            loc = entry.findtext('s:loc', namespaces=ns)
            if not loc:
                continue

            meta = dict(response.meta)
            meta['url'] = loc
            m = re.search(r'.*/(.*?)/$', loc)
            if m:
                meta['id'] = m.group(1)

            lastmod = entry.findtext('s:lastmod', namespaces=ns) or ''
            if lastmod:
                meta['date'] = lastmod[:10]

            image_loc = entry.findtext('image:image/image:loc', namespaces=ns)
            if image_loc:
                meta['image'] = image_loc

            if self.check_item(meta, self.days):
                meta['image_blob'] = self.get_image_blob_from_link(meta['image'])
                yield scrapy.Request(url=loc, callback=self.parse_scene, meta=meta)

    def get_image_from_link(self, image):
        if not image:
            return None
        try:
            r = requests.get(
                image,
                headers={
                    'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                                   '(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'),
                    'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
                },
                timeout=15,
            )
        except requests.RequestException as e:
            # print(f"get_image_from_link: {image} failed: {e}")
            return None
        # print(f"get_image_from_link: {image} -> {r.status_code}")
        if r.status_code == 200:
            return r.content
        return None
