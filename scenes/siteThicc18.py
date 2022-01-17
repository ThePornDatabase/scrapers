import json
from scrapy.http import Request
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteThicc18Spider(BaseSceneScraper):
    name = 'Thicc18'

    headers = {
        "Content-Type": "application/json",
        "apollographql-client-name": "thicc18:site",
        "apollographql-client-version": "1.0",
        "argonath-api-key": "77cd9282-9d81-4ba8-8868-ca9125c76991",
    }

    def start_requests(self):

        scenequery = {
            "operationName": "ListVideo",
            "variables": {
                "after": "",
                "limit": 15
            },
            "query": "query ListVideo($order: [OrderEntry!], $after: ID, $limit: Int) {\n  video {\n    list(input: {order: $order, after: $after, first: $limit}) {\n      result {\n        edges {\n          node {\n            videoId\n            title\n            description {\n              long\n            }\n            talent {\n              type\n              talent {\n                talentId\n                name\n              }\n            }\n          }\n        }\n      }\n    }\n  }\n}\n"
        }
        url = "https://thicc18.team18.app/graphql"
        scenequery = json.dumps(scenequery)
        yield Request(url, headers=self.headers, body=scenequery, method="POST", callback=self.get_scenes)

    selector_map = {
        'title': '',
        'description': '',
        'date': '',
        'image': '',
        'performers': '',
        'tags': '',
        'external_id': r'',
        'trailer': '',
        'pagination': ''
    }

    def get_scenes(self, response):
        meta = response.meta
        jsondata = response.json()['data']['video']['list']['result']['edges']
        for jsonrow in jsondata:
            item = SceneItem()
            sceneid = jsonrow['node']['videoId']
            item['id'] = sceneid.replace(":", "-")
            item['title'] = self.cleanup_title(jsonrow['node']['title'])
            item['description'] = self.cleanup_description(jsonrow['node']['description']['long'])
            item['performers'] = []
            for performer in jsonrow['node']['talent']:
                item['performers'].append(performer['talent']['name'])

            item['site'] = "Thicc 18"
            item['network'] = "Thicc 18"
            item['parent'] = "Thicc 18"
            item['url'] = "https://thicc18.com/videos/" + sceneid.replace(':', '%3A')
            item['date'] = self.parse_date('today').isoformat()
            item['trailer'] = ''
            item['tags'] = ['Big Ass']
            meta['item'] = item.copy()
            imagedata = jsonrow['node']['videoId'].split(":")

            imagequery = {
                "operationName": "BatchFindAssetQuery",
                "variables": {
                    "paths": [
                        "/members/models/" + imagedata[0] + "/scenes/" + imagedata[1] + "/videothumb.jpg",
                    ]
                },
                "query": "query BatchFindAssetQuery($paths: [String!]!) {\n  asset {\n    batch(input: {paths: $paths}) {\n      result {\nserve {\n uri\n}\n}\n}\n}\n}\n"}
            url = "https://thicc18.team18.app/graphql"
            imagequery = json.dumps(imagequery)
            yield Request(url, headers=self.headers, body=imagequery, method="POST", callback=self.get_images, meta=meta)

    def get_images(self, response):
        meta = response.meta
        item = meta['item']
        jsondata = response.json()['data']['asset']['batch']['result'][0]['serve']
        item['image'] = jsondata['uri']
        item['image_blob'] = None
        if item['id'] and item['title']:
            yield item
