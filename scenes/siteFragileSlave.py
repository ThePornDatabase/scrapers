import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteFragileSlaveSpider(BaseSceneScraper):
    name = 'FragileSlave'
    network = 'Fragile Slave'
    parent = 'Fragile Slave'
    site = 'Fragile Slave'

    start_urls = [
        'https://www.fragileslave.com',
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '//div[@class="videocontent"]/p/text()',
        'date': '//p[@class="date"]/text()',
        're_date': r'(\d{1,2}/\d{1,2}/\d{4})',
        'date_formats': ['%m/%d/%Y'],
        'image': '//script[contains(text(), "video_content")]/text()',
        're_image': r'poster=\"(.*?)\".*',
        'performers': '//span[@class="tour_update_models"]/a/text()',
        'tags': '//div[@class="videodetails"]/p/a/text()',
        'external_id': r'.*/(.*?).html',
        'trailer': '//script[contains(text(), "video_content")]/text()',
        're_trailer': r'video src=\"(.*?)\".*',
        'pagination': '/updates/categories/movies/%s/latest/'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="modelimg"]/a[contains(@href, "/trailers")]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)
