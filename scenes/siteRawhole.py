import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteRawholeSpider(BaseSceneScraper):
    name = 'Rawhole'
    network = 'Rawhole'
    parent = 'Rawhole'
    site = 'Rawhole'

    start_urls = [
        'https://www.rawhole.com',
    ]

    selector_map = {
        'title': '//div[contains(@class, "product-page")]/div[1]/h1/text()',
        'description': '//div[@class="description"]/text()',
        'date': '//li[contains(text(), "Added:")]/text()',
        're_date': r'(\d{1,2} \w{3,4} \d{4})',
        'date_formats': ['%d %b %Y'],
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//div[@class="model-v"]//h1/text()',
        'tags': '//i[contains(@class, "fa-tags")]/following-sibling::a/text()',
        'duration': '//li[contains(text(), "Length:")]/text()',
        're_duration': r'((?:\d{1,2}\:)?\d{2}\:\d{2})',
        'trailer': '',
        'external_id': r'',
        'pagination': '/categories/scenes_%s_d.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="product-item"]/div[1]/a[1]/@href').getall()
        for scene in scenes:
            yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_tags(self, response):
        tags = super().get_tags(response)
        tags2 = []
        for tag in tags:
            if "rawhole" not in tag.lower():
                tags2.append(tag.replace("#", ""))
        tags2.append("Gay")
        return tags2

    def get_id(self, response):
        image = self.get_image(response)
        return re.search(r'.*/(\d+)-', image).group(1)

    def get_performers_data(self, response):
        performers = response.xpath('//div[@class="model-v"]')
        performers_data = []
        if len(performers):
            for performer in performers:
                perf = {}
                perf['name'] = performer.xpath('.//h1/text()').get()
                perf['extra'] = {}
                perf['extra']['gender'] = "Male"
                perf['network'] = "Rawhole"
                perf['site'] = "Rawhole"
                image = performer.xpath('.//img/@src')
                if image:
                    image = image.get()
                    if "content" in image:
                        perf['image'] = image
                        perf['image_blob'] = self.get_image_blob_from_link(image)
                performers_data.append(perf)
        return performers_data
