import re
import string
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteRaveBunnysSpider(BaseSceneScraper):
    name = 'RaveBunnys'
    network = 'RaveBunnys'
    parent = 'RaveBunnys'
    site = 'RaveBunnys'

    start_urls = [
        'https://ravebunnys.com',
    ]

    selector_map = {
        'description': '//div[contains(@class, "videoDetails")]/p//text()',
        'performers': '//li[@class="update_models"]/a/text()',
        'tags': '//div[contains(@class, "featuring")]/ul/li/a[contains(@href, "categories")]/text()',
        'external_id': r'',
        'pagination': '/categories/movies/%s/latest/',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class,"item-video")]')
        for scene in scenes:
            scenedate = scene.xpath('.//div[@class="date"]/text()').get()
            if scenedate:
                scenedate = self.parse_date(scenedate.strip(), date_formats=['%m/%d/%Y']).strftime('%Y-%m-%d')
                meta['date'] = scenedate

            title = scene.xpath('.//h4/a/text()').get()
            if title:
                title = title.strip()
                meta['title'] = string.capwords(self.cleanup_title(title)).replace("- Video","").strip()

            sceneid = scene.xpath('.//img/@id').get()
            if sceneid:
                sceneid = re.search(r'.*-(\d+)', sceneid)
                if sceneid:
                    sceneid = sceneid.group(1)
                    meta['id'] = sceneid

            image = scene.xpath('.//img/@src0_3x').get()
            if image:
                image = self.format_link(response, image)
                meta['image'] = image

            duration = scene.xpath('.//div[@class="time"]/text()').get()
            if duration:
                duration = re.search(r'((?:\d{1,2}\:)?\d{2}\:\d{2})', duration.strip())
                if duration:
                    meta['duration'] = self.duration_to_seconds(duration.group(1))

            sceneurl = scene.xpath('.//h4/a/@href').get()

            if self.check_item(meta, self.days) and meta['id']:
                meta['image_blob'] = self.get_image_blob_from_link(image)
                yield scrapy.Request(url=self.format_link(response, sceneurl), callback=self.parse_scene, meta=meta)
