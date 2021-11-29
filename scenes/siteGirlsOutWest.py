import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class GirlsOutWestSpider(BaseSceneScraper):
    name = 'GirlsOutWest'
    network = "GirlsOutWest"
    parent = "GirlsOutWest"

    start_urls = [
        'https://tour.girlsoutwest.com/'
    ]

    selector_map = {
        'title': '//meta[@name="twitter:title"]/@content',
        'description': '',
        'date': "//div[@class='centerwrap clear']/p",
        're_date': r'(\d{2}/\d{2}/\d{4})',
        'image': '//div[@class="videoplayer"]/img/@src0_1x',
        'performers': '//div[@class="centerwrap clear"]/p/a[contains(@href,"/models/")]/text()',
        'tags': "",
        'external_id': r'/trailers/(.*).ht',
        'trailer': '',
        'pagination': '/categories/Movies/%s/latest/'
    }

    def get_scenes(self, response):
        scenes = response.xpath(
            "//div[contains(@class,'latestScene') and not(contains(@class,'latestScenePic')) and not(contains(@class,'latestScenesBlock'))]/h4/a/@href").getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)
