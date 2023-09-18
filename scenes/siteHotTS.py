# Part of AdultPrime
import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteHotTSSpider(BaseSceneScraper):
    name = 'HotTS'

    start_urls = [
        # ~ 'https://hotts.com/',
    ]

    selector_map = {
        'title': '//div[@class="videoDetails clear"]/h3/text()',
        'description': '//div[@class="videoDetails clear"]/p/text()',
        'date': '',
        'duration': '//div[@class="player-time"]/text()',
        'image': '//meta[@property="og:image"]/@content|//meta[@name="twitter:image"]/@content',
        'performers': '//li[@class="update_models"]/a/text()',
        'tags': '//li[@class="label"]/following-sibling::li/a[contains(@href, "categories")]/text()',
        'external_id': r'.*/(.*?).html',
        'trailer': '',
        'pagination': '/categories/movies/%s/latest/'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="item-thumb"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)
