import re
import string
import html
import json
import unidecode
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteDorcelPagesSpider(BaseSceneScraper):
    name = 'DorcelPages'

    start_urls = [
        ['https://api.luxure.com/24api/v1/sites/103/freetour/videos?is_mobile=false&take=12&page=%s', 'Luxure', 'https://luxure.com', 'https://api.luxure.com/24api/v1/sites/103/freetour/videos/%s'],
        ['https://api.russian-institute.com/24api/v1/sites/104/homepage/freetour?is_mobile=false&take=14&page=%s', 'Russian Insitute', 'https://russian-institute.com', 'https://api.russian-institute.com/24api/v1/sites/104/freetour/videos/%s'],
        ['https://api.xxx-vintage.com/24api/v1/sites/105/homepage/freetour?is_mobile=false&take=14&page=%s', 'XXX Vintage', 'https://xxx-vintage.com', 'https://api.xxx-vintage.com/24api/v1/sites/105/freetour/videos/%s'],
        ['https://api.africa-xxx.com/24api/v1/sites/106/homepage/freetour?is_mobile=false&take=14&page=%s', 'Africa XXX', 'https://africa-xxx.com', 'https://api.africa-xxx.com/24api/v1/sites/106/freetour/videos/%s']
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

    def get_next_page_url(self, pagination, page):
        return pagination % page

    def start_requests(self):
        for link in self.start_urls:
            yield scrapy.Request(url=self.get_next_page_url(link[0], self.page),
                                 callback=self.parse,
                                 meta={'page': self.page, 'site': link[1], 'base': link[2], 'pagination': link[0], 'sceneurl': link[3]},
                                 headers=self.headers,
                                 cookies=self.cookies)

    def parse(self, response, **kwargs):
        scenes = self.get_scenes(response)
        count = 0
        for scene in scenes:
            count += 1
            yield scene

        if count:
            if 'page' in response.meta and response.meta['page'] < self.limit_pages:
                meta = response.meta
                meta['page'] = meta['page'] + 1
                print('NEXT PAGE: ' + str(meta['page']))
                yield scrapy.Request(url=self.get_next_page_url(meta['pagination'], meta['page']),
                                     callback=self.parse,
                                     meta=meta,
                                     headers=self.headers,
                                     cookies=self.cookies)

    def get_scenes(self, response):
        meta = response.meta
        jsondata = json.loads(response.text)
        jsondata = jsondata['payload']['scenes']
        for scene in jsondata:
            if isinstance(scene, dict):
                meta['id'] = str(scene['id'])
            else:
                meta['id'] = str(jsondata[scene]['id'])
            url = meta['sceneurl'] % meta['id']
            yield scrapy.Request(url, callback=self.parse_scene, headers=self.headers, cookies=self.cookies, meta=meta)

    def parse_scene(self, response):
        meta = response.meta
        item = SceneItem()
        sceneid = re.search(r'payload.*?scenes.*?(\d+)', response.text).group(1)
        jsondata = json.loads(response.text)
        scene = jsondata['payload']['scenes'][sceneid]
        if "translations" in scene:
            for lang in scene['translations']:
                if lang['language_id'] == 1:
                    item['id'] = str(lang['scene_id'])
                    if lang['title']:
                        item['title'] = unidecode.unidecode(string.capwords(lang['title']).strip())
                    else:
                        item['title'] = unidecode.unidecode(string.capwords(lang['scene']['title']).strip())
                    if lang['story']:
                        item['description'] = unidecode.unidecode(html.unescape(re.sub('<[^<]+?>', '', lang['story'])).strip())
                    else:
                        item['description'] = unidecode.unidecode(html.unescape(re.sub('<[^<]+?>', '', lang['scene']['story'])).strip())
                    item['date'] = lang['scene']['original_publication_date']

        if 'id' not in item or not item['id']:
            item['id'] = str(scene['id'])
            item['title'] = unidecode.unidecode(string.capwords(scene['title']).strip())
            item['description'] = ''
            item['date'] = self.parse_date('today').isoformat()

        if 'original' in scene['video_cover']:
            item['image'] = scene['video_cover']['original']
        else:
            item['image'] = scene['video_cover']['1']

        item['image_blob'] = self.get_image_blob_from_link(item['image'])
        item['trailer'] = None
        item['site'] = meta['site']
        item['parent'] = meta['site']
        item['network'] = 'Dorcel Club'

        item['performers'] = []
        for performer in scene['models']:
            item['performers'].append(unidecode.unidecode(scene['models'][performer]['stage_name']))

        item['tags'] = []
        for tag in scene['mainScenetags']:
            for lang in scene['mainScenetags'][tag]['translations']:
                if lang['language'] == 'en':
                    item['tags'].append(string.capwords(lang['name']))
        item['url'] = meta['base'] + scene['hreflang']['en']

        yield item
