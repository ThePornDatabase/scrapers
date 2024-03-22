import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class NetworkCombatZoneSpider(BaseSceneScraper):
    name = 'CombatZone'
    network = 'Combat Zone'

    start_urls = [
        'https://tour.blackmarketxxx.com',
        'https://tour.fillyfilms.com',
        'https://tour.smashpictures.com',
        'https://tour.combatzonexxx.com',
    ]

    selector_map = {
        'title': '',
        'description': '//div[@class="description"]/p/text()',
        'date': '//div[@class="info"]/p[1]//text()[contains(., "Added")]',
        're_date': r'(\w+ \d{1,2}, \d{4})',
        'image': '//img[contains(@id, "set-target")]/@src0_3x|//img[contains(@id, "set-target")]/@src0_2x|//img[contains(@id, "set-target")]/@src0_1x',
        'performers': '//div[@class="info"]/p[1]//a[contains(@href, "/models/")]/text()',
        'tags': '//ul[@class="tags"]/li/a/text()',
        'duration': '//div[@class="info"]/p[1]//text()[contains(., "Runtime")]',
        're_duration': r'((?:\d{1,2}\:)?\d{2}\:\d{2})',
        'trailer': '',
        'external_id': r'',
        'pagination': '/categories/movies_%s_d.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class,"item-video")]')
        for scene in scenes:
            meta['title'] = self.cleanup_title(scene.xpath('./div[1]/a/span/text()').get())
            duration = scene.xpath('.//div[@class="timeDate"]/text()[1]').get()
            duration = re.search(r'((?:\d{1,2}\:)?\d{2}\:\d{2})', duration)
            if duration:
                meta['duration'] = self.duration_to_seconds(duration.group(1))

            scenedate = scene.xpath('.//div[@class="timeDate"]//text()').getall()
            scenedate = "".join(scenedate).replace(" ", "")
            scenedate = re.search(r'(\d{4}-\d{2}-\d{2})', scenedate)
            if scenedate:
                meta['date'] = scenedate.group(1)

            meta['performers'] = scene.xpath('.//a[contains(@href, "/models/")]/text()').getall()

            image = scene.xpath('.//img[contains(@id, "set-target")]/@src0_3x|.//img[contains(@id, "set-target")]/@src0_2x|.//img[contains(@id, "set-target")]/@src0_1x')
            if image:
                meta['image'] = self.format_link(response, image.get())
                meta['image_blob'] = self.get_image_blob_from_link(meta['image'])

            scene = scene.xpath('.//div[@class="item-thumb"]/a/@href').get()
            scene = self.format_link(response, scene)

            sceneid = re.search(r'/(trailers/.*?)\.htm', scene).group(1)
            meta['id'] = sceneid.lower().replace("/", "-")

            if "fillyfilms" in scene:
                meta['site'] = "Filly Films"
            elif "blackmarketxxx" in scene:
                meta['site'] = "Black Market"
            elif "combatzonexxx" in scene:
                meta['site'] = "Combat Zone"
            elif "smashpictures" in scene:
                meta['site'] = "Smash Pictures"

            meta['parent'] = meta['site']

            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(scene, callback=self.parse_scene, meta=meta)
