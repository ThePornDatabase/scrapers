import json

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

    per_page = 10

    def start_requests(self):
        yield scrapy.Request(
            url='https://www.bang.com/api/search/videos/video/_search',
            method='POST',
            headers={'Content-Type': 'application/json'},
            meta={'page': 0},
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
                        self.per_page,
                        self.per_page *
                        next_page))
            )

    def parse_scene(self, json):
        item = SceneItem()
        item['id'] = json['_id']

        json = json['_source']

        if 'preview' in json:
            item['trailer'] = 'https://i.bang.com/v/%s/%s/preview720.mp4' % (
                json['dvd']['id'], json['identifier'])
        else:
            item['trailer'] = ''

        item['site'] = json['studio']['name'].title()
        if item['site'].lower().strip() == 'bang! originals':
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
        item['url'] = 'https://bang.com/video/%s' % item['id']
        item['network'] = 'Bang'
        item['parent'] = 'Bang'

        return item

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
