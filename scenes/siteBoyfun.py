import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
true = True
false = False


class SiteBoyfunSpider(BaseSceneScraper):
    name = 'Boyfun'
    site = 'Boyfun'
    parent = 'Boyfun'
    network = 'Boyfun'

    start_urls = [
        'https://www.boyfun.com'
    ]

    cookies = [{"domain":"www.boyfun.com","hostOnly":true,"httpOnly":false,"name":"warningHidden","path":"/","sameSite":"unspecified","secure":false,"session":true,"storeId":"0","value":"hide"}]

    selector_map = {
        'title': '//span[@class="title"]/text()',
        'description': '//div[@class="heading"]/following-sibling::p/text()',
        'date': '//span[@class="date"]/span[@class="content"]/text()',
        'date_formats': ['%b %d, %Y'],
        'image': '//video/@poster',
        'performers': '//span[@class="models"]/span[@class="content"]/a/text()',
        'tags': '',
        'duration': '',
        'trailer': '',
        'type': 'Scene',
        'external_id': r'.*-(\d+)',
        'pagination': '/videos/page%s.html',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="item-inside"]/a[1]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_tags(self, response):
        return ['Gay']
