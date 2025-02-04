import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class ExposedBondageSpider(BaseSceneScraper):
    name = 'ExposedBondage'
    network = 'Exposed Whores Media'
    parent = 'Exposed Bondage'
    site = 'Exposed Bondage'

    start_urls = [
        'https://exposedbondage.com'
    ]

    selector_map = {
        'title': '//span[contains(@class,"update_title")]/text()',
        'description': '',
        'date': '//span[contains(@class,"update_date")]/text()',
        'date_formats': ['%m/%d/%Y'],
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//div[@class="update_block_info"]/span[contains(@class,"tour_update_models")]/a/text()',
        'tags': '//span[contains(@class,"update_tags")]/a/text()',
        'external_id': r'/updates/(.+)\.html',
        'trailer': '//div[@class="update_image"]/a/@onclick',
        're_trailer': r'tload\(\'(.*)\'\)',
        'pagination': '/tour/categories/updates_%s_d.html'
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="update_details"]/a[1]/@href').getall()
        for scene in scenes:
            yield scrapy.Request(url=scene, callback=self.parse_scene, meta=meta)

    def get_trailer(self, response, path=None):
        if 'trailer' in self.get_selector_map():
            trailer = self.get_element(response, 'trailer', 're_trailer')
            if trailer:
                if type(trailer) is list:
                    trailer = trailer[0]
                if "tload" in trailer:
                    trailer = re.search(r'tload\(\'(.*)\'\)', trailer).group(1)
                if path:
                    return self.format_url(path, trailer).replace(' ', '%20')
                else:
                    return self.format_link(response, trailer).replace(' ', '%20')

        return ''
