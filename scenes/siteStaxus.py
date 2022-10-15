import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteStaxusSpider(BaseSceneScraper):
    name = 'Staxus'
    network = 'Staxus'
    parent = 'Staxus'
    site = 'Staxus'

    start_urls = [
        'https://staxus.com',
    ]

    selector_map = {
        'title': '//div[contains(@class,"video-descr")]//h2/text()',
        'description': '//div[contains(@class,"video-descr") and contains(@class,"content")]/p/text()',
        'date': '//script[contains(text(), "context")]/text()',
        're_date': r'uploadDate.*?(\d{4}-\d{2}-\d{2})',
        'date_formats': ['%Y-%m-%d'],
        'image': '//script[contains(text(), "context")]/text()',
        're_image': r'thumbnailUrl.*?\"(http.*?)\"',
        'trailer': '//script[contains(text(), "context")]/text()',
        're_trailer': r'contentUrl.*?\"(http.*?)\"',
        'performers': '//div[contains(@class,"video-descr__model-item")]//a/text()',
        'tags': '//h4[contains(text(), "Tags")]/following-sibling::p/a/text()',
        'external_id': r'id=(\d+)',
        'pagination': '/trial/category.php?id=50&page=%s&s=d&',
        'type': 'Scene'
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//li[@class="item"]/div/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_duration(self, response):
        duration = response.xpath('//script[contains(text(), "context")]/text()')
        if duration:
            duration = re.search(r'duration.*?\"(\d{1,2})M(\d{1,2})S', duration.get())
            if duration:
                minutes = int(duration.group(1)) * 60
                seconds = int(duration.group(2))
                duration = str(minutes + seconds)
                return duration
        return ''

    def get_image(self, response):
        image = super().get_image(response)
        image = image.replace(".com/contentthumbs", ".com/content/contentthumbs")
        return image
