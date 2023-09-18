import re
import dateparser
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class AllHerLuvSpider(BaseSceneScraper):
    name = 'AllHerLuv'
    network = 'All Her Luv'

    start_urls = [
        'https://www.allherluv.com',
        'https://www.missax.com'
    ]

    selector_map = {
        'title': '//meta[@name="twitter:title"]/@content',
        'description': '//div[@class="container"]/p[contains(@class,"text")]/strong/text()',
        'image': '//img[contains(@class,"update_thumb")]/@src0_1x',  # Image is tokened
        'image_blob': True,
        'performers': '//p[@class="dvd-scenes__data"]/a[contains(@href,"/models/")]/text()',
        'tags': '//p[@class="dvd-scenes__data"]/a[contains(@href,"/categories/")]/text()',
        'external_id': 'trailers/(.+)\\.html',
        'trailer': '',  # tokened, token not in page source
        'pagination': '/tour/categories/movies_%s_d.html'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="photo-thumb_body"]/a/@href').getall()
        for scene in scenes:
            yield scrapy.Request(url=scene, callback=self.parse_scene)

    def get_date(self, response):
        date = response.xpath('//p[@class="dvd-scenes__data" and contains(text(),"Added:")]').get()
        if date:
            date = re.search(r'(\d{2}\/\d{2}\/\d{4})', date).group(1)
            if date:
                return dateparser.parse(date).isoformat()

    def get_site(self, response):
        if "allherluv" in response.url:
            return "All Her Luv"

        if "missax" in response.url:
            return "MissaX"

    def get_image(self, response):
        image = self.process_xpath(response, self.get_selector_map('image')).get()
        if image:
            return self.format_link(response, image)

        return ''
