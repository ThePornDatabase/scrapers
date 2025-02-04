import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class NetworkBrokeStraightBoysSpider(BaseSceneScraper):
    name = 'BrokeStraightBoys'
    network = 'Broke Straight Boys'

    start_urls = [
        'https://www.boygusher.com',
        'https://www.brokestraightboys.com',
        'https://www.collegeboyphysicals.com',
    ]

    selector_map = {
        'title': '//div[@class="inner"]/div[@class="dettl-bar"]/div[1]/text()|//div[@class="deTlt"]/h1/text()',
        'description': '//div[@class="desc"]//text()|//div[@class="dtlp"]/p//text()',
        'date': '',
        'image': '//img[contains(@src, "/thumbs") and contains(@src, "video")]/@src',
        'performers': '//div[@class="model-desc"]/div//a/text()|//div[@class="dtlp"]/span//a/text()',
        'tags': '',
        'duration': '',
        'trailer': '',
        'external_id': r'.*/(.*?)$',
        'pagination': '/episodes.php?page=%s&s=1&t=&nats=',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//ul[@class="listingC"]/li//a/@href|//ul[@id="vids"]/li/div/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_tags(self, response):
        return ['Gay']
