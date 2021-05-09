import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
import dateparser


class PefectGonzoSpider(BaseSceneScraper):
    name = 'PerfectGonzo'
    network = "DEV8 Entertainment"
    parent = "PerfectGonzo"

    start_urls = [
        'https://www.perfectgonzo.com/'
    ]

    selector_map = {
        'title': '//div[@class="row"]/div/h2/text()',
        'description': '//p[@class="mg-md"]/text()',
        'date': '//span[contains(text(),"Added")]/text()',
        'image': '//video/@poster',
        'performers': '//div[@id="video-info"]//a[contains(@href,"/models/")]/text()',
        'tags': '//a[contains(@href,"tag[]")]/text()',
        'external_id': '\\/movies\\/(.*)',
        'trailer': '//video/source/@src',
        'pagination': '/movies/page-%s/?tag=&q=&model=&sort=recent'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="itemm"]')
        for scene in scenes:
            try:
                site = scene.xpath(
                    './/p[contains(text(),"Site")]/a/text()').get().strip()
            except BaseException:
                site = 'PerfectGonzo'
            if not site:
                site = 'PerfectGonzo'

            scene = scene.xpath('./a/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta={'site': site})

    def get_date(self, response):
        date = self.process_xpath(
            response, self.get_selector_map('date')).get()
        date = date.replace('Added', '').strip()
        return dateparser.parse(date.strip()).isoformat()

    def get_image(self, response):
        image = self.process_xpath(
            response, self.get_selector_map('image')).get()
        if not image:
            try:
                image = response.xpath(
                    '//div[@class="col-sm-12"]/a/img/@src').get()
            except BaseException:
                return ''

        return self.format_link(response, image)
