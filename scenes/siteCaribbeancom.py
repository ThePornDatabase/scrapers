import re
import string
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteCaribbeancomSpider(BaseSceneScraper):
    name = 'Caribbeancom'
    network = 'Caribbeancom'
    parent = 'Caribbeancom'
    site = 'Caribbeancom'

    start_urls = [
        'https://en.caribbeancom.com',
    ]

    selector_map = {
        'title': '//h1[@itemprop="name"]/text()',
        'description': '',
        'date': '//span[contains(@itemprop, "uploadDate") or contains(@itemprop, "datePublished")]/text()',
        'date_formats': ['%Y/%m/%d'],
        'image': '',
        'performers': '//span[@class="spec-content"]/a[contains(@itemprop, "actor")]/span/text()',
        'tags': '//span[@class="spec-content"]/a[contains(@itemprop, "genre")]/text()',
        'duration': '//span[contains(@itemprop, "duration")]/text()',
        'trailer': '',
        'external_id': r'moviepages/(.*?)/',
        'pagination': '/eng/listpages/all%s.htm',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="meta-title"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_image(self, response):
        image_script = response.xpath('//script[contains(text(), "var image")]/text()')
        if image_script:
            image_script = image_script.get()
            image_link = re.search(r'var image.*?movie_id\+[\'\"](.*?)[\'\"]', image_script).group(1)
            movieid = re.search(r'moviepages/(.*?)/', response.url).group(1)
            image = f'https://en.caribbeancom.com/moviepages/{movieid}{image_link}'
            image = self.format_link(response, image)
            return image
        return None

    def get_performers(self, response):
        performers = response.xpath('//span[@class="spec-content"]/a[contains(@itemprop, "actor")]/span/text()')
        if performers:
            performers = performers.get()
            if "," in performers:
                performers = performers.split(",")
            else:
                performers = [performers]
            performers = list(map(lambda x: string.capwords(x.strip()), performers))
            return performers
        return []
