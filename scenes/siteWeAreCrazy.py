import re
import requests
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
true = True
false = False


class SiteWeAreCrazySpider(BaseSceneScraper):
    name = 'WeAreCrazy'
    network = 'We Are Crazy'
    parent = 'We Are Crazy'
    site = 'We Are Crazy'

    start_urls = [
        'https://wearecrazy.com',
    ]

    # cookies = [{"name":"agreedToDisclaimer","value":"true"},{"name":"unq_trfc","value":"1"}]
    cookies = [{
                "domain": "wearecrazy.com",
                "hostOnly": true,
                "httpOnly": false,
                "name": "agreedToDisclaimer",
                "path": "/",
                "sameSite": "unspecified",
                "secure": false,
                "session": false,
                "storeId": "0",
                "value": "true"
            }
        ]


    selector_map = {
        'title': '//h1/text()',
        'description': '//div[contains(@id, "Description")]/div//text()',
        'date': '//td[contains(text(), "Released")]/following-sibling::td[1]/text()',
        'image': '',
        'performers': '//td[contains(text(), "Starring")]/following-sibling::td[1]/a/text()',
        'tags': '//td[contains(text(), "Categories")]/following-sibling::td[1]/a/text()',
        'external_id': r'vd/(\d+)/',
        'pagination': '/videos/page%s/',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = self.copy_meta(response)
        scenes = response.xpath('//div[contains(@class,"video-list-view")]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_tags(self, response):
        tags = super().get_tags(response)
        if 'Virtual Reality' not in tags:
            tags.append('Virtual Reality')
        return sorted(filter(None, tags))
    
    def get_image(self, response):
        image_sets = response.xpath('//div[@class="carousel"]/div//img/@srcset')
        if image_sets:
            image_sets = image_sets.getall()
            entries = []
            for s in image_sets:
                for part in s.split(','):
                    m = re.match(r'\s*(\S+)\s+(\d+)w', part)
                    if m:
                        u, w = m.group(1), m.group(2)
                        n = re.search(r'gallery_(\d+)', u)
                        if n:
                            entries.append((int(n.group(1)), -int(w), u))
            if entries:
                return min(entries)[2]
        return ''
