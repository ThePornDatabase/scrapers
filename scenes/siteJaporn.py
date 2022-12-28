import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteJapornSpider(BaseSceneScraper):
    name = 'Japorn'
    network = 'Japorn'
    parent = 'Japorn'
    site = 'Japorn'

    start_urls = [
        'https://www.japornxxx.com',
    ]

    selector_map = {
        'title': '//div[@class="block"]/h2[1]/text()',
        'description': '//div[@class="description"]/p//text()',
        'date': '//strong[contains(text(), "Date:")]/following-sibling::text()[1]',
        'date_formats': ['%d %B %Y'],
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//div[contains(@class,"actorRelated block")]/div[@class="related"]/a/text()',
        'tags': '//div[@class="tags"]/ul/li/a/text()',
        'duration': '//strong[contains(text(), "Length:")]/following-sibling::text()[1]',
        'trailer': '//script[contains(text(), ".mp4")]/text()',
        're_trailer': r'url\: \"(http.*?\.mp4)',
        'external_id': r'.*_(\d+)',
        'pagination': '/scene?page=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        scenes = response.xpath('//a[contains(@class, "scene item")]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)
