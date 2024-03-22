import re
import json
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteKingNoireXXXSpider(BaseSceneScraper):
    name = 'KingNoireXXX'
    site = 'KingNoireXXX'
    parent = 'KingNoireXXX'
    network = 'KingNoireXXX'

    start_urls = [
        'https://kingnoirexxx.mymember.site',
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '/api/videos?count=20&page=%s',
    }

    def get_scenes(self, response):
        meta = response.meta
        jsondata = json.loads(response.text)
        jsondata = jsondata['data']

        for scene in jsondata:
            link = f"https://kingnoirexxx.mymember.site/api/videos/{str(scene['id'])}"
            yield scrapy.Request(link, callback=self.parse_scene, meta=meta)

    def parse_scene(self, response):
        scene = json.loads(response.text)
        item = SceneItem()

        item['id'] = scene['id']
        item['duration'] = scene['duration']
        item['title'] = scene['title']
        if "{" in item['title'] and "}" in item['title']:
            item['title'] = re.sub(r'{.*?}', "", item['title']).strip()

        if "description" in scene and scene['description']:
            item['description'] = scene['description']
        else:
            item['description'] = ""

        item['date'] = re.search(r'(\d{4}-\d{2}-\d{2})', scene['publish_date']).group(1)

        item['performers'] = []
        for performer in scene['casts']:
            item['performers'].append(performer['screen_name'])

        item['tags'] = []
        for tag in scene['tags']:
            item['tags'].append(tag['name'])

        item['image'] = scene['poster_src']
        if item['image']:
            item['image_blob'] = self.get_image_blob_from_link(item['image'])

        item['trailer'] = ""

        item['type'] = "Scene"
        item['site'] = "KingNoireXXX"
        item['parent'] = "KingNoireXXX"
        item['network'] = "KingNoireXXX"

        item['url'] = f"https://kingnoirexxx.com/videos/{item['id']}"

        if item['id'] and item['title']:
            yield self.check_item(item, self.days)
