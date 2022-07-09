import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteHotAndTattedSpider(BaseSceneScraper):
    name = 'HotAndTatted'
    network = 'Hot and Tatted'
    parent = 'Hot and Tatted'
    site = 'Hot and Tatted'

    start_urls = [
        'https://www.hotandtatted.com',
    ]

    selector_map = {
        'title': '//div[contains(@class,"videoDetails")]/h3/text()',
        'description': '//div[contains(@class,"videoDetails")]/p//text()',
        'date': '//span[contains(text(), "Added:")]/following-sibling::text()',
        'date_formats': ['%Y-%m-%d'],
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//li[@class="update_models"]/a/text()',
        'tags': '//div[contains(@class,"featuring")]/ul/li/a[contains(@href, "categories")]/text()',
        'trailer': '//script[contains(text(), "var video_content")]/text()',
        're_trailer': r'video src=\"(.*?\.mp4)',
        'external_id': r'trailers(.*)\.htm',
        'pagination': '/categories/Movies/%s/latest/'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="item-thumb"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)
