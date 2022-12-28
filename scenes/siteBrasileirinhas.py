import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteBrasileirinhasSpider(BaseSceneScraper):
    name = 'Brasileirinhas'
    network = 'Brasileirinhas'
    parent = 'Brasileirinhas'
    site = 'Brasileirinhas'

    start_urls = [
        'https://www.brasileirinhas.com.br',
    ]

    selector_map = {
        'title': '//h1[@class="titleVideo"]/text()',
        'description': '//h1[@class="titleVideo"]/following-sibling::p/text()',
        'date': '',
        'image': '',
        'performers': '',
        'tags': '',
        'duration': '//span[@class="tempoCena"]/text()',
        'trailer': '',
        'external_id': r'.*-(\d+)\.htm',
        'pagination': '/videos-porno/pagina-%s.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[contains(@class, "conteudoVideos")]/div/a[contains(@class, "filmeLink")]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_image(self, response):
        sceneid = super().get_id(response)
        if sceneid:
            image = f"https://static1.brasileirinhas.com.br/Brasileirinhas/images/conteudo/cenas/player/{sceneid}.jpg"
            return image
        return None
