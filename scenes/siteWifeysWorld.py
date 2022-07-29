import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteWifeysWorldSpider(BaseSceneScraper):
    name = 'WifeysWorld'
    network = 'Wifeys World'
    parent = 'Wifeys World'
    site = 'Wifeys World'

    headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Mobile Safari/537.36'}

    custom_scraper_settings = {
        'AUTOTHROTTLE_ENABLED': True,
        'USER_AGENT': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Mobile Safari/537.36',
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
            'scrapy_fake_useragent.middleware.RandomUserAgentMiddleware': None,
            'scrapy_fake_useragent.middleware.RetryUserAgentMiddleware': None,
            'scrapy.downloadermiddlewares.cookies.CookiesMiddleware': 100,
            'tpdb.custommiddlewares.CustomProxyMiddleware': 350,
            'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 400,
        }
    }

    start_urls = [
        'https://m.wifeysworld.com',
    ]

    selector_map = {
        'title': '//title/text()',
        'description': '//span[contains(@class, "description")]/text()',
        'date': '//span[@class="update_date"]/text()',
        'date_formats': ['%m/%d/%Y'],
        'image': '//div[contains(@class, "block_image")]/a//img/@src0_2x',
        'performers': '',
        'tags': '//span[contains(@class, "update_tags")]/a/text()',
        'trailer': '',
        'external_id': r'.*/(.*?)\.htm',
        'pagination': '/tour/categories/updates_%s_d.html'
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="updateItem"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta, headers=self.headers)

    def get_title(self, response):
        title = super().get_title(response)
        if " - Wifey" in title:
            title = re.search(r'(.*) - Wifey', title).group(1)
        title = title.replace("Wifey's World", "")
        return title.strip()

    def get_performers(self, response):
        return ['Sandra Otterson']

    def get_description(self, response):
        description = super().get_description(response)
        return description.replace("\n", "").replace("\r", "").replace("\t", "")
