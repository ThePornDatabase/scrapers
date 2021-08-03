import scrapy
import re
import dateparser

from tpdb.BaseSceneScraper import BaseSceneScraper


class siteTerrorXXXSpider(BaseSceneScraper):
    name = 'TerrorXXX'
    network = 'Terror XXX'
    parent = 'Terror XXX'

    start_urls = [
        'https://terrorxxx.com',
    ]

    selector_map = {
        'title': '//div[contains(@class,"title")]/span[@class="update_title"]/text()',
        'description': '//span[contains(@class,"description")]/text()',
        'date': '',
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//span[@class="tour_update_models"]/a/text()',
        'tags': '',
        'external_id': '.*\/(.*?).html',
        'trailer': '//script[contains(text(),"/trailers/")]',
        're_trailer': '\"(\/trailers.*?\.mp4)\"',
        'pagination': '/categories/Movies_%s_d.html'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="updateItem"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_site(self, response):
        return "Terror XXX"
        
    def get_parent(self, response):
        return "Terror XXX"
        
    def get_date(self, response):
        return dateparser.parse('today').isoformat()


    def get_trailer(self, response):
        if 'trailer' in self.get_selector_map() and self.get_selector_map('trailer'):
            trailer = self.process_xpath(response, self.get_selector_map('trailer'))
            if trailer:
                trailer = self.get_from_regex(trailer.get(), 're_trailer')
                return "https://terrorxxx.com/" + trailer.replace(" ", "%20")

        return ''
