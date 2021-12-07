import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


def match_site(argument):
    match = {
        'av69': "AV69",
        'avanal': "AVAnal",
        'avstockings': "AVStockings",
        'avtits': "AVTits",
        'ferame': "Ferame",
        'gangav': "GangAV",
        'hairyav': "HairyAV",
        'heymilf': "Hey MILF",
        'heyoutdoor': "Hey Outdoor",
        'lingerieav': "LingerieAV",
        'pussyav': "PussyAV",
        'schoolgirlshd': "Schoolgirls HD",
        'shiofuky': "Shiofuky",
    }
    return match.get(argument, argument)


class SiteSubmissiveXSpider(BaseSceneScraper):
    name = 'JavHDAlt'
    network = 'JavHD'

    start_urls = [
        'https://av69.tv',
        'https://avanal.com',
        'https://avstockings.com',
        'https://avtits.com',
        'https://ferame.com',
        'https://gangav.com',
        'https://hairyav.com',
        'https://heymilf.com',
        'https://heyoutdoor.com',
        'https://lingerieav.com',
        'https://pussyav.com',
        'https://schoolgirlshd.com',
        'https://shiofuky.com',
    ]

    cookies = {
        'locale': 'en',
    }

    selector_map = {
        'title': '//h1[@itemprop="name"]/text()',
        'description': '//span[@class="info-title" and contains(text(), "Description")]/following-sibling::p/text()',
        'date': '',
        'image': '//div[@class="player"]/span/img/@src',
        'performers': '//span[@class="info-title" and contains(text(), "Featuring")]/following-sibling::*//a/text()',
        'tags': '//div[@class="categories-links"]/a/text()',
        'external_id': r'id/(\d+)/',
        'trailer': '',
        'pagination': '/en/movies/justadded/%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="thumb-body"]/a[contains(@href, "/en/id")]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_site(self, response):
        return match_site(super().get_site(response))

    def get_parent(self, response):
        return match_site(super().get_site(response))

    def get_tags(self, response):
        tags = super().get_tags(response)
        if "Asian" not in tags:
            tags.append("Asian")
        return tags
