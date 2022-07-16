import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteWakeUpNFuckSpider(BaseSceneScraper):
    name = 'WakeUpNFuck'
    network = 'Karak Ltd'
    parent = 'Woodman Casting X'
    site = 'Wake Up N Fuck'

    start_urls = [
        'https://www.wakeupnfuck.com',
    ]

    selector_map = {
        'title': '//h2/text()',
        'description': '',
        'date': '',
        'image': '//script[contains(text(), "image")]/text()',
        're_image': r'image:.+?(http.*?\.\w{3,4})\"',
        'performers': '//div[@class="starring"]/a//p/text()',
        'tags': '//div[@class="tags"]/ul/li/a/text()',
        'trailer': '//script[contains(text(), "image")]/text()',
        're_trailer': r'url:.*?(http.*?\.mp4)',
        'external_id': r'.*/(.*)',
        'pagination': '/scene?page=%s'
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//a[contains(@href, "/scene/")]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_date(self, response):
        scenedate = response.xpath('//div[@class="description"]/text()').getall()
        scenedate = " ".join(scenedate)
        if re.search(r'(\d{1,2} \w+ \d{4})', scenedate):
            scenedate = re.search(r'(\d{1,2} \w+ \d{4})', scenedate).group(1)
            return self.parse_date(scenedate, date_formats=['%d %B %Y']).isoformat()
        return self.parse_date('today').isoformat()
