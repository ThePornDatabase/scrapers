import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteDominicPacificoSpider(BaseSceneScraper):
    name = 'DominicPacifico'
    site = 'Dominic Pacifico'
    parent = 'Dominic Pacifico'
    network = 'Dominic Pacifico'

    start_urls = [
        'https://dominicpacifico.com'
    ]

    selector_map = {
        'title': '//div[contains(@class, "video-block")]/div[1]/h2/text()',
        'description': '//div[contains(@class, "video-block")]//h4/text()',
        'image': '//meta[@property="og:image"]/@content',
        'type': 'Scene',
        'external_id': r'videos/(\d+)',
        'pagination': '/scenes.html?start=%s',
    }

    def get_next_page_url(self, base, page):
        page = str((int(page) - 1) * 18)
        return self.format_url(base, self.get_selector_map('pagination') % page)

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "img-wrapper")]/a/@href').getall()
        for scene in scenes:
            if "?nats" in scene:
                scene = re.search(r'(.*?)\?nat', scene).group(1)
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)
