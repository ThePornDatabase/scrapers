import re

import dateparser
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class LetsDoeItSpider(BaseSceneScraper):
    name = 'LetsDoeIt'
    network = "LetsDoeIt"

    start_urls = [
        'https://www.letsdoeit.com'
    ]

    selector_map = {
        'title': '//div[contains(@class,"module-video-details")]//h1/text()',
        'description': '//meta[@name="description"]/@content',
        'date': "//meta[@itemprop='uploadDate']/@content",
        'image': '//meta[@itemprop="thumbnailUrl"]/@content',
        'performers': '//div[@class="actors"]/h2/span/a/strong/text()',
        'tags': "//a[contains(@href,'/tags/') or contains(@href,'/categories/')]/text()",
        'external_id': '\/watch\/(.*)\/',
        'trailer': '//meta[@itemprop="contentURL"]/@content',
        'pagination': '/videos.en.html?order=-recent&page=%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath("//div[@class='cards card-video']//a[@class='link']/@href").getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_site(self, response):
        site = response.xpath('//div[@class="actors"]/h2/a/strong/text()').get().strip()
        return site
