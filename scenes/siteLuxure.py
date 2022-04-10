import re
import string
import html
import json
import unidecode
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteLuxureSpider(BaseSceneScraper):
    name = 'Luxure'
    network = 'Dorcel Club'
    parent = 'Luxure'
    site = 'Luxure'

    start_urls = [
        'https://api.luxure.com',
    ]

    headers = {
        'token': 'mysexmobile',
        'siteId': '103',
    }

    selector_map = {
        'title': '',
        'description': '',
        'date': '',
        'image': '',
        'performers': '',
        'tags': '',
        'trailer': '',
        'external_id': r'',
        'pagination': '/24api/v1/sites/103/freetour/videos?is_mobile=false&take=12&page=%s'
    }

    def get_scenes(self, response):
        meta = response.meta
        jsondata = json.loads(response.text)
        jsondata = jsondata['payload']['scenes']
        for scene in jsondata:
            if isinstance(scene, dict):
                meta['id'] = str(scene['id'])
            else:
                meta['id'] = str(jsondata[scene]['id'])
            url = f"https://api.luxure.com/24api/v1/sites/103/freetour/videos/{meta['id']}"
            yield scrapy.Request(url, callback=self.parse_scene, headers=self.headers, cookies=self.cookies, meta=meta)

    def parse_scene(self, response):
        item = SceneItem()
        sceneid = re.search(r'payload.*?scenes.*?(\d+)', response.text).group(1)
        jsondata = json.loads(response.text)
        scene = jsondata['payload']['scenes'][sceneid]
        if "translations" in scene:
            for lang in scene['translations']:
                if lang['language_id'] == 1:
                    item['id'] = str(lang['scene_id'])
                    item['title'] = unidecode.unidecode(string.capwords(lang['title']).strip())
                    item['description'] = unidecode.unidecode(html.unescape(re.sub('<[^<]+?>', '', lang['story'])).strip())
                    item['date'] = lang['scene']['original_publication_date']

        if 'id' not in item or not item['id']:
            item['id'] = str(scene['id'])
            item['title'] = unidecode.unidecode(string.capwords(scene['title']).strip())
            item['description'] = ''
            item['date'] = self.parse_date('today').isoformat()

        item['image'] = scene['video_cover']['original']
        item['image_blob'] = self.get_image_blob_from_link(item['image'])
        item['trailer'] = None
        item['site'] = 'Luxure'
        item['parent'] = 'Luxure'
        item['network'] = 'Dorcel Club'

        item['performers'] = []
        for performer in scene['models']:
            item['performers'].append(unidecode.unidecode(scene['models'][performer]['stage_name']))

        item['tags'] = []
        for tag in scene['mainScenetags']:
            for lang in scene['mainScenetags'][tag]['translations']:
                if lang['language'] == 'en':
                    item['tags'].append(string.capwords(lang['name']))
        item['url'] = "https://luxure.com" + scene['hreflang']['en']

        yield item
