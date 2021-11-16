import re
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteStrapLezzSpider(BaseSceneScraper):
    name = 'StrapLezz'
    network = 'Strap Lezz'
    parent = 'Strap Lezz'
    site = 'Strap Lezz'

    date_trash = ['Released:', 'Added:', 'Published:', 'Posted on']

    start_urls = [
        'https://straplezz.com/',
    ]

    selector_map = {
        'title': '//h1[@class="card-title"]/text()',
        'description': '//i[contains(@class,"fa-calendar-alt")]/../../following-sibling::p/text()',
        'date': '//i[contains(@class,"fa-calendar-alt")]/following-sibling::text()',
        'date_formats': ['%B %d, %Y'],
        'image': '//comment()[contains(.,"First Thumb")]/following-sibling::img/@src0_4x',
        'performers': '//div[contains(@class,"card model")]/a/h3/text()',
        'tags': '//li[contains(@class,"tag")]/a/text()',
        'external_id': r'updates/(.*).html',
        'trailer': '//comment()[contains(.,"Link to Trailer")]/following-sibling::a/@onclick',
        're_trailer': r'tload\(\'(.*.mp4)\'',
        'pagination': '/categories/movies_%s_d.html'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//a[contains(@href,"/updates/")]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_image(self, response):
        image = self.process_xpath(response, self.get_selector_map('image')).get()
        if not image:
            image = response.xpath('//comment()[contains(.,"First Thumb")]/following-sibling::img/@src0_3x').get()
        if not image:
            image = response.xpath('//comment()[contains(.,"First Thumb")]/following-sibling::img/@src0_2x').get()
        if not image:
            image = response.xpath('//comment()[contains(.,"First Thumb")]/following-sibling::img/@src0_1x').get()

        if image:
            image = self.format_link(response, image)
            return image.replace(" ", "%20")

        return None
