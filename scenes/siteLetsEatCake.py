import re
from cleantext import clean
import string
from slugify import slugify
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteLetsEatCakeSpider(BaseSceneScraper):
    name = 'LetsEatCake'

    start_urls = [
        'https://letseatcakexx.mymember.site',
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '/api/videos?count=20&page=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        jsondata = response.json()
        jsondata = jsondata['data']
        for scene in jsondata:
            meta['id'] = scene['id']
            meta['date'] = re.search(r'(\d{4}-\d{2}-\d{2})', scene['publish_date']).group(1)
            meta['title'] = string.capwords(scene['title'])
            meta['duration'] = str(scene['duration'])
            scene_url = f"https://letseatcakexx.mymember.site/api/videos/{meta['id']}"
            yield scrapy.Request(scene_url, callback=self.parse_scene, meta=meta)

    def parse_scene(self, response):
        meta = response.meta
        item = self.init_scene()
        scene = response.json()

        item['title'] = meta['title']
        item['date'] = meta['date']
        item['id'] = meta['id']
        item['duration'] = meta['duration']

        description = clean(scene['description'].replace("\n", "").strip(), no_emoji=True)
        item['description'] = self.cleanup_description(description)


        if "poster_src" in scene and scene['poster_src']:
            item['image'] = scene['poster_src']
            if 'image' not in item or not item['image']:
                item['image'] = None
                item['image_blob'] = None
            else:
                item['image_blob'] = self.get_image_blob_from_link(item['image'])

            if 'image_blob' not in item:
                item['image'] = None
                item['image_blob'] = None

            if item['image']:
                if "?" in item['image']:
                    item['image'] = re.search(r'(.*?)\?', item['image']).group(1)

        item['tags'] = []
        if "tags" in scene and scene['tags']:
            for tag in scene['tags']:
                item['tags'].append(tag['name'])

        if "casts" in scene and scene['casts']:
            item['performers'] = []
            for cast in scene['casts']:
                item['performers'].append(cast['screen_name'])

            item['performers_data'] = self.get_performers_data(item['performers'])

        item['url'] = f"https://letseatcakexx.com/videos/{item['id']}-{slugify(item['title'])}"

        item['site'] = "Lets Eat Cake"
        item['parent'] = "Lets Eat Cake"
        item['network'] = "Lets Eat Cake"

        item['type'] = 'Scene'

        yield self.check_item(item, self.days)

    def get_performers_data(self, response):
        performers = self.get_performers(response)
        performers_data = []
        if len(performers):
            for performer in performers:
                perf = {}
                perf['name'] = performer
                perf['extra'] = {}
                perf['extra']['gender'] = "Male"
                perf['network'] = "Lets Eat Cake"
                perf['site'] = "Lets Eat Cake"
                performers_data.append(perf)
        return performers_data
