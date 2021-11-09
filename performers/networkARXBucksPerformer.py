import json
from scrapy.http import Request
from tpdb.items import PerformerItem
from tpdb.BasePerformerScraper import BasePerformerScraper


class NetworkARXBucksPerformerSpider(BasePerformerScraper):
    name = 'ARXBucksPerformer'

    headers = {
        "Content-Type": "application/json"
    }

    def start_requests(self):
        true = True
        null = None
        data = {
            "operationName": "Actors",
            "variables": {
                "first": 5000,
                "after": "",
                "siteId": null,
                "isAvailable": true,
                "orderBy": {"field": "STAGE_NAME", "direction": "ASC"}
            },
            "query": "query Actors($first: Int, $after: String, $siteId: Int, $orderBy: ActorsOrderBy) {\n  actors(first: $first, after: $after, siteId: $siteId, orderBy: $orderBy) {\n    totalCount\n    edges {\n      node {\n        ...actorFields\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment actorFields on Actor {\n  id\n  dob\n  gender\n  hasProfileImage\n  stageName\n  thumbnailUrl\n  metadataTitle\n  metadataDescription\n  __typename\n}\n"
        }
        url = "https://arwest-api-production.herokuapp.com/graphql"
        data2 = json.dumps(data)
        # ~ print(data2)
        yield Request(url, headers=self.headers, body=data2, method="POST", callback=self.get_performers)

    selector_map = {
        'external_id': r'',
        'pagination': ''
    }

    def get_performers(self, response):
        jsondata = response.json()['data']['actors']['edges']
        for jsonrow in jsondata:
            item = PerformerItem()
            item['name'] = jsonrow['node']['stageName']
            item['url'] = "https://arxbucks.com"
            item['image'] = jsonrow['node']['thumbnailUrl']
            item['gender'] = jsonrow['node']['gender'].title()
            if item['gender'] == "Transsexual":
                item['gender'] = "Trans"
            # ~ item['image'] = jsonrow['node']['thumbnailUrl']
            # ~ if "https" not in item['image']:
            item['image'] = None
            item['image_blob'] = None
            item['birthday'] = jsonrow['node']['dob']
            if not item['birthday']:
                item['birthday'] = ''
            item['network'] = "ARX Bucks"
            item['bio'] = ''
            item['astrology'] = ''
            item['birthplace'] = ''
            item['ethnicity'] = ''
            item['haircolor'] = ''
            item['weight'] = ''
            item['height'] = ''
            item['measurements'] = ''
            item['tattoos'] = ''
            item['piercings'] = ''
            item['cupsize'] = ''
            item['fakeboobs'] = ''
            item['eyecolor'] = ''
            item['nationality'] = ''
            if item['name']:
                yield item
