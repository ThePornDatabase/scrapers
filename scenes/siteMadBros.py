import re
import string
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteMadBrosSpider(BaseSceneScraper):
    name = 'MadBros'
    site = 'MadBros'
    parent = 'MadBros'
    network = 'MadBros'

    start_urls = [
        'https://madbrosx.com'
    ]

    selector_map = {
        'title': '//div[@class="mx-heading-h4"]/text()',
        'description': '//div[contains(@class, "mx-single-video-info-excerpt")]/p/text()',
        'date': '//div[contains(@class, "info-meta-date")]/text()[contains(., "date")]',
        're_date': r'(\d{1,2}/\d{1,2}/\d{4})',
        'date_formats': ['%d/%m/%Y'],
        'performers': '//div[contains(text(), "Featuring")]/a/text()',
        'type': 'Scene',
        'external_id': r'.*/(.*?)/$',
        'pagination': '/videos/page/%s/',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="wpb_wrapper"]/div[@class="mx-video-item"]')
        for scene in scenes:
            duration = scene.xpath('.//div[@class="video-duration"]/text()')
            if duration:
                duration = re.sub(r'[^0-9:]+', '', duration.get())
                meta['duration'] = self.duration_to_seconds(duration)

            image = scene.xpath('.//img/@src')
            if image:
                meta['image'] = image.get()
                meta['image_blob'] = self.get_image_blob_from_link(meta['image'])

            meta['trailer'] = scene.xpath('./div[1]/@data-preview-src').get()

            sceneid = scene.xpath('.//div[@class="mx-cart"]/@data-href').get()
            meta['id'] = re.search(r'=(\d+)', sceneid).group(1)

            scene = scene.xpath('./div[1]/a/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_image(self, response):
        image = response.xpath('//div[@data-vjs-player]/div/iframe/@src')
        if image:
            image = image.get()
            image = re.search(r'.*/(.*?)\?', image)
            if image:
                image = image.group(1)
                return f"https://vz-02cf0b27-667.b-cdn.net/{image}/thumbnail.jpg"
        return None

    def get_tags(self, response):
        tags = []
        taglist = response.xpath('//div[contains(@class, "video-info-categories")]/a/text()').getall()
        for tagentry in taglist:
            tagentry = string.capwords(tagentry.replace("#", ""))
            tags.append(tagentry)
        return tags
