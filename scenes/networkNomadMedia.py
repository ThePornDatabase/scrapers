import re
from urllib.parse import urlparse
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class NomadMediaSpider(BaseSceneScraper):
    name = 'NomadMedia'
    network = "Nomad Media"

    start_urls = [
        'https://www.aziani.com',
        'https://www.gangbangcreampie.com',
        'https://www.gloryholesecrets.com',
    ]

    selector_map = {
        'title': '//div[contains(@class,"trailer")]/h2/text()',
        'description': '//div[@class="desc"]/p/text()',
        'date': '',
        'image': '//img[@id="set-target-1_0"]/@src | //video/@poster',
        'performers': '//h5/a[contains(@href,"/models/")]/text()',
        'tags': '//h5[@class="video_categories"]/a/text()',
        'trailer': '//video/source/@src',
        'external_id': '.*\\/(.*?)\\.html$',
        'pagination': '/tour/categories/movies_%s_d.html'
    }

    def get_scenes(self, response):

        sceneresponses = response.xpath('//div[@class="details"]')
        for sceneresponse in sceneresponses:
            date = sceneresponse.xpath('./p/strong/text()')
            if date:
                date = self.parse_date(date.get().strip()).isoformat()
            else:
                date = self.parse_date('today').isoformat()

            scene = sceneresponse.xpath('./h5/a/@href').get().strip()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta={'date': date})

    def get_image(self, response):
        image = self.process_xpath(
            response, self.get_selector_map('image')).get()

        if image is not None:
            return self.format_link(response, image)

    def get_trailer(self, response):
        parsed_uri = urlparse(response.url)
        domain = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)
        if 'trailer' in self.get_selector_map() and self.get_selector_map('trailer'):
            trailer = self.process_xpath(response, self.get_selector_map('trailer')).get()
            if trailer:
                if trailer[0] == "/":
                    trailer = domain + trailer
                return trailer
        return ''
