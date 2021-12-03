import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


def match_site(argument):
    match = {
        'dirtcheapanal': "Dirt Cheap Anal",
        'dirtcheapbigtits': "Dirt Cheap Big Tits",
        'dirtcheapmilfs': "Dirt Cheap MILFs",
        'dirtcheapporn': "Dirt Cheap Porn",
        'dirtcheappov': "Dirt Cheap POV",
        'dirtcheapteens': "Dirt Cheap Teens",
    }
    return match.get(argument, argument)


class NetworkDirtcheapSpider(BaseSceneScraper):
    name = 'DirtCheap'
    network = 'Naughty America'

    start_urls = [
        'https://www.dirtcheapanal.com',
        'https://www.dirtcheapbigtits.com',
        'https://www.dirtcheapmilfs.com',
        'https://www.dirtcheapporn.com',
        'https://www.dirtcheappov.com',
        'https://www.dirtcheapteens.com',
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '',
        'date': '//span[contains(text(), "Added")]/text()',
        're_date': r'(\w+ \d{1,2}, \d{4})',
        'date_formats': ['%b %d, %Y'],
        'image': '//video/@poster',
        'performers': '//div[@class="scenepage-info"]//a/text()',
        'tags': '',
        'external_id': r'.*-(\d+)',
        'trailer': '//video/source/@src',
        'pagination': '/scenes?page=%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="scene-thumbnail"]/a/@href').getall()
        for scene in scenes:
            if "?nats=" in scene:
                scene = re.search(r'(.*)\?nats=', scene).group(1)
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_site(self, response):
        return match_site(super().get_site(response))

    def get_parent(self, response):
        return match_site(super().get_site(response))

    def get_tags(self, response):
        if "anal" in response.url:
            return ['Anal']
        if "bigtits" in response.url:
            return ['Big Boobs']
        if "milfs" in response.url:
            return ['MILF']
        if "pov" in response.url:
            return ['POV']
        if "teen" in response.url:
            return ['18+ Teens']
        return []
