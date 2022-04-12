import re
import string
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteDeauxmaLiveSpider(BaseSceneScraper):
    name = 'DeauxmaLive'
    network = 'vna'
    parent = 'Deauxma Live'
    site = 'Deauxma Live'

    start_urls = [
        'https://www.deauxmalive.com',
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '//div[@class="customcontent"]/div/text()',
        'date': '//div[@class="date"]/text()',
        'date_formats': ['%B %d %Y'],
        'image': '//center/img/@src',
        'image_blob': True,
        'performers': '//div[@class="customcontent"]/h3/text()',
        'tags': '//div[@class="customcontent"]/h4/text()',
        'trailer': '',
        'external_id': r'videoset/(\d+)/',
        'pagination': '/videoset/page/%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//h3/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_performers(self, response):
        performers = self.process_xpath(response, self.get_selector_map('performers'))
        if performers:
            performers = re.sub(r"[^a-zA-Z0-9, -]", "", performers.get())
            performers = performers.lower().replace("nbsp", "").split(",")
            performers = list(map(lambda x: string.capwords(x.strip()), performers))
            performers = [i for i in performers if i]
            return performers
        return []

    def get_tags(self, response):
        tags = self.process_xpath(response, self.get_selector_map('tags'))
        if tags:
            tags = tags.get().split(",")
            tags = list(map(lambda x: string.capwords(x.strip()), tags))
            tags = [i for i in tags if i]
            return tags
        return []
