import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper
import re
import dateparser
from datetime import datetime


class NomadMediaSpider(BaseSceneScraper):
    name = 'NomadMedia'
    network = "Nomad Media"
    parent = "Aziani"

    start_urls = [
        'https://www.aziani.com',
        'https://www.gangbangcreampie.com',
        'https://www.gloryholesecrets.com',
    ]

    selector_map = {
        'title': '//div[contains(@class,"trailer")]/h2/text()',
        'description': '//div[@class="desc"]/p/text()',
        'date': '',
        'image': '//img[@id="set-target-1_0"]/@src | //video/@poster',
        'performers': '//h5/a[contains(@href,"/models/")]/text()',
        'tags': '//h5[@class="video_categories"]/a/text()',
        'trailer': '//video/source/@src',
        'external_id': '.*\\/(.*?)\\.html$',
        'pagination': '/tour/categories/movies_%s_d.html'
    }

    def get_scenes(self, response):

        sceneresponses = response.xpath('//div[@class="details"]')
        for sceneresponse in sceneresponses:
            date = sceneresponse.xpath('./p/strong/text()').get().strip()
            if not date:
                date = datetime.now()

            scene = sceneresponse.xpath('./h5/a/@href').get().strip()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta={'date': date})

    def get_image(self, response):
        image = self.process_xpath(
            response, self.get_selector_map('image')).get()

        if image is not None:
            return self.format_link(response, image)
