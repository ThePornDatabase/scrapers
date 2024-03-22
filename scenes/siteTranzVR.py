import re
import scrapy
import json
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteTranzVRSpider(BaseSceneScraper):
    name = 'TranzVR'
    network = 'TranzVR'
    parent = 'TranzVR'
    site = 'TranzVR'

    start_urls = [
        'https://www.tranzvr.com',
    ]

    selector_map = {
        'title': '',
        'description': '',
        'date': '',
        'image': '',
        'performers': '',
        'tags': '//div[@class="tag-list__body"]//a/text()',
        'duration': '',
        'trailer': '',
        'external_id': r'.*-(\d+)$',
        'pagination': '/?o=d&p=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//li[contains(@class,"cards-list__item")]/div/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def parse_scene(self, response):
        scene = response.xpath('//script[contains(@type, "ld+json")]/text()').get()
        scene = json.loads(scene)
        item = SceneItem()

        item['title'] = self.cleanup_title(scene['name'])
        item['id'] = re.search(r'.*-(\d+)$', response.url).group(1)

        item['description'] = self.cleanup_description(scene['description'])

        images = response.xpath('//div[contains(@class, "detail__video")]//picture//img/@srcset')
        item['image'] = ''
        item['image_blob'] = ''

        if images:
            images = images.get()
            images = images.split(",")
            images = images[-1]
            if images and " " in images:
                item['image'] = re.search(r'(.*) ', images).group(1)
                item['image_blob'] = self.get_image_blob_from_link(item['image'])

        if not item['image']:
            if 'thumbnailUrl' in scene and scene['thumbnailUrl']:
                item['image'] = scene['thumbnailUrl']
                item['image_blob'] = self.get_image_blob_from_link(item['image'])

        if scene['contentUrl']:
            item['trailer'] = self.format_link(response, scene['contentUrl']).replace(" ", "%20")
        else:
            item['trailer'] = ""

        scene_date = self.parse_date(scene['uploadDate'], date_formats=['%Y-%m-%d']).strftime('%Y-%m-%d')
        item['date'] = ""
        if scene_date:
            item['date'] = scene_date

        item['url'] = scene['embedUrl']
        if "?" in item['url']:
            item['url'] = re.search(r'(.*)\?', item['url']).group(1)

        item['tags'] = self.get_tags(response)

        item['duration'] = self.duration_to_seconds(scene['duration'])

        item['site'] = 'TranzVR'
        item['parent'] = 'TranzVR'
        item['network'] = 'TranzVR'

        item['performers'] = []
        for model in scene['actor']:
            item['performers'].append(model['name'])

        yield self.check_item(item, self.days)
