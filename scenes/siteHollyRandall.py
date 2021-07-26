import scrapy
import re

from tpdb.BaseSceneScraper import BaseSceneScraper


class siteHollyRandallSpider(BaseSceneScraper):
    name = 'HollyRandall'
    network = 'Holly Randall'
    parent = 'Holly Randall'

    start_urls = [
        'https://www.hollyrandall.com',
    ]

    selector_map = {
        'title': '//h2/text()',
        'description': '//h3[contains(text(),"description")]/following-sibling::p/text()',
        'date': '//p[contains(text(),"Added")]/text()[contains(.,"Added")]',
        'date_formats': ['%B %d, %Y'],
        'image': '//img[contains(@class,"update_thumb")]/@src0_1x',
        'performers': '//p/a[contains(@href,"/models")]/text()',
        'tags': '//ul[@class="tags"]/li/a/text()',
        'external_id': '.*\/(.*).html',
        'trailer': '',
        'pagination': '/categories/movies_%s_d.html#'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="item-thumb"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)


    def get_image(self, response):
        image = self.process_xpath(response, self.get_selector_map('image'))
        if not image:
            image = response.xpath('//img[contains(@class,"update_thumb")]/@src')
        if image:
            image = self.get_from_regex(image.get(), 're_image')

            if image:
                if re.search('\/(p\d+.jpg)', image):
                    return ''
                image = self.format_link(response, image)
                return image.replace(" ", "%20").replace('content//', 'content/')

        return None

    def get_site(self, response):
        return "Holly Randall"

    def get_parent(self, response):
        return "Holly Randall"
        
