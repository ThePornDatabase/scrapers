import json
import requests
import base64
from datetime import date, timedelta
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class BangSpider(BaseSceneScraper):
    name = 'Bang'
    network = 'Bang'
    parent = 'Bang'

    selector_map = {
        'external_id': 'video/(.+)'
    }

    per_page = 50

    def start_requests(self):
        if self.page:
            page = int(self.page)
        else:
            page = 0

        yield scrapy.Request(
            url='https://www.bang.com/api/search/videos/video/_search',
            method='POST',
            headers={'Content-Type': 'application/json'},
            meta={'page': page},
            callback=self.parse,
            body=json.dumps(self.get_elastic_payload(self.per_page, 0))
        )

    def parse(self, response, **kwargs):
        scenes = response.json()['hits']['hits']
        for scene in scenes:
            yield self.parse_scene(scene)

        if 'page' in response.meta and response.meta['page'] < self.limit_pages:
            next_page = response.meta['page'] + 1
            if (next_page * self.per_page) > response.json()['hits']['total']:
                return

            print('NEXT PAGE: ' + str(next_page))
            yield scrapy.Request(
                url='https://www.bang.com/api/search/videos/video/_search',
                method='POST',
                headers={'Content-Type': 'application/json'},
                callback=self.parse,
                meta={'page': next_page},
                body=json.dumps(
                    self.get_elastic_payload(
                        self.per_page, self.per_page * next_page))
            )

    def parse_scene(self, json):
        item = SceneItem()
        item['id'] = json['_id']

        json = json['_source']
        # ~ print ("   ")
        # ~ print(f'JSON: {json}')

        if 'preview' in json:
            item['trailer'] = 'https://i.bang.com/v/%s/%s/preview720.mp4' % (
                json['dvd']['id'], json['identifier'])
        else:
            item['trailer'] = ''

        item['site'] = json['studio']['name'].title()
        if item['site'].lower().strip() == 'bang! originals' or item['site'].lower().strip() == 'bang originals':
            item['site'] = json['series']['name'].title()

        item['title'] = json['name']
        item['description'] = json['description']
        item['date'] = json['releaseDate']
        item['tags'] = list(map(lambda x: x['name'].title(), json['genres']))
        item['performers'] = list(map(lambda x: x['name'], json['actors']))
        try:
            item['image'] = 'https://i.bang.com/screenshots/%s/movie/%s/%s.jpg' % (
                json['dvd']['id'], json['order'], json['screenshots'][0]['screenId'])
        except BaseException:
            print(f"Index out of Range: {item['id']}")
            item['image'] = None
        item['image_blob'] = None
        if item['image']:
            imagereq = requests.get(item['image'])
            item['image_blob'] = base64.b64encode(imagereq.content).decode('utf-8')
            if len(item['image_blob']) < 500:
                item['image_blob'] = None
        item['url'] = 'https://bang.com/video/%s' % item['id']
        item['network'] = 'Bang'
        item['parent'] = 'Bang'

        if item['title']:
            days = int(self.days)
            if days > 27375:
                filterdate = "0000-00-00"
            else:
                filterdate = date.today() - timedelta(days)
                filterdate = filterdate.strftime('%Y-%m-%d')

            if self.debug:
                if not item['date'] > filterdate:
                    item['filtered'] = "Scene filtered due to date restraint"
                print(item)
            else:
                if filterdate:
                    if item['date'] > filterdate:
                        return item
                else:
                    return item
            return None

    def get_elastic_payload(self, per_page, offset: int = 0):
        return {
            'size': per_page,
            'from': offset,
            'sort': [
                {
                    'releaseDate': {
                        'order': 'desc'
                    }
                }
            ],
            'query': {
                'bool': {
                    'must': [
                        {
                            'match': {
                                'status': 'ok'
                            }
                        },
                        {
                            'range': {
                                'releaseDate': {
                                    'lte': 'now'
                                }
                            }
                        }
                    ],
                    'must_not': [
                        {
                            'match': {
                                'type': 'trailer'
                            }
                        }
                    ]
                }
            }
        }
