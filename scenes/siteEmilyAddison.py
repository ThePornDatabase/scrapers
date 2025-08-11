import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteEmilyAddisonSpider(BaseSceneScraper):
    name = 'EmilyAddison'
    network = 'Emily Addison'
    parent = 'Emily Addison'
    site = 'Emily Addison'

    start_urls = [
        'https://www.emilyaddison.com',
    ]

    selector_map = {
        'title': '//div[contains(@class, "videoDetails")]/h3/text()',
        'date': '//div[contains(@class, "videoInfo")]//span[contains(text(), "Date")]/following-sibling::text()',
        'image': '//img[contains(@class, "update_thumb")]/@src0_2x',
        'performers': '//li[@class="update_models"]/a/text()',
        'tags': '//li[@class="label" and contains(text(), "Tags:")]/following-sibling::li/a/text()',
        'external_id': r'',
        'pagination': '/categories/movies/%s/latest/',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "item-video")]')
        for scene in scenes:
            duration = scene.xpath('.//div[@class="time"]/text()')
            if duration:
                duration = duration.get()
                duration = re.search(r'((?:\d{1,2}\:)?\d{2}\:\d{2})', duration)
                if duration:
                    meta['duration'] = self.duration_to_seconds(duration.group(1))

            scenedate = scene.xpath('.//div[@class="date"]/text()')
            if scenedate:
                scenedate = re.search(r'(\d{4}-\d{2}-\d{2})', scenedate.get())
                if scenedate:
                    meta['date'] = scenedate.group(1)

            scene = scene.xpath('./div[1]/a/@href').get()
            yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_id(self, response):
        imageid = response.xpath('//img[contains(@class, "update_thumb")]/@id')
        if imageid:
            imageid = re.search(r'-(\d+)', imageid.get())
            if imageid:
                return imageid.group(1)
        return re.search(r'.*/(.*?)\.htm', response.url).group(1).lower()

    def get_image(self, response):
        image = super().get_image(response)
        if image in response.url:
            return ""
        return image
