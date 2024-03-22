import re
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


def match_site(argument):
    match = {
        'becomingfemme': "Becoming Femme",
        'pure-bbw': "Pure BBW",
        'pure-ts': "Pure TS",
        'pure-xxx': "Pure XXX",
        'tspov': "TSPOV",
    }
    return match.get(argument, argument)


class CXWowSpider(BaseSceneScraper):
    name = 'CXWow'
    network = 'CX Wow'

    start_urls = [
        'https://www.becomingfemme.com/',
        'https://www.pure-bbw.com/',
        'https://www.pure-ts.com/',
        'https://www.pure-xxx.com/',
        'https://www.tspov.com/',
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '//h4/following-sibling::p/text()',
        'performers': '//h5[contains(text(), "Featuring")]/following-sibling::ul/li/a/text()',
        'date': '//h5[contains(text(), "Added")]/following-sibling::p/text()',
        'date_formats': ['%B %d, %Y'],
        'image': '//div[contains(@class, "player-window-play")]/following-sibling::img[1]/@src0_4x',
        'duration': '//div[contains(@class, "player-time")]/text()',
        're_duration': r'/.*?(\d{1,2}:\d{2}(?::\d{2})?)',
        'tags': '//ul[@class="tags"]/li/a/text()',
        'trailer': '//script[contains(text(), "playsinline")]/text()',
        're_trailer': r'playsinline.*?(/.*?)[\'\"]',
        'external_id': '/trailers/(.*).html',
        'pagination': '/tour/updates/page_%s.html',

    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[contains(@class,"iLScenePic")]/a/@href|//div[@class="mtVideoThumb"]/a/@href').getall()
        for scene in scenes:
            if "join.php" not in scene:
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_site(self, response):
        return match_site(super().get_site(response))

    def get_parent(self, response):
        return match_site(super().get_parent(response))

    def get_performers(self, response):
        performers = super().get_performers(response)
        performers.append("Christian XXX")
        return performers
