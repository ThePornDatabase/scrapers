import re
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
        'title': '//div[@class="gqTop"]/div/span[@class="gqTitle"]/text()',
        'description': '//span[@class="gqDescription"]/text()',

        'image': '//div[@class="gqTop"]/@style',
        'performers': '//a[@class="gqModel"]/text()',
        'tags': "",
        'external_id': 'post/details/(\\d+)',
        'trailer': '',
        'pagination': '/search/videos?page=%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath(
            '//div[contains(@class,"gqPostContainer")]/a/@href').getall()
        for scene in scenes:
            yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_date(self, response):
        return dateparser.parse('today').isoformat()

    def get_site(self, response):
        site = response.xpath('//div[@class="gqProducer"]/a/text()').get()
        return site.strip()

    def get_image(self, response):
        image = self.process_xpath(
            response, self.get_selector_map('image')).get()

        if "background" in image:
            image = re.search('url\\((.*)\\)', image).group(1).strip()

        return self.format_link(response, image)
