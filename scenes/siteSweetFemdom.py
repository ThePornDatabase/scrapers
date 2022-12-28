import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteSweetFemdomSpider(BaseSceneScraper):
    name = 'SweetFemdom'
    network = 'SweetFemdom'
    parent = 'SweetFemdom'
    site = 'SweetFemdom'

    start_urls = [
        'https://sweetfemdom.com',
    ]

    selector_map = {
        'title': '//div[contains(@class, "videoDetails")]/h3/text()',
        'description': '//div[contains(@class, "videoDetails")]/p/text()',
        'date': '',
        'image': '//meta[@property="og:image"]/@content|//meta[@property="twitter:image"]/@content',
        'performers': '//li[@class="update_models"]/a/text()',
        'tags': '//li[contains(text(), "Tags")]/following-sibling::li/a[contains(@href, "/categories/")]/text()',
        'trailer': '//script[contains(text(), "video_content")]',
        're_trailer': r'video src=\"(.*?\.\w{3})',
        'external_id': r'.*/(.*)\.htm',
        'pagination': '/tour/categories/movies/%s/latest/',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "item-video")]')
        for scene in scenes:
            duration = scene.xpath('.//div[@class="time"]/text()').get()
            sceneduration = re.search(r'(\d{1,2}:\d{1,2}:?\d{1,2}?)', duration)
            if sceneduration:
                duration = sceneduration.group(1)
                meta['duration'] = self.duration_to_seconds(duration)
            scene = scene.xpath('./div/a/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_image(self, response):
        image = super().get_image(response)
        if not image:
            image = response.xpath('//script[contains(text(), "video_content")]')
            if image:
                image = re.search(r'poster=\"(.*?\.\w{3})', image.get())
                image = self.format_link(response, image.group(1))
        return image
