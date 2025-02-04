import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
true = True
false = False

class SiteCollectiveCorruptionSpider(BaseSceneScraper):
    name = 'CollectiveCorruption'
    site = 'Collective Corruption'
    parent = 'Collective Corruption'
    network = 'Collective Corruption'

    start_urls = [
        'https://collectivecorruption.com'
    ]

    cookies = []

    selector_map = {
        'title': '//span[@class="update_title"]/text()',
        'image': '//div[@class="update_image"]/a/img/@src0_1x',
        'performers': '//span[@class="tour_update_models"]/a/text()',
        'tags': '//span[@class="update_tags"]/a/text()',
        'duration': '',
        'trailer': '//div[@class="update_image"]/a/@onclick',
        're_trailer': r'(/.*)[\'\"]',
        'type': 'Scene',
        'external_id': r'',
        'pagination': '/categories/movies_%s_d.html',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class,"updateItem")]')
        for scene in scenes:
            scenedate = scene.xpath('.//div[contains(@class, "updateDetails")]/p/span/text()')
            if scenedate:
                scenedate = scenedate.get()
                meta['date'] = self.parse_date(scenedate, date_formats=['%m/%d/%Y']).strftime('%Y-%m-%d')
            sceneid = scene.xpath('.//img/@id').get()
            meta['id'] = re.search(r'-(\d+)', sceneid).group(1)

            scene = scene.xpath('./div[1]/a/@href').get()

            if meta['id']:
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_duration(self, response):
        duration = response.xpath('//div[contains(text(), "of video")]/text()')
        if duration:
            duration = duration.get()
            duration = duration.replace("&nbsp;", "").replace(" ", "").strip().lower()
            duration = re.search(r'(\d+)ofvideo', duration)
            if duration:
                duration = duration.group(1)
                return str(int(duration) * 60)
        return None

    def get_image(self, response):
        image = super().get_image(response)
        return image.replace("-1x", "-full")
