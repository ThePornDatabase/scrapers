import re
import string
import json
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteR51Spider(BaseSceneScraper):
    name = 'R51'
    network = 'Czech Casting'
    parent = 'R51'
    site = 'R51'

    start_urls = [
        'https://r51.com',
    ]

    selector_map = {
        'external_id': r'.*/(.*?)/',
        'pagination': '/pages/page-%s/',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//section[contains(@data-section, "vertical")]//h3/parent::a[1]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def parse_scene(self, response):
        jsondata = response.xpath('//script[contains(text(), "uploadDate")]/text()').get()
        scene = json.loads(jsondata)
        item = self.init_scene()
        item['title'] = self.cleanup_title(scene['name'])
        item['date'] = re.search(r'(\d{4}-\d{2}-\d{2})', scene['uploadDate']).group(1)
        item['description'] = self.cleanup_description(scene['description'])
        item['image'] = re.search(r'(.*?)\?', scene['thumbnailUrl']).group(1)
        item['image_blob'] = self.get_image_blob_from_link(scene['thumbnailUrl'])
        tags = scene['keywords'].split(",")
        tags = list(map(lambda x: string.capwords(x.strip()), tags))
        for tag in tags:
            if "r51" not in tag.lower() and re.sub(r'[^a-z]+', '', tag.lower()):
                item['tags'].append(tag)
        item['duration'] = self.duration_to_seconds(scene['duration'])
        item['url'] = scene['potentialAction']['target']['urlTemplate']
        item['id'] = re.search(r'.*/(.*?)/', item['url']).group(1)
        item['site'] = 'R51'
        item['parent'] = 'R51'
        item['network'] = 'Czech Casting'

        yield self.check_item(item, self.days)
