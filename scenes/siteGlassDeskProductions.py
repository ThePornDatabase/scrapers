import re
import string
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteGlassDeskProductionsSpider(BaseSceneScraper):
    name = 'GlassDeskProductions'
    network = 'GlassDeskProductions'
    parent = 'GlassDeskProductions'
    site = 'GlassDeskProductions'

    start_urls = [
        'https://glassdeskproductions.mymember.site',
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
        'external_id': r'',
        'pagination': '/api/videos?count=20&page=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.json()
        scenes = scenes['data']
        for scene in scenes:
            item = self.init_scene()
            item['id'] = scene['id']
            item['title'] = string.capwords(scene['title'])
            item['date'] = re.search(r'(\d{4}-\d{2}-\d{2})', scene['publish_date']).group(1)
            item['duration'] = str(scene['duration'])
            item['image'] = scene['poster_src']
            # ~ item['image_blob'] = self.get_image_blob_from_link(item['image'])
            item['site'] = "GlassDeskProductions"
            item['parent'] = "GlassDeskProductions"
            item['network'] = "GlassDeskProductions"
            item['url'] = f"https://glassdeskproductions.com/videos/{item['id']}"
            meta['item'] = item.copy()
            yield scrapy.Request(f"https://glassdeskproductions.mymember.site/api/videos/{item['id']}", callback=self.get_scene_details, meta=meta)

    def get_scene_details(self, response):
        meta = response.meta
        item = meta['item']
        scene = response.json()

        if scene['description']:
            item['description'] = scene['description']

        if "tags" in scene and scene['tags']:
            for tag in scene['tags']:
                item['tags'].append(string.capwords(tag['name']))

        if "casts" in scene and scene['casts']:
            for cast in scene['casts']:
                name = cast['screen_name']
                if "(" in name and ")" in name:
                    name = re.search(r'\((.*?)\)', name).group(1)
                if "glassdesk" not in name.lower():
                    item['performers'].append(string.capwords(name))

        yield item
