import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


def match_site(argument):
    match = {
        'ghr': "Grindhouse Raw",
        'timfuck': "Timfuck",
        'timsuck': "Timsuck",
        'timjack': "Timjack",
        'latinloads': "Latin Loads",
        'bruthaload': "Bruthaload",
        'kojo': "Knocked Out, Jerked Off",
    }
    return match.get(argument, argument)


class NetworkTreasureIslandMediaSpider(BaseSceneScraper):
    name = 'TreasureIslandMedia'
    network = 'Treasure Island Media'
    parent = 'Treasure Island Media'

    start_urls = [
        'https://ghr.treasureislandmedia.com',
        'https://timfuck.treasureislandmedia.com',
        'https://timsuck.treasureislandmedia.com',
        'https://timjack.treasureislandmedia.com',
        'https://latinloads.treasureislandmedia.com',
        'https://bruthaload.treasureislandmedia.com',
        'https://knockedoutjerkedoff.com',
    ]

    selector_map = {
        'title': '//h2[@class="page-header"]/text()',
        'description': '//meta[@name="description"]/@content',
        'image': '//meta[@property="og:image"]/@content',
        'date': '//meta[@property="article:published_time"]/@content',
        'performers': '//p[contains(@class, "thumbnail")]/a/text()',
        'external_id': r'.*/(.*?)$',
        'pagination': '/scenes?page=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="field-content"]/div/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_site(self, response):
        sitematch = re.search(r'https://(.*?)\.', response.url).group(1)
        return match_site(sitematch)
