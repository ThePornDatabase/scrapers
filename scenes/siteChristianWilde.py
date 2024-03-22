import re
import html
import unidecode
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteChristianWildeSpider(BaseSceneScraper):
    name = 'ChristianWilde'
    site = 'Christian Wilde'
    parent = 'Christian Wilde'
    network = 'Christian Wilde'

    start_urls = [
        'https://christianwilde.com',
    ]

    selector_map = {
        'title': '//span[contains(@class,"update_title")]/text()',
        'description': '//span[contains(@class,"update_description")]/text()',
        'date': '//span[contains(@class,"availdate")]/text()[1]',
        're_date': r'(\d{1,2}/\d{1,2}/\d{4})',
        'date_formats': ['%m/%d/%Y'],
        'image': '//div[contains(@class,"update_image")]/a[contains(@href, "updates")][1]/img/@src0_4x|//div[contains(@class,"update_image")]/a[contains(@href, "updates")][1]/img/@src0_3x|//div[contains(@class,"update_image")]/a[contains(@href, "updates")][1]/img/@src0_2x|//div[contains(@class,"update_image")]/a[contains(@href, "updates")][1]/img/@src0_1x',
        'performers': '//span[contains(@class,"update_models")]/a/text()',
        'tags': '//span[contains(@class,"update_tags")]/a/text()',
        'duration': '',
        'trailer': '//div[contains(@class,"update_image")]/a[contains(@href, "updates")][1]/@onclick',
        're_trailer': r'\'(/trailer.*?)\'',
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

    def get_id(self, response):
        return super().get_id(response).lower()

    def get_duration(self, response):
        duration = response.xpath('//div[@class="update_counts_preview_table"]/text()')
        if duration:
            duration = duration.get()
            duration = unidecode.unidecode(html.unescape(duration.lower().replace("&nbsp;", " ").replace("\xa0", " "))).replace(" ", "")
            duration = re.search(r'(\d+)min', duration)
            if duration:
                return str(int(duration.group(1)) * 60)
        return None

    def get_description(self, response):
        return super().get_description(response).replace("\r", " ").replace("\n", " ").replace("\t", " ")
