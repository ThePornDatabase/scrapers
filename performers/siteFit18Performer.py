import json
import re
from scrapy.http import Request
from tpdb.items import PerformerItem
from tpdb.BasePerformerScraper import BasePerformerScraper


class SiteFit18PerformerSpider(BasePerformerScraper):
    name = 'Fit18Performer'

    headers = {
        "Content-Type": "application/json",
        "apollographql-client-name": "fit18:site",
        "apollographql-client-version": "1.0",
        "argonath-api-key": "77cd9282-9d81-4ba8-8868-ca9125c76991",
    }

    def start_requests(self):

        scenequery = {
            "operationName": "ListTalent",
            "variables": {
                "after": "",
                "limit": 500
            },
            "query": "query ListTalent($order: [OrderEntry!], $after: ID, $limit: Int) {\n  talent {\n    list(input: {order: $order, after: $after, first: $limit}) {\n      result {\n        edges {\n          node {\n            talentId\n            name\n        dimensions {\n          height\n          weight\n          measurements {\n            cup\n            waist\n            hips\n          }\n        }\n          }\n        }\n      }\n    }\n  }\n}\n"
        }
        url = "https://fit18.team18.app/graphql"
        scenequery = json.dumps(scenequery)
        # ~ print(data2)
        yield Request(url, headers=self.headers, body=scenequery, method="POST", callback=self.get_performers)

    selector_map = {
        'external_id': r'',
        'pagination': ''
    }

    def get_performers(self, response):
        meta = response.meta
        jsondata = response.json()['data']['talent']['list']['result']['edges']
        for jsonrow in jsondata:
            item = PerformerItem()
            item['name'] = jsonrow['node']['name']
            item['height'] = str(jsonrow['node']['dimensions']['height']) + "cm"
            item['weight'] = str(jsonrow['node']['dimensions']['weight']) + "kg"
            if jsonrow['node']['dimensions']['measurements']['cup']:
                cup = jsonrow['node']['dimensions']['measurements']['cup']
                cupvalue = re.search(r'(\d{2,3})', cup).group(1)
                cupsize = re.search(r'([A-Za-z]+)', cup).group(1)
                item['cupsize'] = str(round(int(cupvalue) / 2.54)) + cupsize

            if jsonrow['node']['dimensions']['measurements']['waist'] and jsonrow['node']['dimensions']['measurements']['hips']:
                waist = str(round(int(jsonrow['node']['dimensions']['measurements']['waist']) / 2.54))
                hips = str(round(int(jsonrow['node']['dimensions']['measurements']['hips']) / 2.54))
                item['measurements'] = item['cupsize'] + "-" + waist + "-" + hips
            item['network'] = "Fit 18"
            item['url'] = "https://fit18.com/models/" + jsonrow['node']['talentId']
            item['gender'] = 'Female'
            item['bio'] = ''
            item['birthday'] = ''
            item['astrology'] = ''
            item['birthplace'] = ''
            item['ethnicity'] = ''
            item['nationality'] = ''
            item['haircolor'] = ''
            item['tattoos'] = ''
            item['piercings'] = ''
            item['fakeboobs'] = ''
            item['eyecolor'] = ''
            meta['item'] = item.copy()

            imagequery = {
                "operationName": "BatchFindAssetQuery",
                "variables": {
                    "paths": [
                        "/members/models/" + jsonrow['node']['talentId'] + "/profile-sm.jpg"
                    ]
                },
                "query": "query BatchFindAssetQuery($paths: [String!]!) {\n  asset {\n    batch(input: {paths: $paths}) {\n      result {\nserve {\n uri\n}\n}\n}\n}\n}\n"}
            url = "https://fit18.team18.app/graphql"
            imagequery = json.dumps(imagequery)
            yield Request(url, headers=self.headers, body=imagequery, method="POST", callback=self.get_images, meta=meta)

    def get_images(self, response):
        meta = response.meta
        item = meta['item']
        jsondata = response.json()['data']['asset']['batch']['result'][0]['serve']
        item['image'] = jsondata['uri']
        item['image_blob'] = None
        if item['name']:
            yield item
