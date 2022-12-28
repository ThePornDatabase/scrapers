import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SitePaytonHallXXXSpider(BaseSceneScraper):
    name = 'PaytonHallXXX'
    network = 'Dreamnet'
    parent = 'Payton Hall XXX'
    site = 'Payton Hall XXX'

    start_urls = [
        'http://www.paytonhallxxx.com',
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '//div[@class="videocontent"]/p/text()',
        'date': '//div[@class="videodetails"]/p[@class="date"]/text()[1]',
        're_date': r'(\d{2}/\d{2}/\d{4})',
        'image': '//script[contains(text(), "video_content")]/text()',
        're_image': r'poster=\"(.*?)\"',
        'performers': '//span[contains(@class, "update_models")]/a/text()',
        'tags': '//div[@class="videodetails"]/p[@class="date"]/a[contains(@href, "/categories/")]/text()',
        'duration': '//div[@class="videodetails"]/p[@class="date"]/text()[1]',
        're_duration': r'(\d{1,2}:\d{2}(?::\d{2})?)',
        'trailer': '//script[contains(text(), "video_content")]/text()',
        're_trailer': r'video src=\"(.*?)\"',
        'external_id': r'.*/(.*?)\.htm',
        'pagination': '/tour/categories/Movies_%s_d.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="modelimg"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_image(self, response):
        image = super().get_image(response)
        if not re.search(r'.com.*?(\.\w{3})', image):
            image = response.xpath('//div[@class="videoplayer"]/img/@src0_1x')
            if image:
                image = self.format_link(response, image.get())
        return image
