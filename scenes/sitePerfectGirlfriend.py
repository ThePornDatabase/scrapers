import re
import string
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class SitePerfectGirlfriendSpider(BaseSceneScraper):
    name = 'PerfectGirlfriend'
    network = 'Perfect Girlfriend'

    start_urls = [
        'https://perfectgirlfriend.com',
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '//div[@class="entry-content"]/p[not(contains(text(), "Starring"))]/text()',
        'date': '//span[@class="published"]/text()',
        'image': '//span[@class="model_update_thumb"]/img/@src',
        'performers': '//div[@class="entry-content"]/p[contains(text(), "Starring")]/text()',
        'tags': '//a[@rel="category tag"]/text()',
        'external_id': r'.*/(.*?)/$',
        'trailer': '//meta[@itemprop="contentUrl"]/@content',
        'pagination': '/page/%s/?et_blog'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//article/div[1]/a')
        for scene in scenes:
            image = scene.xpath('./img/@src').get()
            scene = scene.xpath('./@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta={'image': image})

    def get_site(self, response):
        return "Perfect Girlfriend"

    def get_parent(self, response):
        return "Perfect Girlfriend"

    def get_performers(self, response):
        performers = response.xpath(self.get_selector_map('performers'))
        if performers:
            performers = performers.get()
            performers = performers.lower().replace("*", "").replace("starring", "").strip()
            performers = performers.split("&")
            return list(map(lambda x: string.capwords(x.strip()), performers))
        return []
