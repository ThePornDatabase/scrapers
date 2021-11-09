import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteCruelFuriesSpider(BaseSceneScraper):
    name = 'CruelFuries'
    network = 'Cruel Furies'

    start_urls = [
        'https://www.cruel-furies.com',
    ]

    cookies = {
        'fury_site_accepted': 'eyJpdiI6InphQ3pBcXp3MmFDV1lRNFEySVwvT2NnPT0iLCJ2YWx1ZSI6Ikg0WkhUK2dONHhPSzlOY1dHVGNXZEE9PSIsIm1hYyI6ImIwOTAxNjljNDI1Yzc2M2UyNzFhNzQwMDQzNzM1ZmRjOTY4MDczNDc5YWZlNWRlMGYyNjliZTg5MDhlNGRiMzcifQ',
    }

    selector_map = {
        'title': '//div[contains(@class,"model-info")]/h3/text()',
        'description': '//div[contains(@class,"model-info")]/p[contains(@class,"mt-4")]/preceding-sibling::p[1]/text()',
        'performers': '//div[contains(@class,"model-info")]//span[contains(text(),"Starring")]/following-sibling::span/a/text()',
        'date': '//div[contains(@class,"model-info")]//span[contains(text(),"Uploaded")]/following-sibling::span/text()',
        'date_formats': ['%Y-%m-%d'],
        'image': '//meta[@property="og:image"]/@content',
        'tags': '//meta[@name="keywords"]/@content',
        'external_id': r'(\d+)$',
        'trailer': '//video/source/@src',
        'pagination': '/list/%s',
    }

    def start_requests(self):
        url = "https://www.cruel-furies.com/"
        yield scrapy.Request(url,
                             callback=self.start_requests2,
                             meta={'page': self.page},
                             headers=self.headers,
                             cookies=self.cookies)

    def start_requests2(self, response):
        for link in self.start_urls:
            yield scrapy.Request(url=self.get_next_page_url(link, self.page),
                                 callback=self.parse,
                                 meta={'page': self.page},
                                 headers=self.headers,
                                 cookies=self.cookies)

    def get_scenes(self, response):
        scenes = self.process_xpath(response, '//div[@class="name"]/h3/a/@href').getall()
        for scene in scenes:
            yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_site(self, response):
        return "Cruel Furies"

    def get_parent(self, response):
        return "Cruel Furies"

    def get_tags(self, response):
        if self.get_selector_map('tags'):
            tags = self.process_xpath(response, self.get_selector_map('tags')).get()
            if tags:
                tags = tags.split(',')
                return list(map(lambda x: x.strip().title(), tags))

        return []

    def get_next_page_url(self, base, page):
        url = self.format_url(base, self.get_selector_map('pagination') % page)
        print(f'URL: {url}')
        return url
