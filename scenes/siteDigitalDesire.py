import re
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteDigitalDesireSpider(BaseSceneScraper):
    name = 'DigitalDesire'
    network = 'Digital Desire'

    start_urls = [
        'https://digitaldesire.com',
    ]

    selector_map = {
        'title': '//meta[@property="og:title"]/@content',
        'description': '//span[contains(@class,"description")]/text()',
        'date': '//div[@class="set_date"]/text()',
        'date_formats': ['%B %d, %Y'],
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//div[@class="title_bar gallery_model"]/span/a/text()',
        'tags': '//span[@class="update_tags"]/a/text()',
        'external_id': r'.*/.*-(\d{2,7})_.*.html',
        'trailer': '',
        'pagination': '/tour/categories/movies_%s_d.html'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="update_details"]/a[1]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_site(self, response):
        return "Digital Desire"

    def get_parent(self, response):
        return "Digital Desire"

    def get_image(self, response):
        image = super().get_image(response)
        if image:
            image = image.replace("-2x", "-1x")
            return image
        return ''

    def get_tags(self, response):
        tags = super().get_tags(response)
        if 'Videos' in tags:
            tags.remove('Videos')
        return tags
