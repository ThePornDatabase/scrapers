import dateparser
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class CouplesCinemaSpider(BaseSceneScraper):
    name = 'CouplesCinema'
    network = 'couplescinema'

    start_urls = [
        'https://www.couplescinema.com'
    ]

    cookies = {
        'couplescinema': '4urdfnv2e95pqbrs77e0jnha7l',
        'couplescinema_locale': 'en'
    }

    selector_map = {
        'title': '//div[contains(@class, "mediaHeader")]//span[contains(@class, "title")]/text()',
        'description': '//span[contains(@class, "description")]/text()',

        'image': '//video/@poster',
        'performers': '//div[contains(@class, "cast")]/a/text()',
        'tags': "",
        'external_id': 'post/details/(\d+)',
        'trailer': '',
        'pagination': '/search/videos?page=%s'
    }

    def get_scenes(self, response):
        scenes = response.css('.post a::attr(href)').getall()
        for scene in scenes:
            yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_date(self, response):
        return dateparser.parse('today').isoformat()

    def get_site(self, response):
        text = response.xpath('//span[contains(@class, "type")]/text()').get()
        return text.split('|')[0].strip()

    def get_image(self, response):
        image = self.process_xpath(
            response, self.get_selector_map('image')).get()

        if image:
            return self.format_link(response, image)
        else:
            return ''
