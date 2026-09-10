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
        'description': '//meta[@name="description"]/@content',
        'date': '//li[contains(text(), "Added:")]/text()',
        # Reads "  Added: Sept. 7, 2026" - dateparser copes with "Sept." but not the
        # "Added:" prefix, so the prefix is stripped here rather than pinning a format.
        're_date': r'Added:\s*(.+)',
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//div[@class="model-v"]//h1/text()',
        # The fa-tags block is gone; the keywords meta is site-wide, not per scene
        'tags': '',
        'duration': '//li[contains(text(), "Length:")]/text()',
        're_duration': r'((?:\d{1,2}\:)?\d{2}\:\d{2})',
        'trailer': '',
        'external_id': r'/free-video/(.*?)\.html',
        'pagination': '/categories/scenes_%s_d.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = self.copy_meta(response)
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
                image = performer.xpath('.//img/@src').get()
                if image and "content" in image:
                    image = self.format_link(response, image)
                    perf['image'] = image
                    perf['image_blob'] = self.get_image_blob_from_link(image)
                performers_data.append(perf)
        return performers_data
