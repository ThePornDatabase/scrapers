import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteBenefitMonkeySpider(BaseSceneScraper):
    name = 'BenefitMonkey'
    network = 'Benefit Monkey'
    parent = 'Benefit Monkey'
    site = 'Benefit Monkey'

    start_urls = [
        'https://thebenefitmonkey.com',
    ]

    selector_map = {
        'title': '//div[contains(@class,"videoDetails")]/h3/text()',
        'description': '//div[contains(@class,"videoDetails")]/p/text()',
        'date': '//span[contains(text(), "Date Added")]/following-sibling::text()',
        'date_formats': ['%B %d, %Y'],
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//li[@class="update_models"]/a/text()',
        'tags': '//li/a[contains(@href, "/categories/")]/text()',
        'external_id': r'.*/(.*?).html',
        'trailer': '',
        'pagination': '/tour/categories/movies/%s/latest/'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="item-thumb"]/div')
        for scene in scenes:
            trailer = scene.xpath('./@data-videothumb')
            if trailer:
                trailer = trailer.get()
                trailer = self.format_link(response, trailer).replace(" ", "%20")
            else:
                trailer = ''
            scene = scene.xpath('./a/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta={'trailer': trailer})
