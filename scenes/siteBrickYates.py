import re
import html
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteBrickYatesSpider(BaseSceneScraper):
    name = 'BrickYates'
    network = 'Brick Yates'
    parent = 'Brick Yates'

    start_urls = [
        'https://www.brickyates.com',
    ]

    selector_map = {
        'title': '//div[contains(@class,"videoDetails")]/h3/text()',
        'description': '//div[contains(@class,"videoDetails")]/p/text()',
        'date': '//span[contains(text(),"Added")]/following-sibling::text()',
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//li[@class="update_models"]/a/text()',
        'tags': '//div[contains(@class,"featuring")]/ul/li/a[contains(@href,"/categories/")]/text()',
        'external_id': r'.*/(.*?).html',
        'trailer': '',
        'pagination': '/tour/categories/Movies/%s/latest/'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="item-thumb"]')
        for scene in scenes:
            image = scene.xpath('./a/img/@src0_3x').get()
            if not image:
                image = scene.xpath('./a/img/@src0_2x').get()
            if not image:
                image = scene.xpath('./a/img/@src0_1x').get()

            if image:
                image = "https://www.brickyates.com" + image
            else:
                image = ''

            scene = scene.xpath('.//a[not(contains(@href,"signup"))]/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta={'image': image})

    def get_site(self, response):
        return "Brick Yates"

    def get_id(self, response):
        externid = super().get_id(response)
        return externid.lower()

    def get_description(self, response):
        description = self.process_xpath(response, self.get_selector_map('description')).getall()
        if description:
            description = " ".join(description)
            return html.unescape(description.strip())

        return ''

    def get_trailer(self, response):
        if 'trailer' in self.get_selector_map() and self.get_selector_map('trailer'):
            trailer = self.process_xpath(response, self.get_selector_map('trailer'))
            if trailer:
                trailer = self.get_from_regex(trailer.get(), 're_trailer')
                trailer = "https://www.brandnewamateurs.com" + trailer
                return trailer.replace(" ", "%20")

        return ''

    def get_image(self, response):
        return ''
