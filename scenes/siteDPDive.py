import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteDPDivaSpider(BaseSceneScraper):
    name = 'DPDiva'
    network = 'DP Diva'
    parent = 'DP Diva'
    site = 'DP Diva'

    start_urls = [
        'https://dpdiva.com',
    ]

    selector_map = {
        'title': '//div[@class="infoHeader"]/h1/text()',
        'description': '//h3[@class="description"]/text()',
        'date': '',
        'image': '//div[@class="trailerLeft"]/div/img/@src',
        'performers': '//div[contains(@class, "infoBox")]//span[@class="tour_update_models"]/a/text()',
        'tags': '//div[@class="tagcats"]/a/text()',
        'duration': '//div[contains(@class, "infoBox")]//div[contains(@class, "Runtime")]/text()',
        're_duration': r'(\d{1,2}?\:?\d{2}\:\d{2})',
        'trailer': '//script[contains(text(), ".mp4")]/text()',
        're_trailer': r'ext.*?\"(\/trailer.*?\.mp4)',
        'external_id': r'trailers/(.*?)\.htm',
        'pagination': '/categories/movies_%s_d.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="videoBlock"]')
        for scene in scenes:
            meta['date'] = self.parse_date(scene.xpath('.//div[@class="date"]/text()').get(), date_formats=['%m-%d-%Y']).isoformat()
            scene = scene.xpath('./div/a/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)
