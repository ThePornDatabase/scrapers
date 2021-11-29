import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteGirlsFuckGirlsSpider(BaseSceneScraper):
    name = 'GirlsFuckGirls'
    network = 'Girls Fuck Girls'

    start_urls = [
        'https://girlsfuckgirls.com',
    ]

    selector_map = {
        'title': '//div[contains(@class, "videoDetails")]//h3/text()',
        'description': '//div[contains(@class, "videoDetails")]//p/text()',
        'performers': '//div[contains(@class, "featuring") and contains(., "Featuring")]//following-sibling::li/a/text()',
        'date': '//div[contains(@class, "videoInfo")]//following-sibling::p[contains(., "Date")]/text()',
        'image': '//meta[@property="og:image"]/@content',
        'tags': '//div[contains(@class,"featuring")]/ul/li/a[contains(@href,"categories")]/text()',
        'external_id': r'/trailers/(.*).html',
        'trailer': '//script[contains(text(),"video_content")]/text()',
        're_trailer': r'video src=\"(.*?\.mp4)',
        'pagination': '/categories/movies/%s/latest/',
    }

    def get_scenes(self, response):
        scenes = self.process_xpath(response, '//div[@class="item-thumb"]/a/@href').getall()
        for scene in scenes:
            yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_image(self, response):
        image = self.process_xpath(response, self.get_selector_map('image')).get()
        if image:
            image = self.format_link(response, image)
            return image.replace("-1x.jpg", "-2x.jpg")
        return None
