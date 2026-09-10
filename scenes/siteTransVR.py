import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteTransVRSpider(BaseSceneScraper):
    name = 'TransVR'
    site = 'TransVR'
    parent = 'TransVR'
    network = 'Grooby Network'

    start_urls = [
        'https://www.transvr.com'
    ]

    selector_map = {
        'title': '//div[@class="trailer_toptitle_left"]/div/following-sibling::text()',
        'description': '//div[contains(@class, "description")]/p//text()',
        'performers': '//div[@class="trailer_toptitle_left"]/a[contains(@href, "models")]/text()',
        'tags': '//div[@class="set_tags"]/ul/li/a/text()',
        'duration': '//div[@class="set_meta"]/i[contains(@class, "play-circle")]/following-sibling::text()[1]',
        're_duration': r'((?:\d{1,2}\:)?\d{2}\:\d{2})',
        'trailer': '',
        'type': 'Scene',
        'external_id': r'',
        're_external_id': r'set-target-(\d+)',
        'pagination': '/tour/categories/movies/%s/latest/',
    }

    def get_scenes(self, response):
        meta = self.copy_meta(response)
        scenes = response.xpath('//div[@class="sexyvideo"]')
        for scene in scenes:
            scenedate = scene.xpath('.//i[contains(@class, "calendar")]/following-sibling::text()')
            if scenedate:
                meta['date'] = self.parse_date(scenedate.get().strip()).strftime('%Y-%m-%d')
            else:
                meta['date'] = None

            sceneurl = scene.xpath('.//h4/a/@href').get()
            sceneurl = "https:" + sceneurl if sceneurl.startswith("//") else sceneurl
            sceneurl = self.format_link(response, sceneurl)

            image = scene.xpath('.//img/@src0')
            if image:
                image = image.get()
                meta['image'] = self.format_link(response, image)
                sceneid = re.search(r'(\d+)\.jpg', image)
                if sceneid:
                    meta['id'] = sceneid.group(1)
                else:
                    meta['id'] = re.search(r'.*/(.*?)\.', sceneurl).group(1).lower()

            if meta['id'] and self.check_item(meta, self.days):
                yield scrapy.Request(sceneurl, callback=self.parse_scene, meta=meta)

    def get_id(self, response):
        image = super().get_image(response)
        sceneid = re.search(r'.*/(\d+)', image).group(1)
        return sceneid

    def get_tags(self, response):
        tags = super().get_tags(response)
        tags.append("Virtual Reality")
        return tags
