import re
import scrapy
import tldextract
from tpdb.BaseSceneScraper import BaseSceneScraper


def match_site(argument):
    match = {
        'povbitch': "POV Bitch",
        'mmpnetwork': "MMP Network",
        'takevan': "Takevan",
        'melonechallenge': "Melone Challenge",
        'fakeshooting': "Fake Shooting",
        'wwmamm': "WWMAMM",
    }
    return match.get(argument, argument)


class SiteMMPNetworkSpider(BaseSceneScraper):
    name = 'MMPNetwork'
    network = 'MMP Network'

    start_urls = [
        'https://mmpnetwork.com',
        'https://fakeshooting.com',
    ]

    selector_map = {
        'title': '//h1[@class="videoTitle"]/text()|//h2[@class="videoTitle"]/text()',
        'description': '//div[@class="videoDescription"]/text()',
        'date': '//div[@class="left"]/div[@class="videoDate"]/text()',
        're_date': r'(\w+ \d{1,2}, \d{4})',
        'image': '//div[@class="player"]/img/@src|//div[@class="player"]//video/@poster',
        'performers': '//div[@class="videoDate"]/a/text()',
        'tags': '//div[@class="videoTags"]/a/text()',
        'external_id': r'video/(\d+)/.*',
        'trailer': '',
        'pagination': '/updates?p=%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="scene"]/div/div/figure/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_site(self, response):
        image = super().get_image(response)
        if image:
            site = tldextract.extract(image).domain
        else:
            site = 'mmpnetwork'
        return match_site(site)

    def get_parent(self, response):
        image = super().get_image(response)
        if image:
            parent = tldextract.extract(image).domain
        else:
            parent = 'mmpnetwork'
        return match_site(parent)
