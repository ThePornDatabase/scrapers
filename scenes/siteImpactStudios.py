import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteImpactStudiosSpider(BaseSceneScraper):
    name = 'ImpactStudios'
    network = 'ImpactStudios'
    parent = 'ImpactStudios'
    site = 'ImpactStudios'

    start_urls = [
        'https://impactstudiosbondage.com',
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '//div[@class="videoDescription"]/p//text()',
        'date': '//h1/following-sibling::div[1]//i[contains(@class, "calendar")]/following-sibling::text()',
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//div[@class="models"]/ul/li/a/text()',
        'tags': '//div[@class="tags"]/ul/li/a/text()',
        'duration': '//h1/following-sibling::div[1]//i[contains(@class, "clock")]/following-sibling::text()',
        'trailer': '',
        'external_id': r'',
        'pagination': '/updates?page=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="videoPic"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_id(self, response):
        image = super().get_image(response)
        sceneid = re.search(r'thumbs/(\d+)/', image)
        if sceneid:
            return sceneid.group(1)
        else:
            return re.search(r'.*/(.*)', response.url).group(1)
