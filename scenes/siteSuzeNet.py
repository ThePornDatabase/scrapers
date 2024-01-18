import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteSuzeNetSpider(BaseSceneScraper):
    name = 'SuzeNet'
    network = 'SuzeNet'
    parent = 'SuzeNet'
    site = 'SuzeNet'

    start_urls = [
        'https://suze.net',
    ]

    selector_map = {
        'title': '//h2//text()',
        'description': '//div[@class="description"]/p/text()',
        'date': '//h3[contains(text(), "info")]/following-sibling::p/text()',
        're_date': r'dded:.*?(\w+ \d{1,2}, \d{4})',
        'date_formats': ['%B %d, %Y'],
        'image': '//img[contains(@class, "update_thumb")]/@src0_4x|//img[contains(@class, "update_thumb")]/@src0_3x|//img[contains(@class, "update_thumb")]/@src0_2x',
        'performers': '//h3[contains(text(), "info")]/following-sibling::p/a/text()',
        'tags': '',
        'trailer': '',
        'external_id': r'.*/(.*?)\.htm',
        'pagination': '/tour/categories/movies_%s_d.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "item-video")]')
        for scene in scenes:
            origimage = scene.xpath('.//img/@src0_4x|.//img/@src0_3x|.//img/@src0_2x|.//img/@src0_1x')
            if origimage:
                meta['origimage'] = self.format_link(response, origimage.get())

            scene = scene.xpath('./div[1]/a/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_duration(self, response):
        duration = response.xpath('//h3[contains(text(), "info")]/following-sibling::p/text()')
        if duration:
            duration = duration.getall()
            duration = "".join(duration).replace("\n", "").replace("\r", "").replace("\t", "")
            duration = re.search(r'untime:.*?((?:\d{1,2}\:)?\d{2}\:\d{2})', duration)
            if duration:
                return self.duration_to_seconds(duration.group(1))
        return None

    def get_image(self, response):
        meta = response.meta
        image = super().get_image(response)
        if ".jpg" in image or ".png" in image:
            return image
        return meta['origimage']
