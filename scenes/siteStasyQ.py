import re
import scrapy
import json
import html
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteStasyQSpider(BaseSceneScraper):
    name = 'StasyQ'
    network = 'StasyQ'
    parent = 'StasyQ'
    site = 'StasyQ'

    start_urls = [
        'https://www.stasyq.com',
    ]

    selector_map = {
        'title': '',
        'description': '',
        'date': '',
        'image': '',
        'performers': '',
        'tags': '',
        'duration': '',
        'trailer': '',
        'external_id': r'.*/(\d+)',
        'pagination': '/releases/%s?sort=recent',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class,"release-preview-card__title")]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def parse_scene(self, response):
        jsondata = response.xpath('//script[contains(text(), "VideoObject")]/text()').get()
        jsondata = jsondata.replace("\n", "").replace("\r", "").replace("\t", "").replace("  ", " ")
        scene = json.loads(jsondata)
        item = SceneItem()
        item['title'] = self.cleanup_title(scene['name'])
        item['description'] = self.cleanup_description(scene['description'])
        item['description'] = html.unescape(item['description'])
        item['date'] = scene['uploadDate']
        item['image'] = scene['thumbnailUrl']
        item['image_blob'] = self.get_image_blob_from_link(item['image'])

        item['performers'] = response.xpath('//div[@class="release-card__model"]//a/text()').getall()
        item['tags'] = ['Erotica']

        item['duration'] = None
        if "duration" in scene and scene['duration']:
            duration = re.search(r'T(\d+)S', scene['duration'])
            if duration:
                item['duration'] = str(int(duration.group(1)) * 60)
        else:
            item['duration'] = None

        item['trailer'] = scene['contentUrl']
        item['id'] = re.search(r'.*/(\d+)', response.url).group(1)
        item['url'] = response.url
        item['site'] = "StasyQ"
        item['parent'] = "StasyQ"
        item['network'] = "StasyQ"
        item['type'] = "Scene"
        yield self.check_item(item, self.days)
