import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteRealGirlsGoneBadSpider(BaseSceneScraper):
    name = 'RealGirlsGoneBad'
    network = 'Real Girls Gone Bad'
    parent = 'Real Girls Gone Bad'
    site = 'Real Girls Gone Bad'

    start_urls = [
        'https://www.realgirlsgonebad.com',
    ]

    cookies = {'rggbwarning_13': 'accepted'}

    selector_map = {
        'title': '//div[@class="epiTitle"]/text()',
        'description': '//div[@class="eachB"]/p/text()',
        'date': '//div[@class="eachB"]//strong[contains(text(), "Added")]/following-sibling::text()',
        'date_formats': ['%d %B, %Y'],
        'image': '//meta[@property="og:image"]/@content',
        'performers': '',
        'tags': '//div[@class="eachB"]//span[@class="tagsC"]/a/text()',
        'external_id': r'.*/(.*?).html',
        'trailer': '',
        'pagination': '/tour/categories/videos_%s_d.html'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//h3/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, cookies=self.cookies)
