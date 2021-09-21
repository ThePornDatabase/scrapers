import re
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteSubmissiveXSpider(BaseSceneScraper):
    name = 'OlderWomanFun'
    network = 'Older Woman Fun'

    start_urls = [
        'https://www.olderwomanfun.com',
    ]

    selector_map = {
        'title': '//span[@class="update_title"]/text()',
        'description': '//span[contains(@class, "description")]/text()',
        'date': '//span[@class="update_date"]/text()',
        'date_formats': ['%m/%d/%Y'],
        'image': '//div[@class="update_image"]/a/img/@src0_3x',
        'performers': '//span[@class="tour_update_models"]/a/text()',
        'tags': '//span[@class="tour_update_tags"]/a/text()',
        'external_id': r'.*/(.*?).html',
        'trailer': '',
        'pagination': '/tour2/categories/updates_%s_d.html'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="update_details"]/a[1]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_site(self, response):
        return 'Older Woman Fun'

    def get_parent(self, response):
        return 'Older Woman Fun'


    def get_image(self, response):
        image = self.process_xpath(response, self.get_selector_map('image'))
        if image:
            image = self.get_from_regex(image.get(), 're_image')
            if image:
                image = "https://www.olderwomanfun.com/tour2/" + image.strip()
                return image.replace(" ", "%20")

        return None
