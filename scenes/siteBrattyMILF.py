import re
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteBrattyMILFSpider(BaseSceneScraper):
    name = 'BrattyMILF'
    site = 'Bratty MILF'
    parent = 'Bratty MILF'
    network = 'Nubiles'

    start_urls = [
        'https://brattymilf.com/',
    ]

    selector_map = {
        'title': '//h2/text()',
        'description': '//div[contains(@class, "collapse")]/p/text()',
        'date': '//div[@class="container"]/div/div/div[@class="clearfix"]/span[@class="date"]/text()',
        'image': '//meta[@property="og:image"]/@content',
        'image_blob': '//meta[@property="og:image"]/@content',
        'performers': '//div[@class="content-pane-performers"]/a/text()',
        'tags': '//div[@class="categories"]/a/text()',
        'external_id': r'watch/(\d+)/',
        'trailer': '',
        'pagination': '/video/gallery/%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//figcaption/div/span/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_next_page_url(self, base, page):
        page = str((int(page) - 1) * 12)
        return self.format_url(base, self.get_selector_map('pagination') % page)
