import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
true = True
false = False


class SiteHarlemSexSpider(BaseSceneScraper):
    name = 'HarlemSex'
    site = 'Harlem Sex'
    parent = 'Harlem Sex'
    network = 'Harlem Sex'

    start_urls = [
        'https://www.harlemsex.com'
    ]

    cookies = []

    selector_map = {
        'title': '//h1/text()',
        'description': '//h2/text()',
        'date': '//script[contains(text(), "datePublished")]/text()',
        're_date': r'datePublished.*?(\d{4}-\d{2}-\d{2})',
        'image': '//comment()[contains(., "TRAILER")]/following-sibling::div//img/@src',
        'performers': '',
        'tags': '//comment()[contains(., "TAGS")]/following-sibling::div//a/h3/text()',
        'trailer': '//comment()[contains(., "TRAILER")]/following-sibling::div//source/@src',
        'type': 'Scene',
        'external_id': r'.*/(\d+)-',
        'pagination': '/en/videos?page=%s',
    }

    def get_next_page_url(self, base, page):
        if int(page) == 1:
            return "https://www.harlemsex.com/en/videos?"
        page = str(int(page) - 1)
        return self.format_url(base, self.get_selector_map('pagination') % page)

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "video-gallery")]/a[1]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)
