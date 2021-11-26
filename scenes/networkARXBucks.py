import json
from datetime import date, timedelta
from scrapy.http import Request
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class NetworkARXBucksSpider(BaseSceneScraper):
    name = 'ARXBucks'

    headers = {
        "Content-Type": "application/json"
    }

    def start_requests(self):
        true = True
        null = None
        data = {
            "operationName": "Scenes",
            "variables": {
                "first": 18,
                "after": "",
                "siteId": null,
                "isAvailable": true,
                "orderBy": {"field": "AVAILABLE_AT", "direction": "DESC"}
            },
            "query": "query Scenes($first: Int, $after: String, $siteId: [Int], $actorId: [Int], $genreId: [Int], $isAvailable: Boolean, $orderBy: ScenesOrderBy) {\n  scenes(\n    first: $first\n    after:$after\n    siteId: $siteId\n    actorId: $actorId\n    genreId: $genreId\n    isAvailable: $isAvailable\n    orderBy: $orderBy\n  ) {\n    totalCount\n    edges {\n      node {\n        ...sceneFields\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment sceneFields on Scene {\n  id\n  title\n  durationText\n  quality\n  thumbnailUrl\n  primaryPhotoUrl\n  url\n  createdAt\n  summary\n  photoCount\n  photoThumbUrlPath\n  photoFullUrlPath\n  isAvailable\n  availableAt\n  metadataTitle\n  metadataDescription\n  downloadPhotosUrl\n  actors {\n    id\n    stageName\n    url\n    __typename\n  }\n  genres {\n    id\n    name\n    slug\n    __typename\n  }\n  videoUrls {\n    trailer\n    full4k\n    fullHd\n    fullLow\n    __typename\n  }\n  sites {\n    id\n    name\n    __typename\n  }\n  __typename\n}\n"
        }
        url = "https://arwest-api-production.herokuapp.com/graphql"
        data2 = json.dumps(data)
        # ~ print(data2)
        yield Request(url, headers=self.headers, body=data2, method="POST", callback=self.get_scenes)

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
        jsondata = response.json()['data']['scenes']['edges']
        for jsonrow in jsondata:
            item = SceneItem()
            item['id'] = jsonrow['node']['id']
            item['title'] = jsonrow['node']['title']
            if len(jsonrow['node']['sites']):
                prefix = match_site(str(jsonrow['node']['sites'][0]['id']))
            else:
                prefix = "https://transdayspa.com"
            item['url'] = prefix + jsonrow['node']['url']
            item['image'] = jsonrow['node']['primaryPhotoUrl']
            item['image_blob'] = None
            item['date'] = jsonrow['node']['createdAt']
            item['trailer'] = jsonrow['node']['videoUrls']['trailer']
            item['description'] = jsonrow['node']['summary']
            item['tags'] = []
            for tag in jsonrow['node']['genres']:
                item['tags'].append(tag['name'])
            item['performers'] = []
            for performer in jsonrow['node']['actors']:
                item['performers'].append(performer['stageName'])
            if len(jsonrow['node']['sites']):
                item['site'] = jsonrow['node']['sites'][0]['name']
                item['parent'] = jsonrow['node']['sites'][0]['name']
            else:
                item['site'] = "Trans Day Spa"
                item['parent'] = "Trans Day Spa"
            item['network'] = "ARX Bucks"
            if item['id'] and item['title']:
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
                            yield item
                    else:
                        yield item


def match_site(argument):
    match = {
        '2': "https://japanlust.com",
        '3': "https://honeytrans.com",
        '4': "https://lesworship.com",
        '5': "https://joibabes.com",
        '8': "https://povmasters.com",
        '10': "https://cuckhunter.com",
        '11': "https://nudeyogaporn.com",
        '12': "https://transroommates.com",
    }
    return match.get(argument, "https://arxbucks.com")
