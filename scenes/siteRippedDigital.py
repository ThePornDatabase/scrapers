import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteRippedDigitalSpider(BaseSceneScraper):
    name = 'RippedDigital'
    network = 'Ripped Digital'
    parent = 'Ripped Digital'
    site = 'Ripped Digital'

    start_urls = [
        'https://ripped.digital',
    ]

    selector_map = {
        'description': '',
        'date': '//li[@class="text_med"]/comment()[contains(., "Date")]/following-sibling::text()',
        'date_formats': ['%m/%d/%Y'],
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//h4/following-sibling::p[@class="link_light"]/a[contains(@href, "model")]/text()',
        'tags': '//div[@class="blogTags"]/ul/li/a/text()',
        'trailer': '',
        'external_id': r'',
        'pagination': '/categories/movies_%s.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = self.copy_meta(response)
        scenes = response.xpath('//div[@class="latestUpdateB"]')
        for scene in scenes:
            sceneid = scene.xpath('./@data-setid').get()
            meta['id'] = sceneid

            title = scene.xpath('.//h4/a/text()')
            if title:
                meta['title'] = self.cleanup_title(title.get())

            duration = scene.xpath('.//i[contains(@class,"fa-video")]/following-sibling::text()')
            if duration:
                duration = duration.get().strip()
                duration = re.search(r'(\d+)', duration)
                if duration:
                    meta['duration'] = str(int(duration.group(1)) * 60)

            scene = scene.xpath('.//div[@class="utmodthumb"]/a/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_image(self, response):
        image = super().get_image(response)
        if "2x" in image:
            image = image.replace("2x", "4x")
        return image