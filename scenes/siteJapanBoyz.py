import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteJapanBoyzSpider(BaseSceneScraper):
    name = 'JapanBoyz'
    network = 'Japan Boyz'
    parent = 'Japan Boyz'
    site = 'Japan Boyz'

    start_urls = [
        'https://www.japanboyz.com',
    ]

    selector_map = {
        'title': '//div[@class="movie-player"]/h2[1]/text()',
        'description': '//div[contains(@class,"description")]/text()',
        'date': '//div[contains(@class, "date")]/i[contains(@class, "calendar")]/following-sibling::span/text()',
        'date_formats': ['%d %b %y'],
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//div[@class="m-info"]/div/a/text()',
        'tags': '//div[contains(@class, "v-tags")]/a/text()',
        'duration': '//div[contains(@class, "date")]/i[contains(@class, "clock")]/following-sibling::text()',
        'trailer': '//script[contains(text(), "playlist")]/text()',
        're_trailer': r'(http.*?\.mp4)',
        'external_id': r'scenes/(.*?)\.html',
        'pagination': '/categories/scenes_%s_d.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "title")]/a[contains(@href, "/scenes/")]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_tags(self, response):
        tags = super().get_tags(response)
        tags = list(map(lambda x: x.replace("#", "").strip().title(), tags))
        return tags
