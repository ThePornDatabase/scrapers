import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteYanksSpider(BaseSceneScraper):
    name = 'Yanks'
    site = 'Yanks'
    parent = 'Yanks'
    network = 'Yanks'

    start_urls = [
        'https://www.yanks.com'
    ]

    selector_map = {
        'title': '//div[@class="main"]/div[1]/div[1]//div[contains(@class, "main-title")]/h2/text()',
        'description': '//ul[@class="tags"]/../preceding-sibling::div[1]/text()',
        'performers': '//div[contains(@class,"update-info-row")]/strong[contains(text(), "Featuring")]/following-sibling::a[not(contains(text(), "&"))]/text()',
        'date': '//div[contains(@class,"update-info-row")]/strong[contains(text(), "Added")]/following-sibling::text()[1]',
        'date_formats': ['%B %d, %Y'],
        'image': '//script[contains(text(), "video_content")]/text()',
        're_image': r'poster=[\'\"](.*?)[\'\"]',
        'tags': '//ul[@class="tags"]/li/a/text()',
        'trailer': '//script[contains(text(), "video_content")]/text()',
        're_trailer': r'src=[\'\"](.*?)[\'\"]',
        'external_id': r'.*/(.*?)\.htm',
        'pagination': '/categories/Movies_%s_d.html'
    }

    def start_requests(self):
        meta = {}
        meta['page'] = self.page
        meta['check_date'] = "2024-03-15"

        for link in self.start_urls:
            yield scrapy.Request(url=self.get_next_page_url(link, self.page), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="item-title"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)
