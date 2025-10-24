import re
import json
import scrapy
import string
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteCzechCastingSpider(BaseSceneScraper):
    name = 'CzechCasting'
    network = 'CzechCasting'
    parent = 'CzechCasting'
    site = 'CzechCasting'

    start_urls = [
        'https://czechcasting.com',
    ]

    selector_map = {
        'performers': '',
        'external_id': r'.*/(.*?)/',
        'pagination': '/pages/page-%s/',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//a[contains(@href, "/video/") and h3]/ancestor::div[contains(@class, "model-item")]')
        for scene in scenes:
            perf_image = scene.xpath('.//div[contains(@class, "media-wrapper")]/following-sibling::img/@src')
            if perf_image:
                meta['perf_image'] = perf_image.get()
                scene = scene.xpath('./div[1]/a/@href').get()
                if re.search(self.get_selector_map('external_id'), scene):
                    yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def parse_scene(self, response):
        meta = response.meta
        scenedata = response.xpath('//script[contains(@type, "ld+json")]/text()').get()
        scene = json.loads(scenedata)
        item = self.init_scene()

        item['title'] = string.capwords(self.cleanup_title(scene['name']))

        if "description" in scene and scene['description']:
            item['description'] = self.cleanup_description(scene['description'])

        item['date'] = re.search(r'(\d{4}-\d{2}-\d{2})', scene['uploadDate']).group(1)

        image = scene['thumbnailUrl']
        item['image'] = re.search(r'(.*?)\?', image).group(1)
        item['image_blob'] = self.get_image_blob_from_link(image)

        item['duration'] = self.duration_to_seconds(scene['duration'])

        if "keywords" in scene and scene['keywords']:
            for keyword in scene['keywords'].split(","):
                if not re.search(r'(\d{3,})', keyword) and "czech" not in keyword.lower():
                    item['tags'].append(string.capwords(keyword).strip())

        performer = re.search(r'casting-(.*?)-(\d+)/', response.url)
        if performer:
            perf_name = performer.group(1)
            perf_name = re.sub(r'[^a-zA-Z0-9 ]+', ' ', perf_name).strip()
            perf_id = performer.group(2)

            if " " not in perf_name:
                performer_name = string.capwords(perf_name) + " " + perf_id
            else:
                performer_name = string.capwords(perf_name)
            item['performers'].append(performer_name)
            perf = {}
            perf['name'] = performer_name
            perf['extra'] = {}
            perf['extra']['gender'] = "Female"
            perf['image'] = meta['perf_image']
            perf['image'] = re.search(r'(.*?)\?', meta['perf_image']).group(1)

            perf['image_blob'] = self.get_image_blob_from_link(meta['perf_image'])
            perf['site'] = "Czech Casting"
            perf['network'] = "Czech Casting"
            item['performers_data'] = [perf]

        item['site'] = "Czech Casting"
        item['parent'] = "Czech Casting"
        item['network'] = "Czech Casting"

        item['url'] = response.url
        item['id'] = re.search(r'.*/(.*?)/', response.url).group(1)

        yield self.check_item(item, self.days)
