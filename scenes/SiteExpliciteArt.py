import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteExpliciteArtSpider(BaseSceneScraper):
    name = 'ExpliciteArt'
    site = 'Explicite-Art'
    parent = 'Explicite-Art'
    network = 'Explicite-Art'

    start_urls = [
        'https://www.explicite-art.com'
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '//div[@class="player-info-desc"]/p/text()',
        'duration': '//div[@class="player-info-left"]//span[contains(text(), "RUNTIME")]/following-sibling::text()[1]',
        'performers': '//div[@class="player-info-row"]/a[contains(@href, "/pornstars/")]/text()',
        'tags': '//span[@class="tags"]/a[contains(@href, "channel")]/text()',
        'type': 'Scene',
        'external_id': r'.*-(\d+)\.htm',
        'pagination': '/visitor/videos/page%s.html',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="content"]/a[1]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_image(self, response):
        image = response.xpath('//script[contains(text(), "image")]/text()')
        if image:
            image = image.get()
            image = image.replace("\r", "").replace("\t", "").replace("\n", "").replace(" ", "").strip()
            image = re.search(r'image:.*?(http.*?)[\'\"]', image)
            if image:
                image = image.group(1)
                return image

    def get_trailer(self, response):
        trailer = response.xpath('//script[contains(text(), "image")]/text()')
        if trailer:
            trailer = trailer.get()
            trailer = trailer.replace("\r", "").replace("\t", "").replace("\n", "").replace(" ", "").strip()
            trailer = re.search(r'file:.*?(/media.*?)[\'\"]', trailer)
            if trailer:
                trailer = trailer.group(1)
                return self.format_link(response, trailer)

    def get_performers(self, response):
        performers = super().get_performers(response)
        performers2 = []
        for performer in performers:
            if "compilation" not in performer.lower():
                if "film" not in performer.lower():
                    if "sex" not in performer.lower():
                        performers2.append(performer)
        return performers2

    def get_performers_data(self, response):
        performers = self.get_performers(response)
        performers_data = []
        if len(performers):
            for performer in performers:
                perf = {}
                perf['name'] = performer
                perf['extra'] = {}
                perf['extra']['gender'] = "Female"
                perf['network'] = "Explicite-Art"
                perf['site'] = "Explicite-Art"
                performers_data.append(perf)
        return performers_data
