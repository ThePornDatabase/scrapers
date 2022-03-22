import re
import string
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


def match_site(argument):
    match = {
        'lesarchive': 'Lesarchive',
        'teen-depot': 'Teen Depot',
        'teendreams': 'Teen Dreams',
    }
    return match.get(argument, '')


class NetworkDreamCashSpider(BaseSceneScraper):
    name = 'DreamCash'
    network = 'Dream Cash'

    start_urls = [
        'https://www.lesarchive.com',
        'https://www.teendreams.com',
        'https://www.teen-depot.com',
    ]

    selector_map = {
        'title': '//meta[@name="twitter:title"]/@content',
        'description': '//p[@class="description"]/text()',
        'date': '//div[@class="content-date"]/span/text()',
        're_date': r'(\d{4}-\d{2}-\d{2})',
        'date_formats': ['%Y-%m-%d'],
        'image': '//script[contains(text(), "poster")]/text()',
        'image_blob': True,
        're_image': r'poster=\"(.*?)\"',
        'performers': '//h3[@class="item-name"]/span/text()',
        'tags': '',
        'external_id': r'.*/(.*?).html',
        'trailer': '//script[contains(text(), "video_content")]/text()',
        're_trailer': r'video src=\"(.*?\.mp4)',
        'pagination': '/t4/categories/movies_%s_d.html'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="content-item"]/div/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_performers(self, response):
        performers = self.process_xpath(response, self.get_selector_map('performers'))
        if performers:
            performers = performers.get()
            if "&" in performers:
                performers = performers.split("&")
                performers = list(map(lambda x: string.capwords(x.strip()), performers))
            elif " and " in performers.lower():
                performers = performers.lower().split(" and ")
                performers = list(map(lambda x: string.capwords(x.strip()), performers))
            else:
                performers = [string.capwords(performers.strip())]
        else:
            performers = []
        return performers

    def get_tags(self, response):
        if "teen" in response.url:
            return ['Teen']
        if "lesarchive" in response.url:
            return ['Lesbian']
        return []

    def get_site(self, response):
        return match_site(super().get_site(response))

    def get_parent(self, response):
        return match_site(super().get_parent(response))
