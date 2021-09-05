import re
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteLASublimeSpider(BaseSceneScraper):
    name = 'LASublime'
    network = 'MVG Cash'

    start_urls = [
        'https://tours.lasublimexxx.com',
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '//div[contains(@class,"full-text")]//p/text()',
        'date': '//div[contains(@class,"full-text")]//small/strong[contains(text(),"Date")]/../following-sibling::text()',
        'date_formats': ['%d/%m/%Y'],
        'image': '//style[contains(text(),"background")]/text()',
        're_image': '.*\'(http.*?\').*',
        'performers': '//strong[contains(text(),"Actors")]/following-sibling::a/i/following-sibling::text()',
        'tags': '//strong[contains(text(),"Categories")]/following-sibling::a/i/following-sibling::text()',
        'external_id': r'.*\/(.*?).html',
        'trailer': '',
        'pagination': '/tour/categories/movies_%s_d.html'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="scene-carousel-content"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_image(self, response):
        image = super().get_image(response)
        image = re.search(r'.*(\/content.*?\.jpg).*', image)
        if image:
            image = image.group(1)
            image = "https://tours.lasublimexxx.com/tour" + image.replace("-2x.", "-3x.")
            return image
        return ''

    def get_site(self, response):
        return "LA Sublime"

    def get_parent(self, response):
        return "LA Sublime"
