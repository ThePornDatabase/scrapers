import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteDownBlouseWowSpider(BaseSceneScraper):
    name = 'DownblouseWow'
    site = 'Downblouse Wow'
    parent = 'Downblouse Wow'
    network = 'Downblouse Wow'

    start_urls = [
        'https://downblousewow.com/?videos',
    ]

    selector_map = {
        'title': '//h2[@class="name"]/text()',
        'description': '',
        'date': '//div[@class="info"]//p[contains(text(), "Added")]/text()',
        're_date': r'(\w+ \d{1,2}, \d{4})',
        'image': '//div[@class="container"]//div[@class="row"]/p[1]/a[1]/img/@src',
        'performers': '//h2[@class="name"]/text()',
        'tags': '//div[@class="info"]//p[@class="tags"]/a/text()',
        'duration': '',
        'trailer': '',
        'external_id': r'lid=(\d+)',
        'pagination': '',
        'type': 'Scene',
    }

    def start_requests(self):
        for link in self.start_urls:
            yield scrapy.Request(link, callback=self.get_scenes, headers=self.headers, cookies=self.cookies)

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="itemminfo"]/p[1]/a/@href').getall()
        for scene in scenes:
            if "join" not in scene:
                meta['id'] = re.search(r'lid=(\d+)', scene).group(1)
                if meta['id']:
                    yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_duration(self, response):
        duration = response.xpath('//div[@class="info"]//p[contains(text(), "Added")]/text()')
        if duration:
            duration = duration.get()
            duration = re.search(r'(\d+\.\d+)min', duration)
            if duration:
                duration = duration.group(1)
                duration = str(int(float(duration) * 60))
                return duration
        return None
