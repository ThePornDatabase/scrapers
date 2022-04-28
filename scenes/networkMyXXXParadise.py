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


class NetworkMyXXXParadiseSpider(BaseSceneScraper):
    name = 'MyXXXParadise'
    network = 'MyXXXParadise'

    start_urls = [
        'https://www.myxxxparadise.com',
    ]

    selector_map = {
        'title': '//meta[@property="og:title"]/@content',
        'description': '//meta[@property="og:description"]/@content',
        'date': '//ul[@class="stats-list"]/li/span[@class="icon i-calendar"]/following-sibling::span',
        're_date': r'(\d{4}-\d{2}-\d{2})',
        'date_formats': ['%Y-%m-%d'],
        'image': '//meta[@property="og:image"]/@content',
        'performers': '',
        'tags': '//div[@class="tags-block"]/a[contains(@href, "/search/")]/text()',
        'trailer': '',
        'external_id': r'video/(.*?).html',
        'pagination': '/videos/page%s.html'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[contains(@class,"item-inner-col")]/a[contains(@href,"/video/")]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_site(self, response):
        site = response.xpath('//ul[@class="models-list"]/li/a//text()')
        if site:
            return match_site(site.get().replace(".com", ""))
        return super().get_site(response)

    def get_parent(self, response):
        site = response.xpath('//ul[@class="models-list"]/li/a//text()')
        if site:
            return match_site(site.get().replace(".com", ""))
        return super().get_parent(response)
