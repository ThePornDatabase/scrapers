import re
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class AnnaClaireCloudsSpider(BaseSceneScraper):
    name = 'AnnaClaireClouds'
    network = 'Anna Claire Clouds'
    parent = 'Anna Claire Clouds'

    start_urls = [
        'https://annaclaireclouds.com/'
    ]

    selector_map = {
        'title': '//span[@class="update_title"]/text()',
        'description': '//span[@class="latest_update_description"]/text()',
        'date': '//span[@class="availdate"]/text()',
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//span[@class="tour_update_models"]/a/text()',
        'tags': '//span[@class="update_tags"]/a/text()',
        'external_id': 'updates\\/(.*).html',
        'trailer': '//video/source/@src',
        'pagination': '/categories/Movies_%s_d.html'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="updateItem"]/a')
        for scene in scenes:
            image = scene.xpath('./img/@src').get()
            if not image:
                image = ''
            scene = scene.xpath('./@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta={'image': image})

    def get_site(self, response):
        return "Anna Claire Clouds"

    def get_tags(self, response):
        if self.get_selector_map('tags'):
            tags = self.process_xpath(
                response, self.get_selector_map('tags')).getall()
            return list(map(lambda x: x.strip().title(), tags))
        return []
