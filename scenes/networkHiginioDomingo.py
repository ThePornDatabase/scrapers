import re
import unidecode
import html
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class NetworkHiginioDomingoSpider(BaseSceneScraper):
    name = 'HiginioDomingo'
    parent = 'Higinio Domingo'
    network = 'Higinio Domingo'

    start_urls = [
        'https://charmmodels.net',
        'https://domingoview.com',
        'https://letstryhard.com',
        'https://test-shoots.com',
    ]

    selector_map = {
        'title': '//span[@class="update_title"]/text()',
        'description': '//span[contains(@class,"latest_update_description")]/text()',
        'date': '//span[contains(@class,"availdate")]/text()',
        'date_formats': ['%m/%d/%Y'],
        'image': '//div[@class="update_table_right"]/div[1]/a/img/@src0_2x|//div[@class="update_table_right"]/div[1]/a/img/@src0_3x|//div[@class="update_table_right"]/div[1]/a/img/@src0_4x',
        'performers': '//span[contains(@class,"tour_update_models")]/a/text()',
        'tags': '//span[contains(@class,"update_tags")]/a/text()',
        'trailer': '//div[@class="update_table_right"]/div[1]/a[1]/@onclick',
        're_trailer': r'\([\'\"](/.*)[\'\"]',
        'external_id': r'.*/(.*?)\.htm',
        'pagination': '/categories/movies_%s_d.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="updateItem"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_duration(self, response):
        duration = response.xpath('//div[@class="update_counts_preview_table"]/text()')
        if duration:
            duration = duration.get()
            duration = unidecode.unidecode(html.unescape(duration.lower().replace("&nbsp;", " ").replace("\xa0", " ")))
            duration = re.sub(r'[^a-z0-9]+', '', duration)
            duration = re.search(r'(\d+)min', duration)
            if duration:
                return str(int(duration.group(1)) * 60)
        return None
