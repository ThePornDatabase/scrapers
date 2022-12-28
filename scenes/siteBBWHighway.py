import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteBBWHighwaySpider(BaseSceneScraper):
    name = 'BBWHighway'
    network = 'BBW Highway'
    parent = 'BBW Highway'
    site = 'BBW Highway'

    start_urls = [
        'https://bbwhighway.com',
    ]

    selector_map = {
        'title': '//meta[@property="og:title"]/@content',
        'description': '//div[@class="videocontent"]/p/text()',
        'date': '//p[@class="date"]/text()',
        're_date': r'(\d{2}/\d{2}/\d{4})',
        'date_formats': ['%m/%d/%Y'],
        'duration': '//p[@class="date"]/text()',
        're_duration': r'(\d{2}:\d{2})',
        'image': '//div[@class="videoplayer"]/img/@src0_2x',
        'performers': '//span[contains(@class,"tour_update_models")]/a/text()',
        'tags': '',
        'trailer': '',
        'external_id': r'trailers/(.*?)\.htm',
        'pagination': '/tour/categories/Movies/%s/latest/',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class,"modelfeature")]/div/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_tags(self, response):
        return ['Interracial', 'BBW']

    def get_image(self, response):
        image = super().get_image(response)
        if "/content" not in image:
            image = response.xpath('//script[contains(text(), "video_content")]/text()')
            if image:
                image = image.get()
                image = re.search(r'poster.*?\"(\/tour.*?\.jpg)\"', image)
                if image:
                    image = image.group(1)
        if image:
            return self.format_link(response, image)
        return None
