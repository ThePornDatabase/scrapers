import re
import requests
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteSlaveToBondageSpider(BaseSceneScraper):
    name = 'SlaveToBondage'
    network = 'SlaveToBondage'
    parent = 'SlaveToBondage'
    site = 'SlaveToBondage'

    start_urls = [
        'https://www.slavetobondage.com',
    ]

    selector_map = {
        'title': '//div[contains(@class, "titleBlock")]/h2/text()',
        'description': '//div[contains(@class, "videoContent")]/p//text()',
        'performers': '//p[contains(text(), "Featuring")]/following-sibling::ul[1]/li/a/text()',
        'tags': '//p[contains(text(), "Tags")]/following-sibling::ul[1]/li/a/text()',
        'external_id': r'',
        'pagination': '/tour/categories/movies/%s/latest/',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = self.copy_meta(response)
        scenes = response.xpath('//div[contains(@class, "popularScene")]')
        for scene in scenes:
            scenelink = scene.xpath('.//div[contains(@class, "videoPicArea")]/a/@href').get()
            scenelink = self.format_url(response.url, scenelink)

            scenedate = scene.xpath('.//div[@class="date"]/text()')
            if scenedate:
                scenedate = scenedate.get()
                scenedate = self.parse_date(scenedate).strftime('%Y-%m-%d')
                meta['date'] = scenedate

            duration = scene.xpath('.//span[contains(text(), "Runtime:")]/text()')
            if duration:
                duration = duration.get()
                duration = re.search(r'((?:\d{1,2}:)?(?:\d{1,2}:)?\d{2})', duration)
                if duration:
                    duration = duration.group(1)
                    meta['duration'] = self.duration_to_seconds(duration)

            sceneid = scene.xpath('.//img/@id').get()
            if sceneid:
                sceneid = re.search(r'.*-(\d+)', sceneid)
                if sceneid:
                    meta['id'] = sceneid.group(1)
                else:
                    meta['id'] = re.search(r'.*/(.*?)\.', scenelink).group(0).lower()

            image = scene.xpath('.//div[contains(@class, "videoPicArea")]//img/@src0_3x')
            if image:
                meta['image'] = self.format_link(response, image.get())

            parse_scene = True
            if not self.check_item(meta, self.days):
                parse_scene = False

            if meta['id'] and parse_scene:
                yield scrapy.Request(scenelink, callback=self.parse_scene, meta=meta)
