import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteViktorRomSpider(BaseSceneScraper):
    name = 'ViktorRom'
    network = 'Viktor Rom'
    parent = 'Viktor Rom'
    site = 'Viktor Rom'

    start_urls = [
        'https://www.viktor-rom.com',
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '//h2[contains(@class, "my-text")]/text()',
        'date': '//script[contains(text(), "@context")]/text()',
        're_date': r'datePublished.*?(\d{4}-\d{2}-\d{2})',
        'image': '//script[contains(text(), "@context")]/text()',
        're_image': r'ImageObject.*?(http.*)[\'\"]',
        'performers': '//i[contains(@class, "far fa-star")]/following-sibling::text()',
        'tags': '//h3[@class="h90" and not(./i)]/text()',
        'duration': '',
        'trailer': '',
        'external_id': r'.*/(\d+)-',
        'pagination': '/en/videos?page=%s',
        'type': 'Scene',
    }

    def get_next_page_url(self, base, page):
        page = str(int(page) - 1)
        return self.format_url(base, self.get_selector_map('pagination') % page)

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class,"col-lg-6 col-12")]/div[contains(@class, "h4 pt-3")]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_tags(self, response):
        tags = super().get_tags(response)
        if "Gay" not in tags:
            tags.append("Gay")
        return tags
