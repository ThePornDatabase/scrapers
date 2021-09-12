import re
from urllib.parse import urlparse
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class AssylumSpider(BaseSceneScraper):
    name = 'Slavemouth'
    network = 'DerangedDollars'

    start_urls = [
        'https://www.slavemouth.com'
    ]

    selector_map = {
        'title': '//h3[@class="mas_title"]/text()',
        'description': '//p[@class="mas_longdescription"]/text()',
        'date': '//div[@class="lch"]//comment()/following-sibling::text()',
        'image': '//div[@class="mainpic"]/comment()',
        'performers': '',
        'tags': '//p[@class="tags"]/a/text()',
        'external_id': '\\/(.+)$',
        'trailer': '',
        'pagination': '/show.php?a=180_2&so=%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath(
            '//div[@class="item"]/a[@class="itemimg"]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_image(self, response):
        image = self.process_xpath(
            response, self.get_selector_map('image')).get()

        if not image:
            image = response.xpath(
                '//div[@class="mainpic"]/img/@src').get().strip()

        if "src" in image:
            image = re.search('src=\"(.*?)\"\\ ', image).group(1).strip()

        return self.format_link(response, image)

    def get_domain(self, response):
        parsed_uri = urlparse(response.url)
        domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
        return domain

    def get_performers(self, response):
        performers = response.xpath(
            '//div[@class="lch"]/span[contains(@class,"lc_info")]/text()').get().strip()
        performers = performers.split(",")
        performers = list(filter(None, performers))

        return list(map(lambda x: x.strip(), performers))

    def get_trailer(self, response):
        image = response.xpath(
            '//script[contains(text(),"mp4")]').get().strip()
        image = self.get_domain(
            response) + re.search('src:\\s+\'(.*)\'', image).group(1).strip()
        return image
