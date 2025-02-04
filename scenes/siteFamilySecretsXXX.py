import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteFamilySecretsXXXSpider(BaseSceneScraper):
    name = 'FamilySecretsXXX'
    network = 'Exposed Whores Media'
    parent = 'Family Secrets XXX'
    site = 'Family Secrets XXX'

    start_urls = [
        'https://familysecretsxxx.com'
    ]

    selector_map = {
        'title': '//span[contains(@class,"update_title")]/text()',
        'description': '//span[contains(@class,"latest_update_description")]/text()',
        'date': '//span[contains(@class,"availdate")]/text()',
        'date_formats': ['%m/%d/%Y'],
        'image': '//div[@class="update_table_right"]/div[1]/a/img/@src0_2x',
        'performers': '//div[@class="update_block_info"]/span[contains(@class,"tour_update_models")]/a/text()',
        'tags': '//span[contains(@class,"update_tags")]/a/text()',
        'external_id': r'/updates/(.+)\.html',
        'pagination': '/tour/categories/movies_%s.html'
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="updateItem"]/a[1]/@href').getall()
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
