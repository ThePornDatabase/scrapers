import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteRawFuckClubSpider(BaseSceneScraper):
    name = 'RawFuckClub'
    network = 'Raw Fuck Club'
    parent = 'Raw Fuck Club'
    site = 'Raw Fuck Club'

    start_urls = [
        'https://www.rawfuckclub.com',
    ]

    selector_map = {
        'title': '//div[@class="fluid-breadcrumbs"]/..//h2/text()',
        'description': '//p[@class="watch-description"]/text()',
        'date': '//p[@class="watch-published-date"]/text()[contains(., ",")]',
        're_date': r'(\w+ \d{1,2}, \d{4})',
        'date_formats': ['%B %d, %Y'],
        'image': '//meta[@property="og:image"]/@content|//meta[@name="twitter:image"]/@content',
        'performers': '//div[@class="tag-badges"]/a/span[contains(@class, "primary")]/text()',
        'tags': '//div[@class="tag-badges"]/a/span[contains(@class, "secondary")]/text()',
        'duration': '',
        'trailer': '',
        'external_id': r'video/(.*?)-',
        'pagination': '/browse/newest?page=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        # ~ scenes = response.xpath('//div[contains(@class,"slick-gallery-single")]/div[1]/div[1]/div[1]/div/a[contains(@class, "stateful-link")]/@href').getall()
        scenes = response.xpath('//a[@class="stateful-link"]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)
