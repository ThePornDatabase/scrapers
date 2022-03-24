import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class DeepLushSpider(BaseSceneScraper):
    name = 'DeepLush'
    network = 'Deep Lush'
    parent = 'Deep Lush'

    start_urls = ["https://deeplush.com"]

    selector_map = {
        'title': '//h2/text()',
        'description': '//div[@class="collapse "]//text()',
        'tags': '//a[contains(@href,"/video/category/")]//text()',
        'performers': '//a[contains(@class,"performer")]//text()',
        'image': '//video/@poster',
        'trailer': '//video/source[last()]/@src',
        'date': '//span[@class="date"]//text()',
        'date_formats': ['%d %b %Y'],
        'external_id': '[0-9]+/(.+)',
        'pagination': 'video/gallery/%s',
    }

    def get_next_page_url(self, base, page):
        return self.format_url(base, self.get_selector_map('pagination') % ((page - 1) * 12))

    def get_scenes(self, response):
        for scene in response.xpath('//a[contains(@href, "/video/watch/")]/@href').getall():
            yield scrapy.Request(
                url=self.format_link(response, scene),
                callback=self.parse_scene)
