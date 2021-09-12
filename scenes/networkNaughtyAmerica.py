import re
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class NaughtyAmericaSpider(BaseSceneScraper):
    name = 'NaughtyAmerica'
    network = 'Naughty America'
    parent = 'Naughty America'

    start_urls = [
        'https://www.naughtyamerica.com'
    ]

    selector_map = {
        'title': '//title/text()',
        'description': '//div[contains(@class, "synopsis grey-text")]/span/following-sibling::text()',
        'date': '//div[@class="date-tags"]/span[contains(@class,"entry-date")]/text()',
        'image': '//a[@class="play-trailer"]/picture//img/@data-srcset',
        'performers': '//a[@class="scene-title grey-text link"]/text()',
        'tags': '//a[@class="cat-tag"]/text()',
        'external_id': '(\\d+)$',
        'trailer': '',
        'pagination': '/new-porn-videos?page=%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath(
            '//div[@class="scene-grid-item"]/a[contains(@href,"/scene/")]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_image(self, response):
        image = response.xpath(
            '//a[@class="play-trailer"]/picture[1]//source[contains(@data-srcset,"jpg")]/@data-srcset').get()
        if not image:
            image = response.xpath(
                '//dl8-video/@poster[contains(.,"jpg")]').get()

        if image[0:2] == "//":
            image = "https:" + image

        return self.format_link(response, image)

    def get_site(self, response):
        site = response.xpath(
            '//div[@class="scene-info"]/a[contains(@class,"site-title")]/text()').get()
        if site:
            return site.strip()
        return super.get_site(response)
