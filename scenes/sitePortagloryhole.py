import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SitePortagloryholeSpider(BaseSceneScraper):
    name = 'PortaGloryhole'
    network = 'PortaGloryhole'
    parent = 'PortaGloryhole'
    site = 'PortaGloryhole'

    start_urls = [
        'https://www.portagloryhole.com',
    ]

    selector_map = {
        'title': '//h2[contains(@class, "underline")]/text()',
        'description': '',
        'date': '//p/strong/comment()',
        're_date': r'(\d{2}/\d{2}/\d{4})',
        'date_formats': ['%m/%d/%Y'],
        'image': '//a[@name="update"]/following-sibling::div/a/img/@src',
        'performers': '//h5/a[contains(@href, "/models/")]/text()',
        'tags': '//h5/a[contains(@href, "/categories/")]/text()',
        'duration': '//strong[contains(text(), "Length:")]/following-sibling::text()',
        'trailer': '',
        'external_id': r'.*/(.*?)\.htm',
        'pagination': '/t2/categories/movies_%s_d.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="details"]/h5/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)
