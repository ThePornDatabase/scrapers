import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class Spider(BaseSceneScraper):
    name = 'BennyGreen'
    network = 'Benny Green'
    parent = 'Benny Green'
    site = 'Benny Green'

    start_urls = [
        'https://www.bennygreen.it',
    ]

    selector_map = {
        'title': '//div[@class="titolo-video"]/h2[1]/text()',
        'description': '//div[@class="titolo-video"]/div[contains(@class,"captionvideo")]/text()',
        'date': '',
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//h4/a[contains(@href, "/pornostar/")]/text()',
        'tags': '',
        'duration': '',
        'trailer': '//script[contains(text(), "qualityselector")]/text()',
        're_trailer': r'hd1280.*?(http.*?)\'',
        'external_id': r'/(\d+)-',
        'pagination': '/new-video.php?next=%s&term=&categoria=&pornostar=&durata=&risoluzione=&shorting=',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        scenes = response.xpath('//a[@class="link-photo-home"]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)
