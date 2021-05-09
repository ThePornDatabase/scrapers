import re
from datetime import datetime

import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class BellaPassnSpider(BaseSceneScraper):
    name = 'BellaPass'
    network = 'Bella Pass'
    parent = 'Bella Pass'

    start_urls = [
        'https://alexismonroe.com',
        'https://avadawn.com',
        'https://bellahd.com',
        'https://bellanextdoor.com',
        'https://bryci.com',
        'https://calicarter.com',
        'https://hd19.com',
        'https://hunterleigh.com',
        'https://janafox.com',
        'https://joeperv.com',
        'https://katiebanks.com',
        'https://monroelee.com',
        'https://taliashepard.com',
    ]

    selector_map = {
        'title': "//div[contains(@class, 'videoDetails')]//h3/text()",
        'description': "//div[contains(@class, 'videoDetails')]//p/text()",
        'date': "//div[contains(@class, 'videoInfo')][1]//p[1]/text()",
        'performers': "//li[@class='update_models']//a/text()",
        'tags': "//div[contains(@class, 'featuring')][2]//a/text()",
        'image': "img.update_thumb::attr(src0_3x)",
        'external_id': 'trailers/(.+)\\.html',
        'pagination': '/categories/movies/%s/latest/'
    }

    def get_date(self, response):
        return datetime.now().isoformat()

    def get_scenes(self, response):
        scenes = response.xpath(
            "//div[contains(@class, 'items')]//div[@class='item-thumb']//a/@href").getall()
        for link in scenes:
            if re.search(self.get_selector_map(
                    'external_id'), link) is not None:
                yield scrapy.Request(url=self.format_link(response, link), callback=self.parse_scene)
