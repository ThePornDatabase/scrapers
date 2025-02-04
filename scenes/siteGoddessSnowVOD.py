import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteGoddessSnowVODSpider(BaseSceneScraper):
    name = 'GoddessSnowVOD'
    site = 'Goddess Snow VOD'
    parent = 'Goddess Snow VOD'
    network = 'Goddess Snow'

    start_urls = [
        'https://goddesssnow.com'
    ]

    selector_map = {
        'title': '//div[@class="title_bar"]/span/text()',
        'description': '//span[@class="update_description"]/text()',
        'performers': '//span[@class="update_models"]/a/text()',
        'tags': '//span[@class="update_tags"]/a/text()',
        'trailer': '',
        'type': 'Scene',
        'external_id': r'',
        'pagination': '/vod/updates/page_%s.html',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="update_details"]')
        for scene in scenes:
            meta['id'] = scene.xpath('./@data-setid').get()
            image = scene.xpath('.//img/@src0_2x')
            if image:
                image = image.get()
                image = image.replace("-2x", "-full")
                image = self.format_link(response, image)
                meta['image'] = image
                meta['image_blob'] = self.get_image_blob_from_link(image)

            scenedate = scene.xpath('.//span[@class="date"]/text()')
            if scenedate:
                scenedate = scenedate.get()
                meta['date'] = self.parse_date(scenedate, date_formats=['%m/%d/%Y']).strftime('%Y-%m-%d')

            duration = scene.xpath('.//span[@class="duration"]/text()')
            if duration:
                duration = duration.get()
                duration = duration.replace("\r", "").replace("\n", "").replace("\t", "").replace("&nbsp;", "").replace(" ", "")
                duration = re.search(r'(\d+)min', duration)
                if duration:
                    meta['duration'] = str(int(duration.group(1)) * 60)

            scene = scene.xpath('.//a[contains(@class, "details-image")]/@href').get()

            if meta['id']:
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_performers(self, response):
        performers = super().get_performers(response)
        if not performers:
            performers = []
        if "Alexandra Snow" not in performers:
            performers.append("Alexandra Snow")
        return performers
