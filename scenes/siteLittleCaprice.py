import re
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class LittleCapriceSpider(BaseSceneScraper):
    name = 'LittleCaprice'
    network = 'Little Caprice Dreams'

    start_urls = [
        'https://www.littlecaprice-dreams.com'
    ]

    custom_scraper_settings = {
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 1,
        'AUTOTHROTTLE_MAX_DELAY': 60,
        'CONCURRENT_REQUESTS': 1,
        'DOWNLOAD_DELAY': 2,
    }

    selector_map = {
        'title': '//header[@class="project-header"]/h1/text()',
        'description': '//div[@class="desc-text"]/text()',
        'performers': '//div[@class="title"]/b[contains(text(), "Models")]/../following-sibling::div[1]/a/text()',
        'date': '//meta[@name="og:published_time"]/@content',
        're_date': r'(\d{4}-\d{2}-\d{2})',
        'duration': '//b[contains(text(), "Video Duration")]/following-sibling::text()',
        'image': '//meta[@name="og:image"]/@content',
        'tags': '//div[@class="title"]/b[contains(text(), "Tags")]/../following-sibling::div[1]/a/text()',
        'external_id': '',
        'trailer': '',
        'pagination': '/videos/?page=%s'
    }

    def start_requests2(self, response):
        for pagination in self.paginations:
            yield scrapy.Request(url=self.get_next_page_url(self.url, self.page, pagination), callback=self.parse, meta={'page': self.page, 'pagination': pagination}, headers=self.headers, cookies=self.cookies)

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//a[contains(@class,"project-preview") and contains(@class, "project-type-video")]')
        for scene in scenes:
            sceneid = scene.xpath('./@class').get()
            sceneid = re.search(r'project-(\d+) ', sceneid)
            if sceneid:
                meta['id'] = sceneid.group(1)
                scene = scene.xpath('./@href').get()
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_site(self, response):
        site = response.xpath('//div[@class="project-tags"]//b[contains(text(), "Series:")]/../following-sibling::div[@class="list"]/a[contains(@href, "/collection/")]/text()')
        if site:
            site = site.get().replace(" ", "")
            if "series" in site.lower():
                site = site.lower().replace("series", "")
            return site
        return "Little Caprice Dreams"

    def get_parent(self, response):
        return "Little Caprice Dreams"

    def get_network(self, response):
        return "Little Caprice Dreams"

    def get_image(self, response):
        image = super().get_image(response)
        if not image or len(image) < 50:
            image = response.xpath('//div[@id="main-project-content"]/div/div[@class="video"]/div/@style')
            if image:
                image = re.search(r'url.*?(http.*?)[\'\"]', image.get())
                if image:
                    image = image.group(1)
        return image
