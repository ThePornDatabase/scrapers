import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteMyBestSexLifeSpider(BaseSceneScraper):
    name = 'MyBestSexLife'
    network = 'My Best Sex Life'
    parent = 'My Best Sex Life'
    site = 'My Best Sex Life'

    start_urls = [
        'https://mybestsexlife.com',
    ]

    selector_map = {
        'title': '//div[contains(@class, "video-player")]//h2[@class="section-title"]/text()',
        'description': '//h3[contains(text(), "escription")]/following-sibling::text()',
        'date': '//strong[contains(text(), "eleased")]/following-sibling::text()',
        'date_formats': ['%B %d, %Y'],
        'image': '//div[@class="player-thumb"]/img/@src0_1x',
        'performers': '//div[contains(@class, "models-list-thumb")]//img/following-sibling::span/text()',
        'tags': '//ul[@class="tags"]/li/a/text()',
        'duration': '//strong[contains(text(), "untime")]/following-sibling::text()',
        're_duration': r'(\d{1,2}:\d{1,2})',
        'trailer': '',
        'external_id': r'.*/(.*?)\.htm',
        'pagination': '/categories/movies_%s_d.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="img-div"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)
