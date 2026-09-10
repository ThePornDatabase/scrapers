import re
import scrapy
import string
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteDieselVidsSpider(BaseSceneScraper):
    name = 'DieselVids'
    network = 'DieselVids'
    parent = 'DieselVids'
    site = 'DieselVids'

    start_urls = [
        'https://dieselvids.com',
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '',
        'date': '//i[contains(@class, "calendar")]/following-sibling::text()',
        'date_formats': ['%d/%m/%Y'],
        'image': '//meta[@property="og:image"]/@content',
        'tags': '//div[contains(@class, "description")]/ul/li/a/text()',
        'duration': '//i[contains(@class, "clock")]/following-sibling::text()',
        'trailer': '',
        'external_id': r'.*-(\d+)',
        'pagination': '/videos/page%s.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = self.copy_meta(response)
        scenes = response.xpath('//h3/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_performers(self, response):
        title = super().get_title(response)
        title = string.capwords(title)
        performers = []
        if "&" in title:
            performers = [performer.strip() for performer in title.split("&")]
        else:
            performers = [title.strip()]
        return performers
