import re
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteToughLoveXSpider(BaseSceneScraper):
    name = 'ToughLoveX'
    network = 'Radical Entertainment'
    parent = 'ToughLoveX'

    start_urls = [
        'https://tour.toughlovex.com',
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '//div[@class="description"]/p/text()',
        'date': '',
        'image': '//div[@class="player-wrap"]/@style',
        're_image': r'(http.*\.jpg)',
        'performers': '//dt[contains(text(),"Starring")]/following-sibling::dd/a/text()',
        'tags': '',
        'external_id': r'view/(\d+)/',
        'trailer': '//div[@class="player-wrap"]//video/source/@src',
        'pagination': '/videos?order=publish_date&sort=desc&page=%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="content-box"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_site(self, response):
        return "ToughLoveX"

    def get_trailer(self, response):
        if 'trailer' in self.get_selector_map() and self.get_selector_map('trailer'):
            trailer = self.process_xpath(response, self.get_selector_map('trailer'))
            if trailer:
                trailer = self.get_from_regex(trailer.get(), 're_trailer')
                return trailer.replace(" ", "%20")

        return ''
