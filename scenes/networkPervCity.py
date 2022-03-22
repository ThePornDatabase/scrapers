import re
import tldextract
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


def match_site(argument):
    match = {
        'analoverdose': 'Anal Overdose',
        'bangingbeauties': 'Banging Beauties',
        'chocolatebjs': 'Chocolate BJs',
        'oraloverdose': 'Oral Overdose',
        'upherasshole': 'Up Her Asshole',
    }
    return match.get(argument, argument)


class NetworkPervCitySpider(BaseSceneScraper):
    name = 'PervCity'
    network = 'PervCity'

    start_urls = [
        'https://analoverdose.com',
        'https://bangingbeauties.com',
        'https://chocolatebjs.com',
        'https://oraloverdose.com',
        'https://upherasshole.com',
    ]

    selector_map = {
        'title': '//div[@class="infoHeader"]/h1/text()',
        'description': '//div[@class="videoInfo"]/div[@class="infoMBox"]/div[@class="infoBox clear"]/p/text()',
        'date': '',
        'image': '//img[contains(@class, "posterimg")]/@src0_2x',
        'image_blob': True,
        'performers': '//div[@class="infoBox clear"]/h3/span[@class="tour_update_models"]/a/text()',
        'tags': '',
        'external_id': r'.*/(.*?)\.html',
        'trailer': '//script[contains(text(), ".mp4")]/text()',
        're_trailer': r'source type.*?\"(\/?trailers.*?.mp4)\"',
        'pagination': '/categories/movies_%s_d.html'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="videoPic"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_tags(self, response):
        tags = []
        if "asshole" in response.url or "anal" in response.url:
            tags = ['Anal']
        if "chocolatebjs" in response.url:
            tags = ['Blowjob', 'Interracial', 'African American']
        if "oraloverdose" in response.url:
            tags = ['Blowjob']

        return tags

    def get_id(self, response):
        sceneid = super().get_id(response)
        return sceneid.lower()

    def get_parent(self, response):
        return match_site(tldextract.extract(response.url).domain)

    def get_site(self, response):
        return match_site(tldextract.extract(response.url).domain)
