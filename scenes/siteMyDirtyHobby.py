import re
import string
import html
from slugify import slugify
import unidecode
import json
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteMyDirtyHobbySpider(BaseSceneScraper):
    name = 'MyDirtyHobby'
    network = 'MyDirtyHobby'
    parent = 'MyDirtyHobby'
    site = 'MyDirtyHobby'

    start_urls = [
        'https://www.mydirtyhobby.com',
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '/content/api/videos',
        'type': 'Scene',
    }

    def start_requests(self):
        meta = {}
        link = "https://www.mydirtyhobby.com/"
        yield scrapy.Request(link, callback=self.start_requests_2, meta=meta, headers=self.headers, cookies=self.cookies)

    def start_requests_2(self, response):
        meta = response.meta
        meta['link'] = "https://www.mydirtyhobby.com/content/api/videos"
        meta['page'] = self.page
        json_data = {"country": "no", "user_language": "en", "listing": "latest_video", "pageSize": 40, "page": meta['page']}
        yield scrapy.Request(meta['link'], method='POST', body=json.dumps(json_data), callback=self.parse, headers={'Content-Type': 'application/json'}, cookies=self.cookies, meta=meta)

    def parse(self, response, **kwargs):
        meta = response.meta
        scenes = self.get_scenes(response)
        count = 0
        for scene in scenes:
            count += 1
            yield scene

        print(f"Count: {count}")
        print(f"Page: {meta['page']}")
        if count:
            if meta['page'] < self.limit_pages:
                meta['page'] = meta['page'] + 1
                print('NEXT PAGE: ' + str(meta['page']))
                json_data = {"country": "no", "user_language": "en", "listing": "latest_video", "pageSize": 40, "page": meta['page']}
                yield scrapy.Request(meta['link'], method='POST', body=json.dumps(json_data), callback=self.parse, headers={'Content-Type': 'application/json'}, cookies=self.cookies, meta=meta)

    def get_scenes(self, response):
        jsondata = json.loads(response.text)
        for scene in jsondata['items']:
            item = SceneItem()

            item['title'] = unidecode.unidecode(html.unescape(string.capwords(scene['title']).strip()))
            item['description'] = unidecode.unidecode(html.unescape(string.capwords(scene['description']).strip()))
            item['performers'] = [scene['nick']]
            item['id'] = scene['uv_id']
            scenedate = scene['onlineAtFormat'].replace("\\/", "/")
            item['date'] = self.parse_date(scenedate, date_formats=['%m/%d/%Y']).strftime('%Y-%m-%d')
            item['url'] = f"https://www.mydirtyhobby.com/profil/{scene['u_id']}-{scene['nick']}/videos/{scene['uv_id']}-{slugify(scene['title'])}"
            item['site'] = "MyDirtyHobby"
            item['parent'] = "MyDirtyHobby"
            item['network'] = "MyDirtyHobby"
            item['trailer'] = ''
            item['duration'] = self.duration_to_seconds(scene['duration'])
            item['image'] = scene['thumbnail'].replace("\\/", "/")
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            item['image'] = re.search(r'(.*?)\?', item['image']).group(1)
            item['tags'] = []

            yield self.check_item(item, self.days)
