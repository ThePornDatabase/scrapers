import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteMonsterCubSpider(BaseSceneScraper):
    name = 'MonsterCub'

    start_urls = [
        'https://www.monstercub.com',
    ]

    cookies = [{
                    "name": "showWarning",
                    "value": "enter"
                }, {
                    "name": "SceneSort",
                    "value": "published-newer"
                }
            ]

    selector_map = {
        'title': '//h2[contains(@class, "sectionMainTitle")]/text()',
        'description': '//div[@class="p-5"]/p/text()',
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//span[@class="perfImage"]/a/text()',
        'tags': '//h5[contains(text(), "Categories")]/a/text()',
        'external_id': r'scene/(\d+)-',
        'pagination': '/scenes?page=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "scene_container")]/figure')
        for scene in scenes:
            scenedate = scene.xpath('./..//span[contains(@class, "dateLbl")]/text()')
            if scenedate:
                meta['date'] = self.parse_date(scenedate.get(), date_formats=['%b %d, %Y']).strftime('%Y-%m-%d')

            duration = scene.xpath('./..//i[contains(@class, "icon-clock")]/following-sibling::text()')
            if duration:
                duration = duration.get()
                duration = re.sub(r'[^a-z0-9]+', '', duration.lower())
                duration = re.search(r'(\d+)min', duration)
                if duration:
                    meta['duration'] = str(int(duration.group(1)) * 60)


            scene = scene.xpath('./a[1]/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_performers_data(self, response):
        performers = response.xpath('//span[@class="perfImage"]')
        performers_data = []
        if len(performers):
            for performer in performers:
                perf = {}
                perf['name'] = performer.xpath('./a/text()').get()
                perf['extra'] = {}
                perf['extra']['gender'] = "Male"
                perf['network'] = self.get_network(response)
                perf['site'] = self.get_network(response)
                image = performer.xpath('./a/img/@src')
                if image:
                    image = self.format_link(response, image.get())
                    perf['image'] = image
                    perf['image_blob'] = self.get_image_blob_from_link(image)

                performers_data.append(perf)
        return performers_data
