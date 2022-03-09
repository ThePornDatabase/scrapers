import re
import tldextract
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


def match_site(argument):
    match = {
        'cashforsextape': 'Cash For Sextape',
        'chickiporn': 'ChickiPorn',
        'hardfucktales': 'Hard Fuck Tales',
        'mypickupgirls': 'My Pickup Girls',
        'porntraveling': 'Porn Traveling',
    }
    return match.get(argument, argument)


class NetworkSeriousPartnersSpider(BaseSceneScraper):
    name = 'WTFPassAlt'
    network = 'WTFPass'

    start_urls = [
        'https://cashforsextape.com',
        'https://chickiporn.com',
        'https://hardfucktales.com',
        'https://mypickupgirls.com',
        'https://porntraveling.com',
    ]

    selector_map = {
        'title': '//meta[@property="og:title"]/@content',
        'description': '//meta[@name="description"]/@content',
        'date': '//script[contains(text(), "alltubes")]/text()',
        're_date': r'jwLocationHost.*?js\?t(\d+)\.',
        'date_formats': ['%Y%m%d'],
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//div[contains(@class, "data-actress")]/a[@class="link-red model-link-overlay"]/text()',
        'tags': '//div[@class="video-page-tab-info"]//a[contains(@href, "categories")]/text()',
        'external_id': r'videos/(\d+)/',
        'trailer': '',
        'pagination': '/videos/%s/'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="thumb-container"]/a[@class="thumb-video-link"]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_parent(self, response):
        return match_site(tldextract.extract(response.url).domain)

    def get_site(self, response):
        return match_site(tldextract.extract(response.url).domain)
