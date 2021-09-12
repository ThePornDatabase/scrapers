import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class FamilyTherapyXXXSpider(BaseSceneScraper):
    name = 'FamilyTherapyXXX'
    network = 'FamilyTherapyXXX'
    parent = 'FamilyTherapyXXX'
    site = 'FamilyTherapyXXX'

    start_urls = [
        'https://familytherapyxxx.com'
    ]

    selector_map = {
        'title': '//h1[@class="entry-title"]/text()',
        'description': '//div[@class="entry-content"]/p[1]/text()',
        'performers': '//div[@class="entry-content"]/p[contains(text(),"Starring")]/text()',
        'date': '//span[@class="published"]/text()',
        # ~ 'image': '',
        'tags': '//p[@class="post-meta"]/a[contains(@rel,"category")]/text()',
        'external_id': r'\.com\/(.*)\/',
        'trailer': '//meta[@itemprop="contentUrl"]/@content',
        'pagination': '/page/%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//a[@class="entry-featured-image-url"]/@href').getall()
        for scene in scenes:
            yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta={'site': 'FamilyTherapyXXX'})

    def get_tags(self, response):
        if self.get_selector_map('tags'):
            tags = self.process_xpath(
                response, self.get_selector_map('tags')).getall()
            return list(map(lambda x: x.strip().title(), tags))
        return []

    def get_performers(self, response):
        performers = self.process_xpath(
            response, self.get_selector_map('performers')).get()
        if performers:
            performers = re.search(r'Starring(.*?)\*', performers).group(1)
            if performers:
                performers = performers.replace("&amp;", "&")
                performers = performers.split("&")
                return list(map(lambda x: x.strip(), performers))
        return []

    def get_image(self, response):
        return ''
