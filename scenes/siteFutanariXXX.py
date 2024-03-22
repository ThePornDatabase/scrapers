import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteFutanariXXXSpider(BaseSceneScraper):
    name = 'FutanariXXX'
    network = 'Hentaied'
    parent = 'Futanari XXX'
    site = 'Futanari XXX'

    start_urls = [
        'https://futanari.xxx',
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '//div[@id="fullstory"]/p/text()',
        'date': '//meta[@property="article:published_time"]/@content',
        'image': '//meta[@property="og:image"]/@content',
        'duration': '//div[contains(@class,"duration")]/img/following-sibling::text()',
        'performers': '//div[contains(@class,"taglist")]/a/text()',
        'tags': '//ul[@class="post-categories"]/li/a/text()',
        'director': '//div[contains(@class,"director")]/span/a/text()',
        'external_id': '.*\/(.*?)\/$',
        'trailer': '//video/source/@src',
        'pagination': '/all-videos/page/%s/'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//center[@class="vidcont"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene) and 'futanari' in scene:
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_id(self, response):
        id = response.xpath('//script[contains(@type, "application/json") and contains(@class, "gdrts")]/text()').get()
        id = re.search(r'item_id.*?(\d+),\"nonce', id).group(1)
        return str(id)
