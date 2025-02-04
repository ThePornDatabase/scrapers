import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteDoubleViewCastingSpider(BaseSceneScraper):
    name = 'DoubleViewCasting'
    network = 'Double View Casting'
    parent = 'Double View Casting'
    site = 'Double View Casting'

    start_urls = [
        'http://doubleviewcasting.com',
    ]

    selector_map = {
        'title': '//div[@class="main-content"]/div[contains(@class, "scene-title")]/h3/text()',
        'description': '//div[@class="info-description"]/p/text()',
        'image': '//div[@class="scene-player"]/video/@poster',
        'performers': '//li[@class="models"]/a/text()',
        'tags': '//li[@class="tags"]/a/text()',
        'external_id': r'.*/(\d+)$',
        'pagination': '/scenes/page/%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//li/a[contains(@href, "/scene/")]')
        for scene in scenes:
            meta = {}
            date = scene.xpath('.//span[@class="date"]/text()')
            if date:
                date = date.get()
                date = re.search(r'(\w+ \d{1,2}, \d{4})', date).group(1)
                meta['date'] = self.parse_date(date, date_formats=['%B %d, %Y']).isoformat()
            scene = scene.xpath('./@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_title(self, response):
        title = super().get_title(response)
        return title.strip(":")
