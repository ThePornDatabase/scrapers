import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SitePersiasPalaceSpider(BaseSceneScraper):
    name = 'PersiasPalace'
    network = 'Persias Palace'
    parent = 'Persias Palace'
    site = 'Persias Palace'

    start_urls = [
        'https://persiaspalace.com',
    ]

    selector_map = {
        'title': '//div[contains(@class, "info-left")]/h3/text()',
        'description': '//div[@class="preview-content"]/p/text()',
        'date': '//div[contains(@class, "info-left")]//i[contains(@class, "calendar")]/following-sibling::text()',
        'image': '//div[contains(@class, "player-thumb")]//img/@src0_1x',
        'performers': '',
        'tags': '//div[@class="tag-btn"]/a/text()',
        'duration': '//div[contains(@class, "info-left")]//i[contains(@class, "clock")]/following-sibling::text()',
        're_duration': r'((?:\d{1,2}\:)?\d{2}\:\d{2})',
        'trailer': '',
        'external_id': r'.*/(.*?)\.htm',
        'pagination': '/categories/movies_%s_d.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "grid-item-inner")]/a[1]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_performers(self, response):
        return['Persia Monir']

    def get_duration(self, response):
        duration = response.xpath('//div[contains(@class, "info-left")]//i[contains(@class, "clock")]/following-sibling::text()')
        if duration:
            duration = duration.getall()
            duration = "".join(duration)
            duration = re.search(r'((?:\d{1,2}\:)?\d{2}\:\d{2})', duration)
            if duration:
                return self.duration_to_seconds(duration.group(1))
        return None

    def get_image(self, response):
        image = super().get_image(response)
        if not image or image in response.url:
            image = response.xpath('//div[contains(@class, "player-thumb")]//img/@src')
            if image:
                image = self.format_link(response, image.get())
        return image
